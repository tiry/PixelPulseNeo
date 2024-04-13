import threading
import argparse
from typing import Any
from Matrix import config
import Matrix.driver.commands.mta.route as route
from Matrix.driver.commands.mta.stops import stopResolverSingleton
import Matrix.driver.commands.mta.bus as bus


def truncate(s, length):
    if len(s) > length:
        if "via" in s:
            return truncate(s.split("via")[0], length)
        return s[:length] + "..."
    else:
        return s




if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()    
    parser.add_argument(
        "-r", "--route", nargs="+", help="list of routes to query"
    )
    parser.add_argument("-d", "--direction", help="direction N/S", default="N")
    parser.add_argument("-s", "--station", help="Station name")
    parser.add_argument("-b", "--bus", help="query for bus")
    
    args = parser.parse_args()
    
    if args.bus:
        if args.station is None:
            print("search bus line")
            found_bus_line: str | None = bus.find_route(args.bus)
            if found_bus_line is None:
                print("No bus line found")
            else: 
                print(f"Found {found_bus_line}")
        else:    
            print("search bus stop line")
            buses: dict[str, list[str]] | None = bus.get_stop_info(args.bus, args.station)
            if buses is None:
                print("No match")
            else:
                for station in buses.keys():
                    print(f"{station}:")
                    for ts in buses[station]:
                        print(f"    {ts}")
            
    elif args.station and not args.route:
        stations:list[dict[str, Any]] = stopResolverSingleton.findStopByName(args.station)
        for station in stations:
            print(f" stop_name = {station['stop_name']} ({station['stop_id']})")
    
    elif args.route:
        
        trains: dict = route.getNextTrainsToward(
            direction=args.direction, routes=args.route, station=args.station
        )
        for route in trains.keys():
            times:list[str] = trains[route]
            print(f" Next trains for {route} station {args.station} on direction {args.direction}")
            for t in times:
                print(f"     {t}")   
