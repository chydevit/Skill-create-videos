// Office series sets (first built for "Leanghak's First Day"): her home (morning / night), the street + office tower + tuk-tuk, the hallway
// with the two office doors, the tech team's office (desk row), her company's office, the lunch bench, a Khmer
// restaurant, the meeting-room slide, and props (mirror, offer letter, folders, lunch box, cake box, cat, heart).
import { W, H, INK, TAU, paint, circle, oval, rrect, poly, smooth, text, clamp, lerp, seg, ease, hash, rng } from './core.mjs';
import * as st from './sets.mjs';

const T = (ctx, s, x, y, size, fill, o = {}) => text(ctx, s, x, y, { size, fill, lw: 0, font: 'Arial Black', ...o });

// ---------------------------------------------------------------- her home (one room: mirror corner + practice corner)
export const MIRROR = { x: 1330, y: 400, rx: 165, ry: 235 };
export function home(ctx, t, { night = false } = {}) {
  ctx.fillStyle = night ? '#6b5d8f' : '#ffd9b8'; ctx.fillRect(-1000, -1000, 4000, 1780);
  ctx.fillStyle = night ? '#5a4d7c' : '#f5c49c'; ctx.fillRect(-1000, 690, 4000, 90);
  // window
  const wx = 110, wy = 140, ww = 480, wh = 400;
  ctx.save(); rrect(ctx, wx, wy, ww, wh, 10); ctx.clip();
  const g = ctx.createLinearGradient(0, wy, 0, wy + wh);
  if (night) { g.addColorStop(0, '#1f2048'); g.addColorStop(1, '#3d3f7a'); } else { g.addColorStop(0, '#ffb070'); g.addColorStop(1, '#ffe7b0'); }
  ctx.fillStyle = g; ctx.fillRect(wx, wy, ww, wh);
  if (night) { for (let i = 0; i < 30; i++) { circle(ctx, wx + hash(i) * ww, wy + hash(i * 3) * wh * 0.6, 2); ctx.fillStyle = '#fff6d8'; ctx.fill(); } circle(ctx, wx + 380, wy + 90, 40); ctx.fillStyle = '#fff3d6'; ctx.fill(); circle(ctx, wx + 398, wy + 78, 36); ctx.fillStyle = '#2a2b5a'; ctx.fill(); }
  else { circle(ctx, wx + 330, wy + 260, 70); ctx.fillStyle = '#fff3c4'; ctx.fill(); }
  const r = rng(7); for (let x = wx - 10; x < wx + ww;) { const w = 60 + r() * 60, h = 80 + r() * 120; ctx.fillStyle = night ? '#2c2f5c' : ['#e8875a', '#d9a05b', '#c97a64'][Math.floor(r() * 3)]; ctx.fillRect(x, wy + wh - h, w, h); if (night) for (let k = 0; k < 4; k++) { ctx.fillStyle = r() < 0.5 ? '#ffd98a' : '#3d4170'; ctx.fillRect(x + 10 + (k % 2) * 25, wy + wh - h + 15 + Math.floor(k / 2) * 30, 12, 14); } x += w + 6; }
  ctx.restore();
  rrect(ctx, wx, wy, ww, wh, 10); paint(ctx, null, 10, '#ffffff'); rrect(ctx, wx, wy, ww, wh, 10); paint(ctx, null, 4);
  ctx.beginPath(); ctx.moveTo(wx + ww / 2, wy); ctx.lineTo(wx + ww / 2, wy + wh); paint(ctx, null, 8, '#ffffff');
  for (const k of [0, 1]) { const cx = k ? wx + ww + 10 : wx - 60; smooth(ctx, [[cx, wy - 30], [cx + 50, wy - 30], [cx + 40, wy + wh + 40], [cx + 10, wy + wh + 40]]); paint(ctx, night ? '#9a6fae' : '#ff8fab', 5); }
  // calendar with DAY 1 circled
  ctx.save(); ctx.translate(780, 200); ctx.rotate(0.03); rrect(ctx, -90, -70, 180, 190, 6); paint(ctx, '#ffffff', 5); ctx.fillStyle = '#e8433a'; ctx.fillRect(-88, -68, 176, 36);
  for (let i = 0; i < 20; i++) { ctx.fillStyle = '#d8d2e6'; ctx.fillRect(-76 + (i % 5) * 32, -20 + Math.floor(i / 5) * 32, 20, 18); }
  ctx.beginPath(); ctx.ellipse(-28, 2, 26, 22, -0.2, 0, TAU); paint(ctx, null, 5, '#e8433a'); T(ctx, 'DAY 1!', 0, 136, 26, '#e8433a', { font: 'Chalkboard SE' }); ctx.restore();
  // mirror on a small dresser
  rrect(ctx, 1150, 640, 360, 160, 10); paint(ctx, night ? '#8a6aa0' : '#e9a46a', 6); rrect(ctx, 1170, 690, 320, 18, 6); paint(ctx, night ? '#7a5c90' : '#d18a52', 4);
  oval(ctx, MIRROR.x, MIRROR.y, MIRROR.rx + 18, MIRROR.ry + 18); paint(ctx, '#f2c14e', 7);
  // floor
  ctx.fillStyle = night ? '#6a4d6a' : '#d9a06b'; ctx.fillRect(-1000, 780, 4000, 1000);
  ctx.strokeStyle = night ? '#5a3f5a' : '#c48a55'; ctx.lineWidth = 3; for (let y = 830; y < 1300; y += 70) { ctx.beginPath(); ctx.moveTo(-1000, y); ctx.lineTo(3000, y); ctx.stroke(); }
  ctx.beginPath(); ctx.moveTo(-1000, 780); ctx.lineTo(3000, 780); paint(ctx, null, 4);
  st.plant(ctx, 1640, 790, 0.9);
  if (night) { // floor lamp glow
    ctx.beginPath(); ctx.moveTo(1780, 800); ctx.lineTo(1780, 380); paint(ctx, null, 6); poly(ctx, [[1720, 380], [1840, 380], [1810, 300], [1750, 300]]); paint(ctx, '#ffd98a', 5);
    ctx.save(); ctx.globalAlpha = 0.35; const lg = ctx.createRadialGradient(1780, 360, 20, 1780, 400, 700); lg.addColorStop(0, '#fff0b0'); lg.addColorStop(1, 'rgba(255,240,176,0)'); ctx.fillStyle = lg; ctx.fillRect(1000, -200, 1500, 1400); ctx.restore();
  }
}
// the mirror glass; draw(ctx) paints the reflection inside the oval
export function mirrorGlass(ctx, draw) {
  ctx.save(); oval(ctx, MIRROR.x, MIRROR.y, MIRROR.rx, MIRROR.ry); ctx.clip();
  const g = ctx.createLinearGradient(MIRROR.x - MIRROR.rx, 0, MIRROR.x + MIRROR.rx, 0); g.addColorStop(0, '#cfe9f2'); g.addColorStop(1, '#eaf6fb'); ctx.fillStyle = g; ctx.fillRect(MIRROR.x - 300, MIRROR.y - 300, 600, 600);
  if (draw) draw(ctx);
  ctx.globalAlpha = 0.35; ctx.fillStyle = '#ffffff'; poly(ctx, [[MIRROR.x - 120, MIRROR.y - 260], [MIRROR.x - 60, MIRROR.y - 260], [MIRROR.x - 200, MIRROR.y + 100], [MIRROR.x - 260, MIRROR.y + 100]]); ctx.fill();
  ctx.restore();
  oval(ctx, MIRROR.x, MIRROR.y, MIRROR.rx, MIRROR.ry); paint(ctx, null, 6);
}
export function letter(ctx, x, y, s = 1, rot = 0, words = ['JOB OFFER', 'លិខិតទទួលការងារ']) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  rrect(ctx, -60, -78, 120, 156, 6); paint(ctx, '#ffffff', 5);
  T(ctx, words[0], 0, -50, 18, '#2f6fe0'); text(ctx, words[1], 0, -24, { size: 16, fill: '#3b2d3b', lw: 0 });
  for (let i = 0; i < 4; i++) { ctx.fillStyle = '#d8d2e6'; ctx.fillRect(-44, 0 + i * 16, 88 - (i === 3 ? 30 : 0), 7); }
  circle(ctx, 30, 58, 13); paint(ctx, '#e8433a', 3); ctx.restore();
}
// cartoon heart pounding out of a chest (k = beat 0..1)
export function heart(ctx, x, y, s, k) {
  const sc = s * (1 + 0.45 * Math.max(0, Math.sin(k * Math.PI)));
  ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc);
  ctx.beginPath(); ctx.moveTo(0, 30); ctx.bezierCurveTo(-60, -10, -30, -55, 0, -25); ctx.bezierCurveTo(30, -55, 60, -10, 0, 30); ctx.closePath(); paint(ctx, '#ff4d6d', 6);
  oval(ctx, -16, -20, 9, 6, -0.6); ctx.fillStyle = 'rgba(255,255,255,0.6)'; ctx.fill();
  ctx.restore();
}

// ---------------------------------------------------------------- the street + tower + tuk-tuk
export const TOWER = { x: 700, w: 560, top: -1700 };
export function street(ctx, t) {
  const g = ctx.createLinearGradient(0, -1800, 0, 800); g.addColorStop(0, '#7fc8f0'); g.addColorStop(0.7, '#bfe6f5'); g.addColorStop(1, '#ffe7c0');
  ctx.fillStyle = g; ctx.fillRect(-1000, -2000, 4000, 2800);
  for (let i = 0; i < 6; i++) st.softCloud(ctx, -100 + i * 420 + Math.sin(t * 0.2 + i) * 20, -1500 + (i % 3) * 420, 1.1);
  st.shophouses(ctx, 140);
  // the office tower (glass + a clock showing 7:30)
  const { x, w, top } = TOWER;
  rrect(ctx, x, top, w, 810 - top, 8); paint(ctx, '#5fb8c4', 7);
  for (let yy = top + 50; yy < 560; yy += 110) for (let xx = x + 30; xx < x + w - 60; xx += 105) { rrect(ctx, xx, yy, 80, 80, 6); paint(ctx, hash(xx * 0.3 + yy) > 0.8 ? '#ffe7a0' : '#bfe8f0', 4); }
  rrect(ctx, x - 20, 560, w + 40, 34, 6); paint(ctx, '#e6b52e', 6);
  text(ctx, 'អគារ សូរ្យោទ័យ', x + w / 2 - 60, 578, { size: 30, fill: '#ffffff', lw: 5 });
  circle(ctx, x + w - 70, 577, 26); paint(ctx, '#ffffff', 4); ctx.save(); ctx.translate(x + w - 70, 577); ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, 18); paint(ctx, null, 4); ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(-10, -8); paint(ctx, null, 4); ctx.restore();
  rrect(ctx, x + w / 2 - 110, 610, 220, 200, 6); paint(ctx, '#d9f2f6', 6); ctx.beginPath(); ctx.moveTo(x + w / 2, 610); ctx.lineTo(x + w / 2, 810); paint(ctx, null, 5);
  poly(ctx, [[x + w / 2 - 140, 600], [x + w / 2 + 140, 600], [x + w / 2 + 120, 620], [x + w / 2 - 120, 620]]); paint(ctx, '#e8433a', 5);
}
export function tuktuk(ctx, x, y, s, t, { flip = false, moving = 0 } = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s * (flip ? -1 : 1), s);
  const bob = moving ? Math.sin(t * 22) * 3 : 0;
  // carriage (behind the motorbike)
  for (const wx of [-330, -170]) { circle(ctx, wx, -40, 40); paint(ctx, '#3a3946', 5); circle(ctx, wx, -40, 15); paint(ctx, '#c9ccd6', 3); }
  ctx.translate(0, bob);
  rrect(ctx, -400, -190, 300, 140, 16); paint(ctx, '#2fa3a0', 6);
  rrect(ctx, -380, -170, 120, 70, 8); paint(ctx, '#e9f6f7', 4);
  poly(ctx, [[-430, -330], [-80, -330], [-60, -300], [-450, -300]]); paint(ctx, '#ffd23f', 6);
  for (let i = 0; i < 6; i++) { ctx.fillStyle = '#e8433a'; ctx.fillRect(-430 + i * 62, -328, 30, 26); }
  for (const px of [-420, -110]) { rrect(ctx, px - 6, -305, 12, 120, 4); paint(ctx, '#9aa3b5', 4); }
  ctx.beginPath(); ctx.moveTo(-100, -90); ctx.lineTo(-40, -70); paint(ctx, null, 8);
  ctx.translate(0, -bob);
  st.rider(ctx, 60, 0, 1, t * (moving ? 1 : 0), { box: false });
  ctx.restore();
}

// ---------------------------------------------------------------- the hallway with doors 301 (tech team) and 302 (her company)
export const DOOR = { a: { x: 400, w: 280 }, b: { x: 1240, w: 280 }, top: 240, bot: 790 };
export function hallway(ctx, t, { openA = 0, openB = 0, gold = 0 } = {}) {
  ctx.fillStyle = '#e4efe3'; ctx.fillRect(-1000, -1000, 4000, 1790);
  ctx.fillStyle = '#c9dcc8'; ctx.fillRect(-1000, 560, 4000, 230); ctx.fillStyle = '#b5ccb4'; ctx.fillRect(-1000, 556, 4000, 10);
  for (const lx of [300, 960, 1620]) { rrect(ctx, lx - 80, 30, 160, 26, 10); paint(ctx, '#fff6d8', 5); }
  const door = (d, num, name, col, icon, open) => {
    rrect(ctx, d.x - 18, DOOR.top - 18, d.w + 36, DOOR.bot - DOOR.top + 18, 8); paint(ctx, '#ffffff', 6);
    ctx.fillStyle = '#3d3550'; ctx.fillRect(d.x, DOOR.top, d.w, DOOR.bot - DOOR.top);
    ctx.save(); ctx.translate(d.x, DOOR.top); ctx.scale(1 - open * 0.78, 1); rrect(ctx, 0, 0, d.w, DOOR.bot - DOOR.top, 6); paint(ctx, col, 6);
    rrect(ctx, 30, 40, d.w - 60, 150, 8); paint(ctx, 'rgba(255,255,255,0.25)', 4); rrect(ctx, 30, 230, d.w - 60, 260, 8); paint(ctx, 'rgba(255,255,255,0.18)', 4);
    circle(ctx, d.w - 34, 300, 13); paint(ctx, '#ffd23f', 4); ctx.restore();
    rrect(ctx, d.x + d.w / 2 - 120, DOOR.top - 120, 240, 86, 14); paint(ctx, '#ffffff', 5);
    T(ctx, num, d.x + d.w / 2 - 62, DOOR.top - 77, 40, col);
    T(ctx, name, d.x + d.w / 2 + 40, DOOR.top - 77, 22, '#3b2d3b');
    icon(d.x + d.w / 2 + 40, DOOR.top - 77);
  };
  door(DOOR.a, '301', '', '#4f86c6', (x, y) => { rrect(ctx, x - 50, y - 26, 100, 52, 6); paint(ctx, '#2a2633', 4); T(ctx, '</>', x, y, 24, '#7fd3c8'); }, openA);
  door(DOOR.b, '302', '', '#e07a5f', (x, y) => { for (let i = 0; i < 5; i++) { ctx.save(); ctx.translate(x, y + 18); ctx.rotate((i - 2) * 0.5); oval(ctx, 0, -20, 12, 24); paint(ctx, '#ff8fab', 3.5); ctx.restore(); } }, openB);
  // notice board + plant between the doors
  rrect(ctx, 800, 300, 320, 200, 8); paint(ctx, '#d9a06b', 6); for (let i = 0; i < 4; i++) { ctx.save(); ctx.translate(850 + i * 72, 380 + (i % 2) * 30); ctx.rotate((hash(i) - 0.5) * 0.3); rrect(ctx, -26, -34, 52, 68, 3); paint(ctx, ['#fff27a', '#ffffff', '#9fe3c9', '#ffb3c1'][i], 3); ctx.restore(); }
  st.plant(ctx, 960, 790, 1.0);
  ctx.fillStyle = '#d9d4e6'; ctx.fillRect(-1000, 790, 4000, 1000);
  ctx.strokeStyle = '#c4bdd6'; ctx.lineWidth = 3; for (let x = -1000; x < 3000; x += 160) { ctx.beginPath(); ctx.moveTo(x, 790); ctx.lineTo(x - 300, 1400); ctx.stroke(); }
  ctx.beginPath(); ctx.moveTo(-1000, 790); ctx.lineTo(3000, 790); paint(ctx, null, 4);
  if (gold > 0) { ctx.save(); ctx.globalAlpha = 0.25 * gold; const g = ctx.createLinearGradient(0, 0, W, H); g.addColorStop(0, '#ffb070'); g.addColorStop(1, 'rgba(255,176,112,0)'); ctx.fillStyle = g; ctx.fillRect(-1000, -1000, 4000, 3000); ctx.restore(); }
}

// ---------------------------------------------------------------- the tech team's office: a desk row facing camera
// people are drawn sitting behind the desks (drawFn per desk), then the desk fronts on top.
export const DESKS = [480, 960, 1440];
export function deskRow(ctx, t, people, { screens = true } = {}) {
  for (const [i, x] of DESKS.entries()) {
    if (screens) { rrect(ctx, x + 70, 560, 170, 120, 10); paint(ctx, '#2a2633', 6); rrect(ctx, x + 145, 680, 20, 50, 4); paint(ctx, '#9aa3b5', 4); }
    people[i]?.();
  }
  for (const x of DESKS) { poly(ctx, [[x - 220, 730], [x + 220, 730], [x + 236, 752], [x - 236, 752]]); paint(ctx, st.S.desk, 6); rrect(ctx, x - 236, 752, 472, 300, 6); paint(ctx, st.S.deskD, 6); rrect(ctx, x - 60, 800, 120, 36, 8); paint(ctx, st.S.deskEdge, 4); }
}

// ---------------------------------------------------------------- her company (Lotus Trading)
export function lotusOffice(ctx, t, { cool = 0 } = {}) {
  ctx.fillStyle = '#d6e6f5'; ctx.fillRect(-1000, -1000, 4000, 1780); ctx.fillStyle = '#bcd2ea'; ctx.fillRect(-1000, 690, 4000, 90);
  // window with blinds
  rrect(ctx, 90, 130, 460, 380, 8); paint(ctx, '#eaf6fb', 7); for (let y = 150; y < 500; y += 26) { ctx.fillStyle = '#c9dbe9'; ctx.fillRect(100, y, 440, 12); }
  // logo
  for (let i = 0; i < 5; i++) { ctx.save(); ctx.translate(820, 230); ctx.rotate((i - 2) * 0.5); oval(ctx, 0, -34, 20, 40); paint(ctx, '#ff8fab', 5); ctx.restore(); }
  T(ctx, 'LOTUS TRADING', 1080, 220, 52, '#e07a5f', { align: 'left' }); text(ctx, 'ក្រុមហ៊ុន ឡូតុស', 1080, 280, { size: 38, fill: '#5a4a6a', lw: 0, align: 'left' });
  // wall clock + filing cabinets
  st.clockFace(ctx, 1720, 160, 50, t * 1.2);
  for (let i = 0; i < 2; i++) { rrect(ctx, 1560 + i * 170, 400, 160, 390, 6); paint(ctx, '#9aa3b5', 6); for (let k = 0; k < 3; k++) { rrect(ctx, 1575 + i * 170, 420 + k * 120, 130, 100, 6); paint(ctx, '#b8c0cf', 4); rrect(ctx, 1615 + i * 170, 460 + k * 120, 50, 14, 6); paint(ctx, '#e9edf3', 3); } }
  ctx.fillStyle = '#b9c4d6'; ctx.fillRect(-1000, 780, 4000, 1000); ctx.beginPath(); ctx.moveTo(-1000, 780); ctx.lineTo(3000, 780); paint(ctx, null, 4);
  st.plant(ctx, 640, 790, 0.9);
  if (cool > 0) { ctx.save(); ctx.globalAlpha = 0.22 * cool; ctx.fillStyle = '#3d5a9a'; ctx.fillRect(-1000, -1000, 4000, 3000); ctx.restore(); }
}
export function folders(ctx, x, y, n, t, wob = 0) {
  for (let i = 0; i < n; i++) { const sway = Math.sin(t * 5 + i * 0.4) * wob * i * 1.2; rrect(ctx, x - 70 + sway + (hash(i) - 0.5) * 16, y - (i + 1) * 26, 140, 24, 4); paint(ctx, ['#ffd23f', '#7fd3c8', '#ff9a3f', '#a07bff', '#e9edf3'][i % 5], 4); }
}

// ---------------------------------------------------------------- lunch bench outside the building
export function benchYard(ctx, t) {
  const g = ctx.createLinearGradient(0, -200, 0, 700); g.addColorStop(0, '#8fd0f2'); g.addColorStop(1, '#e6f6fb'); ctx.fillStyle = g; ctx.fillRect(-1000, -1000, 4000, 1800);
  rrect(ctx, -200, 60, 1500, 750, 6); paint(ctx, '#f2e1c4', 7); for (let yy = 120; yy < 760; yy += 160) for (let xx = -150; xx < 1260; xx += 210) { rrect(ctx, xx, yy, 160, 110, 6); paint(ctx, '#bfe8f0', 5); }
  ctx.fillStyle = '#9ed66e'; ctx.fillRect(-1000, 790, 4000, 1000); ctx.fillStyle = '#d9c9a8'; ctx.fillRect(-1000, 810, 4000, 120); ctx.beginPath(); ctx.moveTo(-1000, 790); ctx.lineTo(3000, 790); paint(ctx, null, 4);
  // shade tree
  rrect(ctx, 1520, 300, 60, 520, 20); paint(ctx, '#8a5a3c', 6);
  for (const [x, y, r] of [[1450, 260, 150], [1650, 220, 170], [1550, 120, 160], [1760, 330, 130], [1380, 380, 110]]) { circle(ctx, x, y, r); paint(ctx, '#46b05a', 7); }
  for (const [x, y, r] of [[1450, 260, 120], [1650, 220, 140], [1550, 120, 130], [1760, 330, 100], [1380, 380, 85]]) { circle(ctx, x - 14, y - 14, r * 0.6); ctx.fillStyle = 'rgba(255,255,255,0.12)'; ctx.fill(); }
}
export function bench(ctx, x, y) { for (const k of [-1, 1]) { rrect(ctx, x + k * 170 - 12, y - 10, 24, 90, 6); paint(ctx, '#6b5e5a', 5); } rrect(ctx, x - 230, y - 30, 460, 30, 8); paint(ctx, '#c98f5a', 6); rrect(ctx, x - 230, y - 190, 460, 26, 8); paint(ctx, '#c98f5a', 6); rrect(ctx, x - 230, y - 140, 460, 26, 8); paint(ctx, '#c98f5a', 6); }
export function lunchBox(ctx, x, y, s = 1, open = 1) { ctx.save(); ctx.translate(x, y); ctx.scale(s, s); rrect(ctx, -50, -24, 100, 40, 10); paint(ctx, '#7fd3c8', 5); if (open) { oval(ctx, -14, -24, 30, 12); paint(ctx, '#fffaf0', 4); oval(ctx, 26, -22, 14, 8); paint(ctx, '#e8875a', 3); } ctx.restore(); }

// ---------------------------------------------------------------- a small Khmer restaurant
export function restaurant(ctx, t) {
  ctx.fillStyle = '#ffd98a'; ctx.fillRect(-1000, -1000, 4000, 1780); ctx.fillStyle = '#f2b46a'; ctx.fillRect(-1000, 690, 4000, 90);
  // menu board in Khmer
  rrect(ctx, 150, 120, 560, 330, 10); paint(ctx, '#2f4a3f', 7); text(ctx, 'ម្ហូបខ្មែរ', 430, 175, { size: 52, fill: '#ffd23f', lw: 0 });
  st.DISHES.slice(0, 5).forEach((d, i) => { text(ctx, d, 190, 240 + i * 42, { size: 30, fill: '#fff6e6', lw: 0, align: 'left' }); text(ctx, `${(5 + i) * 1000}៛`, 680, 240 + i * 42, { size: 28, fill: '#9fe3c9', lw: 0, align: 'right' }); });
  // wall fan
  ctx.save(); ctx.translate(1000, 200); circle(ctx, 0, 0, 80); paint(ctx, '#ffffff', 6); ctx.rotate(t * 20); for (let i = 0; i < 3; i++) { ctx.rotate(TAU / 3); oval(ctx, 0, -38, 16, 34); paint(ctx, '#9fd6e8', 4); } ctx.restore(); circle(ctx, 1000, 200, 14); paint(ctx, '#e8433a', 4);
  // drinks fridge + lanterns
  rrect(ctx, 1500, 260, 280, 530, 12); paint(ctx, '#e9edf3', 7); rrect(ctx, 1525, 290, 230, 470, 8); paint(ctx, '#bfe8f0', 4); for (let r = 0; r < 4; r++) for (let c = 0; c < 4; c++) { rrect(ctx, 1545 + c * 52, 310 + r * 110, 30, 80, 8); paint(ctx, ['#ff5c8a', '#46c34f', '#ffd23f', '#ff9a3f'][(r + c) % 4], 3); }
  for (const lx of [380, 1200]) { ctx.beginPath(); ctx.moveTo(lx, -100); ctx.lineTo(lx, 30); paint(ctx, null, 3); oval(ctx, lx, 70, 40, 46); paint(ctx, '#e8433a', 5); ctx.fillStyle = '#ffd23f'; ctx.fillRect(lx - 30, 26, 60, 8); ctx.fillRect(lx - 30, 106, 60, 8); }
  ctx.fillStyle = '#e9c08f'; ctx.fillRect(-1000, 780, 4000, 1000); for (let x = -1000; x < 3000; x += 120) for (let y = 780; y < 1300; y += 120) { ctx.fillStyle = ((x + y) / 120) % 2 ? '#e0b27e' : '#e9c08f'; ctx.fillRect(x, y, 120, 120); }
  ctx.beginPath(); ctx.moveTo(-1000, 780); ctx.lineTo(3000, 780); paint(ctx, null, 4);
}
// the table top with four plates (drawn in front of the diners)
export function lunchTable(ctx, x, y, w = 900, t = 0) {
  poly(ctx, [[x - w / 2, y], [x + w / 2, y], [x + w / 2 + 40, y + 60], [x - w / 2 - 40, y + 60]]); paint(ctx, '#ffffff', 6);
  rrect(ctx, x - w / 2 - 40, y + 60, w + 80, 26, 6); paint(ctx, '#e9edf3', 5);
  rrect(ctx, x - w / 2 - 30, y + 80, w + 60, 230, 6); paint(ctx, '#e8433a', 6); // checked tablecloth hides the diners' legs
  for (let i = 0; i < 12; i++) { ctx.fillStyle = 'rgba(255,255,255,0.35)'; ctx.fillRect(x - w / 2 - 30 + i * (w + 60) / 12, y + 84, (w + 60) / 24, 222); }
  for (let i = 0; i < 4; i++) { const px = x - w * 0.36 + i * w * 0.24; oval(ctx, px, y + 30, 70, 20); paint(ctx, '#ffffff', 4); oval(ctx, px, y + 24, 44, 12); paint(ctx, '#fffaf0', 3); oval(ctx, px + 20, y + 22, 18, 7); paint(ctx, '#c97a4a', 3); }
  // the soup pot in the middle, steaming
  rrect(ctx, x - 50, y - 50, 100, 60, 14); paint(ctx, '#e8875a', 5); oval(ctx, x, y - 50, 50, 12); paint(ctx, '#f6c98a', 4);
  for (let i = 0; i < 3; i++) { const k = (t * 0.7 + i / 3) % 1; ctx.save(); ctx.globalAlpha = (1 - k) * 0.7; ctx.beginPath(); ctx.moveTo(x - 20 + i * 20, y - 60 - k * 80); ctx.quadraticCurveTo(x - 30 + i * 20, y - 80 - k * 80, x - 20 + i * 20, y - 100 - k * 80); paint(ctx, null, 5, '#ffffff'); ctx.restore(); }
}

// ---------------------------------------------------------------- props
export function cakeBox(ctx, x, y, s = 1, open = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  rrect(ctx, -90, -40, 180, 70, 10); paint(ctx, '#ffffff', 6);
  if (open) { const cols = [['#46c34f', '#ffffff'], ['#ff8fab', '#ffd23f'], ['#a07bff', '#ffffff'], ['#ff9a3f', '#46c34f']]; cols.forEach(([a, b], i) => { rrect(ctx, -76 + i * 40, -64, 34, 30, 6); paint(ctx, a, 4); ctx.fillStyle = b; ctx.fillRect(-73 + i * 40, -52, 28, 7); }); }
  else { rrect(ctx, -96, -60, 192, 30, 10); paint(ctx, '#ffd23f', 6); }
  ctx.fillStyle = '#e8433a'; ctx.fillRect(-8, -38, 16, 66); text(ctx, 'នំខ្មែរ', 0, 6, { size: 30, fill: '#e8433a', lw: 0 });
  ctx.restore();
}
export function cat(ctx, x, y, s, t, { sleep = 0 } = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const tail = Math.sin(t * 3) * 0.3;
  ctx.save(); ctx.translate(50, -30); ctx.rotate(-0.8 + tail); rrect(ctx, -8, -80, 16, 80, 8); paint(ctx, '#ff9a3f', 5); ctx.restore();
  oval(ctx, 0, -40, 60, 44); paint(ctx, '#ff9a3f', 6);
  const hy = -100 + sleep * 16;
  for (const k of [-1, 1]) { poly(ctx, [[k * 16, hy - 30], [k * 44, hy - 56], [k * 46, hy - 14]]); paint(ctx, '#ff9a3f', 5); }
  circle(ctx, 0, hy, 46); paint(ctx, '#ff9a3f', 6);
  for (const k of [-1, 1]) { if (sleep > 0.5) { ctx.beginPath(); ctx.arc(k * 18, hy - 2, 9, 0.2, Math.PI - 0.2); paint(ctx, null, 4); } else { oval(ctx, k * 18, hy - 4, 8, 11); paint(ctx, '#fff8e8', 3); circle(ctx, k * 18 + 1, hy - 2, 4); paint(ctx, INK, 0); } }
  oval(ctx, 0, hy + 12, 6, 4); paint(ctx, '#ff6b8a', 3);
  for (const k of [-1, 1]) for (const d of [-1, 1]) { ctx.beginPath(); ctx.moveTo(k * 20, hy + 14 + d * 4); ctx.lineTo(k * 56, hy + 10 + d * 10); paint(ctx, null, 2.5); }
  ctx.restore();
}
// her presentation slide (meeting room screen): one idea, one picture
export function mySlide(ctx, x, y, w, h, k = 1) {
  ctx.save(); rrect(ctx, x, y, w, h, 8); ctx.clip(); ctx.fillStyle = '#fffaf0'; ctx.fillRect(x, y, w, h);
  ctx.globalAlpha = clamp(k * 2);
  ctx.fillStyle = '#e07a5f'; ctx.fillRect(x, y, w, 16);
  text(ctx, 'ឯកសារ រកឃើញក្នុង ១ នាទី', x + w / 2, y + h * 0.2, { size: h * 0.11, fill: '#2d3a6b', lw: 0 });
  // one big picture: a neat folder with a check
  const cx = x + w / 2, cy = y + h * 0.62;
  rrect(ctx, cx - 150, cy - 90, 300, 190, 16); paint(ctx, '#ffd23f', 6); rrect(ctx, cx - 150, cy - 120, 130, 50, 12); paint(ctx, '#ffd23f', 6); rrect(ctx, cx - 150, cy - 90, 300, 190, 16); paint(ctx, '#ffd23f', 6);
  ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(cx - 50, cy); ctx.lineTo(cx - 10, cy + 40); ctx.lineTo(cx + 60, cy - 40); ctx.lineWidth = 22; ctx.strokeStyle = INK; ctx.stroke(); ctx.lineWidth = 12; ctx.strokeStyle = '#46c34f'; ctx.stroke();
  ctx.restore();
}
