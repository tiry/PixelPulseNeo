from typing import Any
from underground import SubwayFeed
from Matrix.driver.commands.mta.stops import stopResolverSingleton
import os
import sys


def get_API_key() -> str:
    key: str = os.environ["MTA_API_KEY"]
    if not key:
        print("API KEY must be loaded in environment")
        sys.exit()
    return key


def getNextTrains(route:str="F", station:str="Carroll") -> dict[str, list[str]]:
    feed: SubwayFeed = SubwayFeed.get(route, api_key=get_API_key())
    stopids:list[str] = stopResolverSingleton.findStopIdsByName(station)
    data:dict[str,list [str]] = {}
    all_stops:dict[str, Any] = feed.extract_stop_dict()
    
    for stopid in stopids:
        if stopid in all_stops[route]:
            data[stopid] = []
            for t in all_stops[route][stopid]:
                data[stopid].append(t.strftime("%Y-%m-%d - %HH:%MM:%SS"))

    #print(f"data = {data}")
    return data


def getNextTrainsToward(direction:str="N", routes:list[str]=["F", "G"], station:str="Carroll", max_entries:int=3) -> dict[str, list[str]]:
    result:dict[str, list[str]] = {}
    for route in routes:
        next_trains: dict[str, list[str]] = getNextTrains(route, station)
        for stopid in next_trains:
            if stopid.endswith(direction):
                times:list[str] = []
                for t in next_trains[stopid]:
                    time_str: str = t.split(" - ")[1][:-5]
                    time_str = time_str.replace("H", "")
                    times.append(time_str)
                times.sort()
        result[route] = times[:max_entries]

    return result
