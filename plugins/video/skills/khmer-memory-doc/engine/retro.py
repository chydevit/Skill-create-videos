"""1960s look for the Sangkum film: movie-poster title/chapter cards, newsreel / Polaroid / archive-card frames for
authentic images, a stylised newspaper for headline transitions, iris-shutter and film-reel wipes, and the
post pass (film grain, scratches, dust, flicker, desaturation as tension grows).
Authentic images are only scaled, panned and framed; their content is never altered."""
import math
import os

import cairocffi as cairo
import numpy as np

from core import (H, W, clamp, draw_text, ease, load_image, mix, np_to_surface, paint_cover, poly, rng, rrect, smooth,
                  src, text_surface, KM_SANS, KM_DISPLAY)

TEAL, TEAL_D, MUSTARD, CORAL, CREAM, CHAR = "#5f9e98", "#3d6f6b", "#d9a43a", "#e0664f", "#f2e6cc", "#2d2e33"
KM_POSTER = "Koulen"
KM_SUB = "Dangrek"
EN_DISPLAY = "Futura"
EN_TYPE = "American Typewriter"
EN_HAND = "Chalkboard SE"

POSTER_SCHEMES = [   # (bg, block, accent, ink)
    (CREAM, TEAL, CORAL, CHAR), (MUSTARD, CORAL, CREAM, CHAR), (TEAL, MUSTARD, CORAL, CREAM), (CORAL, CREAM, TEAL, CHAR),
    (CREAM, CORAL, MUSTARD, CHAR), (TEAL_D, CORAL, MUSTARD, CREAM), (MUSTARD, TEAL, CREAM, CHAR),
    (CREAM, MUSTARD, TEAL, CHAR), ("#8a8a80", "#5a5a56", "#c8a070", "#f0ece0"), ("#5a5c60", "#3a3c40", "#b0705a", "#ece8dc"),
    ("#3a3c40", "#2a2b2e", "#8a6a5a", "#dcd8cc")]


def _khnum(n):
    return "".join("០១២៣៤៥៦៧៨៩"[int(c)] if c.isdigit() else c for c in str(n))


# ------------------------------------------------------------------ poster pieces
def starburst(ctx, x, y, r, col, n=16, inner=0.78, rot=0.0):
    pts = []
    for i in range(n * 2):
        a = rot + i * math.pi / n
        rr = r if i % 2 == 0 else r * inner
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    poly(ctx, pts)
    src(ctx, col)
    ctx.fill()


def halftone(ctx, x, y, w, h, col, a=0.25, cell=18, grow="right"):
    for j in range(int(h / cell) + 1):
        for i in range(int(w / cell) + 1):
            u = i / max(1, w / cell) if grow == "right" else j / max(1, h / cell)
            r = cell * 0.48 * u
            if r < 0.6:
                continue
            src(ctx, col, a)
            ctx.new_path()
            ctx.arc(x + i * cell + (j % 2) * cell / 2, y + j * cell, r, 0, 6.283)
            ctx.fill()


def _wrap(under, over):
    sc = dict(under or dict(layers=[]))
    base = sc.get("over")

    def over2(ctx, t, d):
        if base:
            base(ctx, t, d)
        over(ctx, t, d)
    sc["over"] = over2
    return sc


def poster_chapter(num, km, en, years, under=None, scheme=None, tagline=None):
    """Chapter card styled like a 1960s Khmer movie poster: colour blocks, starburst roundel with the chapter number,
    Koulen Khmer title, Futura English title, the chapter's scene seen through an arched window."""
    bg, block, acc, ink = POSTER_SCHEMES[(scheme if scheme is not None else (num or 0)) % len(POSTER_SCHEMES)]
    WX, WY, WW, WH = 1040, 120, 760, 820   # window onto the scene

    def over(ctx, t, d):
        k_in = ease(clamp(t / 0.9))
        a_out = clamp((d - t) / 0.7)
        ctx.save()
        # poster sheet with an arched window (even-odd), sliding in from the right
        ox = (1 - k_in) * W * 0.25
        ctx.translate(ox, 0)
        ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        ctx.rectangle(-W, 0, W * 3, H)
        ctx.new_sub_path()
        ctx.move_to(WX, WY + WH)
        ctx.line_to(WX, WY + WW / 2)
        ctx.arc(WX + WW / 2, WY + WW / 2, WW / 2, math.pi, 2 * math.pi)
        ctx.line_to(WX + WW, WY + WH)
        ctx.close_path()
        src(ctx, bg, a_out)
        ctx.fill()
        ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
        # window rim
        ctx.move_to(WX, WY + WH)
        ctx.line_to(WX, WY + WW / 2)
        ctx.arc(WX + WW / 2, WY + WW / 2, WW / 2, math.pi, 2 * math.pi)
        ctx.line_to(WX + WW, WY + WH)
        ctx.close_path()
        src(ctx, ink, a_out)
        ctx.set_line_width(10)
        ctx.stroke()
        # colour blocks + halftone
        src(ctx, block, a_out)
        ctx.rectangle(0, 0, 120, H)
        ctx.fill()
        ctx.rectangle(0, H - 120, W, 120)
        ctx.fill()
        halftone(ctx, 560, 150, 420, 230, acc, 0.5 * a_out, 20)
        # roundel
        rot = t * 0.15
        sb = smooth((t - 0.3) / 0.6)
        starburst(ctx, 330, 300, 150 * sb, acc, 18, 0.8, rot)
        ctx.new_path()
        ctx.arc(330, 300, 110 * sb, 0, 6.283)
        src(ctx, ink, a_out)
        ctx.fill()
        if sb > 0.5:
            if num:
                draw_text(ctx, "ជំពូកទី", 330, 262, 34, bg, "mc", a_out, font=KM_SUB)
                draw_text(ctx, _khnum(num), 330, 322, 74, bg, "mc", a_out, font=KM_POSTER)
            else:
                draw_text(ctx, "១៩៥៥", 330, 300, 56, bg, "mc", a_out, font=KM_POSTER)
        # titles
        b = smooth((t - 0.5) / 0.7) * a_out
        rise = (1 - smooth((t - 0.5) / 0.7)) * 40
        ks = 96
        while ks > 56 and text_surface(km, ks, ink, KM_POSTER).get_width() > 820:
            ks -= 4
        draw_text(ctx, km, 180, 470 + rise + (96 - ks) * 0.6, ks, ink, "tl", b, font=KM_POSTER)
        c = smooth((t - 0.9) / 0.7) * a_out
        es = 54
        while es > 30 and text_surface(en.upper(), es, ink, EN_DISPLAY, "Bold").get_width() > 860:
            es -= 2
        draw_text(ctx, en.upper(), 184, 690 + (54 - es) * 0.5, es, block if block != bg else acc, "tl", c,
                  font=EN_DISPLAY, weight="Bold")
        if years:
            ctx.save()
            ctx.translate(184, 800)
            src(ctx, acc, c)
            poly(ctx, [(0, 0), (380, 0), (360, 30), (380, 60), (0, 60)])
            ctx.fill()
            ctx.restore()
            draw_text(ctx, years, 204, 830, 34, ink, "ml", c, font=EN_DISPLAY, weight="Medium")
        draw_text(ctx, "សង្គមរាស្ត្រនិយម  ·  SANGKUM REASTR NIYUM  ·  1955–1970", W / 2, H - 60, 24, bg, "mc",
                  a_out * 0.9, font=EN_DISPLAY, weight="Medium")
        ctx.restore()
    return _wrap(under, over)


def poster_title(km, en, sub_km, sub_en, under=None):
    """Opening title as a full movie poster with the scene behind a big circular window."""
    def over(ctx, t, d):
        a = clamp(t / 0.8) * clamp((d - t) / 1.0)
        cx, cy, r = W * 0.5, H * 0.33, 255 + 8 * math.sin(t * 0.6)
        ctx.save()
        ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        ctx.rectangle(0, 0, W, H)
        ctx.new_sub_path()
        ctx.arc(cx, cy, r, 0, 6.283)
        src(ctx, CREAM, a * 0.96)
        ctx.fill()
        ctx.restore()
        ctx.new_path()
        ctx.arc(cx, cy, r, 0, 6.283)
        src(ctx, CHAR, a)
        ctx.set_line_width(12)
        ctx.stroke()
        for k, col in enumerate((TEAL, MUSTARD, CORAL)):   # mid-century stripes
            src(ctx, col, a)
            ctx.rectangle(0, 60 + k * 26, W, 16)
            ctx.fill()
            ctx.rectangle(0, H - 100 - k * 26, W, 16)
            ctx.fill()
        sb = smooth((t - 0.5) / 0.8)
        starburst(ctx, cx + 360, cy - 170, 110 * sb, CORAL, 16, 0.78, t * 0.2)
        if sb > 0.5:
            draw_text(ctx, "១៩៥៥\n១៩៧០", cx + 360, cy - 170, 40, CREAM, "mc", a, font=KM_POSTER, align="center",
                      spacing=0.8)
        b = smooth((t - 1.0) / 1.0) * a
        draw_text(ctx, km, cx, cy + r + 10, 104, CHAR, "tc", b, font=KM_POSTER)
        c = smooth((t - 1.8) / 1.0) * a
        draw_text(ctx, en.upper(), cx, cy + r + 160, 46, TEAL_D, "tc", c, font=EN_DISPLAY, weight="Bold")
        e = smooth((t - 2.6) / 1.0) * a
        draw_text(ctx, sub_km + "   ·   " + sub_en, cx, cy + r + 228, 30, CORAL, "tc", e, font=KM_SANS, weight="Bold")
    return _wrap(under, over)


# ------------------------------------------------------------------ archive frames (authentic images)
def _card_text(ctx, card, x, y, w, a, dark=True):
    """Archive label: title km/en, date, holding institution / source, credit + licence."""
    ink = CHAR if dark else CREAM
    sub = "#5a5a5a" if dark else "#d8d0c0"
    draw_text(ctx, "ឯកសារបណ្ណសារ · ARCHIVE", x, y, 20, CORAL, "tl", a, font=EN_DISPLAY, weight="Bold")
    yy = y + 40
    if card.get("km"):
        _, h = draw_text(ctx, card["km"], x, yy, 32, ink, "tl", a, font=KM_SANS, weight="Bold", width=w)
        yy += h + 4
    _, h = draw_text(ctx, card.get("en") or "", x, yy, 27, ink, "tl", a, font=EN_DISPLAY, weight="Medium", width=w)
    yy += h + 14
    for lab, key in (("DATE", "date"), ("SOURCE", "inst"), ("PLACE", "found")):
        v = card.get(key)
        if not v:
            continue
        draw_text(ctx, lab, x, yy + 3, 15, CORAL, "tl", a, font=EN_DISPLAY, weight="Bold")
        _, h = draw_text(ctx, v, x + 92, yy, 21, sub, "tl", a, font=EN_TYPE, width=w - 92)
        yy += h + 8
    if card.get("note"):
        _, h = draw_text(ctx, card["note"], x, yy + 6, 20, sub, "tl", a, font=EN_TYPE, width=w, italic=True)
        yy += h + 12
    if card.get("credit"):
        draw_text(ctx, card["credit"], x, yy + 8, 16, sub, "tl", a * 0.9, font=EN_DISPLAY, width=w)


def _img_box(ctx, s, x, y, w, h, z, fx, fy, contain=True):
    paint_cover(ctx, s, x, y, w, h, z, fx, fy, contain=contain)


def archive_card(path, card, z=(1.0, 1.08), focus=(0.5, 0.5), bg=TEAL_D):
    """Photo framed on the left, archive label card on the right (title, date, source, licence)."""
    def over(ctx, t, d):
        s = load_image(path)
        q = ease(clamp(t / d))
        src(ctx, bg)
        ctx.paint()
        halftone(ctx, 0, 0, W, 200, mix(bg, "#000000", 0.25), 0.6, 26, "down")
        a = smooth(t / 0.7)
        iw, ih = s.get_width(), s.get_height()
        bw, bh = 1120, 860
        k = min(bw / iw, bh / ih)
        dw, dh = iw * k, ih * k
        x0, y0 = 90 + (bw - dw) / 2, 110 + (bh - dh) / 2
        src(ctx, "#000000", 0.35 * a)
        ctx.rectangle(x0 + 14, y0 + 16, dw + 24, dh + 24)
        ctx.fill()
        src(ctx, CREAM, a)
        ctx.rectangle(x0 - 12, y0 - 12, dw + 24, dh + 24)
        ctx.fill()
        zz = z[0] + (z[1] - z[0]) * q
        ctx.save()
        ctx.rectangle(x0, y0, dw, dh)
        ctx.clip()
        ctx.translate(x0 + dw / 2, y0 + dh / 2)
        ctx.scale(k * zz, k * zz)
        ctx.translate(-iw * focus[0], -ih * focus[1])
        ctx.set_source_surface(s, 0, 0)
        ctx.get_source().set_filter(cairo.FILTER_GOOD)
        ctx.paint_with_alpha(a)
        ctx.restore()
        # label card (index-card style)
        b = smooth((t - 0.5) / 0.7)
        cx, cy, cw, ch = 1290, 170 + (1 - b) * 40, 560, 720
        src(ctx, "#000000", 0.3 * b)
        ctx.rectangle(cx + 10, cy + 12, cw, ch)
        ctx.fill()
        src(ctx, CREAM, b)
        ctx.rectangle(cx, cy, cw, ch)
        ctx.fill()
        src(ctx, CORAL, b)
        ctx.rectangle(cx, cy, cw, 12)
        ctx.fill()
        src(ctx, "#b8c8c4", 0.5 * b)
        for k2 in range(1, 16):
            ctx.rectangle(cx + 20, cy + 40 + k2 * 44, cw - 40, 1.5)
        ctx.fill()
        _card_text(ctx, card, cx + 34, cy + 40, cw - 68, b)
    return dict(layers=[], over=over)


def newsreel(path, card, z=(1.0, 1.1), fx=(0.5, 0.5), fy=(0.5, 0.5)):
    """Authentic photo projected as a 1960s newsreel: 4:3 gate, moving sprocket strip, flicker, title strip."""
    def over(ctx, t, d):
        s = load_image(path)
        q = ease(clamp(t / d))
        src(ctx, "#0c0b0b")
        ctx.paint()
        gx, gy, gw, gh = 300, 50, 1320, 900
        # sprocket strips
        for sx in (180, 1660):
            src(ctx, "#1c1a1a")
            ctx.rectangle(sx, 0, 80, H)
            ctx.fill()
            off = (t * 180) % 90
            for k in range(14):
                rrect(ctx, sx + 22, -90 + k * 90 + off, 36, 50, 6)
                src(ctx, "#d8d0c0", 0.85)
                ctx.fill()
        zz = z[0] + (z[1] - z[0]) * q
        ctx.save()
        rrect(ctx, gx, gy, gw, gh, 26)
        ctx.clip()
        src(ctx, "#000000")
        ctx.paint()
        weave = math.sin(t * 9) * 1.5
        paint_cover(ctx, s, gx, gy + weave, gw, gh, zz, fx[0] + (fx[1] - fx[0]) * q, fy[0] + (fy[1] - fy[0]) * q,
                    contain=(s.get_width() / s.get_height() < 1.2))
        fl = 0.06 + 0.05 * math.sin(t * 31) * math.sin(t * 7)
        src(ctx, "#fff8e0", max(0, fl))
        ctx.paint()
        ctx.restore()
        # title strip (grows to fit a wrapped title)
        a = smooth((t - 0.4) / 0.6) * clamp((d - t) / 0.5)
        ttl = (card.get("km") or "") + ("   " if card.get("km") else "") + (card.get("en") or "")
        ts = text_surface(ttl, 27, CREAM, KM_SANS, "Bold", width=gw - 60)
        sh_ = ts.get_height() + 58
        src(ctx, CHAR, 0.88 * a)
        ctx.rectangle(gx, gy + gh - sh_, gw, sh_)
        ctx.fill()
        src(ctx, MUSTARD, a)
        ctx.rectangle(gx, gy + gh - sh_, 14, sh_)
        ctx.fill()
        ctx.set_source_surface(ts, gx + 36, gy + gh - sh_ + 8)
        ctx.paint_with_alpha(a)
        meta = "  ·  ".join(v for v in (card.get("date"), card.get("inst"), card.get("credit")) if v)
        draw_text(ctx, meta, gx + 36, gy + gh - 42, 17, "#d8d0c0", "tl", a, font=EN_TYPE, width=gw - 60)
        draw_text(ctx, "ARCHIVE FOOTAGE STILL" if card.get("footage") else "ARCHIVE PHOTOGRAPH", gx + gw - 20, gy + 26,
                  18, MUSTARD, "tr", a, font=EN_DISPLAY, weight="Bold")
    return dict(layers=[], over=over)


def polaroid(path, card, tilt=-0.04, bg=MUSTARD, z=(1.0, 1.06)):
    """Authentic photo as an instant-print card dropped onto a desk; handwritten-style caption + archive label."""
    def over(ctx, t, d):
        s = load_image(path)
        src(ctx, bg)
        ctx.paint()
        for k in range(10):
            src(ctx, mix(bg, "#000000", 0.08), 1)
            ctx.rectangle(0, k * 120, W, 60)
            ctx.fill()
        drop = 1 - ease(clamp(t / 0.8))
        q = ease(clamp(t / d))
        iw, ih = s.get_width(), s.get_height()
        side = 760
        k = min(side * 1.25 / iw, side / ih)
        pw, ph = iw * k, ih * k
        fw, fh = pw + 60, ph + 170
        ctx.save()
        ctx.translate(W * 0.36, H * 0.5 - drop * 200)
        ctx.rotate(tilt + drop * 0.25)
        src(ctx, "#000000", 0.3)
        ctx.rectangle(-fw / 2 + 16, -fh / 2 + 20, fw, fh)
        ctx.fill()
        src(ctx, "#fbf8f0")
        ctx.rectangle(-fw / 2, -fh / 2, fw, fh)
        ctx.fill()
        ctx.save()
        ctx.rectangle(-pw / 2, -fh / 2 + 30, pw, ph)
        ctx.clip()
        zz = z[0] + (z[1] - z[0]) * q
        ctx.translate(0, -fh / 2 + 30 + ph / 2)
        ctx.scale(k * zz, k * zz)
        ctx.translate(-iw / 2, -ih / 2)
        ctx.set_source_surface(s, 0, 0)
        ctx.get_source().set_filter(cairo.FILTER_GOOD)
        ctx.paint()
        ctx.restore()
        draw_text(ctx, card.get("hand") or card.get("en") or "", 0, fh / 2 - 70, 30, "#2a3a6a", "mc", 1.0, font=EN_HAND,
                  width=fw - 60, align="center")
        # tape
        src(ctx, "#f4ecc8", 0.75)
        ctx.rectangle(-70, -fh / 2 - 22, 140, 44)
        ctx.fill()
        ctx.restore()
        b = smooth((t - 0.8) / 0.7)
        cx, cy, cw = 1260, 210, 580
        src(ctx, "#000000", 0.25 * b)
        ctx.rectangle(cx + 10, cy + 12, cw, 660)
        ctx.fill()
        src(ctx, CREAM, b)
        ctx.rectangle(cx, cy, cw, 660)
        ctx.fill()
        _card_text(ctx, card, cx + 32, cy + 34, cw - 64, b)
    return dict(layers=[], over=over)


# ------------------------------------------------------------------ newspaper (headline transitions)
def newspaper_surface(km, en, date):
    """A stylised (not authentic) 1960s newspaper front page with the headline; cached per headline."""
    key = (km, en, date)
    if key in _NEWS:
        return _NEWS[key]
    from core import surface
    w, h = 1400, 960
    s = surface(w, h)
    ctx = cairo.Context(s)
    src(ctx, "#efe8d6")
    ctx.paint()
    src(ctx, CHAR)
    ctx.rectangle(40, 40, w - 80, 6)
    ctx.fill()
    draw_text(ctx, "ព័ត៌មានប្រចាំថ្ងៃ", w / 2, 60, 74, CHAR, "tc", font=KM_POSTER)
    draw_text(ctx, "ILLUSTRATIVE FRONT PAGE · " + (date or ""), w / 2, 168, 20, "#5a5a5a", "tc", font=EN_TYPE)
    ctx.rectangle(40, 206, w - 80, 3)
    ctx.fill()
    _, hh = draw_text(ctx, km, w / 2, 236, 76, CHAR, "tc", font=KM_POSTER, width=w - 120, align="center", spacing=0.85)
    draw_text(ctx, en.upper(), w / 2, 250 + hh, 40, "#3a3a3a", "tc", font=EN_DISPLAY, weight="Bold", width=w - 120,
              align="center")
    R = rng(len(en))
    y0 = 420 + hh
    for col in range(4):   # columns of greyed 'text'
        x = 60 + col * (w - 120) / 4
        for ln in range(int((h - y0 - 50) / 22)):
            src(ctx, "#8a8478", 0.5)
            ctx.rectangle(x, y0 + ln * 22, (w - 120) / 4 - 30 - R.random() * 60 * (ln % 5 == 4), 9)
            ctx.fill()
    _NEWS[key] = s
    return s


_NEWS = {}


def news_overlay(ctx, p, km, en, date):
    """Newspaper spins in (p 0..0.55), holds, then flies past the camera (p 0.75..1)."""
    s = newspaper_surface(km, en, date)
    if p < 0.55:
        q = ease(p / 0.55)
        sc, rot, a = 0.05 + 0.95 * q, (1 - q) * 4 * math.pi, 1.0
    elif p < 0.78:
        sc, rot, a = 1.0, 0.0, 1.0
    else:
        q = ease((p - 0.78) / 0.22)
        sc, rot, a = 1.0 + 1.6 * q, 0.0, 1 - q
    k = min(W * 0.78 / s.get_width(), H * 0.86 / s.get_height()) * sc
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.rotate(rot)
    ctx.scale(k, k)
    src(ctx, "#000000", 0.4 * a)
    ctx.rectangle(-s.get_width() / 2 + 18, -s.get_height() / 2 + 22, s.get_width(), s.get_height())
    ctx.fill()
    ctx.set_source_surface(s, -s.get_width() / 2, -s.get_height() / 2)
    ctx.paint_with_alpha(a)
    ctx.restore()


# ------------------------------------------------------------------ transitions (iris shutter, film reel)
def iris_path(ctx, cx, cy, r, rot, n=7):
    pts = [(cx + math.cos(rot + i * 2 * math.pi / n) * r, cy + math.sin(rot + i * 2 * math.pi / n) * r) for i in range(n)]
    poly(ctx, pts)


def shutter_fx(ctx, p):
    """Camera-iris opening on the incoming shot: blades drawn around the aperture."""
    r = (p ** 1.3) * W * 0.62
    rot = p * 1.2
    ctx.save()
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    ctx.rectangle(0, 0, W, H)
    iris_path(ctx, W / 2, H / 2, r, rot)
    src(ctx, "#141416", clamp(1.6 - p * 1.6))
    ctx.fill()
    ctx.restore()
    if p < 0.95:
        for i in range(7):   # blade edges
            a = rot + i * 2 * math.pi / 7
            x0, y0 = W / 2 + math.cos(a) * r, H / 2 + math.sin(a) * r
            src(ctx, "#5a5a60", 0.6 * (1 - p))
            ctx.set_line_width(3)
            ctx.move_to(x0, y0)
            ctx.line_to(x0 + math.cos(a + 1.9) * W, y0 + math.sin(a + 1.9) * W)
            ctx.stroke()


def iris_clip(ctx, p):
    r = (p ** 1.3) * W * 0.62
    iris_path(ctx, W / 2, H / 2, r, p * 1.2)
    ctx.clip()


def reel_clip(ctx, p):
    x = -260 + p * (W + 520)
    ctx.rectangle(0, 0, x, H)
    ctx.clip()


def reel_fx(ctx, p):
    """A film strip sweeps across with a spinning reel riding on it."""
    x = -260 + p * (W + 520)
    src(ctx, "#1c1a1a")
    ctx.rectangle(x - 120, 0, 140, H)
    ctx.fill()
    off = (p * 900) % 80
    for k in range(16):
        for sx in (x - 108, x - 2):
            rrect(ctx, sx, -80 + k * 80 + off, 22, 40, 5)
            src(ctx, "#e8e0cc", 0.9)
            ctx.fill()
    rot = p * 14
    cx, cy, r = x - 50, H / 2, 230
    ctx.new_path()
    ctx.arc(cx, cy, r, 0, 6.283)
    src(ctx, "#c9c9c4")
    ctx.fill()
    ctx.new_path()
    ctx.arc(cx, cy, r * 0.9, 0, 6.283)
    src(ctx, "#3a3a40")
    ctx.fill()
    for i in range(6):
        a = rot + i * math.pi / 3
        ctx.new_path()
        ctx.arc(cx + math.cos(a) * r * 0.52, cy + math.sin(a) * r * 0.52, r * 0.22, 0, 6.283)
        src(ctx, "#c9c9c4")
        ctx.fill()
    ctx.new_path()
    ctx.arc(cx, cy, r * 0.12, 0, 6.283)
    src(ctx, "#1c1a1a")
    ctx.fill()


# ------------------------------------------------------------------ post pass
_POST = {}


def _assets():
    if _POST:
        return _POST
    r = rng(17)
    grains = []
    from scipy.ndimage import gaussian_filter
    for i in range(8):   # coarse film-stock grain at 1/3 resolution, slightly clumped
        g = gaussian_filter(r.standard_normal((H // 2, W // 2)).astype(np.float32), 0.45) * 1.6
        al = np.clip(np.abs(g) * 0.04, 0, 0.1)
        col = (g > 0).astype(np.float32)
        grains.append(np_to_surface(np.dstack([col, col, col, al])))
    _POST["grain"] = grains
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W * 0.6)) ** 2 + ((yy - H / 2) / (H * 0.6)) ** 2)
    a = np.clip((d - 0.6) * 1.1, 0, 0.55)
    _POST["vig"] = np_to_surface(np.dstack([np.full((H, W, 3), 0.06, np.float32), a]))
    return _POST


def post(ctx, fi, sat=1.0, grain=1.0, scratch=1.0):
    """Film look: desaturation (sat<1), vignette, grain, scratches and dust that change every frame."""
    A = _assets()
    if sat < 0.999:
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_HSL_SATURATION)
        ctx.set_source_rgba(0.5, 0.5, 0.5, 1 - sat)
        ctx.paint()
        ctx.restore()
        if sat < 0.6:   # cooler, flatter shadows in the darkest chapters
            ctx.set_source_rgba(0.12, 0.13, 0.16, (0.6 - sat) * 0.25)
            ctx.paint()
    ctx.set_source_surface(A["vig"], 0, 0)
    ctx.paint()
    ctx.save()
    ctx.scale(2, 2)
    ctx.set_source_surface(A["grain"][(fi // 2) % 8], 0, 0)   # grain holds 2 frames (compresses far better)
    ctx.get_source().set_filter(cairo.FILTER_BILINEAR)
    ctx.paint_with_alpha(0.9 * grain)
    ctx.restore()
    if scratch:
        R = rng(fi * 7 + 3)
        for _ in range(R.integers(0, 3)):   # vertical scratches
            x = R.random() * W
            src(ctx, "#f4efe0" if R.random() < 0.6 else "#1a1a1a", (0.12 + 0.18 * R.random()) * scratch)
            ctx.set_line_width(0.8 + R.random() * 1.6)
            y0 = R.random() * H * 0.5
            ctx.move_to(x, y0)
            ctx.line_to(x + R.normal() * 6, y0 + H * (0.3 + 0.7 * R.random()))
            ctx.stroke()
        for _ in range(R.integers(0, 6)):   # dust specks / hairs
            x, y = R.random() * W, R.random() * H
            src(ctx, "#1a1a1a" if R.random() < 0.7 else "#f4efe0", 0.35 * scratch)
            if R.random() < 0.8:
                ctx.new_path()
                ctx.arc(x, y, 1 + R.random() * 2.5, 0, 6.283)
                ctx.fill()
            else:
                ctx.set_line_width(1.2)
                ctx.move_to(x, y)
                ctx.curve_to(x + 10, y - 8, x + 20, y + 10, x + 34 * R.random(), y + 4)
                ctx.stroke()
        fl = 0.025 * math.sin(fi * 1.7) * math.sin(fi * 0.37)   # gentle exposure flicker
        if fl > 0:
            src(ctx, "#fff8e8", fl)
        else:
            src(ctx, "#000000", -fl)
        ctx.paint()


def results_card(title_km, title_en, rows, note=None, under=None):
    """Election result as 1960s bar chart. rows: [(km, en, pct, seats_text, colour)]."""
    def over(ctx, t, d):
        import cards
        cards.bg_paper(ctx, t)
        a = smooth(t / 0.7) * clamp((d - t) / 0.6)
        draw_text(ctx, title_km, W / 2, 120, 52, CREAM, "mc", a, font=KM_POSTER)
        draw_text(ctx, title_en.upper(), W / 2, 190, 30, MUSTARD, "mc", a, font=EN_DISPLAY, weight="Bold")
        x0, bw = 620, 1000
        for i, (km, en, pct, seats, col) in enumerate(rows):
            y = 300 + i * 190
            ia = a * smooth((t - 0.5 - i * 0.5) / 0.6)
            g = ease(clamp((t - 0.6 - i * 0.5) / 1.4))
            draw_text(ctx, km, x0 - 30, y + 10, 36, CREAM, "tr", ia, font=KM_SANS, weight="Bold")
            draw_text(ctx, en, x0 - 30, y + 66, 24, "#c8c0b0", "tr", ia, font=EN_DISPLAY, weight="Medium")
            src(ctx, "#000000", 0.25 * ia)
            ctx.rectangle(x0, y + 10, bw, 90)
            ctx.fill()
            src(ctx, col, ia)
            ctx.rectangle(x0, y + 10, bw * pct / 100 * g, 90)
            ctx.fill()
            draw_text(ctx, "%d%%" % round(pct * g), x0 + 20, y + 55, 44, CHAR if pct > 20 else CREAM, "ml", ia,
                      font=EN_DISPLAY, weight="Bold")
            draw_text(ctx, seats, x0 + bw + 30, y + 55, 34, CREAM, "ml", ia, font=KM_SANS, weight="Bold")
        if note:
            draw_text(ctx, note, W / 2, H - 120, 22, "#c8c0b0", "mc", a, font=EN_DISPLAY, weight="Medium")
    return _wrap(under, over)
