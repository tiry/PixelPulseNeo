import os
import time
import traceback
from datetime import datetime
from typing import List, Any
import logging
from io import BufferedReader
import threading
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


class BaseCommand:
    def __init__(self, name: str, description: str) -> None:
        self.refresh_timer: float = DEFAULT_REFRESH
        self.name: str = name
        self.description: str = description

        logger.debug(f"Load command with name {name}")

    def execute(
        self,
        stop_event: threading.Event,
        timeout: int = 10,
        args: list = [],
        kwargs: dict = {},
        render: bool = True,
    ) -> tuple | None:
        t0: float = time.time()
        try:
            logger.debug(
                f"#######################\n Execute command '{self.name}' {args} {kwargs}\n"
            )
            self.update(args, kwargs)
            if render:
                res = None
                frame_nb = 0
                while not stop_event.is_set() and not (time.time() - t0) > timeout:
                    res = self.render(args=args, kwargs=kwargs)
                    frame_nb += 1
                    time.sleep(self.refresh_timer)
                    if CAPTURE_PYGAME and frame_nb % CAPTURE_FREQ == 0:
                        self.capture_screen(tag=f"{frame_nb:05d}")
                return (res, None)
        except Exception as e:
            tb: str = traceback.format_exc()
            logger.error(f"Error BaseCommand.execute '{self.name}': {str(e)}")
            logger.error(tb)
            self.exception: Exception = e
            self.traceback: str = tb
            return (None, e)

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


# We want a sigleton matrix because we want to share the same matrix between all the commands
# Failing to do so works with the Matrix emulator but gives super bad result with the real hardware
# XXX make thread safe
matrix_singleton: RGBMatrix = RGBMatrix(options=getMatrixOptions())


class MatrixBaseCmd(BaseCommand):
    def __init__(self, name: str, description: str):
        super().__init__(name, description)

        self.options: RGBMatrixOptions = getMatrixOptions()
        self.matrix: RGBMatrix = matrix_singleton
        # self.matrix = RGBMatrix(options = self.options)
        self.fonts: dict = {}

    def getFont(self, name: str):
        if name not in self.fonts:
            self.fonts[name] = ImageFont.load(get_fonts_dir(name))
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

    def update(self, args: list = [], kwargs: dict = {}) -> str:
        self.image = self.generate_image(args, kwargs)
        self.double_buffer = self.matrix.CreateFrameCanvas()

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

        self.double_buffer.Clear()
        if self.image:
            img_width, img_height = self.image.size
            self.double_buffer.SetImage(self.image, self.xpos, self.ypos)

        self.double_buffer = self.matrix.SwapOnVSync(self.double_buffer)

        if self.refresh:
            self.image_counter += 1
            self.image = self.generate_image(args, kwargs)
        return f"rendered {self.image_counter} images"


class TextScrollBaseCmd(MatrixBaseCmd):
    def __init__(self, name: str, description: str):
        super().__init__(name, description)
        self.speed_x: int = 1
        self.speed_y: int = 0
        self.text: str | None = None
        self.double_buffer = None
        self.font: Any | None = None
        self.text_color: graphics.Color = None
        self.pos: int = 0

    def update(self, args: list = [], kwargs: dict = {}) -> str | None:
        self.text = self.get_text(args=[], kwargs={})
        self.double_buffer = self.matrix.CreateFrameCanvas()

        font = graphics.Font()
        font.LoadFont("/home/tiry/dev/rpi-rgb-led-matrix/fonts/9x18B.bdf")
        self.font = font
        self.text_color = graphics.Color(255, 255, 0)
        self.pos = self.double_buffer.width
        return None

    def get_text(self, args: list = [], kwargs: dict = {}) -> str:
        raise NotImplementedError

    def render(self, args: list = [], kwargs: dict = {}):
        double_buffer: Any = self.double_buffer
        double_buffer.Clear()
        length: int | None = graphics.DrawText(
            double_buffer, self.font, self.pos, 10, self.text_color, self.text
        )
        self.pos -= 1
        if length and self.pos + length < 0:
            self.pos = double_buffer.width
        double_buffer = self.matrix.SwapOnVSync(double_buffer)
