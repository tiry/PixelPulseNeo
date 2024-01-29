from commands.base import PictureScrollBaseCmd, get_icons_dir, get_total_matrix_width, get_total_matrix_height
from commands.news import feed
from PIL import Image
from PIL import ImageDraw

class FeedWrapper():

    def __init__(self, feed):
        self.feed = feed
        self.ids = [ entry.id for entry in feed.entries]
        self.current_id=self.ids[0]
        self.rendered_item_img = None
        self.rendered_item_id = None
    
    def __getitem__(self, key):
        if key=="entries":
            return self.feed
        return super().__getitem__(key)
    
    def get_current_id(self):
        return self.current_id
    
    def get_current_entry(self):
        for entry in self.feed.entries:
            if entry.id == self.current_id:
                return entry 

    def next(self):

        print("Next")
        next_idx = self.ids.index(self.current_id)+1

        if (next_idx>=len(self.ids)):
            self.current_id = self.ids[0]
        else:
            self.current_id = self.ids[next_idx]

        return self.current_id
    
    def set_rendered_img(self, img, id):
        self.rendered_item_img = img
        self.rendered_item_id = id
        assert id == self.current_id

    def set_scrolling_boundaries(self, text_width):

        print(f"set boundary to {text_width}")

        self.scrolling_position=get_total_matrix_width()
        self.max_scrolling_position = - text_width

    def get_next_scrolling_position(self):

        if self.scrolling_position is None:
            return None

        self.scrolling_position -=1.5
        if self.scrolling_position < self.max_scrolling_position:
            print("Reset position")
            self.scrolling_position=get_total_matrix_width()
            return None

        return int(self.scrolling_position)    


    def get_rendered_img(self):
        if self.rendered_item_id == self.current_id:
            if self.rendered_item_img:
                return self.rendered_item_img
        return None
            



        

class NewsCmd(PictureScrollBaseCmd):

    def __init__(self):
        super().__init__("news", "Displays News from RSS feeds")
        self.scroll=False
        self.refresh=True
        self.speedX=0
        self.speedY=0
        #self.src_url = "https://www.france24.com/en/rss"
        self.src_url = "https://www.lemonde.fr/international/rss_full.xml"


    def update(self, parameters):
        self.feed = FeedWrapper(feed.get(self.src_url))
        super().update(parameters)

    def render_news_item(self):

        img = self.feed.get_rendered_img()
        font = self.getFont("6x12.pil")
        if not img:
            entry = self.feed.get_current_entry()
            width = get_total_matrix_width()
            height = get_total_matrix_height() 
            
            # pre-render background

            img = Image.new('RGB', (width, height), color=(0 ,0, 0))  
            img_url = entry.media_thumbnail[0]["url"]
            icon = feed.getImage(img_url)
            
            icon_width, icon_height = icon.size
            target_icon_height = 50
            icon_width = int(icon_width / (icon_height/target_icon_height))
            icon = icon.resize((icon_width, target_icon_height), Image.LANCZOS)
            img.paste(icon, (0, 0))
            
            # XXX render tags + time

            # compute scrolling size 
            _,_, text_width, text_height =  font.getbbox(entry.summary)
            self.feed.set_scrolling_boundaries(text_width)

            # cache the background image 
            self.feed.set_rendered_img(img, entry.id)

        # copy the image before updating
        img = img.copy()

        # render text
        entry = self.feed.get_current_entry()
        draw = ImageDraw.Draw(img)         
        dx = self.feed.get_next_scrolling_position()
        if dx is None:
            # end of scroll => go to the next news
            self.feed.next()
        else:    
            draw.text((dx  , 50), entry.summary, font=font)

        return img

    
    def generate_image(self, parameters):
        img = self.render_news_item()
        return img
    



    