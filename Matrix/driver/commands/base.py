import os
import time
import traceback
from datetime import datetime
from typing import List
import logging
from PIL import Image
from PIL import ImageFont
from PIL import ImageChops
from Matrix.driver.utilz import configure_log, DARKCYAN
from Matrix.config import (
    MATRIX_CHAINED,
    MATRIX_HEIGHT,
    MATRIX_WIDTH,
    USE_EMULATOR,
    DEFAULT_REFRESH,
)

logger = logging.getLogger(__name__)
configure_log(logger, DARKCYAN, "Command", logging.INFO)

if USE_EMULATOR:
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
    import pygame
else:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics


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

def format_date():
    # Get the current date and time
    current_datetime = datetime.now()

    # Correct the day suffix (e.g., 1st, 2nd, 3rd, 4th, etc.)
    day = current_datetime.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    date_str = current_datetime.strftime(f"%A {day}{suffix} %B")

    return date_str

def format_date_short():
    # Get the current date and time
    current_datetime = datetime.now()
    date_str = current_datetime.strftime(f"%m/%d/%y")

    return date_str

def format_time():
    return datetime.now().strftime("%H:%M:%S")

def getMatrixOptions():
    options = RGBMatrixOptions()
    options.rows = get_matrix_height()
    options.cols = get_matrix_width()
    options.chain_length = get_matrix_chained()
    options.parallel = 1
    options.hardware_mapping = "regular"
    options.drop_privileges = False
    # slow down GPIO when running on PI3 to avoid bad rendering on chained panels
    options.gpio_slowdown = 2
    return options


def get_screenshots_dir(name=None):
    current_directory = os.path.dirname(os.path.realpath(__file__))
    relative_path = os.path.join(current_directory, "screenshots/")
    absolute_path = os.path.abspath(relative_path)
    if name:
        return f"{absolute_path}/{name}"
    return absolute_path


def get_icons_dir(name=None):
    current_directory = os.path.dirname(os.path.realpath(__file__))
    relative_path = os.path.join(current_directory, "../icons/")
    absolute_path = os.path.abspath(relative_path)
    if name:
        return f"{absolute_path}/{name}"
    return absolute_path


def get_fonts_dir(name=None):
    current_directory = os.path.dirname(os.path.realpath(__file__))
    relative_path = os.path.join(current_directory, "../fonts/")
    absolute_path = os.path.abspath(relative_path)
    if name:
        return f"{absolute_path}/{name}"

    return absolute_path

def get_capture_dir(name=None):
    current_directory = os.path.dirname(os.path.realpath(__file__))
    relative_path = os.path.join(current_directory, "../captures/")
    absolute_path = os.path.abspath(relative_path)
    if name:
        return f"{absolute_path}/{name}"

    return absolute_path



def trimImage(im, center=True):
    bgc = im.getpixel((0, 0))
    bg = Image.new(im.mode, im.size, bgc)
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    bbox = (bbox[0] - 1, bbox[1], bbox[2] + 1, bbox[3])
    if bbox:
        if center:
            small = im.crop(bbox)
            bg = Image.new(im.mode, (small.size[0], im.size[1]), bgc)
            dy = int((im.size[1] - small.size[1]) / 2)
            bg.paste(small, (0, dy))
            return bg
        else:
            return im.crop(bbox)

    else:
        return im

# XXX Check pygame is enabled
CAPTURE_PYGAME = True
CAPTURE_FREQ = 10

class BaseCommand:

    def __init__(self, name, description):
        self.refresh_timer = DEFAULT_REFRESH
        self.name = name
        self.description = description

        logger.debug(f"Load command with name {name}")

    def execute(self, stop_event, timeout=10, args=[], kwargs={}, render=True):
        t0 = time.time()
        try:
            logger.debug(
                f"#######################\n Execute command '{self.name}' {args} {kwargs}\n"
            )
            self.update(args, kwargs)
            if render:
                res = None
                frame_nb=0
                while not stop_event.is_set() and not (time.time() - t0) > timeout:
                    res = self.render(args=args, kwargs=kwargs)
                    frame_nb+=1
                    time.sleep(self.refresh_timer)
                    if CAPTURE_PYGAME and frame_nb%CAPTURE_FREQ==0:
                        self.capture_screen(tag= f"{frame_nb:05d}")
                return (res, None)
        except Exception as e:
            tb = traceback.format_exc()
            logger.error(f"Error BaseCommand.execute '{self.name}': {str(e)}")
            logger.error(tb)
            self.exception = e
            self.traceback = tb
            return (None, e)

    def update(self, args=[], kwargs={}):
        pass

    def render(self, args=[], kwargs={}):
        raise NotImplementedError

    def getScreenShots(self) -> List[str]:
        result = []
        base_dir = get_screenshots_dir()
        # logger.debug(f"base_dir = {base_dir}")
        # logger.debug(f"=> = {os.listdir(base_dir)}")

        for file in os.listdir(base_dir):
            if file.startswith(self.name):
                result.append(file)
        return result

    def getScreenShot(self, name):
        base_dir = get_screenshots_dir()
        file = f"{base_dir}/{name}"
        return file

    def getScreenShotBlob(self, name):
        base_dir = get_screenshots_dir()
        file = f"{base_dir}/{name}"
        return open(file, "rb")

    def capture_screen(self, tag= None ):
        screen = pygame.display.get_surface()
        target_path= f"{get_capture_dir()}/{self.name}_{tag}.png"
        pygame.image.save(screen, target_path)



# We want a sigleton matrix because we want to share the same matrix between all the commands
# Failing to do so works with the Matrix emulator but gives super bad result with the real hardware
# XXX make thread safe
matrix_singleton = RGBMatrix(options=getMatrixOptions())


class MatrixBaseCmd(BaseCommand):
    def __init__(self, name, description):
        super().__init__(name, description)

        self.options = getMatrixOptions()
        self.matrix = matrix_singleton
        # self.matrix = RGBMatrix(options = self.options)
        self.fonts = {}

    def getFont(self, name):
        if name not in self.fonts:
            self.fonts[name] = ImageFont.load(get_fonts_dir(name))
        return self.fonts[name]


class PictureScrollBaseCmd(MatrixBaseCmd):
    def __init__(self, name, description):
        super().__init__(name, description)
        self.speedX = 1
        self.speedY = 0
        self.scroll = True
        self.refresh = False
        self.image_counter = 0


    def _resize_icon(self, icon: Image, max_height:int = None , max_width:int= None ):
        """
        Resize the icon to fit in max_height or max_width while keeping the aspect ratio
        """
        
        icon_width, icon_height = icon.size
        if max_height:
            icon_width = int(icon_width / (icon_height / max_height))
            icon_height = max_height
        elif max_width:
            icon_height = int(icon_height / (icon_width / max_width))
            icon_width = max_width

        #print(f"resize to {icon_width}x{icon_height}")
        icon = icon.resize((icon_width, icon_height), Image.LANCZOS)
        return icon
    
    def _compute_text_position(self, text:str, font: ImageFont, available_width:int):
        """

        Compute the text position to center it in the available width

        Args:
            text (_type_): _description_
            font (_type_): _description_
            available_width (_type_): _description_

        Returns:
            _type_: _description_
        """

        _, _, text_width, text_height = font.getbbox(text)            
        if text_width < available_width:
            return int((available_width-text_width)/2)
        return 0

    def update(self, args=[], kwargs={}):
        self.image = self.generate_image(args, kwargs)
        self.double_buffer = self.matrix.CreateFrameCanvas()

        #print(f"canvas adapter = {self.double_buffer.display_adapter.__surface}")
        #print(f"{pygame.display}")
        
        #adapter = self.double_buffer.display_adapter


        if self.scroll and self.speedX != 0:
            self.xpos = get_total_matrix_width()
        else:
            self.xpos = 0
        self.ypos = 0
        return "update image source data"

    def generate_image(self, args=[], kwargs={}):
        raise NotImplementedError

    def render(self, args=[], kwargs={}):
        if self.scroll:
            self.xpos -= self.speedX
            if self.xpos < -self.image.size[0]:
                self.xpos = get_total_matrix_width()

            self.ypos += self.speedY
            if self.ypos < -self.image.size[1]:
                self.ypos = get_matrix_height()

        self.double_buffer.Clear()
        img_width, img_height = self.image.size
        self.double_buffer.SetImage(self.image, self.xpos, self.ypos)

        self.double_buffer = self.matrix.SwapOnVSync(self.double_buffer)

        if self.refresh:
            self.image_counter += 1
            self.image = self.generate_image(args, kwargs)
        return f"rendered {self.image_counter} images"


class TextScrollBaseCmd(MatrixBaseCmd):
    def __init__(self, name, description):
        super().__init__(name, description)
        self.speedX = 1
        self.speedY = 0

    def update(self, args=[], kwargs={}):
        self.text = self.get_text(args=[], kwargs={})
        self.double_buffer = self.matrix.CreateFrameCanvas()

        font = graphics.Font()
        font.LoadFont("/home/tiry/dev/rpi-rgb-led-matrix/fonts/9x18B.bdf")
        self.font = font

        self.textColor = graphics.Color(255, 255, 0)
        self.pos = self.double_buffer.width

    def get_text(self, args=[], kwargs={}):
        raise NotImplementedError

    def render(self, args=[], kwargs={}):
        double_buffer = self.double_buffer
        double_buffer.Clear()
        len = graphics.DrawText(
            double_buffer, self.font, self.pos, 10, self.textColor, self.text
        )
        self.pos -= 1
        if self.pos + len < 0:
            self.pos = double_buffer.width
        double_buffer = self.matrix.SwapOnVSync(double_buffer)
