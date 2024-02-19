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
    
    
    def execute_command(self, name:str, command:dict[str, Any]) -> Literal[0, 1, -1]:
    
        if name =="pause":
            if self.pause_counter is None:
                self.pause_counter = command.get("max", 100)
                command["max"]=0
                        
            if self.pause_counter<=0:
                self.pause_counter=None
                return 0
            self.pause_counter-=1
            return 1
        elif name =="keyframe":
            remaining_frames:int= command.get("frames", 0)
            res: int = 0
            if remaining_frames==0:
                return res
            for name in command.keys():
                if name in ["frames", "target", "name"]:
                    continue
                cval:int = getattr(self, name)
                if abs(cval- command[name])>1:
                    delta = (command[name] - cval)/remaining_frames
                    cval += delta 
                    setattr(self, name, cval)
                    res = 1
            remaining_frames-=1
            command["frames"] = remaining_frames
            return res
        else:
            return self._execute_command(name, command)

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
                res = self.execute_command(command["name"], command)
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
    
        angle:float = 90 * self.open/100
        
        max_width: int = 2* self.radius
        margin:int = int((get_total_matrix_width() - max_width) / 2)
        #draw.arc((margin, 34,get_total_matrix_width()-margin, 62), self.tilt + 90-angle, self.tilt + 90 + angle, fill=(255,0,0), width=2)
        
        draw.chord((margin, 34,get_total_matrix_width()-margin, 62), self.tilt + 90-angle, self.tilt + 90 + angle, fill=(200,200,200), width=2)
        draw.arc((margin, 34,get_total_matrix_width()-margin, 62), self.tilt + 90-angle, self.tilt + 90 + angle, fill=(255,220,200), width=2)
                
        #chord
        
class Face():
    
    def __init__(self) -> None:
        
        self.left = Eye(30, 22, 10, (0, 200, 255))
        self.right = Eye(192-30, 22, 10, (0, 200, 255))
        self.mouth = Mouth(0,0,30, 80, (0, 200, 255))

    def update_and_draw(self, img:Image.Image):
        self.left.update_and_draw(img)
        self.right.update_and_draw(img)
        self.mouth.update_and_draw(img)
        return
    
    def load_eyes_command_group(self, command_grps:  list[list[dict[str, Any]]] ):
        for command_group in command_grps:
            self.left.add_command_group(command_group)
            self.right.add_command_group(command_group)
        
    def load_mouth_command_group(self, command_grps:  list[list[dict[str, Any]]] ):
        for command_group in command_grps:
            self.mouth.add_command_group(command_group)
            
    def load_keyframes(self,keyframe_groups:list[list[dict[str, Any]]]):
         for keyframe_group in keyframe_groups:
            sorted_kf: dict[str, list[dict[str, Any]]] = {
                "left" : [],
                "right" : [],
                "mouth" : []
            }
            for kf in keyframe_group:
                target:str|None = kf.get("target", None)
                targets:list[str] = []
                if target is None:
                    print(f"Key frame with no target {kf}")
                    continue
                if target == "eyes":
                    targets.append("left")
                    targets.append("right")
                elif target == "all":
                    targets.extend(["left", "right", "mounth"])
                else:
                    targets.append(target)
                for target in targets:
                    sorted_kf[target].append(kf)
            
            for target in sorted_kf:
                getattr(self, target).add_command_group(sorted_kf[target])
               
                
class EyesCmd(PictureScrollBaseCmd):
    
    
    def __init__(self) -> None:
        super().__init__("eyes", "Simple Eyes rendering")
        self.refresh_timer = 1 / 60.0
        self.scroll = False
        self.refresh = True 
        self.face = Face()
    

    def update(self, args=[], kwargs={}):
        # XXX
        super().update(args, kwargs)
        
        

    def generate_image(self, args: list = [], kwargs: dict = {}) -> Image.Image:

        width: int = get_total_matrix_width()
        height: int = get_total_matrix_height()

        img: Image.Image = Image.new("RGB", (width, height), color=(0, 0, 0))
        #self.eye_left.update_and_draw(img)
        #self.eye_right.update_and_draw(img)
        self.face.update_and_draw(img)
        return img

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--commands", help="execute commands", action="store_true")
    parser.add_argument("-k", "--keyframes", help="execute keyframes", action="store_true")
    
    args = parser.parse_args()
    cmd = EyesCmd()
    
    
    
    if args.commands:    
        
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
            
        cmd.face.load_eyes_command_group(command_grps)        
        mouth_cmds: list[list[dict[str, Any]]] = [
                [{"name":"open", "max": 100}, {"name":"tilt", "speed": 2}]
                ,           
                [{"name":"open", "speed": -1, "min": 80}, {"name":"tilt", "speed": -1, "min": 0}]
                ,
                [{"name":"pause", "max": 60}],
                
                [{"name":"radius", "speed": -1, "min": 10},{"name":"open", "speed": 1, "max": 100}]
            ]
        cmd.face.load_mouth_command_group(mouth_cmds)
    
    elif args.keyframes:
        
        kframes:list[list[dict[str, Any]]] =  [
            [ {"name":"keyframe", "target":"eyes", "open": 100, "frames":60},
            {"name":"keyframe", "target":"mouth", "open": 100, "frames":60}]
            ,
            [ {"name":"keyframe", "target":"eyes", "open": 100, "frames":60},
            {"name":"keyframe", "target":"mouth", "open": 100, "frames":60}],
             [ {"name":"keyframe", "target":"left", "open": 5, "frames":30},
            ],
            [ {"name":"keyframe", "target":"left", "open": 100, "frames":30},
            ]
            
        ]     
        
        cmd.face.load_keyframes(kframes)
    
    print("Execute MTA Command in main thread")
    cmd.execute(threading.Event(), timeout=60)