import argparse
from typing import Any
from Matrix import config
from Matrix.driver.commands.base import (
    PictureScrollBaseCmd,
    get_icons_dir,
    get_total_matrix_height,
    get_total_matrix_width,
)
from PIL import Image
from PIL import ImageDraw


class KittCmd(PictureScrollBaseCmd):
    def __init__(self) -> None:
        super().__init__(
            "kitt", "K.I.T.T from the K2000 TV series"
        )
        self.scroll:bool = False
        self.refresh:bool = True
        self.recommended_duration:int = 15
        
        self.refresh_timer = 1/10
        self.decay=0.85
        self.lights_count = 15
        self.margin:int = 20
        self.lights_width:int = int((get_total_matrix_width()-2*self.margin)/self.lights_count)
        self.lights: list[int]= [0 for _ in range(self.lights_count)]
        self.lights_index=0
        self.lights_dir:int =1
        

    def update(self, args=[], kwargs={}) -> None:
        super().update(args, kwargs)

    def decay_lights(self):
        self.lights = [int(x * self.decay) for x in self.lights]

    def generate_image(self, args: list = [], kwargs: dict = {}) -> Image.Image:
        width: int = get_total_matrix_width()
        height: int = get_total_matrix_height()

        self.decay_lights()
        self.lights[self.lights_index] = 100

        img: Image.Image = Image.new("RGB", (width, height), color=(0, 0, 0))
        background: Image.Image = Image.open(
                    get_icons_dir("kitt/kitt_off2.png")
                ).convert("RGBA")
        
        draw: ImageDraw.ImageDraw = ImageDraw.Draw(img)
        font = self.getFont("7x14.pil")
        
        for idx, light in enumerate(self.lights):
            
            color: tuple[int, int, int] = (int(255*light/100), 0, 0)
            #if color[0]>128:
            dx: int = self.margin + idx*self.lights_width
            draw.rectangle((dx, 24, dx+self.lights_width, 35), fill=color)
        
        self.lights_index+=self.lights_dir
        if self.lights_index == self.lights_count -1: 
            self.lights_dir = -self.lights_dir
        elif self.lights_index == 0:
            self.lights_dir = -self.lights_dir
            
        img.paste(background, (0, 0), mask=background)
        
        return img


