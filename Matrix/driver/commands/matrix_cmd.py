from typing import Any
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from Matrix.driver.commands.base import PictureScrollBaseCmd, get_fonts_dir, trim_image


class MatrixCmd(PictureScrollBaseCmd):
    def __init__(self) -> None:
        super().__init__("matrix", "Displays Picture on Matrix")

    def generate_image(self, args: list = [], kwargs: dict = {}) -> Image.Image:
        W = 64 * 8
        H = 64
        image: Image.Image = Image.new("RGB", (W, H))
        draw: ImageDraw.ImageDraw = ImageDraw.Draw(image)

        font: Any = ImageFont.load(get_fonts_dir("9x18B.pil"))
        draw.text((10, 10), "hello this is a very long text", font=font)

        image = trim_image(image)
        draw = ImageDraw.Draw(image)

        n_steps = 15
        x_step: float = image.size[0] / n_steps
        c_step = int(255 / n_steps)
        for i in range(n_steps):
            c: tuple[int, int, int] = (
                255 - int(i * c_step),
                int(i * c_step * 2) % 255,
                i * c_step,
            )
            draw.rectangle(
                (int(i * x_step), 53, int((i + 1) * x_step), 63),
                fill=c,
                outline=(0, 0, 255),
            )

        return image
