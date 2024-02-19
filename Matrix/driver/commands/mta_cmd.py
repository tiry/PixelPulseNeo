import threading
import argparse
import time
from PIL import Image
from PIL import ImageDraw
from Matrix.driver.commands.base import (
    PictureScrollBaseCmd,
    get_icons_dir,
    get_total_matrix_width,
    get_total_matrix_height,
)
import Matrix.driver.commands.mta.route as route
import Matrix.driver.commands.mta.bus as bus



def truncate(s, length):
    if len(s) > length:
        if "via" in s:
            return truncate(s.split("via")[0], length)
        return s[:length] + "..."
    else:
        return s


PAUSED_FRAMES = 60 * 3


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
        self.next_trains:dict | None = None
        self.next_buses:dict | None = None

    def update(self, args:list=[], kwargs:dict={}) -> None:
        next_trains: dict = route.getNextTrainsToward(
            Direction="N", Routes=["F", "G"], Station="Carroll"
        )
        # print(f"Next trains {next_trains}")
        self.next_trains = next_trains
        self.next_buses  = bus.get_stop_info("B61", "Carroll")
        # print(f"Next Buses {self.next_buses}")
        super().update(args, kwargs)

        if "pause_frames" in kwargs.keys():
            self.tempoframes = int(kwargs["pause_frames"])
            self.pause_duration: int = self.tempoframes

    def generate_image(self, args:list=[], kwargs:dict={}) -> Image.Image:
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
                icon:Image.Image = Image.open(get_icons_dir(f"mta/png/{train}.png")).convert("RGB")
                icon = icon.resize((25, 25), Image.Resampling.LANCZOS)

                img.paste(icon, (7, 4 + idx * 32))

                txt = " / ".join(self.next_trains[train])
                draw.text((40, 10 + idx * 32), txt, font=font7)
                idx += 1

        # display bus info
        icon = Image.open(get_icons_dir("mta/png/MTA_NYC_LOGO.png")).convert("RGB")
        icon = icon.resize((40, 40), Image.Resampling.LANCZOS)
        img.paste(icon, (1, 64 + 4))
        draw.text((6, 64 + 44), "B61", font=font9)
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

    args = parser.parse_args()
    cmd = MtaCmd()
    print("Execute MTA Command in main thread")
    cmd.execute(threading.Event(), timeout=60)
