from typing import Any
from PIL import Image
from PIL import ImageDraw
from Matrix.driver.commands.base import (
    PictureScrollBaseCmd,
    get_icons_dir,
    get_total_matrix_width,
    get_total_matrix_height,
    format_date,
    format_time,
)

from Matrix.driver.commands.wttr.weather import getTodayWeather


class MeteoCmd(PictureScrollBaseCmd):
    def __init__(self) -> None:
        super().__init__("meteo", "Displays Weather forcast from wttr.in")
        self.refresh_timer = 1 / 60.0
        self.scroll = True
        self.refresh = True
        self.background: Image.Image | None = None
        self.weather: dict[Any, Any] | None = None

    def update(self, args: list = [], kwargs: dict = {}) -> None:
        self.weather = getTodayWeather()
        # print(f"weather = {self.weather}")
        super().update(args=[], kwargs={})

    def getWeatherBackground(self):
        if not self.background:
            width: int = get_total_matrix_width()
            height: int = get_total_matrix_height()
            img: Image.Image = Image.new("RGB", (width, height), color=(0, 0, 0))
            if self.weather:
                weatherLabel: str = self.weather["weatherLabel"]
                # tempFull = self.weather["tempFull"]
                temp = self.weather["temp"]
                tempFeelsLike = self.weather["tempFeelsLike"]

                # get weather icon
                weatherIcon: Image.Image = Image.open(
                    get_icons_dir(f"wttr_codes/128/{weatherLabel}.png")
                ).convert("RGB")
                weatherIcon = weatherIcon.resize((48, 48), Image.Resampling.LANCZOS)

                
                img.paste(weatherIcon, (8, 8))
                draw: ImageDraw.ImageDraw = ImageDraw.Draw(img)

                font5 = self.getFont("5x7.pil")
                font6 = self.getFont("6x12.pil")

                tempPos: tuple[int, int] = (10 + weatherIcon.size[0], 20)
                draw.text(tempPos, temp, font=font6)

                date_str: str = format_date()

                draw.text(
                    (tempPos[0] + 2, tempPos[1] + 12),
                    tempFeelsLike,
                    font=font5,
                    fill=(150, 150, 150),
                )
                _, _, text_width, text_height = font6.getbbox(date_str)

                draw.text((width / 2 - text_width / 2, 5), date_str, font=font6)

                self.tempPos: tuple[int, int] = tempPos
                self.background = img
            else:
                print("NO Weather info")
                deadIcon: Image.Image = Image.open(
                    get_icons_dir(f"wttr_codes/dead.png")
                ).convert("RGB")
                deadIcon = deadIcon.resize((32, 41), Image.Resampling.LANCZOS)
                img.paste(deadIcon, (0, 8))

                draw: ImageDraw.ImageDraw = ImageDraw.Draw(img)
                font6 = self.getFont("6x12.pil")
                font5 = self.getFont("5x7.pil")
                draw.text((40,4), " WTTR.in site is down" , font=font6)
                draw.text((40,42), "  -- no weather info --" , font=font5)
                self.background = img
                self.tempPos: tuple[int, int] = (32, 50)

                
        if self.background:
            return self.background.copy()
        else:
            return None

    def generate_image(self, args=[], kwargs={}) -> Image.Image | None:
        # get background
        img: Image.Image | None = self.getWeatherBackground()

        if img:
            # add time to background
            draw: ImageDraw.ImageDraw = ImageDraw.Draw(img)
            font = self.getFont("9x18B.pil")
            time_str: str = format_time()
            draw.text((self.tempPos[0] + 30, 24), time_str, font=font)

        return img
