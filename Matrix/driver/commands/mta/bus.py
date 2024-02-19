import io
import json
import os
import sys
import urllib.parse
from typing import Any
import xml.etree.ElementTree as ElementTree
import requests

# https://bustime.mta.info/wiki/Developers/SIRIStopMonitoring

# routes
# https://bustime.mta.info/api/where/routes-for-agency/MTA%20NYCT.xml?key=xxx

# get stops for route
# https://bustime.mta.info/api/where/stops-for-route/MTA%20NYCT_B61.json?key=xxx&includePolylines=false&version=2

# monitor stop
# https://bustime.mta.info/api/siri/stop-monitoring.json?key={API_KEY}&OperatorRef=MTA&MonitoringRef=308209&LineRef=MTA%20NYCT_B63

AGENCY = "MTA%20NYCT"

ROUTES_URL = (
    "https://bustime.mta.info/api/where/routes-for-agency/MTA%20NYCT.xml?key={API_KEY}"
)
ROUTES_CACHE = "cache/bus_routes.txt"
STOPS_URL = "https://bustime.mta.info/api/where/stops-for-route/{LINE}.json?key={API_KEY}&includePolylines=false&version=2"
STOPS_MONITORING_URL = "https://bustime.mta.info/api/siri/stop-monitoring.json?key={API_KEY}&OperatorRef={AGENCY}&MonitoringRef={STOP_ID}&LineRef={LINE}"


def get_API_key() -> str:
    key: str = os.environ["MTA_SIRI_API_KEY"]
    if not key:
        print("SIDI API KEY must be loaded in environment")
        sys.exit()
    return key


def add_parameter(url, name, value) -> str:
    return url.replace("{" + name + "}", value)


def add_key(url) -> str:
    return add_parameter(url, "API_KEY", get_API_key())


def get_from_cache_or_url(url:str, cache_file:str, format:str="json", refresh=False) -> Any:
    
    dir_path: str = os.path.dirname(os.path.realpath(__file__))

    cache_file = f"{dir_path}/{cache_file}"
    if os.path.isfile(cache_file) and not refresh:
        # print("get Data from cache")
        with open(cache_file) as cache:
            data_txt:Any = io.StringIO(cache.read())
    else:
        # print("get Data from url")
        url = add_key(url)
        response: requests.Response = requests.get(url)
        if response.status_code == 200:
            data_txt: Any = response.text
            with open(cache_file, "w") as cache:
                cache.write(data_txt)
            data_txt = io.StringIO(data_txt)

    if data_txt:
        if format == "json":
            return json.load(data_txt)
        elif format == "xml":
            return ElementTree.parse(data_txt)

    return None


def get_routes(refresh=False)-> dict[str, dict[str,str]]:
    routes:dict[str,dict[str,str]] = {}
    tree:ElementTree.ElementTree = get_from_cache_or_url(ROUTES_URL, ROUTES_CACHE, "xml", refresh)
    root: ElementTree.Element = tree.getroot()
    for route in root.findall("./data/list/route"):
        r_data:dict[str,str] = {}
        for tag in route:
            if tag.text:
                r_data[tag.tag] = tag.text
        route_id: str = r_data["id"]
        routes[route_id] = r_data
    return routes


def find_route(name, refresh=False) -> str | None:
    routes: dict[str, dict[str, str]] = get_routes(refresh)
    for route in routes:
        if name.lower() in routes[route]["shortName"].lower():
            return route
        if name.lower() == routes[route]["id"].lower():
            return route
    return None


def get_stops_for_route(route:str | None, refresh=False) -> Any | None:
    route = find_route(route)
    if not route:
        return None
    route = urllib.parse.quote(route)
    url: str = add_parameter(STOPS_URL, "LINE", route)

    json_data = get_from_cache_or_url(url, f"cache/{route}_stops.txt", "json", refresh)[
        "data"
    ]
    return json_data["references"]["stops"]


def find_stops(route:str, name:str, refresh=False) -> list[dict[str, str]] | None:
    stops: Any | None = get_stops_for_route(route, refresh)
    if not stops:
        return None
    matches:list[dict[str,str]] = []
    name = urllib.parse.quote(name)
    for stop in stops:
        if name.lower() in stop["name"].lower():
            matches.append(
                {
                    "id": stop["id"],
                    "name": stop["name"],
                    "routeIds": stop["routeIds"],
                    "direction": stop["direction"],
                }
            )
    return matches


def extract_time(time_str:str) -> str:
    time_str = time_str.split("T")[1]
    t_comp: list[str] = time_str.split(":")
    return f"{t_comp[0]}:{t_comp[1]}"


def get_stop_info(route:str |None , stop_name:str) -> dict[str, Any] | None:
    route = find_route(route)
    if not route:
        print("Unable to find route")
        return None
    stops: list[dict[str, str]] | None = find_stops(route, stop_name)
    if not stops or len(stops) == 0:
        print(f"Unable to find stops for route = {route}")
        return None

    infos:dict[str,Any] = {}
    for stop in stops:
        stop_id: str = stop["id"]
        url: str = add_parameter(STOPS_MONITORING_URL, "STOP_ID", stop_id)
        url = add_parameter(url, "AGENCY", AGENCY)
        url = add_parameter(url, "LINE", route)
        url = add_key(url)
        response: requests.Response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            monitoring_data = data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]
            # print(f"CALL {monitoring_data}")
            if "MonitoredStopVisit" not in monitoring_data:
                infos["???"] = ["???"]
            else:
                stop_data: list[dict] = monitoring_data["MonitoredStopVisit"]
                #print(stop_data)
                for entry in stop_data:
                    entry = entry["MonitoredVehicleJourney"]
                    direction = entry["DestinationName"]
                    if direction not in infos:
                        infos[direction] = []
                    time_data = entry["MonitoredCall"]
                    time_str: str = extract_time(time_data["AimedArrivalTime"]) + "*"
                    if "ExpectedArrivalTime" in time_data:
                        time_str = extract_time(time_data["ExpectedArrivalTime"])
                    # print(json.dumps(time_data, indent=1))
                    infos[direction].append(time_str)
    return infos


if __name__ == "__main__":
    print(get_stop_info("B61", "Carroll"))
