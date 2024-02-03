import feedparser
from PIL import Image
from PIL import ImageDraw
from urllib.request import urlopen
from unidecode import unidecode
import json


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
            



        


def get(url,max=6):
    
    feed = feedparser.parse(url)

    if len(feed.entries)>max:
        feed.entries = feed.entries[:max]

    for entry in feed.entries:
        entry.summary = unidecode(entry.summary)
        entry.title = unidecode(entry.title)
        print(json.dumps(entry))
        print("ID:", entry.id)
        print("Entry Title:", entry.title)
        print("Entry Link:", entry.link)
        print("Entry Summary:", entry.summary)
        thumb = entry.get("media_thumbnail", None)
        if thumb is None and "media_content" in entry:
            thumb = entry.media_content[0]["url"]
            print(f"new thumb {thumb}")
            entry.__setitem__("media_thumbnail", [{"url" : thumb}])
        print("Thumbs: " , thumb)

        print("Tags:", entry.get("tags", None))


    return feed

def getImage(img_url):
    return Image.open(urlopen(img_url)).convert('RGB')

def format_multilines(summary, font, width):

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

            
