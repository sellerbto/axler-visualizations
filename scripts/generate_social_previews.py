#!/usr/bin/env python3
"""Generate consistent Open Graph preview PNGs from one strict JSON config.

Every public page with an ``og:image`` entry must be represented in
``social-previews.json``. The renderer is deliberately generic: page-specific
copy is data, while layout and styling live only in this script.
"""

from __future__ import annotations

import json
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

REQUIRED_FIELDS = {"path", "image", "label", "title", "subtitle"}


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


def public_pages() -> list[Path]:
    pages = [ROOT / "index.html"]
    pages.extend(sorted(ROOT.glob("*/index.html")))
    return [page for page in pages if page.exists() and page_og_image(page)]


def load_config() -> list[dict[str, str]]:
    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    entries = raw.get("pages")
    if not isinstance(entries, list) or not entries:
        raise SystemExit("social-previews.json must contain a non-empty 'pages' array")

    seen_paths: set[str] = set()
    seen_images: set[str] = set()
    normalized: list[dict[str, str]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise SystemExit("Every social preview config entry must be an object")
        missing = REQUIRED_FIELDS - set(entry)
        if missing:
            raise SystemExit(f"Preview config entry is missing fields: {sorted(missing)}")
        values = {key: str(entry[key]).strip() for key in REQUIRED_FIELDS}
        if any(not value for value in values.values()):
            raise SystemExit(f"Preview config values must be non-empty: {entry}")
        if values["path"] in seen_paths:
            raise SystemExit(f"Duplicate preview path: {values['path']}")
        if values["image"] in seen_images:
            raise SystemExit(f"Duplicate preview image: {values['image']}")
        seen_paths.add(values["path"])
        seen_images.add(values["image"])
        normalized.append(values)
    return normalized


def validate_config(entries: list[dict[str, str]]) -> None:
    by_path = {entry["path"]: entry for entry in entries}
    page_paths = {page.relative_to(ROOT).as_posix() for page in public_pages()}
    config_paths = set(by_path)

    missing = page_paths - config_paths
    stale = config_paths - page_paths
    if missing:
        raise SystemExit(f"Pages with og:image missing from social-previews.json: {sorted(missing)}")
    if stale:
        raise SystemExit(f"Stale social preview config entries: {sorted(stale)}")

    for rel_path, entry in by_path.items():
        page = ROOT / rel_path
        og_image = page_og_image(page)
        assert og_image is not None
        actual_name = Path(urlparse(og_image).path).name
        if actual_name != entry["image"]:
            raise SystemExit(
                f"{rel_path}: og:image points to {actual_name!r}, "
                f"but social-previews.json declares {entry['image']!r}"
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


def fit_title(draw: ImageDraw.ImageDraw, title: str, max_width: int, max_lines: int = 3) -> tuple[ImageFont.ImageFont, list[str]]:
    for size in range(64, 35, -2):
        font = find_font(serif=True, bold=False, size=size)
        lines = wrap_text(draw, title, font, max_width)
        if len(lines) <= max_lines:
            return font, lines
    font = find_font(serif=True, bold=False, size=36)
    return font, wrap_text(draw, title, font, max_width)[:max_lines]


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int, fill: str, outline: str | None = None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def watermark_from_label(label: str) -> str:
    parts = label.strip().split()
    if parts and any(char.isdigit() for char in parts[-1]):
        return parts[-1]
    return "A"


def render_preview(entry: dict[str, str]) -> Path:
    image = Image.new("RGB", SIZE, BG)
    draw = ImageDraw.Draw(image)

    rounded(draw, (28, 28, 1172, 602), 34, BG, LINE, 2)
    draw.text((72, 72), entry["label"], font=find_font(False, False, 20), fill=MUTED)
    draw.line((72, 101, 1128, 101), fill=LINE, width=2)

    rounded(draw, (72, 130, 1128, 542), 28, PAPER, LINE, 2)

    # One generic renderer for every page. Only config data changes.
    draw.text((105, 175), "Interactive visualization", font=find_font(False, False, 21), fill=ACCENT)
    title_font, title_lines = fit_title(draw, entry["title"], 700)
    y = 225
    line_height = title_font.size + 10 if hasattr(title_font, "size") else 52
    for line in title_lines:
        draw.text((105, y), line, font=title_font, fill=INK)
        y += line_height

    subtitle_font = find_font(False, False, 24)
    subtitle_lines = wrap_text(draw, entry["subtitle"], subtitle_font, 690)[:3]
    y += 10
    for line in subtitle_lines:
        draw.text((105, y), line, font=subtitle_font, fill=MUTED)
        y += 34

    mark = watermark_from_label(entry["label"])
    mark_font = find_font(True, True, 116 if len(mark) <= 4 else 92)
    mark_box = draw.textbbox((0, 0), mark, font=mark_font)
    mark_w = mark_box[2] - mark_box[0]
    draw.text((1080 - mark_w, 190), mark, font=mark_font, fill="#e5e1da")

    # Quiet generic mathematical motif; never theorem-specific.
    x0, y0 = 920, 390
    draw.line((805, y0, 1080, y0), fill=LINE, width=2)
    draw.line((x0, 300, x0, 485), fill=LINE, width=2)
    draw.line((x0, y0, 1042, 326), fill=ACCENT, width=5)
    draw.polygon([(1042, 326), (1022, 329), (1033, 344)], fill=ACCENT)
    draw.ellipse((x0 - 5, y0 - 5, x0 + 5, y0 + 5), fill=INK)

    draw.text((105, 505), "Linear Algebra Done Right", font=find_font(True, False, 22), fill=INK)
    footer = "sellerbto.github.io/axler-visualizations"
    footer_font = find_font(False, False, 16)
    footer_box = draw.textbbox((0, 0), footer, font=footer_font)
    footer_w = footer_box[2] - footer_box[0]
    draw.text((1128 - footer_w, 568), footer, font=footer_font, fill=MUTED)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUT_DIR / entry["image"]
    image.save(output, format="PNG", optimize=True)
    return output


def main() -> None:
    entries = load_config()
    validate_config(entries)
    for entry in entries:
        output = render_preview(entry)
        print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()
