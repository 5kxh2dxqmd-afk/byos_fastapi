import logging
import os
from typing import Optional

import httpx
from PIL import Image, ImageDraw

from .base import PluginBase, PluginOutput

logger = logging.getLogger(__name__)


class TflStatusPlugin(PluginBase):
    """Show current London Underground/Overground/Elizabeth line status."""

    BASENAME = "tfl_status"
    OUTPUT_SUBDIR = "tfl_status"
    REGISTRY_ORDER = 45
    REFRESH_INTERVAL = 300
    DISPLAY_NAME = "TfL Line Status"

    API_URL = "https://api.tfl.gov.uk/Line/Mode/tube,overground,elizabeth-line/Status"

    LINE_LABELS = {
        "bakerloo": "Bakerloo",
        "central": "Central",
        "circle": "Circle",
        "district": "District",
        "hammersmith-city": "H & City",
        "jubilee": "Jubilee",
        "metropolitan": "Metropolitan",
        "northern": "Northern",
        "piccadilly": "Piccadilly",
        "victoria": "Victoria",
        "waterloo-city": "Waterloo & City",
        "elizabeth": "Elizabeth",
        "lioness": "Lioness",
        "mildmay": "Mildmay",
        "windrush": "Windrush",
        "weaver": "Weaver",
        "suffragette": "Suffragette",
        "liberty": "Liberty",
    }

    LINE_ORDER = [
        "bakerloo", "central", "circle", "district", "elizabeth",
        "hammersmith-city", "jubilee", "metropolitan", "northern",
        "piccadilly", "victoria", "waterloo-city",
        "lioness", "mildmay", "windrush", "weaver", "suffragette", "liberty",
    ]

    async def run(self, **kwargs) -> Optional[PluginOutput]:
        target_size = kwargs.get("target_size", (800, 480))
        output_dir = kwargs.get("output_dir", "web")
        os.makedirs(output_dir, exist_ok=True)

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(self.API_URL)
                response.raise_for_status()
                data = response.json()
        except Exception as exc:
            logger.error("Failed to fetch TfL status: %s", exc)
            return None

        parsed = self._parse_lines(data)
        img = self._render(parsed, target_size)
        output = self.save_assets(img, output_dir, self.BASENAME)
        logger.info("Saved TflStatus assets to %s", output.monochrome_path)
        return output

    def _parse_lines(self, data) -> dict:
        results = {}
        for line in data:
            statuses = line.get("lineStatuses", [])
            if statuses:
                worst = min(statuses, key=lambda s: s.get("statusSeverity", 10))
            else:
                worst = {"statusSeverity": 10, "statusSeverityDescription": "Good Service"}
            results[line["id"]] = {
                "is_good": worst.get("statusSeverity", 10) >= 10,
                "status": worst.get("statusSeverityDescription", "Good Service"),
            }
        return results

    def _render(self, parsed: dict, target_size) -> Image.Image:
        img = Image.new("L", target_size, color=255)
        draw = ImageDraw.Draw(img)

        title_font = self.load_font(28)
        row_font = self.load_font(16)

        draw.text((20, 15), "TfL Line Status", fill=0, font=title_font)
        draw.line([(20, 50), (target_size[0] - 20, 50)], fill=0, width=2)

        ids = [i for i in self.LINE_ORDER if i in parsed] + \
              [i for i in parsed if i not in self.LINE_ORDER]

        y = 65
        row_height = row_font.size + 14
        col_split = target_size[0] - 40
        label_width = 160

        for line_id in ids:
            label = self.LINE_LABELS.get(line_id, line_id)
            info = parsed[line_id]

            draw.rectangle(
                [(20, y), (20 + label_width, y + row_height - 4)],
                outline=0, width=1
            )
            draw.text((28, y + 4), label, fill=0, font=row_font)

            box_x0 = 20 + label_width
            box_x1 = 20 + col_split
            if info["is_good"]:
                draw.rectangle([(box_x0, y), (box_x1, y + row_height - 4)], outline=0, width=1)
                text_fill = 0
            else:
                draw.rectangle([(box_x0, y), (box_x1, y + row_height - 4)], fill=0)
                text_fill = 255
            draw.text((box_x0 + 8, y + 4), info["status"], fill=text_fill, font=row_font)

            y += row_height
            if y > target_size[1] - 20:
                break

        return img
