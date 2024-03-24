import time
import math
from PIL import Image, ImageDraw, ImageFont
from Matrix.driver.commands.base import (
    get_fonts_dir,
)

def darker(color:tuple, pct:int) -> tuple:
    return tuple([int(c*pct/100) for c in color])

def render_letter_flaps(letter:str, font, fg_color=(0,0,0), bg_color=(255,255,255)) -> tuple[Image.Image, Image.Image]:
      
    bb: tuple[int, int, int, int]=font.getbbox("A")
        
    w:int = bb[2]+4
    h:int = font.size
    bg: Image.Image = Image.new("RGB", (w, h), color=(0, 0, 0))    
    draw: ImageDraw.ImageDraw = ImageDraw.Draw(bg)
    
    if letter == " ":
        draw.rectangle((1,1,w-1,h-1), fill=darker(bg_color,10), outline=darker(bg_color, 5))
        
        draw.line((0, int(h/2), h, int(h/2)), fill=fg_color)
    else:
        if letter == "▓":
            letter = " "
        draw.rectangle((1,1,w-1,h-1), fill=bg_color, outline=darker(bg_color, 70))
        draw.text((2, -1), letter, font=font, fill=fg_color)
        draw.line((0, int(h/2), h, int(h/2)), fill=fg_color)
            
    bg.putpixel((1, 1), (0, 0, 0))
    bg.putpixel((23, 1), (0, 0, 0))
    bg.putpixel((1, 31), (0, 0, 0))
    bg.putpixel((23, 31), (0, 0, 0))

    flap1: Image.Image = bg.copy().crop((0,0,w, int(h/2)))
    flap2: Image.Image = bg.crop((0,int(h/2),w, h))
            
    return (flap1, flap2)   


class FlapRoll():
    
    def __init__(self, letters = "▓ ABCDEFGHIJKLMNOPQRSTUVWXYZ?:!()#$%*+=_-{}[]<>", font_name:str="LiberationMono-Regular.ttf", height=32) -> None:
        
        flaps: list[Image.Image] = []
        letter_index:dict[str,tuple[int, int]] = {}
        font: ImageFont.FreeTypeFont = ImageFont.truetype(get_fonts_dir(font_name), height)
        for letter in letters:
            parts: tuple[Image.Image, Image.Image] = render_letter_flaps(letter, font)
            flaps.extend(parts)
            letter_index[letter] = (len(flaps)-2, len(flaps)-1)
            
        self.flaps: list[Image.Image] = flaps
        self.letter_index: dict[str, tuple[int, int]] = letter_index
        self.height = height
        self.width = flaps[0].width

    def get_flaps_img(self, letter:str) -> tuple[Image.Image,Image.Image]:
        return self.flaps[self.letter_index[letter][0]], self.flaps[self.letter_index[letter][1]]
    
    def get_flaps_by_key(self, letter:str) -> int:
        return self.letter_index[letter][0]
    
    def get_flap_by_index(self, index:int) -> Image.Image:
        index = (index) % len(self.flaps)
        return self.flaps[index]
      
    def turn(self, index:int) -> int:
        return (index + 2) % len(self.flaps)
        

DEFAULT_FLAP_ROLL = FlapRoll("▓ ABCDEFGHIJKLMNOPQRSTUVWXYZ?:!()#*<>-")

class FlapBox():

    def __init__(self, flap_roll:FlapRoll = DEFAULT_FLAP_ROLL):
        self.current_pos:int=0
        self.target_pos:int=0
        self.flap_roll: FlapRoll = flap_roll    
        self.angle=0
    
    def size(self) -> tuple[int,int]:
        return (self.flap_roll.width, self.flap_roll.height)
    
    def render(self) -> Image.Image:
        
        w = self.flap_roll.width
        h = self.flap_roll.height
        
        rendered = Image.new("RGB", (w, h), color=(0, 0, 0))    
    
        if self.angle==0:
            rendered.paste(self.flap_roll.get_flap_by_index(self.current_pos), (0,0))
            rendered.paste(self.flap_roll.get_flap_by_index(self.current_pos+1), (0,16))
        else:
            
            # up flap
            rendered.paste(self.flap_roll.get_flap_by_index(self.current_pos+2), (0,0))
            
            # down flap
            rendered.paste(self.flap_roll.get_flap_by_index(self.current_pos+1), (0,16))
            
            # moving flap
            if self.angle<90:
                flapping: Image.Image = self.flap_roll.get_flap_by_index(self.current_pos)
                target_height:int = int(flapping.height*math.cos(math.radians(self.angle)))
                flapping = flapping.resize((flapping.width, target_height))        
                rendered.paste(flapping, (0,16-flapping.height))
            elif self.angle>90:
                if self.angle>180:
                    self.angle = 180
                flapping: Image.Image = self.flap_roll.get_flap_by_index(self.current_pos+3)
                target_height: int = -int(flapping.height* math.cos(math.radians(self.angle)))
                flapping = flapping.resize((flapping.width, target_height))        
                rendered.paste(flapping, (0,16))
    
        return rendered
                
    def set_target(self, letter:str) -> None:   
        self.target_pos = self.flap_roll.get_flaps_by_key(letter)
    
    def turn(self) -> bool:
        if (self.current_pos != self.target_pos):
            #print("turn")
            self.angle+=20
            if self.angle > 180:
                self.angle = 0
                self.current_pos = self.flap_roll.turn(self.current_pos)
            return True
        return False
        
class FlapPannel():
    
    def __init__(self, width:int=8, height:int=2, message:str|None = None) -> None:
        self.width: int = width
        self.height: int = height
        self.flap_boxes:list[FlapBox] = []
        self.messages:list[str] = []
        if message:
            self.append_text(message)
        self.flapbox_size:tuple[int,int]=(0,0)
        self.init_display()
        
    def init_display(self):
        self.flap_boxes=[]
        for _ in range(self.width*self.height):
            box = FlapBox()
            self.flap_boxes.append(box)
        self.update_target_text()
        self.flapbox_size = self.flap_boxes[0].size()
    
    def append_text(self, text:str) -> None:
        self.messages.append(text.upper())
    
    def update_target_text(self):
        
        target:str =" "*self.width*self.height
        lines: list[str] = self.get_next_words()
        if len(lines)>0:
            target = ''.join(lines)
            
        for idx, letter in enumerate(target):
            self.flap_boxes[idx].set_target(letter)
    
    def get_next_words(self ) -> list[str]:
        
        messages: list[str] = self.messages
        width: int = self.width
        height:int = self.height
         
        # get the current message
        if len(messages) > 0:
            current_message = messages[0]
        else:
            current_message = ""

        # get the next words
        (next_words,remaining_message) = self._get_next_words(current_message, width, height)
        
        if len(remaining_message)==0:
            if len(messages)>0:
                messages.pop(0)
        
        return next_words          
    
    def _get_next_words(self, message:str, width:int=8, height:int=2):

        # next words that can fit on a width x height character display
        next_words:list[str] = [] 
        
        words: list[str] = message.split()
        line: str  = ''
        remaining_words = []

        for word in words:
            if len(line + word) <= width:
                line += word + ' '
            else:
                if line:  # Add the current line if it's not empty
                    next_words.append(line.strip())
                if len(next_words) < height:  # Start a new line if there's space
                    line = word + ' '
                else:  # No more space in display, add word to remaining words
                    remaining_words.append(word)
        if line:  # Add any remaining line content
            next_words.append(line.strip())

        # Center the words on each line
        for i in range(len(next_words)):
            next_words[i] = next_words[i].center(width)

        remaining_message:str = ' '.join(remaining_words).strip()
        return next_words, remaining_message
    
    def render(self, background:Image.Image) -> None:
        changes = False
        
        w:int = self.flapbox_size[0]
        h:int = self.flapbox_size[1]
        
        for i, box in enumerate(self.flap_boxes):
            renered_flaps:Image.Image = box.render()
            if i < self.width:
                background.paste(renered_flaps, (i*w,0))
            else:
                background.paste(renered_flaps, ((i-8)*w,h))
            changed: bool = box.turn()
            changes: bool = changes or changed
        
        if changes is False:
            #print("COMPLETED")
            time.sleep(1)
            self.update_target_text()
            
    
