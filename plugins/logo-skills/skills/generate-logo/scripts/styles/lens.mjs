// lens: a magnifying glass glides across an empty page and the logo can only be seen, magnified, through it.
// Over the main shape it magnifies further, then the camera zooms out while the view opens up around it.
import * as E from '../engine.mjs';

function buildPath(pts) {
  const P = [pts[0], ...pts, pts[pts.length - 1]], samples = [];
  for (let i = 1; i < P.length - 2; i++) {
    const [p0, p1, p2, p3] = [P[i - 1], P[i], P[i + 1], P[i + 2]];
    for (let k = 0; k < 120; k++) {
      const u = k / 120, u2 = u * u, u3 = u2 * u;
      const f = (a, b, c, d) => 0.5 * (2 * b + (-a + c) * u + (2 * a - 5 * b + 4 * c - d) * u2 + (-a + 3 * b - 3 * c + d) * u3);
      samples.push([f(p0[0], p1[0], p2[0], p3[0]), f(p0[1], p1[1], p2[1], p3[1])]);
    }
  }
  samples.push(pts[pts.length - 1]);
  const len = [0];
  for (let i = 1; i < samples.length; i++) len.push(len[i - 1] + Math.hypot(samples[i][0] - samples[i - 1][0], samples[i][1] - samples[i - 1][1]));
  const Ln = len[len.length - 1];
  return s => {
    const d = E.clamp(s) * Ln;
    let lo = 0, hi = len.length - 1;
    while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (len[mid] < d) lo = mid; else hi = mid; }
    const f = (d - len[lo]) / Math.max(1e-6, len[hi] - len[lo]);
    return [E.lerp(samples[lo][0], samples[hi][0], f), E.lerp(samples[lo][1], samples[hi][1], f)];
  };
}

export async function setup(ctx) {
  const L = E.L, W = E.W, H = E.H, theme = E.CFG.theme, k1080 = Math.min(W, H) / 1080;
  const T = { travel: [0.15, 2.0], lock: [1.65, 2.05], reveal: [2.08, 2.95], open: [2.08, 2.6], fadeLens: [2.1, 2.42], ping: 2.08, gloss: [3.05, 3.7], chime: 3.3, hold: 3.45 };
  E.field(L.main);
  const [fx, fy] = L.toFrame(L.main.deep.x, L.main.deep.y);
  const b = L.box;
  const path = buildPath([
    [W + 260 * k1080, b.y1 + 120 * k1080],
    [b.x1 - b.w * 0.12, E.CY + b.h * 0.12],
    [E.CX + b.w * 0.08, b.y0 + b.h * 0.22],
    [b.x0 + b.w * 0.22, E.CY + b.h * 0.18],
    [fx, fy],
  ]);
  const easeTravel = E.bezier(0.42, 0, 0.18, 1);
  const lensAt = t => path(easeTravel(E.prog(t, T.travel)));
  // lens: the darkest saturated logo colour on light pages, white-ish on dark ones
  const sat = c => (Math.max(...c) - Math.min(...c)) / 255;
  const lensCol = theme === 'dark' ? [235, 245, 245]
    : E.mix(L.palette.slice().sort((a, c) => (E.lum(a) - sat(a) * 0.4) - (E.lum(c) - sat(c) * 0.4))[0], [0, 0, 0], 0.1);
  const RO = 146 * k1080, RW = RO * 0.376, RI = RO - RW, RM = RO - RW / 2, HANDLE = RO * 1.7;
  const MAG = 1.45, BIG = 2.4;

  // magnified views draw from a 2x copy of the laid-out logo; the last frames use the 1x copy (exact pixels)
  const big2 = E.canvas(W * 2, H * 2), g2 = big2.getContext('2d');
  g2.imageSmoothingQuality = 'high'; g2.scale(2, 2); E.logoSpace(g2); g2.drawImage(L.canvas, 0, 0);
  const exact1 = E.canvas(W, H), g1 = exact1.getContext('2d');
  g1.imageSmoothingQuality = 'high'; E.logoSpace(g1); g1.drawImage(L.canvas, 0, 0);
  const lg = E.canvas(W, H).getContext('2d');

  function drawLens(g, x, y, s, tilt, alpha) {
    g.save();
    g.globalAlpha = alpha;
    g.translate(x, y); g.rotate(tilt); g.scale(s, s);
    const gr = g.createRadialGradient(-RI * 0.4, -RI * 0.45, 0, -RI * 0.4, -RI * 0.45, RI * 1.3);
    gr.addColorStop(0, 'rgba(255,255,255,0.38)'); gr.addColorStop(0.5, 'rgba(255,255,255,0.06)'); gr.addColorStop(1, E.rgba(lensCol, 0.12));
    g.fillStyle = gr; g.beginPath(); g.arc(0, 0, RI, 0, Math.PI * 2); g.fill();
    g.strokeStyle = E.rgb(lensCol); g.lineCap = 'round';
    const a = Math.PI * 3 / 4;
    g.lineWidth = RW;
    g.beginPath(); g.moveTo(Math.cos(a) * RO, Math.sin(a) * RO); g.lineTo(Math.cos(a) * (RO + HANDLE), Math.sin(a) * (RO + HANDLE)); g.stroke();
    g.beginPath(); g.arc(0, 0, RM, 0, Math.PI * 2); g.stroke();
    g.strokeStyle = 'rgba(255,255,255,0.5)'; g.lineWidth = RW * 0.17;
    g.beginPath(); g.arc(0, 0, RM + RW * 0.12, Math.PI * 1.08, Math.PI * 1.42); g.stroke();
    g.restore();
  }

  function render(t, transparent) {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, W, H);
    if (!transparent) E.paintBg(ctx, t, theme);
    const push = E.pushIn(t, T.hold);
    const [x, y] = lensAt(t);
    const vx = (lensAt(t + 1 / 120)[0] - lensAt(t - 1 / 120)[0]) * 60;
    const tilt = E.clamp(vx / 2600, -0.35, 0.35);
    const zoom = E.lerp(BIG, 1, E.easeInOut(E.prog(t, T.reveal)));
    const mag = t < T.reveal[0] ? E.lerp(MAG, BIG, E.easeInOut(E.prog(t, T.lock))) : zoom;
    const open = E.easeOut(E.prog(t, T.open));
    const lensScale = t < T.reveal[0] ? 1 : zoom / BIG;
    const R = E.lerp(RI * lensScale, Math.hypot(W, H), open);
    const exact = E.smooth((t - T.reveal[1] + 0.08) / 0.08);
    const lensA = t < T.travel[0] ? 0 : 1 - E.smooth(E.prog(t, T.fadeLens));

    lg.setTransform(1, 0, 0, 1, 0, 0);
    lg.clearRect(0, 0, W, H);
    lg.imageSmoothingEnabled = true; lg.imageSmoothingQuality = 'high';
    if (t >= T.travel[0]) {
      lg.save();
      E.applyPush(lg, push);
      if (open < 1) { lg.beginPath(); lg.arc(x, y, R, 0, Math.PI * 2); lg.clip(); }
      lg.translate(x, y); lg.scale(mag, mag); lg.translate(-x, -y);
      if (exact < 1) lg.drawImage(big2, 0, 0, W, H);
      if (exact > 0) { lg.globalAlpha = exact; lg.drawImage(exact1, 0, 0); }
      lg.restore();
    }
    if (lensA > 0) drawLens(lg, x, y, lensScale, tilt * (1 - open), lensA);
    E.gloss(lg, t, T.gloss);
    ctx.save(); E.applyPush(ctx, push);
    E.ripple(ctx, x, y, t, T.ping, { r0: RO * 0.5, r1: Math.max(b.w, b.h) * 0.9, dur: 1.3, color: lensCol, a: transparent ? 0.2 : 0.28 });
    E.ripple(ctx, x, y, t, T.ping + 0.15, { r0: RO * 0.5, r1: Math.max(b.w, b.h) * 0.7, dur: 1.1, color: L.palette[0], a: transparent ? 0.14 : 0.2, lw: 2 });
    ctx.restore();
    if (!transparent && theme !== 'dark') E.shadowPass(ctx, lg.canvas, 1);
    ctx.drawImage(lg.canvas, 0, 0);
  }

  const pf = E.panOf(fx);
  const events = [
    { type: 'pad', t0: 0.2, mood: 'calm', gain: 0.02, attack: 1.6 },
    { type: 'whoosh', t0: T.travel[0], tp: 0.95, t1: T.travel[1] + 0.05, gain: 0.06, fa: 220, fb: 1300, fc: 380, q: 1.1, p0: 0.8, p1: pf, seed: 49 },
    ...[1318.51, 1661.22, 1975.53, 2489.02, 2637.02].map((f, i) => ({ type: 'tone', t: 0.82 + i * 0.13, f, gain: 0.022, tau: 0.4, pan: 0.45 - i * 0.2 })),
    { type: 'glide', t0: T.lock[0], t1: T.lock[1], f0: 420, f1: 840, gain: 0.03, pan: pf },
    { type: 'ping', t: T.ping, pan: pf },
    { type: 'whoosh', t0: T.reveal[0], tp: T.reveal[0] + 0.3, t1: T.reveal[1] + 0.15, gain: 0.085, fa: 240, fb: 1500, fc: 380, q: 1.0, body: 2.4, p0: pf, p1: pf + 0.3, seed: 59 },
    { type: 'glide', t0: T.reveal[0], t1: T.reveal[1], f0: 330, f1: 495, gain: 0.025 },
    { type: 'whoosh', t0: T.gloss[0], tp: T.gloss[0] + 0.3, t1: T.gloss[1], gain: 0.03, fa: 1400, fb: 5200, fc: 2600, q: 1.3, body: 0.2, p0: -0.4, p1: 0.4, seed: 69 },
    { type: 'shimmer', t: T.chime - 0.24 },
    { type: 'chime', t: T.chime },
  ];
  return { render, events, times: { ...T, fadeFrom: 4.5 } };
}
