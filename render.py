#!/usr/bin/env python3
"""Render the 25 November 2026 world-news summary image (1024x1024).

Build-time only: reads stories.json, draws with PIL, writes entry.png.
The graded program (main.py) only copies entry.png to the output dir.
"""
import json
import math
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
PAPER = (247, 243, 234)
INK = (20, 20, 20)
RED = (180, 35, 24)
NAVY = (23, 54, 93)
TEAL = (15, 118, 110)
GOLD = (180, 83, 9)
GREY = (107, 114, 128)
LINE = (216, 210, 196)
SEA = (220, 232, 240)
LAND = (232, 224, 204)
W = 1024
H = 1024


def font(name, size):
    return ImageFont.truetype(os.path.join(BASE, "fonts", name), size)


SERIF = lambda s: font("DejaVuSerif-Bold.ttf", s)
SANSB = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text(draw, xy, s, fnt, fill=INK, anchor="la"):
    draw.text(xy, s, font=fnt, fill=fill, anchor=anchor)


def block(draw, x, y, lines, fnt, max_w, leading, fill=INK, max_lines=None):
    out = []
    for ln in lines:
        out.extend(wrap(draw, ln, fnt, max_w))
    if max_lines:
        out = out[:max_lines]
    for i, ln in enumerate(out):
        draw.text((x, y + i * leading), ln, font=fnt, fill=fill)
    return y + len(out) * leading


def draw_hero_illustration(draw, x, y, w, h):
    # Night sea, flat geometric style: dark navy sky, asymmetric blast, sinking warship.
    # Deliberately NOT a round disc: jagged flame tongues + debris + black smoke,
    # so the image reads as an explosion/fire, never a sunset. No moon.
    draw.rectangle([x, y, x + w, y + h], fill=(16, 32, 64))
    # stars, kept away from the blast so the fire reads clearly
    for sx, sy in [(40, 26), (120, 52), (210, 20), (300, 44), (90, 90), (250, 84)]:
        draw.ellipse([x + sx - 2, y + sy - 2, x + sx + 2, y + sy + 2], fill=(240, 235, 210))
    # blast: layered jagged flame tongues rising off the stricken warship
    draw.polygon([(x + 372, y + 192), (x + 388, y + 128), (x + 406, y + 150),
                  (x + 420, y + 88), (x + 438, y + 122), (x + 452, y + 58),
                  (x + 470, y + 112), (x + 486, y + 70), (x + 500, y + 118),
                  (x + 520, y + 92), (x + 534, y + 140), (x + 548, y + 118),
                  (x + 556, y + 192)], fill=(205, 70, 12))
    draw.polygon([(x + 392, y + 192), (x + 404, y + 140), (x + 420, y + 160),
                  (x + 434, y + 104), (x + 450, y + 132), (x + 462, y + 82),
                  (x + 478, y + 124), (x + 492, y + 96), (x + 506, y + 136),
                  (x + 522, y + 120), (x + 534, y + 192)], fill=(255, 140, 40))
    draw.polygon([(x + 414, y + 192), (x + 426, y + 150), (x + 442, y + 168),
                  (x + 452, y + 118), (x + 466, y + 152), (x + 480, y + 128),
                  (x + 496, y + 164), (x + 512, y + 150), (x + 520, y + 192)],
                 fill=(255, 205, 90))
    # side tongues leaning outward
    draw.polygon([(x + 352, y + 192), (x + 362, y + 150), (x + 376, y + 172),
                  (x + 388, y + 192)], fill=(230, 100, 20))
    draw.polygon([(x + 548, y + 192), (x + 560, y + 158), (x + 572, y + 178),
                  (x + 580, y + 192)], fill=(230, 100, 20))
    # thick black smoke column rising off the flames, drifting left
    for sx, sy, r, col in [(500, 62, 20, (52, 52, 60)), (478, 40, 24, (44, 44, 52)),
                           (448, 22, 20, (60, 60, 68)), (418, 12, 14, (44, 44, 52)),
                           (528, 78, 16, (52, 52, 60)), (552, 96, 13, (70, 70, 78))]:
        draw.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r], fill=col)
    # debris chunks flying off the blast
    for pts in [[(330, 96), (342, 88), (348, 100), (336, 106)],
                [(566, 66), (580, 60), (586, 72), (572, 78)],
                [(592, 130), (604, 124), (608, 136), (596, 140)],
                [(318, 150), (330, 144), (336, 154), (324, 160)]]:
        draw.polygon([(x + px, y + py) for px, py in pts], fill=(12, 12, 16))
    # embers
    for ex, ey, r in [(360, 120, 3), (400, 70, 3), (520, 60, 3), (560, 110, 3),
                      (340, 170, 2), (590, 170, 2), (470, 45, 2)]:
        draw.ellipse([x + ex - r, y + ey - r, x + ex + r, y + ey + r], fill=(255, 190, 60))
    # sea
    draw.rectangle([x, y + 190, x + w, y + h], fill=(24, 58, 96))
    for wy in (215, 240, 268):
        for wx in range(20, w - 20, 70):
            draw.line([x + wx, y + wy, x + wx + 34, y + wy], fill=(120, 170, 210), width=3)
    # fire reflection on the water under the blast
    for rx, ry, rw in [(400, 200, 120), (420, 214, 90), (440, 228, 60),
                       (410, 244, 80), (450, 258, 50)]:
        draw.line([x + rx, y + ry, x + rx + rw, y + ry], fill=(255, 140, 50), width=4)
    # cargo ship silhouette (left) with a small deck fire
    draw.rectangle([x + 60, y + 176, x + 240, y + 216], fill=(10, 18, 34))
    draw.rectangle([x + 96, y + 150, x + 150, y + 176], fill=(10, 18, 34))
    draw.rectangle([x + 196, y + 158, x + 210, y + 176], fill=(10, 18, 34))
    for px in (80, 120, 160, 200):
        draw.rectangle([x + px, y + 186, x + px + 14, y + 198], fill=(255, 190, 80))
    draw.polygon([(x + 110, y + 176), (x + 118, y + 158), (x + 124, y + 170),
                  (x + 130, y + 156), (x + 136, y + 176)], fill=(255, 150, 40))
    # sinking warship (right): bigger, listing hard, stern going under
    draw.polygon([(x + 340, y + 208), (x + 545, y + 168), (x + 580, y + 178),
                  (x + 592, y + 192), (x + 430, y + 232), (x + 360, y + 224)],
                 fill=(8, 14, 28))
    # leaning superstructure + broken mast
    draw.polygon([(x + 470, y + 178), (x + 508, y + 170), (x + 514, y + 146),
                  (x + 478, y + 152)], fill=(8, 14, 28))
    draw.line([x + 520, y + 170, x + 548, y + 118], fill=(8, 14, 28), width=6)
    draw.line([x + 520, y + 170, x + 500, y + 128], fill=(8, 14, 28), width=4)
    # bow gun turret
    draw.polygon([(x + 540, y + 172), (x + 566, y + 167), (x + 572, y + 176),
                  (x + 546, y + 180)], fill=(8, 14, 28))
    # drones: small dots with cross arms
    for dx, dy in [(150, 60), (330, 40), (430, 110)]:
        draw.ellipse([x + dx - 4, y + dy - 4, x + dx + 4, y + dy + 4], fill=(255, 220, 120))
        draw.line([x + dx - 10, y + dy, x + dx + 10, y + dy], fill=(255, 220, 120), width=2)
        draw.line([x + dx, y + dy - 10, x + dx, y + dy + 10], fill=(255, 220, 120), width=2)


def draw_map(draw, x, y, w, h, pins):
    draw.rectangle([x, y, x + w, y + h], fill=SEA)
    # schematic landmasses (equirectangular, lon -180..180 -> x, lat 85..-60 -> y)
    def px(lon):
        return x + (lon + 180) / 360.0 * w
    def py(lat):
        return y + (85 - lat) / 145.0 * h
    land_polys = [
        # North America
        [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 80), (-85, 70),
         (-75, 62), (-60, 47), (-70, 42), (-75, 35), (-80, 26), (-90, 21),
         (-97, 26), (-105, 20), (-110, 24), (-120, 34), (-125, 48), (-140, 60),
         (-155, 58), (-165, 60)],
        # South America (north coast raised to lat ~11-12 so Cartagena sits on land)
        [(-80, 11), (-77, 11), (-72, 12), (-66, 11), (-62, 10), (-60, 5), (-50, -5), (-35, -8), (-40, -20),
         (-48, -28), (-58, -35), (-65, -45), (-70, -52), (-73, -40),
         (-72, -25), (-77, -12), (-80, -3)],
        # Europe
        [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (10, 59),
         (18, 56), (21, 55), (24, 58), (30, 60), (30, 70), (20, 70), (12, 66),
         (5, 60), (5, 58), (0, 55), (-5, 50), (-10, 44), (-9, 38)],
        # Africa
        [(-6, 35), (10, 37), (20, 32), (32, 31), (35, 28), (43, 12), (51, 11),
         (48, 2), (40, -10), (36, -18), (32, -26), (20, -35), (16, -28),
         (12, -18), (9, -1), (-8, 4), (-13, 8), (-17, 15), (-16, 25), (-10, 31)],
        # Asia
        [(30, 70), (40, 68), (55, 68), (70, 72), (90, 75), (110, 76), (130, 72),
         (160, 69), (178, 65), (162, 60), (158, 52), (142, 50), (140, 40),
         (127, 35), (122, 30), (110, 20), (105, 10), (100, 8), (97, 16),
         (92, 21), (88, 22), (80, 13), (77, 8), (73, 20), (66, 25), (60, 25),
         (57, 26), (52, 28), (48, 30), (44, 29), (40, 32), (36, 36), (30, 36),
         (28, 41), (24, 45), (20, 45), (15, 44), (12, 45), (8, 44), (3, 42),
         (0, 40), (-2, 37), (10, 38), (20, 40), (28, 45), (30, 46), (30, 55),
         (32, 60), (30, 66)],
        # Australia
        [(114, -22), (114, -30), (115, -35), (124, -33), (130, -32), (136, -35),
         (140, -38), (147, -39), (150, -37), (153, -27), (146, -19), (142, -11),
         (136, -12), (132, -12), (126, -14), (122, -17), (118, -20)],
        # SE Asia islands / Indonesia
        [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -10),
         (125, -9), (130, -3), (135, -4), (140, -8), (138, -2), (132, 0),
         (128, 2), (122, 0), (118, -2), (112, -6), (106, -6), (100, -2),
         (96, 2)],
        # Sumatra (fat diagonal) + Java (fat band) so pin 11 has land under it
        [(95, 5), (98, 3), (101, 0), (104, -3), (106, -5), (104, -6),
         (100, -3), (97, 0), (95, 3)],
        [(105, -6), (110, -6.5), (114, -7), (114, -8.5), (110, -8.5), (105, -7.5)],
        # UK + Japan hints
        [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (0, 53), (-1, 51)],
        [(130, 31), (133, 34), (137, 35), (140, 38), (141, 42), (143, 44),
         (141, 40), (139, 36), (135, 33), (131, 33)],
    ]
    for poly in land_polys:
        pts = [(px(lon), py(lat)) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=(190, 178, 150))
    # graticule
    for lon in range(-150, 181, 30):
        draw.line([px(lon), y, px(lon), y + h], fill=(200, 214, 226), width=1)
    for lat in range(-60, 86, 30):
        draw.line([x, py(lat), x + w, py(lat)], fill=(200, 214, 226), width=1)
    # pins (small display nudges keep close pins readable; kept tiny so pins stay on land)
    offsets = {1: (14, -10), 3: (12, 8), 4: (12, -8), 5: (-10, 8),
               6: (-10, -10), 7: (10, 10), 8: (0, 0), 9: (-12, -6),
               10: (-4, 0), 11: (0, -2), 12: (0, 0)}
    for n, name, lat, lon in pins:
        dx, dy = offsets.get(n, (0, 0))
        cx, cy = px(lon) + dx, py(lat) + dy
        r = 10
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED, outline=(255, 255, 255), width=2)
        draw.text((cx, cy), str(n), font=SANSB(11), fill=(255, 255, 255), anchor="mm")


def render():
    with open(os.path.join(BASE, "stories.json"), encoding="utf-8") as f:
        d = json.load(f)
    img = Image.new("RGB", (W, H), PAPER)
    dr = ImageDraw.Draw(img)

    # ---- Masthead ----
    text(dr, (12, 8), d["masthead"], SERIF(44), INK)
    text(dr, (12, 62), d["date"], SANSB(20), RED)
    dr.line([12, 96, 1012, 96], fill=INK, width=3)
    dr.line([12, 100, 1012, 100], fill=INK, width=1)

    # ---- Hero ----
    hx, hy, hw, hh = 12, 108, 608, 292
    draw_hero_illustration(dr, hx, hy, hw, hh)
    tx = 636
    text(dr, (tx, 112), d["hero"]["kicker"], SANSB(15), RED)
    dr.line([tx, 136, 1012, 136], fill=LINE, width=1)
    y = block(dr, tx, 146, [d["hero"]["headline"]], SERIF(29), 376, 36, max_lines=4)
    y = block(dr, tx, y + 6, [d["hero"]["deck"]], SANS(14), 376, 17, max_lines=7)
    text(dr, (tx, 388), d["hero"]["source"], SANS(11), GREY)

    # ---- Stats bar ----
    sy = 408
    dr.rectangle([12, sy, 1012, sy + 54], fill=NAVY)
    text(dr, (24, sy + 8), d["markets"]["label"], SANSB(13), (255, 255, 255))
    mx = 24
    for name, val, chg in d["markets"]["items"]:
        s = f"{name} {val}" + (f" {chg}" if chg else "")
        col = (140, 220, 170) if chg.startswith("+") else ((255, 150, 130) if chg.startswith("-") else (255, 255, 255))
        text(dr, (mx, sy + 28), s, SANSB(14), col)
        mx += dr.textlength(s, font=SANSB(14)) + 26
    # Dell line, right side under label row is too tight: put Dell on second row right
    dell = d["markets"]["dell"]
    text(dr, (1012, sy + 8), dell, SANS(11), (200, 215, 235), anchor="ra")

    # ---- Grid ----
    gx, gy = 12, 472
    cw, chh, gap = 330, 124, 4
    for i, g in enumerate(d["grid"]):
        cx = gx + (i % 3) * (cw + gap)
        cy = gy + (i // 3) * (chh + gap)
        dr.rectangle([cx, cy, cx + cw, cy + chh], outline=LINE, width=1)
        # pin badge
        dr.ellipse([cx + 10, cy + 10, cx + 32, cy + 32], fill=RED)
        dr.text((cx + 21, cy + 21), str(g["n"]), font=SANSB(12), fill=(255, 255, 255), anchor="mm")
        text(dr, (cx + 40, cy + 12), g["kicker"], SANSB(12), RED)
        y2 = block(dr, cx + 10, cy + 38, [g["headline"]], SERIF(17), cw - 20, 21, max_lines=2)
        block(dr, cx + 10, y2 + 2, [g["deck"]], SANS(13), cw - 20, 16, max_lines=1)
        text(dr, (cx + 10, cy + chh - 18), g["source"], SANS(10), GREY)

    # ---- Bottom: map (left) ----
    bx, by = 12, 732
    bw, bh = 360, 242
    text(dr, (bx, by), "WHERE IT HAPPENED", SANSB(13), NAVY)
    draw_map(dr, bx, by + 22, bw, bh - 22, d["pins"])

    # ---- Bottom right: more / timeline / date check ----
    rx = 392
    y = by
    text(dr, (rx, y), "MORE OF THE DAY", SANSB(13), NAVY)
    y += 18
    badges = ["7", "8", "9", "10", "11", "–"]
    for i, (lead, rest) in enumerate(d["more"]):
        dr.ellipse([rx, y + 1, rx + 15, y + 16], fill=RED)
        dr.text((rx + 8, y + 8), badges[i], font=SANSB(10), fill=(255, 255, 255), anchor="mm")
        ln = f"{lead} — {rest}"
        y = block(dr, rx + 24, y, [ln], SANS(13), 1012 - rx - 24, 15, max_lines=1)
        y += 1
    y += 2
    text(dr, (rx, y), "TIMELINE — TUE INTO WED, UTC", SANSB(12), NAVY)
    y += 16
    for t, ev in d["timeline"]:
        text(dr, (rx, y), t, SANSB(13), RED)
        y = block(dr, rx + 92, y, [ev], SANS(13), 1012 - rx - 92, 14, max_lines=1)
        y += 1
    y += 3
    # date check box
    box_h = 1000 - y
    dr.rectangle([rx, y, 1012, y + box_h], outline=RED, width=2, fill=(255, 248, 240))
    text(dr, (rx + 10, y + 5), "DATE CHECK", SANSB(12), RED)
    block(dr, rx + 10, y + 22, [d["date_check"]], SANS(12), 1012 - rx - 20, 14, max_lines=3)

    # ---- Footer ----
    text(dr, (512, 1006), d["footer"], SANS(10), GREY, anchor="ma")

    out = os.path.join(BASE, "entry.png")
    img.save(out, optimize=True)
    print(out, img.size, os.path.getsize(out))


if __name__ == "__main__":
    render()
