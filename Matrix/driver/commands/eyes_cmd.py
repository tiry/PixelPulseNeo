import argparse
import threading
from typing import Any
from PIL import Image

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
        self.recommended_duration = 60

    def update(self, args=[], kwargs={}):
        # XXX
        super().update(args, kwargs)

    def generate_image(self, args: list = [], kwargs: dict = {}) -> Image.Image:

        width: int = get_total_matrix_width()
        height: int = get_total_matrix_height()

        img: Image.Image = Image.new("RGB", (width, height), color=(0, 0, 0))
        
        if not self.face.is_active():
            self.face.random_behavior()
        
        self.face.update_and_draw(img)
        return img

if __name__ == "__main__":
    parser = argparse.ArgumentParser()


    parser.add_argument("-c", "--commands", help="execute commands", action="store_true")
    parser.add_argument("-k", "--keyframes", help="execute keyframes", action="store_true")
    parser.add_argument("-e", "--emotions", help="execute emotions", action="store_true")
    
    args = parser.parse_args()
    cmd = EyesCmd()
    
    
    if args.commands:    
        
        command_grps: list[list[dict[str, Any]]] = [
                [{ "target":"eyes", "name":"pause", "max": 60}]
                ,           
                [{ "target":"eyes", "name":"shut", "speed": 2}]
                ,
                [{ "target":"eyes", "name" : "open", "max": 70, "speed": 3}]
                ,
                [{ "target":"eyes", "name" : "shut", "min": 50, "speed" : 3}]
                ,
                [{ "target":"eyes", "name" : "move", "speed": 3}]
                , 
                [{ "target":"eyes", "name":"pause", "max": 60}]
                ,
                [{ "target":"eyes", "name" : "open", "max": 70, "speed": 4}]
                ,
                [{ "target":"eyes", "name" : "move", "speed": -15}]
                , 
                [{ "target":"eyes", "name" : "shut", "min": 50, "speed" : 3}, {"name" : "move", "speed": 15, "max": 0}]
                ,
                [{ "target":"eyes", "name" : "open", "max": 100, "speed": 5}]
                
                ]
        
        cmd.face.load_cmds(command_grps)    
        mouth_cmds: list[list[dict[str, Any]]] = [
                [{ "target":"mouth", "name":"open", "max": 100}, {"name":"tilt", "speed": 2}]
                ,           
                [{"target":"mouth","name":"open", "speed": -1, "min": 80}, {"name":"tilt", "speed": -1, "min": 0}]
                ,
                [{"target":"mouth","name":"pause", "max": 60}],
                
                [{"target":"mouth", "name":"radius", "speed": -1, "min": 10},{"name":"open", "speed": 1, "max": 100}]
            ]
        cmd.face.load_cmds(mouth_cmds)    
        
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
        
        cmd.face.load_cmds(kframes)
    
    elif args.emotions:

        cmd.face.play_emotion("sleeping", 5, 100)
        #cmd.face.play_emotion("happy", 10, 100)
        cmd.face.play_emotion("awake", 5, 100)        
        #cmd.face.play_emotion("neutral", 5, 10)
        #cmd.face.play_emotion("happy", 30, 20)
        #cmd.face.play_emotion("surprised", 15, 20)
        #cmd.face.play_emotion("neutral", 15, 20)
        #cmd.face.play_emotion("happy", 30, 20)
        #cmd.face.play_emotion("wink_left", 10)
        #cmd.face.play_emotion("happy", 10, 20)
        #cmd.face.play_emotion("suspicious", 15, 20)
    
    else:

        #cmd.face.play_emotion("look_left", 15, 20)
        
        cmd.face.random_behavior()
        
        
    print("ExecuteCommand in main thread")
    cmd.execute(threading.Event(), timeout=60)