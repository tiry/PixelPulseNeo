from Matrix.driver.commands.citibikes import api
from Matrix.driver.commands.base import PictureScrollBaseCmd, get_icons_dir, get_total_matrix_height, get_total_matrix_width
from PIL import Image
from PIL import ImageDraw

class CitibikesCmd(PictureScrollBaseCmd):
    
    def __init__(self):
        super().__init__("citibikes", "Displays information about the closest Citibike Station")
        self.scroll=False
        self.refresh=False

    def update(self, parameters):
        citibike_info=api.getStationInfo(["Columbia", "Carroll"])
        self.citibike_info=citibike_info[0]
        print(f" Citi Bike info {self.citibike_info}")        
        super().update(parameters)
    
    def generate_image(self, parameters):
        
        width = get_total_matrix_width()
        height = get_total_matrix_height()
          
        img = Image.new('RGB', (width, height), color=(0 ,0, 0))  
        draw = ImageDraw.Draw(img) 
        font = self.getFont("7x14.pil")

        icon = Image.open(get_icons_dir(f"citibike/logo_wide_small.png")).convert('RGB')
        img.paste(icon, (int((3*64-94)/2),2))

        x = 10 
        iconElec = Image.open(get_icons_dir(f"citibike/elec.png")).convert('RGB')
        iconElec = iconElec.resize((32, 32), Image.LANCZOS)
        img.paste(iconElec, (x,32))
        draw.text((x+32+2, 40), str(self.citibike_info["ebikes"]), font=font)

        x = 70   
        iconFree = Image.open(get_icons_dir(f"citibike/normal.png")).convert('RGB')
        iconFree = iconFree.resize((30, 30), Image.LANCZOS)
        img.paste(iconFree, (x,32))
        draw.text((x+32+2, 40), str(self.citibike_info["free_bikes"]), font=font)

        x = 130   
        iconFree = Image.open(get_icons_dir(f"citibike/dock.png")).convert('RGB')
        iconFree = iconFree.resize((30, 30), Image.LANCZOS)
        img.paste(iconFree, (x,32))
        draw.text((x+32+2, 40), str(self.citibike_info["empty"]), font=font)
        
        return img
   
