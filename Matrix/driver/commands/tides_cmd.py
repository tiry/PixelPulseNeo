

from typing import Any
from PIL import Image
from PIL import ImageDraw
from Matrix.driver.commands.base import (
    PictureScrollBaseCmd,
    get_total_matrix_width,
    get_total_matrix_height,
)
from Matrix import config
import Matrix.driver.commands.mta.route as route
from Matrix.driver.commands.mta.stops import stopResolverSingleton
import Matrix.driver.commands.mta.bus as bus


from Matrix.driver.commands.tidesandcurrents import api
from Matrix import config
from PIL import Image
from PIL import ImageDraw

CURVE_COLOR = (29,162,216)
LINE_COLOR = (2, 26,46)

TIME_COLOR = (127, 205,255)
FEET_COLOR = (127, 205,255)

NOW_COLOR = (118, 182,196)

NAME_COLOR = (222, 243,246)

class TidesCmd(PictureScrollBaseCmd):
    def __init__(self) -> None:
        super().__init__(
            "tides", "Displays tides info from station")
        self.scroll = False
        self.refresh = False
        self.speed_x = 0
        self.speed_y = 0
        self.recommended_duration = 30
        self.tides_data={}

    def update(self, args=[], kwargs={}) -> None:
        self.tides_data:{} = api.get_tide_data()
        super().update(args, kwargs)
        
    def generate_image(self, args: list = [], kwargs: dict = {}) -> Image.Image:
        width: int = get_total_matrix_width()
        height: int = get_total_matrix_height()

        img: Image.Image = Image.new("RGB", (width, height), color=(0, 0, 0))
        draw: ImageDraw.ImageDraw = ImageDraw.Draw(img)
        font = self.getFont("5x7.pil")

        draw.line(self.tides_data["curve"], fill=CURVE_COLOR, width=1)
        
        for entry in self.tides_data["hilo"]:
            
            line_delta = 1
            if entry['type']=="H":
                line_delta=-1
                
            draw.line([(entry['x'], entry['y']), (entry['x'], entry['y']+line_delta*35)], fill=LINE_COLOR)
            #draw.point([entry['x'], entry['y']], fill='red')
        
                    
            txt = f"{entry['t']}"
            _, _, text_width, text_height = font.getbbox(txt)
            draw.text((entry['x']-text_width/2, entry['y']+line_delta*25-text_height), txt, font=font, fill=TIME_COLOR)

            txt = f"{entry['v']}"
            _, _, text_width, text_height = font.getbbox(txt)
            draw.text((entry['x']-text_width/2, entry['y']+line_delta*25-text_height+10), txt, font=font, fill=TIME_COLOR)
        
        x_now = self.tides_data["x_now"]
        draw.line([(x_now, 5), (x_now, 59)], fill=NOW_COLOR)
        
        font = self.getFont("6x12.pil")
        name = self.tides_data["name"]
        draw.text((5,1), name, font=font, fill=NAME_COLOR)

        #print(self.tides_data)

        return img
