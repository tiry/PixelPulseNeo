from underground import SubwayFeed
from Matrix.driver.commands.mta.stops import stopResolverSingleton
import os
import sys


def get_API_key():
    key = os.environ["MTA_API_KEY"]
    if not key:
        print("API KEY must be loaded in environment")
        sys.exit()
    return key


def getNextTrains(Route="F", Station="Carroll"):
    feed = SubwayFeed.get(Route, api_key=get_API_key())
    stopids = stopResolverSingleton.findStopIdsByName(Station)
    # print(f"StopIds = {stopids}")
    data = {}
    all_stops = feed.extract_stop_dict()
    for stopid in stopids:
        if stopid in all_stops[Route]:
            data[stopid] = []
            for t in all_stops[Route][stopid]:
                data[stopid].append(t.strftime("%Y-%m-%d - %HH:%MM:%SS"))

    return data


def getNextTrainsToward(Direction="N", Routes=["F", "G"], Station="Carroll"):
    result = {}
    for route in Routes:
        next_trains = getNextTrains(route, Station)
        for stopid in next_trains:
            if stopid.endswith(Direction):
                times = []
                for t in next_trains[stopid]:
                    time_str = t.split(" - ")[1][:-5]
                    time_str = time_str.replace("H", "")
                    times.append(time_str)
                times.sort()
        result[route] = times[:3]

    return result
