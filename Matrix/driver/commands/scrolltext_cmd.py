from Matrix.driver.commands.base import TextScrollBaseCmd
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

class ScrolltextCmd(TextScrollBaseCmd):

    def __init__(self):
        super().__init__("scrolltext", "Displays Text on Matrix")
    
    def get_text(self, args=[], kwargs={}):
        return "Hello World"