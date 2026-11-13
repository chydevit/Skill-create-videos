// "Bong Smei, Bong Nimith & Devit" — 8 scenes. Shot lengths come from the real dialogue clips
// (beats()/lineDur), so the film re-times itself when voices change.
import { W, H, INK, TAU, paint, circle, oval, rrect, poly, text, clamp, lerp, seg, ease, onTwos, hash, wobble } from './core.mjs';
import { take, clock, beats, talk, cam, toScreen, shk, duration } from './kit.mjs';
import { lineDur } from './vox.mjs';
import { person, chair, chairBack, CAST, notebook, icedCoffee, anchors, toLocal as localOf } from './people.mjs';
import './cast.mjs';
import { drop } from './chars.mjs';
import * as st from './sets.mjs';
import * as fx from './fx.mjs';

const D = lineDur;
// person with lip-sync from the voice track
const pp = (ctx, who, t, o = {}) => person(ctx, who, { t, mouth: typeof who === 'string' ? talk(who, t) : 0, ...o });
const warmLight = (ctx, a = 0.18) => { ctx.save(); const g = ctx.createLinearGradient(0, 0, W, H); g.addColorStop(0, `rgba(255,214,150,${a})`); g.addColorStop(1, 'rgba(255,214,150,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); ctx.restore(); };
const bubble = (ctx, x, y, words, k, { col = '#ffffff', size = 56, tail = -1 } = {}) => {
  if (k <= 0) return;
  const s = ease.back(clamp(k * 3)) * (k > 0.85 ? 1 - (k - 0.85) / 0.15 : 1);
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.font = `${size}px "Koulen"`; const w = ctx.measureText(words).width / 2 + 40;
  rrect(ctx, -w, -size * 0.9, w * 2, size * 1.8, size * 0.8); paint(ctx, col, 5);
  poly(ctx, [[tail * 20, size * 0.85], [tail * 60, size * 1.6], [tail * 50, size * 0.85]]); paint(ctx, col, 0);
  ctx.beginPath(); ctx.moveTo(tail * 20, size * 0.9); ctx.lineTo(tail * 60, size * 1.6); ctx.lineTo(tail * 50, size * 0.9); paint(ctx, null, 5);
  text(ctx, words, 0, 4, { size, fill: '#ff8c6b', lw: 0 });
  ctx.restore();
};
function titleKh(ctx, lt, inAt, outAt, kh, en, y = 300) {
  const k = ease.back(seg(lt, inAt, inAt + 0.6)) * (1 - ease.in(seg(lt, outAt, outAt + 0.4)));
  if (k <= 0) return;
  ctx.save(); ctx.translate(960, y); ctx.scale(k, k);
  rrect(ctx, -600, -130, 1200, 250, 70); paint(ctx, 'rgba(255,248,240,0.94)', 6);
  text(ctx, kh, 0, -30, { size: 100, fill: '#ff8c6b', lw: 0 });
  text(ctx, en, 0, 66, { size: 40, font: 'Arial Black', fill: '#6a5a7a', lw: 0 });
  ctx.restore();
}
const scene = (lens) => lens.reduce((a, b) => a + b, 0);
// Getaway Car-style cartoon helpers
const ghosts = (ctx, n, fn) => { for (let i = n; i >= 1; i--) { ctx.save(); ctx.globalAlpha = 0.16; fn(i); ctx.restore(); } };
const sweat = (ctx, x, y, s, t, n = 3) => { for (let i = 0; i < n; i++) { const k = (t * 1.8 + i / n) % 1, side = i % 2 ? 1 : -1; ctx.save(); ctx.globalAlpha = 1 - k; drop(ctx, x + side * (40 + k * 90) * s, y - Math.sin(k * Math.PI) * 60 * s + k * 40 * s, s * 1.3, side * 0.5); ctx.restore(); } };
const star = (ctx, x, y, k, s = 1) => { if (k <= 0 || k >= 1) return; const sc = Math.sin(k * Math.PI) * s; ctx.save(); ctx.translate(x, y); ctx.rotate(k * 3); ctx.scale(sc, sc); ctx.beginPath(); for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4, r = i % 2 ? 9 : 26; ctx.lineTo(Math.cos(a) * r, Math.sin(a) * r); } ctx.closePath(); paint(ctx, '#fff6c0', 4); ctx.restore(); };

// ============================================================ SCENE 1 — Introduction
{
  const b = beats([4.6, 'n1']), len = b.end + 2.4;
  take(len, (ctx, lt, t) => {
    const k = ease.inOut(seg(lt, 2.4, len));
    const w0 = st.TEAM_WIN, tx = w0.x + w0.w / 2, ty = w0.y + w0.h / 2;
    const z = Math.exp(lerp(0, Math.log(6.4), k * k));
    ctx.save(); cam(ctx, lerp(960, tx, Math.min(1, k * 1.2)), lerp(540, ty, Math.min(1, k * 1.2)), z);
    st.sunsetSky(ctx, { t }); st.skyline(ctx, t); st.officeTower(ctx, t);
    ctx.restore();
    titleKh(ctx, lt, 0.5, 3.9, 'បងស្មី បងនិមិត្ត និង ដេវីត', 'Bong Smei, Bong Nimith & Devit');
    fx.wash(ctx, '#fff6ea', seg(lt, len - 0.35, len) * 0.8);
  }, [[0, 'music', { id: 'w1', style: 'warm', gain: 0.85 }], [0, 'city_amb', { dur: len }], [0.55, 'sparkle'], ...b.cues, [len - 1.4, 'whoosh', { f0: 250, f1: 1400, dur: 1.4, gain: 0.3 }]]);
}

// ============================================================ SCENE 2 — Meet Devit
{
  const SP = 1.9; // typing, then the swivel
  const b = beats([SP + 1.2, 'd1', 0.3, 'd2']), len = b.end + 1.5;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 930, 650, 1.5);
    st.office(ctx, t, {});
    const spin = seg(lt, SP, SP + 0.5);
    let facing = 0.7, back = false, pose = 'type', expr = 'grin', look = [1, 0];
    if (spin > 0) { pose = 'sitTalk'; look = [0, 0]; }
    if (spin > 0 && spin < 1) { back = spin > 0.2 && spin < 0.65; facing = spin < 0.2 ? 0.7 : -0.6 + spin * 0.6; }
    if (spin >= 1) facing = 0.12;
    if (lt > SP + 0.5 && lt < b.at.d1 + D('d1') * 0.8) pose = 'thumbs';
    const bounce = spin >= 1 ? wobble(lt - SP - 0.5, 3, 6) * 0.06 : 0;
    chairBack(ctx, 760, 1110, 1.45, '#8fa6c9');
    if (spin > 0.05 && spin < 0.95) ghosts(ctx, 3, i => pp(ctx, 'devit', t, { x: 760 - i * 26 * Math.sin(spin * 9), y: 1080, s: 1.5, facing: -facing, back: !back, pose: 'sitTalk', sit: true, expr }));
    pp(ctx, 'devit', t, { x: 760, y: 1080, s: 1.5, facing, back, pose, sit: true, expr, look, sq: bounce + (spin > 0 && spin < 1 ? -0.12 * Math.sin(spin * Math.PI) : 0) });
    if (pose === 'thumbs') star(ctx, 760 + 1.5 * 70, 1080 - 1.5 * 250, seg(lt, SP + 0.5, SP + 1.1), 1.4);
    if (spin > 0.05 && spin < 0.9) { ctx.save(); ctx.strokeStyle = 'rgba(255,255,255,0.85)'; ctx.lineWidth = 8; ctx.lineCap = 'round'; for (const r of [230, 270]) { ctx.beginPath(); ctx.ellipse(760, 760, r, r * 0.35, 0, Math.PI * (0.1 + spin), Math.PI * (0.8 + spin)); ctx.stroke(); } ctx.restore(); }
    st.desk(ctx, 980, 1010, 1600, { monitorX: 330, t, codeSpeed: 3 });
    icedCoffee(ctx, 520, 975, 1.1);
    if (lt < SP + 0.2) st.flyingCode(ctx, 1290, 760, t, 16, 1);
    fx.sfxText(ctx, 'TAP TAP TAP!', 1120, 470, seg(lt, 0.2, SP), { size: 64, fill: '#ffd23f', rot: -0.1, wob: 4 });
    fx.sfxText(ctx, 'WHOOSH!', 600, 420, seg(lt, SP, SP + 0.8), { size: 80, fill: '#7fd3c8', rot: 0.12 });
    ctx.restore();
    warmLight(ctx, 0.12);
  }, [[0, 'music_end', { id: 'w1', how: 'fade', dur: 0.6 }], [0, 'music', { id: 'u1', style: 'upbeat', gain: 0.6 }], [0, 'room_tone', { dur: len }], [0, 'typing', { dur: SP, rate: 16 }], [SP, 'swivel'], [SP, 'zip_up'], [SP + 0.5, 'boing', { pitch: 1.4 }], [SP + 0.55, 'sparkle'], ...b.cues, [b.end + 0.4, 'blink']]);
}

// ============================================================ SCENE 3 — Meet Bong Nimith
const NIM = { x: 1330, y: 1060, s: 1.35 };
const toLocal = (wx, wy, o) => [(wx - o.x) / o.s, (wy - o.y) / o.s];
function bgDevit(ctx, t, { wave = 0, look = [1, 0] } = {}) {
  chairBack(ctx, 640, 905, 0.8, '#8fa6c9');
  pp(ctx, 'devit', t, { x: 640, y: 905, s: 0.8, facing: wave ? 0.6 : 0.8, pose: wave ? 'wave' : 'type', sit: true, expr: 'grin', look });
  ctx.save(); ctx.translate(700, 860); ctx.scale(0.5, 0.5); st.desk(ctx, 0, 0, 700, { monitorX: 160, t, mug: false }); ctx.restore();
}
{
  const DRAW = 2.6, b = beats([3.7, 'm1', 0.3, 'm2']), len = b.end + 1.0;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 1180, 560, 1.38);
    st.office(ctx, t, { board: seg(lt, 0.2, DRAW) });
    bgDevit(ctx, t, { wave: lt > 3.2 && lt < 5.0 ? 1 : 0 });
    const turned = lt > DRAW + 0.15;
    if (!turned) {
      const a = lt * 5, [hx, hy] = toLocal(1400 + Math.cos(a) * 90, 330 + Math.sin(a * 1.3) * 60, NIM);
      pp(ctx, 'nimith', t, { ...NIM, back: true, pose: 'reach', reach: [hx, hy], hold: [null, 'marker'] });
      fx.sfxText(ctx, 'SQUEAK!', 1560, 220, seg(lt, 0.5, 2.3), { size: 52, fill: '#7fd3c8', rot: 0.1, wob: 4 });
    } else {
      const tk = seg(lt, DRAW + 0.15, DRAW + 0.45);
      if (tk > 0 && tk < 1) ghosts(ctx, 3, i => pp(ctx, 'nimith', t, { ...NIM, x: NIM.x - i * 30, back: true, pose: 'stand' }));
      const pose = lt < 3.6 ? 'glasses' : 'hold';
      pp(ctx, 'nimith', t, { ...NIM, facing: 0.25, pose, hold: [null, 'marker'], expr: lt < 3.6 ? 'calm' : 'smile', sq: wobble(lt - DRAW - 0.15, 3, 7) * 0.05 });
      const hd = anchors('nimith', { ...NIM, facing: 0.25, pose: 'glasses' }).head;
      star(ctx, hd[0] + 50, hd[1] - 6, seg(lt, 3.0, 3.6), 1.7);
      fx.sfxText(ctx, 'TING!', hd[0] + 170, hd[1] - 90, seg(lt, 3.0, 3.9), { size: 56, fill: '#fff6c0', rot: 0.1 });
    }
    ctx.restore();
    warmLight(ctx, 0.1);
  }, [[0, 'music_end', { id: 'u1', how: 'fade', dur: 0.5 }], [0, 'music', { id: 'w2', style: 'warm', gain: 0.6, melody: false }], [0, 'room_tone', { dur: len }], [0.2, 'marker', { dur: DRAW - 0.3 }], [DRAW + 0.15, 'whoosh', { f0: 600, f1: 2000, dur: 0.25, gain: 0.35 }], [DRAW + 0.15, 'zip_up'], [3.05, 'sparkle'], [3.05, 'register_ding'], ...b.cues]);
}
{
  const b = beats([0.6, 'n2']), len = b.end + 1.3, sayAt = b.at.n2 + D('n2') * 0.55;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 1000, 600, 1.12);
    st.office(ctx, t, { board: 1 });
    bgDevit(ctx, t, { wave: 1 });
    pp(ctx, 'nimith', t, { ...NIM, facing: -0.55, pose: 'hold', hold: [null, 'marker'], expr: lt > sayAt ? 'grin' : 'smile', look: [-1, 0] });
    bubble(ctx, 640, 360, 'បងនិមិត្ត!', seg(lt, sayAt - 0.2, len), { tail: -1 });
    ctx.restore();
    warmLight(ctx, 0.1);
  }, [[0, 'room_tone', { dur: len }], ...b.cues, [sayAt - 0.15, 'sparkle']]);
}

// ============================================================ SCENE 4 — Meet Bong Smei
const SMEI_IN = 3.8;
{
  take(SMEI_IN, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 1000, 600, 1.08);
    st.office(ctx, t, { board: 1, light: 'gold', doorOpen: ease.out(seg(lt, 0, 0.6)) });
    bgDevit(ctx, t, { look: lt > 1.4 ? [1, 0] : [0.5, 0] });
    const wk = seg(lt, 0.5, 3.2), x = lerp(1830, 1520, ease.out(wk));
    const nodD = lt > 2.3 && lt < 2.8 ? Math.sin(seg(lt, 2.3, 2.8) * Math.PI) : 0, nodN = lt > 3.0 && lt < 3.5 ? Math.sin(seg(lt, 3.0, 3.5) * Math.PI) : 0;
    pp(ctx, 'nimith', t, { ...NIM, x: 1240, facing: 0.6, pose: 'hold', hold: [null, 'marker'], expr: 'smile', nod: nodN * 0.6 });
    fx.sfxText(ctx, 'CREAK...', 1700, 300, seg(lt, 0, 1.2), { size: 50, fill: '#e6b52e', rot: -0.08 });
    pp(ctx, 'smei', t, { x, y: 1040, s: 1.3, facing: lt < 2.6 ? -0.5 : -0.2, pose: wk < 1 ? 'walk' : 'stand', ph: lt * 1.5, hold: [null, 'tea'], expr: 'smile', nod: nodD + nodN });
    ctx.restore();
    warmLight(ctx, 0.28);
  }, [[0, 'room_tone', { dur: SMEI_IN }], [0.05, 'creak'], [0.6, 'footsteps', { n: 5, gap: 0.5 }]]);
}
{
  const b = beats([0.6, 's1', 0.35, 's2']), len = b.end + 1.7;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 1150, 580, 1.75);
    st.office(ctx, t, { board: 1, light: 'gold' });
    const sip = lt > b.end + 0.3 && lt < b.end + 1.3;
    pp(ctx, 'smei', t, { x: 1150, y: 975, s: 1.4, facing: 0.15, pose: sip ? 'sip' : 'hold', hold: [null, 'tea'], expr: sip ? 'proud' : 'smile' });
    fx.sfxText(ctx, 'SLURP!', 1340, 360, seg(lt, b.end + 0.45, b.end + 1.4), { size: 52, fill: '#ffd23f', rot: 0.1, wob: 3 });
    ctx.restore();
    warmLight(ctx, 0.3);
    // golden light beams
    ctx.save(); ctx.globalAlpha = 0.12; ctx.fillStyle = '#fff1c4'; for (let i = 0; i < 3; i++) { poly(ctx, [[-100 + i * 260, -50], [80 + i * 260, -50], [700 + i * 300, H + 50], [400 + i * 300, H + 50]]); ctx.fill(); } ctx.restore();
  }, [[0, 'room_tone', { dur: len }], ...b.cues, [b.end + 0.45, 'sip']]);
}

// ============================================================ SCENE 5 — The Big Project
const MEET = { smei: { x: 1180, y: 1040, s: 1.2 }, devit: { x: 1470, y: 1050, s: 1.2 }, nimith: { x: 1760, y: 1120, s: 1.12 } };
function meeting(ctx, t, { devit = {}, nimith = {}, smei = {} } = {}) {
  st.meetingRoom(ctx, t);
  pp(ctx, 'smei', t, { ...MEET.smei, facing: -0.35, pose: 'presentL', hold: [null, 'tea'], expr: 'smile', ...smei });
  chairBack(ctx, MEET.devit.x, MEET.devit.y, 1.0, '#ffb38a');
  chairBack(ctx, MEET.nimith.x, MEET.nimith.y, 1.0, '#a8cdee');
  pp(ctx, 'devit', t, { ...MEET.devit, facing: -0.4, pose: 'sitTalk', sit: true, expr: 'grin', ...devit });
  pp(ctx, 'nimith', t, { ...MEET.nimith, facing: -0.45, pose: 'sitTalk', sit: true, expr: 'calm', ...nimith });
  st.meetingTable(ctx, 1500, 960, 760);
}
{
  const b = beats([0.7, 's3', 0.3, 's4']), len = b.end + 0.9;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 1080, 600, 1.2);
    meeting(ctx, t, { devit: { look: [-1, 0] }, nimith: { look: [-1, 0] } });
    ctx.restore();
  }, [[0, 'music_end', { id: 'w2', how: 'fade', dur: 0.6 }], [0, 'music', { id: 'w3', style: 'warm', gain: 0.45, melody: false, bpm: 92 }], [0, 'room_tone', { dur: len }], ...b.cues]);
}
{
  const b = beats([0.45, 'd3']), len = b.end + 0.7;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 1470, 640, 1.75);
    const wind = seg(lt, 0, 0.22), up = seg(lt, 0.22, 0.5);
    const hop = up > 0 ? ease.out(up) * 150 + Math.sin(lt * 9) * 6 * (up >= 1 ? 1 : 0) : 0;
    meeting(ctx, t, { devit: up > 0 ? { pose: 'jump', sit: false, hop, y: MEET.devit.y + 40, facing: 0.1, expr: 'laugh', sq: up < 1 ? -0.22 * Math.sin(up * Math.PI) : wobble(lt - 0.5, 3, 6) * 0.1 } : { sq: 0.28 * ease.in(wind) }, nimith: { look: [-1, -0.5] } });
    if (up > 0 && up < 1) { ctx.save(); ctx.strokeStyle = 'rgba(255,255,255,0.9)'; ctx.lineWidth = 8; ctx.lineCap = 'round'; for (const dx of [-90, -30, 40, 100]) { ctx.beginPath(); ctx.moveTo(1470 + dx, 900); ctx.lineTo(1470 + dx, 1040); ctx.stroke(); } ctx.restore(); }
    fx.sfxText(ctx, 'BOING!', 1720, 480, seg(lt, 0.25, 1.1), { size: 90, fill: '#ffd23f', rot: 0.1 });
    if (up > 0) fx.dust(ctx, 1470, 860, seg(lt, 0.25, 0.9), { n: 5, spread: 120, r: 24, col: '#ffffff', seed: 4 });
    ctx.restore();
  }, [[0, 'room_tone', { dur: len }], [0.22, 'boing', { pitch: 1.2 }], [0.25, 'sting_idea'], ...b.cues]);
}
{
  const b = beats([0.55, 'm3', 0.3, 'm4']), len = b.end + 0.8;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 1700, 640, 1.75);
    const raised = lt > 0.2 && lt < b.at.m4 + 0.4;
    meeting(ctx, t, { nimith: { pose: raised ? 'raise' : 'sitTalk', facing: -0.2, expr: lt > b.at.m4 ? 'thinking' : 'calm' }, devit: { look: [1, 0], expr: lt > b.at.m4 + 1.0 ? 'worried' : 'smile' } });
    if (raised) { const h = anchors('nimith', { ...MEET.nimith, facing: -0.2, pose: 'raise', sit: true }).handR; fx.sfxText(ctx, '!', h[0] + 60, h[1] - 50, seg(lt, 0.25, 1.4), { size: 120, fill: '#ff5c8a', rot: 0.15 }); }
    ctx.restore();
  }, [[0, 'room_tone', { dur: len }], [0.2, 'whoosh', { f0: 800, f1: 2200, dur: 0.2, gain: 0.25 }], ...b.cues]);
}
{
  const b = beats([0.4, 's5']), len = b.end + 1.4;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 1400, 600, 1.8);
    const nod = lt > b.end && lt < b.end + 0.6 ? Math.sin(seg(lt, b.end, b.end + 0.6) * Math.PI) : 0;
    meeting(ctx, t, { smei: { pose: 'hold', facing: 0.25, expr: lt > b.end ? 'proud' : 'smile', nod } });
    ctx.restore();
    warmLight(ctx, 0.15);
  }, [[0, 'room_tone', { dur: len }], ...b.cues, [b.end + 0.1, 'sting_tiny']]);
}

// ============================================================ SCENE 6 — Launch Day Crash
{
  const b = beats([0.9, 'n3']), len = b.end + 0.6;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 1100, 650, 1.3);
    st.office(ctx, t, { board: 1 });
    st.banner(ctx, 1110, 250, 1000, 'LAUNCH DAY!');
    pp(ctx, 'smei', t, { x: 1480, y: 1050, s: 1.2, facing: -0.3, pose: 'hold', hold: [null, 'tea'], expr: 'proud' });
    pp(ctx, 'devit', t, { x: 740, y: 1080, s: 1.25, facing: 0.3, pose: 'cheer', expr: 'laugh', hop: 0, y: 1080 - Math.abs(Math.sin(lt * 7)) * 20 });
    pp(ctx, 'nimith', t, { x: 1110, y: 1070, s: 1.2, facing: -0.1, pose: 'clap', expr: 'grin' });
    ctx.restore();
    st.confetti(ctx, t, { n: 110, area: [0, -200, W, H + 200] });
    fx.impact(ctx, 420, 300, 110, seg(lt, 0.12, 0.8), { word: 'POP!', size: 70, col: '#ffd23f', wcol: '#ff5c8a' });
    fx.sfxText(ctx, 'YAY!', 1500, 320, seg(lt, 0.5, 1.8), { size: 100, fill: '#7fd3c8', rot: 0.12, wob: 3 });
  }, [[0, 'music_end', { id: 'w3', how: 'fade', dur: 0.4 }], [0, 'music', { id: 'tr1', style: 'triumph', gain: 0.6 }], [0.15, 'party_pop'], [0.45, 'party_horn'], ...b.cues]);
}
let ERR_AT = 0;
{
  const b = beats([0.3, 'n4']), len = b.end + 0.9, err = b.at.n4 + D('n4') * 0.66;
  const pings = []; for (let tt = 0.15, g = 0.42; tt < err - 0.05; tt += g, g = Math.max(0.07, g * 0.8)) pings.push([tt, 'ping', { n: 1, gain: 0.8 }]);
  take(len, (ctx, lt, t) => {
    const e = seg(lt, err, err + 0.12);
    ctx.fillStyle = e > 0 ? '#3b2a3a' : '#ffe2d4'; ctx.fillRect(0, 0, W, H);
    if (e <= 0) st.confetti(ctx, t, { n: 50 });
    const [sx, sy] = shk(t, e > 0 && lt < err + 0.5 ? 12 : 0);
    const orders = 1 + Math.pow(lt / Math.max(0.1, err), 1.7) * 22;
    st.phoneScreen(ctx, 960 + sx, 560 + sy, 1.08, t, { orders, error: e });
    for (const [pt] of pings) { const k = seg(lt, pt, pt + 0.5); if (k > 0 && k < 1) { const h = hash(pt * 13); fx.sfxText(ctx, 'DING!', h > 0.5 ? 1400 + h * 300 : 300 + h * 300, 200 + hash(pt * 7) * 600, k, { size: 50, fill: '#ffd23f', rot: (h - 0.5) * 0.5 }); } }
    if (e > 0) { st.redWash(ctx, t, 1); fx.impact(ctx, 1450, 330, 170, seg(lt, err, err + 1.0), { word: 'CRASH!', size: 80, col: '#ffd23f', wcol: '#e8433a' }); }
  }, [...pings, ...b.cues, [err, 'music_end', { id: 'tr1', how: 'tapestop', dur: 0.8 }], [err, 'error_buzz'], [err + 0.1, 'alarm_beep', { n: 4 }]]);
}
{
  const len = 1.6;
  take(len, (ctx, lt, t) => {
    const [sx, sy] = shk(t, lt < 0.6 ? 22 * (1 - lt / 0.6) + 5 : 5);
    ctx.save(); ctx.translate(sx, sy);
    ctx.fillStyle = '#3b3550'; ctx.fillRect(0, 0, W, H);
    st.serverRack(ctx, 620, 1020, 1.5, t, { smoke: 1, n: 3 });
    fx.dust(ctx, 860, 300, seg(lt, 0.05, 1.3), { n: 9, spread: 380, r: 90, col: '#5a5068', rise: 120, seed: 31 });
    fx.impact(ctx, 1420, 330, 220, seg(lt, 0.05, 1.3), { word: 'KABOOM!', size: 96, col: '#ffd23f', wcol: '#e8433a' });
    ctx.restore();
    st.redWash(ctx, t, 1);
  }, [[0, 'music', { id: 'tn', style: 'tension', gain: 0.8 }], [0.05, 'crash'], [0, 'steam_hiss'], [0.2, 'server_hum', { dur: 1.4 }], [0.5, 'alarm_beep', { n: 3 }]]);
}
{
  const b = beats([0.3, 'd4', 0.25, 'd5']), len = b.end + 0.5;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 960, 560, 1.9);
    st.office(ctx, t, { board: 1 });
    pp(ctx, 'devit', t, { x: 960 + Math.sin(t * 60) * 4, y: 980, s: 1.55, facing: 0.05, pose: 'panic', expr: 'panic', sq: Math.sin(t * 30) * 0.02 });
    sweat(ctx, 960, 980 - 1.55 * 260, 1.4, t, 4);
    fx.stressMarks(ctx, 1220, 440, 2.2, t); fx.stressMarks(ctx, 700, 470, 1.8, t + 0.3);
    ctx.restore();
    st.redWash(ctx, t, 1);
  }, [...b.cues, [0.35, 'heartbeat', { n: 2 }]]);
}
{
  const b = beats([0.9, 's6', 0.45, 's7']), len = b.end + 1.0;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 1080, 580, 1.45);
    st.office(ctx, t, { board: 1 });
    const DV = { x: 900, y: 1010, s: 1.4 }, SM = { x: 1140, y: 1060, s: 1.35 };
    const reach = ease.inOut(seg(lt, 0.2, 0.8));
    const calm = seg(lt, b.at.s6, b.at.s7 + 0.5);
    const dvo = { ...DV, facing: 0.35, pose: calm < 0.6 ? 'panic' : 'stand' };
    // Devit's right shoulder (world) -> Smei's local space, so the hand lands on it whatever the body shapes
    const tgt = localOf('smei', { ...SM, pose: 'reachL' }, anchors('devit', dvo).shR);
    pp(ctx, 'devit', t, { ...dvo, expr: calm < 0.4 ? 'panic' : calm < 1 ? 'worried' : 'smile', look: [1, -0.3] });
    if (calm < 0.5) sweat(ctx, DV.x, DV.y - DV.s * 250, 1.2, t, 3);
    pp(ctx, 'smei', t, { ...SM, facing: -0.45, pose: 'reachL', reach: [lerp(-60, tgt[0], reach), lerp(-150, tgt[1], reach)], hold: [null, 'tea'], expr: 'calm' });
    if (calm >= 1) star(ctx, 1290, 520, seg(lt, b.at.s7 + 0.5, b.at.s7 + 1.4), 1.3);
    ctx.restore();
    st.redWash(ctx, t, 1 - calm);
    warmLight(ctx, 0.2 * calm);
  }, [...b.cues, [0, 'music_end', { id: 'tn', how: 'fade', dur: 0.1 }], [0.2, 'music', { id: 'tn2', style: 'tension', gain: 0.5 }], [0.9, 'music_end', { id: 'tn2', how: 'fade', dur: 1.2 }], [b.at.s7 + 0.4, 'sting_tiny']]);
}

// ============================================================ SCENE 7 — Teamwork
const plan = ctx => { ctx.save(); ctx.translate(30, -6); st.archDiagram(ctx, 0, 0, 0.22, 1, '#e07a5f'); ctx.restore(); text(ctx, 'Plan B', -30, -26, { size: 16, font: 'Arial Black', fill: '#4f86c6', lw: 0 }); };
{
  const b = beats([0.9, 'm5']), len = b.end + 0.6;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 1000, 560, 2.0);
    st.office(ctx, t, { board: 1 });
    const N = { x: 1000, y: 1080, s: 1.3 };
    pp(ctx, 'nimith', t, { ...N, facing: 0.05, pose: 'notebook', expr: 'calm', look: [0, 0.4] });
    const an = anchors('nimith', { ...N, facing: 0.05, pose: 'notebook' });
    notebook(ctx, (an.handL[0] + an.handR[0]) / 2, (an.handL[1] + an.handR[1]) / 2 + 20, 2.3, ease.out(seg(lt, 0.25, 0.7)), plan);
    star(ctx, N.x - 260, N.y - 560, seg(lt, 0.6, 1.3), 1.5); star(ctx, N.x + 250, N.y - 600, seg(lt, 0.75, 1.45), 1.2);
    fx.sfxText(ctx, 'TA-DA!', N.x + 330, N.y - 680, seg(lt, 0.6, 1.8), { size: 70, fill: '#ffd23f', rot: 0.1 });
    ctx.restore();
    warmLight(ctx, 0.12);
  }, [[0, 'music', { id: 'bd', style: 'build', gain: 0.55 }], [0, 'room_tone', { dur: len }], [0.3, 'page_flip'], [0.6, 'ta_da_small'], ...b.cues]);
}
{
  const b = beats([0.4, 'm6', 0.3, 'd6']), len = b.end + 1.1;
  take(len, (ctx, lt, t) => {
    const LB = b.at.m6 + 0.6;
    // left panel: Nimith scales the system
    ctx.save(); poly(ctx, [[0, 0], [W / 2 + 70, 0], [W / 2 - 70, H], [0, H]]); ctx.clip();
    ctx.fillStyle = '#f8e6d6'; ctx.fillRect(0, 0, W, H);
    st.dashboard(ctx, 70, 120, 860, 620, t, { servers: 1 + 4 * ease.inOut(seg(lt, LB, len - 0.4)), lb: seg(lt, LB - 0.3, LB + 0.2), bars: seg(lt, LB, len) });
    pp(ctx, 'nimith', t, { x: 300, y: 1480, s: 1.45, facing: 0.5, pose: 'reach', reach: [150, -520], expr: 'calm' });
    fx.sfxText(ctx, 'BEEP BOOP!', 520, 820, seg(lt, LB, LB + 1.2), { size: 54, fill: '#c3a8ff', rot: -0.08 });
    ctx.restore();
    // right panel: Devit makes the code faster
    ctx.save(); poly(ctx, [[W / 2 + 70, 0], [W, 0], [W, H], [W / 2 - 70, H]]); ctx.clip();
    ctx.fillStyle = '#2c3247'; ctx.fillRect(0, 0, W, H);
    ctx.save(); ctx.translate(1060, 90); ctx.scale(2.2, 2.2); st.codeLines(ctx, 0, 0, t * 5, 20); ctx.restore();
    ctx.fillStyle = 'rgba(44,50,71,0.45)'; ctx.fillRect(960, 0, 960, H);
    pp(ctx, 'devit', t, { x: 1480, y: 1110, s: 1.8, facing: 0.15, pose: 'type', sit: true, expr: 'determined' });
    fx.speedStreaks(ctx, 1500, 700, 380, 500, t, { n: 7, dir: -1, alpha: 0.5 });
    fx.sfxText(ctx, 'CLICK CLACK!', 1560, 170, 0.5, { size: 60, fill: '#8fe3c4', rot: -0.06 + Math.sin(t * 20) * 0.02 });
    ctx.restore();
    ctx.beginPath(); ctx.moveTo(W / 2 + 70, 0); ctx.lineTo(W / 2 - 70, H); paint(ctx, null, 14, '#fff6ea'); ctx.beginPath(); ctx.moveTo(W / 2 + 70, 0); ctx.lineTo(W / 2 - 70, H); paint(ctx, null, 5);
  }, [[0, 'whoosh', { f0: 400, f1: 2500, dur: 0.3, gain: 0.4 }], [0, 'typing', { dur: len, rate: 18, gain: 0.7, pan: 0.6 }], ...b.cues, [b.at.m6 + 0.6, 'sparkle'], [b.at.m6 + 1.2, 'ping', { n: 3, gap: 0.3, gain: 0.6 }]]);
}
{
  const len = 3.8;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 1000, 560, 1.12);
    st.office(ctx, t, { board: 1 });
    st.clockFace(ctx, 820, 300, 64, lt * 9);
    fx.sfxText(ctx, 'TICK TOCK!', 820, 180, 0.5, { size: 46, fill: '#ffd23f', rot: Math.sin(t * 8) * 0.1 });
    st.dashboard(ctx, 1170, 210, 420, 300, t, { servers: 5, lb: 1, bars: 0.4 + 0.6 * seg(lt, 0, len) });
    const nod = Math.max(0, Math.sin(lt * 4)) * 0.8;
    pp(ctx, 'smei', t, { x: 1000, y: 930, s: 1.0, facing: 0.05, pose: 'hold', hold: [null, 'tea'], expr: 'proud', nod });
    pp(ctx, 'devit', t, { x: 720, y: 1010, s: 1.2, facing: 0.15, pose: 'type', sit: true, expr: 'determined' });
    pp(ctx, 'nimith', t, { x: 1290, y: 1120, s: 1.05, facing: -0.15, pose: 'type', sit: true, expr: 'calm' });
    // shared desk + laptop lids (backs toward us)
    poly(ctx, [[300, 960], [1700, 960], [1760, 1010], [240, 1010]]); paint(ctx, st.S.desk, 5); rrect(ctx, 240, 1010, 1520, 200, 6); paint(ctx, st.S.deskD, 5);
    for (const lx of [720, 1290]) { poly(ctx, [[lx - 110, 965], [lx + 110, 965], [lx + 98, 885], [lx - 98, 885]]); paint(ctx, '#d9dde8', 5); st.nhamLogo(ctx, lx, 925, 0.22); }
    ctx.restore();
    warmLight(ctx, 0.12);
  }, [[0, 'clock_fast', { dur: 3.4 }], [0, 'typing', { dur: 3.4, gain: 0.5 }], [0.6, 'nod'], [1.4, 'nod']]);
}

// ============================================================ SCENE 8 — Success and Lesson
{
  const b = beats([0.7, 'n5']), len = b.end + 0.4;
  take(len, (ctx, lt, t) => {
    ctx.fillStyle = '#f8e6d6'; ctx.fillRect(0, 0, W, H);
    const ok = ease.out(seg(lt, 0.2, 0.6));
    st.dashboard(ctx, 230, 120 + (1 - ok) * 40, 1460, 840, t, { servers: 5, lb: 1, bars: 1, status: ok });
    if (lt > 0.25) st.confetti(ctx, t, { n: 40, seed: 3 });
  }, [[0, 'music_end', { id: 'bd', how: 'cut' }], [0.2, 'chime_success'], [0.25, 'music', { id: 'tr2', style: 'triumph', gain: 0.55 }], ...b.cues]);
}
{
  const n6 = beats([0.2, 'n6']), split = n6.at.n6 + D('n6') * 0.5;
  const len1 = split + 0.1, len2 = n6.end - split + 1.4;
  take(len1, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 960, 560, 1);
    st.sunsetSky(ctx, { horizon: 900, t, sunY: 420 });
    st.shophouses(ctx, t * 260);
    const rx = lerp(-200, 1500, lt / len1);
    fx.speedStreaks(ctx, rx - 220, 820, 360, 260, t, { n: 6, dir: -1, alpha: 0.7 });
    st.rider(ctx, rx, 1010, 1.25, t);
    fx.dust(ctx, rx - 180, 1000, (lt * 2.5) % 1, { n: 4, spread: 140, r: 34, seed: Math.floor(lt * 2.5) });
    fx.sfxText(ctx, 'ZOOM!', rx + 120, 560, seg(lt, 0.2, 1.4), { size: 90, fill: '#ffd23f', rot: -0.1 });
    ctx.restore();
  }, [...n6.cues, [0, 'motorbike', { dur: len1, gain: 0.35 }], [0.4, 'honk'], [0, 'city_amb', { dur: len1 + len2 }]]);
  const cust = { ...CAST.nimith, shirt: '#ffb3c1', shirtD: '#f39aab', collar: '#ffd0da', glasses: false, hairStyle: 'ponytail', tie: '#9fe3c9', H: 360, sw: 38, ww: 32, eyeSize: 1.05 };
  const kid = { ...CAST.devit, shirt: '#9fe3c9', shirtD: '#7fcfb2', collar: '#c4f3e1', headphones: false, H: 250, style: 'shirt' };
  take(len2, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 960, 600, 1.2);
    st.sunsetSky(ctx, { horizon: 900, t, sunY: 420 });
    st.shophouses(ctx, 410);
    st.rider(ctx, 620, 1010, 1.15, 0, {});
    const give = seg(lt, 0.3, 0.9);
    fx.sfxText(ctx, 'YUM!', 1440, 380, seg(lt, 0.9, 2.2), { size: 90, fill: '#ff8c6b', rot: 0.1, wob: 3 });
    pp(ctx, cust, t, { x: 1120, y: 960, s: 1.0, facing: -0.4, pose: give < 1 ? 'reach' : 'thumbs', reach: [-90, -250], expr: 'grin' });
    pp(ctx, kid, t, { x: 1300, y: 960, s: 1.0, facing: -0.2, pose: 'cheer', expr: 'laugh' });
    // the delivery bag
    const bx = lerp(820, 1040, ease.inOut(give)), by = lerp(800, 760, give);
    rrect(ctx, bx - 40, by - 50, 80, 70, 10); paint(ctx, '#fff6ea', 4); st.nhamLogo(ctx, bx, by - 14, 0.24);
    ctx.restore();
    if (give >= 1) st.confetti(ctx, t, { n: 20, seed: 9, area: [900, -100, 600, 900] });
  }, [[0.85, 'sparkle'], [0.9, 'ping', { n: 2, gap: 0.2, gain: 0.6 }]]);
}
{
  const len = 2.8;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 1000, 600, 1.4);
    st.office(ctx, t, { board: 1 });
    pp(ctx, 'smei', t, { x: 1400, y: 950, s: 0.95, facing: -0.3, pose: 'hold', hold: [null, 'tea'], expr: 'proud' });
    const hf = lt > 0.55;
    const dvo = { x: 840, y: 1060, s: 1.4, facing: 0.7, pose: 'highfive' }, hand = anchors('devit', dvo).handR;
    const nmo = { x: 1190, y: 1080, s: 1.2, facing: -0.6, pose: 'reachL' };
    const meet = ease.out(seg(lt, 0.15, 0.55)), nh = localOf('nimith', nmo, hand);
    pp(ctx, 'devit', t, { ...dvo, hold: ['coffee', null], expr: hf ? 'laugh' : 'grin', sq: hf ? wobble(lt - 0.55, 3, 6) * 0.1 : 0 });
    pp(ctx, 'nimith', t, { ...nmo, reach: [lerp(-90, nh[0], meet), lerp(-120, nh[1], meet)], expr: hf ? 'laugh' : 'grin', sq: hf ? wobble(lt - 0.55, 3, 6) * 0.08 : 0 });
    if (hf) fx.impact(ctx, hand[0], hand[1] - 20, 120, seg(lt, 0.55, 1.5), { word: 'POW!', size: 70, col: '#ffd23f', wcol: '#ff5c8a' });
    ctx.restore();
    st.confetti(ctx, t, { n: 50, seed: 5 });
  }, [[0.55, 'highfive'], [0.6, 'sparkle']]);
}
// rooftop at night
const roofBack = (ctx, t, z = 1, cy = 560) => {
  ctx.save(); cam(ctx, 960, cy, z);
  st.nightSky(ctx, t); st.skyline(ctx, t, { night: 1 }); st.rooftop(ctx, t);
  pp(ctx, 'devit', t, { x: 760, y: 960, s: 1.0, back: true, pose: 'sitBack' });
  pp(ctx, 'smei', t, { x: 960, y: 960, s: 1.05, back: true, pose: 'sitBack' });
  pp(ctx, 'nimith', t, { x: 1160, y: 960, s: 1.0, back: true, pose: 'sitBack' });
  ctx.restore();
};
{
  const len = 3.6;
  take(len, (ctx, lt, t) => roofBack(ctx, t, lerp(1.15, 1.0, ease.inOut(lt / len)), 600),
    [[0, 'music_end', { id: 'tr2', how: 'fade', dur: 0.8 }], [0, 'music', { id: 'td', style: 'tender', gain: 0.7 }], [0, 'night_amb', { dur: len }]]);
}
function roofFront(ctx, t, o = {}) {
  st.nightSky(ctx, t, { horizon: 900 });
  ctx.save(); ctx.translate(960, 900); ctx.scale(0.62, 0.62); ctx.translate(-1100, -880); ctx.globalAlpha = 0.9; st.skyline(ctx, t, { night: 1 }); ctx.restore();
  rrect(ctx, -400, 880, 2800, 400, 4); paint(ctx, '#7c7398', 0);
  pp(ctx, 'devit', t, { x: 620, y: 1050, s: 1.22, sit: true, pose: 'sitTalk', hold: ['coffee', null], facing: 0.5, expr: 'smile', ...o.devit });
  pp(ctx, 'smei', t, { x: 960, y: 1110, s: 1.2, sit: true, pose: 'sitTalk', hold: [null, 'tea'], facing: 0, expr: 'calm', ...o.smei });
  pp(ctx, 'nimith', t, { x: 1300, y: 1190, s: 1.08, sit: true, pose: 'sitTalk', facing: -0.5, expr: 'smile', ...o.nimith });
  rrect(ctx, -400, 960, 2800, 300, 6); paint(ctx, '#968cb2', 5);
  for (let x = -400; x < 2400; x += 120) { ctx.beginPath(); ctx.moveTo(x, 960); ctx.lineTo(x, 1260); paint(ctx, null, 3, '#857ba3'); }
}
{
  const b = beats([0.6, 'd7', 0.3, 'd8', 0.5, 'm7']), len = b.end + 0.9;
  take(len, (ctx, lt, t) => {
    const onN = lt > b.at.m7 - 0.2;
    ctx.save(); cam(ctx, onN ? 1080 : 840, 720, 1.7);
    roofFront(ctx, t, { devit: { facing: 0.7, look: [1, 0], expr: lt > b.at.d8 + D('d8') ? 'grin' : 'smile' }, nimith: { look: [-1, 0], expr: onN ? 'smile' : 'calm' }, smei: { look: [onN ? 1 : -1, 0], expr: 'smile' } });
    ctx.restore();
  }, [...b.cues, [0, 'night_amb', { dur: len }]]);
}
{
  const b = beats([0.5, 's8', 0.35, 's9', 0.3, 's10']), len = b.end + 0.4;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 960, 690, 2.1);
    roofFront(ctx, t, { devit: { look: [1, -0.2] }, nimith: { look: [-1, -0.2] } });
    ctx.restore();
  }, [...b.cues, [0, 'night_amb', { dur: len }]]);
}
{
  const b = beats([0.3, 's11']), len = b.end + 2.0;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 960, 740, lerp(1.45, 1.25, ease.inOut(lt / len)));
    roofFront(ctx, t, { devit: { expr: lt > b.end ? 'laugh' : 'smile', look: [1, 0] }, nimith: { expr: lt > b.end ? 'laugh' : 'smile', look: [-1, 0] }, smei: { expr: lt > b.end ? 'proud' : 'calm' } });
    ctx.restore();
  }, [...b.cues, [b.end + 0.2, 'sting_tiny'], [0, 'night_amb', { dur: len }]]);
}
{
  const len = 6.0;
  take(len, (ctx, lt, t) => {
    const k = ease.inOut(seg(lt, 0, 4.5));
    roofBack(ctx, t, lerp(1.0, 0.55, k), lerp(600, -500, k));
    titleKh(ctx, lt, 2.6, 5.4, 'ចប់', 'The End  •  Bong Smei, Bong Nimith & Devit', 420);
    fx.wash(ctx, '#1b1a33', seg(lt, len - 0.6, len));
  }, [[0.3, 'whoosh', { f0: 200, f1: 900, dur: 3, gain: 0.25 }], [2.6, 'chime_success'], [len - 0.1, 'music_end', { id: 'td', how: 'fade', dur: 2.4 }], [0, 'night_amb', { dur: len }]]);
}

export { drawFrame, allCues } from './kit.mjs';
export const DURATION = duration();
