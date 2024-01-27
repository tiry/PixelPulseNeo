
import csv
import io
import json
import zipfile

import requests
import os

# url to the zip file containing MTA metadata
DATA_URL = "http://web.mta.info/developers/data/nyct/subway/google_transit.zip"
CACHE = "cache/stops.txt"



def request_data() -> zipfile.ZipFile:
    """Request the metadata zip file from the MTA."""
    res = requests.get(DATA_URL)
    res.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(res.content))


class Resolver(object):

    def __init__(self, refresh=False):
        self.stops={}
        self.stopsByName={}

        stops_txt = None
        
        dir_path = os.path.dirname(os.path.realpath(__file__))

        cache_file = f"{dir_path}/{CACHE}"
        if os.path.isfile(cache_file) and not refresh:
            #print("load stops definition data from cache")
            with open(cache_file) as cache:
                stops_txt = io.StringIO(cache.read())
            
        else:
            print("Download stops data from Google")
            # get zip file
            zpfile = request_data()
            stops_txt = io.StringIO(zpfile.read("stops.txt").decode())
            with open(cache_file, "w") as cache:
                cache.write(stops_txt.getvalue())


        # iterate using dictreader
        for stop in csv.DictReader(stops_txt):
            # skip stations, i only want stop info.
            if stop["location_type"] == "1":
                continue

            # parse stop direction
            if stop["stop_id"].endswith("N"):
                direction = "NORTH"
            elif stop["stop_id"].endswith("S"):
                direction = "SOUTH"
            else:
                raise ValueError(f"Cannot parse direction: {stop['stop_id']}.")
            stop["direction"] = direction

            name = stop["stop_name"]

            self.stops[stop["stop_id"]]=dict(
                        stop_id=stop["stop_id"],
                        stop_name=name,
                        direction=stop["direction"],
                        stop_lat=float(stop["stop_lat"]),
                        stop_lon=float(stop["stop_lon"]),
                    )
            if not name in self.stopsByName:
                self.stopsByName[name] = []
            self.stopsByName[name].append(stop["stop_id"])

    def getStopByName(self,name):
        return self.stopsByName[name]

    def getStopById(self,id):
        return self.stops[id]

    def findStopByName(self,name):
        matches = []
        for stopid in self.stops:
            stop = self.stops[stopid]
            if name.lower() in stop["stop_name"].lower():
                matches.append(stop)
        return matches
    
    def findStopIdsByName(self,name):
        matches = []
        for stopid in self.stops:
            stop = self.stops[stopid]
            if name.lower() in stop["stop_name"].lower():
                matches.append(stop["stop_id"])
        return matches


stopResolverSingleton = Resolver()

if __name__ == "__main__":
    print(f"loaded {len(stopResolverSingleton.stopsByName)} stops")
    print(f"findStopByName('Carroll') {stopResolverSingleton.findStopByName('Carroll')} ")
    