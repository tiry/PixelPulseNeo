from PIL import Image
from Matrix.driver.commands.base import (
    PictureScrollBaseCmd,
    get_total_matrix_width,
    get_total_matrix_height,
    )
from Matrix.driver.monitor import probe
from Matrix.driver.commands.splitflap.FB import FlapPannel

class SplitflapCmd(PictureScrollBaseCmd):
    def __init__(self) -> None:
        super().__init__("splitflap", "Display text using Split Flap Display")
        self.scroll = False
        self.refresh = True
        self.n_frame:int=0
        self.refresh_timer:float = 1/30
        self.recommended_duration = 120
        self.background:Image.Image | None = None
        self.font_height=32
        self.font = None
        
        width: int = get_total_matrix_width()
        self.flap_panel:FlapPannel = FlapPannel(width=int(width/24))
        self.flap_panel.append_text("HAVE A NICE DAY")
        self.flap_panel.append_text("use the app to ")
        self.flap_panel.append_text("change the text")
                
    def update_image(self):
        
        width: int = get_total_matrix_width()
        height: int = get_total_matrix_height()
        self.background =  Image.new("RGB", (width, height), color=(0, 0, 0))    
        
        
        if self.font is None:
            self.logger.info(f"Loading font {self.font_height} px")
            self.font = self.getFont("LiberationMono-Regular.ttf", self.font_height, )
    
    
    def update(self, args: list = [], kwargs: dict = {}) -> str:
        self.update_image()
        return super().update(args, kwargs)
        
    def generate_image(self, args=[], kwargs={}) -> Image.Image | None:

        if self.background is not None:
            background: Image.Image = self.background.copy()
            
            self.flap_panel.render(background)
                
            return background
        
        return None
    
        