

import io
import json
import xml.etree.ElementTree as ElementTree 
import requests
import os
import sys
import urllib.parse

# https://bustime.mta.info/wiki/Developers/SIRIStopMonitoring

# routes
# https://bustime.mta.info/api/where/routes-for-agency/MTA%20NYCT.xml?key=xxx

# get stops for route
# https://bustime.mta.info/api/where/stops-for-route/MTA%20NYCT_B61.json?key=xxx&includePolylines=false&version=2

# monitor stop
# https://bustime.mta.info/api/siri/stop-monitoring.json?key={API_KEY}&OperatorRef=MTA&MonitoringRef=308209&LineRef=MTA%20NYCT_B63

AGENCY = "MTA%20NYCT"

ROUTES_URL = "https://bustime.mta.info/api/where/routes-for-agency/MTA%20NYCT.xml?key={API_KEY}"
ROUTES_CACHE = "cache/bus_routes.txt"
STOPS_URL = "https://bustime.mta.info/api/where/stops-for-route/{LINE}.json?key={API_KEY}&includePolylines=false&version=2"
STOPS_MONITORING_URL = "https://bustime.mta.info/api/siri/stop-monitoring.json?key={API_KEY}&OperatorRef={AGENCY}&MonitoringRef={STOP_ID}&LineRef={LINE}"

def get_API_key():
    key = os.environ["MTA_SIRI_API_KEY"]
    if not key:
        print("SIDI API KEY must be loaded in environment")
        sys.exit()
    return key

def add_parameter(url, name, value):  
    return url.replace("{" + name + "}", value)

def add_key(url):
    return add_parameter(url, "API_KEY", get_API_key())

def get_from_cache_or_url(url, cache_file, format="json", refresh=False):

    data= None
    data_txt = None
    dir_path = os.path.dirname(os.path.realpath(__file__))

    cache_file = f"{dir_path}/{cache_file}"
    if os.path.isfile(cache_file) and not refresh:
        #print("get Data from cache")
        with open(cache_file) as cache:
            data_txt = io.StringIO(cache.read())
    else:
        #print("get Data from url")
        url = add_key(url)
        response = requests.get(url)
        if response.status_code == 200:
            data_txt = response.text
            with open(cache_file, "w") as cache:
                cache.write(data_txt)
            data_txt = io.StringIO(data_txt)

    if data_txt:
        if format == "json":
            data = json.load(data_txt)
        elif format == "xml":
            data = ElementTree.parse(data_txt)

    return data

def get_routes(refresh=False):
    routes = {}
    tree =  get_from_cache_or_url(ROUTES_URL, ROUTES_CACHE, "xml", refresh)
    root = tree.getroot()
    for route in root.findall("./data/list/route"):
        r_data={}
        for tag in route:
            r_data[tag.tag] = tag.text
        route_id = r_data["id"]
        routes[route_id] = r_data
    return routes

def find_route(name, refresh=False):
    routes = get_routes(refresh)
    for route in routes:
        if name.lower() in routes[route]["shortName"].lower():
            return route
        if name.lower() == routes[route]["id"].lower():
            return route
    return None

def get_stops_for_route(route, refresh=False):
    route = find_route(route)
    if not route:
        return None
    route = urllib.parse.quote(route)
    url = add_parameter(STOPS_URL, "LINE", route)

    json_data= get_from_cache_or_url(url, f"cache/{route}_stops.txt", "json", refresh)["data"]
    return json_data["references"]["stops"]

def find_stops(route, name, refresh=False):
    stops = get_stops_for_route(route, refresh)
    if not stops:
        return None
    matches=[]
    name = urllib.parse.quote(name)
    for stop in stops:
        if name.lower() in stop["name"].lower():
            matches.append({"id" : stop["id"], "name" : stop["name"], "routeIds" : stop["routeIds"], "direction" : stop["direction"]})
    return matches


def extract_time(time_str):
    time_str = time_str.split("T")[1]
    t_comp = time_str.split(":")
    return f"{t_comp[0]}:{t_comp[1]}"

def get_stop_info(route, stop_name):    
    route = find_route(route)
    if not route:
        print(f"Unable to find route")
        return None
    stops = find_stops(route, stop_name)
    if not stops or len(stops)==0:
        print(f"Unable to find stops for route = {route}")
        return None
    
    infos = {}
    for stop in stops:
        stop_id = stop["id"]
        url = add_parameter(STOPS_MONITORING_URL, "STOP_ID", stop_id)
        url = add_parameter(url, "AGENCY", AGENCY)
        url = add_parameter(url, "LINE", route)
        url = add_key(url)
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            monitoring_data = data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"]
            
            for entry in monitoring_data:
                entry = entry["MonitoredVehicleJourney"]
                direction = entry["DestinationName"]
                if direction not in infos:
                    infos[direction] = []
                time_data = entry["MonitoredCall"]
                time_str = extract_time(time_data["AimedArrivalTime"]) + "*"
                if "ExpectedArrivalTime" in time_data:
                    time_str = extract_time(time_data["ExpectedArrivalTime"])
                #print(json.dumps(time_data, indent=1))
                infos[direction].append(time_str)
    return infos



if __name__ == "__main__":
    print(get_stop_info("B61", "Carroll"))
    
