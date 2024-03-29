import argparse
import threading
from typing import Any, Literal
from PIL import Image, ImageDraw
from abc import ABC, abstractmethod

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
        self.keyframe_counter:int | None = None
    
    def add_command_group(self, group: list[dict[str, Any]]):
        self.command_groups.append(group)
        #print(f"added command group => {self.command_groups}")
        
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
    
    def get_keyframe_counter(self) -> int | None:
        return self.keyframe_counter
    
    def get_or_set_keyframe_counter(self, value:int) -> int:
        if self.keyframe_counter is None:
            self.keyframe_counter = value
        return self.get_keyframe_counter() #type: ignore
    
    def decrement_keyframe(self) -> None:
        if self.keyframe_counter is not None:
            self.keyframe_counter -=1

    def execute_command(self, name:str, command:dict[str, Any]) -> Literal[0, 1, -1]:
    
        if name =="pause":
            #print(f"pause {self.__class__.__name__}")
            if self.pause_counter is None:
                self.pause_counter = command.get("max", 100)
            if self.pause_counter<=0:
                self.pause_counter=None
                #print(f"END pause {self.__class__.__name__}")
                #print(self.command_groups)
                return 0
            self.pause_counter-=1
            return 1
        elif name =="keyframe":
            remaining_frames:int= self.get_or_set_keyframe_counter(command.get("frames", 0))
            res: int = 0
            if remaining_frames > 0:
                for name in command.keys():
                    if name in ["frames", "target", "name"]:
                        continue
                    cval:float = getattr(self, name)
                    if abs(cval- command[name])>1:
                        delta = (command[name] - cval)/remaining_frames
                        cval += delta 
                        setattr(self, name, cval)
                        res = 1            
            if res == 0:
                #print(f"{self.__class__.__name__} reset key frame counter" )
                self.keyframe_counter = None
            self.decrement_keyframe()
            #print(f"{self.__class__.__name__} remaining frames {remaining_frames}")
            return res
        else:
            #print(f"{self.__class__.__name__} command {name}") 
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
