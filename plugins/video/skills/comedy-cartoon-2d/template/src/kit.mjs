// Shot machinery shared by every film: the shot registry, camera, shake, a title card,
// a head-on perspective street, radial speed lines, and the frame/cue entry points.
import { W, H, C, INK, TAU, paint, poly, text, lerp, seg, ease, hash, onTwos } from './core.mjs';
import { LINES, lineDur, meta } from './vox.mjs';
import * as bg from './bg.mjs';
import * as fx from './fx.mjs';

// ---------------------------------------------------------------- shot registry
// shot(start, end, draw(ctx, lt, t), cues) — lt is local time in the shot, t is film time.
// cues: [[lt, name, {opts}], ...] — sound effects, stings, dialogue ids and music sections (see references/audio.md).
export const SHOTS = [];
let SHIFT = 0;
export const shot = (a, b, draw, cues = []) => SHOTS.push({ a: a + SHIFT, b: b + SHIFT, draw, cues });
// Every shot defined after setShift(s) starts s seconds later than written. Use it when a beat has to grow
// (e.g. a dialogue line came out longer) without retyping every later time; then trim elsewhere.
export const setShift = s => { SHIFT = s; };
export const duration = () => {
  for (let i = 1; i < SHOTS.length; i++) if (Math.abs(SHOTS[i].a - SHOTS[i - 1].b) > 1e-6)
    console.warn(`WARNING shots don't tile: shot ${i - 1} ends ${SHOTS[i - 1].b.toFixed(2)}s, shot ${i} starts ${SHOTS[i].a.toFixed(2)}s`);
  return SHOTS[SHOTS.length - 1].b;
};
export function drawFrame(ctx, t) {
  const s = SHOTS.find(sh => t >= sh.a && t < sh.b) || SHOTS[SHOTS.length - 1];
  ctx.save(); s.draw(ctx, t - s.a, t); ctx.restore();
  fx.grain(ctx, t, 0.03);
}
export function allCues() {
  const out = [];
  for (const s of SHOTS) for (const [lt, name, opts] of s.cues) out.push({ t: s.a + lt, name, ...(opts || {}) });
  return out.sort((a, b) => a.t - b.t);
}

// ---------------------------------------------------------------- dialogue-driven timing + lip-sync
// take(len, draw, cues): append a shot at the running clock (story films: lengths come from the voices).
let CLOCK = 0;
export const take = (len, draw, cues = []) => { shot(CLOCK, CLOCK + len, draw, cues); CLOCK += len; };
export const clock = () => CLOCK;
// beats(['d1', 0.3, 'd2'], start): lines back to back with gaps (seconds). -> { cues, end, at: {id: start} }
export function beats(items, start = 0) {
  let t = start; const cues = [], at = {};
  for (const it of items) { if (typeof it === 'number') t += it; else { at[it] = t; cues.push([t, it]); t += lineDur(it); } }
  return { cues, end: t, at };
}
// talk(who, t): mouth openness 0..1 at film time t (from the clip's loudness; a flap before the clip exists)
let SPEECH = null;
export function talk(who, t) {
  if (!SPEECH) SPEECH = allCues().filter(c => LINES[c.name]).map(c => ({ t: c.t, id: c.name, who: LINES[c.name][0], d: lineDur(c.name) }));
  for (const s of SPEECH) {
    if (s.who !== who || t < s.t || t >= s.t + s.d) continue;
    const lt = onTwos(t - s.t), m = meta(s.id);
    if (m) return m.env[Math.min(m.env.length - 1, Math.floor(lt * 24))] || 0;
    return Math.max(0, Math.sin(lt * 26)) * 0.8;
  }
  return 0;
}
export const speaking = (who, t) => talk(who, t) > 0 || (SPEECH || []).some(s => s.who === who && t >= s.t && t < s.t + s.d);

// ---------------------------------------------------------------- camera
// cam(ctx, cx, cy, zoom, rot): world point (cx, cy) lands in the frame centre.
export const cam = (ctx, cx, cy, z = 1, rot = 0) => { ctx.translate(W / 2, H / 2); ctx.rotate(rot); ctx.scale(z, z); ctx.translate(-cx, -cy); };
// screen position of a world point under cam(cx, cy, z) (handy for iris targets)
export const toScreen = (x, y, cx, cy, z = 1) => [W / 2 + (x - cx) * z, H / 2 + (y - cy) * z];
// camera shake offsets, new every frame (on ones)
export const shk = (t, amp, seed = 1) => [(hash(Math.floor(t * 24) * 1.31 + seed) - 0.5) * 2 * amp, (hash(Math.floor(t * 24) * 2.71 + seed * 3) - 0.5) * 2 * amp];
export const P = (a, b, k) => [lerp(a[0], b[0], k), lerp(a[1], b[1], k)];
// point along a hop/jump arc of height h
export const arc = (a, b, k, h) => [lerp(a[0], b[0], k), lerp(a[1], b[1], k) - Math.sin(k * Math.PI) * h];

// ---------------------------------------------------------------- title card (ribbon banner that pops in and out)
export function titleCard(ctx, lt, words, { inAt = 0.25, outAt = 2.45, x = 960, y = 250, size = 168, ribbon = C.red, ribbonD = C.redD, fill = C.yellow } = {}) {
  const inK = seg(lt, inAt, inAt + 0.5), outK = seg(lt, outAt, outAt + 0.25);
  if (inK <= 0 || outK >= 1) return;
  const s = ease.back(inK) * (1 - ease.in(outK));
  ctx.save(); ctx.translate(x, y); ctx.rotate(-0.05 + Math.sin(lt * 3) * 0.01); ctx.scale(s, s);
  ctx.font = `${size}px "Impact"`; const hw = Math.max(300, ctx.measureText(words).width / 2 + 70);
  poly(ctx, [[-hw, -70], [hw, -90], [hw - 20, 90], [-hw + 20, 100]]); paint(ctx, ribbon, 10);
  poly(ctx, [[-hw - 50, -30], [-hw, -70], [-hw + 20, 100], [-hw - 40, 70]]); paint(ctx, ribbonD, 8);
  poly(ctx, [[hw + 50, -50], [hw, -90], [hw - 20, 90], [hw + 44, 52]]); paint(ctx, ribbonD, 8);
  text(ctx, words, 8, 14, { size, fill: INK, lw: 18 });
  text(ctx, words, 0, 4, { size, fill, lw: 16 });
  ctx.restore();
}

// ---------------------------------------------------------------- head-on perspective street (low-angle chase shots)
// spd = world units/sec toward camera (0 = parked). extra(pr) draws things in the street; pr(X, Y, Z) projects.
export function perspStreet(ctx, t, { vpy = 690, vpx = 960, spd = 30, h = 1.0, z0 = 0, extra = null, cop = null, palette = [C.teal, C.orange, C.mustard, C.brick, C.plum, C.tealD, C.orangeL] } = {}) {
  const f = 950;
  bg.sky(ctx, { horizon: vpy + 30, sun: false, cloudX: t * 40 });
  const pr = (X, Y, Z) => [vpx + X * f / Z, vpy + (h - Y) * f / Z];
  const dist = t * spd + z0;
  const blds = [];
  for (let i = 0; i < 26; i++) { const L = 14, zi = ((i * L - dist) % (26 * L) + 26 * L) % (26 * L) + 1.2; blds.push({ z1: zi, z2: zi + L * 0.92, i }); }
  blds.sort((a, b) => b.z1 - a.z1);
  for (const b of blds) for (const side of [-1, 1]) {
    const X = side * 11, Hb = 14 + hash(b.i * 7 + side) * 26;
    poly(ctx, [pr(X, 0, b.z1), pr(X, Hb, b.z1), pr(X, Hb, b.z2), pr(X, 0, b.z2)]); paint(ctx, palette[(b.i * 3 + (side > 0 ? 2 : 0)) % palette.length], Math.max(1.5, 60 / b.z1));
    ctx.fillStyle = 'rgba(255,240,190,0.55)';
    for (let v = 0.15; v < 0.9; v += 0.2) for (const u of [0.15, 0.55]) {
      const zA = lerp(b.z1, b.z2, u), zB = lerp(b.z1, b.z2, u + 0.25);
      poly(ctx, [pr(X, Hb * v, zA), pr(X, Hb * (v + 0.1), zA), pr(X, Hb * (v + 0.1), zB), pr(X, Hb * v, zB)]); ctx.fill();
    }
  }
  const zn = 0.6, zf = 400;
  poly(ctx, [pr(-11, 0, zn), pr(-11, 0, zf), pr(11, 0, zf), pr(11, 0, zn)]); ctx.fillStyle = C.walk; ctx.fill();
  poly(ctx, [pr(-7, 0, zn), pr(-7, 0, zf), pr(7, 0, zf), pr(7, 0, zn)]); ctx.fillStyle = C.road; ctx.fill();
  for (const sd of [-7, 7]) { ctx.beginPath(); ctx.moveTo(...pr(sd, 0, zn)); ctx.lineTo(...pr(sd, 0, zf)); paint(ctx, null, 5); }
  ctx.fillStyle = C.lane;
  for (let k = 0; k < 40; k++) { const z = ((k * 6 - dist) % 240 + 240) % 240 + 0.8; poly(ctx, [pr(-0.25, 0, z), pr(-0.25, 0, z + 3), pr(0.25, 0, z + 3), pr(0.25, 0, z)]); ctx.fill(); }
  (extra || cop)?.(pr);
}
// speed lines bursting out from a point (low-angle / big-moment shots)
export function radialLines(ctx, t, cx, cy, { n = 26, spd = 1.8, col = 'rgba(255,255,255,0.75)', inner = 260 } = {}) {
  ctx.save(); ctx.strokeStyle = col; ctx.lineCap = 'round';
  for (let i = 0; i < n; i++) {
    const a = hash(i * 3.3) * TAU, k = (t * spd + hash(i * 1.7)) % 1, r = inner + k * 1300, l = 80 + k * 260;
    ctx.lineWidth = 3 + k * 8;
    ctx.beginPath(); ctx.moveTo(cx + Math.cos(a) * r, cy + Math.sin(a) * r); ctx.lineTo(cx + Math.cos(a) * (r + l), cy + Math.sin(a) * (r + l)); ctx.stroke();
  }
  ctx.restore();
}
