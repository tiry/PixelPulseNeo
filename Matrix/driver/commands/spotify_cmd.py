import datetime
from typing import Any
from urllib.request import urlopen
from PIL import Image
from PIL import ImageDraw
from Matrix.driver.commands.base import (
    PictureScrollBaseCmd,
    get_total_matrix_width,
    get_total_matrix_height,
    get_icons_dir,
)
from Matrix.driver.commands.spotify import client


def load_image(img_url) -> Image.Image:
    return Image.open(urlopen(img_url)).convert("RGB")


class SpotifyCmd(PictureScrollBaseCmd):
    def __init__(self) -> None:
        super().__init__(
            "spotify", "Displays information related to current played song on Spotify"
        )
        self.scroll = False
        self.refresh = True
        self.refresh_timer = 1
        self.speed_x = 0
        self.speed_y = 0

        self.cached_image: Image.Image | None = None
        self.cached_track_id: str | None = None
        self.track_info: dict[str, Any] | None = None
        self.cached_placeholder: Image.Image | None = None
        self.recommended_duration = 15*60

    def update(self, args=[], kwargs={}) -> str:
        self.track_info = client.get_current_track_info()
        print(f"Track info {self.track_info}")
        return super().update(args, kwargs)

    def render_no_track(self) -> Image.Image:
        if self.cached_placeholder is None:
            font = self.getFont("6x12.pil")
            font5 = self.getFont("5x7.pil")

            width: int = get_total_matrix_width()
            height: int = get_total_matrix_height()
            img: Image.Image = Image.new("RGB", (width, height), color=(0, 0, 0))

            icon: Image.Image = Image.open(
                get_icons_dir("spotify/spotify.png")
            ).convert("RGB")
            resized_icon: Image.Image = icon.resize((64, 64))
            img.paste(resized_icon, (0, 0))

            draw: ImageDraw.ImageDraw = ImageDraw.Draw(img)
            text = "No Track"
            xoffset: int = 64 + self._compute_text_position(text, font, 128)
            draw.text((xoffset, 10), text, font=font)

            text = "playing on Spotify"
            xoffset = 64 + self._compute_text_position(text, font5, 128)
            draw.text((xoffset, 30), text, font=font5)

            self.cached_placeholder = img

        return self.cached_placeholder

    def render_track_info(self) -> Image.Image:
        font = self.getFont("6x12.pil")
        font5 = self.getFont("5x7.pil")
        font4 = self.getFont("4x6.pil")

        if self.track_info is None:
            # interrupt execution
            self.execution_done=True
            return self.render_no_track()

        if (
            self.track_info["track_id"] != self.cached_track_id
            or self.cached_image is None
        ):
            # render and cache the result

            width: int = get_total_matrix_width()
            height: int = get_total_matrix_height()
            img: Image.Image = Image.new("RGB", (width, height), color=(0, 0, 0))

            thumb: Image.Image = load_image(self.track_info["thumbnail"])
            img.paste(thumb, (0, 0))

            draw: ImageDraw.ImageDraw = ImageDraw.Draw(img)

            xoffset: int = 64 + self._compute_text_position(
                self.track_info["artist_name"], font, 128
            )
            draw.text((xoffset, 2), self.track_info["artist_name"], font=font)

            xoffset = 64 + self._compute_text_position(
                self.track_info["track_name"], font5, 128
            )
            draw.text((xoffset, 20), self.track_info["track_name"], font=font5)

            xoffset = 64 + self._compute_text_position(
                self.track_info["album_name"], font4, 128
            )
            draw.text((xoffset, 40), self.track_info["album_name"], font=font4)

            draw.line((64 + 10, 60, 192 - 10, 60), fill=(255, 255, 255))

            end: str = str(
                datetime.timedelta(
                    seconds=int(self.track_info["track_duration"] / 1000)
                )
            )[-5:]
            draw.text((192 - 20, 52), end, font=font4)

            self.cached_image = img
            self.cached_track_id = self.track_info["track_id"]

        # copy the image before updating
        img = self.cached_image.copy()
        draw = ImageDraw.Draw(img)
        start: str = str(
            datetime.timedelta(seconds=int(self.track_info["track_position"] / 1000))
        )[-5:]
        draw.text((64 + 2, 52), start, font=font4)

        line_width = 192 - 10 - 64 + 10
        progress = int(
            self.track_info["track_position"]
            / self.track_info["track_duration"]
            * line_width
        )
        draw.line((64 + 10, 60, 64 + 10 + progress, 60), fill=(29, 185, 84))

        return img

    def generate_image(self, args: list = [], kwargs: dict = {}) -> Image.Image:
        img: Image.Image = self.render_track_info()
        self.track_info = client.get_current_track_info()
        return img
