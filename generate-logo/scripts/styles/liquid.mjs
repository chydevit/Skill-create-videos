// liquid: a drop falls onto the page and spreads into the biggest shape; every other shape squeezes out
// as a bead from the nearest edge and takes its form. Ends on the logo's exact pixels.
import * as E from '../engine.mjs';

const easeSpread = E.bezier(0.3, 0.1, 0.12, 1);
const easeFall = E.bezier(0.55, 0, 0.9, 0.55);

// Point on part p's edge nearest to (x, y), in logo px.
function contactPoint(p, x, y) {
  let best = null, bd = Infinity;
  for (let yy = 1; yy < p.h - 1; yy += 2) for (let xx = 1; xx < p.w - 1; xx += 2) {
    const i = yy * p.w + xx;
    if (p.A[i] < 0.5 || (p.A[i - 1] >= 0.5 && p.A[i + 1] >= 0.5 && p.A[i - p.w] >= 0.5 && p.A[i + p.w] >= 0.5)) continue;
    const d = Math.hypot(xx + p.rx - x, yy + p.ry - y);
    if (d < bd) { bd = d; best = { x: xx + p.rx, y: yy + p.ry }; }
  }
  return best || { x: p.cx, y: p.cy };
}

export async function setup(ctx) {
  const L = E.L, W = E.W, H = E.H, theme = E.CFG.theme, res = L.res;
  const main = E.field(L.main);
  const others = L.parts.slice(1);
  others.sort((a, b) => (a.text === b.text ? 0 : a.text ? 1 : -1) || (a.text ? a.x0 - b.x0 : Math.hypot(a.cx - main.cx, a.cy - main.cy) - Math.hypot(b.cx - main.cx, b.cy - main.cy)));
  const n = others.length;
  const T = { fall: [0.12, 0.5], land: 0.5, spread: [0.54, 1.42] };
  const gap = n ? Math.min(0.12, 0.9 / n) : 0, dur = n > 3 ? 0.5 : 0.7, k = dur / 0.7;
  others.forEach((p, j) => {
    E.field(p);
    p.sq = [1.3 + j * gap, 1.3 + j * gap + dur];
    p.contact = contactPoint(p, main.cx, main.cy);
  });
  const lastEnd = n ? others[n - 1].sq[1] : T.spread[1];
  T.gloss = [Math.max(2.2, lastEnd + 0.15), Math.max(2.2, lastEnd + 0.15) + 0.75];
  T.chime = T.gloss[0] + 0.38; T.hold = T.gloss[1];

  const drop = { x: main.cx, y: main.cy };
  const r0 = 0.56 * main.deep.d, r1 = 0.8 * main.deep.d;
  const lg = E.canvas(W, H).getContext('2d');
  const [fx, fy] = L.toFrame(drop.x, drop.y);
  const colA = E.mainColour(main), k1080 = Math.min(W, H) / 1080;

  function render(t, transparent) {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, W, H);
    if (!transparent) E.paintBg(ctx, t, theme);
    const push = E.pushIn(t, T.hold);
    const big = Math.max(L.box.w, L.box.h);
    ctx.save(); E.applyPush(ctx, push);
    E.ripple(ctx, fx, fy, t, T.land, { r0: 40 * k1080, r1: big, color: colA, a: transparent ? 0.22 : 0.3 });
    E.ripple(ctx, fx, fy, t, T.land + 0.16, { r0: 40 * k1080, r1: big * 0.78, color: colA, a: transparent ? 0.14 : 0.2, lw: 2 });
    for (const p of others) if (!p.text) {
      const [ox, oy] = L.toFrame(p.cx, p.cy);
      E.ripple(ctx, ox, oy, t, p.sq[1] - 0.08, { r0: 30 * k1080, r1: Math.max(p.bw, p.bh) * L.S * 1.3, dur: 0.9, color: E.mix(L.palette[1] || colA, [0, 0, 0], 0), a: transparent ? 0.16 : 0.22, lw: 2 });
    }
    ctx.restore();

    lg.setTransform(1, 0, 0, 1, 0, 0);
    lg.clearRect(0, 0, W, H);
    lg.imageSmoothingEnabled = true; lg.imageSmoothingQuality = 'high';

    if (t >= T.fall[0]) {
      const fall = easeFall(E.prog(t, [T.fall[0], T.land]));
      const spread = easeSpread(E.prog(t, [T.spread[0], T.spread[1] - 0.1]));
      const exact = E.smooth(E.prog(t, [T.spread[1] - 0.1, T.spread[1]]));
      const r = E.lerp(r0, r1, E.easeOut(E.prog(t, [T.land - 0.02, T.spread[1]])));
      const wob = 9 * res * Math.sin(Math.PI * spread) * (1 - spread * 0.4);
      const tk = 1 - E.smooth(spread / 0.6);           // a plain drop of the main colour, then the logo's colours
      const layer = exact >= 1 ? main.sprite : E.morphPart(main, drop.x, drop.y, r, spread, wob, t, exact, colA, tk);
      const z = t < T.land ? E.lerp(3.4, 1, fall) : 1;
      const blur = t < T.land ? E.lerp(26, 0, fall) * k1080 : 0;
      const alpha = t < T.land ? E.smooth(E.prog(t, [T.fall[0], T.fall[0] + 0.22])) : 1;
      const sq = E.spring(t, T.land, 0.16, 3.6, 7.5);
      const jel = E.spring(t, T.spread[1] - 0.12, 0.03, 2.7, 5.5) + (n ? E.spring(t, others[0].sq[1] - 0.05, -0.012, 3.2, 6) : 0);
      lg.save();
      lg.globalAlpha = alpha;
      if (blur > 0.3) lg.filter = `blur(${blur.toFixed(2)}px)`;
      E.applyPush(lg, push);
      lg.translate(fx, fy); lg.scale(z * (1 + sq + jel), z * (1 - sq - jel * 0.9)); lg.translate(-fx, -fy);
      E.logoSpace(lg);
      lg.drawImage(layer, main.rx, main.ry);
      lg.restore();
      // droplet highlight while it is still a drop
      const hl = (t < T.land ? alpha : 1) * (1 - E.smooth(E.prog(t, [T.land + 0.05, T.spread[0] + 0.35])));
      if (hl > 0.01) {
        const rr = r * L.S * z, hx = fx - rr * 0.36, hy = fy - rr * 0.42;
        lg.save();
        E.applyPush(lg, push);
        lg.globalCompositeOperation = 'source-atop';
        const g = lg.createRadialGradient(hx, hy, 0, hx, hy, rr * 0.55);
        g.addColorStop(0, `rgba(255,255,255,${0.55 * hl})`); g.addColorStop(1, 'rgba(255,255,255,0)');
        lg.fillStyle = g; lg.fillRect(hx - rr, hy - rr, rr * 2, rr * 2);
        lg.restore();
      }
    }

    for (const p of others) {
      if (t < p.sq[0]) continue;
      const s0 = p.sq[0], s1 = p.sq[1];
      const exact = E.smooth(E.prog(t, [s1 - 0.08 * k, s1]));
      let layer;
      if (exact >= 1) layer = p.sprite;
      else {
        const grow = E.easeOut(E.prog(t, [s0, s0 + 0.32 * k]));
        const travel = E.easeInOut(E.prog(t, [s0 + 0.04 * k, s1 - 0.12 * k]));
        const m = easeSpread(E.prog(t, [s0 + 0.16 * k, s1 - 0.08 * k]));
        const cx = E.lerp(p.contact.x, p.deep.x, travel), cy = E.lerp(p.contact.y, p.deep.y, travel);
        layer = E.morphPart(p, cx, cy, E.lerp(2 * res, 0.85 * p.deep.d, grow), m, 5 * res * Math.sin(Math.PI * m), t, exact);
      }
      const st = E.spring(t, s1 - 0.06, p.text ? 0.05 : 0.07, 3.0, 6.5);
      const [ax, ay] = L.toFrame(p.contact.x, p.contact.y);
      const ang = Math.atan2(p.deep.y - p.contact.y, p.deep.x - p.contact.x);
      lg.save();
      E.applyPush(lg, push);
      lg.translate(ax, ay); lg.rotate(ang); lg.scale(1 + st, 1 - st * 0.6); lg.rotate(-ang); lg.translate(-ax, -ay);
      E.logoSpace(lg);
      lg.drawImage(layer, p.rx, p.ry);
      lg.restore();
    }

    E.gloss(lg, t, T.gloss);
    if (!transparent && theme !== 'dark') E.shadowPass(ctx, lg.canvas, E.smooth(E.prog(t, [T.land - 0.1, T.spread[1]])));
    ctx.drawImage(lg.canvas, 0, 0);
  }

  const pan = E.panOf(fx);
  const events = [
    { type: 'pad', t0: 0.35, mood: 'warm', gain: 0.022 },
    { type: 'whoosh', t0: 0.1, tp: 0.47, t1: 0.62, gain: 0.07, fa: 220, fb: 1500, fc: 500, q: 1.0, seed: 12, p0: pan, p1: pan },
    { type: 'plop', t: T.land, gain: 0.34, f0: 360, f1: 1080, pan },
    { type: 'sub', t: T.land, gain: 0.2, f0: 92, f1: 46, tau: 0.42, pan },
    { type: 'click', t: T.land - 0.002, gain: 0.08, fc: 5200, bodyGain: 0.1, pan },
    { type: 'whoosh', t0: 0.52, tp: 0.92, t1: 1.5, gain: 0.06, fa: 160, fb: 820, fc: 260, q: 1.2, body: 2.6, seed: 33, p0: pan, p1: pan },
    { type: 'plop', t: T.spread[1] - 0.11, gain: 0.12, f0: 240, f1: 520, rise: 0.06, tau: 0.08, pan },
  ];
  others.forEach((p, j) => {
    const pp = E.panOf(L.toFrame(p.cx, p.cy)[0]);
    if (!p.text && j < 4) events.push({ type: 'glide', t0: p.sq[0], t1: p.sq[1] - 0.08, f0: 300, f1: 760, gain: 0.03, pan: pp });
    events.push({ type: 'plop', t: p.sq[1] - 0.06, gain: p.text ? 0.07 : 0.24, f0: p.text ? 480 + j * 50 : 560, f1: p.text ? (480 + j * 50) * 2.3 : 1500, rise: p.text ? 0.03 : 0.04, tau: p.text ? 0.035 : 0.06, pan: pp });
  });
  events.push(
    { type: 'whoosh', t0: T.gloss[0] - 0.02, tp: T.gloss[0] + 0.36, t1: T.gloss[1] + 0.05, gain: 0.035, fa: 1400, fb: 5200, fc: 2600, q: 1.3, body: 0.2, p0: -0.4, p1: 0.4, seed: 57 },
    { type: 'shimmer', t: T.chime - 0.28 },
    { type: 'chime', t: T.chime },
  );
  return { render, events, times: { ...T, fadeFrom: 4.5 } };
}
