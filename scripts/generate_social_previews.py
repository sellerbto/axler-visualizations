#!/usr/bin/env python3
"""Generate consistent Open Graph preview PNGs from theorem number + title.

The theorem config intentionally contains only two fields: ``number`` and
``title``. Folder paths, image names, labels, and layout are derived here.
The homepage preview is fixed site chrome and does not need a config entry.
"""

from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "social-previews.json"
OUT_DIR = ROOT / "assets" / "social"
SIZE = (1200, 630)

BG = "#fbfaf7"
PAPER = "#fffdfa"
INK = "#171717"
MUTED = "#716c64"
LINE = "#d8d2c7"
ACCENT = "#2f6feb"

ENTRY_FIELDS = {"number", "title"}
NUMBER_RE = re.compile(r"^\d+(?:\.\d+)+$")
HOME_TITLE = "Axler Visualizations"
HOME_LABEL = "AXLER COMPANION"
HOME_IMAGE = "home.png"


class HeadParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "meta":
            return
        values = {k.lower(): (v or "") for k, v in attrs}
        key = values.get("property") or values.get("name")
        content = values.get("content")
        if key and content:
            self.meta[key.lower()] = content


def page_og_image(path: Path) -> str | None:
    parser = HeadParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.meta.get("og:image")


def slug_from_number(number: str) -> str:
    return number.replace(".", "-")


def theorem_path(number: str) -> str:
    return f"{slug_from_number(number)}/index.html"


def theorem_image(number: str) -> str:
    return f"{slug_from_number(number)}.png"


def load_theorems() -> list[dict[str, str]]:
    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    entries = raw.get("theorems")
    if not isinstance(entries, list) or not entries:
        raise SystemExit("social-previews.json must contain a non-empty 'theorems' array")

    seen: set[str] = set()
    normalized: list[dict[str, str]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise SystemExit("Every theorem preview entry must be an object")
        fields = set(entry)
        if fields != ENTRY_FIELDS:
            raise SystemExit(
                "Every theorem preview entry must contain exactly 'number' and 'title'; "
                f"got {sorted(fields)}"
            )
        number = str(entry["number"]).strip()
        title = str(entry["title"]).strip()
        if not NUMBER_RE.fullmatch(number):
            raise SystemExit(f"Invalid theorem number: {number!r}")
        if not title:
            raise SystemExit(f"Theorem {number} has an empty title")
        if number in seen:
            raise SystemExit(f"Duplicate theorem number: {number}")
        seen.add(number)
        normalized.append({"number": number, "title": title})
    return normalized


def public_theorem_pages() -> set[str]:
    pages: set[str] = set()
    for page in sorted(ROOT.glob("*/index.html")):
        if page_og_image(page):
            pages.add(page.relative_to(ROOT).as_posix())
    return pages


def validate_config(entries: list[dict[str, str]]) -> None:
    home = ROOT / "index.html"
    home_og = page_og_image(home)
    if not home_og or Path(urlparse(home_og).path).name != HOME_IMAGE:
        raise SystemExit(f"index.html must expose og:image ending in {HOME_IMAGE!r}")

    expected_paths = {theorem_path(entry["number"]) for entry in entries}
    actual_paths = public_theorem_pages()
    missing = actual_paths - expected_paths
    stale = expected_paths - actual_paths
    if missing:
        raise SystemExit(f"Theorem pages missing from social-previews.json: {sorted(missing)}")
    if stale:
        raise SystemExit(f"Configured theorem pages do not exist or lack og:image: {sorted(stale)}")

    for entry in entries:
        number = entry["number"]
        path = ROOT / theorem_path(number)
        og_image = page_og_image(path)
        assert og_image is not None
        actual_name = Path(urlparse(og_image).path).name
        expected_name = theorem_image(number)
        if actual_name != expected_name:
            raise SystemExit(
                f"{path.relative_to(ROOT)}: og:image points to {actual_name!r}; "
                f"expected derived name {expected_name!r}"
            )


def find_font(serif: bool, bold: bool, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if serif:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf",
        ]
    else:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    try:
        return ImageFont.truetype("DejaVuSerif.ttf" if serif else "DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if text_width(draw, candidate, font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_title(
    draw: ImageDraw.ImageDraw,
    title: str,
    context: str,
    max_width: int = 650,
    max_lines: int = 3,
    max_height: int = 225,
) -> tuple[ImageFont.ImageFont, list[str], int]:
    """Fit the only variable text block; fail instead of producing overlap."""
    for size in range(68, 37, -2):
        font = find_font(serif=True, bold=False, size=size)
        lines = wrap_text(draw, title, font, max_width)
        line_height = size + 10
        if len(lines) <= max_lines and len(lines) * line_height <= max_height:
            return font, lines, line_height
    raise SystemExit(
        f"{context}: title does not fit the fixed preview safe area; shorten the title"
    )


def rounded(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    radius: int,
    fill: str,
    outline: str | None = None,
    width: int = 1,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def render_preview(*, label: str, title: str, watermark: str, image_name: str, context: str) -> Path:
    image = Image.new("RGB", SIZE, BG)
    draw = ImageDraw.Draw(image)

    rounded(draw, (28, 28, 1172, 602), 34, BG, LINE, 2)
    draw.text((72, 72), label, font=find_font(False, False, 20), fill=MUTED)
    draw.line((72, 101, 1128, 101), fill=LINE, width=2)

    # Fixed zones make overlap impossible by construction: variable title text
    # stays left of x=755 and above y=470; motif starts at x=805; footer is below y=540.
    rounded(draw, (72, 130, 1128, 520), 28, PAPER, LINE, 2)
    draw.text((105, 175), "Interactive visualization", font=find_font(False, False, 21), fill=ACCENT)

    title_font, title_lines, line_height = fit_title(draw, title, context)
    y = 225
    for line in title_lines:
        draw.text((105, y), line, font=title_font, fill=INK)
        y += line_height

    mark_font = find_font(True, True, 116 if len(watermark) <= 4 else 92)
    mark_box = draw.textbbox((0, 0), watermark, font=mark_font)
    mark_w = mark_box[2] - mark_box[0]
    draw.text((1080 - mark_w, 190), watermark, font=mark_font, fill="#e5e1da")

    # Generic motif shared by every preview; never theorem-specific.
    x0, y0 = 920, 390
    draw.line((805, y0, 1080, y0), fill=LINE, width=2)
    draw.line((x0, 300, x0, 485), fill=LINE, width=2)
    draw.line((x0, y0, 1042, 326), fill=ACCENT, width=5)
    draw.polygon([(1042, 326), (1022, 329), (1033, 344)], fill=ACCENT)
    draw.ellipse((x0 - 5, y0 - 5, x0 + 5, y0 + 5), fill=INK)

    draw.text((72, 558), "Linear Algebra Done Right", font=find_font(True, False, 18), fill=INK)
    footer = "sellerbto.github.io/axler-visualizations"
    footer_font = find_font(False, False, 14)
    footer_box = draw.textbbox((0, 0), footer, font=footer_font)
    footer_w = footer_box[2] - footer_box[0]
    draw.text((1128 - footer_w, 562), footer, font=footer_font, fill=MUTED)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUT_DIR / image_name
    image.save(output, format="PNG", optimize=True)
    return output


def main() -> None:
    entries = load_theorems()
    validate_config(entries)

    outputs = [
        render_preview(
            label=HOME_LABEL,
            title=HOME_TITLE,
            watermark="A",
            image_name=HOME_IMAGE,
            context="index.html",
        )
    ]

    for entry in entries:
        number = entry["number"]
        outputs.append(
            render_preview(
                label=f"AXLER {number}",
                title=entry["title"],
                watermark=number,
                image_name=theorem_image(number),
                context=theorem_path(number),
            )
        )

    for output in outputs:
        print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()
