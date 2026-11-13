// Episode 6 "ម៉ោងហ្គេម និងម៉ោងរៀន": props, screens and sets first made for that episode; Episode 7 reuses the icon tags (ICON, tag)
// (time-of-day chips, the phone game, the group chat, the night classroom/corridor/campus, the motorbike, David's room).
import { W, H, INK, TAU, paint, circle, oval, rrect, poly, smooth, text, clamp, lerp, seg, ease, hash } from './core.mjs';
import { person, CAST, teaCup } from './people.mjs';
import * as st from './sets.mjs';
import * as pl from './places.mjs';

const fit = (ctx, s, size, maxW) => { ctx.font = `${size}px "Koulen"`; return Math.min(size, size * maxW / ctx.measureText(s).width); };
const star5 = (ctx, x, y, r, col = '#ffd23f', lw = 4) => { ctx.beginPath(); for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * 0.45 : r; ctx.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); } ctx.closePath(); paint(ctx, col, lw); };

// ---------------------------------------------------------------- icons (drawn in a ~100 px box around 0,0)
export const ICON = {
  sun(ctx) { ctx.lineCap = 'round'; for (let i = 0; i < 8; i++) { const a = i * TAU / 8; ctx.beginPath(); ctx.moveTo(Math.cos(a) * 30, Math.sin(a) * 30); ctx.lineTo(Math.cos(a) * 44, Math.sin(a) * 44); paint(ctx, null, 7, '#ffb020'); } circle(ctx, 0, 0, 24); paint(ctx, '#ffd23f', 5); },
  rice(ctx) { ctx.lineCap = 'round'; for (const k of [-1, 1]) { ctx.beginPath(); ctx.moveTo(10 + k * 8, -40); ctx.lineTo(-14 + k * 10, 6); paint(ctx, null, 5, '#c9824a'); } smooth(ctx, [[-30, -4], [-20, -24], [0, -30], [20, -24], [30, -4]], false); ctx.closePath(); paint(ctx, '#ffffff', 4); ctx.beginPath(); ctx.moveTo(-38, -4); ctx.lineTo(38, -4); ctx.quadraticCurveTo(34, 30, 0, 32); ctx.quadraticCurveTo(-34, 30, -38, -4); paint(ctx, '#e8433a', 5); },
  game(ctx) { rrect(ctx, -44, -24, 88, 50, 24); paint(ctx, '#7c5cff', 5); rrect(ctx, -30, -4, 22, 8, 3); paint(ctx, '#ffffff', 0); rrect(ctx, -23, -11, 8, 22, 3); paint(ctx, '#ffffff', 0); circle(ctx, 18, -6, 6); paint(ctx, '#ffd23f', 3); circle(ctx, 30, 6, 6); paint(ctx, '#ff5c8a', 3); },
  work(ctx) { rrect(ctx, -16, -34, 32, 16, 6); paint(ctx, null, 5); rrect(ctx, -40, -22, 80, 54, 8); paint(ctx, '#c97a4a', 5); ctx.beginPath(); ctx.moveTo(-40, -2); ctx.lineTo(40, -2); paint(ctx, null, 4); rrect(ctx, -7, -8, 14, 12, 3); paint(ctx, '#ffd23f', 3); },
  sunset(ctx) { ctx.save(); ctx.beginPath(); ctx.rect(-50, -50, 100, 54); ctx.clip(); circle(ctx, 0, 6, 30); paint(ctx, '#ff9a3f', 5); ctx.restore(); ctx.lineCap = 'round'; for (const [y, w] of [[10, 44], [22, 30], [32, 16]]) { ctx.beginPath(); ctx.moveTo(-w, y); ctx.lineTo(w, y); paint(ctx, null, 6, '#e8433a'); } for (let i = 0; i < 5; i++) { const a = Math.PI + (i + 0.5) * Math.PI / 5; ctx.beginPath(); ctx.moveTo(Math.cos(a) * 38, 6 + Math.sin(a) * 38); ctx.lineTo(Math.cos(a) * 48, 6 + Math.sin(a) * 48); paint(ctx, null, 6, '#ffb020'); } },
  moon(ctx) { ctx.beginPath(); ctx.arc(0, 0, 32, 0.6, TAU - 0.6 + 0.0001); ctx.arc(16, -6, 26, TAU - 0.9, 0.9, true); ctx.closePath(); paint(ctx, '#fff3a0', 5); star5(ctx, 30, -26, 9, '#fff3a0', 3); star5(ctx, 38, 14, 6, '#fff3a0', 3); },
  trophy(ctx) { for (const k of [-1, 1]) { ctx.beginPath(); ctx.arc(k * 30, -16, 14, k > 0 ? -Math.PI / 2 : Math.PI / 2, k > 0 ? Math.PI / 2 : Math.PI * 1.5); paint(ctx, null, 6, '#e6a817'); } ctx.beginPath(); ctx.moveTo(-30, -36); ctx.lineTo(30, -36); ctx.quadraticCurveTo(30, 12, 0, 14); ctx.quadraticCurveTo(-30, 12, -30, -36); paint(ctx, '#ffd23f', 5); rrect(ctx, -6, 12, 12, 16, 3); paint(ctx, '#e6a817', 4); rrect(ctx, -22, 26, 44, 14, 4); paint(ctx, '#c97a4a', 4); star5(ctx, 0, -14, 11, '#fff6c0', 3); },
  swords(ctx) { for (const k of [-1, 1]) { ctx.save(); ctx.rotate(k * 0.78); rrect(ctx, -6, -46, 12, 62, 4); paint(ctx, '#dfe6f2', 4); rrect(ctx, -18, 14, 36, 8, 4); paint(ctx, '#ffd23f', 4); rrect(ctx, -5, 22, 10, 22, 4); paint(ctx, '#8a5a3c', 4); ctx.restore(); } },
  laugh(ctx) { circle(ctx, 0, 0, 38); paint(ctx, '#ffd23f', 5); for (const k of [-1, 1]) { ctx.beginPath(); ctx.arc(k * 14, -8, 8, Math.PI * 1.1, Math.PI * 1.9); paint(ctx, null, 4); oval(ctx, k * 26, 2, 7, 12, k * 0.3); paint(ctx, '#8fd3ff', 3); } ctx.beginPath(); ctx.moveTo(-20, 8); ctx.quadraticCurveTo(0, 36, 20, 8); ctx.closePath(); paint(ctx, '#7a3640', 4); },
  calendar(ctx) { rrect(ctx, -40, -34, 80, 74, 10); paint(ctx, '#ffffff', 5); rrect(ctx, -40, -34, 80, 24, 8); paint(ctx, '#e8433a', 5); for (const k of [-1, 1]) { rrect(ctx, k * 20 - 4, -44, 8, 18, 4); paint(ctx, '#9aa3b5', 3); } text(ctx, '៣០', 0, 14, { size: 34, fill: '#2d3a6b', lw: 0 }); },
  gradcap(ctx) { poly(ctx, [[0, -30], [50, -12], [0, 6], [-50, -12]]); paint(ctx, '#2a2633', 5); rrect(ctx, -26, -4, 52, 26, 8); paint(ctx, '#2a2633', 5); ctx.beginPath(); ctx.moveTo(0, -12); ctx.lineTo(36, -2); ctx.lineTo(36, 26); paint(ctx, null, 4, '#ffd23f'); circle(ctx, 36, 30, 6); paint(ctx, '#ffd23f', 3); },
  heart(ctx) { pl.heart(ctx, 0, 4, 0.55, 0); },
  battery(ctx) { rrect(ctx, -40, -22, 74, 44, 8); paint(ctx, '#ffffff', 5); rrect(ctx, 34, -8, 8, 16, 3); paint(ctx, INK, 0); rrect(ctx, -34, -16, 62, 32, 4); paint(ctx, '#46c34f', 0); poly(ctx, [[4, -18], [-10, 2], [0, 2], [-6, 18], [10, -4], [0, -4]]); paint(ctx, '#ffd23f', 3); },
  usb(ctx) { usb(ctx, 0, 0, 1.4, -0.5); },
};
// the time of day in the top-left corner, at the start of each part: «☀ ៨:០០ ព្រឹក»
export function timeChip(ctx, icon, label, k) {
  if (k <= 0) return; const s = ease.back(clamp(k));
  ctx.save(); ctx.translate(46, 46); ctx.scale(s, s); ctx.font = '58px "Koulen"';
  const w = ctx.measureText(label).width + 170, h = 112;
  rrect(ctx, 10, 12, w, h, 56); ctx.fillStyle = INK; ctx.fill(); rrect(ctx, 0, 0, w, h, 56); paint(ctx, '#fff6e6', 7);
  ctx.save(); ctx.translate(62, 56); ctx.scale(0.95, 0.95); ICON[icon](ctx); ctx.restore();
  text(ctx, label, 124, 60, { size: 58, fill: '#2d3a6b', lw: 0, align: 'left' }); ctx.restore();
}
// a sticker label with an icon: coach joke, VS banner, grad tag, defence countdown
export function tag(ctx, x, y, label, k, { icon = null, icon2 = null, col = '#fff6e6', ink = '#2d3a6b', size = 60, rot = -0.03, chip = null } = {}) {
  if (k <= 0) return; const s = ease.back(clamp(k));
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s); ctx.font = `${size}px "Koulen"`;
  const tw = ctx.measureText(label).width, w = tw + (icon ? 150 : 70) + (icon2 ? 120 : 0), h = size * 1.75;
  rrect(ctx, -w / 2 + 10, -h / 2 + 12, w, h, h / 2); ctx.fillStyle = INK; ctx.fill(); rrect(ctx, -w / 2, -h / 2, w, h, h / 2); paint(ctx, col, 7);
  const tx = icon ? -w / 2 + 130 : -w / 2 + 35;
  if (icon) { ctx.save(); ctx.translate(-w / 2 + 72, 0); ctx.scale(size / 66, size / 66); ICON[icon](ctx); ctx.restore(); }
  text(ctx, label, tx + tw / 2, 4, { size, fill: ink, lw: 0 });
  if (icon2) { ctx.save(); ctx.translate(tx + tw + 62, 0); ctx.scale(size / 66, size / 66); ICON[icon2](ctx); ctx.restore(); }
  if (chip) { ctx.font = '40px "Koulen"'; const cw = ctx.measureText(chip).width + 60; rrect(ctx, -cw / 2, -h / 2 - 44, cw, 62, 31); paint(ctx, '#e8433a', 6); text(ctx, chip, 0, -h / 2 - 12, { size: 40, fill: '#ffffff', lw: 0 }); }
  ctx.restore();
}
// «🏆 VICTORY!» — burst rays, a trophy and gold letters
export function victory(ctx, x, y, k, t, s0 = 1) {
  if (k <= 0) return; const s = ease.back(clamp(k * 1.4)) * s0;
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.save(); ctx.rotate(t * 0.4); for (let i = 0; i < 16; i++) { ctx.rotate(TAU / 16); poly(ctx, [[0, 0], [-40, -560], [40, -560]]); ctx.fillStyle = i % 2 ? 'rgba(255,224,120,0.35)' : 'rgba(255,255,255,0.25)'; ctx.fill(); } ctx.restore();
  ctx.save(); ctx.translate(-470, -4); ctx.scale(2.1, 2.1); ICON.trophy(ctx); ctx.restore();
  ctx.save(); ctx.rotate(-0.05); text(ctx, 'VICTORY!', 90, 0, { size: 190, fill: '#ffd23f', lw: 16 }); ctx.restore();
  for (let i = 0; i < 5; i++) star5(ctx, -360 + i * 180, -150 - (i % 2) * 40 + Math.sin(t * 4 + i) * 8, 18 + (i % 2) * 8, '#fff6c0', 4);
  ctx.restore();
}

// ---------------------------------------------------------------- small props
export function pillow(ctx, x, y, s = 1) { ctx.save(); ctx.translate(x, y); ctx.scale(s, s); smooth(ctx, [[-110, -10], [-96, -36], [0, -44], [96, -36], [110, -10], [98, 14], [0, 22], [-98, 14]]); paint(ctx, '#f4f1ff', 6); for (const k of [-1, 1]) { ctx.beginPath(); ctx.moveTo(k * 60, -30); ctx.quadraticCurveTo(k * 70, -8, k * 60, 12); paint(ctx, null, 3, '#cfc8ea'); } ctx.restore(); }
export function breakfast(ctx, x, y, s = 1) { ctx.save(); ctx.translate(x, y); ctx.scale(s, s); oval(ctx, 0, 0, 74, 22); paint(ctx, '#ffffff', 5); oval(ctx, -18, -8, 34, 14); paint(ctx, '#fffaf0', 3); oval(ctx, 26, -8, 28, 12); paint(ctx, '#ffffff', 3); circle(ctx, 28, -10, 9); paint(ctx, '#ffc23f', 3); rrect(ctx, -46, -16, 34, 12, 6); paint(ctx, '#c9573a', 3); ctx.restore(); }
export function gingerTea(ctx, x, y, s = 1, t = 0) { ctx.save(); ctx.translate(x, y); ctx.scale(s, s); oval(ctx, 0, 6, 36, 10); paint(ctx, '#ffffff', 4); teaCup(ctx, 0, 0, 1.1, t, true); ctx.save(); ctx.translate(32, 0); ctx.rotate(0.3); smooth(ctx, [[-10, -6], [0, -12], [12, -8], [14, 2], [2, 6], [-10, 4]]); paint(ctx, '#e8c26a', 3); ctx.restore(); ctx.restore(); }
// David's thick thesis binder: «សារណា» / FINAL YEAR; open = pages fanned out
export function thesis(ctx, x, y, s = 1, rot = 0, { open = 0 } = {}) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  if (open > 0) { for (let i = 0; i < 4; i++) { ctx.save(); ctx.rotate((i - 1.5) * 0.12 * open); rrect(ctx, -60 + i * 10 * open, -84, 120, 160, 6); paint(ctx, '#ffffff', 4); for (let l = 0; l < 6; l++) { ctx.beginPath(); ctx.moveTo(-44 + i * 10 * open, -60 + l * 20); ctx.lineTo(40 + i * 10 * open - (l % 3) * 14, -60 + l * 20); paint(ctx, null, 3, '#b8c2d8'); } ctx.restore(); } }
  else {
    rrect(ctx, -70, -92, 140, 180, 8); paint(ctx, '#2f6fe0', 6); rrect(ctx, 56, -86, 18, 168, 6); paint(ctx, '#fffaf0', 4);
    rrect(ctx, -60, -58, 112, 70, 6); paint(ctx, '#ffffff', 4);
    text(ctx, 'សារណា', -4, -36, { size: 30, fill: '#2d3a6b', lw: 0 }); text(ctx, 'FINAL YEAR', -4, -2, { size: 15, font: 'Arial Black', fill: '#e8433a', lw: 0 });
  }
  ctx.restore();
}
export function mangoPlate(ctx, x, y, s = 1, n = 5) { ctx.save(); ctx.translate(x, y); ctx.scale(s, s); oval(ctx, 0, 0, 60, 18); paint(ctx, '#ffffff', 5); for (let i = 0; i < n; i++) { ctx.save(); ctx.translate(-34 + i * 17, -8); ctx.rotate(-0.4 + i * 0.2); smooth(ctx, [[-10, 6], [-6, -14], [6, -16], [10, 6]]); paint(ctx, '#ffb020', 3); ctx.restore(); } ctx.restore(); }
// a lunch box wrapped in a checked krama cloth, knot on top
export function bundle(ctx, x, y, s = 1, col = '#e8433a', rot = 0) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  rrect(ctx, -50, -36, 100, 62, 14); paint(ctx, col, 5);
  ctx.save(); rrect(ctx, -50, -36, 100, 62, 14); ctx.clip(); ctx.fillStyle = 'rgba(255,255,255,0.4)'; for (let i = -50; i < 50; i += 22) ctx.fillRect(i, -36, 9, 62); for (let j = -36; j < 26; j += 22) ctx.fillRect(-50, j, 100, 9); ctx.restore();
  for (const k of [-1, 1]) { smooth(ctx, [[0, -36], [k * 18, -62], [k * 34, -58], [k * 14, -34]]); paint(ctx, col, 4); } circle(ctx, 0, -38, 10); paint(ctx, col, 4);
  ctx.restore();
}
export function usb(ctx, x, y, s = 1, rot = 0) { ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s); rrect(ctx, -12, -34, 24, 50, 7); paint(ctx, '#e8433a', 4); rrect(ctx, -9, -54, 18, 22, 3); paint(ctx, '#dfe6f2', 4); for (const k of [-1, 1]) { rrect(ctx, k * 4 - 2.5, -48, 5, 5, 1); ctx.fillStyle = INK; ctx.fill(); } ctx.restore(); }
export function jug(ctx, x, y, s = 1, rot = 0) { ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s); ctx.beginPath(); ctx.moveTo(-26, -60); ctx.lineTo(24, -60); ctx.lineTo(30, 20); ctx.quadraticCurveTo(0, 30, -30, 20); ctx.closePath(); paint(ctx, 'rgba(220,240,250,0.9)', 5); ctx.save(); ctx.beginPath(); ctx.rect(-40, -30, 80, 60); ctx.clip(); ctx.beginPath(); ctx.moveTo(-26, -60); ctx.lineTo(24, -60); ctx.lineTo(30, 20); ctx.quadraticCurveTo(0, 30, -30, 20); ctx.closePath(); ctx.fillStyle = '#f2a03a'; ctx.fill(); ctx.restore(); ctx.beginPath(); ctx.arc(32, -24, 18, -1.3, 1.3); paint(ctx, null, 6); poly(ctx, [[-26, -60], [-40, -70], [-24, -50]]); paint(ctx, 'rgba(220,240,250,0.9)', 4); ctx.restore(); }
export function glass(ctx, x, y, s = 1, fill = 1) { ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.beginPath(); ctx.moveTo(-14, -36); ctx.lineTo(14, -36); ctx.lineTo(11, 4); ctx.lineTo(-11, 4); ctx.closePath(); paint(ctx, 'rgba(230,246,250,0.9)', 4); if (fill > 0) { ctx.save(); ctx.beginPath(); ctx.moveTo(-14, -36); ctx.lineTo(14, -36); ctx.lineTo(11, 4); ctx.lineTo(-11, 4); ctx.closePath(); ctx.clip(); ctx.fillStyle = '#f2a03a'; ctx.fillRect(-20, 4 - 38 * fill, 40, 40); ctx.restore(); } ctx.restore(); }
export function deskLamp(ctx, x, y, s = 1, on = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  if (on > 0) { ctx.save(); ctx.globalAlpha = 0.35 * on; const g = ctx.createRadialGradient(80, -150, 10, 80, -60, 420); g.addColorStop(0, '#fff2b0'); g.addColorStop(1, 'rgba(255,230,150,0)'); ctx.fillStyle = g; poly(ctx, [[40, -170], [130, -170], [420, 60], [-260, 60]]); ctx.fill(); ctx.restore(); }
  oval(ctx, 0, 0, 50, 12); paint(ctx, '#3f6fbf', 5); ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(0, -4); ctx.lineTo(-30, -130); ctx.lineTo(60, -190); paint(ctx, null, 10); ctx.beginPath(); ctx.moveTo(0, -4); ctx.lineTo(-30, -130); ctx.lineTo(60, -190); paint(ctx, null, 5, '#3f6fbf');
  ctx.save(); ctx.translate(70, -186); ctx.rotate(0.5); ctx.beginPath(); ctx.moveTo(-40, 30); ctx.quadraticCurveTo(0, -40, 40, 30); ctx.closePath(); paint(ctx, '#3f6fbf', 5); oval(ctx, 0, 30, 26, 8); paint(ctx, on ? '#fff6b0' : '#ddd', 3); ctx.restore();
  ctx.restore();
}
// open laptop seen from the front; screen(ctx, w, h) draws the display in local coords
export function laptop(ctx, x, y, s = 1, screen = null, t = 0) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  rrect(ctx, -170, -230, 340, 220, 14); paint(ctx, '#3a3946', 6); rrect(ctx, -156, -216, 312, 192, 6); ctx.fillStyle = '#f4f1ff'; ctx.fill();
  if (screen) { ctx.save(); rrect(ctx, -156, -216, 312, 192, 6); ctx.clip(); ctx.translate(-156, -216); screen(ctx, 312, 192, t); ctx.restore(); }
  poly(ctx, [[-190, -8], [190, -8], [214, 16], [-214, 16]]); paint(ctx, '#c9ccd6', 5);
  ctx.restore();
}
// the thesis document being tidied into chapters (k: 0 = one messy page, 1 = five neat chapters)
export function thesisDoc(ctx, w, h, k, t) {
  ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, w, h); ctx.fillStyle = '#2f6fe0'; ctx.fillRect(0, 0, w, 26); text(ctx, 'សារណា.docx', 16, 14, { size: 16, fill: '#ffffff', lw: 0, align: 'left' });
  const ch = ['ជំពូកទី ១', 'ជំពូកទី ២', 'ជំពូកទី ៣', 'ជំពូកទី ៤', 'ជំពូកទី ៥'], cols = ['#ff5c8a', '#ffb020', '#46c34f', '#3fb3ff', '#a07bff'];
  for (let i = 0; i < 5; i++) {
    const kk = ease.back(seg(k, i * 0.15, i * 0.15 + 0.4)), mx = 20 + hash(i * 3) * 160, my = 40 + hash(i * 7) * 110, nx = 16, ny = 36 + i * 30;
    const x = lerp(mx, nx, kk), y = lerp(my, ny, kk), rot = lerp((hash(i) - 0.5) * 0.6, 0, kk);
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); rrect(ctx, 0, 0, lerp(110, 280, kk), 24, 5); ctx.fillStyle = cols[i]; ctx.globalAlpha = 0.25 + kk * 0.75; ctx.fill(); ctx.globalAlpha = 1;
    text(ctx, ch[i], 10, 13, { size: 15, fill: kk > 0.5 ? '#ffffff' : '#2d2a3e', lw: 0, align: 'left' }); if (kk > 0.9) text(ctx, '✓', lerp(110, 280, kk) - 16, 13, { size: 16, font: 'Arial Black', fill: '#ffffff', lw: 0 }); ctx.restore();
  }
}

// ---------------------------------------------------------------- the phone game (landscape)
// st: { win: 0..1 (victory overlay), labels: 0..1 (move/attack hints), tap: 0..1 (red button pressed), t0 }
export function gameScreen(ctx, w, h, t, st = {}) {
  ctx.fillStyle = '#7fd36e'; ctx.fillRect(0, 0, w, h);
  ctx.fillStyle = '#6cc35c'; for (let i = 0; i < 18; i++) { circle(ctx, hash(i) * w, hash(i * 2.1) * h, 10 + hash(i * 3) * 18); ctx.fill(); }
  ctx.save(); ctx.beginPath(); ctx.moveTo(w * 0.62, 0); ctx.bezierCurveTo(w * 0.5, h * 0.4, w * 0.55, h * 0.6, w * 0.38, h); ctx.lineWidth = h * 0.14; ctx.strokeStyle = '#5fb8e8'; ctx.stroke(); ctx.restore();
  ctx.fillStyle = '#e6cf8f'; ctx.beginPath(); ctx.moveTo(0, h * 0.78); ctx.lineTo(w, h * 0.22); ctx.lineWidth = h * 0.12; ctx.strokeStyle = '#e6cf8f'; ctx.stroke();
  const tower = (x, y, col) => { rrect(ctx, x - 16, y - 46, 32, 50, 4); paint(ctx, col, 3); poly(ctx, [[x - 22, y - 46], [x + 22, y - 46], [x, y - 70]]); paint(ctx, col, 3); rrect(ctx, x - 18, y - 60 - 18, 36, 6, 3); ctx.fillStyle = '#46c34f'; ctx.fill(); };
  tower(w * 0.1, h * 0.8, '#3f8bd0'); tower(w * 0.9, h * 0.25, '#e8433a');
  const tt = t * 1.3;
  const heroes = [[0.3, 0.6, '#3fb3ff'], [0.42, 0.52, '#ffd23f'], [0.36, 0.72, '#ff5c8a'], [0.62, 0.4, '#e8433a'], [0.7, 0.5, '#8a4f7d'], [0.66, 0.3, '#ff9a3f']];
  heroes.forEach(([hx, hy, col], i) => {
    const x = (hx + Math.sin(tt + i * 1.7) * 0.05) * w, y = (hy + Math.cos(tt * 1.3 + i) * 0.05) * h, r = h * 0.05;
    circle(ctx, x, y, r); paint(ctx, col, 3); circle(ctx, x - r * 0.3, y - r * 0.2, r * 0.22); paint(ctx, '#ffffff', 0); circle(ctx, x + r * 0.3, y - r * 0.2, r * 0.22); paint(ctx, '#ffffff', 0);
    rrect(ctx, x - r, y - r * 1.9, r * 2, r * 0.4, 2); ctx.fillStyle = '#2a2633'; ctx.fill(); rrect(ctx, x - r, y - r * 1.9, r * 2 * (0.4 + 0.6 * hash(i + Math.floor(tt))), r * 0.4, 2); ctx.fillStyle = i < 3 ? '#46c34f' : '#e8433a'; ctx.fill();
  });
  // skill flashes between the teams
  for (let i = 0; i < 3; i++) { const k = (t * 1.7 + i / 3) % 1; ctx.save(); ctx.globalAlpha = 1 - k; star5(ctx, w * (0.45 + i * 0.06), h * (0.45 + (i % 2) * 0.1), h * 0.04 + k * h * 0.08, ['#fff6c0', '#9fe3ff', '#ffb3c1'][i], 2); ctx.restore(); }
  // HUD: score + timer, joystick (move), red attack button + skills
  rrect(ctx, w / 2 - h * 0.34, 4, h * 0.68, h * 0.12, 8); ctx.fillStyle = 'rgba(30,30,50,0.7)'; ctx.fill();
  text(ctx, '12  ⚔  9', w / 2, h * 0.1, { size: h * 0.08, font: 'Arial Black', fill: '#ffffff', lw: 0 });
  const jx = w * 0.13, jy = h * 0.74, jr = h * 0.13;
  circle(ctx, jx, jy, jr); ctx.fillStyle = 'rgba(255,255,255,0.35)'; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(255,255,255,0.8)'; ctx.stroke();
  circle(ctx, jx + Math.sin(t * 3) * jr * 0.35, jy + Math.cos(t * 2.3) * jr * 0.3, jr * 0.45); ctx.fillStyle = 'rgba(255,255,255,0.85)'; ctx.fill();
  const bx = w * 0.88, by = h * 0.74, br = h * 0.12 * (1 - (st.tap || 0) * 0.15);
  circle(ctx, bx, by, br); paint(ctx, '#e8433a', 4); circle(ctx, bx - br * 0.3, by - br * 0.3, br * 0.25); ctx.fillStyle = 'rgba(255,255,255,0.5)'; ctx.fill();
  for (const [dx, dy] of [[-0.17, 0.08], [-0.13, -0.12], [0.0, -0.2]]) { circle(ctx, bx + dx * w * 0.6, by + dy * h, h * 0.05); paint(ctx, '#3f8bd0', 3); }
  if ((st.labels || 0) > 0) {
    const a = ease.back(clamp(st.labels));
    ctx.save(); ctx.globalAlpha = clamp(st.labels * 2);
    for (const [x, y, s, c] of [[jx, jy - jr - h * 0.09, 'ដើរ', '#3f8bd0'], [bx, by - br - h * 0.09, 'វាយ', '#e8433a']]) { ctx.save(); ctx.translate(x, y); ctx.scale(a, a); rrect(ctx, -h * 0.13, -h * 0.07, h * 0.26, h * 0.14, h * 0.07); paint(ctx, '#ffffff', 3); text(ctx, s, 0, 2, { size: h * 0.09, fill: c, lw: 0 }); ctx.restore(); }
    ctx.restore();
  }
  if ((st.win || 0) > 0) {
    ctx.save(); ctx.globalAlpha = clamp(st.win * 2) * 0.55; ctx.fillStyle = '#1d1530'; ctx.fillRect(0, 0, w, h); ctx.restore();
    ctx.save(); ctx.translate(w / 2, h * 0.5); const s = ease.back(clamp(st.win)) * h / 560; ctx.scale(s, s); victory(ctx, 60, 0, 1, t, 0.9); ctx.restore();
  }
}
// a phone held sideways for the game; centre cx,cy, width w
export function gamePhone(ctx, cx, cy, w, t, st = {}, rot = 0) {
  const h = w * 0.48, u = w / 1000;
  ctx.save(); ctx.translate(cx, cy); ctx.rotate(rot);
  rrect(ctx, -w / 2, -h / 2, w, h, 60 * u); paint(ctx, st.body || '#2c2a33', Math.max(4, 10 * u));
  const sw = w - 70 * u, sh = h - 40 * u;
  ctx.save(); rrect(ctx, -sw / 2, -sh / 2, sw, sh, 40 * u); ctx.clip(); ctx.translate(-sw / 2, -sh / 2); gameScreen(ctx, sw, sh, t, st); ctx.restore();
  ctx.restore();
}

// ---------------------------------------------------------------- group chat «គ្រួសារ Office»
// a little round avatar: the person's head in a circle
export function avatar(ctx, who, x, y, r, t = 0) {
  ctx.save(); circle(ctx, x, y, r); ctx.fillStyle = { smey: '#cfe6ff', nimith: '#e6e0ff', leanghak: '#ffe0ea', pisey: '#dff5e4', sopheak: '#fff3c4', david: '#e3e6ee' }[who] || '#eee'; ctx.fill(); ctx.clip();
  const c = CAST[who], s = r / 70, hy = c.H * (c.legs + c.torso) + 40 * c.headS * (c.hy || 1) + (c.neck || 0);
  person(ctx, who, { x, y: y + hy * s + r * 0.15, s, facing: 0, expr: 'grin', t: 0.3 }); ctx.restore();
  circle(ctx, x, y, r); paint(ctx, null, Math.max(2.5, r * 0.07));
}
// msgs: [{ who, lines:[...], at, kind:'text'|'voice', icon }]; lt = take time; the newest message sits at the bottom
export function chatPhone(ctx, cx, cy, h, t, lt, msgs, { buzz = 0 } = {}) {
  const w = h * 0.5, u = h / 1000;
  ctx.save(); ctx.translate(cx + Math.sin(t * 90) * 6 * buzz, cy);
  rrect(ctx, -w / 2, -h / 2, w, h, 70 * u); paint(ctx, '#2c2a33', Math.max(4, 10 * u));
  const sw = w - 44 * u, sh = h - 44 * u;
  ctx.save(); rrect(ctx, -sw / 2, -sh / 2, sw, sh, 52 * u); ctx.clip(); ctx.translate(-sw / 2, -sh / 2);
  ctx.fillStyle = '#efe9ff'; ctx.fillRect(0, 0, sw, sh);
  // header
  ctx.fillStyle = '#7c5cff'; ctx.fillRect(0, 0, sw, 200 * u);
  circle(ctx, 80 * u, 128 * u, 46 * u); ctx.fillStyle = '#ffd23f'; ctx.fill(); ctx.save(); ctx.translate(80 * u, 132 * u); ctx.scale(0.7 * u * 1.4, 0.7 * u * 1.4); ICON.heart(ctx); ctx.restore();
  text(ctx, 'គ្រួសារ Office', 146 * u, 112 * u, { size: fit(ctx, 'គ្រួសារ Office', 44 * u, sw - 170 * u), fill: '#ffffff', lw: 0, align: 'left' });
  text(ctx, '6 members', 146 * u, 162 * u, { size: 24 * u, font: 'Arial Black', fill: '#d9d0ff', lw: 0, align: 'left' });
  // messages stack upward from the bottom
  const shown = msgs.filter(m => lt >= m.at), gap = 26 * u, bubH = m => (m.kind === 'voice' ? 120 : 64 + m.lines.length * 60) * u;
  let y = sh - 60 * u; const offs = [];
  for (let i = shown.length - 1; i >= 0; i--) { const m = shown[i], hh = bubH(m); y -= hh; offs[i] = y; y -= gap; }
  shown.forEach((m, i) => {
    const k = ease.back(clamp((lt - m.at) / 0.35)), by = offs[i], hh = bubH(m), bx = 120 * u, bw = sw - 150 * u;
    if (by + hh < 200 * u) return;
    ctx.save(); ctx.translate(bx, by + hh); ctx.scale(k, k); ctx.translate(-bx, -by - hh);
    avatar(ctx, m.who, 62 * u, by + hh - 40 * u, 38 * u, t);
    rrect(ctx, bx, by, bw, hh, 30 * u); paint(ctx, '#ffffff', 4 * u);
    text(ctx, { smey: 'បងស្មី', nimith: 'បងនិមិត្ត', leanghak: 'បងស្រីលាងហាក់', pisey: 'បងពិសី', sopheak: 'សុភ័ក្រ' }[m.who] || m.who, bx + 26 * u, by + 34 * u, { size: 28 * u, fill: '#7c5cff', lw: 0, align: 'left' });
    if (m.kind === 'voice') {
      circle(ctx, bx + 60 * u, by + 80 * u, 26 * u); paint(ctx, '#7c5cff', 3 * u); poly(ctx, [[bx + 52 * u, by + 66 * u], [bx + 72 * u, by + 80 * u], [bx + 52 * u, by + 94 * u]]); ctx.fillStyle = '#ffffff'; ctx.fill();
      for (let b = 0; b < 16; b++) { const a = 8 + Math.abs(Math.sin(b * 1.7 + (m.play ? t * 8 : 0))) * 30; rrect(ctx, bx + 104 * u + b * 18 * u, by + (80 - a / 2) * u, 9 * u, a * u, 4 * u); ctx.fillStyle = '#b9a8ff'; ctx.fill(); }
    } else m.lines.forEach((ln, j) => text(ctx, ln, bx + 26 * u, by + (92 + j * 60) * u, { size: fit(ctx, ln, 40 * u, bw - 120 * u), fill: '#2d2a3e', lw: 0, align: 'left' }));
    if (m.icon) { ctx.save(); ctx.translate(bx + bw - 50 * u, by + hh - 46 * u); ctx.scale(0.62 * u * 1.5, 0.62 * u * 1.5); ICON[m.icon](ctx); ctx.restore(); }
    ctx.restore();
  });
  ctx.restore();
  rrect(ctx, -60 * u, -h / 2 + 34 * u, 120 * u, 28 * u, 14 * u); ctx.fillStyle = '#2c2a33'; ctx.fill();
  ctx.restore();
}

// ---------------------------------------------------------------- sets
const nightWin = (ctx, x, y, w, h, on, i) => { rrect(ctx, x, y, w, h, 4); ctx.fillStyle = on ? (i % 3 ? '#ffd98a' : '#ffe9b0') : '#3a3f7a'; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = INK; ctx.stroke(); };
// the university at night: building with lit windows, a sign, trees, a streetlight and a bench
export const UNI_NAME = 'សាកលវិទ្យាល័យ';
export function uniBuilding(ctx, x, y, s = 1, t = 0) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  rrect(ctx, -560, -560, 1120, 560, 6); paint(ctx, '#e9d2bd', 7);
  poly(ctx, [[-600, -560], [600, -560], [520, -660], [-520, -660]]); paint(ctx, '#c9573a', 7);
  rrect(ctx, -220, -720, 440, 90, 10); paint(ctx, '#2d3a6b', 6); text(ctx, UNI_NAME, 0, -676, { size: 58, fill: '#ffd23f', lw: 0 });
  for (let r = 0; r < 3; r++) for (let c = 0; c < 8; c++) { if (c === 3 || c === 4) { if (r === 2) continue; } nightWin(ctx, -500 + c * 128, -520 + r * 150, 84, 100, hash(r * 8 + c) > 0.25, r * 8 + c); }
  rrect(ctx, -130, -260, 260, 260, 8); paint(ctx, '#7c5a4a', 6); rrect(ctx, -110, -240, 100, 240, 4); paint(ctx, '#ffe9b0', 4); rrect(ctx, 10, -240, 100, 240, 4); paint(ctx, '#ffe9b0', 4);
  for (const k of [-1, 1]) { rrect(ctx, k * 170 - 18, -300, 36, 300, 8); paint(ctx, '#fff6e6', 5); }
  ctx.restore();
}
export function streetLamp(ctx, x, y, s = 1, glow = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  if (glow > 0) { ctx.save(); ctx.globalAlpha = 0.4 * glow; const g = ctx.createRadialGradient(0, -420, 10, 0, -200, 520); g.addColorStop(0, '#fff2b0'); g.addColorStop(1, 'rgba(255,230,150,0)'); ctx.fillStyle = g; poly(ctx, [[-30, -430], [30, -430], [380, 40], [-380, 40]]); ctx.fill(); ctx.restore(); }
  rrect(ctx, -10, -430, 20, 430, 8); paint(ctx, '#3a3f5c', 5); rrect(ctx, -60, -460, 120, 36, 16); paint(ctx, '#3a3f5c', 5); oval(ctx, 0, -424, 46, 10); paint(ctx, '#fff6b0', 3);
  ctx.restore();
}
export function campus(ctx, t, { lamp = 1 } = {}) {
  st.nightSky(ctx, t, { horizon: 760 });
  uniBuilding(ctx, 1020, 780, 1.0, t);
  for (const [x, r] of [[180, 150], [1820, 170]]) { rrect(ctx, x - 22, 560, 44, 230, 14); paint(ctx, '#5a4030', 6); for (const [dx, dy, rr] of [[-60, 520, r * 0.7], [50, 500, r * 0.75], [0, 430, r * 0.8]]) { circle(ctx, x + dx, dy, rr); paint(ctx, '#2f6e4f', 7); } }
  ctx.fillStyle = '#5c5f86'; ctx.fillRect(-1000, 780, 4000, 1000); ctx.fillStyle = '#6d7098'; ctx.fillRect(-1000, 780, 4000, 70);
  ctx.beginPath(); ctx.moveTo(-1000, 780); ctx.lineTo(3000, 780); paint(ctx, null, 4);
  streetLamp(ctx, 1420, 860, 1.25, lamp);
}
// a night classroom: dark windows, strip lights, the big whiteboard (writing reveals with k)
export function classroom(ctx, t, { write = 0 } = {}) {
  ctx.fillStyle = '#d9e2ef'; ctx.fillRect(-1000, -1000, 4000, 1780); ctx.fillStyle = '#c4cfe0'; ctx.fillRect(-1000, 650, 4000, 130);
  for (const wx of [-260, 1780]) { rrect(ctx, wx, 140, 360, 380, 8); paint(ctx, '#232a5a', 7); for (let i = 0; i < 18; i++) { circle(ctx, wx + 20 + hash(i) * 320, 160 + hash(i * 3) * 340, 2 + hash(i * 5) * 3); ctx.fillStyle = '#fff6d8'; ctx.fill(); } ctx.beginPath(); ctx.moveTo(wx + 180, 140); ctx.lineTo(wx + 180, 520); paint(ctx, null, 7, '#ffffff'); }
  for (const lx of [300, 960, 1620]) { rrect(ctx, lx - 160, -10, 320, 24, 10); paint(ctx, '#f4f8ff', 5); }
  rrect(ctx, 300, 120, 1320, 520, 12); paint(ctx, '#8e99a5', 8); rrect(ctx, 320, 140, 1280, 480, 6); paint(ctx, '#ffffff', 4);
  rrect(ctx, 320, 620, 1280, 22, 6); paint(ctx, '#b7c0cc', 4);
  // the professor's writing, revealed left to right
  if (write > 0) {
    ctx.save(); ctx.beginPath(); ctx.rect(320, 140, 1280 * clamp(write * 1.15), 480); ctx.clip();
    text(ctx, 'ការពារសារណា', 960, 300, { size: 120, fill: '#2f6fe0', lw: 0 });
    text(ctx, '– ១ ខែទៀត –', 960, 440, { size: 96, fill: '#e8433a', lw: 0 });
    text(ctx, 'Thesis Defense – 1 Month', 960, 552, { size: 52, font: 'Arial Black', fill: '#2d3a6b', lw: 0 });
    ctx.restore();
  }
  ctx.fillStyle = '#b48a6a'; ctx.fillRect(-1000, 780, 4000, 1000); ctx.beginPath(); ctx.moveTo(-1000, 780); ctx.lineTo(3000, 780); paint(ctx, null, 4);
}
export function schoolDesk(ctx, x, y, s = 1) { ctx.save(); ctx.translate(x, y); ctx.scale(s, s); poly(ctx, [[-130, 0], [130, 0], [146, 24], [-146, 24]]); paint(ctx, '#e6b98c', 6); rrect(ctx, -146, 24, 292, 18, 5); paint(ctx, '#c9915a', 5); for (const k of [-1, 1]) { rrect(ctx, k * 120 - 8, 42, 16, 150, 5); paint(ctx, '#7c8599', 5); } ctx.restore(); }
// an extra student (back view mostly): a one-off look built from a seed
export function student(i) {
  const shirts = ['#ffffff', '#f2c94c', '#9fd6e8', '#ffb3c1', '#c9e6a0', '#e0d0ff'], hairS = ['short', 'neat', 'ponytail', 'bob', 'short', 'wavy'];
  const h = hairS[i % hairS.length];
  return { H: 380 + (i % 3) * 18, legs: 0.4, torso: 0.29, headS: 1.5, hx: 0.95, hy: 1.03, belly: 0, arm: 60, nose: 'button', sw: 40, ww: 36, skin: ['#d9a07a', '#c98f68', '#e0a378'][i % 3], skinD: '#b07a55', hair: '#221d24', gray: '#221d24',
    shirt: shirts[i % shirts.length], shirtD: '#d6d6e0', collar: '#ffffff', pants: '#2f3e66', pantsD: '#22305a', shoe: '#3a2a22', style: 'tee', hairStyle: h, tie: '#ff5c8a', clip: '#46c34f', eyeSize: 1.1, lashes: h === 'ponytail' || h === 'bob' || h === 'wavy', thinBrows: h !== 'short' && h !== 'neat' };
}
// the university corridor at night (scroll for the tracking shot)
export function uniHall(ctx, t, scroll = 0) {
  ctx.fillStyle = '#e9e1f2'; ctx.fillRect(-1000, -1000, 4000, 1780); ctx.fillStyle = '#d4c8e2'; ctx.fillRect(-1000, 600, 4000, 180);
  const P = 760;
  for (let k = -1; k < 5; k++) {
    const x = k * P - (scroll % P);
    rrect(ctx, x + 60, 180, 300, 360, 8); paint(ctx, '#232a5a', 7); circle(ctx, x + 300, 250, 24); ctx.fillStyle = '#fff3d6'; ctx.fill(); for (let i = 0; i < 8; i++) { circle(ctx, x + 80 + hash(i + k) * 260, 200 + hash(i * 3 + k) * 320, 2.5); ctx.fillStyle = '#fff6d8'; ctx.fill(); }
    ctx.beginPath(); ctx.moveTo(x + 210, 180); ctx.lineTo(x + 210, 540); paint(ctx, null, 6, '#ffffff');
    rrect(ctx, x + 440, 200, 220, 580, 8); paint(ctx, '#b7865c', 6); rrect(ctx, x + 470, 240, 160, 110, 6); paint(ctx, '#ffe9b0', 4); circle(ctx, x + 630, 520, 10); paint(ctx, '#ffd23f', 3);
    rrect(ctx, x + 460, 140, 180, 46, 8); paint(ctx, '#ffffff', 4); text(ctx, `បន្ទប់ ${'០១២៣៤៥៦៧៨៩'[(k + 12) % 10]}០${'១២៣៤'[(k + 4) % 4]}`, x + 550, 164, { size: 28, fill: '#2d3a6b', lw: 0 });
  }
  for (let k = -1; k < 6; k++) { const lx = k * 520 - (scroll * 1.0 % 520); rrect(ctx, lx - 120, 30, 240, 22, 10); paint(ctx, '#fff6d8', 5); }
  ctx.fillStyle = '#a99cbd'; ctx.fillRect(-1000, 780, 4000, 1000); ctx.save(); ctx.globalAlpha = 0.25; for (let k = -1; k < 6; k++) { const lx = k * 520 - (scroll % 520); oval(ctx, lx, 900, 160, 30); ctx.fillStyle = '#ffffff'; ctx.fill(); } ctx.restore();
  ctx.beginPath(); ctx.moveTo(-1000, 780); ctx.lineTo(3000, 780); paint(ctx, null, 4);
}
// night street for the motorbike ride: lit shophouses scrolling, street lamps, the road
export function nightStreet(ctx, t, scroll) {
  st.nightSky(ctx, t, { horizon: 700 });
  const pal = ['#8a6aa0', '#4f6a9a', '#a0606a', '#5f8a8a', '#7a6aa0'], P = 1620;
  for (let k = -1; k < 3; k++) for (let i = 0; i < 6; i++) {
    const bx = ((i * 270 - scroll * 0.6) % P + P) % P + k * P - 300; if (bx < -400 || bx > 2200) continue;
    const hh = 380 + (i % 3) * 70;
    rrect(ctx, bx, 810 - hh, 260, hh, 4); paint(ctx, pal[(i + k + 6) % pal.length], 5);
    for (let r = 0; r < Math.floor(hh / 130); r++) for (let c = 0; c < 2; c++) nightWin(ctx, bx + 36 + c * 120, 810 - hh + 40 + r * 120, 70, 80, hash(i * 7 + r * 3 + c + k) > 0.3, i + r);
    rrect(ctx, bx + 10, 700, 240, 26, 4); paint(ctx, ['#ff9fb2', '#9fe3c9', '#ffd98a'][i % 3], 4);
  }
  ctx.fillStyle = '#4a4d70'; ctx.fillRect(-1000, 810, 4000, 60); ctx.fillStyle = '#34365a'; ctx.fillRect(-1000, 870, 4000, 400);
  ctx.fillStyle = '#fff6e6'; for (let x = -((scroll * 1.0) % 220) - 220; x < 2200; x += 220) { rrect(ctx, x, 990, 110, 12, 6); ctx.fill(); }
  for (let x = -((scroll * 1.0) % 700) - 700; x < 2400; x += 700) streetLamp(ctx, x, 830, 0.95, 0.8);
}
// side-view scooter facing right; riders(ctx) is called between the body and the front fairing
export function moto(ctx, x, y, s, t, riders, { moving = 1 } = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const bob = Math.sin(t * 18) * 2 * moving;
  for (const wx of [-120, 130]) { circle(ctx, wx, -44, 46); paint(ctx, '#2a2633', 6); circle(ctx, wx, -44, 20); paint(ctx, '#c9ccd6', 4); ctx.save(); ctx.translate(wx, -44); ctx.rotate(t * 14 * moving); for (let i = 0; i < 3; i++) { ctx.rotate(TAU / 3); ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, 18); paint(ctx, null, 3); } ctx.restore(); }
  ctx.translate(0, bob);
  smooth(ctx, [[-170, -80], [-110, -150], [40, -140], [120, -110], [150, -60], [70, -40], [-60, -40], [-170, -50]]); paint(ctx, '#e8433a', 6);
  rrect(ctx, -150, -176, 190, 34, 16); paint(ctx, '#2a2633', 6);
  riders && riders(ctx, bob);
  smooth(ctx, [[60, -120], [120, -210], [160, -200], [170, -110], [140, -70]]); paint(ctx, '#e8433a', 6);
  ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(140, -210); ctx.lineTo(110, -250); paint(ctx, null, 8); rrect(ctx, 80, -262, 70, 16, 8); paint(ctx, '#3a3946', 4);
  oval(ctx, 178, -150, 14, 18); paint(ctx, '#fff6b0', 4);
  if (moving) { ctx.save(); ctx.globalAlpha = 0.3; poly(ctx, [[186, -160], [560, -230], [560, -60], [186, -140]]); ctx.fillStyle = '#fff6b0'; ctx.fill(); ctx.restore(); }
  ctx.restore();
}
// David's small room at night (desk drawn by the caller)
export function davidRoom(ctx, t, { lamp = 1 } = {}) {
  ctx.fillStyle = '#4a4e86'; ctx.fillRect(-1000, -1000, 4000, 1780); ctx.fillStyle = '#41457a'; ctx.fillRect(-1000, 660, 4000, 120);
  // window: moon over city lights
  ctx.save(); rrect(ctx, 1240, 120, 480, 380, 10); ctx.clip(); st.nightSky(ctx, t, { horizon: 520 }); for (let i = 0; i < 9; i++) { const bx = 1240 + i * 56, hh = 80 + hash(i) * 120; ctx.fillStyle = '#2a2d55'; ctx.fillRect(bx, 500 - hh, 50, hh); for (let r = 0; r < 4; r++) { if (hash(i * 5 + r) > 0.5) { ctx.fillStyle = '#ffd98a'; ctx.fillRect(bx + 12, 510 - hh + r * 26, 10, 12); } } } ctx.restore();
  rrect(ctx, 1240, 120, 480, 380, 10); paint(ctx, null, 9, '#e9e1f2'); ctx.beginPath(); ctx.moveTo(1480, 120); ctx.lineTo(1480, 500); paint(ctx, null, 8, '#e9e1f2');
  // posters + a calendar with the defence date circled
  ctx.save(); ctx.translate(320, 250); ctx.rotate(-0.04); rrect(ctx, -130, -110, 260, 200, 6); paint(ctx, '#ffd98a', 5); text(ctx, 'កុំបោះបង់!', 0, -40, { size: 52, fill: '#e8433a', lw: 0 }); text(ctx, "DON'T GIVE UP", 0, 30, { size: 26, font: 'Arial Black', fill: '#2d3a6b', lw: 0 }); ctx.restore();
  ctx.save(); ctx.translate(760, 230); rrect(ctx, -100, -90, 200, 190, 6); paint(ctx, '#ffffff', 5); rrect(ctx, -100, -90, 200, 44, 6); paint(ctx, '#e8433a', 5); for (let r = 0; r < 4; r++) for (let c = 0; c < 6; c++) { rrect(ctx, -86 + c * 29, -36 + r * 30, 22, 22, 3); ctx.fillStyle = '#e3e6ee'; ctx.fill(); } ctx.beginPath(); ctx.ellipse(-86 + 4 * 29 + 11, -36 + 3 * 30 + 11, 20, 18, 0, 0, TAU - 0.01); paint(ctx, null, 4, '#e8433a'); ctx.restore();
  // shelf of books
  rrect(ctx, 40, 470, 420, 18, 4); paint(ctx, '#8a5a3c', 5); for (let i = 0; i < 9; i++) { rrect(ctx, 60 + i * 42, 470 - 90 - (i % 3) * 14, 34, 90 + (i % 3) * 14, 4); paint(ctx, ['#e8433a', '#3f8bd0', '#ffd23f', '#46c34f', '#a07bff'][i % 5], 4); }
  ctx.fillStyle = '#6a5a7a'; ctx.fillRect(-1000, 780, 4000, 1000); ctx.beginPath(); ctx.moveTo(-1000, 780); ctx.lineTo(3000, 780); paint(ctx, null, 4);
  if (lamp < 1) { ctx.save(); ctx.fillStyle = `rgba(10,12,40,${(1 - lamp) * 0.5})`; ctx.fillRect(-1000, -1000, 4000, 3000); ctx.restore(); }
}
// a cosy home behind each sender in the split screen
export function homePanel(ctx, x, y, w, h, col, t, i = 0) {
  ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
  ctx.fillStyle = col; ctx.fillRect(x, y, w, h); ctx.fillStyle = 'rgba(0,0,0,0.1)'; ctx.fillRect(x, y + h * 0.7, w, h * 0.3);
  rrect(ctx, x + w * 0.15, y + h * 0.12, w * 0.32, h * 0.22, 6); paint(ctx, '#232a5a', 5); circle(ctx, x + w * 0.38, y + h * 0.18, 10); ctx.fillStyle = '#fff3d6'; ctx.fill();
  ctx.save(); ctx.globalAlpha = 0.3; const g = ctx.createRadialGradient(x + w * 0.75, y + h * 0.25, 10, x + w * 0.75, y + h * 0.25, w * 0.6); g.addColorStop(0, '#fff2b0'); g.addColorStop(1, 'rgba(255,230,150,0)'); ctx.fillStyle = g; ctx.fillRect(x, y, w, h); ctx.restore();
  rrect(ctx, x + w * 0.68, y + h * 0.1, w * 0.18, h * 0.14, 4); paint(ctx, ['#ffd98a', '#9fe3c9', '#ffb3c1', '#c9e6a0', '#e0d0ff'][i % 5], 4);
  ctx.restore();
}
// a polaroid: draw(ctx) paints a full 1920x1080 frame which is shrunk into the photo
export function polaroid(ctx, x, y, w, rot, k, draw, caption = null) {
  if (k <= 0) return; const s = ease.back(clamp(k)), h = w * 9 / 16;
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  rrect(ctx, -w / 2 - 22 + 10, -h / 2 - 22 + 14, w + 44, h + 110, 6); ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.fill();
  rrect(ctx, -w / 2 - 22, -h / 2 - 22, w + 44, h + 110, 6); paint(ctx, '#fffdf6', 5);
  ctx.save(); ctx.beginPath(); ctx.rect(-w / 2, -h / 2, w, h); ctx.clip(); ctx.translate(-w / 2, -h / 2); ctx.scale(w / W, h / H); draw(ctx); ctx.restore();
  ctx.beginPath(); ctx.rect(-w / 2, -h / 2, w, h); paint(ctx, null, 3);
  if (caption) text(ctx, caption, 0, h / 2 + 44, { size: Math.min(46, w / 9), fill: '#2d3a6b', lw: 0 });
  ctx.restore();
}
// mortarboard + gown drawn over a person (anchors from people.anchors)
export function gradCap(ctx, x, y, s = 1, rot = 0, t = 0) { ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s); rrect(ctx, -44, -10, 88, 34, 10); paint(ctx, '#2a2633', 6); poly(ctx, [[0, -40], [92, -14], [0, 12], [-92, -14]]); paint(ctx, '#2a2633', 6); circle(ctx, 0, -14, 7); paint(ctx, '#ffd23f', 3); const sw = Math.sin(t * 3) * 6; ctx.beginPath(); ctx.moveTo(0, -14); ctx.quadraticCurveTo(50, -10, 70 + sw * 0.3, 30); paint(ctx, null, 4, '#ffd23f'); rrect(ctx, 62 + sw * 0.3, 28, 16, 26, 6); paint(ctx, '#ffd23f', 3); ctx.restore(); }
export function gown(ctx, a, s = 1) { const [lx, ly] = a.shL, [rx] = a.shR, cx = (lx + rx) / 2; poly(ctx, [[lx - 16 * s, ly - 6 * s], [rx + 16 * s, ly - 6 * s], [rx + 60 * s, ly + 230 * s], [lx - 60 * s, ly + 230 * s]]); paint(ctx, '#2a2633', 6); poly(ctx, [[cx - 30 * s, ly - 8 * s], [cx + 30 * s, ly - 8 * s], [cx, ly + 60 * s]]); paint(ctx, '#e8433a', 5); }
