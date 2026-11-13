// Phone + laptop screens for "Don't Click Strange Links", and the little icons they use
// (padlock, shield, check/cross, warning, Wi-Fi, gift, stamp) plus the cartoon thief.
// phoneUI(ctx, cx, cy, h, t, state) draws a big cartoon phone centred on (cx, cy); laptopUI(ctx, x, y, w, h, t, state)
// draws a laptop whose screen is the rect (x, y, w, h). `state.mode` picks the screen; the other keys are 0..1 animations.
import { GlobalFonts } from '@napi-rs/canvas';
import { INK, TAU, paint, circle, oval, rrect, poly, smooth, hose, text, clamp, lerp, seg, ease, hash } from './core.mjs';

GlobalFonts.registerFromPath('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 'Arial Bold');
GlobalFonts.registerFromPath('/System/Library/Fonts/Supplemental/Courier New Bold.ttf', 'Courier New Bold');

export const UI = { bg: '#f4f1ff', card: '#ffffff', ink: '#2d2a3e', dim: '#8d87b0', line: '#dcd7ef', red: '#e8433a', redL: '#ffd3cf', green: '#46c34f', greenL: '#d4f5d0', blue: '#3f7fe0', yellow: '#ffd23f', purple: '#7f5cff', dark: '#232036' };
const lab = (ctx, s, x, y, size, fill = UI.ink, o = {}) => text(ctx, s, x, y, { size, fill, lw: 0, font: 'Arial Bold', ...o });

// one line of text in pieces [[str, colour, mark]], mark = highlight colour (or true); returns the width
export function richLine(ctx, parts, x, y, size, { font = 'Courier New Bold', align = 'left' } = {}) {
  ctx.save(); ctx.font = `${size}px "${font}"`; ctx.textBaseline = 'middle'; ctx.textAlign = 'left';
  const ws = parts.map(p => ctx.measureText(p[0]).width), tot = ws.reduce((a, b) => a + b, 0);
  let cx = align === 'center' ? x - tot / 2 : x;
  parts.forEach(([s, col, mark], i) => {
    if (mark) { rrect(ctx, cx - 4, y - size * 0.62, ws[i] + 8, size * 1.24, size * 0.2); ctx.fillStyle = typeof mark === 'string' ? mark : UI.redL; ctx.fill(); }
    ctx.fillStyle = col; ctx.fillText(s, cx, y); cx += ws[i];
  });
  ctx.restore();
  return tot;
}
// x of the i-th piece's centre (for pointing at a highlighted letter)
export function pieceX(ctx, parts, i, x, size, { font = 'Courier New Bold', align = 'left' } = {}) {
  ctx.save(); ctx.font = `${size}px "${font}"`;
  const ws = parts.map(p => ctx.measureText(p[0]).width), tot = ws.reduce((a, b) => a + b, 0);
  ctx.restore();
  let cx = align === 'center' ? x - tot / 2 : x; for (let k = 0; k < i; k++) cx += ws[k];
  return cx + ws[i] / 2;
}

// ---------------------------------------------------------------- icons
export function padlock(ctx, x, y, s = 1, { open = 0, col = UI.yellow, label = null, labelCol = INK } = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.save(); ctx.translate(0, -open * 34); ctx.lineCap = 'butt';
  ctx.beginPath(); ctx.moveTo(-40, -6); ctx.lineTo(-40, -40); ctx.arc(0, -40, 40, Math.PI, 0); ctx.lineTo(40, -6 + open * 30);
  ctx.lineWidth = 30; ctx.strokeStyle = INK; ctx.stroke(); ctx.lineWidth = 16; ctx.strokeStyle = '#b8bfcc'; ctx.stroke();
  ctx.restore();
  rrect(ctx, -64, -16, 128, 104, 20); paint(ctx, col, 7);
  rrect(ctx, -50, -6, 100, 14, 7); ctx.fillStyle = 'rgba(255,255,255,0.35)'; ctx.fill();
  if (label) text(ctx, label, 0, 40, { size: 44, font: 'Arial Black', fill: labelCol, lw: 0 });
  else { circle(ctx, 0, 30, 12); paint(ctx, INK, 0); poly(ctx, [[-7, 32], [7, 32], [10, 62], [-10, 62]]); paint(ctx, INK, 0); }
  ctx.restore();
}
function shieldPath(ctx) { ctx.beginPath(); ctx.moveTo(0, -92); ctx.quadraticCurveTo(46, -62, 82, -70); ctx.lineTo(78, 0); ctx.quadraticCurveTo(68, 62, 0, 98); ctx.quadraticCurveTo(-68, 62, -78, 0); ctx.lineTo(-82, -70); ctx.quadraticCurveTo(-46, -62, 0, -92); ctx.closePath(); }
export function shield(ctx, x, y, s = 1, { col = UI.green, glow = 0, word = null, mark = 'check', k = 1, t = 0 } = {}) {
  if (s <= 0) return;
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  if (glow > 0) { ctx.save(); ctx.globalAlpha = glow * (0.55 + 0.2 * Math.sin(t * 7)); const g = ctx.createRadialGradient(0, 0, 40, 0, 0, 200); g.addColorStop(0, '#b6ffb0'); g.addColorStop(1, 'rgba(182,255,176,0)'); ctx.fillStyle = g; ctx.fillRect(-200, -200, 400, 400); ctx.restore(); }
  shieldPath(ctx); paint(ctx, col, 7);
  ctx.save(); ctx.scale(0.74, 0.74); shieldPath(ctx); ctx.restore(); ctx.fillStyle = 'rgba(255,255,255,0.22)'; ctx.fill();
  if (mark === 'check') check(ctx, 0, 4, 1.1, k);
  if (word) text(ctx, word, 0, 140, { size: 60, font: 'Arial Black', fill: '#ffffff', lw: 12 });
  ctx.restore();
}
function strokePart(ctx, pts, k, s, col) {
  const L = []; let tot = 0; for (let i = 1; i < pts.length; i++) { const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); L.push(d); tot += d; }
  let rem = tot * clamp(k); ctx.beginPath(); ctx.moveTo(...pts[0]);
  for (let i = 1; i < pts.length && rem > 0; i++) { const f = Math.min(1, rem / L[i - 1]); ctx.lineTo(lerp(pts[i - 1][0], pts[i][0], f), lerp(pts[i - 1][1], pts[i][1], f)); rem -= L[i - 1]; }
  ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.lineWidth = 26 * s; ctx.strokeStyle = INK; ctx.stroke(); ctx.lineWidth = 14 * s; ctx.strokeStyle = col; ctx.stroke();
}
export function check(ctx, x, y, s = 1, k = 1, col = '#ffffff') { if (k <= 0) return; ctx.save(); ctx.translate(x, y); strokePart(ctx, [[-36 * s, 0], [-10 * s, 26 * s], [38 * s, -28 * s]], k, s, col); ctx.restore(); }
export function cross(ctx, x, y, s = 1, k = 1, col = '#ffffff') { if (k <= 0) return; ctx.save(); ctx.translate(x, y); strokePart(ctx, [[-30 * s, -30 * s], [30 * s, 30 * s]], k * 2, s, col); if (k > 0.5) strokePart(ctx, [[30 * s, -30 * s], [-30 * s, 30 * s]], k * 2 - 1, s, col); ctx.restore(); }
export function warnTri(ctx, x, y, s = 1, col = UI.red) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.beginPath(); ctx.moveTo(0, -80); ctx.lineTo(84, 66); ctx.lineTo(-84, 66); ctx.closePath(); ctx.lineJoin = 'round'; ctx.lineWidth = 30; ctx.strokeStyle = INK; ctx.stroke(); ctx.lineWidth = 16; ctx.strokeStyle = col; ctx.stroke(); ctx.fillStyle = col; ctx.fill();
  text(ctx, '!', 0, 14, { size: 96, font: 'Arial Black', fill: '#ffffff', lw: 0 });
  ctx.restore();
}
export function wifi(ctx, x, y, s = 1, { col = UI.blue, bars = 3, lw = 14 } = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.lineCap = 'round';
  circle(ctx, 0, 0, 12); paint(ctx, col, 5);
  for (let i = 1; i <= 3; i++) { ctx.beginPath(); ctx.arc(0, 0, 16 + i * 26, -Math.PI * 0.75, -Math.PI * 0.25); ctx.lineWidth = lw + 10; ctx.strokeStyle = INK; ctx.stroke(); ctx.lineWidth = lw; ctx.strokeStyle = i <= bars ? col : '#c9c4dd'; ctx.stroke(); }
  ctx.restore();
}
export function gift(ctx, x, y, s = 1, t = 0) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(Math.sin(t * 8) * 0.08);
  rrect(ctx, -50, -20, 100, 76, 8); paint(ctx, '#ff5c8a', 6); rrect(ctx, -58, -44, 116, 30, 8); paint(ctx, '#ff7aa2', 6);
  ctx.fillStyle = UI.yellow; ctx.fillRect(-10, -42, 20, 96); for (const k of [-1, 1]) { oval(ctx, k * 22, -56, 22, 13, k * 0.5); paint(ctx, UI.yellow, 5); }
  ctx.restore();
}
// rubber stamp slamming down: k 0..1
export function stamp(ctx, word, x, y, k, { col = UI.red, rot = -0.18, size = 120 } = {}) {
  if (k <= 0) return;
  const sc = k < 0.25 ? lerp(2.4, 0.92, ease.in(k / 0.25)) : 1 + 0.08 * Math.sin(Math.min(1, (k - 0.25) / 0.3) * Math.PI) * (1 - (k - 0.25));
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(sc, sc); ctx.globalAlpha = k < 0.25 ? 0.5 + 2 * k : 1;
  ctx.font = `${size}px "Impact"`; const w = ctx.measureText(word).width + size * 0.6, h = size * 1.25;
  rrect(ctx, -w / 2, -h / 2, w, h, size * 0.16); ctx.lineWidth = size * 0.1; ctx.strokeStyle = col; ctx.stroke();
  rrect(ctx, -w / 2 + size * 0.1, -h / 2 + size * 0.1, w - size * 0.2, h - size * 0.2, size * 0.1); ctx.lineWidth = size * 0.035; ctx.stroke();
  text(ctx, word, 0, size * 0.04, { size, fill: col, lw: 0 });
  ctx.restore();
}

// ---------------------------------------------------------------- the cartoon thief (hooded, eye mask, sneaky grin)
// origin at the feet, ~260 px tall at s = 1. pose: sneak | type | grab | bonk | laugh | sit
export function thief(ctx, x, y, s = 1, t = 0, { pose = 'sneak', flip = false, sq = 0, look = 1, reach = null } = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s * (flip ? -1 : 1) * (1 + sq), s / (1 + sq));
  const tw = Math.floor(t * 12) / 12, bob = pose === 'sneak' ? Math.abs(Math.sin(tw * 7)) * -8 : pose === 'laugh' ? Math.abs(Math.sin(tw * 16)) * -6 : 0;
  const HOOD = '#4b3a6b', HOODD = '#3a2c56', GLOVE = '#ffffff';
  if (pose !== 'sit') for (const k of [-1, 1]) {
    const ph = pose === 'sneak' ? Math.sin(tw * 7 + (k > 0 ? Math.PI : 0)) * 16 : 0, lift = pose === 'sneak' ? Math.max(0, Math.sin(tw * 7 + (k > 0 ? Math.PI : 0))) * 12 : 0;
    hose(ctx, [[k * 22, -78], [k * 26 + ph * 0.5, -40 - lift], [k * 24 + ph, -10 - lift]], 20, '#2a2433');
    oval(ctx, k * 24 + ph + 10, -8 - lift, 24, 11); paint(ctx, INK, 4);
  }
  ctx.translate(0, bob);
  const body = () => smooth(ctx, [[-50, -160], [50, -160], [64, -80], [40, -64], [-40, -64], [-64, -80]]);
  body(); paint(ctx, HOOD); rrect(ctx, -30, -112, 60, 28, 10); paint(ctx, HOODD, 4);
  const hands = {
    sneak: [[-70, -150], [70, -150]], type: [[-36, -96], [40, -100]], grab: [[-60, -100], reach || [40, -260]],
    bonk: [[-80, -190], [80, -190]], laugh: [[-40, -110], [44, -120]], sit: [[-40, -100], [44, -104]],
  }[pose] || [[-60, -100], [60, -100]];
  if (pose === 'type') { const b = Math.sin(t * 30); hands[0][1] -= Math.max(0, b) * 10; hands[1][1] -= Math.max(0, -b) * 10; }
  for (const [i, hd] of hands.entries()) { const sh = [i ? 40 : -40, -146]; hose(ctx, [sh, [lerp(sh[0], hd[0], 0.5) + (i ? 18 : -18), lerp(sh[1], hd[1], 0.5) + 10], hd], 20, HOOD); circle(ctx, hd[0], hd[1], 17); paint(ctx, GLOVE, 5); }
  // head in a hood
  const hy = -214;
  circle(ctx, 0, hy, 70); paint(ctx, HOOD);
  oval(ctx, 6 * look, hy + 8, 50, 46); paint(ctx, '#c98f68', 5);
  rrect(ctx, -50 + 6 * look, hy - 22, 100, 32, 14); paint(ctx, INK, 0);
  const dazed = pose === 'bonk';
  for (const ex of [-18, 22]) {
    oval(ctx, ex + 6 * look, hy - 6, 11, 10); paint(ctx, '#fff8e8', 0);
    if (dazed) { ctx.save(); ctx.translate(ex + 6 * look, hy - 6); ctx.rotate(t * 12); ctx.beginPath(); ctx.moveTo(-6, 0); ctx.lineTo(6, 0); ctx.moveTo(0, -6); ctx.lineTo(0, 6); paint(ctx, null, 3); ctx.restore(); }
    else { circle(ctx, ex + 6 * look + 3 * look, hy - 5, 4.5); paint(ctx, INK, 0); }
  }
  // sneaky grin with teeth (a wobbly O when bonked)
  if (dazed) { oval(ctx, 6 * look, hy + 32, 12, 9); paint(ctx, '#7a3640', 4); }
  else { ctx.beginPath(); ctx.moveTo(-26 + 6 * look, hy + 20); ctx.quadraticCurveTo(6 * look, hy + 50, 34 + 6 * look, hy + 18); ctx.quadraticCurveTo(6 * look, hy + 30, -26 + 6 * look, hy + 20); paint(ctx, '#ffffff', 4); }
  ctx.restore();
}

// ---------------------------------------------------------------- the phone
// screen-local layout (in u = h/1000): screen 456 x 956. LINK is where the scam link sits (for a finger to aim at).
export const PHONE = { link: [0.5, 0.6], answer: [0.75, 0.86], decline: [0.25, 0.86], update: [0.5, 0.52] };
export const phonePoint = (cx, cy, h, [fx, fy]) => { const u = h / 1000, sw = h * 0.5 - 44 * u, sh = h - 44 * u; return [cx - sw / 2 + fx * sw, cy - sh / 2 + fy * sh]; };
export function phoneUI(ctx, cx, cy, h, t, st = {}) {
  const w = h * 0.5, u = h / 1000;
  ctx.save(); ctx.translate(cx, cy); ctx.rotate(st.rot || 0);
  if (st.buzz) { ctx.translate(Math.sin(t * 95) * 7 * u * st.buzz * 3, 0); ctx.rotate(Math.sin(t * 70) * 0.03 * st.buzz); }
  rrect(ctx, -w / 2, -h / 2, w, h, 70 * u); paint(ctx, st.body || '#2c2a33', Math.max(4, 10 * u));
  const sw = w - 44 * u, sh = h - 44 * u;
  ctx.save(); rrect(ctx, -sw / 2, -sh / 2, sw, sh, 52 * u); ctx.clip(); ctx.translate(-sw / 2, -sh / 2);
  phoneScreen(ctx, sw, sh, u, t, st);
  ctx.restore();
  rrect(ctx, -60 * u, -h / 2 + 34 * u, 120 * u, 28 * u, 14 * u); ctx.fillStyle = st.body || '#2c2a33'; ctx.fill();
  ctx.restore();
}
function statusBar(ctx, sw, u, col = UI.ink) {
  lab(ctx, '8:15', 52 * u, 42 * u, 26 * u, col);
  rrect(ctx, sw - 86 * u, 30 * u, 44 * u, 22 * u, 5 * u); ctx.lineWidth = 3 * u; ctx.strokeStyle = col; ctx.stroke(); ctx.fillStyle = col; ctx.fillRect(sw - 82 * u, 34 * u, 30 * u, 14 * u);
}
function msgHeader(ctx, sw, u, name = 'Unknown', sub = '+855 96 *** 777') {
  ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, sw, 170 * u); ctx.fillStyle = UI.line; ctx.fillRect(0, 168 * u, sw, 3 * u);
  statusBar(ctx, sw, u);
  circle(ctx, 80 * u, 115 * u, 34 * u); ctx.fillStyle = '#c9c4dd'; ctx.fill(); lab(ctx, '?', 80 * u, 117 * u, 40 * u, '#ffffff');
  lab(ctx, name, 132 * u, 102 * u, 30 * u, UI.ink, { align: 'left' }); lab(ctx, sub, 132 * u, 136 * u, 22 * u, UI.dim, { align: 'left' });
}
function bubble(ctx, x, y, w, h, u, col = '#e9e6f5') { rrect(ctx, x, y, w, h, 30 * u); ctx.fillStyle = col; ctx.fill(); poly(ctx, [[x + 10 * u, y + h - 30 * u], [x - 14 * u, y + h + 6 * u], [x + 40 * u, y + h - 6 * u]]); ctx.fill(); }
function phoneScreen(ctx, sw, sh, u, t, st) {
  const m = st.mode || 'home';
  if (m === 'home' || m === 'code') {
    const g = ctx.createLinearGradient(0, 0, 0, sh); g.addColorStop(0, '#7fd3c8'); g.addColorStop(1, '#3f7fe0'); ctx.fillStyle = g; ctx.fillRect(0, 0, sw, sh);
    statusBar(ctx, sw, u, '#ffffff');
    lab(ctx, '8:15', sw / 2, 230 * u, 130 * u, '#ffffff'); lab(ctx, 'Monday', sw / 2, 320 * u, 30 * u, '#ffffff');
    if (m === 'home') for (let i = 0; i < 8; i++) { const ix = 80 * u + (i % 4) * 100 * u, iy = 560 * u + Math.floor(i / 4) * 120 * u; rrect(ctx, ix - 34 * u, iy - 34 * u, 68 * u, 68 * u, 18 * u); ctx.fillStyle = ['#ff5c8a', '#ffd23f', '#46c34f', '#ff9a3f', '#a07bff', '#ffffff', '#2fd3a0', '#e8433a'][i]; ctx.fill(); }
    if (m === 'code') {
      const k = ease.back(clamp(st.k ?? 1)), y0 = lerp(-260 * u, 420 * u, k);
      rrect(ctx, 24 * u, y0, sw - 48 * u, 230 * u, 30 * u); ctx.fillStyle = 'rgba(255,255,255,0.95)'; ctx.fill();
      lab(ctx, 'MyBank  •  now', 60 * u, y0 + 44 * u, 22 * u, UI.dim, { align: 'left' });
      lab(ctx, 'Your login code:', 60 * u, y0 + 88 * u, 28 * u, UI.ink, { align: 'left' });
      lab(ctx, '482 915', sw / 2, y0 + 160 * u, 78 * u, UI.purple);
    }
    return;
  }
  ctx.fillStyle = UI.bg; ctx.fillRect(0, 0, sw, sh);
  if (m === 'msg' || m === 'quiz') {
    msgHeader(ctx, sw, u, m === 'quiz' ? 'MyBank?' : 'Unknown');
    const bx = 30 * u, by = 230 * u, bw = sw - 80 * u;
    if (m === 'msg') {
      const k = ease.back(clamp(st.k ?? 1)); ctx.save(); ctx.translate(bx, by + 300 * u); ctx.scale(k, k); ctx.translate(-bx, -by - 300 * u);
      bubble(ctx, bx, by, bw, 520 * u, u);
      gift(ctx, bx + bw / 2, by + 90 * u, 0.9 * u * 1.1, t);
      lab(ctx, 'Congratulations!', bx + bw / 2, by + 200 * u, 34 * u, UI.ink);
      lab(ctx, 'You won a', bx + bw / 2, by + 250 * u, 34 * u, UI.ink); lab(ctx, 'NEW PHONE!', bx + bw / 2, by + 298 * u, 40 * u, '#ff5c8a');
      const fl = st.flash ? (Math.floor(t * 6) % 2 ? 1 : 0) : 0;
      rrect(ctx, bx + 30 * u, by + 360 * u, bw - 60 * u, 120 * u, 24 * u); ctx.fillStyle = fl ? UI.yellow : '#dfe9ff'; ctx.fill();
      lab(ctx, 'Click here >>', bx + bw / 2, by + 396 * u, 30 * u, UI.blue);
      richLine(ctx, [['fr33-phone.win', UI.blue]], bx + bw / 2, by + 444 * u, 26 * u, { align: 'center' });
      ctx.fillStyle = UI.blue; ctx.fillRect(bx + 80 * u, by + 462 * u, bw - 160 * u, 3 * u);
      ctx.restore();
    } else {
      bubble(ctx, bx, by, bw, 560 * u, u);
      lab(ctx, 'MyBank:', bx + 40 * u, by + 60 * u, 30 * u, UI.ink, { align: 'left' });
      lab(ctx, 'Your account', bx + 40 * u, by + 115 * u, 34 * u, UI.ink, { align: 'left' }); lab(ctx, 'is LOCKED!', bx + 40 * u, by + 160 * u, 38 * u, UI.red, { align: 'left' });
      lab(ctx, 'Log in now:', bx + 40 * u, by + 230 * u, 30 * u, UI.ink, { align: 'left' });
      const r1 = st.reveal1 || 0, r2 = st.reveal2 || 0;
      richLine(ctx, [['r', UI.blue, r1 > 0 ? UI.redL : 0], ['n', UI.blue, r1 > 0 ? UI.redL : 0], ['ybank-login.co', UI.blue]], bx + 40 * u, by + 290 * u, 30 * u);
      if (r1 > 0) { const parts = [['r', UI.blue], ['n', UI.blue], ['ybank-login.co', UI.blue]], ox = (pieceX(ctx, parts, 0, bx + 40 * u, 30 * u) + pieceX(ctx, parts, 1, bx + 40 * u, 30 * u)) / 2; ctx.save(); ctx.globalAlpha = clamp(r1 * 3); oval(ctx, ox, by + 290 * u, 34 * u, 30 * u); paint(ctx, null, 5 * u, UI.red); ctx.restore(); }
      rrect(ctx, bx + 40 * u, by + 350 * u, bw - 80 * u, 70 * u, 14 * u); ctx.fillStyle = '#ffffff'; ctx.fill();
      lab(ctx, 'Password: _______', bx + 60 * u, by + 386 * u, 28 * u, UI.dim, { align: 'left' });
      if (r2 > 0) { ctx.save(); ctx.globalAlpha = clamp(r2 * 3); rrect(ctx, bx + 30 * u, by + 340 * u, bw - 60 * u, 90 * u, 18 * u); paint(ctx, null, 5 * u, UI.red); ctx.restore(); }
      lab(ctx, 'Hurry! 10 minutes left!', bx + 40 * u, by + 480 * u, 26 * u, UI.red, { align: 'left' });
    }
    if (st.alert > 0) {
      const a = clamp(st.alert);
      ctx.save(); ctx.globalAlpha = 0.9 * clamp(a * 2); ctx.fillStyle = UI.red; ctx.fillRect(0, 0, sw, sh);
      for (let i = 0; i < 6; i++) { ctx.fillStyle = 'rgba(0,0,0,0.12)'; ctx.fillRect(0, ((t * 300 * u + i * 180 * u) % sh), sw, 60 * u); }
      ctx.restore();
      const k = ease.back(seg(a, 0.1, 0.6));
      ctx.save(); ctx.translate(sw / 2, 380 * u); ctx.scale(k, k);
      warnTri(ctx, 0, 0, 1.3 * u * (1 + 0.06 * Math.sin(t * 14)), UI.yellow);
      ctx.restore();
      if (k > 0) { ctx.save(); ctx.translate(sw / 2, 600 * u); ctx.scale(k, k); text(ctx, 'PHISHING!', 0, 0, { size: 84 * u, fill: '#ffffff', lw: 12 * u }); text(ctx, 'សារបោកប្រាស់', 0, 110 * u, { size: 56 * u, fill: UI.yellow, lw: 10 * u }); ctx.restore(); }
    }
    return;
  }
  if (m === 'tutorial') { // a video-editing lesson playing; st.k = playback progress
    ctx.fillStyle = '#16141f'; ctx.fillRect(0, 0, sw, sh); statusBar(ctx, sw, u, '#ffffff');
    const vy = 110 * u, vh = 330 * u; ctx.fillStyle = '#2d2a3e'; ctx.fillRect(0, vy, sw, vh);
    rrect(ctx, 24 * u, vy + 24 * u, sw - 48 * u, 150 * u, 10 * u); ctx.fillStyle = '#3f7fe0'; ctx.fill();
    circle(ctx, sw / 2, vy + 99 * u, 34 * u); ctx.fillStyle = 'rgba(255,255,255,0.9)'; ctx.fill(); poly(ctx, [[sw / 2 - 10 * u, vy + 80 * u], [sw / 2 + 18 * u, vy + 99 * u], [sw / 2 - 10 * u, vy + 118 * u]]); ctx.fillStyle = '#3f7fe0'; ctx.fill();
    const cols = ['#ff9a3f', '#2fd3a0', '#ffd23f', '#ff5c8a', '#a07bff'];
    for (let i = 0; i < 5; i++) { rrect(ctx, 24 * u + i * 84 * u, vy + 200 * u, 76 * u, 46 * u, 8 * u); ctx.fillStyle = cols[i]; ctx.fill(); }
    for (let i = 0; i < 5; i++) { rrect(ctx, 24 * u + i * 84 * u, vy + 258 * u, 76 * u, 30 * u, 6 * u); ctx.fillStyle = '#55507a'; ctx.fill(); }
    const px = 24 * u + ((t * 0.35) % 1) * (sw - 48 * u); ctx.fillStyle = '#ff4d6d'; ctx.fillRect(px - 2 * u, vy + 190 * u, 5 * u, 110 * u);
    const k = st.k ?? 0.35; ctx.fillStyle = '#4a4560'; ctx.fillRect(20 * u, vy + vh + 22 * u, sw - 40 * u, 8 * u); ctx.fillStyle = '#ff4d6d'; ctx.fillRect(20 * u, vy + vh + 22 * u, (sw - 40 * u) * k, 8 * u); circle(ctx, 20 * u + (sw - 40 * u) * k, vy + vh + 26 * u, 12 * u); ctx.fill();
    text(ctx, 'មេរៀនទី ១៖ កាត់តវីដេអូ', 28 * u, vy + vh + 96 * u, { size: 46 * u, fill: '#ffffff', lw: 0, align: 'left' });
    lab(ctx, 'Video editing for beginners', 28 * u, vy + vh + 150 * u, 24 * u, '#b9b3d6', { align: 'left' });
    for (let i = 0; i < 3; i++) { const yy = vy + vh + 200 * u + i * 110 * u; rrect(ctx, 24 * u, yy, 150 * u, 90 * u, 10 * u); ctx.fillStyle = cols[i + 1]; ctx.fill(); text(ctx, `មេរៀនទី ${'២៣៤'[i]}`, 200 * u, yy + 34 * u, { size: 34 * u, fill: '#ffffff', lw: 0, align: 'left' }); rrect(ctx, 200 * u, yy + 62 * u, 180 * u, 12 * u, 6 * u); ctx.fillStyle = '#3d3852'; ctx.fill(); }
    return;
  }
  if (m === 'text') {
    msgHeader(ctx, sw, u, st.from || 'Manager', st.sub || 'now');
    const k = ease.back(clamp(st.k ?? 1)), lines = st.lines || [];
    ctx.save(); ctx.translate(30 * u, 260 * u); ctx.scale(k, k); ctx.translate(-30 * u, -260 * u);
    bubble(ctx, 30 * u, 230 * u, sw - 80 * u, (lines.length * 52 + 60) * u, u);
    lines.forEach((l, i) => lab(ctx, l, 60 * u, 284 * u + i * 52 * u, 34 * u, UI.ink, { align: 'left' }));
    ctx.restore();
    return;
  }
  if (m === 'update') {
    statusBar(ctx, sw, u);
    lab(ctx, 'Settings', 50 * u, 130 * u, 46 * u, UI.ink, { align: 'left' });
    rrect(ctx, 30 * u, 200 * u, sw - 60 * u, 620 * u, 30 * u); ctx.fillStyle = '#ffffff'; ctx.fill();
    const done = clamp(st.done || 0), prog = clamp(st.prog || 0);
    if (done < 0.5) {
      // gear
      ctx.save(); ctx.translate(sw / 2, 320 * u); ctx.rotate(prog * 6); for (let i = 0; i < 8; i++) { ctx.rotate(TAU / 8); ctx.fillStyle = '#9aa3b5'; ctx.fillRect(-12 * u, -66 * u, 24 * u, 26 * u); } circle(ctx, 0, 0, 48 * u); paint(ctx, '#9aa3b5', 0); circle(ctx, 0, 0, 18 * u); ctx.fillStyle = '#ffffff'; ctx.fill(); ctx.restore();
      lab(ctx, 'Software Update', sw / 2, 440 * u, 36 * u, UI.ink); lab(ctx, prog > 0 ? 'Installing…' : 'Available', sw / 2, 488 * u, 30 * u, prog > 0 ? UI.dim : UI.red);
      if (prog <= 0) { const p = st.press || 0, sc = 1 - 0.12 * Math.sin(clamp(p) * Math.PI); ctx.save(); ctx.translate(sw / 2, 600 * u); ctx.scale(sc, sc); rrect(ctx, -150 * u, -46 * u, 300 * u, 92 * u, 46 * u); ctx.fillStyle = UI.blue; ctx.fill(); lab(ctx, 'Update Now', 0, 2 * u, 34 * u, '#ffffff'); ctx.restore(); }
      else { rrect(ctx, 70 * u, 580 * u, sw - 140 * u, 40 * u, 20 * u); ctx.fillStyle = '#e6e3f2'; ctx.fill(); rrect(ctx, 70 * u, 580 * u, (sw - 140 * u) * prog, 40 * u, 20 * u); ctx.fillStyle = UI.green; ctx.fill(); lab(ctx, `${Math.round(prog * 100)}%`, sw / 2, 670 * u, 34 * u, UI.ink); }
    } else {
      const k = ease.back(seg(done, 0.5, 0.9));
      shield(ctx, sw / 2, 420 * u, 1.5 * u * k, { glow: 1, t });
      lab(ctx, 'Up to date', sw / 2, 680 * u, 40 * u, UI.green);
    }
    return;
  }
  if (m === 'call' || m === 'blocked') {
    const g = ctx.createLinearGradient(0, 0, 0, sh); g.addColorStop(0, m === 'call' ? '#3b2d55' : '#ffffff'); g.addColorStop(1, m === 'call' ? '#1d1830' : '#f4f1ff'); ctx.fillStyle = g; ctx.fillRect(0, 0, sw, sh);
    statusBar(ctx, sw, u, m === 'call' ? '#ffffff' : UI.ink);
    if (m === 'call') {
      const ringing = !st.answered;
      if (ringing) for (let i = 0; i < 3; i++) { const k = (t * 1.2 + i / 3) % 1; ctx.save(); ctx.globalAlpha = 1 - k; circle(ctx, sw / 2, 330 * u, (90 + k * 120) * u); ctx.lineWidth = 6 * u; ctx.strokeStyle = '#c3a8ff'; ctx.stroke(); ctx.restore(); }
      circle(ctx, sw / 2, 330 * u, 90 * u); ctx.fillStyle = '#6d5a8f'; ctx.fill(); lab(ctx, '?', sw / 2, 334 * u, 110 * u, '#ffffff');
      lab(ctx, 'Unknown Number', sw / 2, 520 * u, 40 * u, '#ffffff'); lab(ctx, '+855 ?? ??? ???', sw / 2, 572 * u, 28 * u, '#c3bce0');
      lab(ctx, ringing ? 'incoming call…' : `00:0${Math.min(9, Math.floor(st.timer || 0))}`, sw / 2, 630 * u, 28 * u, '#c3bce0');
      const btn = (x, col, rot) => { circle(ctx, x, 830 * u, 60 * u); ctx.fillStyle = col; ctx.fill(); ctx.save(); ctx.translate(x, 830 * u); ctx.rotate(rot); rrect(ctx, -34 * u, -10 * u, 68 * u, 20 * u, 10 * u); ctx.fillStyle = '#ffffff'; ctx.fill(); ctx.restore(); };
      if (ringing) { btn(sw * 0.25, UI.red, 0); btn(sw * 0.75, UI.green, -0.5 + Math.sin(t * 20) * 0.2); }
      else { const p = st.press || 0; ctx.save(); ctx.translate(sw / 2, 830 * u); ctx.scale(1 - 0.15 * Math.sin(clamp(p) * Math.PI), 1 - 0.15 * Math.sin(clamp(p) * Math.PI)); ctx.translate(-sw / 2, -830 * u); btn(sw / 2, UI.red, 0); ctx.restore(); }
    } else {
      const k = ease.back(clamp(st.k ?? 1));
      ctx.save(); ctx.translate(sw / 2, 360 * u); ctx.scale(k, k); circle(ctx, 0, 0, 110 * u); ctx.lineWidth = 26 * u; ctx.strokeStyle = UI.red; ctx.stroke(); ctx.save(); ctx.rotate(-0.78); ctx.fillStyle = UI.red; ctx.fillRect(-100 * u, -13 * u, 200 * u, 26 * u); ctx.restore(); ctx.restore();
      lab(ctx, 'Number Blocked', sw / 2, 560 * u, 42 * u, UI.red);
      lab(ctx, '+855 ?? ??? ???', sw / 2, 620 * u, 28 * u, UI.dim); ctx.fillStyle = UI.dim; ctx.fillRect(sw / 2 - 110 * u, 618 * u, 220 * u, 4 * u);
    }
    return;
  }
  if (m === 'safe') {
    const g = ctx.createLinearGradient(0, 0, 0, sh); g.addColorStop(0, '#7be07a'); g.addColorStop(1, '#2f9e47'); ctx.fillStyle = g; ctx.fillRect(0, 0, sw, sh);
    statusBar(ctx, sw, u, '#ffffff');
    shield(ctx, sw / 2, sh * 0.42, 1.9 * u * ease.back(clamp(st.k ?? 1)), { glow: 1, t, col: '#46c34f' });
    text(ctx, 'SAFE', sw / 2, sh * 0.72, { size: 110 * u, font: 'Arial Black', fill: '#ffffff', lw: 14 * u });
  }
}

// ---------------------------------------------------------------- the laptop
// The screen is (x, y, w, h); a keyboard deck is drawn under it unless base === false.
export function laptopUI(ctx, x, y, w, h, t, st = {}) {
  const u = w / 1000;
  if (st.base !== false) { poly(ctx, [[x - 30 * u, y + h + 26 * u], [x + w + 30 * u, y + h + 26 * u], [x + w + 110 * u, y + h + 120 * u], [x - 110 * u, y + h + 120 * u]]); paint(ctx, '#c9cfdb', 7); poly(ctx, [[x + 60 * u, y + h + 44 * u], [x + w - 60 * u, y + h + 44 * u], [x + w - 30 * u, y + h + 92 * u], [x + 30 * u, y + h + 92 * u]]); paint(ctx, '#9aa3b5', 0); }
  rrect(ctx, x - 26 * u, y - 26 * u, w + 52 * u, h + 52 * u, 26 * u); paint(ctx, '#2c2a33', 7);
  ctx.save(); rrect(ctx, x, y, w, h, 8 * u); ctx.clip(); ctx.translate(x, y);
  ctx.fillStyle = UI.bg; ctx.fillRect(0, 0, w, h);
  // browser chrome
  ctx.fillStyle = '#e6e3f2'; ctx.fillRect(0, 0, w, 54 * u); for (let i = 0; i < 3; i++) { circle(ctx, (28 + i * 26) * u, 27 * u, 8 * u); ctx.fillStyle = ['#ff5f57', '#febc2e', '#28c840'][i]; ctx.fill(); }
  laptopScreen(ctx, w, h, u, t, st);
  ctx.restore();
}
function card(ctx, x, y, w, h, u, col = '#ffffff') { rrect(ctx, x, y, w, h, 22 * u); ctx.fillStyle = col; ctx.fill(); ctx.lineWidth = 3 * u; ctx.strokeStyle = UI.line; ctx.stroke(); }
function addrBar(ctx, x, y, w, u, parts, { lock = true, warn = false, size = 30 } = {}) {
  rrect(ctx, x, y - 30 * u, w, 60 * u, 30 * u); ctx.fillStyle = '#ffffff'; ctx.fill(); ctx.lineWidth = 3 * u; ctx.strokeStyle = UI.line; ctx.stroke();
  if (lock) padlock(ctx, x + 36 * u, y + 2 * u, 0.24 * u, { col: UI.green });
  if (warn) warnTri(ctx, x + 36 * u, y + 2 * u, 0.2 * u, UI.red);
  return richLine(ctx, parts, x + 66 * u, y, size * u);
}
const fakeParts = (hl, flash) => [['http://myb', UI.ink], ['4', hl > 0 ? UI.red : UI.ink, hl > 0 ? (flash ? UI.yellow : UI.redL) : 0], ['nk.com', UI.ink]];
function laptopScreen(ctx, w, h, u, t, st) {
  const m = st.mode || 'blank';
  if (m === 'links') {
    const L = clamp(st.labels ?? 1), hl = st.hl || 0, flash = hl > 0 && Math.floor(t * 4) % 2 === 0;
    for (const [i, real] of [[0, true], [1, false]]) {
      const cx = i ? 520 * u : 40 * u, cw = 440 * u;
      card(ctx, cx, 90 * u, cw, h - 120 * u, u);
      rrect(ctx, cx, 90 * u, cw, 80 * u, 22 * u); ctx.fillStyle = real ? UI.green : UI.red; ctx.globalAlpha = L; ctx.fill(); ctx.globalAlpha = 1;
      if (L > 0) { ctx.save(); ctx.globalAlpha = L; text(ctx, real ? 'REAL ✓' : 'FAKE ✗', cx + cw / 2, 132 * u, { size: 46 * u, font: 'Arial Black', fill: '#ffffff', lw: 0 }); ctx.restore(); }
      if (real) addrBar(ctx, cx + 20 * u, 225 * u, cw - 40 * u, u, [['https://mybank.com', UI.ink]], { size: 27 });
      else addrBar(ctx, cx + 20 * u, 225 * u, cw - 40 * u, u, fakeParts(hl, flash), { lock: false, warn: hl > 0, size: 27 });
      // the bank page itself (the fake one is a perfect copy: that's the trick)
      circle(ctx, cx + cw / 2 - 90 * u, 330 * u, 34 * u); ctx.fillStyle = UI.yellow; ctx.fill(); lab(ctx, '$', cx + cw / 2 - 90 * u, 332 * u, 40 * u, UI.ink);
      lab(ctx, 'MyBank', cx + cw / 2 + 30 * u, 332 * u, 46 * u, '#2f6fe0');
      for (let r = 0; r < 2; r++) { rrect(ctx, cx + 60 * u, 400 * u + r * 70 * u, cw - 120 * u, 50 * u, 12 * u); ctx.fillStyle = '#f0eef8'; ctx.fill(); }
      rrect(ctx, cx + 120 * u, 545 * u, cw - 240 * u, 56 * u, 28 * u); ctx.fillStyle = UI.blue; ctx.fill(); lab(ctx, 'Log in', cx + cw / 2, 574 * u, 28 * u, '#ffffff');
    }
    if (st.mag > 0) {
      const k = ease.inOut(clamp(st.mag)), fx0 = pieceX(ctx, fakeParts(1, 0), 1, 606 * u, 27 * u), fy0 = 225 * u, mx = lerp(w * 0.75, fx0, k), my = lerp(h * 0.75, fy0 + 10 * u, k), R = 70 * u;
      ctx.save(); circle(ctx, mx, my, R); ctx.clip(); ctx.fillStyle = '#ffffff'; ctx.fillRect(mx - R, my - R, 2 * R, 2 * R);
      if (k > 0.85) { ctx.save(); ctx.globalAlpha = seg(k, 0.85, 1); lab(ctx, '4', mx, my + 4 * u, 110 * u, UI.red); ctx.restore(); }
      ctx.restore();
      ctx.save(); ctx.translate(mx, my); ctx.rotate(0.7); rrect(ctx, R - 6 * u, -16 * u, 130 * u, 32 * u, 14 * u); paint(ctx, '#8a4f7d', 6); ctx.restore();
      circle(ctx, mx, my, R); paint(ctx, null, 12 * u, INK); circle(ctx, mx, my, R - 6 * u); paint(ctx, null, 6 * u, '#9aa3b5');
    }
    if (st.stamp > 0) stamp(ctx, 'FAKE!', 740 * u, 430 * u, st.stamp, { size: 110 * u, rot: -0.2 });
    if (st.stranger > 0) { const k = ease.back(clamp(st.stranger)); ctx.save(); ctx.translate(260 * u, 470 * u); ctx.scale(k, k); rrect(ctx, -200 * u, -50 * u, 400 * u, 100 * u, 24 * u); paint(ctx, '#fff6c0', 5); lab(ctx, 'From: Unknown?', 0, 2 * u, 34 * u, UI.red); ctx.restore(); }
    return;
  }
  if (m === '2fa') {
    // login card (left), the 2FA lock (middle), the phone with the code (right)
    card(ctx, 40 * u, 100 * u, 380 * u, h - 140 * u, u);
    lab(ctx, 'MyBank Login', 230 * u, 150 * u, 34 * u, '#2f6fe0');
    for (const [r, l] of ['User', 'Password'].entries()) { lab(ctx, l, 80 * u, 220 * u + r * 110 * u, 24 * u, UI.dim, { align: 'left' }); rrect(ctx, 70 * u, 240 * u + r * 110 * u, 320 * u, 54 * u, 12 * u); ctx.fillStyle = '#f0eef8'; ctx.fill(); }
    lab(ctx, 'smey', 90 * u, 268 * u, 28 * u, UI.ink, { align: 'left' });
    lab(ctx, '•'.repeat(Math.round(clamp(st.typed ?? 1) * 8)), 90 * u, 382 * u, 34 * u, UI.ink, { align: 'left' });
    rrect(ctx, 110 * u, 450 * u, 240 * u, 56 * u, 28 * u); ctx.fillStyle = UI.blue; ctx.fill(); lab(ctx, 'Log in', 230 * u, 479 * u, 28 * u, '#ffffff');
    const lock = ease.back(clamp(st.lock ?? 1)), deny = st.deny || 0;
    if (deny > 0 && deny < 1) { ctx.save(); ctx.globalAlpha = 0.35 * Math.sin(deny * Math.PI); ctx.fillStyle = UI.red; ctx.fillRect(0, 0, w, h); ctx.restore(); }
    padlock(ctx, 560 * u, 360 * u, 1.55 * u, { open: 1 - lock, col: lock > 0.9 ? UI.green : UI.yellow, label: '2FA', labelCol: '#ffffff' });
    if (deny > 0.15 && deny < 1) text(ctx, 'DENIED!', 560 * u, 560 * u, { size: 64 * u, fill: UI.red, lw: 10 * u, rot: -0.08 });
    // the phone with the code
    phoneUI(ctx, 840 * u, 340 * u, 440 * u, t, { mode: 'code', k: st.code ?? 1 });
    return;
  }
  if (m === 'password') {
    const weak = clamp(st.weak ?? 1), crack = clamp(st.crack || 0), strong = clamp(st.strong || 0);
    lab(ctx, 'Password', 160 * u, 150 * u, 40 * u, UI.ink, { align: 'left' });
    rrect(ctx, 150 * u, 190 * u, 700 * u, 110 * u, 20 * u); ctx.fillStyle = '#ffffff'; ctx.fill(); ctx.lineWidth = 6 * u; ctx.strokeStyle = strong > 0 ? UI.green : crack > 0 || weak > 0.99 ? UI.red : UI.line; ctx.stroke();
    if (strong <= 0) {
      const digits = '123456'.slice(0, Math.round(weak * 6));
      for (let i = 0; i < digits.length; i++) {
        const fall = Math.max(0, crack - 0.25 - hash(i) * 0.2) * 1.6, dx = (i - 2.5) * 70 * u + (hash(i * 3) - 0.5) * fall * 300 * u, dy = fall * fall * 900 * u;
        ctx.save(); ctx.translate(500 * u + dx, 248 * u + dy); ctx.rotate((hash(i * 7) - 0.5) * fall * 6); ctx.globalAlpha = 1 - clamp(fall * 1.2);
        text(ctx, digits[i], 0, 0, { size: 84 * u, font: 'Arial Black', fill: weak > 0.99 ? UI.red : UI.ink, lw: 0 }); ctx.restore();
      }
      if (crack > 0 && crack < 0.45) { ctx.save(); ctx.globalAlpha = 1 - seg(crack, 0.3, 0.45); ctx.beginPath(); const pts = [[300, 195], [350, 230], [330, 260], [420, 300]]; ctx.moveTo(pts[0][0] * u, pts[0][1] * u); for (const p of pts) ctx.lineTo(p[0] * u, p[1] * u); ctx.moveTo(620 * u, 190 * u); ctx.lineTo(600 * u, 240 * u); ctx.lineTo(660 * u, 270 * u); ctx.lineTo(640 * u, 300 * u); paint(ctx, null, 7 * u, INK); ctx.restore(); }
    } else {
      const pw = 'Mango-TukTuk-77!', n = Math.round(strong * pw.length);
      richLine(ctx, [[pw.slice(0, n), UI.ink]], 190 * u, 248 * u, 58 * u);
      if (strong > 0.99) check(ctx, 900 * u, 248 * u, 1.1 * u * ease.back(seg(st.ok || 0, 0, 1)), 1, UI.green);
    }
    // strength meter
    const lvl = strong > 0 ? strong : weak * 0.18 * (1 - crack);
    lab(ctx, 'Strength', 160 * u, 370 * u, 30 * u, UI.dim, { align: 'left' });
    rrect(ctx, 150 * u, 400 * u, 700 * u, 40 * u, 20 * u); ctx.fillStyle = '#e6e3f2'; ctx.fill();
    if (lvl > 0.01) { rrect(ctx, 150 * u, 400 * u, 700 * u * lvl, 40 * u, 20 * u); ctx.fillStyle = strong > 0.6 ? UI.green : strong > 0 ? UI.yellow : UI.red; ctx.fill(); }
    const word = strong > 0.6 ? 'STRONG' : strong > 0 ? '…' : weak > 0.99 ? 'WEAK!' : '';
    lab(ctx, word, 500 * u, 500 * u, 54 * u, strong > 0.6 ? UI.green : UI.red);
    if (st.accounts > 0) { // a different password for every account
      const k = clamp(st.accounts);
      [['MyBank', '#2f6fe0'], ['Mail', '#e8433a'], ['Social', '#7f5cff']].forEach(([nm, col], i) => { const kk = ease.back(seg(k, i * 0.25, i * 0.25 + 0.4)); if (kk <= 0) return; ctx.save(); ctx.translate(250 * u + i * 250 * u, 566 * u); ctx.scale(kk, kk); rrect(ctx, -110 * u, -36 * u, 220 * u, 72 * u, 18 * u); ctx.fillStyle = col; ctx.fill(); lab(ctx, nm, 0, -8 * u, 24 * u, '#ffffff'); lab(ctx, ['K7#m...', 'Zq!9...', 'Tuk@3...'][i], 0, 20 * u, 20 * u, '#ffffff'); ctx.restore(); });
    }
    return;
  }
  if (m === 'slides') {
    const clean = clamp(st.clean || 0);
    for (let i = 0; i < 4; i++) { rrect(ctx, 24 * u, (80 + i * 120) * u, 150 * u, 100 * u, 8 * u); ctx.fillStyle = i === 0 ? '#ffe7d6' : '#ffffff'; ctx.fill(); ctx.lineWidth = 3 * u; ctx.strokeStyle = i === 0 ? '#e07a5f' : UI.line; ctx.stroke(); }
    const sx = 200 * u, sy = 80 * u, sw2 = 770 * u, sh2 = 500 * u;
    rrect(ctx, sx, sy, sw2, sh2, 12 * u); ctx.fillStyle = '#ffffff'; ctx.fill(); ctx.lineWidth = 4 * u; ctx.strokeStyle = UI.line; ctx.stroke();
    ctx.save(); rrect(ctx, sx, sy, sw2, sh2, 12 * u); ctx.clip();
    // the wall of text flies away line by line
    lab(ctx, 'REPORT 2027 — ALL DETAILS', sx + 30 * u, sy + 40 * u, 30 * u, UI.ink, { align: 'left' });
    for (let i = 0; i < 14; i++) { const f = ease.in(seg(clean, i * 0.035, i * 0.035 + 0.35)); ctx.globalAlpha = 1 - f; ctx.fillStyle = '#c9c4dd'; ctx.fillRect(sx + 30 * u + f * 900 * u, sy + (80 + i * 28) * u, (420 + hash(i) * 280) * u, 12 * u); }
    ctx.globalAlpha = 1;
    const k = ease.back(seg(clean, 0.6, 0.9));
    if (k > 0) {
      ctx.fillStyle = '#ffffff'; ctx.fillRect(sx, sy, sw2, sh2);
      ctx.save(); ctx.translate(sx + sw2 / 2, sy + sh2 * 0.42); ctx.scale(k, k);
      circle(ctx, 0, -20, 80 * u); paint(ctx, '#fff27a', 7 * u); rrect(ctx, -34 * u, 52 * u, 68 * u, 46 * u, 10 * u); paint(ctx, '#9aa3b5', 6 * u);
      ctx.restore();
      ctx.save(); ctx.globalAlpha = clamp(k); text(ctx, 'មួយស្លាយ = គំនិតមួយ', sx + sw2 / 2, sy + sh2 * 0.84, { size: 56 * u, fill: '#e07a5f', lw: 0 }); ctx.restore();
    }
    ctx.restore();
    return;
  }
  if (m === 'profile') {
    const blur = st.blur || [0, 0, 0], priv = clamp(st.priv || 0);
    ctx.fillStyle = '#ffb070'; ctx.fillRect(0, 54 * u, w, 120 * u);
    circle(ctx, 140 * u, 190 * u, 74 * u); paint(ctx, '#cf9468', 6); // Smey's avatar
    ctx.save(); ctx.beginPath(); ctx.arc(140 * u, 190 * u, 74 * u, Math.PI * 1.05, Math.PI * 1.95); ctx.closePath(); ctx.fillStyle = '#221d24'; ctx.fill(); ctx.restore();
    for (const k of [-1, 1]) { circle(ctx, 140 * u + k * 22 * u, 196 * u, 7 * u); ctx.fillStyle = INK; ctx.fill(); }
    oval(ctx, 143 * u, 218 * u, 14 * u, 12 * u); paint(ctx, '#d98266', 3); ctx.beginPath(); ctx.arc(140 * u, 236 * u, 18 * u, 0.2, Math.PI - 0.2); paint(ctx, null, 4 * u);
    lab(ctx, 'Smey', 240 * u, 230 * u, 50 * u, UI.ink, { align: 'left' });
    // privacy toggle
    const tx = 640 * u, ty = 230 * u;
    rrect(ctx, tx, ty - 34 * u, 320 * u, 68 * u, 34 * u); ctx.fillStyle = priv > 0.5 ? UI.greenL : UI.redL; ctx.fill(); ctx.lineWidth = 4 * u; ctx.strokeStyle = priv > 0.5 ? UI.green : UI.red; ctx.stroke();
    circle(ctx, tx + lerp(36, 284, ease.inOut(priv)) * u, ty, 26 * u); paint(ctx, priv > 0.5 ? UI.green : UI.red, 4 * u);
    lab(ctx, priv > 0.5 ? 'Friends Only' : 'Public', tx + (priv > 0.5 ? 130 : 180) * u, ty + 2 * u, 30 * u, priv > 0.5 ? '#2f8c43' : UI.red);
    const rows = [['Phone', '012 345 678'], ['Birthday', '12 / 05 / 1994'], ['Home', 'St. 271, Phnom Penh']];
    rows.forEach(([k, v], i) => {
      const ry = 340 * u + i * 85 * u;
      card(ctx, 60 * u, ry - 34 * u, 880 * u, 68 * u, u);
      lab(ctx, k, 90 * u, ry, 30 * u, UI.dim, { align: 'left' });
      lab(ctx, v, 330 * u, ry, 34 * u, UI.ink, { align: 'left' });
      const b = clamp(blur[i] || 0);
      if (b > 0) { // pixelate over the value
        const bw = 520 * u * ease.out(b);
        for (let px = 0; px < bw; px += 26 * u) for (let py = -28 * u; py < 28 * u; py += 26 * u) { ctx.fillStyle = ['#b9b3d6', '#cfc9e6', '#a59fc6', '#ddd8ef'][Math.floor(hash(px * 0.37 + py * 1.3 + i) * 4)]; ctx.fillRect(320 * u + px, ry + py, Math.min(26 * u, bw - px), 26 * u); }
        if (b > 0.9) padlock(ctx, 860 * u, ry + 4 * u, 0.26 * u, { col: UI.green });
      }
    });
  }
}
