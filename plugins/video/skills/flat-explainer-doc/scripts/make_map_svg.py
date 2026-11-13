#!/usr/bin/env python3
"""Flat-style explainer map SVG (2400x1350) from Natural Earth + real elevation.

  make_map_svg.py --view LON LAT WIDTH_DEG --out scenes/map_x.svg
                  [--style ochre|green|ice] [--borders] [--rivers 6] [--no-terrain]
                  [--desert LAT]   land south of LAT gets the desert tone (stylised climate zone)

Look (matching the reference explainer maps): teal sea with a faint grid and "^" wave marks, land with a dark
drop-shadow and a thick orange coastline, elevation-tinted zones, clusters of 2-tone mountain glyphs where the
terrain is high, thin rivers.
The root gets data-view="lon,lat,width" so explainer.map_card(pins=[dict(lon=, lat=, label=)]) can place pins.
Projection: plate carree scaled by cos(centre latitude) (regional maps).
Data: Natural Earth (public domain) and Mapzen/AWS terrarium elevation tiles, cached in khmer-history-doc/geo_cache.
"""
import argparse
import io
import math
import os
import random
import sys
import urllib.request
import zipfile

import numpy as np
import shapefile

KH = os.path.expanduser("~/.claude/skills/khmer-history-doc")
CACHE = os.path.join(KH, "geo_cache")
STYLES = {
    "ochre": dict(sea="#4aa58c", sea_grid="#5bb39a", wave="#8fd8b8", shadow="#2d6e66", coast="#f2961d",
                  land=["#a39a2c", "#8f8a2a", "#7d7a28"], desert="#f5a31a", desert_d="#e88f16",
                  mtn="#7a5a3a", mtn_d="#5e4430", lake="#4aa58c", river="#3f8f6e", border="#ffe7a0"),
    "green": dict(sea="#3f8fb0", sea_grid="#4f9dbd", wave="#9ad6e8", shadow="#285f78", coast="#f2b53d",
                  land=["#7fae4a", "#6c9a3f", "#5b8636"], desert="#d9b04a", desert_d="#c79a3a",
                  mtn="#5d6a3a", mtn_d="#45502c", lake="#3f8fb0", river="#2f7f95", border="#fff4c0"),
    "ice": dict(sea="#3d72c8", sea_grid="#4d82d4", wave="#a9ccff", shadow="#284f96", coast="#ffffff",
                land=["#b8cf5a", "#a3bd4a", "#8fa83f"], desert="#e3d27a", desert_d="#d1bd62",
                mtn="#7d8a5a", mtn_d="#5e6a44", lake="#2d5fb5", river="#2d5fb5", border="#ffffff"),
}
FILES = {"land": "ne_50m_land", "lakes": "ne_50m_lakes", "rivers": "ne_10m_rivers_lake_centerlines",
         "countries": "ne_50m_admin_0_countries"}


def shp(name):
    d = os.path.join(CACHE, name)
    if not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
        url = "https://naciscdn.org/naturalearth/%s/%s/%s.zip" % (
            name.split("_")[1], "cultural" if "admin" in name else "physical", name)
        zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(url, timeout=120).read())).extractall(d)
    return shapefile.Reader(os.path.join(d, name + ".shp"))


def elevation(bbox, width_deg):
    """-> fn(lon, lat) -> metres, from terrarium tiles (reuses khmer-history-doc/scripts/fetch_geo.py)."""
    sys.path.insert(0, os.path.join(KH, "scripts"))
    import fetch_geo as G
    z = max(3, min(8, int(round(math.log2(360 / width_deg * 4)))))
    lon0, lat0, lon1, lat1 = bbox
    lat0, lat1 = max(-80, lat0), min(80, lat1)
    d = np.load(G.dem("mapsvg", round(lon0, 2), round(lat0, 2), round(lon1, 2), round(lat1, 2), z))
    dem, x0, y0 = d["dem"], int(d["x0"]), int(d["y0"])

    def f(lon, lat):
        x, y = G.tile_xy(lon, max(-80, min(80, lat)), z)
        px, py = int((x - x0) * 256), int((y - y0) * 256)
        if 0 <= py < dem.shape[0] and 0 <= px < dem.shape[1]:
            return float(dem[py, px])
        return 0.0
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--view", nargs=3, type=float, required=True, metavar=("LON", "LAT", "WIDTH"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--style", default="ochre", choices=STYLES)
    ap.add_argument("--borders", action="store_true")
    ap.add_argument("--rivers", type=int, default=6, help="max river scalerank to draw (0-10, lower = fewer)")
    ap.add_argument("--no-terrain", action="store_true")
    ap.add_argument("--desert", type=float, default=None, help="latitude: land south of it is desert-toned")
    a = ap.parse_args()
    S = STYLES[a.style]
    lc, la, wd = a.view
    k = 2400 / (wd * math.cos(math.radians(la)))
    kx = k * math.cos(math.radians(la))

    def P(lon, lat):
        return 1200 + (lon - lc) * kx, 675 - (lat - la) * k

    def U(px, py):
        return lc + (px - 1200) / kx, la - (py - 675) / k

    hw, hh = wd / 2 * 1.15, 1350 / k / 2 * 1.15
    bbox = (lc - hw, la - hh, lc + hw, la + hh)

    def hit(b):
        return not (b[2] < bbox[0] or b[0] > bbox[2] or b[3] < bbox[1] or b[1] > bbox[3])

    def path(points, parts, close=True, minstep=2.5):
        out = []
        idx = list(parts) + [len(points)]
        for i in range(len(parts)):
            ring = points[idx[i]:idx[i + 1]]
            pts, last = [], None
            for lon, lat in ring:
                x, y = P(lon, lat)
                if last is None or abs(x - last[0]) + abs(y - last[1]) >= minstep:
                    pts.append((x, y))
                    last = (x, y)
            if len(pts) < (3 if close else 2):
                continue
            out.append("M" + " L".join("%.1f %.1f" % p for p in pts) + (" Z" if close else ""))
        return " ".join(out)

    land = " ".join(path(s.points, s.parts) for s in shp(FILES["land"]).shapes() if hit(s.bbox))
    lakes = " ".join(path(s.points, s.parts) for s in shp(FILES["lakes"]).shapes() if hit(s.bbox))
    rv = shp(FILES["rivers"])
    fields = [f[0] for f in rv.fields[1:]]
    ri = fields.index("scalerank") if "scalerank" in fields else None
    rivers = " ".join(path(sr.shape.points, sr.shape.parts, close=False, minstep=4) for sr in rv.iterShapeRecords()
                      if hit(sr.shape.bbox) and (ri is None or sr.record[ri] <= a.rivers))
    borders = ""
    if a.borders:
        borders = " ".join(path(s.points, s.parts) for s in shp(FILES["countries"]).shapes() if hit(s.bbox))

    rnd = random.Random(3)
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2400 1350" data-view="%g,%g,%g">' % (lc, la, wd),
         '<defs><clipPath id="landclip"><path d="%s" fill-rule="evenodd"/></clipPath></defs>' % land,
         '<rect width="2400" height="1350" fill="%s"/>' % S["sea"]]
    # sea grid + wave marks
    grid = " ".join("M%d 0 V1350" % x for x in range(0, 2401, 160)) + " " + \
        " ".join("M0 %d H2400" % y for y in range(0, 1351, 160))
    o.append('<path d="%s" stroke="%s" stroke-width="3" fill="none"/>' % (grid, S["sea_grid"]))
    for _ in range(26):
        x, y = rnd.uniform(60, 2340), rnd.uniform(60, 1290)
        o.append('<path d="M%.0f %.0f l16 -14 l16 14" fill="none" stroke="%s" stroke-width="5" '
                 'stroke-linecap="round" stroke-linejoin="round" opacity="0.8"/>' % (x, y, S["wave"]))
    # land: drop shadow, body, coastline
    o.append('<path d="%s" transform="translate(10 16)" fill="%s" fill-rule="evenodd"/>' % (land, S["shadow"]))
    o.append('<path d="%s" fill="%s" fill-rule="evenodd"/>' % (land, S["land"][0]))
    zones, mtns = [], []
    if not a.no_terrain:
        try:
            E = elevation(bbox, wd)
            for gy in range(0, 1351, 34):
                for gx in range(0, 2401, 34):
                    jx, jy = gx + rnd.uniform(-12, 12), gy + rnd.uniform(-12, 12)
                    e = E(*U(jx, jy))
                    if e > 450:
                        zones.append('<circle cx="%.0f" cy="%.0f" r="%d" fill="%s"/>'
                                     % (jx, jy, 30, S["land"][1 if e < 1300 else 2]))
            for gy in range(20, 1351, 46):
                for gx in range(20, 2401, 52):
                    jx, jy = gx + rnd.uniform(-18, 18), gy + rnd.uniform(-14, 14)
                    e = E(*U(jx, jy))
                    if e > 1100 and rnd.random() < min(0.9, (e - 900) / 1800):
                        s = 22 + min(26, (e - 1100) / 90)
                        mtns.append((jy, '<path d="M%.0f %.0f q%.0f %.0f %.0f 0 z" fill="%s"/>'
                                     '<path d="M%.0f %.0f q%.0f %.0f %.0f 0 h%.0f z" fill="%s"/>'
                                     % (jx - s, jy, s, -2.2 * s, 2 * s, S["mtn"],
                                        jx, jy - 1.1 * s, s * 0.5, s * 0.2, s, -s, S["mtn_d"])))
        except Exception as ex:   # offline: flat land is still a valid map
            print("[map] terrain skipped:", ex)
    o.append('<g clip-path="url(#landclip)">')
    o.append('<g opacity="0.55">%s</g>' % "".join(zones))
    if a.desert is not None:
        _, dy = P(lc, a.desert)
        wav = "M0 %.0f " % dy + " ".join("Q%.0f %.0f %.0f %.0f" % (x + 60, dy + (40 if (x // 120) % 2 else -40),
                                                                      x + 120, dy) for x in range(0, 2400, 120))
        o.append('<path d="%s V1350 H0 Z" fill="%s"/>' % (wav, S["desert"]))
        for _ in range(40):
            x, y = rnd.uniform(0, 2400), rnd.uniform(dy + 60, 1350)
            o.append('<ellipse cx="%.0f" cy="%.0f" rx="%d" ry="%d" fill="%s"/>'
                     % (x, y, rnd.randint(60, 160), rnd.randint(25, 50), S["desert_d"]))
    o.append('<path d="%s" fill="none" stroke="%s" stroke-width="4" opacity="0.85"/>' % (rivers, S["river"]))
    if borders:
        o.append('<path d="%s" fill="none" stroke="%s" stroke-width="3" stroke-dasharray="10 9" opacity="0.6"/>'
                 % (borders, S["border"]))
    o.append("".join(m for _, m in sorted(mtns)))
    o.append("</g>")
    o.append('<path d="%s" fill="%s" stroke="%s" stroke-width="7"/>' % (lakes, S["lake"], S["coast"]))
    o.append('<path d="%s" fill="none" stroke="%s" stroke-width="10" stroke-linejoin="round" fill-rule="evenodd"/>'
             % (land, S["coast"]))
    o.append('<desc>px = 1200 + (lon - %g) * %.4f; py = 675 - (lat - %g) * %.4f</desc>' % (lc, kx, la, k))
    o.append("</svg>")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, "w").write("\n".join(o))
    print("[map] %s  zones %d  mountains %d" % (a.out, len(zones), len(mtns)))


if __name__ == "__main__":
    main()
