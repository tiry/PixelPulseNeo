from Matrix.driver.commands.base import PictureScrollBaseCmd, get_fonts_dir, trimImage
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

class MatrixCmd(PictureScrollBaseCmd):

    def __init__(self):
        super().__init__("matrix", "Displays Picture on Matrix")
    
    def generate_image(self, parameters):
        W=64*8
        H=64
        image = Image.new("RGB", (W, H)) 
        draw = ImageDraw.Draw(image) 
        
        font = ImageFont.load(get_fonts_dir("9x18B.pil"))
        draw.text((10, 10), "hello this is a very long text", font=font)

        image = trimImage(image)
        draw = ImageDraw.Draw(image) 

        n_steps=15
        x_step = image.size[0]/n_steps
        c_step = int(255/n_steps)
        for i in range(n_steps):
            c = (255-int(i*c_step),  int(i*c_step*2)%255, i*c_step)
            draw.rectangle((int(i*x_step), 53, int((i+1)*x_step), 63), fill=c, outline=(0, 0, 255))
        
        return image