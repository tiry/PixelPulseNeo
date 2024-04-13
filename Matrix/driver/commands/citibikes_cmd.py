import argparse
import threading
from typing import Any
from Matrix.driver.commands.citibikes import api
from Matrix import config
from Matrix.driver.commands.base import (
    PictureScrollBaseCmd,
    get_icons_dir,
    get_total_matrix_height,
    get_total_matrix_width,
)
from PIL import Image
from PIL import ImageDraw


class CitibikesCmd(PictureScrollBaseCmd):
    def __init__(self) -> None:
        super().__init__(
            "citibikes", "Displays information about the closest Citibike Station"
        )
        self.scroll = False
        self.refresh = False
        self.recommended_duration = 10

    def update(self, args=[], kwargs={}) -> None:
        citibike_info: list = api.getStationInfo(config.CITIBIKES)
        self.citibike_info = citibike_info[0]
        print(f" Citi Bike info {self.citibike_info}")
        super().update(args, kwargs)

    def generate_image(self, args: list = [], kwargs: dict = {}) -> Image.Image:
        width: int = get_total_matrix_width()
        height: int = get_total_matrix_height()

        img: Image.Image = Image.new("RGB", (width, height), color=(0, 0, 0))
        draw: ImageDraw.ImageDraw = ImageDraw.Draw(img)
        font = self.getFont("7x14.pil")

        
        icon: Image.Image = Image.open(
            get_icons_dir("citibike/logo_wide_small.png")
        ).convert("RGB")
        log_width: int = icon.size[0]
        img.paste(icon, (int((width - log_width) / 2), 2))

        item_width=62
        spacing:int = int((width-3*item_width)/2)
        spacing = item_width + spacing
        
        x = 10
        iconElec: Image.Image = Image.open(get_icons_dir("citibike/elec.png")).convert(
            "RGB"
        )
        iconElec = iconElec.resize((32, 32), Image.Resampling.LANCZOS)
        img.paste(iconElec, (x, 32))
        draw.text((x + 32 + 2, 40), str(self.citibike_info["ebikes"]), font=font)

        x = x + spacing
        iconFree: Image.Image = Image.open(
            get_icons_dir("citibike/normal.png")
        ).convert("RGB")
        iconFree = iconFree.resize((30, 30), Image.Resampling.LANCZOS)
        img.paste(iconFree, (x, 32))
        draw.text((x + 32 + 2, 40), str(self.citibike_info["free_bikes"]), font=font)

        x = x + spacing
        iconFree = Image.open(get_icons_dir("citibike/dock.png")).convert("RGB")
        iconFree = iconFree.resize((30, 30), Image.Resampling.LANCZOS)
        img.paste(iconFree, (x, 32))
        draw.text((x + 32 + 2, 40), str(self.citibike_info["empty"]), font=font)

        return img


if __name__ == "__main__":
    parser = argparse.ArgumentParser()


    parser.add_argument(
        "-q", "--query", nargs="+", help="list of commands to execute"
    )



    #parser.add_argument("-e", "--emotions", help="execute emotions", action="store_true")
    
    args = parser.parse_args()
    
    if args.query:
        res:list[dict[Any, Any]] = api.getStationInfo(args.query)
        for station in res:
            print(f" Station : {station['name']}")
    else:
        cmd = CitibikesCmd()
        print("Execute Citibike Command in main thread")
        cmd.execute(threading.Event(), timeout=60)
