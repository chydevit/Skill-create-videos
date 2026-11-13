// Episode 7 "គីមឡុង ស្ដេចញ៉ែ": props and effects only this episode needs
// (flirting sparkles, the «ប្លុក!» rejection, name cards, the camera + tripod + viewfinder, the meeting room, sunflowers, the photo).
import { W, H, INK, TAU, LW, paint, circle, oval, rrect, poly, smooth, text, clamp, lerp, seg, ease, hash } from './core.mjs';
import { person, CAST, camera } from './people.mjs';
import * as st from './sets.mjs';
import * as pl from './places.mjs';
import * as fx from './fx.mjs';
import { ICON, tag } from './ep6.mjs';

const fit = (ctx, s, size, maxW) => { ctx.font = `${size}px "Koulen"`; return Math.min(size, size * maxW / ctx.measureText(s).width); };
const heartPath = (ctx, x, y, s) => { ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.beginPath(); ctx.moveTo(0, 30); ctx.bezierCurveTo(-60, -10, -30, -55, 0, -25); ctx.bezierCurveTo(30, -55, 60, -10, 0, 30); ctx.closePath(); ctx.restore(); };
export const sparkle = (ctx, x, y, r, col = '#fff3a0', lw = 4) => { ctx.beginPath(); for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4, rr = i % 2 ? r * 0.28 : r; ctx.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); } ctx.closePath(); paint(ctx, col, lw); };

// ---------------------------------------------------------------- more sticker icons (same ~100 px box as ep6's)
Object.assign(ICON, {
  cool(ctx) { circle(ctx, 0, 0, 38); paint(ctx, '#ffd23f', 5); rrect(ctx, -34, -16, 30, 20, 8); paint(ctx, '#2a2633', 4); rrect(ctx, 4, -16, 30, 20, 8); paint(ctx, '#2a2633', 4); ctx.beginPath(); ctx.moveTo(-4, -8); ctx.lineTo(4, -8); paint(ctx, null, 4); ctx.beginPath(); ctx.moveTo(-14, 16); ctx.quadraticCurveTo(4, 28, 18, 12); paint(ctx, null, 5); },
  fist(ctx) { for (const k of [-1, 1]) { ctx.save(); ctx.translate(k * 22, 0); ctx.scale(k, 1); rrect(ctx, -26, -20, 34, 40, 12); paint(ctx, '#ffcc4d', 4); for (let i = 0; i < 3; i++) { ctx.beginPath(); ctx.moveTo(-2, -10 + i * 10); ctx.lineTo(8, -10 + i * 10); paint(ctx, null, 3); } rrect(ctx, -44, -12, 22, 24, 6); paint(ctx, '#ffcc4d', 4); ctx.restore(); } },
  crown(ctx) { poly(ctx, [[-42, 22], [-46, -24], [-22, 0], [0, -34], [22, 0], [46, -24], [42, 22]]); paint(ctx, '#ffd23f', 5); for (const [x, y, c] of [[-24, 10, '#e8433a'], [0, 10, '#3fb3ff'], [24, 10, '#46c34f']]) { circle(ctx, x, y, 6); paint(ctx, c, 3); } },
  broken(ctx) { for (const k of [-1, 1]) { ctx.save(); ctx.translate(k * 7, k * 3); ctx.rotate(k * 0.12); ctx.beginPath(); ctx.rect(k > 0 ? 0 : -60, -60, 60, 120); ctx.clip(); heartPath(ctx, 0, 4, 0.62); paint(ctx, '#e8433a', 5); ctx.restore(); } ctx.beginPath(); ctx.moveTo(0, -18); ctx.lineTo(-6, -4); ctx.lineTo(6, 6); ctx.lineTo(-2, 20); paint(ctx, null, 4); },
  sunflower(ctx) { for (let i = 0; i < 12; i++) { ctx.save(); ctx.rotate(i * TAU / 12); oval(ctx, 0, -28, 10, 18); paint(ctx, '#ffc61a', 3.5); ctx.restore(); } circle(ctx, 0, 0, 18); paint(ctx, '#7a4a22', 4); for (let i = 0; i < 6; i++) { circle(ctx, Math.cos(i) * 8, Math.sin(i * 1.7) * 8, 2.5); ctx.fillStyle = '#4a2c14'; ctx.fill(); } },
  cam(ctx) { camera(ctx, 0, 4, 1.1); },
  sparkles(ctx) { sparkle(ctx, -14, -6, 30); sparkle(ctx, 24, 18, 16); sparkle(ctx, 26, -26, 12); },
  wink(ctx) { circle(ctx, 0, 0, 38); paint(ctx, '#ffd23f', 5); circle(ctx, -14, -8, 6); ctx.fillStyle = INK; ctx.fill(); ctx.beginPath(); ctx.moveTo(6, -6); ctx.quadraticCurveTo(14, -16, 22, -6); paint(ctx, null, 5); ctx.beginPath(); ctx.moveTo(-16, 12); ctx.quadraticCurveTo(2, 28, 20, 10); paint(ctx, null, 5); },
});

// ---------------------------------------------------------------- flirting: ✨💕 orbiting his face (k = 0..1 strength)
export function flirtFx(ctx, hx, hy, t, k = 1, s = 1) {
  if (k <= 0) return;
  ctx.save(); ctx.globalAlpha = Math.min(1, k * 2);
  for (let i = 0; i < 6; i++) {
    const a = t * 1.6 + i * TAU / 6, r = (130 + Math.sin(t * 3 + i) * 14) * s, x = hx + Math.cos(a) * r * 1.15, y = hy - 10 * s + Math.sin(a) * r * 0.7, b = ease.back(clamp(k * 1.5 - i * 0.08));
    if (b <= 0) continue;
    if (i % 2) { heartPath(ctx, x, y, 0.36 * s * b * (1 + Math.sin(t * 9 + i) * 0.12)); paint(ctx, i % 4 === 1 ? '#ff4d6d' : '#ff8fab', 4); }
    else sparkle(ctx, x, y, 20 * s * b * (0.8 + 0.3 * Math.sin(t * 7 + i)));
  }
  ctx.restore();
}
// «ប្លុក!» — the flirt bounces off: a grey cloud word with a little drop
export function plok(ctx, x, y, lt, at) { if (lt < at) return; fx.sfxText(ctx, 'ប្លុក!', x, y, seg(lt, at, at + 1.1), { size: 104, fill: '#a4aab8', rot: 0.08 }); }

// ---------------------------------------------------------------- name card: name chip over a role line (+ icons)
export function nameCard(ctx, x, y, name, role, k, { icon = null, icon2 = null, col = '#fff6e6', ink = '#2d3a6b', size = 52, rot = -0.03 } = {}) {
  tag(ctx, x, y, role, k, { icon, icon2, col, ink, size, rot, chip: name });
}

// ---------------------------------------------------------------- a notepad (the waitress)
export function notepad(ctx, x, y, s = 1, rot = 0) { ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s); rrect(ctx, -26, -34, 52, 68, 5); paint(ctx, '#fffaf0', 4); rrect(ctx, -26, -40, 52, 12, 4); paint(ctx, '#e8433a', 3.5); for (let i = 0; i < 4; i++) { ctx.beginPath(); ctx.moveTo(-16, -14 + i * 12); ctx.lineTo(14 - (i % 2) * 10, -14 + i * 12); paint(ctx, null, 2.5, '#9aa3b5'); } ctx.restore(); }
// a folder of documents (Channy)
export function folder(ctx, x, y, s = 1, rot = 0) { ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s); rrect(ctx, -34, -44, 68, 88, 5); paint(ctx, '#3f8bd0', 4.5); rrect(ctx, -26, -50, 54, 12, 3); paint(ctx, '#ffffff', 3); rrect(ctx, -20, -20, 40, 26, 3); paint(ctx, '#ffffff', 3); ctx.restore(); }

// ---------------------------------------------------------------- tripod + camera (rec: red light blinks; timer: countdown light)
export function tripod(ctx, x, y, s = 1, t = 0, { rec = false, timer = 0 } = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.lineCap = 'round';
  for (const a of [-0.28, 0.02, 0.3]) { ctx.beginPath(); ctx.moveTo(0, -250); ctx.lineTo(Math.sin(a) * 260, 0); paint(ctx, null, 13); ctx.beginPath(); ctx.moveTo(0, -250); ctx.lineTo(Math.sin(a) * 260, 0); paint(ctx, null, 6, '#8a8d99'); }
  rrect(ctx, -10, -300, 20, 60, 5); paint(ctx, '#55525e', 4);
  camera(ctx, 0, -326, 1.25, 0, rec, t);
  if (timer > 0) { const on = Math.sin(t * (6 + timer * 14)) > 0; circle(ctx, 30, -350, 9); ctx.fillStyle = on ? '#ff5c3b' : '#6b6875'; ctx.fill(); }
  ctx.restore();
}
export function tripodSide(ctx, x, y, s = 1, t = 0, { rec = true, dir = -1 } = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.lineCap = 'round';
  for (const a of [-0.3, 0.05, 0.32]) { ctx.beginPath(); ctx.moveTo(0, -250); ctx.lineTo(Math.sin(a) * 240, 0); paint(ctx, null, 13); ctx.beginPath(); ctx.moveTo(0, -250); ctx.lineTo(Math.sin(a) * 240, 0); paint(ctx, null, 6, '#8a8d99'); }
  rrect(ctx, -10, -300, 20, 60, 5); paint(ctx, '#55525e', 4);
  ctx.save(); ctx.translate(0, -330); ctx.scale(dir < 0 ? 1 : -1, 1);
  rrect(ctx, -40, -30, 80, 56, 8); paint(ctx, '#2a2730', LW * 0.8); rrect(ctx, -86, -20, 50, 38, 6); paint(ctx, '#3d3a46', 4); oval(ctx, -88, -1, 6, 17); paint(ctx, '#5b7fb0', 3);
  rrect(ctx, 24, -22, 30, 22, 4); paint(ctx, '#9fd6e8', 3);
  circle(ctx, 30, -38, 6); ctx.fillStyle = rec && Math.sin(t * 8) > -0.3 ? '#ff3b3b' : '#6b6875'; ctx.fill();
  ctx.restore(); ctx.restore();
}
// what the camera sees: frame corners, REC ●, timecode, battery (draw over a scene)
export function viewfinder(ctx, t, lt, { label = 'REC' } = {}) {
  ctx.save(); ctx.lineCap = 'square';
  ctx.fillStyle = 'rgba(0,0,0,0.12)'; ctx.fillRect(0, 0, W, H);
  for (const [x, y, sx, sy] of [[80, 80, 1, 1], [W - 80, 80, -1, 1], [80, H - 80, 1, -1], [W - 80, H - 80, -1, -1]]) { ctx.beginPath(); ctx.moveTo(x, y + sy * 90); ctx.lineTo(x, y); ctx.lineTo(x + sx * 90, y); paint(ctx, null, 8, '#ffffff'); }
  ctx.beginPath(); ctx.moveTo(W / 2 - 40, H / 2); ctx.lineTo(W / 2 + 40, H / 2); ctx.moveTo(W / 2, H / 2 - 40); ctx.lineTo(W / 2, H / 2 + 40); paint(ctx, null, 3, 'rgba(255,255,255,0.7)');
  if (Math.sin(t * 6) > -0.2) { circle(ctx, 150, 150, 18); ctx.fillStyle = '#ff3b3b'; ctx.fill(); }
  text(ctx, label, 236, 152, { size: 52, font: 'Arial Black', fill: '#ffffff', lw: 7 });
  const s = Math.floor(lt), f = Math.floor((lt % 1) * 24);
  text(ctx, `00:00:${String(s).padStart(2, '0')}:${String(f).padStart(2, '0')}`, W - 330, 152, { size: 40, font: 'Courier New', fill: '#ffffff', lw: 6 });
  rrect(ctx, W - 230, H - 170, 100, 46, 8); paint(ctx, null, 5, '#ffffff'); rrect(ctx, W - 222, H - 162, 70, 30, 4); ctx.fillStyle = '#ffffff'; ctx.fill(); rrect(ctx, W - 128, H - 156, 8, 18, 2); ctx.fillStyle = '#ffffff'; ctx.fill();
  text(ctx, '4K  24fps', 250, H - 140, { size: 34, font: 'Arial Black', fill: '#ffffff', lw: 6 });
  ctx.restore();
}

// ---------------------------------------------------------------- the meeting room: a big screen with David's slides, chairs, a plant
export function slide(ctx, x, y, w, h, n = 0) {
  ctx.save(); rrect(ctx, x, y, w, h, 8); ctx.clip();
  ctx.fillStyle = '#ffffff'; ctx.fillRect(x, y, w, h); ctx.fillStyle = '#2d3a6b'; ctx.fillRect(x, y, w, h * 0.2);
  if (n === 3) { ctx.fillStyle = '#ffe3ec'; ctx.fillRect(x, y, w, h); ctx.save(); ctx.translate(x + w / 2, y + h * 0.42); ctx.scale(h / 260, h / 260); ICON.heart(ctx); ctx.restore(); text(ctx, 'គ្រួសារ Office', x + w / 2, y + h * 0.78, { size: h * 0.15, fill: '#e8433a', lw: 0 }); ctx.restore(); rrect(ctx, x, y, w, h, 8); paint(ctx, null, 6); return; }
  text(ctx, ['សារណាបញ្ចប់ការសិក្សា', 'ប្រធានបទ', 'លទ្ធផល'][n % 3], x + w / 2, y + h * 0.11, { size: h * 0.11, fill: '#ffffff', lw: 0 });
  if (n % 3 === 0) { text(ctx, 'ដេវីត', x + w / 2, y + h * 0.5, { size: h * 0.16, fill: '#e8433a', lw: 0 }); text(ctx, 'Final Year Thesis', x + w / 2, y + h * 0.72, { size: h * 0.08, font: 'Arial Black', fill: '#2d3a6b', lw: 0 }); }
  else if (n % 3 === 1) { for (let i = 0; i < 4; i++) { circle(ctx, x + w * 0.12, y + h * (0.36 + i * 0.15), h * 0.025); ctx.fillStyle = '#e8433a'; ctx.fill(); rrect(ctx, x + w * 0.18, y + h * (0.34 + i * 0.15), w * (0.6 - (i % 2) * 0.18), h * 0.04, 4); ctx.fillStyle = '#c9cfdc'; ctx.fill(); } }
  else { for (let i = 0; i < 5; i++) { const bh = h * (0.15 + i * 0.1); rrect(ctx, x + w * (0.14 + i * 0.15), y + h * 0.88 - bh, w * 0.1, bh, 4); paint(ctx, ['#3fb3ff', '#46c34f', '#ffd23f', '#ff9a3f', '#e8433a'][i], 3); } }
  ctx.restore(); rrect(ctx, x, y, w, h, 8); paint(ctx, null, 6);
}
export function meetingRoom(ctx, t, { slideN = 0, door = 0, gold = 0 } = {}) {
  ctx.fillStyle = '#e8eef6'; ctx.fillRect(-1000, -1000, 4000, 1780);
  ctx.fillStyle = '#c9a77c'; ctx.fillRect(-1000, 780, 4000, 1000); ctx.fillStyle = '#b8936a'; ctx.fillRect(-1000, 776, 4000, 10);
  for (let i = 0; i < 12; i++) { ctx.fillStyle = 'rgba(255,255,255,0.08)'; ctx.fillRect(-1000 + i * 340, 786, 160, 1000); }
  // wall stripe + the screen
  ctx.fillStyle = '#d3deec'; ctx.fillRect(-1000, 560, 4000, 220);
  rrect(ctx, 150, 120, 760, 450, 14); paint(ctx, '#2a2633', 8); slide(ctx, 172, 142, 716, 406, slideN);
  // window (right) and the door (far right)
  rrect(ctx, 1080, 150, 360, 300, 10); paint(ctx, gold ? '#ffc98a' : '#bfe6ff', 7); ctx.beginPath(); ctx.moveTo(1260, 150); ctx.lineTo(1260, 450); ctx.moveTo(1080, 300); ctx.lineTo(1440, 300); paint(ctx, null, 6);
  for (const [x, h] of [[1110, 90], [1170, 140], [1230, 70], [1300, 120], [1370, 100]]) { ctx.fillStyle = 'rgba(80,110,160,0.35)'; ctx.fillRect(x, 450 - h, 46, h); }
  rrect(ctx, 1660, 220, 220, 560, 8); paint(ctx, '#3d3550', 6);
  ctx.save(); ctx.translate(1660, 220); ctx.scale(1 - door * 0.8, 1); rrect(ctx, 0, 0, 220, 560, 8); paint(ctx, '#d6a986', 5); circle(ctx, 190, 290, 10); paint(ctx, '#fbe3a2', 3); ctx.restore();
  // a plant by the screen
  rrect(ctx, 20, 680, 70, 100, 10); paint(ctx, '#e07a5f', 5); for (let i = 0; i < 5; i++) { ctx.save(); ctx.translate(55, 690); ctx.rotate(-0.9 + i * 0.45); oval(ctx, 0, -60, 18, 60); paint(ctx, '#46a35a', 4); ctx.restore(); }
}

// ---------------------------------------------------------------- sunflowers raining down (slow motion), k = 0..1 strength
export function sunflowers(ctx, t, k = 1, n = 26) {
  if (k <= 0) return;
  ctx.save(); ctx.globalAlpha = Math.min(1, k * 2);
  for (let i = 0; i < n; i++) {
    const sp = 0.05 + hash(i * 3.1) * 0.06, y = ((hash(i) * 1.4 + t * sp) % 1.3) * (H + 300) - 200, x = hash(i * 7.7) * W + Math.sin(t * 0.8 + i) * 50;
    ctx.save(); ctx.translate(x, y); ctx.rotate(t * 0.4 * (i % 2 ? 1 : -1) + i); const s = (0.5 + hash(i * 1.3) * 0.7) * ease.back(clamp(k * 1.4 - hash(i * 5) * 0.3)); ctx.scale(s, s); ICON.sunflower(ctx); ctx.restore();
  }
  ctx.restore();
}
// soft dreamy glow for the slow-motion moment
export function dreamGlow(ctx, k) { if (k <= 0) return; ctx.save(); ctx.globalAlpha = 0.5 * k; const g = ctx.createRadialGradient(W / 2, H / 2, 200, W / 2, H / 2, 1100); g.addColorStop(0, 'rgba(255,240,200,0)'); g.addColorStop(1, 'rgba(255,190,120,0.9)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); ctx.restore(); }
// a scoreboard card: «ឈ្នះហ្គេម ១០០% 🏆 | ឈ្នះស្នេហា ០% 💔»
export function scoreCard(ctx, x, y, k, t) {
  if (k <= 0) return; const s = ease.back(clamp(k));
  ctx.save(); ctx.translate(x, y); ctx.rotate(-0.03); ctx.scale(s, s);
  rrect(ctx, -620 + 12, -86 + 14, 1240, 172, 40); ctx.fillStyle = INK; ctx.fill();
  rrect(ctx, -620, -86, 620, 172, 40); paint(ctx, '#46c34f', 7); rrect(ctx, 0, -86, 620, 172, 40); paint(ctx, '#3d3a46', 7);
  ctx.save(); ctx.translate(-540, 0); ctx.scale(0.9, 0.9); ICON.trophy(ctx); ctx.restore(); text(ctx, 'ឈ្នះហ្គេម ១០០%', -270, 6, { size: 62, fill: '#ffffff', lw: 0 });
  ctx.save(); ctx.translate(540, 0); ctx.scale(0.95, 0.95); ctx.rotate(Math.sin(t * 9) * 0.08); ICON.broken(ctx); ctx.restore(); text(ctx, 'ឈ្នះស្នេហា ០%', 270, 6, { size: 62, fill: '#ff8fab', lw: 0 });
  rrect(ctx, -10, -96, 20, 192, 6); paint(ctx, '#fff6e6', 5);
  ctx.restore();
}
// the freeze-frame photo border (draw the scene inside first, then this on top); k = 0..1 for the flash → frame
export function photoFrame(ctx, k, rot = -0.02) {
  ctx.save(); ctx.translate(W / 2, H / 2); ctx.rotate(rot * k); const m = 70 * k;
  ctx.beginPath(); ctx.rect(-W, -H, W * 2, H * 2); ctx.rect(-W / 2 + m, -H / 2 + m * 0.7, W - 2 * m, H - m * 1.9); ctx.fillStyle = '#fffaf0'; ctx.fill('evenodd');
  ctx.lineWidth = 6; ctx.strokeStyle = INK; ctx.strokeRect(-W / 2 + m, -H / 2 + m * 0.7, W - 2 * m, H - m * 1.9);
  ctx.restore();
}
