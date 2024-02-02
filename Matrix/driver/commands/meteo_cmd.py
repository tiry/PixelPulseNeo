from Matrix.driver.commands.base import PictureScrollBaseCmd, get_icons_dir, get_total_matrix_width, get_total_matrix_height
from Matrix.driver.commands.wttr.weather import getTodayWeather
from PIL import Image
from PIL import ImageDraw
from datetime import datetime

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

def format_time():
    return  datetime.now().strftime("%H:%M:%S")

class MeteoCmd(PictureScrollBaseCmd):
    def __init__(self):
        super().__init__("meteo", "Displays Weather forcast from wttr.in")
        self.refresh_timer = 1/60.0
        self.scroll=True
        self.refresh=True
        self.background=None

    def update(self, parameters):
        self.weather = getTodayWeather()
        #print(f"weather = {self.weather}")
        super().update(parameters)

    def getWeatherBackground(self):
        
        if not self.background:

          weatherLabel = self.weather["weatherLabel"]
          tempFull = self.weather["tempFull"]
          temp = self.weather["temp"]
          tempFeelsLike = self.weather["tempFeelsLike"]

          # get weather icon
          weatherIcon = Image.open(get_icons_dir(f"wttr_codes/128/{weatherLabel}.png")).convert('RGB')
          weatherIcon = weatherIcon.resize((48, 48), Image.LANCZOS)

          width = get_total_matrix_width()
          height = get_total_matrix_height()
          
          img = Image.new('RGB', (width, height), color=(0 ,0, 0))  

          img.paste(weatherIcon, (8,8))
          draw = ImageDraw.Draw(img) 

          font5 = self.getFont("5x7.pil") 
          font6 = self.getFont("6x12.pil")

          tempPos = (10+ weatherIcon.size[0], 20)
          draw.text(tempPos, temp, font=font6)

          date_str = format_date()
         
          draw.text((tempPos[0] + 2, tempPos[1]+ 12), tempFeelsLike, font=font5, fill = (150,150,150))
          _,_, text_width, text_height =  font6.getbbox(date_str)

          draw.text((width/2 - text_width/2, 5 ), date_str, font=font6)        

          self.tempPos = tempPos
          self.background = img
        
        return self.background.copy()


    def generate_image(self, parameters):
        
        # get background
        img = self.getWeatherBackground()

        # add time to background
        draw = ImageDraw.Draw(img)
        font = self.getFont("9x18B.pil")
        time_str = format_time()
        draw.text((self.tempPos[0]+30, 24), time_str, font=font)
          
        return img
        