import feedparser
from PIL import Image
from urllib.request import urlopen
from unidecode import unidecode
import hashlib
from bs4 import BeautifulSoup


class FeedWrapper:
    def __init__(self, feed, max_width, max_height):
        self.feed = feed
        self.ids = [entry.id for entry in feed.entries]
        self.current_id = self.ids[0]
        self.rendered_item_img = None
        self.rendered_item_id = None
        self.max_width = max_width
        self.max_height = max_height

    def __getitem__(self, key):
        if key == "entries":
            return self.feed

    def get_current_id(self):
        return self.current_id

    def get_current_entry(self):
        for entry in self.feed.entries:
            if entry.id == self.current_id:
                return entry

    def next(self):
        # print("Next")
        next_idx = self.ids.index(self.current_id) + 1

        if next_idx >= len(self.ids):
            self.current_id = self.ids[0]
        else:
            self.current_id = self.ids[next_idx]

        return self.current_id

    def set_rendered_img(self, img, id):
        self.rendered_item_img = img
        self.rendered_item_id = id
        assert id == self.current_id

    def set_scrolling_boundaries(self, text_width):
        # print(f"set boundary to {text_width}")

        self.scrolling_position = self.max_height
        self.max_scrolling_position = -text_width

    def get_next_scrolling_position(self):
        if self.scrolling_position is None:
            return None

        self.scrolling_position -= 1.5
        if self.scrolling_position < self.max_scrolling_position:
            # print("Reset position")
            self.scrolling_position = self.max_width
            return None

        return int(self.scrolling_position)

    def get_rendered_img(self):
        if self.rendered_item_id == self.current_id:
            if self.rendered_item_img:
                return self.rendered_item_img
        return None


def get(url, max_width, max_height, max_items=6) -> FeedWrapper:
    feed = feedparser.parse(url)

    if len(feed.entries) > max_items:
        feed.entries = feed.entries[:max_items]

    for entry in feed.entries:
        entry.summary = unidecode(entry.get("summary", ""))
        entry.title = unidecode(entry.title)
        if entry.summary == "":
            entry.summary = entry.title

        id_str = entry.get("id", None)
        if id_str is None:
            id_str = hashlib.md5(entry.summary.encode())
            entry.id = id_str

        # print(entry.keys())
        # print(entry.summary)
        # print(entry.summary_detail)

        # print(json.dumps(entry))
        # print("ID:", entry.id)
        # print("Entry conetnt:", entry.content)
        # print("Entry Link:", entry.link)
        # print("Entry Summary:", entry.summary)
        thumb = entry.get("media_thumbnail", None)
        if thumb is None and "media_content" in entry:
            thumb = entry.media_content[0]["url"]
            entry.__setitem__("media_thumbnail", [{"url": thumb}])
        if thumb is None:
            if "enc_enclosure" in entry.keys():
                thumb = entry.enc_enclosure["rdf:resource"]
                # print(f"new thumb {thumb}")
                entry.__setitem__("media_thumbnail", [{"url": thumb}])
            elif "content" in entry.keys():
                xml = entry.content[0].value
                soup = BeautifulSoup(xml, "html.parser")
                imgs = soup.select("img")
                if len(imgs) > 0:
                    thumb = imgs[0].get("src")
                    entry.__setitem__("media_thumbnail", [{"url": thumb}])
            elif "summary" in entry.keys():
                # print("use summary")
                xml = entry.summary
                soup = BeautifulSoup(xml, "html.parser")
                imgs = soup.select("img")
                if len(imgs) > 0:
                    thumb = imgs[0].get("src")
                    entry.__setitem__("media_thumbnail", [{"url": thumb}])
                    entry.summary = entry.title

        # print("Tags:", entry.get("tags", None))

    return FeedWrapper(feed, max_width, max_height)


def getImage(img_url):
    return Image.open(urlopen(img_url)).convert("RGB")


def format_multilines(summary, font, width):
    layout = []
    current_line = []
    last_width = 0
    for word in summary.split():
        current_line.append(word)
        _, _, text_width, text_height = font.getbbox(unidecode(" ".join(current_line)))
        if text_width > width:
            # remove last added
            current_line.pop(-1)
            layout.append((" ".join(current_line), int((width - last_width) / 2)))
            current_line = [word]
        else:
            last_width = text_width
    return layout
