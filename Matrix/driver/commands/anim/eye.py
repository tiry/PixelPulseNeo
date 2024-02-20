from typing import Any, Literal
from PIL import Image, ImageDraw
from Matrix.driver.commands.anim.base import AnimatedStuff, brighten

class Eye(AnimatedStuff):
    
    def __init__(self, x: int, y: int, radius: int, color: tuple[int, int, int]):
        
        AnimatedStuff.__init__(self)
        self.x: int = x  
        self.y: int = y
        self.radius: int = radius
        self.color: tuple[int, int, int] = color
        self.background :tuple[int, int, int] = (220, 220, 220)
        self.open:int = 80
        self.tilt:int=0
  
    def _execute_command(self, name:str, command:dict[str, Any]) -> Literal[0, 1, -1]:
        
        if name =="shut":
            min_open:int = command.get("min", 0)
            speed: int = command.get("speed", 1)
            if self.open <= min_open:
                return 0
            self.open -=speed
            return 1
            
        elif name =="open":
            max_open:int = command.get("max", 100)
            speed: int = command.get("speed", 1)
            if self.open >= max_open:
                return 0
            self.open +=speed
            return 1
        
        elif name =="move":
            tilt_max:int = command.get("max", 100)
            tilt_min:int = command.get("min", -100)
            speed: int = command.get("speed", 1)
            if (self.tilt >= tilt_max and speed > 0)  or (self.tilt <= tilt_min and speed <0):
                return 0
            self.tilt +=speed
            return 1
        
        
        return -1
           
            
    def draw(self, img: Image.Image):
        
        eye: Image.Image = self.draw_eye()
        lids: Image.Image = self.draw_lids()
        background:Image.Image = Image.new("RGB", (self.radius*4+1, self.radius*4+1), color=(0, 0, 0)) 
        compo: Image.Image = Image.composite(eye, background, lids)
        
        img.paste(compo, (self.x-2*self.radius, self.y-2*self.radius))
    
    def draw_lids(self) -> Image.Image:
        
        img:Image.Image = Image.new("1", (self.radius*4+1, self.radius*4+1), color=0)
        draw: ImageDraw.ImageDraw = ImageDraw.Draw(img)
        center: tuple[int, int] = (self.radius*2, self.radius*2)
        ratio:float = self.open/100
        draw.ellipse(
            (center[0] - self.radius*2, center[1] - ratio*self.radius*2, center[0] + self.radius*2, center[1] + ratio*self.radius*2),
            fill=1,
            outline=1
        )
        return img
        
    def draw_eye(self) -> Image.Image:
        
        img:Image.Image = Image.new("RGB", (self.radius*4+1, self.radius*4+1), color=(0, 0, 0))
        
        draw: ImageDraw.ImageDraw = ImageDraw.Draw(img)
        center: tuple[int, int] = (self.radius*2, self.radius*2)
        draw.ellipse(
            (center[0] - self.radius*2, center[1] - self.radius*2, center[0] + self.radius*2, center[1] + self.radius*2),
            fill=self.background,
            outline=brighten(self.background, 0.8)
        )
        
        x_offset:int = int(1.5 * self.radius * self.tilt/100)
        x_radius_ratio:float = 1 - abs(0.2 * self.tilt/100)
        y_radius_ratio:float = 1 - abs(0.1 * self.tilt/100)
        
        draw.ellipse(
            (center[0]+ x_offset - self.radius* x_radius_ratio, center[1] - self.radius*y_radius_ratio , center[0] + x_offset + self.radius*x_radius_ratio, center[1] + self.radius* y_radius_ratio),
            fill=self.color,
            outline=brighten(self.color, 0.8)
        )
        draw.ellipse(
            (center[0]+ x_offset - x_radius_ratio * self.radius/4, center[1] - self.radius/4, center[0]+ x_offset + x_radius_ratio * self.radius/4, center[1] + self.radius/4),
            fill=(0,0,0),
            outline=brighten(self.color, 0.4),
        )
        return img
