import logging
import os
from typing import Optional

import feedparser
from PIL import Image, ImageDraw

from .base import PluginBase, PluginOutput

logger = logging.getLogger(__name__)


class RSSFeedPlugin(PluginBase):
    """Show latest headlines from a configured RSS feed."""

    BASENAME = "rss_feed"
    OUTPUT_SUBDIR = "rss_feed"
    REGISTRY_ORDER = 40
    REFRESH_INTERVAL = 1800
    DISPLAY_NAME = "RSS Feed"

    FEED_URL = "https://news.ycombinator.com/rss"
    MAX_ITEMS = 10

    async def run(self, **kwargs) -> Optional[PluginOutput]:
        target_size = kwargs.get("target_size", (800, 480))
        output_dir = kwargs.get("output_dir", "web")
        os.makedirs(output_dir, exist_ok=True)

        feed = feedparser.parse(self.FEED_URL)
        if not feed.entries:
            logger.warning("RSSFeedPlugin: no entries returned for %s", self.FEED_URL)
            return None

        img = Image.new("L", target_size, color=255)
        draw = ImageDraw.Draw(img)
        title_font = self.load_font(30)
        item_font = self.load_font(18)

        feed_title = feed.feed.get("title", "RSS Feed")
        draw.text((30, 20), feed_title, fill=0, font=title_font)
        draw.line([(30, 60), (target_size[0] - 30, 60)], fill=0, width=2)

        y = 80
        line_height = item_font.size + 12
        for entry in feed.entries[: self.MAX_ITEMS]:
            title = entry.get("title", "")
            if len(title) > 90:
                title = title[:87] + "..."
            draw.text((30, y), f"\u2022 {title}", fill=0, font=item_font)
            y += line_height
            if y > target_size[1] - 30:
                break

        output = self.save_assets(img, output_dir, self.BASENAME)
        logger.info("Saved RSSFeed assets to %s", output.monochrome_path)
        return output
