#!/usr/bin/env python3
"""Regenerate land110m.json from the Natural Earth 110m land source.

The source (ne_110m_land.geojson, Natural Earth 110m land, public
domain) ships in this repo so regeneration is offline and repeatable.
The output is the compact {"rings": [[[lon, lat], ...], ...]} format
render.py's load_land() reads: one ring per polygon ring, coordinates
rounded to 2 decimals, simplified with Douglas-Peucker (tolerance
0.5 degrees — the 110m data is coarse, so this keeps coastlines
recognisable while shrinking the file to ~16 KB).

Run:  python3 gen_land.py
Writes: land110m.json (overwrites in place)
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "ne_110m_land.geojson")
OUT = os.path.join(HERE, "land110m.json")
TOL = 0.5  # degrees, Douglas-Peucker


def _perp_dist(px, py, ax, ay, bx, by):
    """Perpendicular distance from P to segment AB (degrees)."""
    dx, dy = bx - ax, by - ay
    seg2 = dx * dx + dy * dy
    if seg2 == 0.0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / seg2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def simplify(points, tol):
    """Iterative Douglas-Peucker on a closed ring (last == first)."""
    if len(points) <= 4:
        return points
    closed = points[0] == points[-1]
    pts = points[:-1] if closed else list(points)
    n = len(pts)
    keep = [False] * n
    keep[0] = keep[n - 1] = True
    stack = [(0, n - 1)]
    while stack:
        a, b = stack.pop()
        if b - a < 2:
            continue
        ax, ay = pts[a]
        bx, by = pts[b]
        dmax, idx = 0.0, -1
        for i in range(a + 1, b):
            d = _perp_dist(pts[i][0], pts[i][1], ax, ay, bx, by)
            if d > dmax:
                dmax, idx = d, i
        if dmax > tol:
            keep[idx] = True
            stack.append((a, idx))
            stack.append((idx, b))
    out = [p for p, k in zip(pts, keep) if k]
    if closed:
        out.append(out[0])
    return out


def main():
    with open(SRC, encoding="utf-8") as f:
        fc = json.load(f)
    rings = []
    for feat in fc["features"]:
        geom = feat["geometry"]
        polys = ([geom["coordinates"]] if geom["type"] == "Polygon"
                 else geom["coordinates"])
        for poly in polys:
            for ring in poly:
                pts = [(round(lon, 2), round(lat, 2)) for lon, lat in ring]
                # de-duplicate consecutive identical points (rounding)
                dedup = [pts[0]]
                for p in pts[1:]:
                    if p != dedup[-1]:
                        dedup.append(p)
                simp = simplify(dedup, TOL)
                if len(simp) >= 4:
                    rings.append([[lon, lat] for lon, lat in simp])
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"rings": rings}, f, separators=(",", ":"))
    npts = sum(len(r) for r in rings)
    print(f"{OUT}: {len(rings)} rings, {npts} points, "
          f"{os.path.getsize(OUT)} bytes")


if __name__ == "__main__":
    main()
