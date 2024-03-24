import threading
import argparse
from typing import Any
from PIL import Image
from PIL import ImageDraw
from Matrix.driver.commands.base import (
    PictureScrollBaseCmd,
    get_icons_dir,
    get_total_matrix_width,
    get_total_matrix_height,
)
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

PAUSED_FRAMES = 60 * 8

class MtaCmd(PictureScrollBaseCmd):
    def __init__(self) -> None:
        super().__init__(
            "mta", "Displays next trains and bus arrival time for a given location"
        )
        self.scroll = True
        self.refresh = False
        self.speed_x = 0
        self.speed_y = 0
        self.tempoframes = PAUSED_FRAMES
        self.pause_duration = PAUSED_FRAMES
        self.direction = -1
        self.next_trains: dict | None = None
        self.next_buses: dict | None = None
        self.recommended_duration = 30

    def reset_state(self) -> None:
        super().reset_state()
        self.scroll = True
        self.refresh = False
        self.speed_x = 0
        self.speed_y = 0
        self.tempoframes = PAUSED_FRAMES
        self.pause_duration = PAUSED_FRAMES
        self.direction = -1
        self.next_trains: dict | None = None
        self.next_buses: dict | None = None
        self.recommended_duration = 30
    
    def update(self, args: list = [], kwargs: dict = {}) -> None:
        self.logger.info("Get info from MTA")
        next_trains: dict = route.getNextTrainsToward(
            direction=config.MTA_SUBWAY_DIRECTION, routes=config.MTA_SUBWAY_ROUTES, station=config.MTA_SUBWAY_STATION
        )
        self.logger.info(f"Next trains {next_trains}")
        self.next_trains = next_trains
        self.next_buses = bus.get_stop_info(config.MTA_BUS_LINE, config.MTA_BUS_STATION)
        self.logger.info(f"Next Buses {self.next_buses}")
        super().update(args, kwargs)

        #if "pause_frames" in kwargs.keys():
        #    self.tempoframes = int(kwargs["pause_frames"])
        #    self.pause_duration: int = self.tempoframes

    def generate_image(self, args: list = [], kwargs: dict = {}) -> Image.Image:
        width: int = get_total_matrix_width()
        height: int = get_total_matrix_height() * 2

        img: Image.Image = Image.new("RGB", (width, height), color=(0, 0, 0))
        draw: ImageDraw.ImageDraw = ImageDraw.Draw(img)
        font9 = self.getFont("9x18B.pil")
        font7 = self.getFont("7x14.pil")
        font6 = self.getFont("6x12.pil")
        font5 = self.getFont("5x7.pil")
        idx = 0

        # display train info
        if self.next_trains:
            for train in self.next_trains:
                icon: Image.Image = Image.open(
                    get_icons_dir(f"mta/png/{train}.png")
                ).convert("RGB")
                icon = icon.resize((25, 25), Image.Resampling.LANCZOS)

                img.paste(icon, (7, 4 + idx * 32))

                txt = " / ".join(self.next_trains[train])
                draw.text((40, 10 + idx * 32), txt, font=font7)
                idx += 1

        # display bus info
        icon = Image.open(get_icons_dir("mta/png/MTA_NYC_LOGO.png")).convert("RGB")
        icon = icon.resize((40, 40), Image.Resampling.LANCZOS)
        img.paste(icon, (1, 64 + 4))
        draw.text((6, 64 + 44), config.MTA_BUS_LINE, font=font9)
        idx = 0
        if self.next_buses:
            for bus_stop in self.next_buses:
                direction = truncate(bus_stop, 30)
                _, _, text_width, text_height = font5.getbbox(direction)
                xoffset = int((64 * 3 - text_width - 42) / 2)
                draw.text(
                    (42 + xoffset, 64 + 4 + 16 * idx),
                    direction,
                    font=font5,
                    fill=(0, 128, 255),
                )

                times = " ".join(self.next_buses[bus_stop][:4])
                _, _, text_width, text_height = font6.getbbox(times)
                xoffset = int((64 * 3 - text_width - 42) / 2)
                draw.text((42 + xoffset, 64 + 16 * (idx + 1)), times, font=font6)
                idx += 2

        return img

    def render(self, args=[], kwargs={}) -> None:
        super().render(args, kwargs)

        self.tempoframes -= 1
        if self.tempoframes <= 0:
            if self.ypos == -64:
                self.tempoframes = self.pause_duration
                self.direction = +1
            elif self.ypos == 0:
                self.tempoframes = self.pause_duration
                self.direction = -1
            self.speed_y = 4 * self.direction
        else:
            if self.ypos == -64:
                self.speed_y = 0
            elif self.ypos == 0:
                self.speed_y = 0


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()    
    parser.add_argument(
        "-r", "--route", nargs="+", help="list of routes to query"
    )
    parser.add_argument("-d", "--direction", help="direction N/S", default="N")
    parser.add_argument("-s", "--station", help="Statcion name")
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
    else:
        cmd = MtaCmd()
        print("Execute MTA Command in main thread")
        cmd.execute(threading.Event(), timeout=60)
