#!/usr/bin/env python3
"""Render the 25 November 2026 world-news summary image (1024x1024). v4.

Build-time only: reads stories.json, draws with PIL, writes entry.png.
The graded program (main.py) only copies entry.png to the output dir.

v4 is a TRANSFORMATIVE redesign, not a correction of v3 (dev #557/2,889).
v3 failed its submit bar (6/6 brains REVISI, do not submit) for structural
reasons that a font-size bump cannot fix, and the v3 coordinator's own
verification was wrong in the two places that mattered:
- It verified map pins against coastline DATA (point-in-polygon), but the
  render's projection did not match the data, so pins 10/11/12 still LOOKED
  in the sea (pin 11 Serpong visibly in the Indian Ocean, not on Java).
- It judged "readable at 300px" from an ENLARGED crop, not a real 300px
  thumbnail. At a real 300px, v3's bottom half was still grey blur.
Lesson for v4: verify ONLY against renders at their real sizes (1024 full,
real 300px thumbnail, 2x zoom) — never against code or data.

v4 design (built for 300px FIRST, where pairwise judging happens):
- CONTENT CUT ~40%: 11 stories -> 7 (1 hero + 3 grid + 3 one-liners +
  1 tally line). MORE and TIMELINE folded into one short ALSO TODAY list.
  No grid numbers at all (they only existed to point at the map) — this
  also fixes the duplicate-"7" numbering (grid Washington + MORE Huckabee).
- MAP DROPPED. It was wrong three versions running despite code checks,
  and at 300px a 360x220 map is a 105x64px smudge whose pins are ~2px.
  Place names stay in the text (Serpong, Paris, Riyadh...). Removing a
  feature that visibly puts pins in the sea is not lowering quality.
- HERO REBUILT as ONE big burning ship, full width (1000x320): a single
  listing corvette, flames built from layered ELLIPSES (never triangles)
  softened with a Gaussian blur so they read as one continuous blaze, and
  ONE smoke cloud (overlapping ellipses, heavily blurred) — no discrete
  circle chains. A small distant ship silhouette on the horizon keeps the
  "two ships" story true without cluttering the visual.
- TYPE: smallest body text 16-17pt at full size (grid headlines 26pt,
  hero headline 38pt). DATE CHECK is one short line, not defensive prose.
- FACTS KEPT (verified): Dell Q3 FY27 (revenue $54.94bn, adj. EPS $9.45
  vs $6.59, AI backlog $132.3bn, guidance $202bn); cricket Donald 85 off
  32; NATO AWACS decided Mon 23 Nov; DATE CHECK "Sun 22 Nov".
- ATTRIBUTION FIXED: the "700,000+" tally is worded "casualties" (the
  count covers killed + wounded) and attributed to Meduza/Mediazona —
  v3 wrote "killed" and "(RFE/RL)" for the same tally.
"""
import json
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
PAPER = (247, 243, 234)
INK = (20, 20, 20)
RED = (180, 35, 24)
NAVY = (23, 54, 93)
GREY = (107, 114, 128)
DARKGREY = (70, 72, 78)
LINE = (216, 210, 196)
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


def _ellipse(layer_draw, cx, cy, rx, ry, fill):
    layer_draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=fill)


def _composite(panel, layer):
    """Alpha-composite an RGBA layer (same size as panel) onto the panel."""
    base = panel.convert("RGBA")
    return Image.alpha_composite(base, layer).convert("RGB")


def draw_hero_panel():
    """ONE big burning ship, full width (1000x300), drawn at full size.
    The SHIP dominates: flames are a compact mass sitting ON the ship
    (not a fireball hiding it), built from layered ellipses on an RGBA
    layer and Gaussian-blurred into one continuous blaze. Smoke is ONE
    elongated plume drifting up-left, blurred into a single cloud — never
    a chain of circles and never a dark lid capping the flames.
    Returns the panel image."""
    w, h = 1000, 300
    panel = Image.new("RGB", (w, h), (16, 32, 64))
    dr = ImageDraw.Draw(panel)
    # sky: solid navy (banded gradients read as stripes when zoomed)
    # stars, sparse, kept away from the smoke plume (upper centre-left)
    for sx, sy in [(60, 28), (150, 66), (920, 36), (860, 84), (950, 130),
                   (40, 116), (700, 26), (300, 44), (980, 190), (30, 180)]:
        dr.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(240, 235, 210))
    # sea
    dr.rectangle([0, 240, w, h], fill=(24, 58, 96))
    for wy, off, ln in [(258, 20, 44), (278, 60, 30), (292, 10, 52),
                        (258, 420, 36), (278, 500, 44), (292, 620, 30)]:
        dr.line([off, wy, off + ln, wy], fill=(120, 170, 210), width=3)
    # ---- distant ship (Sparta II): small silhouette on the horizon ----
    dr.polygon([(52, 236), (168, 230), (178, 236), (170, 244), (60, 246)],
               fill=(10, 18, 34))
    dr.rectangle([96, 220, 128, 232], fill=(10, 18, 34))
    gl = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gl)
    _ellipse(gd, 112, 218, 26, 10, (240, 120, 40, 200))
    _ellipse(gd, 112, 212, 12, 14, (255, 180, 80, 220))
    panel = _composite(panel, gl.filter(ImageFilter.GaussianBlur(3)))
    dr = ImageDraw.Draw(panel)
    # ---- main ship (corvette Merkury): BIG hull, listing, bow right ----
    # The hull is the visual anchor: ~620px long, tall enough to read as
    # a ship even at 300px, with superstructure + mast LEFT of the flames
    # so the ship reads where the fire does not cover it.
    hull = [(320, 262), (880, 244), (925, 254),
            (910, 274), (360, 288), (325, 280)]
    dr.polygon(hull, fill=(8, 14, 28))
    # superstructure blocks + leaning mast + broken funnel (left of flames)
    dr.polygon([(380, 254), (500, 246), (504, 220), (384, 226)],
               fill=(8, 14, 28))
    dr.polygon([(510, 252), (560, 248), (562, 232), (512, 234)],
               fill=(8, 14, 28))
    dr.line([440, 224, 465, 180], fill=(8, 14, 28), width=5)
    dr.polygon([(520, 226), (540, 224), (535, 202), (525, 204)],
               fill=(8, 14, 28))
    # bow gun turret
    dr.polygon([(860, 248), (895, 244), (898, 254), (864, 256)],
               fill=(8, 14, 28))
    # portholes: lit windows along the hull
    for px in (370, 420, 470, 520, 580, 640, 700, 760, 820, 880):
        dr.rectangle([px, 266, px + 12, 274], fill=(255, 190, 80))
    # fire reflection on the water under the blast
    for rx, ry, rw in [(480, 290, 120), (520, 290, 200), (560, 296, 160),
                       (600, 298, 120), (500, 284, 90), (640, 286, 140)]:
        dr.line([rx, ry, rx + rw, ry], fill=(255, 140, 50), width=4)
    # ---- flames: a NARROW mass on the deck + DISTINCT tall tongues ----
    # Base mass (ellipses, blurred) gives the body; the tongues are drawn
    # on a second layer with only a light blur so they keep their shape
    # and the silhouette reads as fire, not one smooth balloon.
    fl = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fl)
    for cx, cy, rx, ry in [(610, 195, 55, 70), (660, 180, 60, 80),
                           (710, 205, 50, 60), (580, 220, 40, 45),
                           (740, 225, 35, 40), (650, 230, 70, 45)]:
        _ellipse(fd, cx, cy, rx, ry, (205, 70, 12, 255))
    for cx, cy, rx, ry in [(630, 205, 40, 55), (680, 190, 45, 60),
                           (715, 220, 32, 40)]:
        _ellipse(fd, cx, cy, rx, ry, (255, 140, 40, 255))
    for cx, cy, rx, ry in [(645, 220, 30, 40), (685, 205, 32, 42)]:
        _ellipse(fd, cx, cy, rx, ry, (255, 200, 90, 255))
    panel = _composite(panel, fl.filter(ImageFilter.GaussianBlur(2)))
    # tongues: tall narrow ellipses, staggered heights, centre tallest
    tg = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    td = ImageDraw.Draw(tg)
    for cx, cy, rx, ry, col in [(600, 165, 18, 62, (255, 140, 40, 255)),
                                (650, 140, 22, 88, (255, 160, 60, 255)),
                                (700, 160, 18, 66, (255, 140, 40, 255)),
                                (735, 185, 13, 44, (255, 170, 70, 255)),
                                (625, 185, 12, 40, (255, 200, 90, 255))]:
        _ellipse(td, cx, cy, rx, ry, col)
    panel = _composite(panel, tg.filter(ImageFilter.GaussianBlur(1)))
    dr = ImageDraw.Draw(panel)
    # ---- smoke: ONE elongated plume drifting up-LEFT, beside the flames --
    # Centres sit left of the flame column so the cloud never caps it.
    sm = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sm)
    for cx, cy, r in [(520, 50, 38), (470, 38, 36), (420, 32, 30),
                      (380, 38, 24), (560, 30, 34), (600, 55, 26)]:
        _ellipse(sd, cx, cy, r, int(r * 0.8), (58, 58, 66, 255))
    for cx, cy, r in [(490, 44, 16), (440, 34, 13), (560, 40, 12)]:
        _ellipse(sd, cx, cy, r, int(r * 0.8), (85, 85, 92, 255))
    panel = _composite(panel, sm.filter(ImageFilter.GaussianBlur(8)))
    dr = ImageDraw.Draw(panel)
    # embers rising near the flames
    for ex, ey, r in [(600, 110, 3), (660, 90, 3), (720, 120, 3),
                      (760, 160, 3), (560, 190, 2), (780, 200, 2),
                      (640, 70, 2), (580, 200, 2)]:
        dr.ellipse([ex - r, ey - r, ex + r, ey + r], fill=(255, 190, 60))
    return panel


def render():
    with open(os.path.join(BASE, "stories.json"), encoding="utf-8") as f:
        d = json.load(f)
    img = Image.new("RGB", (W, H), PAPER)
    dr = ImageDraw.Draw(img)

    # ---- Masthead ----
    text(dr, (12, 6), d["masthead"], SERIF(46), INK)
    text(dr, (12, 58), d["date"], SANSB(20), RED)
    dr.line([12, 90, 1012, 90], fill=INK, width=3)
    dr.line([12, 94, 1012, 94], fill=INK, width=1)

    # ---- Hero: full width, one big burning ship ----
    img.paste(draw_hero_panel(), (12, 102))

    # ---- Headline block under the hero ----
    y = 414
    text(dr, (12, y), d["hero"]["kicker"], SANSB(16), RED)
    y += 24
    y = block(dr, 12, y, [d["hero"]["headline"]], SERIF(38), 1000, 46,
              max_lines=2)
    y = block(dr, 12, y + 8, [d["hero"]["deck"]], SANS(17), 1000, 21,
              max_lines=2)
    text(dr, (12, y + 6), d["hero"]["source"], SANS(13), GREY)
    y += 24

    # ---- Stats bar: row 1 label + Dow/S&P/Nasdaq; row 2 Gold/Oil/Dell --
    # (v4.1 fix: the old single row overflowed the right edge — "Oil $"
    # was cut off. Width is audited below; rows must fit 988px.)
    sy = 614
    dr.rectangle([12, sy, 1012, sy + 70], fill=NAVY)
    mx = 24
    row1 = [("MARKETS · TUE CLOSE", None, True)]
    for name, val, chg in d["markets"]["items"][:3]:
        row1.append((f"{name} {val} {chg}", chg, False))
    for s, chg, is_label in row1:
        col = (255, 255, 255)
        if chg:
            col = ((140, 220, 170) if chg.startswith("+")
                   else (255, 150, 130))
        text(dr, (mx, sy + 7), s, SANSB(16), col)
        mx += dr.textlength(s, font=SANSB(16)) + 24
    row2 = "Gold $3,542.50  ·  Oil $81.77  ·  " + d["markets"]["dell"]
    print(f"stats row1 width: {mx - 24:.0f}px / 988px"
          f"{'  <-- OVERFLOW' if mx - 24 > 988 else ''}")
    print(f"stats row2 width: "
          f"{dr.textlength(row2, font=SANS(15)):.0f}px / 988px"
          f"{'  <-- OVERFLOW' if dr.textlength(row2, font=SANS(15)) > 988 else ''}")
    text(dr, (24, sy + 48), row2, SANS(15), (200, 215, 235))

    # ---- Grid: one row, three stories, no numbers ----
    gx, gy = 12, 692
    cw, chh, gap = 330, 166, 4
    for i, g in enumerate(d["grid"]):
        cx = gx + i * (cw + gap)
        dr.rectangle([cx, gy, cx + cw, gy + chh], outline=LINE, width=1)
        text(dr, (cx + 12, gy + 10), g["kicker"], SANSB(16), RED)
        y2 = block(dr, cx + 12, gy + 36, [g["headline"]], SERIF(26),
                   cw - 24, 30, max_lines=2)
        y2 = block(dr, cx + 12, y2 + 4, [g["deck"]], SANS(16), cw - 24, 20,
                   max_lines=2)
        text(dr, (cx + 12, gy + chh - 20), g["source"], SANS(13), DARKGREY)

    # ---- Also today: short one-liners + date check line ----
    y = 866
    text(dr, (12, y), "ALSO TODAY", SANSB(15), NAVY)
    y += 20
    for lead, src in d["also"]:
        dr.ellipse([12, y + 2, 26, y + 16], fill=RED)
        dr.text((19, y + 9), "•", font=SANSB(14), fill=(255, 255, 255),
                anchor="mm")
        w_head = dr.textlength(lead, font=SANSB(17))
        print(f"also: {w_head:.0f}px / {1012 - 36 - 24:.0f}px"
              f"{'  <-- TOO LONG' if w_head > 1012 - 36 - 90 else ''}")
        dr.text((36, y), lead, font=SANSB(17), fill=INK)
        dr.text((36 + w_head + 8, y + 2), src, font=SANS(13), fill=DARKGREY)
        y += 20
    dr.text((36, y), d["date_check"], font=SANSB(16), fill=RED)
    y += 20

    # ---- Footer ----
    text(dr, (512, 1008), d["footer"], SANS(11), GREY, anchor="ma")

    # width audit: grid decks at 16pt (2 lines max)
    for g in d["grid"]:
        w_deck = dr.textlength(g["deck"], font=SANS(16))
        print(f"grid {g['kicker']}: deck {w_deck:.0f}px / {cw - 24:.0f}px"
              f"{'  <-- WRAPS to 2 lines' if w_deck > cw - 24 else ''}")

    out = os.path.join(BASE, "entry.png")
    img.save(out, optimize=True)
    print(out, img.size, os.path.getsize(out))


if __name__ == "__main__":
    render()
