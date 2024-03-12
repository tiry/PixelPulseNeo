from PIL import Image
from PIL import ImageDraw
from Matrix.driver.commands.arkanoid import bb
from Matrix.driver.commands.base import (
    PictureScrollBaseCmd,
    get_total_matrix_width,
    get_total_matrix_height)

class ArkanoidCmd(PictureScrollBaseCmd):
    def __init__(self) -> None:
        super().__init__("arkanoid", "Block Breaker game")
        self.scroll = False
        self.refresh = True
        self.speed_x = 0
        self.speed_y = 0
        self.pre_rendered :Image.Image | None = None
        self.recommended_duration = 300
        self.stage:bb.Stage|None = None

 
    def update(self, args: list = [], kwargs: dict = {}) -> str:
        
        width: int = get_total_matrix_width()
        height: int = get_total_matrix_height()
        stage = bb.Stage(width, height)
        self.stage = stage
        return super().update(args, kwargs)

        
    def generate_image(self, args=[], kwargs={}) -> Image.Image | None:

        width: int = get_total_matrix_width()
        height: int = get_total_matrix_height()
        img:Image.Image = Image.new("RGB", (width, height), color=(0, 0, 0))  
        draw: ImageDraw.ImageDraw = ImageDraw.Draw(img)
        
        if self.stage is not None:
            self.stage.draw(draw)
            self.stage.play()

        return img
        

    def handle_text_payload(self, msg:str):    
        if self.stage is None:
            return
        self.logger.info(f"handle_text_payload {msg}")
        if msg.upper()=="LEFT":
            self.stage.input("LEFT")
        elif msg.upper()=="RIGHT":
            self.stage.input("RIGHT")
                

