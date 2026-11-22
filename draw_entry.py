#!/usr/bin/env python3
"""Draw the Daily Picture front page for Saturday 21 November 2026.

The page is a 1024x1024 broadsheet-style summary of the day's world news,
rendered entirely with Pillow primitives: a masthead, a small night-scene
illustration, the lead headline, a short standfirst, and seven story cards.
Running the script writes entry.png next to itself.
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Page geometry and palette
# ---------------------------------------------------------------------------

PAGE = 1024
EDGE = 46                      # side margin of the text block
COL_W = PAGE - 2 * EDGE        # usable width for everything

INK = (13, 21, 38)             # page background, deep ink navy
CARD = (22, 34, 58)            # story card background
CARD_LINE = (58, 84, 122)      # hairline borders
PAPER = (233, 228, 214)        # warm off-white for print text
FADED = (158, 174, 199)        # secondary text
GOLD = (216, 164, 65)          # accent colour

FONT_DIR = Path("/usr/share/fonts/truetype/liberation")
SERIF_BOLD = FONT_DIR / "LiberationSerif-Bold.ttf"
SERIF_ITALIC = FONT_DIR / "LiberationSerif-Italic.ttf"
SANS = FONT_DIR / "LiberationSans-Regular.ttf"
SANS_BOLD = FONT_DIR / "LiberationSans-Bold.ttf"

_font_cache = {}


def font(path, size):
    """Load (and memoise) a TrueType font at a given size."""
    key = (str(path), size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(str(path), size)
    return _font_cache[key]


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def wrap_to_width(draw, text, fnt, limit):
    """Greedy word wrap: split text into lines no wider than limit pixels."""
    lines, current = [], ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=fnt) <= limit:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def centred(draw, y, text, fnt, fill):
    draw.text((PAGE / 2, y), text, font=fnt, fill=fill, anchor="ma")


def block(draw, x, y, text, fnt, limit, leading, fill):
    """Draw a left-aligned wrapped paragraph; return the y below it."""
    for line in wrap_to_width(draw, text, fnt, limit):
        draw.text((x, y), line, font=fnt, fill=fill, anchor="la")
        y += leading
    return y


# ---------------------------------------------------------------------------
# Night scene: village under a missile streak
# ---------------------------------------------------------------------------

def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_night_scene(draw, box):
    x0, y0, x1, y1 = box
    rng = random.Random(20261121)

    # Sky: one horizontal strip per row, easing from near-black to steel blue.
    top, bottom = (8, 15, 40), (38, 58, 96)
    for row in range(y1 - y0):
        draw.line([(x0, y0 + row), (x1, y0 + row)],
                  fill=lerp(top, bottom, row / max(1, y1 - y0)))

    # Stars scattered over the upper two thirds.
    for _ in range(110):
        sx = rng.randint(x0 + 6, x1 - 6)
        sy = rng.randint(y0 + 6, y0 + (y1 - y0) * 2 // 3)
        r = rng.choice([1, 1, 1, 2])
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(198, 210, 240))

    # Crescent moon, top left.
    mx, my, mr = x0 + 108, y0 + 40, 15
    draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(232, 230, 205))
    draw.ellipse([mx - mr + 9, my - mr - 3, mx + mr + 9, my + mr - 3],
                 fill=lerp(top, bottom, 0.18))

    # Missile streaking down from the top right, drawn as layered strokes.
    head = (x1 - 348, y0 + 92)
    tail = (x1 - 128, y0 + 16)
    for width, colour in ((9, (110, 82, 40)), (5, GOLD), (2, (255, 238, 190))):
        draw.line([tail, head], fill=colour, width=width)
    draw.ellipse([head[0] - 6, head[1] - 6, head[0] + 6, head[1] + 6],
                 fill=(255, 246, 214))

    # NATO roundel: ring with a four-point compass star, high in the sky
    # so the rooftops drawn later do not swallow it.
    cx, cy, cr = x0 + 200, y0 + 48, 27
    draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr],
                 fill=(24, 48, 94), outline=(150, 178, 216), width=2)
    star = []
    for k in range(8):
        rad = cr - 7 if k % 2 == 0 else 9
        ang = -math.pi / 2 + k * math.pi / 4
        star.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(star, fill=(226, 234, 246))

    # Village rooftops: a row of silhouetted houses along the baseline.
    ground = y1 - 18
    houses = [(0, 64, 46), (58, 84, 58), (136, 58, 40), (188, 96, 52),
              (278, 66, 44), (338, 88, 60), (420, 60, 42), (474, 92, 54),
              (560, 70, 46), (624, 98, 58), (716, 64, 44), (774, 86, 52),
              (854, 78, 48)]
    for off, w, h in houses:
        hx = x0 + off
        draw.rectangle([hx, ground - h, hx + w, ground], fill=(5, 8, 15))
        draw.polygon([(hx - 4, ground - h), (hx + w + 4, ground - h),
                      (hx + w / 2, ground - h - 20)], fill=(5, 8, 15))
        # A few lamplit windows per house.
        for _ in range(rng.randint(1, 3)):
            wx = rng.randint(hx + 6, hx + w - 9)
            wy = rng.randint(ground - h + 8, ground - 10)
            draw.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 184, 77))

    # Field strip in front of the houses.
    draw.rectangle([x0, ground, x1, y1], fill=(9, 22, 16))

    # Polish flag on a pole at the right edge of the village.
    px = x1 - 96
    draw.line([(px, ground), (px, ground - 104)], fill=(190, 196, 208), width=3)
    draw.rectangle([px, ground - 104, px + 46, ground - 91], fill=(245, 245, 245))
    draw.rectangle([px, ground - 91, px + 46, ground - 78], fill=(210, 38, 48))

    # Crater flash bursting out of the field, right of centre.
    fx, fy = x0 + 628, y1 - 12
    for dx, dy, colour in ((30, 9, (214, 138, 44)), (19, 6, (255, 202, 85)),
                           (10, 4, (255, 243, 196))):
        draw.ellipse([fx - dx, fy - dy, fx + dx, fy + dy], fill=colour)
    for ang_deg, length in ((90, 34), (60, 26), (120, 26), (35, 19), (145, 19)):
        ang = math.radians(ang_deg)
        draw.line([(fx, fy - 2),
                   (fx - length * math.cos(ang), fy - 2 - length * math.sin(ang))],
                  fill=(255, 220, 140), width=2)

    draw.rectangle(box, outline=CARD_LINE, width=2)


# ---------------------------------------------------------------------------
# Story cards
# ---------------------------------------------------------------------------

STORIES = [
    ("IRAN HITS US BASES IN BAHRAIN",
     "Tehran strikes American facilities; a civilian plant burns as the "
     "Gulf crisis widens."),
    ("TANKERS HIT IN HORMUZ",
     "Two tankers struck and a third hits a naval mine blamed on Iran; "
     "oil routes on edge."),
    ("HOUTHI MISSILES DOWNED OVER RIYADH",
     "Saudi air defences intercept three ballistic missiles aimed at "
     "the capital."),
    ("PALISADES ARSONIST CONVICTED",
     "The man who set the fire that killed 12 and razed some 6,800 "
     "buildings is found guilty."),
    ("RUSSIA POUNDS UKRAINE'S GRID",
     "Europe's largest substation hit; Kryvyi Rih double-tap leaves "
     "2 dead and 60 hurt."),
    ("COP31 DEADLOCKED",
     "Talks stall over fossil-fuel language as negotiators fail to "
     "bridge the divide."),
    ('"EL CHAPO ISIDRO" CAPTURED',
     "Mexico seizes the FBI most-wanted cartel figure in a major "
     "operation."),
]

LEAD = (
    "Rutte flies to Warsaw as Poland invokes Article 4 after Russian "
    "missiles and a drone fell on Polish soil in Friday's mass strike. "
    "Warsaw formally asks NATO for F-35 jets and AWACS cover; Tusk calls "
    "the strike an intentional provocation. Trump calls it a mistake; "
    "Zelensky brands Putin a 'killer' as the alliance weighs its response."
)


def story_card(draw, box, headline, blurb):
    """One story panel; fonts step down until the text fits the box."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=CARD, outline=CARD_LINE, width=1)
    draw.rectangle([x0, y0, x0 + 5, y1], fill=GOLD)
    inner_x, inner_w = x0 + 18, (x1 - x0) - 32
    size = 20
    head_lines = body_lines = []
    head_f = body_f = None
    while size > 12:
        head_f = font(SANS_BOLD, size)
        body_f = font(SANS, size - 3)
        head_lines = wrap_to_width(draw, headline, head_f, inner_w)
        body_lines = wrap_to_width(draw, blurb, body_f, inner_w)
        needed = len(head_lines) * (size + 4) + 5 + len(body_lines) * (size + 1)
        if needed <= (y1 - y0) - 16:
            break
        size -= 1
    y = y0 + 9
    for line in head_lines:
        draw.text((inner_x, y), line, font=head_f, fill=PAPER, anchor="la")
        y += size + 4
    y += 5
    for line in body_lines:
        draw.text((inner_x, y), line, font=body_f, fill=FADED, anchor="la")
        y += size + 1


# ---------------------------------------------------------------------------
# Compose the page
# ---------------------------------------------------------------------------

def build_page():
    page = Image.new("RGB", (PAGE, PAGE), INK)
    draw = ImageDraw.Draw(page)

    # Masthead.
    draw.line([(EDGE, 30), (PAGE - EDGE, 30)], fill=GOLD, width=3)
    draw.line([(EDGE, 37), (PAGE - EDGE, 37)], fill=GOLD, width=1)
    centred(draw, 48, "THE DAILY PICTURE", font(SERIF_BOLD, 60), PAPER)
    centred(draw, 118, "SATURDAY 21 NOVEMBER 2026", font(SANS_BOLD, 21), GOLD)
    draw.line([(EDGE, 148), (PAGE - EDGE, 148)], fill=CARD_LINE, width=1)

    # Illustrated scene.
    draw_night_scene(draw, (EDGE, 160, PAGE - EDGE, 336))

    # Headline, two centred lines.
    head_f = font(SERIF_BOLD, 53)
    centred(draw, 352, "NATO VOWS TO DEFEND", head_f, PAPER)
    centred(draw, 410, '"EVERY INCH" OF POLAND', head_f, PAPER)
    draw.line([(EDGE, 474), (PAGE - EDGE, 474)], fill=CARD_LINE, width=1)

    # Standfirst paragraph.
    y = block(draw, EDGE, 488, LEAD, font(SERIF_ITALIC, 22), COL_W, 29, PAPER)
    draw.line([(EDGE, y + 8), (PAGE - EDGE, y + 8)], fill=CARD_LINE, width=1)

    # Story cards: rows of two, two, then three.
    grid_top = y + 22
    rows = [STORIES[0:2], STORIES[2:4], STORIES[4:7]]
    row_h = (PAGE - EDGE - grid_top) / len(rows)
    for r, row in enumerate(rows):
        ry = grid_top + r * row_h
        cell = COL_W / len(row)
        for c, (headline, blurb) in enumerate(row):
            bx0 = EDGE + c * cell + (0 if c == 0 else 5)
            bx1 = EDGE + (c + 1) * cell - (0 if c == len(row) - 1 else 5)
            story_card(draw, (bx0, ry, bx1, ry + row_h - 10), headline, blurb)

    return page


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "entry.png"
    build_page().save(out, format="PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes)")
