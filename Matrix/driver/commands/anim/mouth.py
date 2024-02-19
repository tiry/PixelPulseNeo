from typing import Any, Literal
from PIL import Image, ImageDraw
from Matrix.driver.commands.anim.base import AnimatedStuff


from Matrix.driver.commands.base import (
    PictureScrollBaseCmd,
    get_total_matrix_width,
    get_total_matrix_height,
)



class Mouth(AnimatedStuff):
    
    def __init__(self, x: int, y: int, radius: int, open_pct:int, color: tuple[int, int, int]):
        
        AnimatedStuff.__init__(self)
        self.x: int = x  
        self.y: int = y
        self.radius: int = radius
        self.color: tuple[int, int, int] = color
        self.open: int = open_pct
        self.tilt:int = 20
  
    def _execute_command(self, name:str, command:dict[str, Any]) -> Literal[0, 1, -1]:
        
        if name =="smile":
            speed: int = command.get("speed", 1)
            if self.open >= 100:
                self.open=100
                return 0
            self.open +=speed
            return 1
        
        elif name =="tilt":
            tilt_max:int = command.get("max", 30)
            tilt_min:int = command.get("min", -30)
            speed: int = command.get("speed", 1)
            if (self.tilt >= tilt_max and speed > 0)  or (self.tilt <= tilt_min and speed <0):
                return 0
            self.tilt +=speed
            return 1
        
        elif name =="open":
            open_max:int = command.get("max", 30)
            open_min:int = command.get("min", -30)
            speed: int = command.get("speed", 1)
            if (self.open >= open_max and speed > 0)  or (self.open <= open_min and speed <0):
                return 0
            
            self.open +=speed
            return 1
        
        elif name =="radius":
            radius_max:int = command.get("max", 40)
            radius_min:int = command.get("min", -40)
            speed: int = command.get("speed", 1)
            if (self.radius >= radius_max and speed > 0)  or (self.radius <= radius_min and speed <0):
                return 0
            self.radius +=speed
            return 1
        
        return -1
           
            
    def draw(self, img: Image.Image):
        draw: ImageDraw.ImageDraw = ImageDraw.Draw(img)
    
        max_width: int = 2* self.radius
        margin:int = int((get_total_matrix_width() - max_width) / 2)
        
        start:int = int( (1-self.open/100)*180 - 90)  
        end:int = int(90 + (self.open/100)*180)
        #draw.arc((margin, 34,get_total_matrix_width()-margin, 62), self.tilt + 90-angle, self.tilt + 90 + angle, fill=(255,0,0), width=2)
        
        draw.chord((margin, 34,get_total_matrix_width()-margin, 62), self.tilt + start, self.tilt + end, fill=(200,200,200), width=2)
        draw.arc((margin, 34,get_total_matrix_width()-margin, 62), self.tilt + start, self.tilt + end, fill=(255,220,200), width=2)
        
        #draw.arc((margin, 34,get_total_matrix_width()-margin, 62), start, end , fill=(255,220,200), width=2)
                
        #chord
