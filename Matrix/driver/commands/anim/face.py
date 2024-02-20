from typing import Any, Literal
from PIL import Image, ImageDraw
from Matrix.driver.commands.anim.eye import Eye
from Matrix.driver.commands.anim.mouth import Mouth

class Face():
    
    def __init__(self) -> None:
        
        self.left = Eye(30, 22, 10, (0, 200, 255))
        self.right = Eye(192-30, 22, 10, (0, 200, 255))
        self.mouth = Mouth(0,0,30, 40, (0, 200, 255))

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
                #if target is None:
                #    print(f"Key frame with no target {kf}")
                #    targets.extend(["left", "right", "mounth"])
                if target == "eyes":
                    targets.append("left")
                    targets.append("right")
                elif target == "all" or target is None:
                    targets.extend(["left", "right", "mouth"])
                else:
                    targets.append(target)
                for target in targets:
                    sorted_kf[target].append(kf)
            
            for target in sorted_kf:
                getattr(self, target).add_command_group(sorted_kf[target])
    
    def get_emotion_keyframe(self, name:str, frames=60) -> list[dict[str, Any]]:
        
        emotion_dictionnary:dict[str, list[dict[str, Any]]] = {
            "surprised" :  [ 
                { "target":"eyes", "open": 100},
                { "target":"mouth", "open": 100,  "open2": 100, "radius" : 8, "tilt": 0 }],
            "neutral" :  [ 
                { "target":"eyes", "open": 70, "tilt": 0},
                { "target":"mouth", "open": 30, "open2": 10, "radius" : 45, "tilt": 0 }],
            "wink_left" :  [ 
                { "target":"left", "open": 0, "tilt": 0},
                {"target":"right", "open": 80, "tilt": 0},
                { "target":"mouth", "open": 30, "radius" : 10, "tilt": 30 }]

        }
        
        keyframes: list[dict[str, Any]] = emotion_dictionnary[name]
        
        result:list[dict[str, Any]] = []
        for kf in keyframes:
            result.append(dict( {"name":"keyframe", "frames":frames }, **kf))
        
        return result
