import time
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageChops
import os
import traceback

from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics

MATRIX_CHAINED = 3 
MATRIX_WIDTH = 64
MATRIX_HEIGHT = 64

def get_matrix_width():
    return MATRIX_WIDTH

def get_matrix_height():
    return MATRIX_HEIGHT

def get_matrix_chained():
    return MATRIX_CHAINED

def get_total_matrix_width():
    return get_matrix_width() * get_matrix_chained()

def get_total_matrix_height():
    return get_matrix_height() 

def getMatrixOptions():
    options = RGBMatrixOptions()
    options.rows = get_matrix_height()
    options.cols = get_matrix_width()
    options.chain_length = get_matrix_chained()
    options.parallel = 1
    options.hardware_mapping = 'regular'
    return options

def get_icons_dir(name=None):
    current_directory = os.path.dirname(os.path.realpath(__file__))  
    relative_path = os.path.join(current_directory, "../icons/") 
    absolute_path = os.path.abspath(relative_path) 
    if name:
        return f"{absolute_path}/{name}"
    
def get_fonts_dir(name=None):
    current_directory = dir_path = os.path.dirname(os.path.realpath(__file__))  
    relative_path = os.path.join(current_directory, "../fonts/") 
    absolute_path = os.path.abspath(relative_path) 
    if name:
        return f"{absolute_path}/{name}"
    
    return absolute_path

def trimImage(im, center=True):
    bgc = im.getpixel((0,0))
    bg = Image.new(im.mode, im.size, bgc)
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    bbox= (bbox[0]-1, bbox[1], bbox[2]+1, bbox[3])
    if bbox:
        if center:
            small = im.crop(bbox)
            bg = Image.new(im.mode, (small.size[0], im.size[1]), bgc)
            dy = int((im.size[1] - small.size[1])/2)
            bg.paste(small, (0,dy)) 
            return bg
        else:
            return im.crop(bbox)

    else:
        return im

class BaseCommand:

    def __init__(self, name, description, parameters=None):
        
        self.refresh_timer=1/60.0

        self.name = name
        self.description = description
        self.parameters = parameters or {}

        print(f"Load command with name {name}")


    def execute(self, stop_event, render=True):
        
        try:
            print(f"#######################\n Execute command '{self.name}'\n")
            self.update(self.parameters)

            if render:
                while not stop_event.is_set():
                    self.render(self.parameters)    
                    time.sleep(self.refresh_timer)
        except Exception as e:
            tb = traceback.format_exc()
            print(f"Error executing command '{self.name}': {str(e)}")
            print(tb)
            self.exception = e
            self.traceback = tb
    
    def update(self, parameters):
        pass

    def render(self, parameters):
        raise NotImplementedError

class MatrixBaseCmd(BaseCommand):

    def __init__(self, name, description, parameters=None):
        super().__init__(name, description, parameters)

        self.options = getMatrixOptions()
        self.matrix = RGBMatrix(options = self.options)
        self.fonts={}
    
    def getFont(self, name):
        if not name in self.fonts:
            self.fonts[name]= ImageFont.load(get_fonts_dir(name)) 
        return self.fonts[name]
         



class PictureScrollBaseCmd(MatrixBaseCmd):

    def __init__(self, name, description, parameters=None):
        super().__init__(name, description, parameters)
        self.speedX=1
        self.speedY=0
        self.scroll = True
        self.refresh = False
        
    def update(self, parameters):
        self.image = self.generate_image(parameters)
        self.double_buffer = self.matrix.CreateFrameCanvas()
        
        if self.scroll and self.speedX!=0:
            self.xpos = get_total_matrix_width()
        else:
            self.xpos = 0
        self.ypos = 0

    def generate_image(self, parameters):
        raise NotImplementedError
        
    def render(self, parameters):
        if self.scroll:
            self.xpos -= self.speedX
            if (self.xpos < -self.image.size[0]):
                self.xpos = get_total_matrix_width()
            
            self.ypos += self.speedY
            if (self.ypos < - self.image.size[1]):
                self.ypos = get_matrix_height()

        self.double_buffer.Clear()
        img_width, img_height = self.image.size
        self.double_buffer.SetImage(self.image, self.xpos, self.ypos)
        #self.double_buffer.SetImage(self.image, -self.xpos + img_width)

        self.double_buffer = self.matrix.SwapOnVSync(self.double_buffer)

        if self.refresh:
            self.image = self.generate_image(parameters)
          



class TextScrollBaseCmd(MatrixBaseCmd):

    def __init__(self, name, description, parameters=None):
        super().__init__(name, description, parameters)
        self.speedX=1
        self.speedY=0
        

    def update(self, parameters):
        self.text = self.get_text(parameters)
        self.double_buffer = self.matrix.CreateFrameCanvas()
        
        font = graphics.Font()
        font.LoadFont("/home/tiry/dev/rpi-rgb-led-matrix/fonts/9x18B.bdf")
        self.font = font

        self.textColor = graphics.Color(255, 255, 0)
        self.pos = self.double_buffer.width


    def get_text(self, parameters):
        raise NotImplementedError
        
    def render(self, parameters):

        double_buffer = self.double_buffer
        double_buffer.Clear()
        len = graphics.DrawText(double_buffer, self.font, self.pos, 10, self.textColor, self.text)
        self.pos -= 1
        if (self.pos + len < 0):
            self.pos = double_buffer.width
        double_buffer = self.matrix.SwapOnVSync(double_buffer)