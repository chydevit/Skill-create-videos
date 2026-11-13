// Shared helpers for the Office series episodes (cast keys, the office, desks, labels, little effects).
// Episode 7's scenes live in q1..q3.mjs; a new episode adds its own scene files and imports them from shots.mjs.
import { W, H, INK, TAU, paint, circle, oval, rrect, poly, text, clamp, lerp, seg, ease, hash } from '../core.mjs';
import { talk } from '../kit.mjs';
import { lineDur, LINES } from '../vox.mjs';
import { person, anchors, CAST, chair, chairBack } from '../people.mjs';
import { drop } from '../chars.mjs';
import * as pl from '../places.mjs';
import * as st from '../sets.mjs';
import * as fx from '../fx.mjs';

export const D = lineDur;
// film times of a few moments, for the ending's polaroids (set by the parts as their takes are laid out)
export const MARKS = {};
export const KP = 'sopheak', DV = 'david', SM = 'smey', NM = 'nimith', LH = 'leanghak', PS = 'pisey', PR = 'professor', KL = 'kimlong', CN = 'channy', SN = 'sreyneang';
export const pp = (ctx, who, t, o = {}) => person(ctx, who, { t, mouth: talk(who, t), ...o });
export const warmLight = (ctx, a = 0.18, col = '255,214,150') => { ctx.save(); const g = ctx.createLinearGradient(0, 0, W, H); g.addColorStop(0, `rgba(${col},${a})`); g.addColorStop(1, `rgba(${col},0)`); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); ctx.restore(); };
export const goldHour = (ctx, a = 1) => { ctx.save(); ctx.globalAlpha = 0.28 * a; const g = ctx.createLinearGradient(0, 0, W, H); g.addColorStop(0, '#ff9a50'); g.addColorStop(1, '#ffd08a'); ctx.fillStyle = g; ctx.globalCompositeOperation = 'multiply'; ctx.fillRect(0, 0, W, H); ctx.restore(); warmLight(ctx, 0.22 * a, '255,190,120'); };
export const nightTint = (ctx, a = 0.45) => { ctx.save(); ctx.fillStyle = `rgba(20,24,70,${a})`; ctx.fillRect(-2000, -2000, 6000, 5000); ctx.restore(); };
export const sweat = (ctx, x, y, s, t, n = 3) => { for (let i = 0; i < n; i++) { const k = (t * 1.8 + i / n) % 1, side = i % 2 ? 1 : -1; ctx.save(); ctx.globalAlpha = 1 - k; drop(ctx, x + side * (40 + k * 90) * s, y - Math.sin(k * Math.PI) * 60 * s + k * 40 * s, s * 1.3, side * 0.5); ctx.restore(); } };
export const star = (ctx, x, y, k, s = 1) => { if (k <= 0 || k >= 1) return; const sc = Math.sin(k * Math.PI) * s; ctx.save(); ctx.translate(x, y); ctx.rotate(k * 3); ctx.scale(sc, sc); ctx.beginPath(); for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4, r = i % 2 ? 9 : 26; ctx.lineTo(Math.cos(a) * r, Math.sin(a) * r); } ctx.closePath(); paint(ctx, '#fff6c0', 4); ctx.restore(); };
export const stars = (ctx, at, lt, pts, s = 1.2) => pts.forEach(([x, y], i) => star(ctx, x, y, seg(lt, at + i * 0.12, at + 0.9 + i * 0.12), s));
export const atHead = (who, o, headY) => headY - anchors(who, { ...o, x: 0, y: 0 }).head[1];
export const headOf = (who, o) => anchors(who, o).head;
export const blush = (ctx, who, o, a = 1) => { const hd = anchors(who, o).head, s = o.s ?? 1, HS = CAST[who].headS; ctx.save(); ctx.globalAlpha = a * 0.6; for (const k of [-1, 1]) { oval(ctx, hd[0] + (k * 30 + (o.facing || 0) * 14) * HS * s, hd[1] + 14 * HS * s, 13 * s * HS, 7 * s * HS); ctx.fillStyle = '#ff6b6b'; ctx.fill(); } ctx.restore(); };
export const steam = (ctx, x, y, t, s = 1) => { for (let i = 0; i < 3; i++) { const k = (t * 1.6 + i / 3) % 1; ctx.save(); ctx.globalAlpha = (1 - k) * 0.8; fx.puff(ctx, x + (i - 1) * 40 * s, y - k * 90 * s, (16 + k * 22) * s, '#ffffff', 1, 4); ctx.restore(); } };
export function bokeh(ctx, t, base = '#e9c993', cols = ['rgba(255,246,220,0.45)', 'rgba(127,211,200,0.3)', 'rgba(255,176,112,0.35)']) { ctx.fillStyle = base; ctx.fillRect(0, 0, W, H); for (let i = 0; i < 14; i++) { circle(ctx, hash(i) * W + Math.sin(t * 0.3 + i) * 20, hash(i * 3.3) * H, 80 + hash(i * 7) * 140); ctx.fillStyle = cols[i % cols.length]; ctx.fill(); } }
export const fit = (ctx, s, size, maxW) => { ctx.font = `${size}px "Koulen"`; return Math.min(size, size * maxW / ctx.measureText(s).width); };
export function titleKh(ctx, lt, inAt, outAt, kh, en, y = 250, size = 100) {
  const k = ease.back(seg(lt, inAt, inAt + 0.6)) * (1 - ease.in(seg(lt, outAt, outAt + 0.4)));
  if (k <= 0) return;
  ctx.save(); ctx.translate(960, y); ctx.rotate(-0.025); ctx.scale(k, k);
  rrect(ctx, -700, -130, 1400, 250, 60); paint(ctx, '#fff6e6', 10);
  text(ctx, kh, 0, -24, { size: fit(ctx, kh, size, 1300), fill: '#e8433a', lw: 12 });
  text(ctx, en, 0, 72, { size: 42, font: 'Arial Black', fill: '#2d3a6b', lw: 0 });
  ctx.restore();
}
// a big card (head chip + two lines) for the closing line
export function banner(ctx, head, l1, l2, k, col = '#46a35a', y = 200) {
  if (k <= 0) return; const s = ease.back(clamp(k));
  ctx.save(); ctx.translate(960, y); ctx.scale(s, s); ctx.rotate(-0.02);
  rrect(ctx, -820 + 12, -120 + 14, 1640, 250, 50); ctx.fillStyle = INK; ctx.fill();
  rrect(ctx, -820, -120, 1640, 250, 50); paint(ctx, '#fff6e6', 9);
  if (head) { ctx.font = '44px "Koulen"'; const w = ctx.measureText(head).width + 70; rrect(ctx, -w / 2, -156, w, 70, 35); paint(ctx, col, 6); text(ctx, head, 0, -121, { size: 44, fill: '#ffffff', lw: 0 }); }
  text(ctx, l1, 0, -28, { size: fit(ctx, l1, 78, 1540), fill: col, lw: 0 }); text(ctx, l2, 0, 64, { size: fit(ctx, l2, 66, 1540), fill: '#2d3a6b', lw: 0 });
  ctx.restore();
}
// a little ❤ for every "កូនពៅ" (found in the line text, so it follows the real timing)
export function heartPop(ctx, x, y, k, s = 1) { if (k <= 0 || k >= 1) return; ctx.save(); ctx.globalAlpha = k > 0.75 ? (1 - k) / 0.25 : 1; pl.heart(ctx, x + Math.sin(k * 9) * 14, y - k * 120, 0.55 * s * ease.back(clamp(k * 4)), 0); ctx.restore(); }
export function koonPov(ctx, b, lt, x, y, s = 1, only = null) { for (const [id, at] of Object.entries(b.at)) { if (only && !only.includes(id)) continue; const txt = LINES[id]?.[1] || ''; let i = txt.indexOf('កូនពៅ'); while (i >= 0) { const tw = at + D(id) * (i / txt.length) + 0.1; heartPop(ctx, x, y, seg(lt, tw, tw + 1.4), s); i = txt.indexOf('កូនពៅ', i + 1); } } }
export const heartCues = b => Object.entries(b.at).flatMap(([id, at]) => { const txt = LINES[id]?.[1] || '', out = []; let i = txt.indexOf('កូនពៅ'); while (i >= 0) { out.push([at + D(id) * (i / txt.length) + 0.1, 'pop', { f0: 1600, f1: 900, gain: 0.3 }]); i = txt.indexOf('កូនពៅ', i + 1); } return out; });
export function thoughtBubble(ctx, x, y, k, draw, dir = -1, s0 = 1) { if (k <= 0) return; const s = ease.back(clamp(k)) * s0; ctx.save(); ctx.translate(x, y); ctx.scale(s, s); for (const [bx, by, r] of [[dir * -170, 150, 14], [dir * -130, 112, 22]]) { circle(ctx, bx, by, r); paint(ctx, '#ffffff', 5); } oval(ctx, 0, 0, 150, 104); paint(ctx, '#ffffff', 7); draw(); ctx.restore(); }
// «💤»: three Zs drifting up from a sleeping head
export function zzz(ctx, x, y, t, s = 1, a = 1) { if (a <= 0) return; for (let i = 0; i < 3; i++) { const k = (t * 0.55 + i / 3) % 1; ctx.save(); ctx.globalAlpha = Math.sin(k * Math.PI) * a; ctx.translate(x + k * 90 * s + Math.sin(k * 6 + i) * 12 * s, y - k * 150 * s); ctx.rotate(-0.2); text(ctx, 'Z', 0, 0, { size: (34 + k * 40) * s, fill: '#8fd3ff', lw: 8 * s }); ctx.restore(); } }
export const yawnLines = (ctx, x, y, k) => { if (k <= 0 || k >= 1) return; ctx.save(); ctx.globalAlpha = Math.sin(k * Math.PI); ctx.lineCap = 'round'; for (let i = 0; i < 5; i++) { const a = -Math.PI / 2 + (i - 2) * 0.35, r0 = 70 + k * 20, r1 = 110 + k * 30; ctx.beginPath(); ctx.moveTo(x + Math.cos(a) * r0, y + Math.sin(a) * r0); ctx.lineTo(x + Math.cos(a) * r1, y + Math.sin(a) * r1); paint(ctx, null, 7, '#2d3a6b'); } ctx.restore(); };
export const sfx = (ctx, word, x, y, lt, at, o = {}) => { if (lt > at) fx.sfxText(ctx, word, x, y, seg(lt, at, at + (o.dur || 0.9)), { size: 90, fill: '#ffd23f', rot: -0.08, ...o }); };

// ---------------------------------------------------------------- the tech office (same room as Ep 5)
export const DK = { sopheak: 520, david: 1240 };
export function wallClock(ctx, cx, cy, r, hour) {
  circle(ctx, cx, cy, r); paint(ctx, '#ffffff', Math.max(5, r * 0.12)); ctx.lineCap = 'round';
  for (let i = 0; i < 12; i++) { const a = i * TAU / 12; ctx.beginPath(); ctx.moveTo(cx + Math.sin(a) * r * 0.78, cy - Math.cos(a) * r * 0.78); ctx.lineTo(cx + Math.sin(a) * r * 0.88, cy - Math.cos(a) * r * 0.88); paint(ctx, null, Math.max(2, r * 0.05)); }
  for (const [a, l, w] of [[(hour % 12) / 12 * TAU, 0.48, 0.13], [(hour % 1) * TAU, 0.74, 0.09]]) { ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx + Math.sin(a) * r * l, cy - Math.cos(a) * r * l); paint(ctx, null, Math.max(3, r * w)); }
  circle(ctx, cx, cy, r * 0.08); paint(ctx, '#e8433a', 0);
}
export function room(ctx, t, { door = 0, light = 'day', hour = 8, board = 0 } = {}) {
  st.office(ctx, t, { board, doorOpen: door, light });
  wallClock(ctx, 1825, 130, 50, hour);
}
// a long back desk row with three monitors (group scenes stand in front of it)
export function backRow(ctx) {
  for (const x of [520, 960, 1400]) { rrect(ctx, x - 90, 560, 180, 120, 10); paint(ctx, '#2a2633', 6); rrect(ctx, x - 78, 572, 156, 96, 6); paint(ctx, '#7fd3c8', 0); rrect(ctx, x - 10, 680, 20, 40, 4); paint(ctx, '#9aa3b5', 4); }
  poly(ctx, [[300, 720], [1620, 720], [1640, 742], [280, 742]]); paint(ctx, st.S.desk, 6); rrect(ctx, 280, 742, 1360, 80, 6); paint(ctx, st.S.deskD, 6);
}
// monitor on a desk; screen(ctx, x, y, w, h) paints the display
export function monitor(ctx, x, { on = true, side = 1, screen = null } = {}) { const mx = x + side * 145; rrect(ctx, mx - 85, 560, 170, 120, 10); paint(ctx, '#2a2633', 6); rrect(ctx, mx - 73, 572, 146, 96, 6); ctx.fillStyle = on ? '#7fd3c8' : '#1d1b26'; ctx.fill(); if (screen && on) { ctx.save(); rrect(ctx, mx - 73, 572, 146, 96, 6); ctx.clip(); screen(ctx, mx - 73, 572, 146, 96); ctx.restore(); } rrect(ctx, mx - 10, 680, 20, 50, 4); paint(ctx, '#9aa3b5', 4); return mx; }
export function deskFront(ctx, x, w = 220) { poly(ctx, [[x - w, 730], [x + w, 730], [x + w + 16, 752], [x - w - 16, 752]]); paint(ctx, st.S.desk, 6); rrect(ctx, x - w - 16, 752, 2 * w + 32, 300, 6); paint(ctx, st.S.deskD, 6); rrect(ctx, x - 60, 800, 120, 36, 8); paint(ctx, st.S.deskEdge, 4); }
// a seated person behind a desk, head at headY
export const seat = (who, x, o = {}) => { const p = { s: 1.22, sit: true, facing: 0.15, pose: 'type', expr: 'smile', ...o }; return { ...p, x, y: atHead(who, { ...p, x: 0 }, p.headY ?? 525) }; };
// a video timeline on a monitor (Sopheak editing; k = progress)
export const editScreen = k => (ctx, x, y, w, h) => { ctx.fillStyle = '#232036'; ctx.fillRect(x, y, w, h); ctx.fillStyle = '#ff9a3f'; ctx.fillRect(x + 8, y + 8, w * 0.5, h * 0.42); for (let i = 0; i < 6; i++) { ctx.fillStyle = ['#ff5c8a', '#3fb3ff', '#46c34f', '#ffd23f', '#a07bff', '#ff9a3f'][i]; ctx.fillRect(x + 6 + i * (w - 12) / 6, y + h * 0.62, (w - 12) / 6 - 3, h * 0.13); } ctx.fillStyle = '#ffffff'; ctx.fillRect(x + 6 + (w - 12) * clamp(k), y + h * 0.56, 2, h * 0.38); };
export const doneScreen = (ctx, x, y, w, h) => { ctx.fillStyle = '#e9fbe6'; ctx.fillRect(x, y, w, h); circle(ctx, x + w / 2, y + h * 0.42, 22); paint(ctx, '#46c34f', 4); ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(x + w / 2 - 10, y + h * 0.42); ctx.lineTo(x + w / 2 - 2, y + h * 0.42 + 9); ctx.lineTo(x + w / 2 + 12, y + h * 0.42 - 9); paint(ctx, null, 5, '#ffffff'); text(ctx, 'រួចរាល់!', x + w / 2, y + h * 0.82, { size: 22, fill: '#2f8c43', lw: 0 }); };
export { chair, chairBack };
