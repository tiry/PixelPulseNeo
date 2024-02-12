from Matrix.driver.commands.base import (
    PictureScrollBaseCmd,
    get_total_matrix_width,
    get_total_matrix_height,
)
from PIL import Image
from Matrix.driver.commands.simu.conway import runStep, randomGrid, ON
import random

palettes = [
    # fire
    [
        "03071e",
        "370617",
        "6a040f",
        "9d0208",
        "d00000",
        "dc2f02",
        "e85d04",
        "f48c06",
        "faa307",
        "ffba08",
    ],
    # blue
    [
        "d9ed92",
        "b5e48c",
        "99d98c",
        "76c893",
        "52b69a",
        "34a0a4",
        "168aad",
        "1a759f",
        "1e6091",
        "184e77",
    ],
    #
    ["355070", "6d597a", "b56576", "e56b6f", "eaac8b"],
    #
    [
        "582f0e",
        "7f4f24",
        "936639",
        "a68a64",
        "b6ad90",
        "c2c5aa",
        "a4ac86",
        "656d4a",
        "414833",
        "333d29",
    ],
    #
    [
        "54478c",
        "2c699a",
        "048ba8",
        "0db39e",
        "16db93",
        "83e377",
        "b9e769",
        "efea5a",
        "f1c453",
        "f29e4c",
    ],
    #
    ["ccdbdc", "9ad1d4", "80ced7", "007ea7", "003249"],
]


def hex_to_rgb(hex_color):
    # Check if the input is valid
    if len(hex_color) != 6:
        raise ValueError("Invalid hex color format. Please use the format RRGGBB.")

    # Extract the red, green, and blue components and convert them to integers
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return (r, g, b)


_palette = None


def getPalette():
    global _palette
    if not _palette:
        _palette = palettes[random.randint(0, len(palettes) - 1)]
    return _palette


def getColor(idx):
    return hex_to_rgb(getPalette()[idx])


class ConwayCmd(PictureScrollBaseCmd):
    def __init__(self):
        super().__init__("conway", "Render Conway's game of life")
        self.refresh_timer = 1 / 60.0
        self.scroll = False
        self.refresh = True
        self.background = None
        self.tailLength = len(getPalette())

    def update(self, args=[], kwargs={}):
        model = randomGrid(get_total_matrix_width(), get_total_matrix_height())
        # print(model)
        self.models = [model]
        super().update(args, kwargs)

    def renderArray(self, model, img, color=(255, 255, 255)):
        width, height = model.shape
        for x in range(width):
            for y in range(height):
                if model[x][y] == ON:
                    img.putpixel((x, y), color)

    def updateModel(self):
        last_model = self.models[-1]
        self.models.append(runStep(last_model))
        if len(self.models) > self.tailLength:
            self.models.pop(0)

    def generate_image(self, args=[], kwargs={}):
        width, height = self.models[-1].shape
        img = Image.new("RGB", (width, height), color=(0, 0, 0))

        for idx, model in enumerate(self.models):
            c = getColor(idx)
            self.renderArray(model, img, c)

        self.updateModel()
        return img
