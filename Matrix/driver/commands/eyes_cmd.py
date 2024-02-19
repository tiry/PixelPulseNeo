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

from Matrix.driver.commands.anim.face import Face
        
                
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
    parser.add_argument("-e", "--emotions", help="execute emotions", action="store_true")
    
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
    
    elif args.emotions:
        
        kframes:list[list[dict[str, Any]]] =  [
        ]     
        
        kframes.append(cmd.face.get_emotion_keyframe("neutral", 60))
        
        kframes.append(cmd.face.get_emotion_keyframe("surprised", 60))

        kframes.append(cmd.face.get_emotion_keyframe("neutral", 60))
        
        kframes.append(cmd.face.get_emotion_keyframe("wink_left", 30))
        
        kframes.append(cmd.face.get_emotion_keyframe("neutral", 30))

        
        cmd.face.load_keyframes(kframes)
    
    print("Execute MTA Command in main thread")
    cmd.execute(threading.Event(), timeout=60)