// neon: on a dark background, glowing tube outlines trace each shape, the logo lights up with a flash,
// letters (if the logo has a text row) flicker on like a neon sign; otherwise the lit mark stutters once.
// Shapes too dark for the dark background are shown white, like a logo's white-text variant.
import * as E from '../engine.mjs';

function tint(img, color) {
  const cv = E.canvas(img.width, img.height), g = cv.getContext('2d');
  g.drawImage(img, 0, 0);
  g.globalCompositeOperation = 'source-in';
  g.fillStyle = color; g.fillRect(0, 0, cv.width, cv.height);
  return cv;
}

// Tube outline sprite for a part: a thin band along its edge in its own (brightened) colours.
function outline(p, halfWidth) {
  E.field(p);
  const cv = E.canvas(p.w, p.h), g = cv.getContext('2d'), img = g.createImageData(p.w, p.h), d = img.data;
  const white = p.lum < 0.25;
  for (let i = 0; i < p.w * p.h; i++) {
    const a = E.clamp(1 - Math.abs(p.sdf[i]) / halfWidth);
    if (a <= 0) continue;
    const c = white ? [255, 255, 255] : E.mix([p.C[i * 3], p.C[i * 3 + 1], p.C[i * 3 + 2]], [255, 255, 255], 0.25);
    d[i * 4] = c[0]; d[i * 4 + 1] = c[1]; d[i * 4 + 2] = c[2]; d[i * 4 + 3] = 255 * a;
  }
  g.putImageData(img, 0, 0);
  return cv;
}

function flickerSchedule(n, start, gap) {
  let a = 7;
  const rnd = () => { a = (a * 16807) % 2147483647; return a / 2147483647; };
  return Array.from({ length: n }, (_, i) => {
    const s = start + i * gap + (rnd() - 0.5) * gap * 0.6;
    const steps = rnd() < 0.6 ? [[0, 1], [0.035, 0.05], [0.09, 0.75], [0.12, 0.1], [0.2, 1]] : [[0, 0.8], [0.05, 0.1], [0.13, 1]];
    return steps.map(([dt, v]) => [s + dt, v]);
  });
}
const level = (steps, t, before = 0) => { let v = before; for (const [ts, lv] of steps) if (t >= ts) v = lv; return v; };

export async function setup(ctx) {
  const L = E.L, W = E.W, H = E.H, k1080 = Math.min(W, H) / 1080;
  const marks = L.parts.filter(p => !p.text), letters = L.reading.filter(p => p.text);
  const tubeHalf = 3.2 * k1080 / L.S;                       // ~6px tube on screen
  marks.forEach((p, i) => {
    p.tube = outline(p, tubeHalf);
    p.lit = p.lum < 0.25 ? tint(p.sprite, '#ffffff') : p.sprite;
    const n = marks.length, span = Math.min(0.25, 0.6 / n);
    p.draw = [0.15 + i * span, Math.min(1.3, 1.1 + i * span)];
    p.r = Math.hypot(p.bw, p.bh);
  });
  letters.forEach(p => { p.lit = p.lum < 0.25 ? tint(p.sprite, '#ffffff') : p.sprite; p.ghost = tint(p.sprite, '#bfe9e4'); });

  const T = { ignite: 1.45, fill: [1.4, 1.62], outlineOut: [1.5, 1.95] };
  const gap = letters.length ? Math.min(0.085, 0.8 / letters.length) : 0;
  const flick = flickerSchedule(letters.length, 1.85, gap);
  const lettersEnd = letters.length ? Math.max(...flick.map(s => s[s.length - 1][0])) : 0;
  const stutter = letters.length ? [] : [[1.95, 0.2], [2.0, 1], [2.07, 0.35], [2.12, 1]];
  T.gloss = [Math.max(2.45, lettersEnd + 0.15), Math.max(2.45, lettersEnd + 0.15) + 0.6];
  T.chime = T.gloss[0] + 0.2; T.pulse = T.chime - 0.05; T.hold = T.gloss[0] + 0.45;

  const glowCol = E.mainColour(L.main);
  const rnd = E.mulberry32(12);
  const dust = Array.from({ length: 70 }, () => ({
    x: rnd() * W, y: rnd() * H, v: (8 + rnd() * 22) * k1080, r: (0.8 + rnd() * 1.8) * k1080, a: 0.12 + rnd() * 0.3,
    w: 0.3 + rnd() * 0.6, tw: 1 + rnd() * 3, ph: rnd() * 6.28, c: L.palette[Math.floor(rnd() * L.palette.length)],
  }));
  const logo = E.canvas(W, H), lg = logo.getContext('2d');
  const fx = E.canvas(W, H), fg = fx.getContext('2d');
  const [mx, my] = L.toFrame(L.main.cx, L.main.cy);

  function render(t, transparent) {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, W, H);
    const lit = E.smooth((t - T.ignite) / 0.6);
    const flash = t > T.ignite ? Math.exp(-(t - T.ignite) * 4) : 0;
    if (!transparent) {
      E.paintBg(ctx, t, 'dark');
      if (lit > 0) {
        const r = ctx.createRadialGradient(mx, my, 0, mx, my, Math.max(L.box.w, L.box.h) * 1.1);
        r.addColorStop(0, E.rgba(glowCol, 0.16 * lit)); r.addColorStop(1, E.rgba(glowCol, 0));
        ctx.fillStyle = r; ctx.fillRect(0, 0, W, H);
      }
      const boost = 1 + 1.4 * flash;
      ctx.save(); ctx.globalCompositeOperation = 'lighter';
      for (const p of dust) {
        const y = ((p.y - p.v * t) % H + H) % H, x = p.x + Math.sin(t * p.w + p.ph) * 14;
        ctx.fillStyle = E.rgba(p.c, Math.min(1, p.a * (0.6 + 0.4 * Math.sin(t * p.tw + p.ph)) * boost * E.smooth(t / 0.6)));
        ctx.beginPath(); ctx.arc(x, y, p.r, 0, Math.PI * 2); ctx.fill();
      }
      ctx.restore();
    }
    const push = E.pushIn(t, T.hold);

    // tubes drawing on: a sweep around each shape's centre
    fg.setTransform(1, 0, 0, 1, 0, 0);
    fg.clearRect(0, 0, W, H);
    const outA = 1 - E.smooth(E.prog(t, T.outlineOut));
    if (outA > 0) for (const p of marks) {
      const pr = E.easeInOut(E.prog(t, p.draw));
      if (pr <= 0) continue;
      fg.save();
      E.applyPush(fg, push); E.logoSpace(fg);
      if (pr < 1) {
        fg.beginPath(); fg.moveTo(p.cx, p.cy);
        fg.arc(p.cx, p.cy, p.r, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * pr); fg.closePath(); fg.clip();
      }
      fg.drawImage(p.tube, p.rx, p.ry);
      fg.restore();
    }

    // lit logo
    lg.setTransform(1, 0, 0, 1, 0, 0);
    lg.clearRect(0, 0, W, H);
    lg.imageSmoothingEnabled = true; lg.imageSmoothingQuality = 'high';
    const fillA = E.smooth(E.prog(t, T.fill)) * level(stutter, t, 1);
    lg.save(); E.applyPush(lg, push); E.logoSpace(lg);
    if (fillA > 0) { lg.globalAlpha = fillA; for (const p of marks) lg.drawImage(p.lit, p.rx, p.ry); }
    letters.forEach((p, i) => { const v = level(flick[i], t); if (v > 0) { lg.globalAlpha = v; lg.drawImage(p.lit, p.rx, p.ry); } });
    lg.restore();
    // unlit tubes for the letters
    const ghost = 0.09 * E.smooth(E.prog(t, [0.25, 0.9]));
    if (ghost > 0 && letters.length) {
      ctx.save(); E.applyPush(ctx, push); E.logoSpace(ctx);
      letters.forEach((p, i) => { ctx.globalAlpha = ghost * (1 - level(flick[i], t)); if (ctx.globalAlpha > 0.003) ctx.drawImage(p.ghost, p.rx, p.ry); });
      ctx.restore();
    }
    E.gloss(lg, t, T.gloss, 0.32);

    const pulse = Math.exp(-Math.pow((t - T.pulse) / 0.22, 2));
    const glowA = 0.5 + 0.9 * flash + 0.45 * pulse;
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    ctx.globalAlpha = Math.min(1, glowA * 0.75); ctx.filter = `blur(${30 * k1080}px)`; ctx.drawImage(logo, 0, 0);
    ctx.globalAlpha = Math.min(1, glowA * 0.45); ctx.filter = `blur(${9 * k1080}px)`; ctx.drawImage(logo, 0, 0);
    if (outA > 0) {
      ctx.globalAlpha = outA; ctx.filter = `blur(${16 * k1080}px)`; ctx.drawImage(fx, 0, 0); ctx.drawImage(fx, 0, 0);
      ctx.filter = `blur(${5 * k1080}px)`; ctx.drawImage(fx, 0, 0);
    }
    ctx.restore();
    ctx.drawImage(logo, 0, 0);
    if (outA > 0) { ctx.save(); ctx.globalAlpha = outA * (1 - fillA * 0.6); ctx.globalCompositeOperation = 'lighter'; ctx.drawImage(fx, 0, 0); ctx.restore(); }
    if (!transparent && flash > 0.01) {
      const r = ctx.createRadialGradient(mx, my, 0, mx, my, Math.max(L.box.w, L.box.h) * 0.8);
      r.addColorStop(0, `rgba(220,255,245,${0.32 * flash})`); r.addColorStop(1, 'rgba(220,255,245,0)');
      ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = r; ctx.fillRect(0, 0, W, H); ctx.restore();
    }
  }

  const pm = E.panOf(mx);
  const events = [
    { type: 'hum', t0: 0.1, t1: 5, level: 0.006, boostAt: T.ignite },
    { type: 'crackle', t0: 0.15, t1: 1.3, pan: pm },
    { type: 'glide', t0: 0.15, t1: 1.25, f0: 180, f1: 360, gain: 0.022, pan: pm },
    { type: 'zap', t: T.ignite - 0.02, gain: 0.16, dur: 0.16, fc: 2600, pan: pm },
    { type: 'sub', t: T.ignite, gain: 0.2, f0: 95, f1: 45, tau: 0.5, pan: pm * 0.75 },
    { type: 'whoosh', t0: T.ignite - 0.25, tp: T.ignite, t1: T.ignite + 0.6, gain: 0.05, fa: 300, fb: 2200, fc: 600, p0: pm, p1: pm, seed: 19 },
    { type: 'pad', t0: 1.4, mood: 'dark', gain: 0.018, attack: 1.2 },
  ];
  letters.forEach((p, i) => {
    let prev = 0;
    for (const [ts, lv] of flick[i]) {
      if (lv > prev + 0.3) events.push({ type: 'zap', t: ts, gain: 0.05 * lv, dur: 0.035, fc: 3000 + i * 150, pan: E.panOf(L.toFrame(p.cx, p.cy)[0]) });
      prev = lv;
    }
  });
  stutter.forEach(([ts, lv]) => { if (lv >= 1) events.push({ type: 'zap', t: ts, gain: 0.09, dur: 0.05, fc: 2800, pan: pm }); });
  events.push(
    { type: 'whoosh', t0: T.gloss[0], tp: T.gloss[0] + 0.3, t1: T.gloss[1], gain: 0.03, fa: 1400, fb: 5200, fc: 2600, q: 1.3, body: 0.2, p0: -0.4, p1: 0.4, seed: 29 },
    { type: 'shimmer', t: T.chime - 0.24 },
    { type: 'chime', t: T.chime },
  );
  return { render, events, times: { ...T, fadeFrom: 4.5 } };
}
