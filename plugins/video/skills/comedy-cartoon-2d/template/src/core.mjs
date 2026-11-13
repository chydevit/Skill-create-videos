// Shared drawing + timing helpers: palette, easing, ink/fill/cel-shade primitives, rubber-hose limbs, IK, lettering.
import { GlobalFonts } from '@napi-rs/canvas';
import { fileURLToPath } from 'node:url';
import fs from 'node:fs';

export const W = 1920, H = 1080, FPS = 24;
// film.json "style": "bold" (default: TV-cartoon ink + 7 px lines) or "pastel" (soft plum ink, 5 px clean lines)
const STYLE = (() => { try { return JSON.parse(fs.readFileSync('film.json', 'utf8')).style || 'bold'; } catch { return 'bold'; } })();
export const INK = STYLE === 'pastel' ? '#3b2d3b' : '#1d1520';
export const LW = STYLE === 'pastel' ? 5 : 7;

GlobalFonts.registerFromPath('/System/Library/Fonts/Supplemental/Impact.ttf', 'Impact');
GlobalFonts.registerFromPath('/System/Library/Fonts/Supplemental/Arial Black.ttf', 'Arial Black');
GlobalFonts.registerFromPath('/System/Library/Fonts/Supplemental/Rockwell.ttc', 'Rockwell');
GlobalFonts.registerFromPath('/System/Library/Fonts/Supplemental/ChalkboardSE.ttc', 'Chalkboard SE');
// Khmer display face (bundled, OFL). text() switches to it automatically for Khmer strings.
for (const f of [fileURLToPath(new URL('../assets/fonts/Koulen-Regular.ttf', import.meta.url)), `${process.env.HOME}/Library/Fonts/Koulen-Regular.ttf`]) {
  try { if (GlobalFonts.registerFromPath(f, 'Koulen')) break; } catch {}
}
export const isKhmer = s => /[\u1780-\u17FF\u19E0-\u19FF]/.test(s);

export const C = {
  skyTop: '#ff9f5a', skyMid: '#ffc46b', skyLow: '#ffe2a0',
  cloud: '#fff4da', cloudS: '#ffd9a8',
  teal: '#2fa3a0', tealD: '#1d7476', tealL: '#7fd3c8', tealF: '#8fc9c0',
  orange: '#f2823a', orangeD: '#c95f22', orangeL: '#ffb070',
  yellow: '#ffd23f', yellowD: '#e0a91c', mustard: '#e6b52e',
  brick: '#d9603b', brickD: '#a8432a', cream: '#fbe8c4', creamD: '#e9c993',
  plum: '#8a4f7d', plumD: '#62345a',
  road: '#5b6273', roadD: '#474d5c', roadL: '#6f7789', lane: '#fbe8c4',
  walk: '#efcf9f', walkD: '#d9b07c', curb: '#c79a6c',
  green: '#46c34f', greenD: '#2c8c39', greenL: '#93e66f', greenX: '#1f6a2b',
  red: '#e8433a', redD: '#b02a24', blue: '#2f6fe0', blueD: '#1f4aa8',
  skin: '#f6c39b', skinD: '#dc9a70', skin2: '#eab38a', skin2D: '#c98a62',
  white: '#ffffff', glass: '#bfe8e6', interior: '#2f4b52',
  metal: '#c8d0d8', metalD: '#8e99a5', tire: '#2c2a30', tireL: '#4a4750',
  navy: '#2d3a6b', navyD: '#1e2750', black: '#2a2633', blackL: '#3d3849',
  hairRed: '#d8452f', hairRedD: '#a8301f',
  sack: '#d7ac6a', sackD: '#b0844a', money: '#7fcf6a', moneyD: '#4f9a45',
  copBlue: '#3566b8', copBlueD: '#244a8c', gold: '#ffcc33',
  sea: '#2f8fa3', seaD: '#226f82', seaL: '#5fb8c4',
};

export const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
export const lerp = (a, b, t) => a + (b - a) * t;
export const seg = (t, a, b) => clamp((t - a) / (b - a));
export const TAU = Math.PI * 2;
export const ease = {
  in: t => t * t,
  out: t => 1 - (1 - t) * (1 - t),
  inOut: t => (t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2),
  in3: t => t * t * t,
  out3: t => 1 - Math.pow(1 - t, 3),
  back: t => { const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
  elastic: t => (t <= 0 ? 0 : t >= 1 ? 1 : Math.pow(2, -9 * t) * Math.sin((t * 10 - 0.75) * (TAU / 3)) + 1),
  bounce: t => {
    const n1 = 7.5625, d1 = 2.75;
    if (t < 1 / d1) return n1 * t * t;
    if (t < 2 / d1) return n1 * (t -= 1.5 / d1) * t + 0.75;
    if (t < 2.5 / d1) return n1 * (t -= 2.25 / d1) * t + 0.9375;
    return n1 * (t -= 2.625 / d1) * t + 0.984375;
  },
};
// Character animation is held "on twos" (12 drawings/sec) like TV cartoons.
export const onTwos = t => Math.floor(t * 12 + 1e-6) / 12;
export const hash = n => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
export const jit = (t, seed, amp) => (hash(Math.floor(t * 12 + 1e-6) * 7.13 + seed * 91.7) - 0.5) * 2 * amp;
export function rng(seed) {
  let a = seed >>> 0;
  return () => { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
// damped spring settle: 0 at t=0 -> oscillates -> 0
export const wobble = (t, freq = 3, damp = 5) => (t < 0 ? 0 : Math.sin(t * freq * TAU) * Math.exp(-t * damp));

export function paint(ctx, fill, lw = LW, stroke = INK) {
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (lw > 0) { ctx.lineWidth = lw; ctx.strokeStyle = stroke; ctx.lineJoin = 'round'; ctx.lineCap = 'round'; ctx.stroke(); }
}
export function circle(ctx, x, y, r) { ctx.beginPath(); ctx.arc(x, y, Math.max(0.01, r), 0, TAU); }
export function oval(ctx, x, y, rx, ry, rot = 0) { ctx.beginPath(); ctx.ellipse(x, y, Math.max(0.01, Math.abs(rx)), Math.max(0.01, Math.abs(ry)), rot, 0, TAU); }
export function rrect(ctx, x, y, w, h, r) {
  r = Math.min(r, Math.abs(w) / 2, Math.abs(h) / 2);
  ctx.beginPath();
  ctx.moveTo(x + r, y); ctx.lineTo(x + w - r, y); ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r); ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h); ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r); ctx.quadraticCurveTo(x, y, x + r, y); ctx.closePath();
}
export function poly(ctx, pts, closed = true) {
  ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
  if (closed) ctx.closePath();
}
// Catmull-Rom through points -> smooth closed/open blob
export function smooth(ctx, pts, closed = true, tension = 0.5, newPath = true) {
  const n = pts.length;
  if (newPath) ctx.beginPath();
  const P = i => (closed ? pts[(i + n) % n] : pts[clamp(i, 0, n - 1)]);
  ctx.moveTo(pts[0][0], pts[0][1]);
  const last = closed ? n : n - 1;
  for (let i = 0; i < last; i++) {
    const p0 = P(i - 1), p1 = P(i), p2 = P(i + 1), p3 = P(i + 2);
    const k = tension / 3 * 2;
    ctx.bezierCurveTo(p1[0] + (p2[0] - p0[0]) * k / 2, p1[1] + (p2[1] - p0[1]) * k / 2,
      p2[0] - (p3[0] - p1[0]) * k / 2, p2[1] - (p3[1] - p1[1]) * k / 2, p2[0], p2[1]);
  }
  if (closed) ctx.closePath();
}
// Rubber-hose limb: ink tube with a colored core.
export function hose(ctx, pts, w, color, lw = LW) {
  const path = () => { ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]);
    if (pts.length === 2) ctx.lineTo(pts[1][0], pts[1][1]);
    else if (pts.length === 3) ctx.quadraticCurveTo(pts[1][0], pts[1][1], pts[2][0], pts[2][1]);
    else ctx.bezierCurveTo(pts[1][0], pts[1][1], pts[2][0], pts[2][1], pts[3][0], pts[3][1]); };
  ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  path(); ctx.strokeStyle = INK; ctx.lineWidth = w + lw * 2; ctx.stroke();
  path(); ctx.strokeStyle = color; ctx.lineWidth = w; ctx.stroke();
}
// Flat fill + one-tone cel shade: shade shows where the base shape, shifted by (dx,dy), doesn't cover.
export function cel(ctx, pathFn, base, shadeCol, dx = 10, dy = -10, lw = LW) {
  ctx.save(); pathFn(); ctx.fillStyle = shadeCol; ctx.fill(); ctx.clip();
  ctx.translate(dx, dy); pathFn(); ctx.fillStyle = base; ctx.fill(); ctx.restore();
  if (lw > 0) { pathFn(); paint(ctx, null, lw); }
}
export function clipTo(ctx, pathFn, drawFn) { ctx.save(); pathFn(); ctx.clip(); drawFn(); ctx.restore(); }
export function withT(ctx, x, y, s = 1, rot = 0, fn, sx = 1, sy = 1) {
  ctx.save(); ctx.translate(x, y); if (rot) ctx.rotate(rot); ctx.scale(s * sx, s * sy); fn(); ctx.restore();
}
// Squash & stretch about a pivot (volume preserving-ish).
export function squash(ctx, amt) { ctx.scale(1 + amt, 1 / (1 + amt)); }

export function text(ctx, str, x, y, { size = 80, font = 'Impact', fill = C.yellow, lw = 10, align = 'center', base = 'middle', rot = 0, stroke = INK, sx = 1 } = {}) {
  if (isKhmer(str)) font = 'Koulen';
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(sx, 1);
  ctx.font = `${size}px "${font}"`; ctx.textAlign = align; ctx.textBaseline = base;
  ctx.lineJoin = 'round';
  if (lw > 0) { ctx.lineWidth = lw; ctx.strokeStyle = stroke; ctx.strokeText(str, 0, 0); }
  ctx.fillStyle = fill; ctx.fillText(str, 0, 0); ctx.restore();
}
// two-bone IK; returns knee/elbow. bend = +1/-1 picks side.
export function ik(ax, ay, bx, by, l1, l2, bend = 1) {
  const dx = bx - ax, dy = by - ay; let d = Math.hypot(dx, dy);
  d = Math.min(d, l1 + l2 - 0.01);
  const a = Math.atan2(dy, dx);
  const cosA = clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1);
  const ang = a - bend * Math.acos(cosA);
  return [ax + Math.cos(ang) * l1, ay + Math.sin(ang) * l1];
}
