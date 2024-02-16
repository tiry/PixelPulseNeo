from PIL import Image
from PIL import ImageDraw
import datetime
from urllib.request import urlopen
from Matrix.driver.commands.base import (
    PictureScrollBaseCmd,
    get_total_matrix_width,
    get_total_matrix_height,
    get_icons_dir,
)
from Matrix.driver.commands.spotify import client

def getImage(img_url):
    return Image.open(urlopen(img_url)).convert("RGB")

    
class SpotifyCmd(PictureScrollBaseCmd):
    def __init__(self):
        super().__init__("spotify", "Displays information related to current played song on Spotify")
        self.scroll = False
        self.refresh = True
        self.refresh_timer= 1
        self.speedX = 0
        self.speedY = 0
        
        self.cached_image = None
        self.cached_track_id = None
        self.track_info = None

    def update(self, args=[], kwargs={}):
        self.track_info  = client.get_current_track_info()

        print(f"Track info {self.track_info}")
        return super().update(args, kwargs)

    def render_no_track(self):
        width = get_total_matrix_width()
        height = get_total_matrix_height()
        img = Image.new("RGB", (width, height), color=(0, 0, 0))
        return img
    
    def render_track_info(self):

        font = self.getFont("6x12.pil")
        font5 = self.getFont("5x7.pil")
        font4 = self.getFont("4x6.pil")

        if self.track_info is None:
            return self.render_no_track()

        if self.track_info["track_id"]!= self.cached_track_id or self.cached_image is None:
            # render and cache the result

            width = get_total_matrix_width()
            height = get_total_matrix_height()
            img = Image.new("RGB", (width, height), color=(0, 0, 0))
            
            thumb = getImage(self.track_info["thumbnail"])         
            img.paste(thumb, (0, 0))
            
            draw = ImageDraw.Draw(img)

            xoffset = 64  + self._compute_text_position(self.track_info["artist_name"], font, 128)
            draw.text((xoffset, 2), self.track_info["artist_name"], font=font)

            xoffset = 64  + self._compute_text_position(self.track_info["track_name"], font, 128)
            draw.text((xoffset, 20), self.track_info["track_name"], font=font)

            xoffset = 64  + self._compute_text_position(self.track_info["album_name"], font4, 128)
            draw.text((xoffset, 40), self.track_info["album_name"], font=font4)

            draw.line((64+10, 60, 192-10, 60), fill=(255, 255, 255))

            end = str(datetime.timedelta(seconds = int(self.track_info["track_duration"]/1000)))[-5:]
            draw.text((192-20, 52), end, font=font4)

            self.cached_image = img
            self.cached_track_id = self.track_info["track_id"]

        
        # copy the image before updating
        img = self.cached_image.copy()
        draw = ImageDraw.Draw(img)
        start = str(datetime.timedelta(seconds = int(self.track_info["track_position"]/1000)))[-5:]
        draw.text((64+2, 52), start, font=font4)

        line_width = 192-10 - 64+10
        progress = int(self.track_info["track_position"] / self.track_info["track_duration"] * line_width)
        draw.line((64+10, 60, 64+10 + progress, 60), fill=(29, 185, 84))

        return img

    def generate_image(self, args=[], kwargs={}):
        img = self.render_track_info()
        self.track_info  = client.get_current_track_info()
        return img
