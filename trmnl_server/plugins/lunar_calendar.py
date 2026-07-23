import logging
import os
from datetime import date
from typing import Optional

import ephem
from PIL import Image, ImageDraw

from .base import PluginBase, PluginOutput

logger = logging.getLogger(__name__)


class LunarCalendarPlugin(PluginBase):
    """Current moon phase, calculated locally with no external API."""

    BASENAME = "lunar_calendar"
    OUTPUT_SUBDIR = "lunar_calendar"
    REGISTRY_ORDER = 55
    REFRESH_INTERVAL = 21600
    DISPLAY_NAME = "Lunar Calendar"

    PHASE_NAMES = [
        "New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
        "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent",
    ]

    async def run(self, **kwargs) -> Optional[PluginOutput]:
        target_size = kwargs.get("target_size", (800, 480))
        output_dir = kwargs.get("output_dir", "web")
        os.makedirs(output_dir, exist_ok=True)

        today = date.today()
        moon = ephem.Moon(today.strftime("%Y/%m/%d"))
        phase_pct = moon.phase
        idx = int((phase_pct / 100) * 8) % 8
        phase_name = self.PHASE_NAMES[idx]

        img = Image.new("L", target_size, color=255)
        draw = ImageDraw.Draw(img)
        name_font = self.load_font(48)
        pct_font = self.load_font(24)
        date_font = self.load_font(18)

        bbox = draw.textbbox((0, 0), phase_name, font=name_font)
        w = bbox[2] - bbox[0]
        draw.text(((target_size[0] - w) / 2, target_size[1] / 2 - 60), phase_name, fill=0, font=name_font)

        pct_text = f"{phase_pct:.0f}% illuminated"
        bbox2 = draw.textbbox((0, 0), pct_text, font=pct_font)
        w2 = bbox2[2] - bbox2[0]
        draw.text(((target_size[0] - w2) / 2, target_size[1] / 2 + 10), pct_text, fill=0, font=pct_font)

        date_text = today.strftime("%A, %B %d, %Y")
        bbox3 = draw.textbbox((0, 0), date_text, font=date_font)
        w3 = bbox3[2] - bbox3[0]
        draw.text(((target_size[0] - w3) / 2, target_size[1] / 2 + 50), date_text, fill=0, font=date_font)

        output = self.save_assets(img, output_dir, self.BASENAME)
        logger.info("Saved LunarCalendar assets to %s", output.monochrome_path)
        return output
