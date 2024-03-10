import random
from PIL import Image
from PIL import ImageDraw
from Matrix.driver.commands.base import (
    PictureScrollBaseCmd,
    get_total_matrix_width,
    get_total_matrix_height,
    get_icons_dir,
    format_date_short,
    format_time,
)
from Matrix.driver.commands.news import feed

feeds: list[dict[str, str]] = [
    {
        "url": "https://www.france24.com/en/rss",
        "name": "france24",
        "logo": "France_24.png",
    },
    {
        "url": "https://www.lemonde.fr/international/rss_full.xml",
        "name": "lemonde",
        "logo": "lemonde.jpeg",
    },
    {
        "url": "http://rss.cnn.com/rss/cnn_topstories.rss",
        "name": "cnn top stories",
        "logo": "cnn.png",
    },
    {
        "url": "http://rss.cnn.com/rss/cnn_world.rss	",
        "name": "cnn world",
        "logo": "cnn.png",
    },
    {
        "url": "https://www.tomshardware.com/feeds/all",
        "name": "tomshardware",
        "logo": "tomshardware.png",
    },
    {
        "url": "https://www.science.org/rss/news_current.xml",
        "name": "science.org",
        "logo": "science.png",
    },
    {
        "url": "https://www.wired.com/feed/rss", 
        "name": "wired", 
        "logo": "wired.png"
    },
    {
        "url": "https://www.wired.com/feed/category/science/latest/rss",
        "name": "wired science",
        "logo": "wired.png",
    },
    {
        "url": "https://feeds.arstechnica.com/arstechnica/index",
        "name": "ars technica",
        "logo": "ars.png",
    },
    {
        "url": "https://www.anandtech.com/rss",
        "name": "anandtech",
        "logo": "anandtech.png",
    },
]


def get_feed_definition(name=None) -> dict[str, str]:
    if name:
        for item in feeds:
            if item["name"] == name:
                return item
    return feeds[random.randint(0, len(feeds) - 1)]


class NewsCmd(PictureScrollBaseCmd):
    def __init__(self) -> None:
        super().__init__("news", "Displays News from RSS feeds")
        self.scroll = False
        self.refresh = True
        self.speed_x = 0
        self.speed_y = 0
        self.feed: feed.FeedWrapper | None = None
        self.feed_definition: dict[str, str] | None = None
        self.recommended_duration = 120

    def update(self, args: list = [], kwargs: dict = {}) -> str:
        self.feed_definition = get_feed_definition()
        self.feed = feed.get(
            self.feed_definition["url"],
            get_total_matrix_width(),
            get_total_matrix_height(),
        )
        return super().update(args, kwargs)

    def render_news_item(self):
        if self.feed is None or self.feed_definition is None:
            print("No feed available, returning None")
            return None

        img: Image.Image | None = self.feed.get_rendered_img()
        font = self.getFont("6x12.pil")
        font5 = self.getFont("5x7.pil")

        if not img:
            # render image
            entry = self.feed.get_current_entry()

            if entry is None:
                print("No entry available, returning None")
                return None

            width: int = get_total_matrix_width()
            height: int = get_total_matrix_height()

            # pre-render background
            img = Image.new("RGB", (width, height), color=(0, 0, 0))

            try:
                thumb_url: str = entry.media_thumbnail[0]["url"]
                thumb: Image.Image = feed.getImage(thumb_url)
                resized_thumb = self._resize_icon(thumb, max_height=50)
                img.paste(resized_thumb, (0, 0))
            except AttributeError:
                resized_thumb: Image.Image = Image.new("RGB", (50, 50), color=(0, 0, 0))

            target_height = 30
            margin = 1
            icon: Image.Image = Image.open(
                get_icons_dir(f"news/{self.feed_definition['logo']}")
            ).convert("RGB")
            resized_icon = self._resize_icon(icon, max_height=target_height)
            img.paste(resized_icon, (192 - resized_icon.size[0] - margin, margin))

            draw: ImageDraw.ImageDraw = ImageDraw.Draw(img)

            available_text_width: int = (
                192 - resized_icon.size[0] - resized_thumb.size[0]
            )
            self.available_text_width: int = available_text_width

            self.resized_thumb_size: tuple[int, int] = resized_thumb.size
            date_text: str = format_date_short()
            xoffset: int = resized_thumb.size[0] + self._compute_text_position(
                date_text, font5, available_text_width
            )
            draw.text((xoffset, 40), date_text, font=font5)

            # compute scrolling size
            _, _, text_width, text_height = font.getbbox(entry.summary)
            self.feed.set_scrolling_boundaries(text_width)

            # cache the background image
            self.feed.set_rendered_img(img, entry.id)

        # copy the image before updating
        img = img.copy()

        # render text
        entry = self.feed.get_current_entry()
        if entry is None:
            print("No entry available, returning None")
            return None

        draw = ImageDraw.Draw(img)

        time_text: str = format_time()
        xoffset = self.resized_thumb_size[0] + self._compute_text_position(
            time_text, font, self.available_text_width
        )
        draw.text((xoffset, 15), time_text, font=font)

        dx: int | None = self.feed.get_next_scrolling_position()
        if dx is None:
            # end of scroll => go to the next news
            self.feed.next()
        else:
            draw.text((dx, 50), entry.summary, font=font)

        return img

    def generate_image(self, args=[], kwargs={}) -> Image.Image | None:
        img: Image.Image | None = self.render_news_item()
        return img

    def handle_text_payload(self, msg:str):    
        if msg.lower() == "next":
            self.update()