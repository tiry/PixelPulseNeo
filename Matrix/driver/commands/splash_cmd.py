from PIL import Image
from PIL import ImageDraw
from Matrix.driver.commands.base import (
    PictureScrollBaseCmd,
    get_total_matrix_width,
    get_total_matrix_height,
    get_icons_dir,
)
from Matrix.driver.monitor import probe

class SplashCmd(PictureScrollBaseCmd):
    def __init__(self) -> None:
        super().__init__("splash", "Simple Splash Screen")
        self.scroll = False
        self.refresh = True
        self.speed_x = 0
        self.speed_y = 0
        self.pre_rendered :Image.Image | None = None
 
    def update(self, args: list = [], kwargs: dict = {}) -> str:
 
        width: int = get_total_matrix_width()
        height: int = get_total_matrix_height()
        img:Image.Image = Image.new("RGB", (width, height), color=(0, 0, 0))

        self.add_logo(img, 3)
        self.pre_rendered = img
        return super().update(args, kwargs)

    def add_logo(self, img:Image.Image, variant:int = 0):

        images: list[str] = ["pulse.png", "square.png", "title.png", "ppn_wide.png"]
        image_name = images[variant]
        icon: Image.Image = Image.open(
            get_icons_dir(f"splash/{image_name}")
        ).convert("RGB")
        resized_icon = self._resize_icon(icon, max_height=64)
        offset = int((get_total_matrix_width() - resized_icon.size[0])/2)
        img.paste(resized_icon, (offset,0))
        
        font5 = self.getFont("5x7.pil")
        draw: ImageDraw.ImageDraw = ImageDraw.Draw(img)
        git_rev= probe.git_metrics()["git_rev"][:10]
        draw.text((5, 55), f"V:{git_rev}", font=font5)
        
    def generate_image(self, args=[], kwargs={}) -> Image.Image | None:

        if self.pre_rendered is None:
            width: int = get_total_matrix_width()
            height: int = get_total_matrix_height()
            return Image.new("RGB", (width, height), color=(0, 0, 0))
        else:
            return self.pre_rendered
        
