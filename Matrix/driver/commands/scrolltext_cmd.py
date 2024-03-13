import math
from typing import Any, List
from PIL import Image, ImageOps
from Matrix.driver.commands.base import TextScrollBaseCmd, get_total_matrix_height, get_total_matrix_width 


class WaveDeformer:
    
    def __init__(self, shift_amplitude:int, freq:int, phase_step:float=0.3, gridspace:int=20) -> None:
        self.shift_amplitude: int=shift_amplitude
        self.freq: int = freq
        self.gridspace: int = gridspace
        self.target_grid:list[tuple] = []
        self.phase:float=0
        self.phase_step:float=phase_step

    def init_grid(self, img):
        w, h = img.size

        target_grid = []
        for x in range(0, w, self.gridspace):
            for y in range(0, h, self.gridspace):
                target_grid.append((x, y, x + self.gridspace, y + self.gridspace))
        self.target_grid = target_grid

    def transform(self, x, y):
        y = y + self.shift_amplitude*math.sin(x/self.freq + self.phase)
        return x, y

    def transform_rectangle(self, x0, y0, x1, y1):
        return (*self.transform(x0, y0),
                *self.transform(x0, y1),
                *self.transform(x1, y1),
                *self.transform(x1, y0),
                )

    def getmesh(self, img):
        
        self.phase+=self.phase_step
        source_grid = [self.transform_rectangle(*rect) for rect in self.target_grid]

        return [t for t in zip(self.target_grid, source_grid)]

class ScrolltextCmd(TextScrollBaseCmd):
    
    def __init__(self):
        super().__init__("scrolltext", "Displays Text on Matrix")
        self.msg:str = "Hello, use the mobile app to control this text and the way the scrolling works."
        self.speed_y = 0    
        self.freq:int = 128
        self.amplitude:int = 4
        self.shift_amplitude:int = 7
        self.text_color = (255,255,255)
        self.text_speed:int = 3
        self.phase:float = 0
        self.phase_step:float = 0.3
        self.refresh_timer: float = 1/30.0
        
        self.wave = WaveDeformer(self.shift_amplitude, int(self.freq/5), self.phase_step, 32)
        self.wave.init_grid(self._get_background())
  
        
    def get_text(self, args: list = [], kwargs: dict = {}) -> str:
        return self.msg

    def get_text_color(self):
        return self.text_color
   
    def handle_text_payload(self, msg:str):    
        self.logger.info(f"handle_text_payload {msg}")
        self.msg = msg
        self.update_text_params(self.msg)
        self.logger.info("Scrolling message updated")

    def handle_json_payload(self, payload:Any):
        if payload is not None:
            self.logger.info(f"processing message {payload}")
            self.logger.info(f"payload keys: {payload.keys()}")
            
            if "freq" in payload.keys():
                self.freq = int(payload["freq"])
            if "amplitude" in payload.keys():
                self.amplitude = int(payload["amplitude"])
            if "speed" in payload.keys():
                self.text_speed = int(payload["speed"])
            if "font_height" in payload.keys():
                self.font_height = int(payload["font_height"])
                self.update_text_params(self.msg)
            if "color" in payload.keys():
                clist = payload["color"]
                self.text_color = tuple(clist[:3])
            if "freq_delta" in payload.keys():
                self.freq += int(payload["freq_delta"])
            if "amplitude_delta" in payload.keys():
                self.amplitude += int(payload["amplitude_delta"])
            if "speed_delta" in payload.keys():
                self.text_speed += int(payload["speed_delta"])
            if "phase_step_delta" in payload.keys():
                self.phase_step += int(payload["phase_step_delta"])
            if "shift_amplitude_delta" in payload.keys():
                self.shift_amplitude += int(payload["shift_amplitude_delta"])
            if "font_height_delta" in payload.keys():
                self.font_height += int(payload["font_height_delta"])
                if self.font_height < 10:
                    self.font_height = 10
                self.get_font(True) # force refresh // bypass all caches
                self.update_text_params(self.msg)
                
    def render(self, args: list = [], kwargs: dict = {}) -> str:        
        # Sin modulation
        y_offset =  int(self.amplitude* math.sin(((self.image_counter%self.freq)/self.freq)*2*math.pi))
        self.ypos = y_offset # int((get_total_matrix_height() - self.text_height) / 2) + y_offset
        return super().render()     
    
    def generate_image(self, args: List = [], kwargs: dict = {}) -> Image.Image|None: 
        
        img:Image.Image|None = super().generate_image()
        if img is not None:
            #return self.bend_image_oldschool(img)
            return self.bend_image(img)
        return img
        

    def bend_image_oldschool(self, img:Image.Image) -> Image.Image:
        
        self.phase += self.phase_step
        if self.phase > 2*math.pi:
            self.phase = 0
         
        col:list[Any] = []
        for x in range(0, get_total_matrix_width()):
            col = []
            for y in range(0, get_total_matrix_height()):
                col.append(img.getpixel((x,y)))
            
            y_shift =  int(self.shift_amplitude* math.sin(((x%self.freq)/self.freq)*2*math.pi + self.phase))
            col = self._shift_array(col, y_shift)
            
            for y in range(0, get_total_matrix_height()):
                img.putpixel((x,y), col[y])
            
        return img
    
    def bend_image(self, img:Image.Image) -> Image.Image:
        
        result_image = ImageOps.deform(img, self.wave)
        
        return result_image
    
    def _shift_array(self, list:list, shift:int) -> list:
        return list[shift:] + list[:shift]
    
    
if __name__ == "__main__":
    
    import threading
    #import cProfile
    cmd = ScrolltextCmd()
    
    cmd.execute(threading.Event(), timeout=60)
    #cProfile.run("cmd.execute(threading.Event(), timeout=60)")