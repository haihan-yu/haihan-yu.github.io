#!/usr/bin/env python3
"""Render the editable SVG's rect/polygons with Pillow; no font or SVG engine needed.

Usage: python3 scripts/generate-icons.py [--preview /path/to/preview.png]
Requires Python 3.9+ and Pillow. Only the preview's labels use a system font.
"""

import argparse
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image, ImageDraw, ImageFont


SITE = Path(__file__).resolve().parents[1]
STATIC = SITE / "static"
NS = {"svg": "http://www.w3.org/2000/svg"}
SUPERSAMPLE = 8


def source():
    svg = ET.parse(STATIC / "favicon.svg").getroot()
    background = svg.find("svg:rect[@id='background']", NS)
    if background is None:
        raise ValueError("SVG must contain the background rectangle")
    viewbox = [float(n) for n in svg.attrib["viewBox"].split()]
    if viewbox[:2] != [0, 0] or viewbox[2] != viewbox[3]:
        raise ValueError("SVG must use a square viewBox starting at 0,0")
    return svg, background, viewbox[2]


def render(size, *, full_bleed=False):
    svg, background, extent = source()
    scale = size * SUPERSAMPLE / extent
    image = Image.new("RGBA", (size * SUPERSAMPLE,) * 2)
    draw = ImageDraw.Draw(image)
    bounds = (0, 0, image.width - 1, image.height - 1)
    color = background.attrib["fill"]
    if full_bleed:
        draw.rectangle(bounds, fill=color)
    else:
        draw.rounded_rectangle(bounds, radius=float(background.attrib["rx"]) * scale, fill=color)
    group_id = "monogram-small" if size <= 16 else "monogram"
    group = svg.find(f"svg:g[@id='{group_id}']", NS)
    if group is None:
        raise ValueError(f"SVG must contain {group_id}")
    for shape in group:
        if shape.tag != f"{{{NS['svg']}}}polygon":
            raise ValueError("The icon renderer supports SVG polygons only")
        values = [float(n) for n in re.split(r"[\s,]+", shape.attrib["points"].strip())]
        points = [(x * scale, y * scale) for x, y in zip(values[::2], values[1::2])]
        draw.polygon(points, fill=shape.get("fill", group.attrib["fill"]))
    image = image.resize((size, size), Image.Resampling.LANCZOS)
    return image.convert("RGB") if full_bleed else image


def version():
    match = re.search(r'^\s+icon_version:\s*"([A-Za-z0-9_-]+)"\s*$', (SITE / "config.yml").read_text(), re.M)
    if not match:
        raise ValueError("Set params.assets.icon_version in config.yml before generating icons")
    return match[1]


def font(size, bold=False):
    candidates = [
        Path("/System/Library/Fonts/Supplemental") / ("Arial Bold.ttf" if bold else "Arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu") / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default(size=size)


def preview(path):
    board = Image.new("RGB", (1152, 800), "#FAF9FC")
    draw = ImageDraw.Draw(board)
    ink, muted = "#292333", "#756D80"
    draw.text((48, 36), "ACADEMIC IDENTITY", font=font(13, True), fill=muted)
    draw.text((45, 62), "Haihan Yu", font=font(44, True), fill=ink)
    draw.text((48, 122), "Geometric HY / Purple #5E42BC", font=font(18), fill=muted)

    draw.rounded_rectangle((48, 176, 468, 696), radius=20, fill="white", outline="#E9E5EF")
    mark = render(256)
    board.paste(mark, (130, 244), mark)
    draw.text((84, 548), "The primary mark", font=font(24, True), fill=ink)
    draw.text((84, 587), "Shared weight. Open space.", font=font(18), fill=muted)
    draw.text((84, 615), "A clear signature at every size.", font=font(18), fill=muted)
    draw.text((84, 654), "SVG MASTER / NO FONT DEPENDENCY", font=font(12, True), fill=muted)

    for top, dark in [(176, False), (448, True)]:
        fill = "#25212F" if dark else "#FFFFFF"
        text = "#E9E4F3" if dark else ink
        secondary = "#B8AFC8" if dark else muted
        draw.rounded_rectangle((492, top, 1104, top + 248), radius=20, fill=fill, outline=fill if dark else "#E9E5EF")
        draw.text((520, top + 24), "ACTUAL PIXELS / " + ("DARK" if dark else "LIGHT"), font=font(13, True), fill=secondary)
        for center, size in [(550, 16), (658, 32), (782, 48)]:
            icon = render(size)
            board.paste(icon, (center - size // 2, top + 108 - size // 2), icon)
            draw.text((center, top + 145), f"{size} px", anchor="mt", font=font(14), fill=secondary)
        tab_fill = "#393342" if dark else "#F3F0F7"
        draw.rounded_rectangle((520, top + 186, 1076, top + 226), radius=9, fill=tab_fill)
        tiny = render(16)
        board.paste(tiny, (536, top + 198), tiny)
        draw.text((566, top + 197), "Haihan Yu - Research", font=font(16), fill=text)
        draw.line((1050, top + 202, 1058, top + 210), fill=secondary, width=1)
        draw.line((1058, top + 202, 1050, top + 210), fill=secondary, width=1)

    draw.text((48, 738), "SVG   /   ICO 16, 32, 48   /   PNG 16, 32   /   APPLE 180   /   ANDROID 192, 512", font=font(14), fill=muted)
    path.parent.mkdir(parents=True, exist_ok=True)
    board.save(path, optimize=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", type=Path, default=SITE.parent / "output" / "favicon-preview.png")
    args = parser.parse_args()
    icon_version = version()
    _, background, _ = source()
    purple = background.attrib["fill"]
    frames = {size: render(size) for size in (16, 32, 48)}
    for size in (16, 32):
        frames[size].save(STATIC / f"favicon-{size}x{size}.png", optimize=True)
    frames[48].save(STATIC / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)], append_images=[frames[16], frames[32]])
    render(180, full_bleed=True).save(STATIC / "apple-touch-icon.png", optimize=True)
    for size in (192, 512):
        render(size, full_bleed=True).save(STATIC / f"android-chrome-{size}x{size}.png", optimize=True)
    manifest = {
        "name": "Haihan Yu",
        "short_name": "Haihan Yu",
        "start_url": "/",
        "display": "browser",
        "background_color": "#FFFFFF",
        "theme_color": purple,
        "icons": [
            {"src": f"/android-chrome-{size}x{size}.png?v={icon_version}", "sizes": f"{size}x{size}", "type": "image/png", "purpose": "any"}
            for size in (192, 512)
        ],
    }
    (STATIC / "site.webmanifest").write_text(json.dumps(manifest, indent=2) + "\n")
    preview(args.preview)
    print(f"Generated icons from {STATIC / 'favicon.svg'}")
    print(f"Preview: {args.preview}")


if __name__ == "__main__":
    main()
