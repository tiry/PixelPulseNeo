import os
import time
import traceback
import json
from datetime import datetime
from typing import List, Any
import logging
from io import BufferedReader
import threading
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageChops
from Matrix.driver.utilz import configure_log, DARKCYAN
from Matrix.driver.commands.msg_stack import MessageStack, get_message_stack
from Matrix.driver import power
from Matrix.config import (
    MATRIX_CHAINED,
    MATRIX_HEIGHT,
    MATRIX_WIDTH,
    USE_EMULATOR,
    DEFAULT_REFRESH,
)

logger: logging.Logger = logging.getLogger(__name__)
configure_log(logger, DARKCYAN, "Command", logging.INFO)

if USE_EMULATOR:
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
    import pygame
else:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics  # type: ignore


def get_matrix_width() -> int:
    return MATRIX_WIDTH


def get_matrix_height() -> int:
    return MATRIX_HEIGHT


def get_matrix_chained() -> int:
    return MATRIX_CHAINED


def get_total_matrix_width() -> int:
    return get_matrix_width() * get_matrix_chained()


def get_total_matrix_height() -> int:
    return get_matrix_height()


def format_date() -> str:
    # Get the current date and time
    current_datetime: datetime = datetime.now()

    # Correct the day suffix (e.g., 1st, 2nd, 3rd, 4th, etc.)
    day: int = current_datetime.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix: str = ["st", "nd", "rd"][day % 10 - 1]
    date_str: str = current_datetime.strftime(f"%A {day}{suffix} %B")

    return date_str


def format_date_short() -> str:
    # Get the current date and time
    current_datetime: datetime = datetime.now()
    date_str: str = current_datetime.strftime("%m/%d/%y")

    return date_str


def format_time() -> str:
    return datetime.now().strftime("%H:%M:%S")


def getMatrixOptions() -> RGBMatrixOptions:
    options: RGBMatrixOptions = RGBMatrixOptions()
    options.rows = get_matrix_height()
    options.cols = get_matrix_width()
    options.chain_length = get_matrix_chained()
    options.parallel = 1
    options.hardware_mapping = "regular"
    if not USE_EMULATOR:
        options.drop_privileges = False  # type: ignore
        # slow down GPIO when running on PI3 to avoid bad rendering on chained panels
        options.gpio_slowdown = 2  # type: ignore
    return options


def get_screenshots_dir(name=None) -> str:
    current_directory: str = os.path.dirname(os.path.realpath(__file__))
    relative_path: str = os.path.join(current_directory, "screenshots/")
    absolute_path: str = os.path.abspath(relative_path)
    if name:
        return f"{absolute_path}/{name}"
    return absolute_path


def get_icons_dir(name=None) -> str:
    current_directory: str = os.path.dirname(os.path.realpath(__file__))
    relative_path: str = os.path.join(current_directory, "../icons/")
    absolute_path: str = os.path.abspath(relative_path)
    if name:
        return f"{absolute_path}/{name}"
    return absolute_path


def get_fonts_dir(name=None) -> str:
    current_directory: str = os.path.dirname(os.path.realpath(__file__))
    relative_path: str = os.path.join(current_directory, "../fonts/")
    absolute_path: str = os.path.abspath(relative_path)
    if name:
        return f"{absolute_path}/{name}"

    return absolute_path


def get_capture_dir(name=None) -> str:
    current_directory: str = os.path.dirname(os.path.realpath(__file__))
    relative_path: str = os.path.join(current_directory, "../captures/")
    absolute_path: str = os.path.abspath(relative_path)
    if name:
        return f"{absolute_path}/{name}"

    return absolute_path


def trim_image(im: Image.Image, center: bool = True) -> Image.Image:
    bgc = im.getpixel((0, 0))
    bg: Image.Image = Image.new(im.mode, im.size, bgc)
    diff: Image.Image = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox: tuple[int, int, int, int] | None = diff.getbbox()
    if bbox:
        bbox = (bbox[0] - 1, bbox[1], bbox[2] + 1, bbox[3])
        if center:
            small: Image.Image = im.crop(bbox)
            bg = Image.new(im.mode, (small.size[0], im.size[1]), bgc)
            dy = int((im.size[1] - small.size[1]) / 2)
            bg.paste(small, (0, dy))
            return bg
        else:
            return im.crop(bbox)
    else:
        return im

# XXX Check pygame is enabled
CAPTURE_PYGAME = False
CAPTURE_FREQ = 60

# We want a sigleton matrix because we want to share the same matrix between all the commands
# Failing to do so works with the Matrix emulator but gives super bad result with the real hardware
# XXX make thread safe
_matrix_singleton: RGBMatrix | None = None
_matrix_lock: threading.RLock = threading.RLock()

def get_matrix_singleton() -> RGBMatrix:
    with _matrix_lock:
        global _matrix_singleton
        if _matrix_singleton is None:
            _matrix_singleton = RGBMatrix(options=getMatrixOptions())
        return _matrix_singleton

# No Lock version 
def get_matrix() -> RGBMatrix:
    global _matrix_singleton
    if _matrix_singleton is None:
        return get_matrix_singleton()
    return _matrix_singleton

def release_matrix_singleton() -> None:
    with _matrix_lock:
        global _matrix_singleton
        if _matrix_singleton is not None:
            _matrix_singleton.Clear()
            _matrix_singleton = None    

class BaseCommand:
    def __init__(self, name: str, description: str) -> None:
        
        # power on the LED Matrix if needed
        power.on()
        
        self.refresh_timer: float = DEFAULT_REFRESH
        self.name: str = name
        self.description: str = description

        self.recommended_duration:int=10
        
        logger.debug(f"Load command with name {name}")
        
        self.logger: logging.Logger=logger
        self.execution_done:bool = False
        self.t0: float=time.time()
        self.t_last_render: float=time.time()
        self.reset_state()
        

    def get_recommended_duration(self) -> int:
        return self.recommended_duration
    
    def reset_state(self) -> None:
        self.execution_done=False
        self.t0=time.time()

    def wait_for_next_frame(self):
        
        frame_interval = time.time() - self.t_last_render

        if frame_interval < self.refresh_timer:
            pause_time = self.refresh_timer - frame_interval
            #print(f"pausing {pause_time}s")
            time.sleep(pause_time)
        return
        
    def execute(
        self,
        stop_event: threading.Event,
        timeout: int = 10,
        args: list = [],
        kwargs: dict = {},
        render: bool = True,
    ) -> tuple | None:
        t0: float = time.time()
        self.reset_state()
        
        try:
            logger.debug(
                f"#######################\n Execute command '{self.name}' {args} {kwargs}\n"
            )
            self.update(args, kwargs)
            if render:
                res = None
                frame_nb = 0
                while not self.execution_done and not stop_event.is_set() and not (time.time() - t0) > timeout:
                    res = self.render(args=args, kwargs=kwargs)
                    frame_nb += 1
                    t_last_render=time.time()
                    
                    self.wait_for_next_frame()
                    self.t_last_render=t_last_render
                    
                    #time.sleep(self.refresh_timer)
                    
                    # hack to generate screenshots
                    if CAPTURE_PYGAME and frame_nb % CAPTURE_FREQ == 0:
                        self.capture_screen(tag=f"{frame_nb:05d}")
                    
                    self.process_message_if_needed()
                    if frame_nb >0 and frame_nb %500==0:
                        fps: float = int(frame_nb / (time.time() - t0)) 
                        logger.info(f"[{self.name}] fps={fps}")
                        #print(f"[{self.name}] FPS = {fps}")
                return (res, None)
        except Exception as e:
            tb: str = traceback.format_exc()
            logger.error(f"Error BaseCommand.execute '{self.name}': {str(e)}")
            logger.error(tb)
            self.exception: Exception = e
            self.traceback: str = tb
            return (None, e)
    
    def process_message_if_needed(self):
        msg: dict[str, str] | None = get_message_stack().pop()    
        if msg is not None:
            if msg["command_name"] != self.name:
                logger.debug(f"dropping message: {msg}")
            else:
                self.handle_message(msg)
 
    def handle_text_payload(self, msg:str):    
        pass
    
    def handle_json_payload(self, payload:Any):
        pass        

    def handle_message(self, msg: dict[str, str]) -> None:
        self.logger.info(f" Received message {msg}")
        txt: str | None = msg.get("message", None)
        if txt is not None:
            try:
                object = json.loads(txt)
                self.handle_json_payload(object)
            except json.JSONDecodeError:
                if type(txt) == bytes:
                    txt = txt.decode("utf-8")
                self.handle_text_payload(txt)    
            
                        
    
    def update(self, args: list = [], kwargs: dict = {}) -> None:
        pass

    def render(self, args: list = [], kwargs: dict = {}):
        raise NotImplementedError

    def get_screenshots(self) -> List[str]:
        result: list[str] = []
        base_dir: str = get_screenshots_dir()
        # logger.debug(f"base_dir = {base_dir}")
        # logger.debug(f"=> = {os.listdir(base_dir)}")

        for file in os.listdir(base_dir):
            if file.startswith(self.name):
                result.append(file)
        return result

    def get_screenshot(self, name: str) -> str:
        base_dir: str = get_screenshots_dir()
        file: str = f"{base_dir}/{name}"
        return file

    def get_screenshot_blob(self, name: str) -> BufferedReader:
        base_dir: str = get_screenshots_dir()
        file: str = f"{base_dir}/{name}"
        return open(file, "rb")

    def capture_screen(self, tag=None):
        screen = pygame.display.get_surface()
        target_path: str = f"{get_capture_dir()}/{self.name}_{tag}.png"
        pygame.image.save(screen, target_path)



class MatrixBaseCmd(BaseCommand):
    def __init__(self, name: str, description: str):
        super().__init__(name, description)

        self.options: RGBMatrixOptions = getMatrixOptions()
        
        
        # force init, but do not store as member variable
        get_matrix_singleton()

        
        self.fonts: dict = {}

    def getFont(self, name: str, size:int = 30, refresh:bool = False):
        if name not in self.fonts or refresh is True:
            try:
                self.fonts[name] = ImageFont.load(get_fonts_dir(name))
            except Exception as e:
                self.fonts[name] = ImageFont.truetype(get_fonts_dir(name),size=size)
        return self.fonts[name]


class PictureScrollBaseCmd(MatrixBaseCmd):
    def __init__(self, name: str, description: str) -> None:
        super().__init__(name, description)
        self.speed_x: int = 1
        self.speed_y: int = 0
        self.scroll: bool = True
        self.refresh: bool = False
        self.image_counter: int = 0
        self.image: Image.Image | None = None
        self.double_buffer: Any = None
        self.xpos: int = 0
        self.ypos: int = 0

    def _resize_icon(
        self,
        icon: Image.Image,
        max_height: int | None = None,
        max_width: int | None = None,
    ) -> Image.Image:
        """
        Resize the icon to fit in max_height or max_width while keeping the aspect ratio
        """

        icon_width, icon_height = icon.size
        if max_height:
            icon_width = int(icon_width / (icon_height / max_height))
            icon_height: int = max_height
        elif max_width:
            icon_height = int(icon_height / (icon_width / max_width))
            icon_width: int = max_width

        # print(f"resize to {icon_width}x{icon_height}")
        icon = icon.resize((icon_width, icon_height), Image.Resampling.LANCZOS)
        return icon

    def _compute_text_position(self, text: str, font: Any, available_width: int) -> int:
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
            return int((available_width - text_width) / 2)
        return 0

    def reset_state(self) -> None:
        super().reset_state()
        self.double_buffer = get_matrix().CreateFrameCanvas()

    def update(self, args: list = [], kwargs: dict = {}) -> str:
        self.image = self.generate_image(args, kwargs)
        
        if self.scroll and self.speed_x != 0:
            self.xpos = get_total_matrix_width()
        else:
            self.xpos = 0
        self.ypos = 0
        return "update image source data"

    def generate_image(self, args: list = [], kwargs: dict = {}) -> Image.Image:
        raise NotImplementedError

    def render(self, args: list = [], kwargs: dict = {}) -> str:
        if self.scroll:
            self.xpos -= self.speed_x
            if self.image:
                if self.xpos < -self.image.size[0]:
                    self.xpos = get_total_matrix_width()

                self.ypos += self.speed_y
                if self.ypos < -self.image.size[1]:
                    self.ypos = get_matrix_height()
                elif self.ypos > self.image.size[1]:
                    self.ypos = -get_matrix_height()

        #self.double_buffer.Clear()
        if self.image:
            img_width, img_height = self.image.size
            self.double_buffer.SetImage(self.image, self.xpos, self.ypos)

        self.double_buffer = get_matrix().SwapOnVSync(self.double_buffer)

        if self.refresh:
            self.image_counter += 1
            self.image = self.generate_image(args, kwargs)
        return f"rendered {self.image_counter} images"


class TextScrollBaseCmd(PictureScrollBaseCmd):
    def __init__(self, name: str, description: str):
        super().__init__(name, description)
        self.text: str | None = None
        self.font: Any | None = None
        self.text_width:int = 0
        self.text_height: int = 0
        self.text_offset:int = 0
        self.text_speed:int = 1
        self.speed_x = 0
        self.refresh = True
        self.font_height:int=32
        self.background: Image.Image | None = None
    
    def _get_background(self) -> Image.Image:
        if self.background is None:
            width: int = get_total_matrix_width()
            height: int = get_total_matrix_height()
            self.background = Image.new("RGB", (width, height), color=(0, 0, 0))
        return self.background
    
    def get_text_color(self):
        return (255, 255, 255)
        
    
    def generate_image(self, args: List = [], kwargs: dict = {}) -> Image.Image|None:
        
        # generate background if needed
        background: Image.Image = self._get_background().copy()
        
        draw: ImageDraw.ImageDraw = ImageDraw.Draw(background)
          
        y_top = int((get_total_matrix_height() - self.text_height) / 2)
        draw.text((self.text_offset, y_top), self.get_text(), font=self.get_font(), fill=self.get_text_color())
        
        self.text_offset-=self.text_speed
        
        if self.text_offset < -self.text_width:
            self.text_offset = get_total_matrix_width()
        
        return background
    
    def get_font(self, refresh:bool=False): 
        if self.font is None or refresh:
            self.logger.info(f"Loading font {self.font_height} px")
            self.font = self.getFont("BodoniFLF-Bold.ttf", self.font_height, refresh=refresh)
        return self.font
           
    def get_text(self, args: list = [], kwargs: dict = {}) -> str:
        raise NotImplementedError
    
    
    def update_text_params(self, text:str):
        
        self.text = text
        _, _, text_width, text_height = self.get_font().getbbox(self.text)
        self.text_width = text_width
        self.text_height = text_height    
        if self.text_offset ==0:
            self.text_offset = get_total_matrix_width()
        
    
    def update(self, args: list = [], kwargs: dict = {}) -> str:
        self.update_text_params(self.get_text())        
        return super().update(args, kwargs)
