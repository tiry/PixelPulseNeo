from commands.base import PictureScrollBaseCmd, get_icons_dir, get_total_matrix_width, get_total_matrix_height
import feedparser
from PIL import Image
from PIL import ImageDraw
from io import BytesIO
from urllib.request import urlopen
from unidecode import unidecode

class NewsCmd(PictureScrollBaseCmd):
    def __init__(self):
        super().__init__("news", "Displays News from RSS feeds")
        self.scroll=True
        self.refresh=False
        self.speedX=0
        self.speedY=-1


    def update(self, parameters):
        url = "https://www.france24.com/en/rss"
        feed = feedparser.parse(url)

        for entry in feed.entries:
            print("Entry Title:", entry.title)
            print("Entry Link:", entry.link)
            print("Entry Summary:", entry.summary)
            print("Thumbs: " , entry.media_thumbnail)
            print("Tags:", entry.tags)
            
            #print(entry.keys())
        #    print(feed)
        self.feed = feed
        super().update(parameters)

    def format_multilines(self, summary, font, width):

        layout = []
        current_line = []
        last_width = 0 
        for word in summary.split():
            current_line.append(word)
            _,_, text_width, text_height =  font.getbbox(unidecode(" ".join(current_line)))
            if text_width > width:
                # remove last added
                current_line.pop(-1)
                layout.append((" ".join(current_line),int( (width-last_width)/2)))
                current_line = [word]
            else: 
                last_width = text_width
        return layout
    
    def render_news_item(self, entry):

        width = get_total_matrix_width()
        height = get_total_matrix_height() 

        img = Image.new('RGB', (width, height), color=(0 ,0, 0))  
        
        font7 = self.getFont("6x12.pil")
        draw = ImageDraw.Draw(img) 

        
        img_url = entry.media_thumbnail[0]["url"]
        icon = Image.open(urlopen(img_url)).convert('RGB')

        draw.text((0  , 50), unidecode(entry.summary), font=font7)

        width, height = icon.size
        target_height = 50
        width = int(width / (height/target_height))
        icon = icon.resize((width, target_height), Image.LANCZOS)
        img.paste(icon, (0, 0))

        return img

    def generate_image(self, parameters):
        
        entries = self.feed.entries
        nb_items = len(entries)
        if nb_items > 10:
            nb_items = 10
            entries = entries[:10]

        width = get_total_matrix_width()
        height = get_total_matrix_height() * nb_items

        img = Image.new('RGB', (width, height), color=(0 ,0, 0))  
        
        idx=0
        for entry in self.feed.entries:
            img.paste(self.render_news_item(entry), (0, idx*64))
            idx+=1

        return img
    


    