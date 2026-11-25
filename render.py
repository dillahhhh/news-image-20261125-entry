#!/usr/bin/env python3
"""Render the 25 November 2026 world-news summary image (1024x1024). v3.

Build-time only: reads stories.json + land110m.json, draws with PIL,
writes entry.png. The graded program (main.py) only copies entry.png
to the output dir.

v3 fixes (vs v2, dev #557/2,889):
- MAP: land drawn from real Natural Earth 110m coastline (land110m.json,
  single-line, simplified 0.7 deg), not schematic blobs. Every pin centre
  verified against the real coastline (see /tmp/verify_pins.py and
  /tmp/test_candidates.py): sea pins sit in water (Gulf of Finland,
  Strait of Hormuz), land pins on land, coastal pins straddle the coast;
  every disc covers its true location (offsets <= 5px, disc r=8).
- THUMBNAIL: bottom half rebuilt for 300px legibility WITHOUT cutting
  content (still 11 stories, all verified facts kept): stats bar gets a
  full-width Dell row at 13pt; grid headlines 20pt, decks 14pt; MORE
  headlines bold 14pt with the source inline; timeline dates bold 13pt
  with 14pt events; DATE CHECK 13pt with trimmed wording (same facts).
- HERO: flames rebuilt as one asymmetric blaze (one dominant tongue,
  varied heights, no repeated triangles); smoke is ONE merged cloud in a
  single grey; debris squares removed (small shards + embers instead);
  cargo-ship fire enlarged.
- TIMELINE: first column is dates only (MON 23 NOV / TUE 24 NOV); the
  08:15 time moved into the event text. No invented times.
Facts kept from v2 (verified): Dell Q3 FY27 (revenue $54.94bn, adj. EPS
$9.45 vs $6.59, AI backlog $132.3bn, guidance $202bn); cricket Donald
85 off 32; "700,000+" tally (Meduza/Mediazona, NOT "killed and wounded");
NATO AWACS decided Mon 23 Nov; DATE CHECK "Sun 22 Nov" (correct).
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
DARKGREY = (70, 72, 78)
LINE = (216, 210, 196)
SEA = (220, 232, 240)
LAND = (232, 224, 204)
LAND_EDGE = (190, 178, 150)
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
    # Night sea, flat geometric style: dark navy sky, one asymmetric blaze,
    # sinking warship. Deliberately NOT a round disc: one dominant flame
    # tongue + varied heights, so the fire reads as a blaze, never a sunset.
    # No moon.
    draw.rectangle([x, y, x + w, y + h], fill=(16, 32, 64))
    # stars, kept away from the blast so the fire reads clearly
    for sx, sy in [(40, 26), (120, 52), (210, 20), (300, 44), (90, 90), (250, 84)]:
        draw.ellipse([x + sx - 2, y + sy - 2, x + sx + 2, y + sy + 2], fill=(240, 235, 210))
    # blast: ONE asymmetric blaze. A single dominant central tongue leaning
    # right, a shorter left tongue, varied peak heights and widths, wide
    # uneven base glow underneath. No repeated triangle row.
    draw.ellipse([x + 372, y + 146, x + 560, y + 198], fill=(240, 120, 40))
    # outer flame mass (deep orange): dominant tongue peaks y~56, others
    # 84-150, base at y192, left edge low, right edge mid.
    draw.polygon([(x + 366, y + 192), (x + 376, y + 152), (x + 390, y + 116),
                  (x + 402, y + 158), (x + 414, y + 96), (x + 428, y + 140),
                  (x + 442, y + 56), (x + 458, y + 116), (x + 472, y + 74),
                  (x + 486, y + 128), (x + 502, y + 88), (x + 516, y + 138),
                  (x + 530, y + 104), (x + 544, y + 148), (x + 556, y + 192)],
                 fill=(205, 70, 12))
    # mid flame (bright orange): fewer, fatter tongues, offset peaks.
    draw.polygon([(x + 390, y + 192), (x + 402, y + 150), (x + 416, y + 170),
                  (x + 430, y + 108), (x + 446, y + 148), (x + 460, y + 86),
                  (x + 476, y + 130), (x + 490, y + 100), (x + 506, y + 142),
                  (x + 520, y + 124), (x + 534, y + 192)], fill=(255, 140, 40))
    # rounded flame lobes breaking any triangle repetition: one big lobe
    # left-centre, one smaller right, one low centre.
    draw.ellipse([x + 424, y + 98, x + 462, y + 146], fill=(255, 170, 70))
    draw.ellipse([x + 494, y + 80, x + 520, y + 118], fill=(255, 170, 70))
    draw.ellipse([x + 452, y + 140, x + 488, y + 176], fill=(255, 190, 90))
    # bright core: low, wide, uneven top edge.
    draw.polygon([(x + 412, y + 192), (x + 424, y + 160), (x + 440, y + 176),
                  (x + 452, y + 128), (x + 466, y + 162), (x + 480, y + 134),
                  (x + 494, y + 168), (x + 510, y + 154), (x + 522, y + 192)],
                 fill=(255, 205, 90))
    # side tongues leaning outward, asymmetric (left tall/narrow, right
    # short/wide).
    draw.polygon([(x + 350, y + 192), (x + 360, y + 148), (x + 372, y + 170),
                  (x + 386, y + 192)], fill=(230, 100, 20))
    draw.polygon([(x + 552, y + 192), (x + 564, y + 162), (x + 576, y + 180),
                  (x + 584, y + 192)], fill=(230, 100, 20))
    # smoke: ONE merged cloud, single dark grey, puffs overlapping by more
    # than half so they read as one continuous plume drifting left, with
    # two small lighter puffs attached (still overlapping the main mass).
    smoke = (44, 44, 52)
    for sx, sy, r in [(506, 56, 22), (482, 38, 26), (452, 22, 22),
                      (422, 12, 15), (530, 74, 18), (554, 94, 14), (496, 30, 20)]:
        draw.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r], fill=smoke)
    for sx, sy, r in [(470, 30, 10), (520, 60, 8)]:
        draw.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r], fill=(70, 70, 78))
    # debris: no floating black squares. Three small dark shards tight
    # against the blast + embers.
    for pts in [[(340, 108), (348, 100), (350, 110)],
                [(566, 78), (574, 72), (574, 82)],
                [(596, 138), (604, 132), (604, 142)]]:
        draw.polygon([(x + px, y + py) for px, py in pts], fill=(12, 12, 16))
    # embers
    for ex, ey, r in [(360, 120, 3), (400, 70, 3), (520, 60, 3), (560, 110, 3),
                      (340, 170, 2), (590, 170, 2), (470, 45, 2), (440, 90, 2),
                      (500, 150, 2)]:
        draw.ellipse([x + ex - r, y + ey - r, x + ex + r, y + ey + r], fill=(255, 190, 60))
    # sea
    draw.rectangle([x, y + 190, x + w, y + h], fill=(24, 58, 96))
    for wy in (215, 240, 268):
        for wx in range(20, w - 20, 70):
            draw.line([x + wx, y + wy, x + wx + 34, y + wy], fill=(120, 170, 210), width=3)
    # fire reflection on the water under the blast (wide, uneven streaks)
    for rx, ry, rw in [(380, 200, 70), (400, 200, 120), (420, 214, 90),
                       (440, 228, 60), (410, 244, 80), (450, 258, 50),
                       (470, 206, 100), (400, 270, 90), (460, 244, 70)]:
        draw.line([x + rx, y + ry, x + rx + rw, y + ry], fill=(255, 140, 50), width=4)
    # cargo ship silhouette (left) with a BIGGER deck fire: glow + three
    # tongues, ~50px wide (was ~26px).
    draw.ellipse([x + 98, y + 146, x + 156, y + 180], fill=(240, 120, 40))
    draw.rectangle([x + 60, y + 176, x + 240, y + 216], fill=(10, 18, 34))
    draw.rectangle([x + 96, y + 150, x + 150, y + 176], fill=(10, 18, 34))
    draw.rectangle([x + 196, y + 158, x + 210, y + 176], fill=(10, 18, 34))
    for px in (80, 120, 160, 200):
        draw.rectangle([x + px, y + 186, x + px + 14, y + 198], fill=(255, 190, 80))
    draw.polygon([(x + 104, y + 176), (x + 112, y + 150), (x + 120, y + 166),
                  (x + 128, y + 142), (x + 136, y + 164), (x + 144, y + 152),
                  (x + 152, y + 176)], fill=(255, 150, 40))
    draw.polygon([(x + 118, y + 176), (x + 124, y + 158), (x + 132, y + 168),
                  (x + 138, y + 176)], fill=(255, 205, 90))
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


def load_land():
    with open(os.path.join(BASE, "land110m.json"), encoding="utf-8") as f:
        return json.load(f)["rings"]


def draw_map(draw, x, y, w, h, pins):
    # Real Natural Earth 110m coastline, equirectangular (lon -180..180 -> x,
    # lat 85..-60 -> y). Drawn on a separate layer so coastlines outside
    # the map rect are clipped by the paste.
    def px(lon):
        return (lon + 180) / 360.0 * w
    def py(lat):
        return (85 - lat) / 145.0 * h
    layer = Image.new("RGB", (w, h), SEA)
    ld = ImageDraw.Draw(layer)
    for ring in load_land():
        pts = [(px(lon), py(lat)) for lon, lat in ring]
        if len(pts) < 3:
            continue
        ld.polygon(pts, fill=LAND)
        # 2px edge in land colour fattens thin islands (Java) by ~1px so
        # they read at this scale; coastlines shift ~1px seaward, a fair
        # generalisation at 1px/degree.
        ld.line(pts + [pts[0]], fill=LAND, width=2, joint="curve")
    draw._image.paste(layer, (x, y))
    # graticule
    for lon in range(-150, 181, 30):
        draw.line([x + px(lon), y, x + px(lon), y + h], fill=(200, 214, 226), width=1)
    for lat in range(-60, 86, 30):
        draw.line([x, y + py(lat), x + w, y + py(lat)], fill=(200, 214, 226), width=1)
    # pins: centres verified against the REAL coastline (true spot on land
    # for land stories, in water for sea stories, straddling for coastal).
    # Every disc (r=8) still covers its true location (offsets <= 5px).
    # Clusters 1/9 and 6/7 are 10-12px apart: discs touch, numbers stay
    # readable; that is the honest minimum at 1px/degree.
    offsets = {1: (0, 0), 3: (4, 3), 4: (0, 0), 5: (-4, 0), 6: (1, -4),
               7: (-1, 4), 9: (-2, -5), 10: (-4, 0), 11: (2, 1)}
    for n, name, lat, lon in pins:
        dx, dy = offsets.get(n, (0, 0))
        cx, cy = x + px(lon) + dx, y + py(lat) + dy
        r = 8
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED, outline=(255, 255, 255), width=2)
        draw.text((cx, cy), str(n), font=SANSB(10), fill=(255, 255, 255), anchor="mm")


def render():
    with open(os.path.join(BASE, "stories.json"), encoding="utf-8") as f:
        d = json.load(f)
    img = Image.new("RGB", (W, H), PAPER)
    dr = ImageDraw.Draw(img)

    # ---- Masthead ----
    text(dr, (12, 6), d["masthead"], SERIF(44), INK)
    text(dr, (12, 58), d["date"], SANSB(20), RED)
    dr.line([12, 90, 1012, 90], fill=INK, width=3)
    dr.line([12, 94, 1012, 94], fill=INK, width=1)

    # ---- Hero (wider: ~65% of the page) ----
    hx, hy, hw, hh = 12, 102, 650, 292
    hero_img = Image.new("RGB", (608, 292))
    draw_hero_illustration(ImageDraw.Draw(hero_img), 0, 0, 608, 292)
    img.paste(hero_img.resize((hw, hh), Image.LANCZOS), (hx, hy))
    tx = 678
    text(dr, (tx, 106), d["hero"]["kicker"], SANSB(15), RED)
    dr.line([tx, 130, 1012, 130], fill=LINE, width=1)
    y = block(dr, tx, 140, [d["hero"]["headline"]], SERIF(28), 334, 34, max_lines=4)
    y = block(dr, tx, y + 6, [d["hero"]["deck"]], SANS(14), 334, 17, max_lines=6)
    text(dr, (tx, 382), d["hero"]["source"], SANS(11), GREY)

    # ---- Stats bar: three rows so Dell gets a full-width row at 13pt ----
    sy = 400
    dr.rectangle([12, sy, 1012, sy + 76], fill=NAVY)
    text(dr, (24, sy + 7), d["markets"]["label"], SANSB(13), (255, 255, 255))
    mx = 24
    for name, val, chg in d["markets"]["items"]:
        s = f"{name} {val}" + (f" {chg}" if chg else "")
        col = (140, 220, 170) if chg.startswith("+") else ((255, 150, 130) if chg.startswith("-") else (255, 255, 255))
        text(dr, (mx, sy + 29), s, SANSB(14), col)
        mx += dr.textlength(s, font=SANSB(14)) + 26
    text(dr, (24, sy + 53), d["markets"]["dell"], SANS(13), (200, 215, 235))

    # ---- Grid: taller cells (132), bigger type ----
    gx, gy = 12, 482
    cw, chh, gap = 330, 132, 4
    for i, g in enumerate(d["grid"]):
        cx = gx + (i % 3) * (cw + gap)
        cy = gy + (i // 3) * (chh + gap)
        dr.rectangle([cx, cy, cx + cw, cy + chh], outline=LINE, width=1)
        # pin badge
        dr.ellipse([cx + 10, cy + 10, cx + 32, cy + 32], fill=RED)
        dr.text((cx + 21, cy + 21), str(g["n"]), font=SANSB(12), fill=(255, 255, 255), anchor="mm")
        text(dr, (cx + 40, cy + 12), g["kicker"], SANSB(13), RED)
        y2 = block(dr, cx + 10, cy + 38, [g["headline"]], SERIF(20), cw - 20, 24, max_lines=2)
        block(dr, cx + 10, y2 + 2, [g["deck"]], SANS(14), cw - 20, 17, max_lines=1)
        text(dr, (cx + 10, cy + chh - 18), g["source"], SANS(11), DARKGREY)

    # 6th cell: DATE CHECK (13pt, trimmed wording, same facts)
    dcx, dcy = gx + 2 * (cw + gap), gy + 1 * (chh + gap)
    dr.rectangle([dcx, dcy, dcx + cw, dcy + chh], outline=RED, width=2, fill=(255, 248, 240))
    text(dr, (dcx + 10, dcy + 8), "DATE CHECK", SANSB(13), RED)
    block(dr, dcx + 10, dcy + 28, [d["date_check"]], SANS(13), cw - 20, 15, max_lines=6)

    # ---- Bottom: map (left) ----
    bx, by = 12, 756
    bw, bh = 360, 220
    text(dr, (bx, by), "WHERE IT HAPPENED", SANSB(15), NAVY)
    draw_map(dr, bx, by + 20, bw, bh, d["pins"])

    # ---- Bottom right: more / timeline ----
    rx = 392
    y = by
    text(dr, (rx, y), "MORE OF THE DAY", SANSB(15), NAVY)
    y += 22
    # one strong line per item: bold headline + source inline (grey, 11pt)
    for n, lead, rest, src in d["more"]:
        dr.ellipse([rx, y + 1, rx + 15, y + 16], fill=RED)
        dr.text((rx + 8, y + 8), str(n), font=SANSB(10), fill=(255, 255, 255), anchor="mm")
        ln = f"{lead} — {rest}"
        w_head = dr.textlength(ln, font=SANSB(14))
        print(f"more {n}: headline {w_head:.0f}px / {1012 - rx - 24:.0f}px")
        dr.text((rx + 24, y), ln, font=SANSB(14), fill=INK)
        dr.text((rx + 24 + w_head + 6, y + 2), src, font=SANS(11), fill=DARKGREY)
        y += 22
    y += 6
    text(dr, (rx, y), "TIMELINE — MON INTO WED, UTC", SANSB(14), NAVY)
    y += 20
    for t, ev in d["timeline"]:
        text(dr, (rx, y), t, SANSB(13), RED)
        w_ev = dr.textlength(ev, font=SANS(14))
        print(f"timeline {t}: event {w_ev:.0f}px / {1012 - rx - 98:.0f}px")
        y = block(dr, rx + 98, y, [ev], SANS(14), 1012 - rx - 98, 15, max_lines=1)
        y += 6

    # ---- Footer ----
    text(dr, (512, 1008), d["footer"], SANS(10), GREY, anchor="ma")

    # width audit: grid decks at 14pt (1 line max — a wrap would cut words)
    for g in d["grid"]:
        w_deck = dr.textlength(g["deck"], font=SANS(14))
        print(f"grid {g['n']}: deck {w_deck:.0f}px / {cw - 20:.0f}px"
              f"{'  <-- WRAPS, trim!' if w_deck > cw - 20 else ''}")

    out = os.path.join(BASE, "entry.png")
    img.save(out, optimize=True)
    print(out, img.size, os.path.getsize(out))


if __name__ == "__main__":
    render()
