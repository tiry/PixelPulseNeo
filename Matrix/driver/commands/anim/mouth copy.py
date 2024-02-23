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
        self.open2: int = 60
        self.tilt:int = 0
        self.tilt2:int = 0
        
  
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

        mouth_y = 34
        mouth_height:int = 62-34
        
        max_width: int = 2* self.radius
        margin:int = int((get_total_matrix_width() - max_width) / 2)
        
        draw_top_lips=False
        top_lips_offset:int| None = None
        if self.open>50:
            start_lips_b:int = 0  
            end_lips_b:int = 180

            draw_top_lips =True
            top_lips_offset = int( (1 - (self.open-50)/100) * mouth_height/2)
            #if (top_lips_height)==0:
            #    top_lips_height=1 
        else:
            start_lips_b:int = int( (1-self.open/100)*180 - 90)  
            end_lips_b:int = int(90 + (self.open/100)*180)
        
        #draw.arc((margin, 34,get_total_matrix_width()-margin, 62), self.tilt + 90-angle, self.tilt + 90 + angle, fill=(255,0,0), width=2)
        
        start2:int = int( (1-self.open*self.open2/10000)*180 - 90)  
        end2:int = int(90 + (self.open*self.open2/10000)*180)
        
        if start2 > 180 or end2 > 180:
            start2 = 0
            end2 = 180
        
        draw.chord((margin, mouth_y,get_total_matrix_width()-margin, mouth_y + mouth_height), self.tilt+self.tilt2 + start2, self.tilt+self.tilt2 + end2, fill=(200,200,200), width=2)

        draw.arc((margin, mouth_y,get_total_matrix_width()-margin, mouth_y+mouth_height), self.tilt + start_lips_b, self.tilt + end_lips_b, fill=(255,220,200), width=2)
        
        if draw_top_lips is True and top_lips_offset:
            #top_lips_height=0
            draw.chord((margin, 34+ top_lips_offset,get_total_matrix_width()-margin, 62- top_lips_offset), self.tilt + 180, self.tilt + 360, fill=(255,220,200), width=2)
            draw.arc((margin, 34+ top_lips_offset,get_total_matrix_width()-margin, 62- top_lips_offset), self.tilt + 180, self.tilt + 360, fill=(255,220,200), width=2)
        
        #draw.arc((margin, 34,get_total_matrix_width()-margin, 62), start, end , fill=(255,220,200), width=2)
                
        #chord
