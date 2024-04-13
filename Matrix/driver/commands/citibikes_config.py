import argparse
import threading
from typing import Any
from Matrix.driver.commands.citibikes import api



if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-q", "--query", nargs="+", help="list of commands to execute"
    )
    
    args = parser.parse_args()
    
    if args.query:
        res:list[dict[Any, Any]] = api.getStationInfo(args.query)
        for station in res:
            print(f" Station : {station['name']}")
    else:
        parser.print_help()