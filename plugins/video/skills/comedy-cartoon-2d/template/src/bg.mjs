// Backgrounds, sets and props.
import { W, H, C, INK, LW, TAU, paint, circle, oval, rrect, poly, smooth, cel, clipTo, text, rng, clamp, lerp, hash, jit } from './core.mjs';

// ---------------------------------------------------------------- sky
export function sky(ctx, { top = C.skyTop, mid = C.skyMid, low = C.skyLow, horizon = 700, cloudX = 0, sun = true } = {}) {
  const g = ctx.createLinearGradient(0, 0, 0, horizon);
  g.addColorStop(0, top); g.addColorStop(0.55, mid); g.addColorStop(1, low);
  ctx.fillStyle = g; ctx.fillRect(-4000, -3000, 12000, horizon + 3000);
  if (sun) { circle(ctx, 1500, horizon - 380, 110); paint(ctx, '#fff0b8', 0); circle(ctx, 1500, horizon - 380, 150); ctx.fillStyle = 'rgba(255,240,184,0.25)'; ctx.fill(); }
  for (const [x, y, s] of [[220, 150, 1], [900, 90, 0.8], [1350, 220, 0.7], [1800, 120, 1.1], [2500, 170, 0.9]]) {
    let cx = ((x - cloudX) % 2600 + 2600) % 2600 - 300;
    cloud(ctx, cx, y, s);
  }
}
export function cloud(ctx, x, y, s) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const p = () => { ctx.beginPath(); for (const [cx, cy, r] of [[-70, 10, 40], [-20, -14, 56], [44, -4, 46], [90, 14, 32]]) { ctx.moveTo(cx + r, cy); ctx.arc(cx, cy, r, 0, TAU); } };
  p(); ctx.fillStyle = C.cloud; ctx.fill(); rrect(ctx, -110, 10, 230, 36, 18); ctx.fill();
  ctx.restore();
}

// ---------------------------------------------------------------- building rows (parallax)
function makeRow(seed, n, wr, hr, pal) {
  const r = rng(seed), items = []; let x = 0;
  for (let i = 0; i < n; i++) {
    const w = Math.round(lerp(wr[0], wr[1], r())), h = Math.round(lerp(hr[0], hr[1], r()));
    items.push({ x, w, h, col: pal[Math.floor(r() * pal.length)], roof: Math.floor(r() * 4), win: Math.floor(r() * 3), seed: r() * 1000 });
    x += w + Math.round(r() * 16);
  }
  return { items, period: x };
}
const FAR = makeRow(11, 16, [110, 230], [200, 420], ['#9fd0c6', '#b6dccf', '#f6c58e', '#efb27c', '#d9b8c8']);
const MID = makeRow(23, 14, [170, 300], [240, 470], [C.teal, C.orange, C.mustard, C.brick, C.plum, C.tealD, C.orangeL]);
const SHOPS = makeRow(37, 9, [280, 380], [250, 330], [C.cream, C.orangeL, C.tealL, C.yellow, '#f5a3a0']);
const darker = col => ({ [C.teal]: C.tealD, [C.orange]: C.orangeD, [C.mustard]: C.yellowD, [C.brick]: C.brickD, [C.plum]: C.plumD, [C.tealD]: '#155b5d', [C.orangeL]: C.orange, [C.cream]: C.creamD, [C.tealL]: C.teal, [C.yellow]: C.yellowD, '#f5a3a0': '#d97a77' }[col] || 'rgba(0,0,0,0.2)');

function forEachWrapped(row, scroll, fn, margin = 400) {
  const P = row.period;
  for (const b of row.items) {
    let sx = ((b.x - scroll) % P + P) % P - margin;
    while (sx < W + margin) { if (sx + b.w > -margin) fn(b, sx); sx += P; }
  }
}
export function farCity(ctx, scroll, baseY) {
  forEachWrapped(FAR, scroll, (b, x) => {
    ctx.fillStyle = b.col; ctx.fillRect(x, baseY - b.h, b.w, b.h + 4);
    if (b.roof === 1) ctx.fillRect(x + b.w * 0.3, baseY - b.h - 40, b.w * 0.4, 40);
    if (b.roof === 2) { ctx.fillRect(x + b.w / 2 - 3, baseY - b.h - 70, 6, 70); }
    ctx.fillStyle = 'rgba(255,255,255,0.18)';
    for (let yy = baseY - b.h + 24; yy < baseY - 30; yy += 46) for (let xx = x + 16; xx < x + b.w - 24; xx += 36) ctx.fillRect(xx, yy, 16, 22);
  }, 300);
}
export function midCity(ctx, scroll, baseY, lw = 5) {
  forEachWrapped(MID, scroll, (b, x) => {
    const top = baseY - b.h;
    if (b.roof === 1) { rrect(ctx, x + b.w * 0.25, top - 50, b.w * 0.5, 54, 4); paint(ctx, darker(b.col), lw); }
    if (b.roof === 2) { // water tower
      ctx.beginPath(); ctx.moveTo(x + b.w * 0.6, top); ctx.lineTo(x + b.w * 0.6 + 6, top - 40); ctx.moveTo(x + b.w * 0.6 + 50, top); ctx.lineTo(x + b.w * 0.6 + 44, top - 40); paint(ctx, null, lw);
      rrect(ctx, x + b.w * 0.6 - 4, top - 100, 58, 62, 10); paint(ctx, '#b0703c', lw);
      ctx.beginPath(); ctx.moveTo(x + b.w * 0.6 - 10, top - 98); ctx.lineTo(x + b.w * 0.6 + 25, top - 128); ctx.lineTo(x + b.w * 0.6 + 60, top - 98); ctx.closePath(); paint(ctx, '#8a5530', lw);
    }
    if (b.roof === 3) { ctx.beginPath(); ctx.moveTo(x + 20, top); ctx.lineTo(x + 20, top - 60); paint(ctx, null, lw - 1); circle(ctx, x + 20, top - 64, 6); paint(ctx, C.red, 3); }
    rrect(ctx, x, top, b.w, b.h + 20, 3);
    cel(ctx, () => rrect(ctx, x, top, b.w, b.h + 20, 3), b.col, darker(b.col), 14, 0, lw);
    rrect(ctx, x - 6, top - 6, b.w + 12, 16, 3); paint(ctx, darker(b.col), lw);
    // windows
    const wc = b.win === 0 ? '#ffe9a8' : b.win === 1 ? '#3d5a66' : '#fff4d6';
    for (let yy = top + 34; yy < baseY - 50; yy += 62) for (let xx = x + 22; xx < x + b.w - 40; xx += 52) {
      const lit = hash(xx * 3.1 + yy * 1.7 + b.seed) > 0.5;
      rrect(ctx, xx, yy, 28, 38, 3); paint(ctx, lit ? '#ffe9a8' : '#3d5a66', 3.5);
    }
  }, 400);
}
export function shopRow(ctx, scroll, baseY) {
  forEachWrapped(SHOPS, scroll, (b, x) => {
    const top = baseY - b.h;
    cel(ctx, () => rrect(ctx, x, top, b.w, b.h + 10, 2), b.col, darker(b.col), 14, 0);
    rrect(ctx, x - 8, top - 10, b.w + 16, 22, 4); paint(ctx, darker(b.col));
    // upper windows
    for (let xx = x + 28; xx < x + b.w - 50; xx += 74) { rrect(ctx, xx, top + 34, 46, 56, 4); paint(ctx, '#ffe9a8', 4.5); ctx.beginPath(); ctx.moveTo(xx + 23, top + 34); ctx.lineTo(xx + 23, top + 90); paint(ctx, null, 3); }
    // awning (striped)
    const ay = top + 120, aw = b.w - 30;
    ctx.save(); poly(ctx, [[x + 15, ay], [x + 15 + aw, ay], [x + 30 + aw, ay + 50], [x, ay + 50]]); ctx.clip();
    for (let i = 0; i < aw + 40; i += 36) { ctx.fillStyle = (i / 36) % 2 ? '#fff6e0' : (b.seed % 2 > 1 ? C.red : C.teal); ctx.fillRect(x + i - 4, ay, 36, 52); }
    ctx.restore(); poly(ctx, [[x + 15, ay], [x + 15 + aw, ay], [x + 30 + aw, ay + 50], [x, ay + 50]]); paint(ctx, null, 5);
    // scalloped edge
    ctx.beginPath(); for (let i = 0; i < aw + 30; i += 30) { ctx.moveTo(x + i + 30, ay + 50); ctx.arc(x + i + 15, ay + 50, 15, 0, Math.PI); } paint(ctx, b.seed % 2 > 1 ? C.red : C.teal, 4.5);
    // shop window + door
    rrect(ctx, x + 24, ay + 82, b.w * 0.5, baseY - ay - 92, 4); paint(ctx, '#bfe8e6', 5);
    ctx.save(); rrect(ctx, x + 24, ay + 82, b.w * 0.5, baseY - ay - 92, 4); ctx.clip(); poly(ctx, [[x + 40, baseY], [x + 90, ay + 70], [x + 110, ay + 70], [x + 60, baseY]]); ctx.fillStyle = 'rgba(255,255,255,0.45)'; ctx.fill(); ctx.restore();
    rrect(ctx, x + b.w * 0.62, ay + 76, b.w * 0.24, baseY - ay - 76, 4); paint(ctx, darker(darker(b.col)) === 'rgba(0,0,0,0.2)' ? C.tealD : '#5b3a2e', 5);
    circle(ctx, x + b.w * 0.62 + 12, ay + 76 + (baseY - ay - 76) / 2, 4); paint(ctx, C.gold, 2);
  }, 420);
}
// ---------------------------------------------------------------- street
export function street(ctx, scroll, y0 = 860, { walk = 70, lanes = true, curbCol = C.curb } = {}) {
  ctx.fillStyle = C.walk; ctx.fillRect(-4000, y0 - walk, 12000, walk);
  // sidewalk tiles
  ctx.strokeStyle = C.walkD; ctx.lineWidth = 4; ctx.beginPath();
  for (let x = -((scroll % 120) + 120) % 120 - 120; x < W + 240; x += 120) { ctx.moveTo(x, y0 - walk); ctx.lineTo(x - 20, y0); }
  ctx.stroke();
  ctx.fillStyle = curbCol; ctx.fillRect(-4000, y0, 12000, 16);
  ctx.beginPath(); ctx.moveTo(-4000, y0); ctx.lineTo(8000, y0); ctx.moveTo(-4000, y0 + 16); ctx.lineTo(8000, y0 + 16); paint(ctx, null, 5);
  ctx.fillStyle = C.road; ctx.fillRect(-4000, y0 + 16, 12000, 2000);
  ctx.fillStyle = C.roadD; ctx.fillRect(-4000, y0 + 16, 12000, 22);
  if (lanes) {
    ctx.fillStyle = C.lane;
    for (let x = -((scroll * 1.15 % 260) + 260) % 260 - 260; x < W + 300; x += 260) { rrect(ctx, x, y0 + 150, 130, 14, 7); ctx.fill(); }
  }
}
export function lamp(ctx, x, y, s = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  rrect(ctx, -16, -24, 32, 24, 4); paint(ctx, C.tealD);
  rrect(ctx, -7, -360, 14, 340, 4); paint(ctx, C.tealD);
  ctx.beginPath(); ctx.moveTo(0, -350); ctx.quadraticCurveTo(0, -390, 50, -390); paint(ctx, null, 14); ctx.beginPath(); ctx.moveTo(0, -350); ctx.quadraticCurveTo(0, -390, 50, -390); paint(ctx, null, 6, C.tealD);
  ctx.beginPath(); ctx.moveTo(30, -392); ctx.lineTo(80, -392); ctx.lineTo(70, -370); ctx.lineTo(40, -370); ctx.closePath(); paint(ctx, C.tealD, 5);
  oval(ctx, 55, -366, 14, 6); paint(ctx, '#fff3b0', 4);
  ctx.restore();
}
export function hydrant(ctx, x, y, s = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  rrect(ctx, -20, -70, 40, 70, 8); paint(ctx, C.red); ctx.beginPath(); ctx.arc(0, -70, 20, Math.PI, TAU); paint(ctx, C.red);
  rrect(ctx, -32, -52, 64, 16, 6); paint(ctx, C.redD); rrect(ctx, -26, -6, 52, 10, 4); paint(ctx, C.redD);
  ctx.restore();
}
export function mailbox(ctx, x, y, s = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  rrect(ctx, -10, -60, 20, 60, 3); paint(ctx, C.navyD);
  ctx.beginPath(); ctx.moveTo(-38, -60); ctx.lineTo(-38, -130); ctx.arc(0, -130, 38, Math.PI, TAU); ctx.lineTo(38, -60); ctx.closePath(); paint(ctx, C.blue);
  rrect(ctx, -24, -128, 48, 8, 3); paint(ctx, INK, 0);
  ctx.restore();
}
export function trashCan(ctx, x, y, s = 1, { crush = 0, lid = true, rot = 0 } = {}) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s * (1 + crush * 0.7), s * (1 - crush * 0.55));
  const body = () => { ctx.beginPath(); ctx.moveTo(-42, -120); ctx.lineTo(42, -120); ctx.lineTo(34, 0); ctx.lineTo(-34, 0); ctx.closePath(); };
  cel(ctx, body, C.metal, C.metalD, -10, 0);
  ctx.beginPath(); for (const yy of [-90, -50, -18]) { ctx.moveTo(-40, yy); ctx.lineTo(40, yy); } paint(ctx, null, 4);
  if (crush > 0.3) { ctx.beginPath(); ctx.moveTo(-20, -100); ctx.lineTo(0, -80); ctx.lineTo(-14, -60); ctx.moveTo(18, -70); ctx.lineTo(4, -40); paint(ctx, null, 4); }
  if (lid) trashLid(ctx, 0, -122, 1, 0);
  ctx.restore();
}
export function trashLid(ctx, x, y, s, rot) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  ctx.beginPath(); ctx.moveTo(-50, 4); ctx.quadraticCurveTo(0, -30, 50, 4); ctx.closePath(); paint(ctx, C.metal);
  rrect(ctx, -12, -24, 24, 10, 4); paint(ctx, C.metalD, 4);
  ctx.restore();
}
export function bananaPeel(ctx, x, y, s = 1, rot = 0) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  for (const a of [-0.9, 0, 0.9]) { ctx.save(); ctx.rotate(a); ctx.beginPath(); ctx.moveTo(-8, 0); ctx.quadraticCurveTo(-14, 30, 0, 44); ctx.quadraticCurveTo(14, 30, 8, 0); ctx.closePath(); paint(ctx, C.yellow, 4.5); ctx.restore(); }
  rrect(ctx, -6, -18, 12, 20, 4); paint(ctx, '#8a6a2a', 4);
  ctx.restore();
}
export function fishBone(ctx, x, y, s = 1, rot = 0) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  ctx.beginPath(); ctx.moveTo(-40, 0); ctx.lineTo(30, 0); for (let i = -30; i <= 20; i += 12) { ctx.moveTo(i, -14); ctx.lineTo(i, 14); } paint(ctx, null, 5, '#f2ece0'); ctx.lineWidth = 0;
  ctx.beginPath(); ctx.moveTo(-40, 0); ctx.lineTo(-56, -14); ctx.lineTo(-56, 14); ctx.closePath(); paint(ctx, '#f2ece0', 4);
  circle(ctx, 40, 0, 12); paint(ctx, '#f2ece0', 4); circle(ctx, 44, -3, 3); paint(ctx, INK, 0);
  ctx.restore();
}
export function tinCan(ctx, x, y, s = 1, rot = 0) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  rrect(ctx, -14, -20, 28, 40, 4); paint(ctx, C.red, 4.5); ctx.fillStyle = '#fff'; ctx.fillRect(-12, -6, 24, 10);
  ctx.restore();
}

// ---------------------------------------------------------------- the BANK
export function bank(ctx, x, y, s = 1, { doors = 0, alarm = 0, t = 0 } = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  // body
  cel(ctx, () => rrect(ctx, -380, -520, 760, 520, 4), C.cream, C.creamD, 18, 0);
  // pediment
  poly(ctx, [[-420, -520], [0, -680], [420, -520]]); paint(ctx, C.teal);
  poly(ctx, [[-330, -540], [0, -650], [330, -540]]); paint(ctx, C.tealD, 5);
  rrect(ctx, -430, -540, 860, 34, 6); paint(ctx, C.creamD);
  // sign
  rrect(ctx, -180, -500, 360, 86, 10); paint(ctx, C.tealD);
  text(ctx, 'BANK', 0, -455, { size: 76, font: 'Rockwell', fill: C.yellow, lw: 8 });
  circle(ctx, 0, -590, 30); paint(ctx, C.yellow, 5); text(ctx, '$', 0, -588, { size: 40, font: 'Arial Black', fill: C.tealD, lw: 0 });
  // columns
  for (const cx of [-300, -170, 170, 300]) {
    cel(ctx, () => rrect(ctx, cx - 30, -400, 60, 380, 4), '#fff4dc', C.creamD, 10, 0);
    rrect(ctx, cx - 40, -410, 80, 20, 4); paint(ctx, C.creamD); rrect(ctx, cx - 40, -36, 80, 20, 4); paint(ctx, C.creamD);
    ctx.beginPath(); for (const k of [-12, 0, 12]) { ctx.moveTo(cx + k, -385); ctx.lineTo(cx + k, -45); } paint(ctx, null, 3, C.creamD);
  }
  // windows w/ bars
  for (const wx of [-236, 236]) { rrect(ctx, wx - 36, -330, 72, 150, 30); paint(ctx, '#3d5a66'); ctx.beginPath(); for (let k = -24; k <= 24; k += 16) { ctx.moveTo(wx + k, -326); ctx.lineTo(wx + k, -184); } paint(ctx, null, 5); }
  // doorway
  rrect(ctx, -110, -330, 220, 316, 10); paint(ctx, '#3a2a30');
  // doors (swing open: scale x toward hinge)
  const dOpen = clamp(doors);
  for (const k of [-1, 1]) {
    ctx.save(); ctx.translate(k * 110, 0); ctx.scale(lerp(1, -0.35, dOpen) * 1, 1);
    rrect(ctx, k > 0 ? -110 : 0, -330, 110, 316, 6); paint(ctx, C.tealD);
    rrect(ctx, k > 0 ? -92 : 18, -300, 74, 110, 6); paint(ctx, C.tealL, 5);
    circle(ctx, k > 0 ? -90 : 90, -170, 8); paint(ctx, C.gold, 4);
    ctx.restore();
  }
  // steps
  for (let i = 0; i < 3; i++) { rrect(ctx, -170 - i * 30, -14 + i * 14 - 14, 340 + i * 60, 16, 3); paint(ctx, C.creamD, 5); }
  // alarm bell
  const ax = 300, ay = -470, sh = alarm > 0 ? Math.sin(t * 90) * 5 * alarm : 0;
  ctx.save(); ctx.translate(ax + sh, ay);
  if (alarm > 0) {
    const on = Math.floor(t * 8) % 2;
    ctx.save(); ctx.globalAlpha = 0.35 * alarm; circle(ctx, 0, 0, on ? 110 : 80); ctx.fillStyle = C.red; ctx.fill(); ctx.restore();
    ctx.beginPath(); for (let i = 0; i < 6; i++) { const a = -Math.PI * 0.95 + i * 0.37; ctx.moveTo(Math.cos(a) * 62, Math.sin(a) * 62); ctx.lineTo(Math.cos(a) * (84 + on * 10), Math.sin(a) * (84 + on * 10)); } paint(ctx, null, 6);
  }
  circle(ctx, 0, 0, 44); paint(ctx, C.red); circle(ctx, -12, -12, 10); paint(ctx, '#ff8a80', 0); circle(ctx, 0, 0, 9); paint(ctx, C.metal, 4);
  ctx.restore();
  ctx.restore();
}

// ---------------------------------------------------------------- speed-line loop (for driving shots)
export function speedBG(ctx, t, { speed = 2400, top = C.orange, mid = C.yellow, band = C.teal, horizon = 640, groundY = 860, roadCol = C.road, dir = 1 } = {}) {
  ctx.fillStyle = top; ctx.fillRect(-1000, -1000, W + 2000, horizon + 1000);
  ctx.fillStyle = mid; ctx.fillRect(-1000, horizon - 260, W + 2000, 260);
  ctx.fillStyle = band; ctx.fillRect(-1000, horizon, W + 2000, groundY - horizon);
  ctx.fillStyle = roadCol; ctx.fillRect(-1000, groundY, W + 2000, 2000);
  // streaks
  const lines = [[horizon - 520, 'rgba(255,255,255,0.55)', 1.0, 260], [horizon - 380, 'rgba(255,240,200,0.6)', 0.8, 420], [horizon - 200, 'rgba(255,255,255,0.7)', 1.2, 300], [horizon - 120, C.orangeL, 0.9, 520],
    [horizon + 50, C.tealL, 1.3, 380], [horizon + 120, C.tealD, 1.1, 260], [horizon + 180, C.tealL, 1.5, 600], [groundY + 40, C.roadL, 1.6, 300], [groundY + 120, C.lane, 1.8, 200], [groundY + 190, C.roadL, 2.0, 500]];
  lines.forEach(([y, col, k, len], i) => {
    const P = 900 + i * 137;
    for (let n = -1; n < 4; n++) {
      const x = ((-(t * speed * k * dir) + n * P + i * 311) % (P * 3) + P * 3) % (P * 3) - P;
      rrect(ctx, x, y, len, 10 + (i % 3) * 4, 6); ctx.fillStyle = col; ctx.fill();
    }
  });
}

// ---------------------------------------------------------------- drive-through
export function driveThru(ctx, x, y, s = 1, { t = 0, speakerTalk = 0, window = 0 } = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  // building (barn-shaped)
  ctx.beginPath(); ctx.moveTo(-420, 0); ctx.lineTo(-420, -340); ctx.lineTo(-280, -470); ctx.lineTo(-20, -470); ctx.lineTo(120, -340); ctx.lineTo(120, 0); ctx.closePath();
  cel(ctx, () => { ctx.beginPath(); ctx.moveTo(-420, 0); ctx.lineTo(-420, -340); ctx.lineTo(-280, -470); ctx.lineTo(-20, -470); ctx.lineTo(120, -340); ctx.lineTo(120, 0); ctx.closePath(); }, C.brick, C.brickD, 16, 0);
  ctx.beginPath(); ctx.moveTo(-440, -330); ctx.lineTo(-290, -490); ctx.lineTo(-10, -490); ctx.lineTo(140, -330); paint(ctx, null, 16); ctx.beginPath(); ctx.moveTo(-440, -330); ctx.lineTo(-290, -490); ctx.lineTo(-10, -490); ctx.lineTo(140, -330); paint(ctx, null, 8, C.cream);
  // sign
  rrect(ctx, -380, -430, 460, 92, 14); paint(ctx, C.yellow);
  text(ctx, 'BURGER BARN', -150, -384, { size: 62, font: 'Impact', fill: C.red, lw: 7 });
  // X-braced barn door panel
  rrect(ctx, -380, -300, 180, 260, 6); paint(ctx, C.cream); ctx.beginPath(); ctx.moveTo(-380, -300); ctx.lineTo(-200, -40); ctx.moveTo(-200, -300); ctx.lineTo(-380, -40); paint(ctx, null, 8);
  // service window
  rrect(ctx, -110, -260, 200, 150, 8); paint(ctx, '#ffe9a8');
  ctx.save(); rrect(ctx, -110, -260, 200, 150, 8); ctx.clip();
  // worker silhouette
  circle(ctx, -10, -190, 36); paint(ctx, C.skin2); rrect(ctx, -46, -170, 72, 70, 20); paint(ctx, C.red);
  rrect(ctx, -44, -236, 70, 24, 6); paint(ctx, C.yellow, 5);
  ctx.restore();
  rrect(ctx, -126, -114, 232, 22, 6); paint(ctx, C.metal);
  rrect(ctx, -120, -276, 220, 26, 8); paint(ctx, C.teal);
  ctx.restore();
}
// menu board + speaker box ("the speaker" talks)
export function menuBoard(ctx, x, y, s = 1, { talk = 0, t = 0 } = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  rrect(ctx, -12, -200, 24, 200, 4); paint(ctx, C.metalD);
  rrect(ctx, -150, -470, 300, 290, 16); paint(ctx, C.tealD);
  text(ctx, 'MENU', 0, -432, { size: 44, font: 'Impact', fill: C.yellow, lw: 6 });
  const items = [['BURGER', '$3'], ['BUCKET', '$9'], ['FRIES', '$2'], ['SHAKE', '$3']];
  items.forEach(([n, p], i) => { text(ctx, n, -124, -380 + i * 48, { size: 28, font: 'Arial Black', fill: C.cream, lw: 0, align: 'left' }); text(ctx, p, 124, -380 + i * 48, { size: 28, font: 'Arial Black', fill: C.yellow, lw: 0, align: 'right' }); });
  // speaker box with a face-like grille
  rrect(ctx, -70, -170, 140, 120, 18); paint(ctx, C.red);
  rrect(ctx, -50, -150, 100, 70, 10); paint(ctx, '#3a2a30', 5);
  const open = talk > 0 ? (0.4 + 0.6 * Math.abs(Math.sin(t * 22))) * talk : 0;
  ctx.beginPath(); for (let i = 0; i < 4; i++) { const yy = -138 + i * 15; ctx.moveTo(-38, yy); ctx.lineTo(38, yy); } paint(ctx, null, 4, '#6a5a60');
  if (talk > 0) { circle(ctx, 54, -158, 7); paint(ctx, '#7cff6a', 3); for (let i = 0; i < 3; i++) { ctx.beginPath(); ctx.arc(70, -120, 22 + i * 16 + open * 8, -0.6, 0.6); paint(ctx, null, 4); } }
  ctx.restore();
}

// ---------------------------------------------------------------- bridge
export function sea(ctx, t, y0, { col = C.sea } = {}) {
  ctx.fillStyle = col; ctx.fillRect(-4000, y0, 12000, 3000);
  ctx.strokeStyle = C.seaL; ctx.lineWidth = 6; ctx.lineCap = 'round';
  for (let r = 0; r < 6; r++) { const yy = y0 + 30 + r * 60; ctx.beginPath(); for (let x = -200 + ((t * 40 * (r % 2 ? 1 : -1)) % 300); x < W + 300; x += 300) { ctx.moveTo(x, yy); ctx.quadraticCurveTo(x + 25, yy - 12, x + 50, yy); ctx.quadraticCurveTo(x + 75, yy + 12, x + 100, yy); } ctx.stroke(); }
}
// arched deck: height profile along x (world). Crest at cx.
export function deckY(x, cx, baseY, rise, half) { const u = clamp((x - cx) / half, -1, 1); return baseY - rise * (1 - u * u); }
export function bridgeTower(ctx, x, baseY, h, s = 1) {
  ctx.save(); ctx.translate(x, baseY); ctx.scale(s, s);
  for (const k of [-1, 1]) cel(ctx, () => rrect(ctx, k * 50 - 22, -h, 44, h + 200, 6), C.tealD, '#155b5d', 8, 0);
  for (const yy of [-h + 40, -h * 0.55, -h * 0.15]) { rrect(ctx, -60, yy, 120, 30, 6); paint(ctx, C.tealD); }
  ctx.restore();
}
// cityscape far across water + hills
export function skyline(ctx, y0, col = '#d98c6a') {
  ctx.fillStyle = col;
  const r = rng(5); let x = -200;
  ctx.beginPath(); ctx.moveTo(-200, y0);
  while (x < W + 200) { const w = 40 + r() * 70, h = 30 + r() * 140; ctx.lineTo(x, y0 - h); ctx.lineTo(x + w, y0 - h); x += w; }
  ctx.lineTo(W + 200, y0); ctx.closePath(); ctx.fill();
}

// ---------------------------------------------------------------- police station + parking
export function policeStation(ctx, x, y, s = 1, { t = 0 } = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  cel(ctx, () => rrect(ctx, -520, -560, 1040, 560, 4), '#7f9cc9', '#62809f', 18, 0);
  // bricks hint
  ctx.save(); rrect(ctx, -520, -560, 1040, 560, 4); ctx.clip(); ctx.strokeStyle = 'rgba(40,50,90,0.18)'; ctx.lineWidth = 3;
  for (let yy = -540; yy < 0; yy += 34) { ctx.beginPath(); ctx.moveTo(-520, yy); ctx.lineTo(520, yy); ctx.stroke(); for (let xx = -520 + ((yy / 34) % 2 ? 0 : 35); xx < 520; xx += 70) { ctx.beginPath(); ctx.moveTo(xx, yy); ctx.lineTo(xx, yy + 34); ctx.stroke(); } }
  ctx.restore();
  rrect(ctx, -560, -590, 1120, 40, 6); paint(ctx, C.navy);
  // sign
  rrect(ctx, -330, -540, 660, 110, 14); paint(ctx, C.navy);
  text(ctx, 'POLICE STATION', 0, -484, { size: 80, font: 'Impact', fill: '#fff', lw: 0 });
  // windows
  for (const wx of [-420, -260, 260, 420]) { rrect(ctx, wx - 50, -390, 100, 130, 6); paint(ctx, '#ffe9a8'); ctx.beginPath(); ctx.moveTo(wx, -390); ctx.lineTo(wx, -260); ctx.moveTo(wx - 50, -325); ctx.lineTo(wx + 50, -325); paint(ctx, null, 4); }
  // blue lamps
  for (const lx of [-150, 150]) { rrect(ctx, lx - 6, -330, 12, 60, 3); paint(ctx, INK, 0); circle(ctx, lx, -350, 26); paint(ctx, '#6fa8ff'); ctx.save(); ctx.globalAlpha = 0.3; circle(ctx, lx, -350, 46); ctx.fillStyle = '#9fc4ff'; ctx.fill(); ctx.restore(); }
  // door
  rrect(ctx, -100, -260, 200, 260, 8); paint(ctx, C.navyD); ctx.beginPath(); ctx.moveTo(0, -260); ctx.lineTo(0, 0); paint(ctx, null, 5);
  rrect(ctx, -84, -240, 66, 90, 6); paint(ctx, '#bfe8e6', 4); rrect(ctx, 18, -240, 66, 90, 6); paint(ctx, '#bfe8e6', 4);
  ctx.restore();
}
export function squadCar(ctx, x, y, s = 1, { t = 0, flip = false } = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s * (flip ? -1 : 1), s);
  oval(ctx, 0, 0, 230, 14); ctx.fillStyle = 'rgba(40,20,40,0.25)'; ctx.fill();
  for (const wx of [-140, 140]) { circle(ctx, wx, -40, 40); paint(ctx, C.tire); circle(ctx, wx, -40, 18); paint(ctx, C.metal, 5); }
  const body = () => { ctx.beginPath(); ctx.moveTo(-250, -60); ctx.lineTo(-250, -130); ctx.lineTo(-150, -140); ctx.lineTo(-100, -215); ctx.lineTo(90, -215); ctx.lineTo(150, -140); ctx.lineTo(250, -130); ctx.lineTo(250, -60); ctx.closePath(); };
  cel(ctx, body, '#fbfbfb', '#d8dde6', 0, -12);
  ctx.save(); body(); ctx.clip(); ctx.fillStyle = INK; ctx.fillRect(-260, -110, 520, 50); ctx.restore(); body(); paint(ctx, null);
  for (const [a, b] of [[-140, -10], [10, 130]]) { poly(ctx, [[a, -150], [a + 30, -205], [b - 20, -205], [b, -150]]); paint(ctx, '#3d5a66', 5); }
  ctx.save(); ctx.scale(flip ? -1 : 1, 1); text(ctx, 'POLICE', 0, -88, { size: 38, font: 'Arial Black', fill: '#fff', lw: 0 }); ctx.restore();
  rrect(ctx, -40, -238, 80, 22, 6); paint(ctx, C.red, 5); ctx.fillStyle = C.blue; ctx.fillRect(0, -235, 37, 16);
  ctx.restore();
}

// ---------------------------------------------------------------- top-down city (for the turn-signal gag)
export function topCity(ctx, { blocks, roadCol = C.road }) {
  ctx.fillStyle = roadCol; ctx.fillRect(-500, -500, W + 1000, H + 1000);
  for (const [bx, by, bw, bh, col, park] of blocks) {
    rrect(ctx, bx - 16, by - 16, bw + 32, bh + 32, 26); paint(ctx, C.walk, 5);
    if (park) { rrect(ctx, bx, by, bw, bh, 18); paint(ctx, '#e7a35a'); for (let i = 0; i < 5; i++) { circle(ctx, bx + 40 + (i * 97) % (bw - 60), by + 40 + (i * 61) % (bh - 60), 26); paint(ctx, C.orange, 5); } }
    else {
      cel(ctx, () => rrect(ctx, bx, by, bw, bh, 12), col, 'rgba(0,0,0,0.15)', -12, -12);
      rrect(ctx, bx + 20, by + 20, bw - 40, bh - 40, 8); paint(ctx, null, 3, 'rgba(0,0,0,0.25)');
    }
  }
}
export function carTop(ctx, x, y, s, rot, { blink = null, on = false, t = 0 } = {}) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  for (const [wx, wy] of [[-55, -48], [55, -48], [-55, 48], [55, 48]]) { rrect(ctx, wx - 18, wy - 10, 36, 20, 6); paint(ctx, C.tire, 4); }
  rrect(ctx, -90, -46, 180, 92, 30); paint(ctx, C.green);
  rrect(ctx, -60, -38, 100, 76, 18); paint(ctx, C.greenD, 5);
  rrect(ctx, 28, -34, 26, 68, 8); paint(ctx, C.interior, 4);
  // Marge's legs sticking out the left window
  ctx.beginPath(); ctx.moveTo(-40, -40); ctx.lineTo(-60, -84); ctx.moveTo(-22, -40); ctx.lineTo(-30, -88); paint(ctx, null, 12); ctx.beginPath(); ctx.moveTo(-40, -40); ctx.lineTo(-60, -84); ctx.moveTo(-22, -40); ctx.lineTo(-30, -88); paint(ctx, null, 7, C.black);
  circle(ctx, -14, 0, 26); paint(ctx, C.sack, 5); text(ctx, '$', -14, 2, { size: 30, font: 'Arial Black', fill: C.moneyD, lw: 0 });
  // headlights
  for (const k of [-1, 1]) { rrect(ctx, 80, k * 28 - 8, 12, 16, 4); paint(ctx, '#fff6c0', 3); }
  if (blink && on) {
    const k = blink === 'L' ? -1 : 1;
    for (const bx of [-86, 86]) { circle(ctx, bx, k * 40, 10); paint(ctx, '#ffb000', 3); ctx.save(); ctx.globalAlpha = 0.4; circle(ctx, bx, k * 40, 26); ctx.fillStyle = '#ffd040'; ctx.fill(); ctx.restore(); }
    // Benny's hand signal out the window
    ctx.beginPath(); ctx.moveTo(40, k * 40); ctx.lineTo(40, k * 80); paint(ctx, null, 14); circle(ctx, 40, k * 84, 10); paint(ctx, C.skin, 4);
  }
  ctx.restore();
}
export function bikeTop(ctx, x, y, s, rot, t = 0) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  ctx.beginPath(); ctx.moveTo(-50, 0); ctx.lineTo(50, 0); paint(ctx, null, 10);
  ctx.beginPath(); ctx.moveTo(34, -22); ctx.lineTo(34, 22); paint(ctx, null, 7);
  oval(ctx, -6, 0, 26, 34); paint(ctx, C.copBlue);
  circle(ctx, 6, 0, 18); paint(ctx, C.navy); rrect(ctx, 18, -10, 12, 20, 4); paint(ctx, INK, 0);
  const on = Math.floor(t * 8) % 2; circle(ctx, 50, 0, 8); paint(ctx, on ? C.red : C.blue, 3);
  ctx.restore();
}
