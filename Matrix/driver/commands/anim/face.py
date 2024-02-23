from typing import Any, Literal
import copy
import random
from PIL import Image, ImageDraw
from Matrix.driver.commands.anim.eye import Eye
from Matrix.driver.commands.anim.mouth import Mouth

emotion_dictionnary:dict[str, list[dict[str, Any]]] = {
            "surprised" :  [ 
                { "target":"eyes", "open": 100},
                { "target":"mouth", "open": 100, "radius" : 20, "tilt": 0 }],
            "neutral" :  [ 
                { "target":"eyes", "open": 70, "tilt": 0},
                { "target":"mouth", "open": 10, "radius" : 45, "tilt": 0 }],
            "wink_left" :  [ 
                { "target":"left", "open": 0, "tilt": 0},
                {"target":"right", "open": 80, "tilt": 0},
                { "target":"mouth", "open": 30, "radius" : 45, "tilt": 30 }],
            "happy" :  [ 
                { "target":"eyes", "open": 70},
                { "target":"mouth", "open": 40, "tilt": 10, "radius" : 30 }],
            "suspicious" :  [ 
                { "target":"eyes", "open": 40},
                { "target":"mouth", "open": 5, "tilt": 0, "radius" : 45 }]

        }
   
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
    
    def _get_actors(self) -> list[str]:
        return ["left", "right", "mouth"]
    
    def _dispatch(self, cmd_group:list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        sorted_kf: dict[str, list[dict[str, Any]]] = {}
        for actor in self._get_actors():
            sorted_kf[actor]= []
        for kf in cmd_group:
            target:str|None = kf.get("target", None)
            targets:list[str] = []
            if target == "eyes":
                targets.append("left")
                targets.append("right")
            elif target == "all" or target is None:
                targets.extend(self._get_actors())
            else:
                targets.append(target)
            for target in targets:
                nkf = copy.deepcopy(kf)
                nkf["target"] = target
                sorted_kf[target].append(nkf)
        return sorted_kf

    
    def load_cmds(self,keyframe_groups:list[list[dict[str, Any]]]):
         for keyframe_group in keyframe_groups:
            sorted_kf: dict[str, list[dict[str, Any]]] = self._dispatch(keyframe_group)
            for target in sorted_kf:
                getattr(self, target).add_command_group(sorted_kf[target])
    
    def get_emotion_keyframe(self, name:str, frames=60) -> list[dict[str, Any]]: 
        
        keyframes: list[dict[str, Any]] = emotion_dictionnary[name]
        
        result:list[dict[str, Any]] = []
        for kf in keyframes:
            result.append(dict( {"name":"keyframe", "frames":frames }, **kf))
        
        return result

    def play_emotion(self, emotion_name:str, frames:int=10, pause:int|None = None):
        
        emotion: list[dict[str, Any]] = self.get_emotion_keyframe(name=emotion_name, frames=frames)
        
        if emotion is None:
            return
        
        kframes:list[list[dict[str, Any]]] =  []     
        
        kframes.append(emotion)
        
        if pause is not None:
            kframes.append([{"name":"pause", "max": pause}])
        
        self.load_cmds(kframes)
        
    def random_behavior(self):
        
        emotions:list[str] = list(emotion_dictionnary.keys())
        
        for i in range(10):
            
            emotion = emotions[random.randint(0, len(emotions)-1)]
            self.play_emotion(emotion, frames=random.randint(10, 90), pause = random.randint(0, 30))
        
        