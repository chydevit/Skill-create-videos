// rise: a hairline in the logo's colours draws across, opens into a band, and the shapes rise into it one by one
// (left to right) from a soft blur. Calm, corporate; works for any logo.
import * as E from '../engine.mjs';

export async function setup(ctx) {
  const L = E.L, W = E.W, H = E.H, theme = E.CFG.theme, k1080 = Math.min(W, H) / 1080;
  const parts = L.parts.slice().sort((a, b) => a.x0 - b.x0 || a.y0 - b.y0);
  const n = parts.length, gap = Math.min(0.07, 0.75 / n);
  const T = { line: [0.25, 0.95], open: [0.95, 1.85] };
  parts.forEach((p, i) => { p.win = [1.0 + i * gap, 1.0 + i * gap + 0.8]; });
  const end = Math.max(...parts.map(p => p.win[1]));
  T.gloss = [Math.max(2.35, end + 0.15), Math.max(2.35, end + 0.15) + 0.65];
  T.chime = T.gloss[0] + 0.3; T.hold = T.gloss[0] + 0.6;
  const b = L.box, half = b.h / 2 + 30 * k1080, rise = Math.min(0.14 * b.h, 90 * k1080);
  const c1 = L.palette[0], c2 = L.palette[1] || L.palette[0];
  const lg = E.canvas(W, H).getContext('2d');

  function render(t, transparent) {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, W, H);
    if (!transparent) E.paintBg(ctx, t, theme);
    const push = E.pushIn(t, T.hold);
    const lp = E.easeInOut(E.prog(t, T.line)), op = E.easeInOut(E.prog(t, T.open));
    const lineA = 1 - E.smooth(E.prog(t, [T.open[0] + 0.45, T.open[1] + 0.1]));

    lg.setTransform(1, 0, 0, 1, 0, 0);
    lg.clearRect(0, 0, W, H);
    lg.imageSmoothingEnabled = true; lg.imageSmoothingQuality = 'high';
    lg.save();
    E.applyPush(lg, push);
    if (op < 1) { lg.beginPath(); lg.rect(0, E.CY - half * op, W, 2 * half * op); lg.clip(); }
    for (const p of parts) {
      const u = E.prog(t, p.win);
      if (u <= 0) continue;
      const e = E.easeOut(u), [x0, y0] = L.toFrame(p.rx, p.ry);
      lg.save();
      lg.globalAlpha = E.smooth(u / 0.45);
      if (n <= 14 && u < 0.6) lg.filter = `blur(${(7 * (1 - u / 0.6) * k1080).toFixed(2)}px)`;
      const s = E.lerp(0.96, 1, e), cx = x0 + p.w * L.S / 2, cy = y0 + p.h * L.S / 2;
      lg.translate(cx, cy + rise * (1 - e)); lg.scale(s, s); lg.translate(-cx, -cy);
      lg.drawImage(p.sprite, x0, y0, p.w * L.S, p.h * L.S);
      lg.restore();
    }
    lg.restore();
    E.gloss(lg, t, T.gloss);

    if (!transparent && theme !== 'dark') E.shadowPass(ctx, lg.canvas, E.smooth(E.prog(t, [1.1, 2.2])));
    ctx.drawImage(lg.canvas, 0, 0);

    // the hairline, then the two edges of the opening band
    if (lp > 0 && lineA > 0) {
      ctx.save();
      E.applyPush(ctx, push);
      const hw = (b.w / 2 + 40 * k1080) * lp;
      const gr = ctx.createLinearGradient(E.CX - hw, 0, E.CX + hw, 0);
      gr.addColorStop(0, E.rgba(c1, 0)); gr.addColorStop(0.2, E.rgb(c1)); gr.addColorStop(0.8, E.rgb(c2)); gr.addColorStop(1, E.rgba(c2, 0));
      ctx.strokeStyle = gr; ctx.lineWidth = 3 * k1080; ctx.globalAlpha = lineA;
      ctx.shadowColor = E.rgba(c1, 0.6); ctx.shadowBlur = 12 * k1080;
      for (const dir of op > 0 ? [-1, 1] : [0]) {
        const y = E.CY + dir * half * op;
        ctx.beginPath(); ctx.moveTo(E.CX - hw, y); ctx.lineTo(E.CX + hw, y); ctx.stroke();
      }
      ctx.restore();
    }
  }

  const events = [
    { type: 'pad', t0: 0.2, mood: 'warm', gain: 0.02, attack: 1.8 },
    { type: 'glide', t0: T.line[0], t1: T.line[1], f0: 330, f1: 495, gain: 0.045 },
    { type: 'click', t: T.open[0] - 0.02, gain: 0.16, fc: 5200, bodyGain: 0.2 },
    { type: 'sub', t: T.open[0], gain: 0.16, f0: 90, f1: 46, tau: 0.5 },
    { type: 'whoosh', t0: T.open[0] - 0.05, tp: T.open[0] + 0.35, t1: T.open[1] + 0.2, gain: 0.08, fa: 400, fb: 2400, fc: 800, seed: 81 },
  ];
  if (n <= 14) parts.forEach((p, i) => events.push({ type: 'click', t: p.win[0] + 0.05, gain: 0.05, fc: 4400 + (i % 4) * 300, bodyGain: 0.15, pan: E.panOf(L.toFrame(p.cx, 0)[0]) }));
  events.push(
    { type: 'whoosh', t0: T.gloss[0], tp: T.gloss[0] + 0.3, t1: T.gloss[1], gain: 0.03, fa: 1400, fb: 5200, fc: 2600, q: 1.3, body: 0.2, p0: -0.4, p1: 0.4, seed: 91 },
    { type: 'shimmer', t: T.chime - 0.24 },
    { type: 'chime', t: T.chime },
  );
  return { render, events, times: { ...T, fadeFrom: 4.5 } };
}
