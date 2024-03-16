import os
import random
from PIL import Image
from Matrix.driver.commands.base import (
    PictureScrollBaseCmd,
    get_total_matrix_width,
    get_total_matrix_height,
)
from Matrix.driver.monitor import probe

def get_pics_path() -> list[str]:
    current_directory: str = os.path.dirname(os.path.realpath(__file__))
    relative_path: str = os.path.join(current_directory, "pic/")
    absolute_path: str = os.path.abspath(relative_path)
    pics =  os.listdir(absolute_path)
    return [f"{absolute_path}/{pic}" for pic in pics]

class PicCmd(PictureScrollBaseCmd):
    def __init__(self) -> None:
        super().__init__("pic", "Display an Animated Gif or an Data URI Picture")
        self.scroll = False
        self.refresh = True
        self.speed_x = 0
        self.speed_y = 0
        self.pre_rendered :Image.Image | None = None
        self.current_frame=0
        self.n_frame:int=0
        self.refresh_timer:float = 1/20
        self.pics_path:list[str] = get_pics_path()
        self.loop_counter:int=0
        self.recommended_duration = 120
        self.max_loop:int = 4
    
    def get_random_pic(self) -> str:
        return self.pics_path[random.randint(0, len(self.pics_path)-1)]
    
    def update_image(self):
        self.gif:Image.Image = Image.open(self.get_random_pic())
        
        width: int = get_total_matrix_width()
        height: int = get_total_matrix_height()
        self.background:Image.Image =  Image.new("RGB", (width, height), color=(0, 0, 0))    
        self.background.paste(self.gif)
        self.n_frame= self.gif.n_frames
        
    
    def update(self, args: list = [], kwargs: dict = {}) -> str:
        self.update_image()
        return super().update(args, kwargs)
        
    def generate_image(self, args=[], kwargs={}) -> Image.Image | None:

        if self.loop_counter==self.max_loop:
            self.update_image()
            self.loop_counter=0
        
        self.gif.seek(self.current_frame)

        self.current_frame+=1
        if self.current_frame >= self.n_frame:
            self.current_frame=0
            self.loop_counter+=1
        
        bg = self.background.copy()
        bg.paste(self.gif)
        
        return bg
    
        