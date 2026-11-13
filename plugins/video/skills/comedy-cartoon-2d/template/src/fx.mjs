// Effects: puffs, smoke, impact bursts, sound-effect lettering, siren wash, iris.
import { W, H, C, INK, LW, TAU, paint, circle, oval, rrect, poly, text, clamp, lerp, ease, hash } from './core.mjs';

export function puff(ctx, x, y, r, col = '#fff6e6', alpha = 1, lw = 5) {
  ctx.save(); ctx.globalAlpha = alpha;
  ctx.beginPath();
  for (const [dx, dy, k] of [[-0.6, 0.2, 0.6], [0, -0.25, 0.8], [0.6, 0.15, 0.62], [0, 0.35, 0.6]]) { ctx.moveTo(x + dx * r + k * r, y + dy * r); ctx.arc(x + dx * r, y + dy * r, k * r, 0, TAU); }
  ctx.fillStyle = col; ctx.fill();
  ctx.restore();
}
// cluster of puffs that expand + fade over life (0..1)
export function dust(ctx, x, y, life, { n = 5, spread = 120, r = 40, col = '#fff1d8', dir = -1, rise = 40, seed = 1 } = {}) {
  if (life <= 0 || life >= 1) return;
  for (let i = 0; i < n; i++) {
    const a = hash(seed * 13 + i) * 1.6 - 0.8, d = ease.out(life) * spread * (0.5 + hash(seed + i * 7) * 0.7);
    const px = x + dir * d * Math.cos(a), py = y - ease.out(life) * rise * (0.5 + hash(i + seed * 3)) + Math.sin(a) * d * 0.3;
    puff(ctx, px, py, r * (0.6 + life * 0.8) * (0.7 + hash(i * 3 + seed) * 0.6), col, (1 - life) * 0.95);
  }
}
export function exhaust(ctx, x, y, t, { rate = 3, col = '#d9d2c8', dark = false, dir = -1, n = 4, speed = 1 } = {}) {
  for (let i = 0; i < n; i++) {
    const k = ((t * rate + i / n) % 1);
    puff(ctx, x + dir * k * 120 * speed, y - k * 40, 10 + k * 26, dark ? '#4a4450' : col, (1 - k) * 0.85);
  }
}
// spiky impact star with optional word
export function impact(ctx, x, y, r, life, { col = C.yellow, word = null, size = 90, rot = -0.1, wcol = C.red } = {}) {
  if (life < 0 || life > 1) return;
  const s = life < 0.15 ? ease.back(life / 0.15) : 1 - ease.in((life - 0.15) / 0.85) * 0.15;
  const a = life > 0.75 ? 1 - (life - 0.75) / 0.25 : 1;
  ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  ctx.beginPath(); const n = 14;
  for (let i = 0; i < n * 2; i++) { const ang = i * Math.PI / n, rr = i % 2 ? r * 0.55 : r * (0.85 + hash(i) * 0.3); ctx.lineTo(Math.cos(ang) * rr, Math.sin(ang) * rr); }
  ctx.closePath(); paint(ctx, col, LW);
  if (word) text(ctx, word, 0, 4, { size, fill: wcol, lw: 12, font: 'Impact' });
  ctx.restore();
}
// cartoon sound-effect lettering popping in
export function sfxText(ctx, word, x, y, life, { size = 110, fill = C.yellow, rot = -0.12, wob = 0, font = 'Impact' } = {}) {
  if (life < 0 || life > 1) return;
  const s = life < 0.2 ? ease.back(life / 0.2) : 1 + Math.sin(life * 30) * 0.02 * wob;
  const a = life > 0.8 ? 1 - (life - 0.8) / 0.2 : 1;
  ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  text(ctx, word, 6, 8, { size, fill: INK, lw: 14, font });
  text(ctx, word, 0, 0, { size, fill, lw: 12, font });
  ctx.restore();
}
// motion lines trailing an object (screen-space, horizontal)
export function speedStreaks(ctx, x, y, len, h, t, { n = 6, col = '#fff', dir = -1, alpha = 0.8, lw = 6 } = {}) {
  ctx.save(); ctx.globalAlpha = alpha; ctx.strokeStyle = col; ctx.lineCap = 'round'; ctx.lineWidth = lw;
  for (let i = 0; i < n; i++) {
    const yy = y - h / 2 + (i + 0.5) * h / n + Math.sin(i * 7.3) * 8;
    const l = len * (0.4 + hash(i * 3 + Math.floor(t * 12)) * 0.6);
    const off = hash(i * 5 + 1) * 40;
    ctx.beginPath(); ctx.moveTo(x + dir * off, yy); ctx.lineTo(x + dir * (off + l), yy); ctx.stroke();
  }
  ctx.restore();
}
// red/blue siren wash on frame edges
export function sirenWash(ctx, t, amt = 1, rate = 3.2) {
  if (amt <= 0) return;
  const ph = Math.floor(t * rate * 2) % 2;
  const side = (x0, col) => { const g = ctx.createRadialGradient(x0, H / 2, 50, x0, H / 2, 1100); g.addColorStop(0, col); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); };
  ctx.save(); ctx.globalAlpha = 0.42 * amt; ctx.globalCompositeOperation = 'source-over';
  if (ph) side(-200, 'rgba(232,40,40,0.9)'); else side(W + 200, 'rgba(40,90,255,0.9)');
  ctx.restore();
}
export function iris(ctx, cx, cy, r) {
  ctx.save(); ctx.beginPath(); ctx.rect(-10, -10, W + 20, H + 20); ctx.arc(cx, cy, Math.max(0, r), 0, TAU, true); ctx.fillStyle = '#0d0a10'; ctx.fill('evenodd');
  ctx.restore();
}
// flash frame / colour wash
export function wash(ctx, col, a) { if (a <= 0) return; ctx.save(); ctx.globalAlpha = clamp(a); ctx.fillStyle = col; ctx.fillRect(0, 0, W, H); ctx.restore(); }
export function vignette(ctx, a = 0.25) {
  const g = ctx.createRadialGradient(W / 2, H / 2, H * 0.45, W / 2, H / 2, H * 1.05);
  g.addColorStop(0, 'rgba(40,10,30,0)'); g.addColorStop(1, `rgba(40,10,30,${a})`);
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}
// small "worry" stress marks / emanata
export function stressMarks(ctx, x, y, s = 1, t = 0) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const k = 1 + Math.sin(t * 20) * 0.08; ctx.scale(k, k);
  ctx.beginPath(); ctx.moveTo(-14, -14); ctx.lineTo(-4, -4); ctx.moveTo(14, -14); ctx.lineTo(4, -4); ctx.moveTo(-14, 14); ctx.lineTo(-4, 4); ctx.moveTo(14, 14); ctx.lineTo(4, 4); paint(ctx, null, 6, C.red);
  ctx.restore();
}
export function zzz(ctx, x, y, t) { for (let i = 0; i < 3; i++) { const k = (t * 0.7 + i / 3) % 1; ctx.save(); ctx.globalAlpha = 1 - k; text(ctx, 'z', x + k * 40 + i * 6, y - k * 80, { size: 30 + i * 8, font: 'Arial Black', fill: '#fff', lw: 6 }); ctx.restore(); } }
export function musicNote(ctx, x, y, s = 1) { ctx.save(); ctx.translate(x, y); ctx.scale(s, s); oval(ctx, 0, 0, 12, 9, -0.4); paint(ctx, INK, 0); ctx.beginPath(); ctx.moveTo(10, -4); ctx.lineTo(10, -46); ctx.lineTo(28, -38); paint(ctx, null, 5); ctx.restore(); }
// letterbox-free film grain-ish texture? keep it flat. Paper-ish speckle for warmth
export function grain(ctx, t, a = 0.035) {
  ctx.save(); ctx.globalAlpha = a; ctx.fillStyle = '#000';
  const f = Math.floor(t * 12);
  for (let i = 0; i < 260; i++) { const x = hash(i * 1.37 + f * 3.1) * W, y = hash(i * 2.11 + f * 1.7) * H; ctx.fillRect(x, y, 2, 2); }
  ctx.restore();
}
