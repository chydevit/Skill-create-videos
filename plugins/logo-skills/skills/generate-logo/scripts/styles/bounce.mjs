// bounce: the big shapes tumble down (or roll in from the side) and bounce into place like plastic on a counter,
// a confetti pop in the logo's colours, then smaller shapes and letters drop in one by one and bounce.
import * as E from '../engine.mjs';

export async function setup(ctx) {
  const L = E.L, W = E.W, H = E.H, theme = E.CFG.theme, k1080 = Math.min(W, H) / 1080;
  const maxA = L.main.area;
  const big = L.parts.filter(p => !p.text && p.area >= maxA * 0.2);
  const small = L.reading.filter(p => !big.includes(p));
  const fr = p => { const [x0, y0] = L.toFrame(p.rx, p.ry); return { x0, y0, w: p.w * L.S, h: p.h * L.S, bot: L.toFrame(0, p.y1)[1], cx: L.toFrame(p.cx, 0)[0] }; };

  const DUR_BIG = 0.95, DUR_SMALL = 0.75;
  big.forEach((p, i) => {
    p.f = fr(p);
    p.start = 0.1 + i * Math.min(0.35, 0.8 / big.length);
    p.mode = i % 2 === 1 ? 'roll' : 'drop';
    p.win = [p.start, p.start + DUR_BIG];
    p.dy0 = -(p.f.bot + 40);
    p.dx0 = W - p.f.x0 + 40;                           // rolls in from just off the right edge
  });
  const bigEnd = big.length ? Math.max(...big.map(p => p.win[1])) : 0.1;
  const gap = small.length ? Math.min(0.07, 0.9 / small.length) : 0;
  small.forEach((p, j) => {
    p.f = fr(p);
    p.start = (big.length ? big[big.length - 1].start + 0.7 : 0.15) + j * gap;
    p.win = [p.start, p.start + DUR_SMALL];
    p.dy0 = -(p.f.bot + 40);
  });
  const end = Math.max(bigEnd, ...small.map(p => p.win[1]));
  const T = { confetti: bigEnd + 0.02, gloss: [Math.max(2.2, end + 0.2), Math.max(2.2, end + 0.2) + 0.65] };
  T.chime = T.gloss[0] + 0.25; T.hold = T.gloss[0] + 0.45;
  const backRoll = (p, t) => p.dx0 * (1 - E.back(E.prog(t, p.win), 0.6));
  big.filter(p => p.mode === 'roll').forEach(p => { p.arrive = p.win[1]; for (let t = p.win[0]; t < p.win[1]; t += 0.002) if (backRoll(p, t) <= 0) { p.arrive = t; break; } });

  const [ccx, ccy] = L.toFrame(L.main.cx, L.main.cy);
  const rnd = E.mulberry32(5);
  const confetti = Array.from({ length: 18 }, (_, i) => ({
    a: (i / 18) * Math.PI * 2 + rnd() * 0.3, dist: (140 + rnd() * 170) * k1080, s: (5 + rnd() * 5) * k1080,
    c: L.palette[i % L.palette.length], spin: (rnd() - 0.5) * 10, round: rnd() < 0.4,
  }));
  const lg = E.canvas(W, H).getContext('2d');

  function drawPart(p, t, push) {
    if (t < p.start) return;
    const u = E.prog(t, p.win), f = p.f, pivotX = f.x0 + f.w / 2;
    lg.save();
    E.applyPush(lg, push);
    if (p.mode === 'roll') {
      const dx = backRoll(p, t), rot = dx / (f.h * 0.5);
      const sq = E.spring(t, p.arrive, 0.06, 4, 12);
      lg.translate(pivotX + dx, f.y0 + f.h / 2); lg.rotate(rot); lg.scale(1 - sq, 1 + sq); lg.translate(-pivotX, -(f.y0 + f.h / 2));
    } else {
      const d = p.win[1] - p.win[0];
      const dy = p.dy0 * (1 - E.bounceOut(u));
      const rot = (big.includes(p) ? -2.4 : (p.id % 2 ? 0.4 : -0.4)) * (1 - E.easeOut(E.clamp(u / E.BOUNCE_HITS[0])));
      const amp = big.includes(p) ? 0.16 : 0.2;
      const sq = E.BOUNCE_HITS.slice(0, 3).reduce((s, h, k) => s + E.spring(t, p.start + h * d, amp / (1 + k * 1.5), 4.5, 15), 0);
      lg.translate(pivotX, p.f.bot + dy); lg.rotate(rot); lg.scale(1 + sq * 0.8, 1 - sq); lg.translate(-pivotX, -p.f.bot);
    }
    lg.drawImage(p.sprite, f.x0, f.y0, f.w, f.h);
    lg.restore();
  }

  function render(t, transparent) {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, W, H);
    if (!transparent) E.paintBg(ctx, t, theme);
    const push = E.pushIn(t, T.hold);
    lg.setTransform(1, 0, 0, 1, 0, 0);
    lg.clearRect(0, 0, W, H);
    lg.imageSmoothingEnabled = true; lg.imageSmoothingQuality = 'high';
    // big shapes: rolled ones underneath the dropped ones
    big.filter(p => p.mode === 'roll').forEach(p => drawPart(p, t, push));
    big.filter(p => p.mode === 'drop').forEach(p => drawPart(p, t, push));
    small.forEach(p => drawPart(p, t, push));
    E.gloss(lg, t, T.gloss);
    const cu = (t - T.confetti) / 0.75;
    if (cu > 0 && cu < 1) {
      lg.save(); E.applyPush(lg, push);
      for (const p of confetti) {
        const d = E.easeOut(cu) * p.dist, x = ccx + Math.cos(p.a) * d, y = ccy + Math.sin(p.a) * d + 70 * k1080 * cu * cu;
        lg.globalAlpha = 1 - E.smooth((cu - 0.45) / 0.55);
        lg.fillStyle = E.rgb(p.c);
        lg.save(); lg.translate(x, y); lg.rotate(p.spin * cu);
        lg.beginPath();
        if (p.round) lg.arc(0, 0, p.s, 0, Math.PI * 2); else lg.roundRect(-p.s * 1.6, -p.s * 0.7, p.s * 3.2, p.s * 1.4, p.s * 0.7);
        lg.fill(); lg.restore();
      }
      lg.restore();
    }
    if (!transparent && theme !== 'dark') E.shadowPass(ctx, lg.canvas, 1);
    ctx.drawImage(lg.canvas, 0, 0);
  }

  const events = [{ type: 'pad', t0: 0.3, mood: 'bright', gain: 0.02 }];
  big.forEach((p, i) => {
    const pan = E.panOf(p.f.cx), d = p.win[1] - p.win[0];
    if (p.mode === 'drop') {
      events.push({ type: 'glide', t0: p.start, t1: p.start + E.BOUNCE_HITS[0] * d, f0: 1300, f1: 620, gain: 0.018, pan });
      [0.32, 0.18, 0.1, 0.04].forEach((g, k) => events.push({ type: 'tock', t: p.start + E.BOUNCE_HITS[k] * d, gain: g, pan }));
      events.push({ type: 'plop', t: p.start + E.BOUNCE_HITS[0] * d, gain: 0.12, f0: 180, f1: 320, tau: 0.06, pan });
    } else {
      let last = Math.floor(backRoll(p, p.win[0]) / (p.f.h * 0.5) / Math.PI);
      for (let t = p.win[0]; t < p.arrive; t += 0.001) {
        const k = Math.floor(backRoll(p, t) / (p.f.h * 0.5) / Math.PI);
        if (k !== last) { events.push({ type: 'click', t, gain: 0.05 + 0.04 * ((k * 7) % 5) / 5, fc: 2600 + (k % 3) * 300, bodyHz: 380, decay: 0.012, bodyGain: 0.6, pan: E.clamp(pan + backRoll(p, t) / W, -0.4, 0.8) }); last = k; }
      }
      events.push({ type: 'tock', t: p.arrive, gain: 0.28, bodyHz: 300, pan }, { type: 'sub', t: p.arrive, gain: 0.14, f0: 90, f1: 50, tau: 0.3, pan });
    }
  });
  events.push({ type: 'plop', t: T.confetti, gain: 0.2, f0: 300, f1: 950, pan: E.panOf(ccx) }, { type: 'sparkle', t: T.confetti + 0.08, pan: E.panOf(ccx) });
  small.forEach((p, j) => {
    const d = p.win[1] - p.win[0], pan = E.panOf(p.f.cx);
    events.push({ type: 'plop', t: p.start + E.BOUNCE_HITS[0] * d, gain: 0.08, f0: 420 + (j % 12) * 45, f1: 900 + (j % 12) * 80, rise: 0.025, tau: 0.035, pan },
      { type: 'click', t: p.start + E.BOUNCE_HITS[1] * d, gain: 0.03, fc: 3600, bodyHz: 500, bodyGain: 0.4, pan });
  });
  events.push(
    { type: 'whoosh', t0: T.gloss[0], tp: T.gloss[0] + 0.3, t1: T.gloss[1], gain: 0.03, fa: 1400, fb: 5200, fc: 2600, q: 1.3, body: 0.2, p0: -0.4, p1: 0.4, seed: 39 },
    { type: 'shimmer', t: T.chime - 0.24 },
    { type: 'chime', t: T.chime },
  );
  return { render, events, times: { ...T, fadeFrom: 4.5 } };
}
