"""Suggest --cool / --warm colours for brand-loop from a logo image (no extra Python packages needed).

python3 palette.py logo.png
Prints the logo's main colours and a suggested pair of blob families: the dominant hue family (5 shades, dark ->
light) and a contrasting accent family (3 shades). Pass them to loop.sh, or pick your own brand hex values.
"""
import colorsys, subprocess, sys, random

path = sys.argv[1]
raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', path, '-vf', 'scale=96:96:flags=area,format=rgba', '-f', 'rawvideo', '-'],
                     capture_output=True, check=True).stdout
px = [tuple(raw[i:i + 4]) for i in range(0, len(raw), 4)]
pts = []
for r, g, b, a in px:
    if a < 128: continue
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    if s < 0.35 or l > 0.92 or l < 0.08: continue          # skip paper, greys and near-black
    pts.append((r, g, b))
if not pts: sys.exit('no saturated colours found in the logo; pass --cool/--warm yourself')
random.seed(1)
cent = random.sample(pts, min(6, len(pts)))
for _ in range(20):                                          # k-means
    groups = [[] for _ in cent]
    for p in pts:
        k = min(range(len(cent)), key=lambda j: sum((p[i] - cent[j][i]) ** 2 for i in range(3))); groups[k].append(p)
    cent = [tuple(sum(c[i] for c in gr) / len(gr) for i in range(3)) if gr else cent[j] for j, gr in enumerate(groups)]
cols = sorted(((len(gr), c) for gr, c in zip(groups, cent) if len(gr) >= 0.07 * len(pts)), reverse=True)   # ignore edge blends
hexs = lambda c: '#%02x%02x%02x' % tuple(int(v) for v in c)
hue = lambda c: colorsys.rgb_to_hls(*(v / 255 for v in c))[0] * 360
light = lambda c: 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]   # luma: dark -> light
print('main colours (share, hex, hue):')
for n, c in cols: print(f'  {n / len(pts):5.1%}  {hexs(c)}  {hue(c):5.0f}')
h0 = hue(cols[0][1])
near = lambda c: min(abs(hue(c) - h0), 360 - abs(hue(c) - h0)) < 50
fam1 = sorted([c for _, c in cols if near(c)], key=light)
fam2 = sorted([c for _, c in cols if not near(c)], key=light)
def shades(fam, n):
    if len(fam) >= 2: return [hexs(c) for c in fam][:n] if len(fam) >= n else [hexs(c) for c in fam]
    h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in fam[0]))
    return [hexs([v * 255 for v in colorsys.hls_to_rgb(h, ll, s)]) for ll in [max(0.2, l - 0.18), l, min(0.8, l + 0.15)]]
cool = shades(fam1, 5)
warm = shades(fam2, 3) if fam2 else shades([tuple(255 * v for v in colorsys.hls_to_rgb(((h0 + 180) % 360) / 360, 0.5, 0.95))], 3)
print('\nsuggested:  --cool "%s" --warm "%s"' % (','.join(cool), ','.join(warm)))
