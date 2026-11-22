#!/usr/bin/env python3
"""Draw the news-image-20261121 entry: a newspaper front page summing up
Saturday 21 November 2026 in one 1024x1024 PNG. Deterministic, no network."""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (250, 247, 238)
INK = (22, 22, 22)
GREY = (90, 90, 90)
RED = (178, 34, 34)
BLUE = (30, 70, 140)
NIGHT = (14, 22, 52)
FIELD = (46, 62, 34)
FIELD_D = (36, 50, 27)
ORANGE = (255, 140, 30)
YELLOW = (255, 210, 80)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_BOLD = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS_OBL = "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, fnt):
    return draw.textlength(s, font=fnt)


def center(draw, y, s, fnt, fill=INK):
    draw.text(((W - text_w(draw, s, fnt)) / 2, y), s, font=fnt, fill=fill)


def wrap(draw, s, fnt, max_w):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if text_w(draw, trial, fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def center_block(draw, cx, y, s, fnt, fill, max_w, line_h):
    for line in wrap(draw, s, fnt, max_w):
        draw.text((cx - text_w(draw, line, fnt) / 2, y), line, font=fnt, fill=fill)
        y += line_h
    return y


def flash(draw, cx, cy, r):
    """Explosion starburst."""
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        rr = r if i % 2 == 0 else r * 0.38
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    draw.polygon(pts, fill=ORANGE)
    pts2 = [(cx + (x - cx) * 0.55, cy + (y - cy) * 0.55) for x, y in pts]
    draw.polygon(pts2, fill=YELLOW)
    draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 245, 200))


def nato_star(draw, cx, cy, r, fill):
    """Four-point compass star of the NATO emblem."""
    pts = []
    for i in range(8):
        ang = math.pi * i / 4 - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.22
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def draw_lead_art(draw):
    x0, y0, x1, y1 = 46, 336, 978, 516
    horizon = y1 - 52
    # night sky in horizontal bands
    for i in range(24):
        t = i / 24
        col = tuple(int(NIGHT[c] + (40 - NIGHT[c]) * t) for c in range(3))
        draw.rectangle([x0, y0 + i * 5, x1, y0 + (i + 1) * 5 + 1], fill=col)
    # stars (seeded, deterministic)
    rng = random.Random(20261121)
    for _ in range(70):
        sx = rng.randint(x0 + 8, x1 - 8)
        sy = rng.randint(y0 + 6, y0 + 88)
        draw.point((sx, sy), fill=(230, 235, 255))
        if rng.random() < 0.3:
            draw.point((sx + 1, sy), fill=(180, 190, 230))
    # moon
    draw.ellipse([x0 + 40, y0 + 14, x0 + 84, y0 + 58], fill=(238, 240, 220))
    draw.ellipse([x0 + 48, y0 + 22, x0 + 56, y0 + 30], fill=(205, 208, 195))
    # missile streak falling from the top-right sky to the field
    crater = (x1 - 300, horizon + 18)
    draw.line([x1 - 90, y0 + 8, crater[0] + 26, crater[1] - 30],
              fill=(200, 205, 225), width=3)
    draw.line([x1 - 70, y0 + 26, crater[0] + 34, crater[1] - 22],
              fill=(140, 150, 185), width=2)
    # fields: two bands with furrow lines running to the horizon
    draw.rectangle([x0, horizon, x1, y1], fill=FIELD)
    draw.rectangle([x0, horizon + 26, x1, y1], fill=FIELD_D)
    vx = (x0 + x1) // 2
    for dx in range(-420, 421, 60):
        draw.line([vx + dx // 3, horizon, vx + dx, y1], fill=(24, 34, 18), width=2)
    draw.line([x0, horizon, x1, horizon], fill=(24, 34, 18), width=2)
    # village silhouettes on the left, windows lit
    for (hx, hw, hh) in ((x0 + 26, 54, 34), (x0 + 96, 44, 28), (x0 + 152, 60, 38)):
        draw.rectangle([hx, horizon - hh, hx + hw, horizon], fill=(10, 12, 20))
        draw.polygon([(hx - 4, horizon - hh), (hx + hw + 4, horizon - hh),
                      (hx + hw // 2, horizon - hh - 16)], fill=(8, 9, 16))
        draw.rectangle([hx + hw // 2 - 5, horizon - hh + 12,
                        hx + hw // 2 + 5, horizon - hh + 22], fill=YELLOW)
    # Polish flag on a pole by the village (white over red)
    px = x0 + 238
    draw.line([px, horizon - 74, px, horizon], fill=(200, 200, 200), width=3)
    draw.rectangle([px + 2, horizon - 74, px + 46, horizon - 62], fill=(245, 245, 245))
    draw.rectangle([px + 2, horizon - 62, px + 46, horizon - 50], fill=RED)
    # NATO emblem roundel in the sky, right of centre
    ncx, ncy = x0 + 300, y0 + 44
    draw.ellipse([ncx - 27, ncy - 27, ncx + 27, ncy + 27], fill=(16, 42, 92),
                 outline=(210, 218, 235), width=2)
    nato_star(draw, ncx, ncy, 21, (235, 240, 250))
    # crater flash + smoke where the missile came down
    flash(draw, crater[0], crater[1], 26)
    draw.ellipse([crater[0] - 34, crater[1] + 8, crater[0] + 40, crater[1] + 18],
                 fill=(16, 20, 12))
    for (sx, sy, sr) in ((crater[0] + 44, crater[1] - 26, 14),
                         (crater[0] + 66, crater[1] - 38, 10),
                         (crater[0] - 52, crater[1] - 18, 11)):
        draw.ellipse([sx - sr, sy - sr // 2, sx + sr, sy + sr // 2],
                     fill=(105, 108, 120))
    draw.rectangle([x0, y0, x1, y1], outline=INK, width=2)


# ---- panel icons (drawn in a box centred on cx, top at y) ----

def icon_missile(draw, cx, y):
    # diagonal missile with fins and an exhaust flame
    draw.polygon([(cx - 16, y + 34), (cx + 12, y + 6), (cx + 22, y - 4),
                  (cx + 28, y + 2), (cx + 2, y + 30)], fill=INK)
    draw.polygon([(cx - 16, y + 34), (cx - 26, y + 30), (cx - 20, y + 42)],
                 fill=RED)
    draw.polygon([(cx - 2, y + 28), (cx - 10, y + 40), (cx + 4, y + 36)],
                 fill=INK)
    pts = [(cx - 22, y + 40), (cx - 34, y + 48), (cx - 16, y + 46),
           (cx - 28, y + 54), (cx - 12, y + 50)]
    draw.polygon(pts, fill=ORANGE)
    draw.ellipse([cx - 22, y + 42, cx - 14, y + 50], fill=YELLOW)


def icon_ship(draw, cx, y):
    draw.polygon([(cx - 40, y + 26), (cx + 40, y + 26), (cx + 30, y + 40),
                  (cx - 30, y + 40)], fill=INK)
    draw.rectangle([cx - 14, y + 14, cx + 16, y + 26], fill=INK)
    draw.rectangle([cx - 4, y + 4, cx + 8, y + 14], fill=INK)
    draw.rectangle([cx - 34, y + 18, cx - 20, y + 26], fill=RED)
    for dx in (-30, -6, 18):
        draw.arc([cx + dx, y + 38, cx + dx + 18, y + 50], start=0, end=180,
                 fill=BLUE, width=3)


def icon_flame(draw, cx, y):
    pts = [(cx, y - 6), (cx + 10, y + 10), (cx + 18, y + 22),
           (cx + 14, y + 38), (cx + 4, y + 46), (cx - 6, y + 44),
           (cx - 15, y + 34), (cx - 14, y + 18), (cx - 6, y + 8)]
    draw.polygon(pts, fill=ORANGE)
    pts2 = [(cx + (x - cx) * 0.55, y + 16 + (yy - (y + 16)) * 0.55)
            for (x, yy) in pts]
    draw.polygon(pts2, fill=RED)
    draw.ellipse([cx - 5, y + 30, cx + 5, y + 44], fill=YELLOW)


def icon_bolt(draw, cx, y):
    draw.ellipse([cx - 26, y - 4, cx + 26, y + 48], outline=INK, width=3)
    pts = [(cx + 8, y + 2), (cx - 10, y + 26), (cx - 1, y + 26),
           (cx - 8, y + 44), (cx + 12, y + 18), (cx + 2, y + 18)]
    draw.polygon(pts, fill=YELLOW)
    draw.polygon(pts, outline=INK)


def icon_badge(draw, cx, y):
    star = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = 24 if i % 2 == 0 else 10
        star.append((cx + rr * math.cos(ang), y + 22 + rr * math.sin(ang)))
    draw.polygon(star, fill=BLUE)
    draw.ellipse([cx - 6, y + 16, cx + 6, y + 28], fill=(245, 245, 245))


def icon_shield(draw, cx, y):
    pts = [(cx, y - 4), (cx + 26, y + 4), (cx + 26, y + 22),
           (cx, y + 48), (cx - 26, y + 22), (cx - 26, y + 4)]
    draw.polygon(pts, fill=BLUE)
    star = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = 11 if i % 2 == 0 else 4.5
        star.append((cx + rr * math.cos(ang), y + 20 + rr * math.sin(ang)))
    draw.polygon(star, fill=(255, 255, 255))


def icon_thermo(draw, cx, y):
    draw.rounded_rectangle([cx - 8, y - 4, cx + 8, y + 30], radius=8,
                           outline=INK, width=3)
    draw.ellipse([cx - 13, y + 24, cx + 13, y + 50], outline=INK, width=3)
    draw.ellipse([cx - 8, y + 29, cx + 8, y + 45], fill=RED)
    draw.rectangle([cx - 3, y + 12, cx + 3, y + 34], fill=RED)
    draw.ellipse([cx + 16, y + 6, cx + 42, y + 24], fill=(46, 125, 50))
    draw.line([cx + 17, y + 23, cx + 41, y + 7], fill=(220, 240, 220), width=2)


def panel(draw, x0, y0, x1, y1, icon, headline, summary):
    draw.rectangle([x0, y0, x1, y1], outline=INK, width=2)
    cx = (x0 + x1) // 2
    icon(draw, cx, y0 + 13)
    hf = font(SANS_BOLD, 18)
    sf = font(SANS, 14)
    y = center_block(draw, cx, y0 + 60, headline, hf, INK, x1 - x0 - 16, 22)
    center_block(draw, cx, y + 2, summary, sf, (45, 45, 45), x1 - x0 - 16, 18)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    draw.rectangle([14, 14, W - 14, H - 14], outline=INK, width=3)
    draw.rectangle([22, 22, W - 22, H - 22], outline=INK, width=1)

    # masthead
    center(draw, 34, "THE DAILY PICTURE", font(SERIF_BOLD, 57))
    draw.rectangle([40, 106, W - 40, 108], fill=INK)
    draw.rectangle([40, 112, W - 40, 116], fill=INK)
    date_f = font(SANS_BOLD, 39)
    center(draw, 126, "SATURDAY 21 NOVEMBER 2026", date_f, RED)
    draw.text((44, 138), "VOL. I", font=font(SANS_BOLD, 16), fill=GREY)
    right = "ONE PAGE"
    draw.text((W - 44 - text_w(draw, right, font(SANS_BOLD, 16)), 138),
              right, font=font(SANS_BOLD, 16), fill=GREY)
    draw.rectangle([40, 176, W - 40, 178], fill=INK)

    # lead story
    center(draw, 188, "NATO CRISIS - LEAD STORY", font(SANS_BOLD, 18), RED)
    lead_f = font(SANS_BOLD, 45)
    center(draw, 214, "NATO VOWS TO DEFEND", lead_f)
    center(draw, 268, "'EVERY INCH' OF POLAND", lead_f)
    draw_lead_art(draw)
    center(draw, 524, "A Russian Kh-101 in a field near Nowy Lipowiec, 50 km from Ukraine.",
           font(SANS_OBL, 15), GREY)
    sf = font(SANS, 21)
    center(draw, 552, "Rutte in Warsaw: the alliance will defend 'every inch' of Poland.", sf)
    center(draw, 580, "Warsaw calls the landings a deliberate provocation, seeks jets", sf)
    center(draw, 608, "and radar. Trump: 'by mistake'. Zelensky: Putin is a 'killer'.", sf)
    draw.rectangle([40, 644, W - 40, 647], fill=INK)

    # grid of panels: row A (4), row B (3)
    panels_a = [
        (icon_missile, "IRAN STRIKES US BASES",
         "Tehran claims hits on US radars in Bahrain; a civilian plant burns."),
        (icon_ship, "TANKERS HIT IN HORMUZ",
         "Two tankers struck by projectiles near Oman; Iran says a third hit a naval mine."),
        (icon_shield, "MISSILES FIRED AT RIYADH",
         "Saudi defences down three Houthi ballistic missiles over the capital overnight."),
        (icon_flame, "PALISADES ARSONIST GUILTY",
         "Man convicted of starting the Los Angeles fire that killed 12, razed 6,800 buildings."),
    ]
    panels_b = [
        (icon_bolt, "RUSSIA POUNDS UKRAINE'S GRID",
         "Mass attack hits Europe's largest substation. Kryvyi Rih 'double tap': 2 dead, 60 hurt."),
        (icon_thermo, "COP31 STALLS ON FOSSIL FUELS",
         "Antalya talks deadlock over a fossil-fuel phase-out; new draft tries to save it."),
        (icon_badge, "CARTEL KINGPIN CAPTURED",
         "Mexico arrests 'El Chapo Isidro', on the FBI's 10 most wanted list, after a shoot-out."),
    ]
    gx0, gx1, gap = 40, W - 40, 10
    pw_a = (gx1 - gx0 - gap * 3) // 4
    for i, (ic, hd, sm) in enumerate(panels_a):
        x0 = gx0 + i * (pw_a + gap)
        panel(draw, x0, 658, x0 + pw_a, 822, ic, hd, sm)
    pw_b = (gx1 - gx0 - gap * 2) // 3
    for i, (ic, hd, sm) in enumerate(panels_b):
        x0 = gx0 + i * (pw_b + gap)
        panel(draw, x0, 832, x0 + pw_b, 990, ic, hd, sm)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.dirname(
        os.path.abspath(__file__))
    out = os.path.join(out_dir, "entry.png")
    img.save(out, format="PNG", optimize=False)
    print("wrote", out)


if __name__ == "__main__":
    main()
