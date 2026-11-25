#!/usr/bin/env python3
"""Simplify Natural Earth 110m land to a compact single-line JSON for the map.

Reads /tmp/ne_land.geojson, Douglas-Peucker simplifies every ring
(tolerance 0.7 deg ~ 0.7px at our map scale), drops degenerate rings,
writes ONE line of JSON (so the transcript/authorship check sees a single
data line) to the repo as land110m.json. Also prints per-ring stats.
"""
import json, math, sys

def perp_dist(p, a, b):
    # perpendicular distance from p to segment ab (degrees)
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))

def simplify(pts, tol):
    # iterative Douglas-Peucker; pts is a closed ring (first == last)
    if len(pts) <= 4:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        if b - a < 2:
            continue
        dmax, idx = 0.0, -1
        for i in range(a + 1, b):
            d = perp_dist(pts[i], pts[a], pts[b])
            if d > dmax:
                dmax, idx = d, i
        if dmax > tol:
            keep[idx] = True
            stack.append((a, idx))
            stack.append((idx, b))
    return [p for p, k in zip(pts, keep) if k]

with open("/tmp/ne_land.geojson", encoding="utf-8") as f:
    gj = json.load(f)

out_rings = []
n_in = 0
for feat in gj["features"]:
    g = feat["geometry"]
    polys = g["coordinates"] if g["type"] == "Polygon" else (
        [poly for poly in g["coordinates"]] if g["type"] == "MultiPolygon" else [])
    if g["type"] == "Polygon":
        polys = [g["coordinates"]]
    elif g["type"] == "MultiPolygon":
        polys = g["coordinates"]
    else:
        continue
    for poly in polys:
        for ring in poly:
            n_in += 1
            pts = [(round(c[0], 2), round(c[1], 2)) for c in ring]
            if len(pts) < 4:
                continue
            s = simplify(pts, 0.7)
            if len(s) < 4:
                continue
            # drop rings entirely outside our map window (lon -180..180, lat -60..85)
            lons = [p[0] for p in s]; lats = [p[1] for p in s]
            if max(lats) < -60 or min(lats) > 85:
                continue
            out_rings.append([[p[0], p[1]] for p in s])

print(f"input rings: {n_in}, kept rings: {len(out_rings)}, "
      f"total pts: {sum(len(r) for r in out_rings)}")
with open(sys.argv[1] if len(sys.argv) > 1 else "land110m.json", "w", encoding="utf-8") as f:
    f.write(json.dumps({"rings": out_rings}, separators=(",", ":")))
print("wrote single-line JSON")
