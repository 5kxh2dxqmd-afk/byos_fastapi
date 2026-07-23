import logging
import os
from datetime import date
from typing import Optional

from PIL import Image, ImageDraw

from .base import PluginBase, PluginOutput

logger = logging.getLogger(__name__)


class DaysLeftUntilPlugin(PluginBase):
    """Countdown to a configurable target date."""

    BASENAME = "days_left_until"
    OUTPUT_SUBDIR = "days_left_until"
    REGISTRY_ORDER = 60
    REFRESH_INTERVAL = 3600
    DISPLAY_NAME = "Days Left Until"

    TARGET_DATE = date(2026, 12, 25)
    TARGET_LABEL = "Christmas"

    async def run(self, **kwargs) -> Optional[PluginOutput]:
        target_size = kwargs.get("target_size", (800, 480))
        output_dir = kwargs.get("output_dir", "web")
        os.makedirs(output_dir, exist_ok=True)

        days = (self.TARGET_DATE - date.today()).days

        img = Image.new("L", target_size, color=255)
        draw = ImageDraw.Draw(img)
        big_font = self.load_font(96)
        label_font = self.load_font(28)

        big_text = str(days)
        bbox = draw.textbbox((0, 0), big_text, font=big_font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(
            ((target_size[0] - w) / 2, (target_size[1] - h) / 2 - 30),
            big_text, fill=0, font=big_font
        )

        label_text = f"days until {self.TARGET_LABEL}"
        bbox2 = draw.textbbox((0, 0), label_text, font=label_font)
        w2 = bbox2[2] - bbox2[0]
        draw.text(
            ((target_size[0] - w2) / 2, (target_size[1] / 2) + 60),
            label_text, fill=0, font=label_font
        )

        output = self.save_assets(img, output_dir, self.BASENAME)
        logger.info("Saved DaysLeftUntil assets to %s", output.monochrome_path)
        return output
