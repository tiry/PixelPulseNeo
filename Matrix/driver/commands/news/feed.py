import feedparser
from PIL import Image
from urllib.request import urlopen
from unidecode import unidecode


def get(url, max=6):
    feed = feedparser.parse(url)

    if len(feed.entries) > max:
        feed.entries = feed.entries[:max]

    for entry in feed.entries:
        entry.summary = unidecode(entry.summary)
        entry.title = unidecode(entry.title)
        # print(json.dumps(entry))
        # print("ID:", entry.id)
        # print("Entry Title:", entry.title)
        # print("Entry Link:", entry.link)
        # print("Entry Summary:", entry.summary)
        thumb = entry.get("media_thumbnail", None)
        if thumb is None and "media_content" in entry:
            thumb = entry.media_content[0]["url"]
            print(f"new thumb {thumb}")
            entry.__setitem__("media_thumbnail", [{"url": thumb}])
        # print("Thumbs: " , thumb)

        # print("Tags:", entry.get("tags", None))

    return feed


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
