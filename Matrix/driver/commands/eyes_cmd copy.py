import argparse
import threading
from typing import Any, Literal
from PIL import Image, ImageDraw
from abc import ABC, abstractmethod
from Matrix.driver.commands.base import (
    PictureScrollBaseCmd,
    get_total_matrix_width,
    get_total_matrix_height,
)

def brighten(color: tuple[int, int, int], factor: float = 1.1) -> tuple[int, int, int]:
    
    new_color:list[int]= [int(factor*c) for c in color]
    for i in range(3):
        if new_color[i] > 255:
            new_color[i] = 255

    result:tuple[int,int, int]= (new_color[0], new_color[1], new_color[2])
    return result

class AnimatedStuff(ABC):
    
    def __init__(self):
        self.pause_counter:int|None = None        
        self.command_groups:list[list[dict[str, Any]]]=[]
    
    def add_command_group(self, group: list[dict[str, Any]]):
        self.command_groups.append(group)
        print(f"added command group => {self.command_groups}")
        
    def get_current_command_group(self) -> list[dict[str, Any]]|None:
        if len(self.command_groups)==0:
            #print("No More Commands")
            return None
        return self.command_groups[0]
    
    def next_command_group(self) -> list[dict[str, Any]] | None:
        if len(self.command_groups)==0:
            return None
        #print("Close command group")
        return self.command_groups.pop(0)
    
    @abstractmethod
    def _execute_command(self, name:str, command:dict[str, Any]) -> Literal[0, 1, -1]:
        pass       
    
    def process_current_command_group(self) -> list[dict[str, Any]] | None:
        current_command_group:list[dict[str, Any]]|None = self.get_current_command_group()
        
        if current_command_group is None:
            return None        
        
        remaining_command_group:list[dict[str, Any]]=[]
        
        for command in current_command_group:
            
            # -1 = err / not found
            # 1 = ok, continue
            # 0 = ok, completed
            res: Literal[0, 1, -1]=-1
            if "name" in command.keys():
                res = self._execute_command(command["name"], command)
            else:
                print(f"Skip command without name {command}")
            
            if res == 1:
                remaining_command_group.append(command)
        
        current_command_group.clear()
        current_command_group.extend(remaining_command_group)
        
        return current_command_group


    def update_and_draw(self, img: Image.Image):
        
        group: list[dict[str, Any]] | None = self.process_current_command_group()
        if group is not None:
            if len(group)==0:
                self.next_command_group()
            else:
                pass
                #print(f"Continue with group = {group}")
        
        self.draw(img)
    
    @abstractmethod
    def draw(self, img: Image.Image):
         pass

class Eye(AnimatedStuff):
    
    def __init__(self, x: int, y: int, radius: int, color: tuple[int, int, int]):
        
        AnimatedStuff.__init__(self)
        self.x: int = x  
        self.y: int = y
        self.radius: int = radius
        self.color: tuple[int, int, int] = color
        self.background :tuple[int, int, int] = (220, 220, 220)
        self.open:int = 30
        self.tilt:int=0
        self.pause_counter:int|None = None
        
        self.command_groups:list[list[dict[str, Any]]]=[]
    
    def add_command_group(self, group: list[dict[str, Any]]):
        self.command_groups.append(group)
        print(f"added command group => {self.command_groups}")
        
    def get_current_command_group(self) -> list[dict[str, Any]]|None:
        if len(self.command_groups)==0:
            #print("No More Commands")
            return None
        return self.command_groups[0]
    
    def next_command_group(self) -> list[dict[str, Any]] | None:
        if len(self.command_groups)==0:
            return None
        #print("Close command group")
        return self.command_groups.pop(0)
    
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
        
        elif name =="pause":
            if self.pause_counter is None:
                self.pause_counter = command.get("max", 100)
                command["max"]=0
                        
            if self.pause_counter<=0:
                self.pause_counter=None
                return 0
            self.pause_counter-=1
    
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
    
    def process_current_command_group(self) -> list[dict[str, Any]] | None:
        current_command_group:list[dict[str, Any]]|None = self.get_current_command_group()
        
        #print(f"Executing command group {current_command_group}")
        if current_command_group is None:
            return None        
        
        remaining_command_group:list[dict[str, Any]]=[]
        
        for command in current_command_group:
            
            # -1 = err / not found
            # 1 = ok, continue
            # 0 = ok, completed
            res: Literal[0, 1, -1]=-1
            if "name" in command.keys():
                res = self._execute_command(command["name"], command)
            else:
                print(f"Skip command without name {command}")
            
            if res == 1:
                remaining_command_group.append(command)
        
        current_command_group.clear()
        current_command_group.extend(remaining_command_group)
        
        return current_command_group


    def update_and_draw(self, img: Image.Image):
        
        group: list[dict[str, Any]] | None = self.process_current_command_group()
        if group is not None:
            if len(group)==0:
                self.next_command_group()
            else:
                pass
                #print(f"Continue with group = {group}")
        
        self.draw(img)
        
            
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

class Face():
    
    def __init__(self) -> None:
        pass
    

class EyesCmd(PictureScrollBaseCmd):
    def __init__(self) -> None:
        super().__init__("eyes", "Simple Eyes rendering")
        self.refresh_timer = 1 / 60.0
        self.scroll = False
        self.refresh = True
        
        self.eye_left = Eye(30, 22, 10, (0, 200, 255))
        self.eye_right = Eye(192-30, 22, 10, (0, 200, 255))

        command_grps: list[list[dict[str, Any]]] = [
            [{"name":"pause", "max": 60}]
             ,           
            [{"name":"shut", "speed": 2}]
            ,
            [{"name" : "open", "max": 70, "speed": 3}]
            ,
            [{"name" : "shut", "min": 50, "speed" : 3}]
            ,
            [{"name" : "move", "speed": 3}]
             , 
            [{"name":"pause", "max": 60}]
             ,
            [{"name" : "open", "max": 70, "speed": 4}]
            ,
            [{"name" : "move", "speed": -15}]
            , 
            [{"name" : "shut", "min": 50, "speed" : 3}, {"name" : "move", "speed": 15, "max": 0}]
            ,
            [{"name" : "open", "max": 100, "speed": 5}]
            
            ]
        
        for command_group in command_grps:
            self.eye_left.add_command_group(command_group)
            self.eye_right.add_command_group(command_group)
        
        self.eye_left.add_command_group(command_group)
        self.eye_right.add_command_group(command_group)
        

    def update(self, args=[], kwargs={}):
        # XXX
        super().update(args, kwargs)
        
        

    def generate_image(self, args: list = [], kwargs: dict = {}) -> Image.Image:

        width: int = get_total_matrix_width()
        height: int = get_total_matrix_height()

        img: Image.Image = Image.new("RGB", (width, height), color=(0, 0, 0))
        self.eye_left.update_and_draw(img)
        self.eye_right.update_and_draw(img)
        return img

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    args = parser.parse_args()
    cmd = EyesCmd()
    print("Execute MTA Command in main thread")
    cmd.execute(threading.Event(), timeout=60)