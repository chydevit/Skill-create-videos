// Locations for the team story: Phnom Penh skyline, the office, meeting room, launch-day screens,
// dashboard, delivery street, night rooftop. Soft pastel flat style.
import { W, H, INK, TAU, paint, circle, oval, rrect, poly, smooth, cel, text, clamp, lerp, seg, ease, hash, rng } from './core.mjs';
import { person } from './people.mjs';

export const S = {
  skyTop: '#ff9f5a', skyMid: '#ffc46b', skyLow: '#ffe2a0', sun: '#fff0b8',
  bldA: '#2fa3a0', bldB: '#f2823a', bldC: '#e6b52e', bldD: '#7fd3c8', bldE: '#d9603b',
  stone: '#f2b46a', stoneD: '#c9824a', river: '#2f8fa3', riverL: '#5fb8c4',
  wall: '#fbe8c4', wallD: '#e9c993', floor: '#efcf9f', floorD: '#d9b07c', trim: '#ffffff',
  desk: '#f6c98a', deskD: '#d99a52', deskEdge: '#c7853f', monitor: '#2a2633', screen: '#232036',
  leaf: '#46b05a', leafD: '#2f8c43', pot: '#e8433a', board: '#ffffff', boardFrame: '#8e99a5',
  code: ['#ff5c8a', '#2fd3a0', '#ffd23f', '#a07bff', '#3fb3ff', '#ff9a3f'],
  night: '#1f2550', nightL: '#3a3f7a', star: '#fff6d8', lamp: '#ffd23f', red: '#e8433a', green: '#46c34f', blue: '#2f6fe0',
  nham: '#f2823a',
};

// ---------------------------------------------------------------- sky + Phnom Penh skyline
export function sunsetSky(ctx, { horizon = 760, t = 0, sunY = 560 } = {}) {
  const g = ctx.createLinearGradient(0, -400, 0, horizon);
  g.addColorStop(0, '#f2735a'); g.addColorStop(0.35, S.skyTop); g.addColorStop(0.7, S.skyMid); g.addColorStop(1, S.skyLow);
  ctx.fillStyle = g; ctx.fillRect(-3000, -3000, 9000, horizon + 3000);
  ctx.save(); ctx.globalAlpha = 0.35; circle(ctx, 1380, sunY, 190); ctx.fillStyle = '#fff3d6'; ctx.fill(); ctx.restore();
  circle(ctx, 1380, sunY, 110); paint(ctx, S.sun, 0);
  for (const [x, y, s] of [[260, 170, 1], [820, 110, 0.75], [1650, 220, 0.9], [2300, 140, 0.8]]) softCloud(ctx, x - t * 6, y, s);
}
export function softCloud(ctx, x, y, s = 1, col = 'rgba(255,246,236,0.9)') {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.fillStyle = col;
  ctx.beginPath(); for (const [cx, cy, r] of [[-80, 10, 36], [-30, -12, 52], [34, -2, 44], [86, 12, 30]]) { ctx.moveTo(cx + r, cy); ctx.arc(cx, cy, r, 0, TAU); } ctx.fill();
  rrect(ctx, -116, 8, 232, 34, 17); ctx.fill(); ctx.restore();
}
// Independence Monument (Vimean Ekareach): stepped sandstone lotus tower with naga crests on every tier
export function monument(ctx, x, y, s = 1, lit = 0) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const st = lit ? '#f7c98f' : S.stone, sd = lit ? '#d99a5f' : S.stoneD;
  for (let i = 0; i < 3; i++) { rrect(ctx, -150 + i * 22, -24 - i * 22, 300 - i * 44, 24, 3); paint(ctx, i % 2 ? st : sd, 4); }
  const tiers = [[150, 46], [124, 42], [100, 38], [78, 34], [58, 30], [40, 26]];
  let yy = -66;
  tiers.forEach(([w, h], i) => {
    const top = yy - h;
    cel(ctx, () => poly(ctx, [[-w / 2, yy], [w / 2, yy], [w / 2 - 6, top], [-w / 2 + 6, top]]), st, sd, 8, 0, 4);
    ctx.beginPath(); for (let k = -2; k <= 2; k++) { ctx.moveTo(k * w / 6, yy - 4); ctx.lineTo(k * w / 6, top + 4); } paint(ctx, null, 2.5, sd);
    for (let k = -2; k <= 2; k++) { const bx = k * (w - 14) / 4; ctx.beginPath(); ctx.moveTo(bx - 7, top + 2); ctx.quadraticCurveTo(bx, top - 16, bx + 7, top + 2); ctx.closePath(); paint(ctx, st, 3); }
    yy = top - 4;
  });
  ctx.beginPath(); ctx.moveTo(-16, yy); ctx.bezierCurveTo(-22, yy - 40, -4, yy - 60, 0, yy - 80); ctx.bezierCurveTo(4, yy - 60, 22, yy - 40, 16, yy); ctx.closePath(); paint(ctx, st, 4);
  if (lit) { ctx.save(); ctx.globalAlpha = 0.25 * lit; const g = ctx.createRadialGradient(0, -200, 20, 0, -200, 320); g.addColorStop(0, '#ffe2a8'); g.addColorStop(1, 'rgba(255,226,168,0)'); ctx.fillStyle = g; ctx.fillRect(-340, -560, 680, 600); ctx.restore(); }
  ctx.restore();
}
function sugarPalm(ctx, x, y, s = 1, col = '#7fb08f') {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.beginPath(); ctx.moveTo(-4, 0); ctx.lineTo(-3, -150); ctx.lineTo(3, -150); ctx.lineTo(4, 0); ctx.closePath(); paint(ctx, '#a88a6c', 3);
  ctx.fillStyle = col; ctx.beginPath(); for (let k = 0; k < 9; k++) { const a = -Math.PI / 2 + (k - 4) * 0.36; ctx.moveTo(0, -150); ctx.lineTo(Math.cos(a - 0.12) * 46, -150 + Math.sin(a - 0.12) * 46); ctx.lineTo(Math.cos(a + 0.12) * 46, -150 + Math.sin(a + 0.12) * 46); } ctx.fill();
  ctx.restore();
}
// layered city: far towers, the monument, river, near office block with the lit window of our team
export function skyline(ctx, t, { night = 0, windowPeople = true } = {}) {
  const r = rng(7);
  // far towers
  ctx.fillStyle = night ? '#3b3f78' : '#f5b37a';
  for (let x = -300; x < 2400;) { const w = 50 + r() * 70, h = 80 + r() * 180; ctx.fillRect(x, 700 - h, w, h + 60); x += w + 6; }
  // a landmark-ish tall curved tower
  ctx.save(); ctx.translate(560, 700);
  ctx.beginPath(); ctx.moveTo(-40, 0); ctx.lineTo(-40, -420); ctx.quadraticCurveTo(-10, -470, 30, -430); ctx.lineTo(40, 0); ctx.closePath(); paint(ctx, night ? '#4f5394' : S.bldD, 5);
  ctx.fillStyle = night ? 'rgba(255,217,138,0.7)' : 'rgba(255,255,255,0.5)'; for (let yy = -400; yy < -20; yy += 26) ctx.fillRect(-30, yy, 60, 6);
  ctx.restore();
  // mid buildings
  const pal = night ? ['#3f4585', '#4b3f7a', '#35407a'] : [S.bldA, S.bldB, S.bldC, S.bldE];
  const r2 = rng(19);
  for (let x = -200; x < 2300;) {
    const w = 110 + r2() * 120, h = 120 + r2() * 160; const col = pal[Math.floor(r2() * pal.length)];
    if (x > 820 && x < 1180) { x += 60; continue; } // keep the monument clear
    rrect(ctx, x, 760 - h, w, h + 40, 4); paint(ctx, col, 4);
    for (let yy = 760 - h + 20; yy < 740; yy += 34) for (let xx = x + 14; xx < x + w - 20; xx += 30) { const lit = night ? hash(xx * 1.3 + yy) > 0.35 : hash(xx + yy) > 0.6; ctx.fillStyle = lit ? (night ? S.lamp : '#fff6e6') : (night ? '#45436b' : 'rgba(255,255,255,0.35)'); ctx.fillRect(xx, yy, 14, 18); }
    x += w + 10;
  }
  monument(ctx, 1000, 770, 1.15, night);
  // river + palms
  ctx.fillStyle = night ? '#3c4a7a' : S.river; ctx.fillRect(-2000, 770, 6000, 120);
  ctx.strokeStyle = night ? 'rgba(255,217,138,0.5)' : S.riverL; ctx.lineWidth = 5; ctx.lineCap = 'round';
  for (let k = 0; k < 14; k++) { const x = ((k * 173 + t * 30) % 2200) - 140, y = 800 + (k % 4) * 22; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + 60, y); ctx.stroke(); }
  for (const [x, s] of [[120, 0.9], [300, 1.1], [1500, 1], [1720, 0.85]]) sugarPalm(ctx, x, 770, s, night ? '#4f6a6a' : '#86b596');
  ctx.fillStyle = night ? '#3a3a62' : '#e7c39f'; ctx.fillRect(-2000, 880, 6000, 400);
}
// the office tower in the foreground (right) with OUR window
export const TEAM_WIN = { x: 1560, y: 610, w: 150, h: 96 };
export function officeTower(ctx, t, { night = 0 } = {}) {
  rrect(ctx, 1370, 260, 520, 900, 6); paint(ctx, night ? '#4f5394' : '#e6b52e', 6);
  for (let yy = 300; yy < 1100; yy += 130) for (let xx = 1400; xx < 1860; xx += 180) {
    rrect(ctx, xx, yy, 150, 96, 6); paint(ctx, night ? '#2c2f5c' : '#bfe8e6', 5);
  }
  const w = TEAM_WIN;
  ctx.save(); rrect(ctx, w.x, w.y, w.w, w.h, 6); ctx.clip();
  ctx.fillStyle = '#ffe2b8'; ctx.fillRect(w.x, w.y, w.w, w.h);
  ctx.fillStyle = '#f7cfa2'; ctx.fillRect(w.x, w.y + w.h * 0.7, w.w, w.h);
  person(ctx, 'devit', { x: w.x + 32, y: w.y + w.h + 6, s: 0.2, facing: 0.6, t, pose: 'type' });
  person(ctx, 'nimith', { x: w.x + 82, y: w.y + w.h + 2, s: 0.19, facing: -0.2, t, pose: 'draw', hold: [null, 'marker'] });
  person(ctx, 'smei', { x: w.x + 122, y: w.y + w.h + 2, s: 0.19, facing: -0.5, t, hold: [null, 'tea'] });
  ctx.restore();
  rrect(ctx, w.x, w.y, w.w, w.h, 6); paint(ctx, null, 4);
  ctx.save(); ctx.globalAlpha = 0.35 + 0.1 * Math.sin(t * 2); const g = ctx.createRadialGradient(w.x + w.w / 2, w.y + w.h / 2, 10, w.x + w.w / 2, w.y + w.h / 2, 160); g.addColorStop(0, '#ffe6b0'); g.addColorStop(1, 'rgba(255,230,176,0)'); ctx.fillStyle = g; ctx.fillRect(w.x - 160, w.y - 160, w.w + 320, w.h + 320); ctx.restore();
}

// ---------------------------------------------------------------- office interior
// world: floor line y=780, back wall above. Window left, whiteboard right, door far right.
export function office(ctx, t, { light = 'day', board = 1, red = 0, doorOpen = 0 } = {}) {
  ctx.fillStyle = S.wall; ctx.fillRect(-1000, -1000, 4000, 1780);
  ctx.fillStyle = S.wallD; ctx.fillRect(-1000, 700, 4000, 80);
  // window with city
  const wx = 60, wy = 110, ww = 840, wh = 470;
  ctx.save(); rrect(ctx, wx, wy, ww, wh, 10); ctx.clip();
  const g = ctx.createLinearGradient(0, wy, 0, wy + wh); g.addColorStop(0, light === 'gold' ? '#ffc79e' : '#bfe0f2'); g.addColorStop(1, light === 'gold' ? '#ffe7c4' : '#eaf6fb');
  ctx.fillStyle = g; ctx.fillRect(wx, wy, ww, wh);
  const r = rng(3); for (let x = wx - 20; x < wx + ww;) { const w = 50 + r() * 70, h = 90 + r() * 200; ctx.fillStyle = ['#2fa3a0', '#f2823a', '#e6b52e', '#d9603b', '#8a4f7d'][Math.floor(r() * 5)]; ctx.fillRect(x, wy + wh - h, w, h); x += w + 8; }
  monument(ctx, 640, wy + wh, 0.42, 0);
  ctx.restore();
  rrect(ctx, wx, wy, ww, wh, 10); paint(ctx, null, 8, S.trim); rrect(ctx, wx, wy, ww, wh, 10); paint(ctx, null, 4);
  ctx.beginPath(); ctx.moveTo(wx + ww / 2, wy); ctx.lineTo(wx + ww / 2, wy + wh); paint(ctx, null, 8, S.trim);
  // shelf + framed Angkor picture
  rrect(ctx, 960, 140, 150, 110, 6); paint(ctx, '#fff8ee', 4);
  ctx.save(); ctx.translate(1035, 222); ctx.fillStyle = '#e6b98c';
  for (const [x, h, w] of [[-44, 40, 16], [-22, 56, 18], [0, 72, 22], [22, 56, 18], [44, 40, 16]]) { ctx.beginPath(); ctx.moveTo(x - w / 2, 0); ctx.quadraticCurveTo(x, -h * 1.3, x + w / 2, 0); ctx.fill(); }
  ctx.fillRect(-60, -6, 120, 8); ctx.restore();
  // whiteboard with an architecture diagram
  whiteboard(ctx, 1160, 200, 1, board, t);
  // door
  rrect(ctx, 1730, 230, 190, 470, 8); paint(ctx, '#e9d2bd', 5);
  ctx.save(); ctx.translate(1730, 230); ctx.scale(1 - doorOpen * 0.75, 1); rrect(ctx, 0, 0, 190, 470, 8); paint(ctx, '#d6a986', 5); circle(ctx, 160, 250, 9); paint(ctx, '#fbe3a2', 3); ctx.restore();
  // pendant lamps
  for (const lx of [420, 1300]) { ctx.beginPath(); ctx.moveTo(lx, -200); ctx.lineTo(lx, 40); paint(ctx, null, 3); ctx.beginPath(); ctx.moveTo(lx - 46, 80); ctx.quadraticCurveTo(lx, 10, lx + 46, 80); ctx.closePath(); paint(ctx, '#ffd6a0', 4); ctx.save(); ctx.globalAlpha = 0.18; const lg = ctx.createRadialGradient(lx, 90, 10, lx, 90, 260); lg.addColorStop(0, '#fff0c8'); lg.addColorStop(1, 'rgba(255,240,200,0)'); ctx.fillStyle = lg; ctx.fillRect(lx - 260, 90, 520, 400); ctx.restore(); }
  // floor
  ctx.fillStyle = S.floor; ctx.fillRect(-1000, 780, 4000, 1000);
  ctx.strokeStyle = S.floorD; ctx.lineWidth = 3; for (let x = -1000; x < 3000; x += 140) { ctx.beginPath(); ctx.moveTo(x, 780); ctx.lineTo(x - 260, 1400); ctx.stroke(); }
  ctx.beginPath(); ctx.moveTo(-1000, 780); ctx.lineTo(3000, 780); paint(ctx, null, 4);
  plant(ctx, 930, 790, 1.1); plant(ctx, 1660, 790, 0.9);
  if (red > 0) redWash(ctx, t, red);
}
export function plant(ctx, x, y, s = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  for (let k = 0; k < 7; k++) { const a = -Math.PI / 2 + (k - 3) * 0.38; ctx.save(); ctx.translate(0, -70); ctx.rotate(a + Math.PI / 2); ctx.beginPath(); ctx.ellipse(0, -58, 22, 50, 0, 0, TAU); paint(ctx, k % 2 ? S.leaf : S.leafD, 3.5); ctx.restore(); }
  poly(ctx, [[-40, -80], [40, -80], [30, 0], [-30, 0]]); paint(ctx, S.pot, 4);
  ctx.restore();
}
export function whiteboard(ctx, x, y, s = 1, k = 1, t = 0) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  rrect(ctx, 0, 0, 500, 330, 10); paint(ctx, S.board, 5); rrect(ctx, 20, 330, 460, 14, 4); paint(ctx, S.boardFrame, 4);
  archDiagram(ctx, 250, 165, 1, k);
  ctx.restore();
}
// boxes + arrows + database + servers, drawn progressively (k 0..1)
export function archDiagram(ctx, cx, cy, s = 1, k = 1, col = '#4f86c6') {
  ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s);
  ctx.strokeStyle = col; ctx.lineWidth = 5; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  const steps = [
    () => { ctx.strokeRect(-200, -110, 110, 64); },
    () => { arrowTo(ctx, -86, -78, -30, -78); },
    () => { ctx.strokeRect(-26, -110, 110, 64); },
    () => { arrowTo(ctx, 30, -42, 30, 10); },
    () => { ctx.beginPath(); ctx.ellipse(30, 30, 46, 14, 0, 0, TAU); ctx.moveTo(-16, 30); ctx.lineTo(-16, 90); ctx.ellipse(30, 90, 46, 14, 0, Math.PI, 0, true); ctx.lineTo(76, 30); ctx.stroke(); },
    () => { arrowTo(ctx, 88, -78, 140, -78); },
    () => { for (let i = 0; i < 3; i++) ctx.strokeRect(146, -126 + i * 30, 70, 24); },
  ];
  const n = Math.floor(k * steps.length + 1e-6);
  for (let i = 0; i < Math.min(n, steps.length); i++) steps[i]();
  ctx.restore();
}
function arrowTo(ctx, x1, y1, x2, y2) { ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); const a = Math.atan2(y2 - y1, x2 - x1); ctx.moveTo(x2, y2); ctx.lineTo(x2 - Math.cos(a - 0.5) * 14, y2 - Math.sin(a - 0.5) * 14); ctx.moveTo(x2, y2); ctx.lineTo(x2 - Math.cos(a + 0.5) * 14, y2 - Math.sin(a + 0.5) * 14); ctx.stroke(); }
// foreground desk (seen from the front), with a monitor angled toward its user
export function desk(ctx, x, y, w = 760, { monitorX = 200, screen = 'code', t = 0, mug = true, codeSpeed = 1, fly = 0 } = {}) {
  ctx.save(); ctx.translate(x, y);
  // monitor
  ctx.save(); ctx.translate(monitorX, -40);
  rrect(ctx, -8, -40, 16, 44, 4); paint(ctx, '#9aa3b5', 4);
  poly(ctx, [[-150, -250], [130, -230], [130, -40], [-150, -50]]); paint(ctx, S.monitor, 5);
  ctx.save(); poly(ctx, [[-138, -238], [118, -220], [118, -52], [-138, -62]]); ctx.clip(); ctx.fillStyle = S.screen; ctx.fillRect(-150, -250, 300, 220);
  if (screen === 'code') codeLines(ctx, -128, -224, t * codeSpeed);
  ctx.restore();
  ctx.restore();
  // desk top + front
  poly(ctx, [[-w / 2 - 30, -40], [w / 2 + 30, -40], [w / 2, 10], [-w / 2, 10]]); paint(ctx, S.desk, 5);
  rrect(ctx, -w / 2, 10, w, 400, 6); paint(ctx, S.deskD, 5);
  if (mug) { rrect(ctx, -w / 2 + 60, -86, 46, 50, 8); paint(ctx, '#fbe3a2', 4); }
  // keyboard
  poly(ctx, [[-120, -30], [120, -30], [110, -6], [-110, -6]]); paint(ctx, '#e9edf3', 4);
  ctx.restore();
}
export function codeLines(ctx, x, y, t, rows = 9, glow = 0) {
  const scroll = Math.floor(t * 6);
  for (let i = 0; i < rows; i++) {
    const n = i + scroll, ind = (hash(n * 3.1) * 3 | 0) * 16;
    let xx = x + ind;
    for (let w = 0; w < 4; w++) { const len = 14 + hash(n * 7 + w) * 46; ctx.fillStyle = S.code[(n + w) % S.code.length]; rrect(ctx, xx, y + i * 20, len, 10, 4); ctx.fill(); xx += len + 8; }
  }
}
// glyphs flying off a screen
export function flyingCode(ctx, ox, oy, t, n = 14, spread = 1) {
  ctx.save(); ctx.font = 'bold 34px "Arial Black"'; ctx.textAlign = 'center';
  const sym = ['{ }', '</>', '=>', '( )', ';', '[ ]', '#', '++'];
  for (let i = 0; i < n; i++) {
    const k = (t * 0.8 + hash(i * 3.7)) % 1, a = -2.6 + hash(i * 1.3) * 2.2;
    const x = ox + Math.cos(a) * k * 520 * spread, y = oy + Math.sin(a) * k * 360 * spread - k * 60;
    ctx.globalAlpha = Math.sin(k * Math.PI); ctx.fillStyle = S.code[i % S.code.length];
    ctx.lineWidth = 6; ctx.strokeStyle = INK; ctx.strokeText(sym[i % sym.length], x, y); ctx.fillText(sym[i % sym.length], x, y);
  }
  ctx.restore();
}
export function redWash(ctx, t, amt = 1) {
  ctx.save(); ctx.globalAlpha = (0.22 + 0.12 * (Math.sin(t * 7) * 0.5 + 0.5)) * amt; ctx.fillStyle = '#ff4d5e'; ctx.fillRect(-2000, -2000, 6000, 5000); ctx.restore();
}

// ---------------------------------------------------------------- meeting room
export function meetingRoom(ctx, t, { slide = 1 } = {}) {
  ctx.fillStyle = '#bfe3e0'; ctx.fillRect(-1000, -1000, 4000, 1780);
  ctx.fillStyle = '#9fd0cb'; ctx.fillRect(-1000, 700, 4000, 80);
  // screen with the project slide
  rrect(ctx, 150, 110, 900, 520, 12); paint(ctx, '#ffffff', 6);
  ctx.save(); rrect(ctx, 170, 130, 860, 480, 8); ctx.clip();
  const g = ctx.createLinearGradient(170, 130, 1030, 610); g.addColorStop(0, '#fff2e8'); g.addColorStop(1, '#ffe2d4'); ctx.fillStyle = g; ctx.fillRect(170, 130, 860, 480);
  if (slide > 0) {
    ctx.globalAlpha = clamp(slide * 2);
    nhamLogo(ctx, 320, 370, 1.05);
    text(ctx, 'Food Delivery App', 720, 230, { size: 54, font: 'Arial Black', fill: '#ff8c6b', lw: 0 });
    text(ctx, 'កម្មវិធីដឹកជញ្ជូនម្ហូប', 720, 310, { size: 50, fill: '#5a4a6a', lw: 0 });
    rrect(ctx, 520, 390, 400, 130, 22); paint(ctx, '#ffffff', 4);
    text(ctx, '1 Month', 640, 456, { size: 46, font: 'Arial Black', fill: '#4f86c6', lw: 0 });
    text(ctx, '១ ខែ', 830, 452, { size: 52, fill: '#4f86c6', lw: 0 });
  }
  ctx.restore();
  plant(ctx, 1150, 790, 1);
  rrect(ctx, 1260, 180, 560, 360, 10); paint(ctx, '#ffffff', 5);
  ctx.save(); rrect(ctx, 1270, 190, 540, 340, 6); ctx.clip(); ctx.fillStyle = '#cfe6f3'; ctx.fillRect(1270, 190, 540, 340); monument(ctx, 1540, 530, 0.5); ctx.restore();
  ctx.fillStyle = '#c99ac0'; ctx.fillRect(-1000, 780, 4000, 1000);
  ctx.beginPath(); ctx.moveTo(-1000, 780); ctx.lineTo(3000, 780); paint(ctx, null, 4);
}
export function meetingTable(ctx, x, y, w = 1200) {
  ctx.save(); ctx.translate(x, y);
  poly(ctx, [[-w / 2, -40], [w / 2, -40], [w / 2 + 60, 20], [-w / 2 - 60, 20]]); paint(ctx, '#f6e0c4', 5);
  rrect(ctx, -w / 2 - 60, 20, w + 120, 30, 6); paint(ctx, '#e3c39f', 5);
  for (const lx of [-w / 2 + 40, w / 2 - 40]) { rrect(ctx, lx - 12, 50, 24, 300, 6); paint(ctx, '#e3c39f', 5); }
  ctx.restore();
}
export function nhamLogo(ctx, x, y, s = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  circle(ctx, 0, 0, 90); paint(ctx, S.nham, 5);
  ctx.beginPath(); ctx.moveTo(-54, -4); ctx.lineTo(54, -4); ctx.quadraticCurveTo(50, 48, 0, 52); ctx.quadraticCurveTo(-50, 48, -54, -4); ctx.closePath(); paint(ctx, '#fff6ea', 4);
  ctx.strokeStyle = '#fff6ea'; ctx.lineWidth = 5; ctx.lineCap = 'round'; for (const k of [-18, 0, 18]) { ctx.beginPath(); ctx.moveTo(k, -20); ctx.quadraticCurveTo(k + 8, -34, k, -48); ctx.stroke(); }
  text(ctx, 'ញ៉ាំ', 0, 26, { size: 34, fill: S.nham, lw: 0 });
  ctx.restore();
}

// ---------------------------------------------------------------- launch day
export function banner(ctx, x, y, w, words, col = '#ffb3c1') {
  ctx.save(); ctx.translate(x, y);
  ctx.beginPath(); ctx.moveTo(-w / 2, 0); ctx.quadraticCurveTo(0, 40, w / 2, 0); paint(ctx, null, 4);
  const n = 9; for (let i = 0; i < n; i++) { const u = i / (n - 1), px = -w / 2 + u * w, py = 40 * 4 * u * (1 - u) * 0.5; poly(ctx, [[px - 24, py], [px + 24, py], [px, py + 44]]); paint(ctx, ['#ffb3c1', '#ffd98a', '#9fe3c9', '#b7c8ff'][i % 4], 3); }
  text(ctx, words, 0, 80, { size: 48, font: 'Arial Black', fill: '#ff8c6b', lw: 8, stroke: '#ffffff' });
  ctx.restore();
}
export function confetti(ctx, t, { n = 80, area = [0, 0, W, H], seed = 1, fall = 1 } = {}) {
  const cols = ['#ff9fb2', '#ffd98a', '#8fe3c4', '#b7c8ff', '#ffb38a'];
  for (let i = 0; i < n; i++) {
    const x = area[0] + hash(i * 7 + seed) * area[2] + Math.sin(t * 2 + i) * 30;
    const y = area[1] + ((hash(i * 3 + seed) * area[3] + t * (140 + hash(i) * 120) * fall) % area[3]);
    ctx.save(); ctx.translate(x, y); ctx.rotate(t * 4 + i); ctx.scale(1, Math.cos(t * 6 + i)); ctx.fillStyle = cols[i % cols.length]; ctx.fillRect(-8, -5, 16, 10); ctx.restore();
  }
}
// phone UI: orders flooding in, then ERROR 500
export const DISHES = ['បាយសាច់ជ្រូក', 'គុយទាវ', 'អាម៉ុក', 'នំបញ្ចុក', 'បបរ', 'ឡុកឡាក់', 'សម្លកកូរ', 'នំបញ្ចុក'];
export function phoneScreen(ctx, x, y, s, t, { orders = 0, error = 0, ok = 0 } = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  rrect(ctx, -230, -440, 460, 880, 60); paint(ctx, '#2f2e3a', 6);
  ctx.save(); rrect(ctx, -206, -412, 412, 824, 40); ctx.clip();
  ctx.fillStyle = '#fff7f0'; ctx.fillRect(-210, -420, 420, 840);
  ctx.fillStyle = S.nham; ctx.fillRect(-210, -420, 420, 110);
  text(ctx, 'ញ៉ាំ Nham', 0, -352, { size: 46, fill: '#ffffff', lw: 0 });
  const n = Math.floor(orders);
  for (let i = 0; i < Math.min(n, 30); i++) {
    const row = n - 1 - i, yy = -280 + i * 92;
    if (yy > 400) break;
    rrect(ctx, -186, yy, 372, 78, 18); paint(ctx, '#ffffff', 3.5);
    circle(ctx, -146, yy + 39, 24); paint(ctx, ['#ffd98a', '#9fe3c9', '#ffb3c1', '#b7c8ff'][row % 4], 3);
    text(ctx, DISHES[row % DISHES.length], -20, yy + 30, { size: 30, fill: '#4a3a4a', lw: 0 });
    text(ctx, `#${1000 + row * 7}`, 120, yy + 56, { size: 20, font: 'Arial Black', fill: '#b9a6b9', lw: 0 });
  }
  if (ok > 0) { ctx.globalAlpha = ok; ctx.fillStyle = 'rgba(95,211,154,0.92)'; ctx.fillRect(-210, -420, 420, 840); text(ctx, '✓', 0, -40, { size: 200, font: 'Arial Black', fill: '#ffffff', lw: 0 }); text(ctx, 'All good!', 0, 120, { size: 48, font: 'Arial Black', fill: '#ffffff', lw: 0 }); ctx.globalAlpha = 1; }
  if (error > 0) { ctx.globalAlpha = error; ctx.fillStyle = 'rgba(255,90,100,0.94)'; ctx.fillRect(-210, -420, 420, 840); text(ctx, '!', 0, -110, { size: 220, font: 'Arial Black', fill: '#ffffff', lw: 0 }); text(ctx, 'ERROR 500', 0, 70, { size: 62, font: 'Arial Black', fill: '#ffffff', lw: 0 }); text(ctx, 'Server overload', 0, 140, { size: 30, font: 'Arial Black', fill: '#ffe2e4', lw: 0 }); ctx.globalAlpha = 1; }
  ctx.restore();
  ctx.restore();
}
export function serverRack(ctx, x, y, s, t, { smoke = 0, ok = 0, n = 1 } = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  for (let r = 0; r < n; r++) {
    ctx.save(); ctx.translate(r * 230, 0);
    rrect(ctx, -90, -520, 180, 520, 12); paint(ctx, '#565c74', 5);
    for (let i = 0; i < 7; i++) {
      const yy = -500 + i * 70; rrect(ctx, -74, yy, 148, 56, 6); paint(ctx, '#6c7390', 4);
      for (let k = 0; k < 4; k++) { const on = hash(i * 5 + k + Math.floor(t * (smoke ? 12 : 4)) + r * 9) > 0.4; circle(ctx, -56 + k * 16, yy + 28, 5); paint(ctx, on ? (smoke ? S.red : ok ? S.green : '#9fe3c9') : '#3d4154', 2); }
      ctx.fillStyle = '#4a4f66'; ctx.fillRect(10, yy + 18, 52, 6); ctx.fillRect(10, yy + 32, 52, 6);
    }
    ctx.restore();
  }
  if (smoke > 0) for (let i = 0; i < 8; i++) { const k = (t * 0.6 + i / 8) % 1; const px = Math.sin(i * 2.1 + t) * 40 * k, py = -520 - k * 320; ctx.save(); ctx.globalAlpha = (1 - k) * 0.85 * smoke; circle(ctx, px, py, 30 + k * 60); ctx.fillStyle = '#8a8698'; ctx.fill(); ctx.restore(); }
  ctx.restore();
}
// ops dashboard: server nodes behind a load balancer, progress bars, status banner
export function dashboard(ctx, x, y, w, h, t, { servers = 1, lb = 0, bars = 0, status = 0, err = 0 } = {}) {
  ctx.save(); ctx.translate(x, y);
  rrect(ctx, 0, 0, w, h, 18); paint(ctx, '#2c3247', 6);
  ctx.save(); rrect(ctx, 10, 10, w - 20, h - 20, 12); ctx.clip();
  ctx.fillStyle = '#323a52'; ctx.fillRect(0, 0, w, h);
  ctx.fillStyle = status > 0 ? `rgba(95,211,154,${0.25 + 0.6 * status})` : err ? 'rgba(255,107,107,0.55)' : 'rgba(255,255,255,0.08)'; ctx.fillRect(10, 10, w - 20, 70);
  text(ctx, status > 0.5 ? 'All Systems Online' : err ? 'Status: DOWN' : 'Status: scaling…', w / 2, 46, { size: 34, font: 'Arial Black', fill: status > 0.5 ? '#eafff3' : '#ffffff', lw: 0 });
  // users -> LB -> servers
  const cx = w * 0.2, cy = h * 0.5;
  for (let i = 0; i < 5; i++) { circle(ctx, 60, 130 + i * ((h - 200) / 4), 16); paint(ctx, '#ffd98a', 3); }
  if (lb > 0) {
    ctx.globalAlpha = clamp(lb * 2);
    ctx.save(); ctx.setLineDash([12, 10]); ctx.lineDashOffset = -t * 60; for (let i = 0; i < 5; i++) { ctx.beginPath(); ctx.moveTo(76, 130 + i * ((h - 200) / 4)); ctx.lineTo(cx + 40, cy); paint(ctx, null, 4, '#ffd98a'); } ctx.restore();
    rrect(ctx, cx + 40, cy - 50, 130, 100, 16); paint(ctx, '#c3a8ff', 4);
    text(ctx, 'LB', cx + 105, cy, { size: 40, font: 'Arial Black', fill: '#2c3247', lw: 0 });
    ctx.globalAlpha = 1;
  }
  const n = Math.floor(servers);
  for (let i = 0; i < n; i++) {
    const sx = w * 0.62, sy = 120 + i * Math.min(110, (h - 240) / Math.max(1, n - 1));
    rrect(ctx, sx, sy, 140, 70, 10); paint(ctx, err ? S.red : '#8fe3c4', 4);
    for (let k = 0; k < 3; k++) { circle(ctx, sx + 24 + k * 18, sy + 35, 5); paint(ctx, hash(k + i * 3 + Math.floor(t * 6)) > 0.4 ? '#2c3247' : '#ffffff', 0); }
    if (lb > 0) { ctx.save(); ctx.globalAlpha = 0.7; ctx.setLineDash([12, 10]); ctx.lineDashOffset = -t * 60; ctx.beginPath(); ctx.moveTo(cx + 170, cy); ctx.lineTo(sx, sy + 35); paint(ctx, null, 4, '#ffd98a'); ctx.restore(); }
    // load bar
    const load = err ? 1 : clamp(0.9 - bars * 0.55 + Math.sin(t * 3 + i) * 0.06);
    rrect(ctx, sx + 160, sy + 22, 160, 26, 8); paint(ctx, '#252a3c', 3);
    rrect(ctx, sx + 160, sy + 22, 160 * load, 26, 8); paint(ctx, load > 0.8 ? S.red : load > 0.55 ? '#ffd98a' : S.green, 0);
  }
  if (lb <= 0) { ctx.save(); ctx.setLineDash([12, 10]); ctx.lineDashOffset = -t * 60; for (let i = 0; i < 5; i++) { ctx.beginPath(); ctx.moveTo(76, 130 + i * ((h - 200) / 4)); ctx.lineTo(w * 0.62, 155); paint(ctx, null, 4, err ? S.red : '#ffd98a'); } ctx.restore(); }
  ctx.restore();
  ctx.restore();
}
export function clockFace(ctx, x, y, r, a) {
  circle(ctx, x, y, r); paint(ctx, '#ffffff', 5);
  for (let i = 0; i < 12; i++) { const q = i * TAU / 12; ctx.beginPath(); ctx.moveTo(x + Math.cos(q) * r * 0.8, y + Math.sin(q) * r * 0.8); ctx.lineTo(x + Math.cos(q) * r * 0.9, y + Math.sin(q) * r * 0.9); paint(ctx, null, 3); }
  ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + Math.cos(a - Math.PI / 2) * r * 0.75, y + Math.sin(a - Math.PI / 2) * r * 0.75); paint(ctx, null, 5);
  ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + Math.cos(a / 12 - Math.PI / 2) * r * 0.5, y + Math.sin(a / 12 - Math.PI / 2) * r * 0.5); paint(ctx, null, 6);
}

// ---------------------------------------------------------------- delivery street (side view) + rider
export function shophouses(ctx, scroll, night = 0) {
  const pal = ['#f2823a', '#2fa3a0', '#e6b52e', '#d9603b', '#7fd3c8'];
  const P = 1600;
  for (let k = -1; k < 3; k++) for (let i = 0; i < 6; i++) {
    const bx = ((i * 270 - scroll) % P + P) % P + k * P - 300;
    if (bx < -400 || bx > 2200) continue;
    const col = pal[(i + 6) % pal.length];
    rrect(ctx, bx, 330, 260, 480, 4); paint(ctx, col, 4);
    rrect(ctx, bx - 6, 320, 272, 20, 4); paint(ctx, '#ffffff', 4);
    for (const wx of [bx + 30, bx + 150]) { rrect(ctx, wx, 380, 80, 110, 30); paint(ctx, '#ffffff', 4); rrect(ctx, wx + 10, 390, 60, 90, 24); paint(ctx, '#bfe0f2', 3); }
    rrect(ctx, bx + 10, 540, 240, 26, 4); paint(ctx, ['#ff9fb2', '#9fe3c9', '#ffd98a'][i % 3], 4);
    rrect(ctx, bx + 40, 600, 180, 210, 4); paint(ctx, '#8f7a8f', 4);
    for (let g = 0; g < 6; g++) { ctx.beginPath(); ctx.moveTo(bx + 46 + g * 30, 600); ctx.lineTo(bx + 46 + g * 30, 810); paint(ctx, null, 2, '#a99aa9'); }
  }
  ctx.fillStyle = '#efd8bf'; ctx.fillRect(-1000, 810, 4000, 60);
  ctx.fillStyle = '#9aa0b5'; ctx.fillRect(-1000, 870, 4000, 400);
  ctx.fillStyle = '#fff6e6'; for (let x = -((scroll * 1.1) % 220) - 220; x < 2200; x += 220) { rrect(ctx, x, 960, 110, 12, 6); ctx.fill(); }
}
export function rider(ctx, x, y, s, t, { flip = false, box = true } = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s * (flip ? -1 : 1), s);
  const bob = Math.sin(t * 18) * 2;
  for (const wx of [-90, 95]) { circle(ctx, wx, -40, 40); paint(ctx, '#3a3946', 5); circle(ctx, wx, -40, 16); paint(ctx, '#c9ccd6', 3); }
  ctx.translate(0, bob);
  smooth(ctx, [[-120, -60], [-60, -110], [40, -110], [110, -80], [130, -50], [60, -40], [-40, -40], [-120, -40]]); paint(ctx, '#7fb6ff', 5);
  rrect(ctx, 70, -170, 18, 90, 6); paint(ctx, '#565c74', 4); rrect(ctx, 60, -176, 60, 12, 6); paint(ctx, '#565c74', 4);
  if (box) { rrect(ctx, -150, -230, 110, 110, 12); paint(ctx, S.nham, 5); nhamLogo(ctx, -95, -175, 0.38); }
  // rider: helmet, body, arms forward
  rrect(ctx, -40, -230, 70, 100, 24); paint(ctx, '#ffb38a', 5);
  ctx.beginPath(); ctx.moveTo(10, -200); ctx.lineTo(80, -170); paint(ctx, null, 22); ctx.beginPath(); ctx.moveTo(10, -200); ctx.lineTo(80, -170); paint(ctx, null, 12, '#ffb38a');
  ctx.beginPath(); ctx.moveTo(-10, -140); ctx.lineTo(30, -90); ctx.lineTo(40, -50); paint(ctx, null, 26); ctx.beginPath(); ctx.moveTo(-10, -140); ctx.lineTo(30, -90); ctx.lineTo(40, -50); paint(ctx, null, 16, '#5d80b2');
  circle(ctx, 0, -262, 34); paint(ctx, '#e2ad85', 4);
  ctx.beginPath(); ctx.arc(-4, -268, 38, Math.PI * 1.02, Math.PI * 2.05); ctx.closePath(); paint(ctx, '#ff8c6b', 5);
  circle(ctx, 14, -258, 4); paint(ctx, INK, 0);
  ctx.restore();
}

// ---------------------------------------------------------------- rooftop at night
export function nightSky(ctx, t, { horizon = 760 } = {}) {
  const g = ctx.createLinearGradient(0, -1200, 0, horizon); g.addColorStop(0, '#1f2048'); g.addColorStop(0.6, S.night); g.addColorStop(1, '#6b5f92');
  ctx.fillStyle = g; ctx.fillRect(-3000, -3000, 9000, horizon + 3000);
  for (let i = 0; i < 140; i++) { const x = hash(i * 1.7) * 2600 - 340, y = hash(i * 2.3) * (horizon + 1200) - 1250, tw = 0.5 + 0.5 * Math.sin(t * 2 + i); circle(ctx, x, y, 1.5 + hash(i) * 2.5); ctx.fillStyle = `rgba(255,246,216,${0.4 + 0.6 * tw})`; ctx.fill(); }
  circle(ctx, 1560, 180, 60); paint(ctx, '#fff3d6', 0);
  circle(ctx, 1585, 165, 52); ctx.fillStyle = '#2d2f5a'; ctx.fill();
}
export function rooftop(ctx, t) {
  ctx.fillStyle = '#7c7398'; ctx.fillRect(-2000, 860, 6000, 600);
  rrect(ctx, -2000, 820, 6000, 50, 4); paint(ctx, '#968cb2', 5);
  for (const lx of [200, 1700]) { ctx.beginPath(); ctx.moveTo(lx, 820); ctx.lineTo(lx, 600); paint(ctx, null, 5); circle(ctx, lx, 590, 14); paint(ctx, S.lamp, 3); ctx.save(); ctx.globalAlpha = 0.3; circle(ctx, lx, 590, 60); ctx.fillStyle = S.lamp; ctx.fill(); ctx.restore(); }
  // fairy lights
  ctx.beginPath(); ctx.moveTo(200, 600); ctx.quadraticCurveTo(950, 700, 1700, 600); paint(ctx, null, 2);
  for (let i = 1; i < 16; i++) { const u = i / 16, x = lerp(200, 1700, u), yy = 600 + 4 * u * (1 - u) * 100 * 1.0; circle(ctx, x, yy + 8, 7); ctx.fillStyle = ['#ffd98a', '#ff9fb2', '#9fe3c9'][i % 3]; ctx.fill(); }
}
