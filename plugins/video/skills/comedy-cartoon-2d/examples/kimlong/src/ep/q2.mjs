// PART 2 (scenes 6-9): lunch with a cheesy line for the waitress, an ear pinch, the new game duo, Channy again.
import { W, H, INK, TAU, paint, circle, oval, rrect, poly, text, clamp, lerp, seg, ease, hash } from '../core.mjs';
import { take, beats, cam, talk, shk, radialLines } from '../kit.mjs';
import { person, anchors, toLocal, CAST, chair, chairBack } from '../people.mjs';
import * as pl from '../places.mjs';
import * as fx from '../fx.mjs';
import * as e from '../ep6.mjs';
import * as q from '../ep7.mjs';
import { D, MARKS, KP, DV, SM, NM, LH, PS, KL, CN, SN, pp, warmLight, sweat, stars, headOf, atHead, blush, sfx, room, backRow, seat } from './common.mjs';

// ---------------------------------------------------------------- lunch: seven at one long table
const SEAT = { smey: 250, nimith: 485, david: 720, sopheak: 955, pisey: 1190, leanghak: 1425, kimlong: 1660 };
const TY = 712;
const at = (who, o = {}) => seat(who, SEAT[who], { s: 1.05, pose: 'sitTalk', facing: 0, headY: 552, phones: who === KP ? 'neck' : undefined, ...o });
function table(ctx, t) {
  const x0 = 110, x1 = 1810;
  poly(ctx, [[x0, TY], [x1, TY], [x1 + 40, TY + 60], [x0 - 40, TY + 60]]); paint(ctx, '#ffffff', 6);
  rrect(ctx, x0 - 40, TY + 60, x1 - x0 + 80, 26, 6); paint(ctx, '#e9edf3', 5);
  rrect(ctx, x0 - 30, TY + 80, x1 - x0 + 60, 260, 6); paint(ctx, '#e8433a', 6);
  for (let i = 0; i < 26; i++) { ctx.fillStyle = 'rgba(255,255,255,0.35)'; ctx.fillRect(x0 - 30 + i * (x1 - x0 + 60) / 26, TY + 84, (x1 - x0 + 60) / 52, 252); }
  for (const [x, kind] of [[370, 'rice'], [840, 'amok'], [1070, 'soup'], [1310, 'fry'], [1545, 'rice']]) {
    if (kind === 'soup') { rrect(ctx, x - 50, TY - 30, 100, 54, 14); paint(ctx, '#e8875a', 5); oval(ctx, x, TY - 30, 50, 12); paint(ctx, '#f6c98a', 4); for (let i = 0; i < 3; i++) { const k = (t * 0.7 + i / 3) % 1; ctx.save(); ctx.globalAlpha = (1 - k) * 0.6; fx.puff(ctx, x - 20 + i * 20, TY - 50 - k * 70, 10 + k * 12, '#ffffff', 1, 3); ctx.restore(); } }
    else { oval(ctx, x, TY + 6, 66, 20); paint(ctx, '#ffffff', 5); oval(ctx, x, TY - 2, 46, 14); paint(ctx, { rice: '#fffaf0', amok: '#f2b13a', fry: '#7fbf5a' }[kind], 3); }
  }
  for (const x of Object.values(SEAT)) { oval(ctx, x + 10, TY + 40, 62, 16); paint(ctx, '#ffffff', 4); oval(ctx, x + 10, TY + 36, 36, 9); paint(ctx, '#fffaf0', 3); e.glass(ctx, x + 84, TY + 34, 0.9, 0.6); }
}
const diners = (ctx, t, o = {}) => { for (const who of Object.keys(SEAT)) pp(ctx, who, t, at(who, o[who] || {})); };
const waitress = (ctx, t, o) => { pp(ctx, SN, t, o); const h = anchors(SN, o)[o.pose === 'reachL' ? 'handL' : 'handR']; q.notepad(ctx, h[0] + (o.pose === 'reachL' ? -6 : 6), h[1] - 10, 0.85, o.pose === 'reachL' ? -0.5 : 0.15); };

// ============================================================ SCENE 6 — "Just looking at your face fills me up!"
{
  const b = beats([1.6, 'g6a', 0.2]), len = b.end + 0.3, IN = 0.2;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 960, 560, 1.0);
    pl.restaurant(ctx, t);
    diners(ctx, t, { kimlong: { pose: lt > b.at.g6a - 0.2 ? 'raise' : 'sitTalk', expr: 'grin', facing: 0.3, look: [1, 0] } });
    table(ctx, t);
    const w = ease.out(seg(lt, IN, IN + 1.3));
    waitress(ctx, t, { x: lerp(2150, 1850, w), y: 1030, s: 1.05, facing: -0.45, pose: w < 1 ? 'walk' : 'hold', ph: t * 2.1, expr: 'grin', look: [-1, 0.2] });
    ctx.restore();
    q.nameCard(ctx, 1540, 200, 'ស្រីនាង', 'អ្នករត់តុ', seg(lt, IN + 0.9, IN + 1.3), { size: 54, icon: 'rice' });
    warmLight(ctx, 0.14);
  }, [[0, 'city_amb', { dur: len }], [0, 'music', { id: 'm6', style: 'upbeat', gain: 0.22, bpm: 104 }], [IN + 0.2, 'footsteps', { n: 4, gap: 0.3 }], [IN + 1.2, 'pop', { f0: 900, f1: 1300 }], ...b.cues]);
}
{
  const b = beats([0.3, 'g6b', 0.35, 'y6a', 0.1, 'y6b', 0.1]), TAP = b.at.y6b + D('y6b') * 0.7, OFF = b.end + 0.2;
  const b2 = beats([OFF + 0.15, 'g6c']), len = b2.end + 0.2;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 1500, 545, 1.5);
    pl.restaurant(ctx, t);
    const flirt = lt < b.at.y6a, bonked = lt > TAP, panic = lt > b2.at.g6c - 0.15;
    const kO = at(KL, { pose: panic ? 'panic' : flirt ? 'chest' : 'sitTalk', expr: panic ? 'surprised' : flirt ? 'love' : bonked ? 'worried' : 'grin', facing: 0.35, look: [1, -0.2], tilt: bonked && !panic ? 0.1 : 0, sq: bonked ? Math.max(0, Math.sin(seg(lt, TAP, TAP + 0.3) * Math.PI)) * -0.08 : 0 });
    diners(ctx, t, { kimlong: kO, leanghak: { expr: lt > b.at.y6a ? 'laugh' : 'grin', facing: 0.35, look: [1, 0] }, pisey: { expr: lt > b.at.y6b ? 'laugh' : 'smile', facing: 0.3, look: [1, 0] }, sopheak: { expr: lt > TAP ? 'laugh' : 'smile', facing: 0.4, look: [1, 0] } });
    table(ctx, t);
    // Sreyneang: laughs at the line, taps his head with her notepad, walks off
    const tapping = lt > TAP - 0.45 && lt < TAP + 0.3, leave = ease.in(seg(lt, OFF - 0.3, OFF + 0.8));
    const sO = { x: 1880 + leave * 500, y: 1030, s: 1.05, facing: leave > 0 ? 0.5 : -0.4, pose: leave > 0 ? 'walk' : tapping ? 'reachL' : lt > b.at.y6a ? 'wag' : 'hold', ph: t * 2.2, expr: lt > b.at.g6b + D('g6b') * 0.6 ? 'laugh' : 'grin', look: [-1, 0.2] };
    if (tapping) { const hd = headOf(KL, kO), k = Math.sin(seg(lt, TAP - 0.45, TAP) * Math.PI / 2); sO.reach = toLocal(SN, sO, [lerp(hd[0] + 140, hd[0] + 20, k), hd[1] - 110 + k * 20]); }
    waitress(ctx, t, sO);
    const hd = headOf(KL, kO);
    q.flirtFx(ctx, hd[0], hd[1], t, seg(lt, b.at.g6b, b.at.g6b + 0.5) * (1 - seg(lt, b.at.y6a - 0.2, b.at.y6a + 0.2)), 0.8);
    if (bonked && lt < TAP + 1.4) stars(ctx, TAP, lt, [[hd[0] - 70, hd[1] - 110], [hd[0] + 60, hd[1] - 130], [hd[0], hd[1] - 150]], 0.8);
    ctx.restore();
    sfx(ctx, 'BONK!', 1120, 230, lt, TAP, { size: 100, fill: '#ffffff', dur: 0.8 });
    q.plok(ctx, 1500, 260, lt, TAP + 0.5);
    warmLight(ctx, 0.14);
  }, [[0, 'music_end', { id: 'm6', how: 'fade', dur: 0.4 }], [0.1, 'music', { id: 'luv2', style: 'love', gain: 0.32 }], ...b.cues, [b.at.y6a - 0.05, 'music_end', { id: 'luv2', how: 'cut' }], [b.at.y6a - 0.05, 'record_scratch', { gain: 0.6 }], [TAP, 'bonk'], [TAP + 0.5, 'pop', { f0: 520, f1: 110, gain: 0.6 }], [OFF, 'footsteps', { n: 3, gap: 0.3, gain: 0.5 }], ...b2.cues, [b2.at.g6c, 'sting_panic', { gain: 0.5 }]]);
}
{
  const b = beats([0.15, 'k6', 0.2]), len = b.end + 0.8;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 960, 560, 1.0);
    pl.restaurant(ctx, t);
    const o = {}; for (const who of Object.keys(SEAT)) o[who] = { expr: 'laugh', sq: Math.sin(t * 18 + SEAT[who]) * 0.02, facing: (1660 - SEAT[who]) * 0.0004 };
    o.kimlong = { pose: 'rub', expr: 'worried', facing: -0.2, look: [-1, 0] }; o.sopheak = { ...o.sopheak, pose: 'point', facing: 0.4 };
    diners(ctx, t, o);
    table(ctx, t);
    ctx.restore();
    sfx(ctx, 'HAHAHA!', 960, 220, lt, b.at.k6 + 0.4, { size: 100, fill: '#ffd23f', dur: 1.4 });
    warmLight(ctx, 0.14);
  }, [...b.cues, [b.at.k6 + 0.3, 'applause', { gain: 0.25, dur: 1.2 }], [b.at.k6 + 0.2, 'heh']]);
}

// ============================================================ SCENE 7 — an ear pinch and a finger wag
{
  const b = beats([0.4, 'l7', 0.25, 'p7', 0.3, 'g7a', 0.1, 'g7b', 0.2]), PINCH = 0.25, LET = b.at.g7a - 0.1, len = b.end + 0.6;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 1260, 550, 1.5);
    pl.restaurant(ctx, t);
    const pinched = lt > PINCH && lt < LET;
    const kO = at(KL, { x: SEAT.kimlong - (pinched ? 40 : 0), pose: lt > LET ? 'sampeah' : 'sitTalk', expr: pinched ? 'laugh' : lt > LET ? 'laugh' : 'grin', facing: -0.3, tilt: pinched ? -0.22 : 0, look: [-1, 0] });
    kO.x = SEAT.kimlong - (pinched ? 40 : 0);
    const lO = at(LH, { pose: pinched ? 'reach' : 'sitTalk', expr: pinched ? 'determined' : 'laugh', facing: 0.35, look: [1, 0] });
    if (pinched) { const hd = headOf(KL, kO); lO.reach = toLocal(LH, lO, [hd[0] - 74, hd[1] + 4]); }
    const pO = { pose: lt > b.at.p7 - 0.1 && lt < LET ? 'wag' : 'sitTalk', expr: lt > LET ? 'laugh' : 'determined', facing: 0.4, look: [1, 0] };
    const bellyO = who => ({ pose: lt > b.at.l7 + 0.5 ? 'belly' : 'sitTalk', expr: 'laugh', facing: 0.4, look: [1, 0], sq: Math.sin(t * 20 + SEAT[who]) * 0.025 });
    diners(ctx, t, { kimlong: kO, leanghak: lO, pisey: pO, david: bellyO(DV), sopheak: bellyO(KP) });
    table(ctx, t);
    if (pinched) { const hd = headOf(KL, kO); ctx.save(); ctx.globalAlpha = 0.8; ctx.lineCap = 'round'; for (const a of [-2.6, -2.2, -1.8]) { ctx.beginPath(); ctx.moveTo(hd[0] - 80 + Math.cos(a) * 30, hd[1] + Math.sin(a) * 30); ctx.lineTo(hd[0] - 80 + Math.cos(a) * 52, hd[1] + Math.sin(a) * 52); paint(ctx, null, 6, '#e8433a'); } ctx.restore(); }
    ctx.restore();
    sfx(ctx, 'OUCH!', 1500, 230, lt, PINCH + 0.1, { size: 90, fill: '#ff8fab', dur: 0.9 });
    warmLight(ctx, 0.14);
  }, [[PINCH, 'squeak_rubber', { gain: 0.6 }], ...b.cues, [b.at.l7 + 0.6, 'heh'], [LET + 0.4, 'applause', { gain: 0.2, dur: 0.8 }], [len - 0.3, 'city_amb', { dur: 0.3 }]]);
}

// ---------------------------------------------------------------- game time: six in a circle, Kimlong and Sopheak side by side, Pisey behind with fruit
const ARC = {
  nimith: { x: 330, y: 1060, s: 1.15, facing: 0.6 }, leanghak: { x: 600, y: 990, s: 1.04, facing: 0.3 }, david: { x: 840, y: 960, s: 1.0, facing: 0.1 },
  kimlong: { x: 1080, y: 960, s: 1.0, facing: -0.1 }, sopheak: { x: 1320, y: 990, s: 1.04, facing: -0.3 }, smey: { x: 1590, y: 1060, s: 1.15, facing: -0.6 },
};
const PIS = { x: 1200, y: 800, s: 0.88, facing: -0.1 };
const PSG = { ...CAST.pisey, glasses: true, chainGlasses: false };
function gamer(ctx, who, o, t, fast = 1) {
  const O = { sit: true, pose: 'notebook', expr: 'determined', look: [0, 0.7], phones: who === KP ? 'one' : undefined, ...o };
  if (O.pose === 'notebook') O.sq = (O.sq || 0) + Math.sin(t * 22 * fast + O.x) * 0.006 * fast;
  pp(ctx, who, t, O);
  if (O.pose !== 'notebook') return;
  const c = anchors(who, O).chest, s = O.s || 1, w = 82 * s, h = 46 * s, y = c[1] + 2 * s;
  rrect(ctx, c[0] - w / 2, y - h / 2, w, h, 9 * s); paint(ctx, '#2c2a33', 5);
  const hd = headOf(who, O); ctx.save(); ctx.globalAlpha = 0.16 + 0.08 * Math.sin(t * 9 + O.x); ctx.globalCompositeOperation = 'screen'; oval(ctx, hd[0], hd[1] + 20 * s, 60 * s, 50 * s); ctx.fillStyle = ['#7fd3ff', '#ffd23f', '#ff8fab'][Math.floor(t * 3 + O.x) % 3]; ctx.fill(); ctx.restore();
}
function circleOf(ctx, t, opts = {}, { pisey = true } = {}) {
  if (pisey) { const pO = { ...PIS, pose: 'hold', expr: 'smile', look: [0, 0.4], ...(opts.pisey || {}) }; person(ctx, PSG, { t, mouth: talk(PS, t), ...pO }); const h = anchors(PSG, pO).handR; if (pO.pose === 'hold') e.mangoPlate(ctx, h[0] + 10, h[1] + 6, 0.6); }
  for (const who of [LH, DV, KL, KP, NM, SM]) { const o = { ...ARC[who], ...(opts[who] || {}) }; chairBack(ctx, o.x - (o.facing || 0) * 20, o.y - 50 * o.s, o.s * 0.95, who === KL ? '#e8433a' : '#6c7a96'); gamer(ctx, who, o, t, o.fast || 1); }
}
const circleBg = (ctx, t) => { room(ctx, t, { hour: 12.5 }); backRow(ctx); };
const CU = (ctx, who, t, o = {}, bg = '#3f8bd0') => {
  ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);
  radialLines(ctx, t, 960, 560, { n: 30, spd: 2.6, col: 'rgba(255,255,255,0.28)', inner: 380 });
  const O = { x: 960, s: 2.5, sit: true, facing: 0.1, pose: 'notebook', ...o }; O.y = atHead(who, { ...O, x: 0 }, 470);
  gamer(ctx, who, O, t, O.fast || 1);
};

// ============================================================ SCENE 8 — the new duo: «👑 គូហ្គេមថ្មី៖ សុភ័ក្រ & គីមឡុង!»
{
  const b = beats([1.2, 'g8a', 0.15, 'k8', 0.3]), len = b.end + 0.2;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 960, 760, 1.25);
    circleBg(ctx, t);
    circleOf(ctx, t, { kimlong: { expr: 'grin', look: [0.6, 0.4] }, sopheak: { expr: 'determined', look: [-0.6, 0.4] } });
    ctx.restore();
    e.tag(ctx, 700, 170, 'គូហ្គេមថ្មី៖ សុភ័ក្រ & គីមឡុង!', seg(lt, 0.2, 0.7), { icon: 'crown', icon2: 'game', size: 70, col: '#fff6e6', ink: '#7c5cff', rot: -0.03 });
    warmLight(ctx, 0.08);
  }, [[0, 'music', { id: 'm8', style: 'game', gain: 0.26 }], [0.2, 'title_whoosh'], [0.5, 'ta_da_small'], ...b.cues]);
}
{
  const b = beats([0.15, 'g8b', 0.1]), DONE = b.at.g8b + D('g8b') * 0.8, len = b.end + 0.5;
  take(len, (ctx, lt, t) => {
    const half = lt < b.at.g8b + D('g8b') * 0.45;
    if (half) CU(ctx, KL, t, { expr: 'calm', facing: 0.05, look: [0, 0.8], fast: 3 }, '#a07bff');
    else { ctx.fillStyle = '#1d1530'; ctx.fillRect(0, 0, W, H); e.gamePhone(ctx, 960, 540, 1700, t * 3, { win: lt > DONE }); for (const k of [-1, 1]) { const tap = Math.max(0, Math.sin(t * (k > 0 ? 40 : 34))) * 30; ctx.save(); ctx.translate(960 + k * 720, 860 - tap); ctx.scale(k, 1); oval(ctx, 0, 0, 70, 110, -0.5); paint(ctx, CAST.kimlong.skin, 7); ctx.restore(); } }
    if (!half && lt < DONE) for (let i = 0; i < 4; i++) { const k = seg(lt, b.at.g8b + D('g8b') * 0.45 + i * 0.18, b.at.g8b + D('g8b') * 0.45 + i * 0.18 + 0.4); if (k > 0 && k < 1) fx.impact(ctx, 600 + i * 240, 380 + (i % 2) * 140, 110, k, { col: '#ffd23f', word: ['COMBO!', 'x2', 'x5', 'x10'][i], size: 64 }); }
  }, [...b.cues, [b.at.g8b + D('g8b') * 0.45, 'zap'], [b.at.g8b + D('g8b') * 0.6, 'zap'], [b.at.g8b + D('g8b') * 0.72, 'zap'], [DONE, 'ta_da'], [DONE + 0.1, 'party_pop']]);
}
{
  const b = beats([0.15, 'l8a', 0.1, 'l8b', 0.25]), len = b.end;
  take(len, (ctx, lt, t) => {
    CU(ctx, LH, t, { expr: lt < b.at.l8b ? 'surprised' : 'panic', pose: lt < b.at.l8b ? 'notebook' : 'panic', facing: 0.1, look: [0, 0.2] }, '#e8433a');
    sweat(ctx, 960, 300, 1.8, t, 3);
    sfx(ctx, 'NOOO!', 1500, 260, lt, b.at.l8b, { size: 100, fill: '#ffffff', dur: 1.0 });
  }, [[0, 'sting_shock', { gain: 0.5 }], ...b.cues]);
}
{
  const b = beats([0.2, 'd8', 0.3]), FIVE = b.at.d8 + D('d8') * 0.6, len = b.end + 0.5;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 960, 760, 1.25);
    circleBg(ctx, t);
    const five = lt > FIVE;
    circleOf(ctx, t, {
      david: { pose: 'point', expr: 'laugh', facing: 0.3, look: [1, 0] }, leanghak: { pose: 'sitBack', expr: 'tired', look: [0, 0.3] },
      kimlong: { pose: five ? 'highfive' : 'notebook', expr: 'laugh', facing: 0.3, look: [1, -0.2] }, sopheak: { pose: five ? 'highfive' : 'notebook', mirror: five, expr: 'laugh', facing: five ? 0.3 : -0.3, look: [-1, -0.2] },
      smey: { expr: 'laugh', pose: 'clap' }, nimith: { expr: 'laugh', pose: 'clap' }, pisey: { pose: 'clap', expr: 'laugh' },
    });
    ctx.restore();
    sfx(ctx, 'HIGH FIVE!', 1200, 260, lt, FIVE, { size: 84, fill: '#ffd23f', dur: 1.0 });
    warmLight(ctx, 0.08);
  }, [...b.cues, [FIVE, 'highfive'], [FIVE + 0.1, 'applause', { gain: 0.3, dur: 1 }], [len - 0.2, 'music_end', { id: 'm8', how: 'tapestop', dur: 0.6 }]]);
}

// ============================================================ SCENE 9 — Channy brings documents; «ឈ្នះហ្គេម ១០០% 🏆 | ឈ្នះស្នេហា ០% 💔»
{
  const KNOCK = 0.2, OPEN = 0.9, b = beats([1.6, 'c9', 0.15, 'g9a', 0.1, 'g9b', 0.2]), LEAVE = b.end - 0.2, SHUT = LEAVE + 1.1;
  const b2 = beats([SHUT + 0.6, 'k9', 0.25, 'm9', 0.4]), SLUMP = SHUT + 0.15, len = b2.end + 0.6;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 1180, 770, 1.35);
    room(ctx, t, { hour: 12.8, door: ease.out(seg(lt, OPEN - 0.2, OPEN + 0.1)) * (1 - ease.inOut(seg(lt, SHUT - 0.3, SHUT))) });
    backRow(ctx);
    // Channy: in, a folder for Smey, out again (not one glance at Kimlong)
    const inK = ease.out(seg(lt, OPEN, OPEN + 1.0)), outK = ease.in(seg(lt, LEAVE, SHUT - 0.1));
    const cx = lerp(1890, 1800, inK) + outK * 200, cwalk = (inK > 0 && inK < 1) || (outK > 0 && outK < 1);
    const giving = lt > b.at.c9 && lt < LEAVE;
    // Kimlong: phone drops, back straight, hair, the big smile; then the slump on Sopheak's shoulder
    const alert = lt > OPEN + 0.2, slump = ease.out(seg(lt, SLUMP, SLUMP + 0.4));
    const kO = alert ? { ...ARC.kimlong, sit: true, pose: lt < b.at.g9a - 0.1 ? 'fixHair' : slump > 0 ? 'stand' : 'chest', expr: slump > 0 ? 'tired' : lt > b.at.g9b ? 'love' : 'grin', facing: 0.3, look: [1, -0.1], rot: slump * 0.33, sq: alert && slump <= 0 ? -0.04 : 0, camera: true } : null;
    const elbow = lt > b2.at.k9 - 0.1 && lt < b2.at.k9 + D('k9') * 0.6;
    const opts = { kimlong: kO || {}, sopheak: { pose: elbow ? 'reachL' : 'notebook', expr: lt > SLUMP ? 'laugh' : 'grin', look: [-1, 0.2] }, smey: { pose: giving ? 'hold' : 'notebook', expr: giving ? 'smile' : 'determined', look: giving ? [1, -0.2] : [0, 0.7] }, david: { expr: lt > SLUMP ? 'laugh' : 'grin', look: [1, 0] }, leanghak: { expr: 'grin' }, nimith: { expr: lt > b2.at.m9 ? 'laugh' : 'smile', look: [1, 0] } };
    if (elbow && kO) { const sO = { ...ARC.sopheak, sit: true, pose: 'reachL', facing: -0.3 }; opts.sopheak.reach = toLocal(KP, sO, anchors(KL, kO).chest.map((v, i) => v + (i ? 10 : 30) + (i ? 0 : Math.sin(t * 20) * 8))); }
    circleOf(ctx, t, opts);
    // the dropped phone
    if (alert) { const k = ease.in(seg(lt, OPEN + 0.2, OPEN + 0.6)); ctx.save(); ctx.translate(ARC.kimlong.x + 40, lerp(ARC.kimlong.y - 150, ARC.kimlong.y - 10, k)); ctx.rotate(k * 2.4); rrect(ctx, -30, -18, 60, 36, 6); paint(ctx, '#2c2a33', 4); ctx.restore(); }
    if (lt > OPEN - 0.1 && lt < SHUT) { const cO = { x: cx, y: 1060, s: 1.12, facing: outK > 0 ? 0.4 : -0.35, pose: cwalk ? 'walk' : giving ? 'reachL' : 'hold', ph: t * 1.8, expr: 'calm', look: outK > 0 ? [1, 0] : [-1, 0.2] }; if (giving) cO.reach = toLocal(CN, cO, [ARC.smey.x + 120, ARC.smey.y - 200]); pp(ctx, CN, t, cO); const h = anchors(CN, cO)[giving ? 'handL' : 'handR']; if (lt < b.at.c9 + D('c9')) q.folder(ctx, h[0] - (giving ? 10 : -8), h[1] - 8, 0.85, giving ? -0.3 : 0.12); }
    if (kO) { const hd = headOf(KL, kO); q.flirtFx(ctx, hd[0], hd[1], t, seg(lt, b.at.g9a, b.at.g9a + 0.4) * (1 - seg(lt, LEAVE + 0.3, SHUT)), 0.7); }
    ctx.restore();
    sfx(ctx, 'KNOCK KNOCK', 1550, 230, lt, KNOCK, { size: 70, fill: '#ffffff', dur: 0.8 });
    q.plok(ctx, 1100, 250, lt, SHUT);
    q.scoreCard(ctx, 960, 170, seg(lt, b2.at.m9 - 0.2, b2.at.m9 + 0.3), t);
    warmLight(ctx, 0.08);
  }, [[KNOCK, 'knock'], [OPEN - 0.2, 'creak', { i: 1 }], [OPEN + 0.25, 'clunk', { gain: 0.5 }], [OPEN + 0.35, 'zip_up', { gain: 0.4 }], [OPEN + 0.5, 'music', { id: 'luv3', style: 'love', gain: 0.3 }], ...b.cues,
    [SHUT - 0.05, 'door_bam', { gain: 0.5 }], [SHUT, 'music_end', { id: 'luv3', how: 'cut' }], [SHUT + 0.02, 'pop', { f0: 520, f1: 110, gain: 0.6 }], [SLUMP + 0.1, 'flop'], [SLUMP + 0.5, 'sad_trombone', { gain: 0.4 }], ...b2.cues, [b2.at.m9 - 0.1, 'pop', { f0: 900, f1: 1300 }], [b2.at.m9 + 0.3, 'heh']]);
}
