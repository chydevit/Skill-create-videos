"""Flat-explainer graphic grammar (screen space 1920x1080 unless noted).

Overlays (functions over(ctx, t, d); attach with with_over(scene, ...)):
  tag(text, x, y, color, at, style="banner"|"box", size, space="screen"|"set", depth)  pill / banner label
  title_tag(text, color, at)                      banner at top-centre ("Timeline", "Human Era Timeline")
  caption(text, x, y, size, color, at)            plain bold text that pops in
  portal(inner, cx, cy, r, at, cam, ring, blob)   circular "memory bubble" with an ink-blob rim showing another scene

Whole-frame scenes:
  timeline(title, start, end, events, ticks, segments, ...)   animated horizontal timeline (CE or Human Era)
  chapter_title(small, big, bar, labels, under)               "From Bread to Living on / DEAD ANCESTORS" card
  map_card(svg, title, pins, boxes, ...)                      framed flat map with banner pins
  panels(scenes, cams)                                         2-4 vertical panels sliding in
  big_text(lines, bg)                                          flat colour card with text

Human Era: he(year_ce) -> 10000 + year (no year 0 in CE; HE 10,001 = 1 CE, HE 10,000 = 1 BCE).
"""
import math

import cairocffi as cairo

from core import H, W, clamp, draw_text, ease, has_khmer, rrect, src, text_surface

EN = "Avenir Next"
EN_COND = "DIN Condensed"
KM = "Noto Sans Khmer"
KM_DISPLAY = "Koulen"
INK = "#1d1633"
COL = dict(magenta="#c8326f", teal="#13606b", green="#3f9a4a", lime="#9bd447", orange="#e2682a", violet="#5b3fa0",
           navy="#1a2a5a", cream="#fbf3dc", gold="#f2c14e")


def he(year):
    """Human Era year from a CE year (negative = BCE, astronomical-free: -1 means 1 BCE)."""
    return 10000 + year + (1 if year < 0 else 0)


def fmt_year(y):
    return "{:,}".format(y) if abs(y) >= 10000 else str(y)


def _font(text, latin=EN):
    return KM if has_khmer(text) else latin


def _darker(hx, k):
    r, g, b = _rgb(hx)
    return "#%02x%02x%02x" % (int(r * k * 255), int(g * k * 255), int(b * k * 255))


def back_out(p):
    p = clamp(p)
    c = 1.70158
    return 1 + (c + 1) * (p - 1) ** 3 + c * (p - 1) ** 2


def pop(t, at, dur=0.45):
    """(scale, alpha) for a pop-in at time `at`."""
    q = (t - at) / dur
    if q <= 0:
        return 0.0, 0.0
    return (back_out(q) if q < 1 else 1.0), clamp(q * 3)


def with_over(scene, *fns):
    old = scene.get("over")

    def over(ctx, t, d):
        if old:
            old(ctx, t, d)
        for f in fns:
            f(ctx, t, d)
    scene["over"] = over
    return scene


# ------------------------------------------------------------------ labels
def draw_label(ctx, text, x, y, color, size=30, style="banner", s=1.0, a=1.0, fg="#ffffff", anchor="b"):
    """Banner: pointed ends (hexagon pill). Box: rectangle with a pointer below. Anchored at the pointer tip
    (style box) or the bottom-centre (banner)."""
    if s <= 0.001 or a <= 0.001:
        return 0, 0
    ts = text_surface(text, size * (1.12 if has_khmer(text) else 1), fg, _font(text), "Bold")
    tw, th = ts.get_width(), ts.get_height()
    padx, pady = size * 0.75, size * 0.18
    w, h = tw + 2 * padx, th + 2 * pady
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)

    def shape(ox, oy):
        if style == "box":
            ptr = size * 0.32
            rrect(ctx, ox, oy, w, h, 5)
            ctx.move_to(ox + w / 2 - ptr, oy + h - 0.5)
            ctx.line_to(ox + w / 2, oy + h + ptr)
            ctx.line_to(ox + w / 2 + ptr, oy + h - 0.5)
            ctx.close_path()
        else:
            nib = h * 0.36
            ctx.move_to(ox + nib, oy)
            ctx.line_to(ox + w - nib, oy)
            ctx.line_to(ox + w, oy + h / 2)
            ctx.line_to(ox + w - nib, oy + h)
            ctx.line_to(ox + nib, oy + h)
            ctx.line_to(ox, oy + h / 2)
            ctx.close_path()
    if style == "box":
        ctx.translate(-w / 2, -h - size * 0.32)
    else:
        ctx.translate(-w / 2, -h)
    # the reference banners sit on a darker copy offset down-right
    shape(size * 0.12, size * 0.16)
    src(ctx, _darker(color, 0.55), a)
    ctx.fill()
    shape(0, 0)
    src(ctx, color, a)
    ctx.fill()
    ctx.set_source_surface(ts, padx, pady)
    ctx.paint_with_alpha(a)
    ctx.restore()
    return w, h


def tag(text, x, y, color=COL["magenta"], at=0.4, style="banner", size=30, out=None, space="screen", depth=0.5):
    """Label that pops in at `at` s and (optionally) out at `out` s.  space="set" draws in set coordinates at
    `depth` so it sticks to the scene while the camera moves (use with set_tags())."""
    def f(ctx, t, d):
        s, a = pop(t, at)
        if out is not None:
            a *= 1 - clamp((t - out) / 0.3)
        if a > 0:
            draw_label(ctx, text, x, y, color, size, style, s, a)
    f.space, f.depth = space, depth
    return f


def set_tags(scene, *tags_):
    """Attach set-space tags to an svg_scene (they move with the camera)."""
    old = scene.get("dyn")
    by = {}
    for tg in tags_:
        by.setdefault(tg.depth, []).append(tg)

    def dyn(ctx, t, d, depth):
        if old:
            old(ctx, t, d, depth)
        for tg in by.get(depth, []):
            tg(ctx, t, d)
    scene["dyn"] = dyn
    scene["dyn_depths"] = sorted(set(scene.get("dyn_depths", [])) | set(by))
    return scene


def title_tag(text, color=COL["green"], at=0.2, y=70, size=34):
    return tag(text, W / 2, y + size * 1.4, color, at, "banner", size)


def caption(text, x, y, size=54, color="#ffffff", at=0.3, anchor="mc", weight="Heavy"):
    def f(ctx, t, d):
        s, a = pop(t, at)
        if a <= 0:
            return
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(s, s)
        draw_text(ctx, text, 0, 0, size, color, anchor, a, shadow=0.35, font=_font(text), weight=weight)
        ctx.restore()
    return f


# ------------------------------------------------------------------ portal (memory bubble)
def portal(inner, cx=W / 2, cy=H / 2, r=300, at=0.3, cam=None, blob="#1f3fd6", blob2="#1426a8",
           glow="#ff7a2e", ring=("#ffd23f", "#ff8a1f", "#e23a7a", "#6a3fd6"), close=None):
    """A circular window into another scene (`inner`: scene dict or zero-arg fn returning one): soft blue ink-blob
    rim, warm outer glow, and a segmented gradient ring that slowly turns.  close: time (s) to shrink away."""
    from film import draw_scene
    box = {}
    cam = cam or dict(a=(1200, 675, 1.0), b=(1200, 675, 1.12))

    def soft(ctx, x, y, rad, col, al):
        g = cairo.RadialGradient(x, y, 0, x, y, rad)
        c = _rgb(col)
        g.add_color_stop_rgba(0, c[0], c[1], c[2], al)
        g.add_color_stop_rgba(0.62, c[0], c[1], c[2], al)
        g.add_color_stop_rgba(1, c[0], c[1], c[2], 0)
        ctx.set_source(g)
        ctx.arc(x, y, rad, 0, 2 * math.pi)
        ctx.fill()

    def f(ctx, t, d):
        if "sc" not in box:
            box["sc"] = inner() if callable(inner) else inner
        s, a = pop(t, at, 0.6)
        if close is not None:
            s *= 1 - ease(clamp((t - close) / 0.45))
        if s <= 0.01:
            return
        rr = r * s
        ctx.save()
        soft(ctx, cx, cy, rr * 1.75, glow, 0.35 * a)                       # warm outer glow
        for k in range(16):                                               # soft ink blobs
            ang = k / 16 * 2 * math.pi + t * 0.12
            wob = 1 + 0.07 * math.sin(t * 1.4 + k * 1.7)
            bx, by = cx + math.cos(ang) * rr * 1.08 * wob, cy + math.sin(ang) * rr * 1.08 * wob
            soft(ctx, bx, by, rr * (0.30 + 0.07 * math.sin(k * 2.3 + t)), blob if k % 2 else blob2, 0.95 * a)
        soft(ctx, cx, cy, rr * 1.18, blob2, a)
        ctx.save()
        ctx.arc(cx, cy, rr, 0, 2 * math.pi)
        ctx.clip()
        k = max(rr * 2 / W, rr * 2 / H) * 1.1
        ctx.translate(cx, cy)
        ctx.scale(k, k)
        ctx.translate(-W / 2, -H / 2)
        ctx.push_group()
        draw_scene(ctx, box["sc"], t, d, cam)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(a)
        ctx.restore()
        # segmented gradient ring
        ctx.set_line_width(max(4, rr * 0.03))
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        nseg, rot = 7, t * 0.25
        for i in range(nseg):
            a0 = rot + i / nseg * 2 * math.pi
            a1 = a0 + 2 * math.pi / nseg * (0.78 if i % 3 else 0.55)
            c = ring[i % len(ring)]
            src(ctx, c, a)
            ctx.arc(cx, cy, rr * 1.0, a0, a1)
            ctx.stroke()
        ctx.restore()
    return f


def swirls(n=6, color="#2a2a9a", seed=3, a=0.55):
    """Background of slowly turning soft ink swirls (the reference's 'memory' backdrop). Over-layer."""
    import random
    rnd = random.Random(seed)
    spots = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(140, 260)) for _ in range(n)]

    def f(ctx, t, d):
        for i, (x, y, rr) in enumerate(spots):
            for k in range(9):
                ang = k / 9 * 2 * math.pi + t * (0.15 if i % 2 else -0.12)
                bx, by = x + math.cos(ang) * rr * 0.55, y + math.sin(ang) * rr * 0.55
                g = cairo.RadialGradient(bx, by, 0, bx, by, rr * 0.45)
                c = _rgb(color)
                g.add_color_stop_rgba(0, c[0], c[1], c[2], a)
                g.add_color_stop_rgba(1, c[0], c[1], c[2], 0)
                ctx.set_source(g)
                ctx.arc(bx, by, rr * 0.45, 0, 2 * math.pi)
                ctx.fill()
            g = cairo.RadialGradient(x, y, 0, x, y, rr * 0.3)
            c = _rgb(color)
            g.add_color_stop_rgba(0, min(1, c[0] * 1.4), min(1, c[1] * 1.4), min(1, c[2] * 1.4), a)
            g.add_color_stop_rgba(1, c[0], c[1], c[2], 0)
            ctx.set_source(g)
            ctx.arc(x, y, rr * 0.3, 0, 2 * math.pi)
            ctx.fill()
    return f


# ------------------------------------------------------------------ timeline
def timeline(title, start, end, events=(), ticks=(), segments=(), bg=("#0e2f30", "#1f5a50"), title_color=None,
             bar_y=0.62, grow=1.2, he_mode=False, title_at=0.2):
    """Animated timeline card.
    events:   dict(year, label, color, at, icon=None (svg path), side="up")
    ticks:    (year, label) under the bar  - label None -> formatted year
    segments: (y0, y1, label, colour) coloured spans of the bar
    he_mode:  label ticks in Human Era (adds 10,000)."""
    from svgscene import svg_image
    x0, x1 = 120, W - 120
    by = H * bar_y

    def X(y):
        return x0 + (x1 - x0) * (y - start) / float(end - start)

    def over(ctx, t, d):
        g = cairo.LinearGradient(0, 0, 0, H)
        g.add_color_stop_rgb(0, *_rgb(bg[0]))
        g.add_color_stop_rgb(1, *_rgb(bg[1]))
        ctx.set_source(g)
        ctx.paint()
        draw_label(ctx, title, W / 2, 130, title_color or COL["green"], 34, "banner", *pop(t, title_at))
        q = ease(clamp(t / grow))
        xe = x0 + (x1 - x0) * q
        # base bar
        rrect(ctx, x0, by - 18, xe - x0, 36, 4)
        src(ctx, "#ffffff", 0.10)
        ctx.fill()
        for (y0, y1, lab, colr) in segments:
            a0, a1 = X(y0), min(X(y1), xe)
            if a1 <= a0:
                continue
            rrect(ctx, a0, by - 18, a1 - a0, 36, 4)
            src(ctx, colr, 0.95)
            ctx.fill()
            if lab:
                draw_text(ctx, lab, (a0 + X(y1)) / 2, by, 24, "#ffffff", "mc", clamp((xe - a0) / 200),
                          font=_font(lab), weight="Demi Bold")
        src(ctx, "#ffffff", 0.85)
        ctx.rectangle(x0, by + 20, xe - x0, 3)
        ctx.fill()
        for (yr, lab) in ticks:
            xx = X(yr)
            if xx > xe + 1:
                continue
            txt = lab if lab is not None else fmt_year(he(yr) if he_mode else yr)
            draw_label(ctx, txt, xx, by + 80, COL["teal"] if yr >= 0 else COL["orange"], 24, "box", 1.0,
                       clamp((xe - xx) / 120 + 0.01))
        for ev in events:
            xx = X(ev["year"])
            s, a = pop(t, ev.get("at", grow + 0.3))
            if a <= 0:
                continue
            up = ev.get("side", "up") == "up"
            ty = by - 70 if up else by + 160
            src(ctx, "#ffffff", 0.5 * a)
            ctx.rectangle(xx - 1.5, min(ty, by), 3, abs(by - ty))
            ctx.fill()
            if ev.get("icon"):
                ic = svg_image(ev["icon"], 220)
                rad = 62 * s
                ctx.save()
                ctx.arc(xx, ty - 128, rad, 0, 2 * math.pi)
                ctx.clip()
                k = rad * 2 / ic.get_width()
                ctx.translate(xx - rad, ty - 128 - ic.get_height() * k / 2)
                ctx.scale(k, k)
                ctx.set_source_surface(ic, 0, 0)
                ctx.paint_with_alpha(a)
                ctx.restore()
                src(ctx, ev.get("color", COL["orange"]), a)
                ctx.set_line_width(6)
                ctx.arc(xx, ty - 128, rad, 0, 2 * math.pi)
                ctx.stroke()
                ty -= 0
            draw_label(ctx, ev["label"], xx, ty, ev.get("color", COL["orange"]), 24, "box", s, a)
    return dict(layers=[], over=over)


def _rgb(hx):
    hx = hx.lstrip("#")
    return tuple(int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4))


# ------------------------------------------------------------------ chapter title
def chapter_title(small, big, bar=(0.0, 0.15), labels=("", "Now"), under=None, glow="#ffb347",
                  bar_cols=("#3b2a7a", "#e8a33a", "#1fb5a0")):
    """Dark card: small italic line, big condensed glowing title, gradient era bar with a highlighted span.
    bar = (from, to) as fractions of the bar; labels = (under the span, right end)."""
    from film import draw_scene
    box = {}

    def over(ctx, t, d):
        if under:
            if "sc" not in box:
                box["sc"] = under() if callable(under) else under
            sc = box["sc"]
            draw_scene(ctx, sc, t, d, dict(a=(1200, 675, 1.05), b=(1200, 675, 1.1)))
            src(ctx, "#05030c", 0.78)
            ctx.paint()
        else:
            src(ctx, "#08060f", 1)
            ctx.paint()
        a1 = clamp((t - 0.2) / 0.6)
        a2 = clamp((t - 0.5) / 0.7)
        draw_text(ctx, small, W / 2, 330, 46, "#c78bff", "mc", a1, font=_font(small, EN),
                  weight="Medium Italic" if not has_khmer(small) else "")
        bf = KM_DISPLAY if has_khmer(big) else EN_COND
        fs = 130
        while fs > 60 and text_surface(big, fs, "#ffffff", bf, "Bold").get_width() > W - 220:
            fs -= 6       # shrink long titles to fit the frame
        # glow: stacked translucent copies
        for k, al in ((10, 0.10), (6, 0.16), (3, 0.25)):
            for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)):
                draw_text(ctx, big, W / 2 + dx, 450 + dy, fs, glow, "mc", a2 * al, font=bf, weight="Bold")
        draw_text(ctx, big, W / 2, 450, fs, "#fff1dc", "mc", a2, font=bf, weight="Bold")
        bx0, bx1, byy = 560, 1360, 590
        q = ease(clamp((t - 0.9) / 1.0))
        g = cairo.LinearGradient(bx0, 0, bx1, 0)
        for i, c in enumerate(bar_cols):
            g.add_color_stop_rgb(i / (len(bar_cols) - 1), *_rgb(c))
        rrect(ctx, bx0, byy, (bx1 - bx0) * q, 12, 6)
        ctx.set_source(g)
        ctx.fill()
        if q > 0.99:
            a3 = clamp((t - 1.9) / 0.4)
            sx0, sx1 = bx0 + (bx1 - bx0) * bar[0], bx0 + (bx1 - bx0) * bar[1]
            rrect(ctx, sx0, byy - 4, sx1 - sx0, 20, 8)
            src(ctx, "#ffd36b", a3 * (0.75 + 0.25 * math.sin(t * 4)))
            ctx.fill()
            if labels[0]:
                draw_text(ctx, labels[0], (sx0 + sx1) / 2, byy + 44, 26, "#ffffff", "mc", a3, font=_font(labels[0]))
            if labels[1]:
                draw_text(ctx, labels[1], bx1, byy + 44, 24, "#1fb5a0", "mc", a3, font=_font(labels[1]))
    return dict(layers=[], over=over)


# ------------------------------------------------------------------ map card
def map_card(svg, title=None, pins=(), boxes=(), zoom=(1.0, 1.08), frame=("#fdf3d8", "#f6e27a"),
             inset=62, focus=(0.5, 0.5), banner=None, banner_color="#a3214a", routes=()):
    """Framed flat map (an SVG from make_map_svg.py or hand-drawn, viewBox 2400x1350), styled like the reference:
    cream page, yellow border with white dashes, italic place title top-left, optional banner title top-centre.
    pins:   dict(lon, lat | x, y, label, color, at, style, dot=True)
    boxes:  dict(lon0, lat0, lon1, lat1 | x0, y0, x1, y1, at)          white outline rectangles
    routes: dict(pts=[(lon, lat), ...], at, dur=1.6, color="#ffffff")  dashed arrows drawn on over time"""
    from svgscene import svg_attr, svg_image
    view = svg_attr(svg, "data-view")
    view = [float(v) for v in view.split(",")] if view else None
    img = {}

    def proj(lon, lat):
        lc, la, wd = view
        k = 2400 / (wd * math.cos(math.radians(la)))
        return 1200 + (lon - lc) * k * math.cos(math.radians(la)), 675 - (lat - la) * k

    def over(ctx, t, d):
        if "s" not in img:
            img["s"] = svg_image(svg, 2400)
        s = img["s"]
        src(ctx, frame[0], 1)
        ctx.paint()
        rrect(ctx, 22, 22, W - 44, H - 44, 22)
        src(ctx, frame[1], 1)
        ctx.fill()
        # white dashes running round the border
        ctx.set_dash([34, 30])
        ctx.set_line_width(13)
        rrect(ctx, 42, 42, W - 84, H - 84, 10)
        src(ctx, "#ffffff", 0.85)
        ctx.stroke()
        ctx.set_dash([])
        x, y, w, h = inset, inset, W - 2 * inset, H - 2 * inset
        p = clamp(t / d) if d else 0
        z = zoom[0] * (zoom[1] / zoom[0]) ** ease(p)
        k = w / 2400 * z
        ox = x + w / 2 - 2400 * k * focus[0]
        oy = y + h / 2 - 1350 * k * focus[1]
        ctx.save()
        ctx.rectangle(x, y, w, h)
        ctx.clip()
        ctx.translate(ox, oy)
        ctx.scale(k * 2400 / s.get_width(), k * 2400 / s.get_width())
        ctx.set_source_surface(s, 0, 0)
        ctx.get_source().set_filter(cairo.FILTER_GOOD)
        ctx.paint()
        ctx.restore()

        def to_screen(lonlat):
            px, py = proj(*lonlat) if view else lonlat
            return ox + px * k, oy + py * k
        ctx.save()
        ctx.rectangle(x, y, w, h)
        ctx.clip()
        for b in boxes:
            if "lon0" in b:
                (ax, ay), (bx, byy) = to_screen((b["lon0"], b["lat1"])), to_screen((b["lon1"], b["lat0"]))
            else:
                (ax, ay), (bx, byy) = (ox + b["x0"] * k, oy + b["y0"] * k), (ox + b["x1"] * k, oy + b["y1"] * k)
            a = clamp((t - b.get("at", 0.8)) / 0.4)
            src(ctx, "#ffffff", a)
            ctx.set_line_width(5)
            ctx.rectangle(ax, ay, bx - ax, byy - ay)
            ctx.stroke()
        for rt in routes:
            q = ease(clamp((t - rt.get("at", 0.5)) / rt.get("dur", 1.6)))
            if q <= 0:
                continue
            pts = [to_screen(pp) for pp in rt["pts"]]
            seg = [math.hypot(b[0] - a_[0], b[1] - a_[1]) for a_, b in zip(pts, pts[1:])]
            L, goal, acc = sum(seg), sum(seg) * q, 0.0
            ctx.set_line_width(9)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.set_dash([22, 20])
            src(ctx, rt.get("color", "#ffffff"), 0.95)
            ctx.move_to(*pts[0])
            end, ang = pts[0], 0.0
            for (a_, b), ln in zip(zip(pts, pts[1:]), seg):
                if acc + ln >= goal:
                    f_ = (goal - acc) / ln if ln else 0
                    end = (a_[0] + (b[0] - a_[0]) * f_, a_[1] + (b[1] - a_[1]) * f_)
                    ang = math.atan2(b[1] - a_[1], b[0] - a_[0])
                    ctx.line_to(*end)
                    break
                ctx.line_to(*b)
                acc += ln
                end, ang = b, math.atan2(b[1] - a_[1], b[0] - a_[0])
            ctx.stroke()
            ctx.set_dash([])
            if q > 0.05:   # chevron head
                ctx.set_line_width(10)
                for sgn in (1, -1):
                    ctx.move_to(*end)
                    ctx.line_to(end[0] - 30 * math.cos(ang + sgn * 0.7), end[1] - 30 * math.sin(ang + sgn * 0.7))
                ctx.stroke()
        for pn in pins:
            sx, sy = to_screen((pn["lon"], pn["lat"]) if "lon" in pn else (pn["x"], pn["y"]))
            sc, a = pop(t, pn.get("at", 0.6))
            if a <= 0:
                continue
            if pn.get("dot", True):
                src(ctx, "#ffffff", a)
                ctx.arc(sx, sy, 22 * sc, 0, 2 * math.pi)
                ctx.fill()
            if pn.get("label"):
                dy = -34 if pn.get("above", True) else 90
                draw_label(ctx, pn["label"], sx + pn.get("dx", 0), sy + dy, pn.get("color", COL["magenta"]), 30,
                           pn.get("style", "banner"), sc, a)
        ctx.restore()
        if title:
            ttl = title if has_khmer(title) else " ".join(title)   # letter-spaced italic, like the reference
            draw_text(ctx, ttl, x + 70, y + 40, 30, "#ffffff", "tl", 0.95, shadow=0.25, font=_font(title),
                      weight="Medium Italic" if not has_khmer(title) else "")
        if banner:
            draw_label(ctx, banner, W / 2, y + 130, banner_color, 44, "banner", *pop(t, 0.3))
    return dict(layers=[], over=over)


# ------------------------------------------------------------------ panels / text
def panels(scenes, cams=None, gap=10, at=0.25, bg="#140f24"):
    """2-4 vertical panels, each its own scene (zero-arg fns), sliding up one after another."""
    from film import draw_scene
    n = len(scenes)
    built = {}

    def over(ctx, t, d):
        src(ctx, bg, 1)
        ctx.paint()
        pw = (W - gap * (n - 1)) / n
        for i, fn in enumerate(scenes):
            if i not in built:
                built[i] = fn()
            q = ease(clamp((t - at * i) / 0.6))
            if q <= 0:
                continue
            x = i * (pw + gap)
            ctx.save()
            ctx.rectangle(x, 0, pw, H)
            ctx.clip()
            ctx.translate(0, (1 - q) * H * 0.6)
            cam = (cams or [None] * n)[i] or dict(a=(1200, 675, 1.0), b=(1200, 675, 1.08))
            ctx.push_group()
            draw_scene(ctx, built[i], t, d, cam)
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(q)
            ctx.restore()
    return dict(layers=[], over=over)


def big_text(lines, bg="#141029", at=0.2):
    """lines: [(text, size, colour)] centred, popping in one by one."""
    def over(ctx, t, d):
        src(ctx, bg, 1)
        ctx.paint()
        tot = sum(sz * 1.35 for _, sz, _ in lines)
        y = H / 2 - tot / 2
        for i, (txt, sz, col) in enumerate(lines):
            s, a = pop(t, at + i * 0.25)
            if a > 0:
                ctx.save()
                ctx.translate(W / 2, y + sz * 0.67)
                ctx.scale(s, s)
                draw_text(ctx, txt, 0, 0, sz, col, "mc", a, font=_font(txt), weight="Heavy" if sz > 60 else "Bold")
                ctx.restore()
            y += sz * 1.35
    return dict(layers=[], over=over)


# ------------------------------------------------------------------ 3D clips + graphs
def clip(frames_dir, fps=60, hold_last=True, offset=0.0):
    """A shot made of pre-rendered frames (Blender 3D: blender3d/render3d.py -> DIR/f_0001.png ...).
    Frame for time t = offset + t; holds the last frame past the end."""
    import glob as _glob
    import os as _os
    from core import ROOT
    d = frames_dir if _os.path.isabs(frames_dir) else _os.path.join(ROOT, frames_dir)
    files = sorted(_glob.glob(_os.path.join(d, "f_*.png")))
    cache = {}

    def over(ctx, t, dur):
        if not files:
            src(ctx, "#200a20", 1)
            ctx.paint()
            draw_text(ctx, "3D clip missing: %s" % frames_dir, W / 2, H / 2, 34, "#ffffff", "mc")
            return
        i = int((t + offset) * fps)
        i = min(i, len(files) - 1) if hold_last else i % len(files)
        p = files[max(0, i)]
        if p not in cache:
            if len(cache) > 3:
                cache.clear()
            cache[p] = cairo.ImageSurface.create_from_png(p)
        s = cache[p]
        ctx.save()
        ctx.scale(W / s.get_width(), H / s.get_height())
        ctx.set_source_surface(s, 0, 0)
        ctx.get_source().set_filter(cairo.FILTER_GOOD)
        ctx.paint()
        ctx.restore()
    return dict(layers=[], over=over)


def graph(title, points, xlabels=(), ylabel="", color=COL["violet"], bg=("#f4f1e6", "#e9e4d2"), at=0.4, dur=2.2,
          marks=(), ink="#2a2340"):
    """Animated line chart on a light flat card (the reference's population graph).
    points: [(x 0..1, y 0..1)]; marks: [(index, label, colour)] pop as the line reaches them."""
    def over(ctx, t, d):
        g_ = cairo.LinearGradient(0, 0, 0, H)
        g_.add_color_stop_rgb(0, *_rgb(bg[0]))
        g_.add_color_stop_rgb(1, *_rgb(bg[1]))
        ctx.set_source(g_)
        ctx.paint()
        x0, x1, y0, y1 = 260, W - 220, H - 230, 230
        src(ctx, ink, 0.25)
        ctx.set_line_width(3)
        ctx.move_to(x0, y1 - 20)
        ctx.line_to(x0, y0)
        ctx.line_to(x1 + 20, y0)
        ctx.stroke()
        if title:
            draw_label(ctx, title, W / 2, 150, color, 34, "banner", *pop(t, 0.15))
        for (fx, lab) in xlabels:
            draw_text(ctx, lab, x0 + (x1 - x0) * fx, y0 + 40, 26, ink, "tc", 0.8, font=_font(lab), weight="Demi Bold")
        if ylabel:
            draw_text(ctx, ylabel, x0 - 20, y1 - 40, 26, ink, "br", 0.8, font=_font(ylabel), weight="Demi Bold")
        q = ease(clamp((t - at) / dur))
        pts = [(x0 + (x1 - x0) * px, y0 - (y0 - y1) * py) for px, py in points]
        n = len(pts) - 1
        upto = q * n
        ctx.set_line_width(9)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        src(ctx, color, 1)
        ctx.move_to(*pts[0])
        for i in range(1, n + 1):
            if i <= upto:
                ctx.line_to(*pts[i])
            else:
                f = upto - (i - 1)
                if f > 0:
                    ctx.line_to(pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * f,
                                pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * f)
                break
        ctx.stroke()
        for (idx, lab, colr) in marks:
            if idx <= upto + 1e-6:
                px, py = pts[idx]
                s_, a_ = pop(t, at + dur * idx / max(n, 1))
                src(ctx, "#ffffff", a_)
                ctx.arc(px, py, 16 * s_, 0, 2 * math.pi)
                ctx.fill()
                src(ctx, colr, a_)
                ctx.set_line_width(5)
                ctx.arc(px, py, 16 * s_, 0, 2 * math.pi)
                ctx.stroke()
                draw_label(ctx, lab, px, py - 30, colr, 26, "box", s_, a_)
    return dict(layers=[], over=over)
