// PART 3 (scenes 10-15): Kimlong drops the jokes to help David rehearse his thesis defence (camera, tripod, a mock committee),
// Channy notices his serious side and finally smiles at him; a timer photo of the new, bigger family.
import { W, H, INK, TAU, paint, circle, oval, rrect, poly, text, clamp, lerp, seg, ease, hash } from '../core.mjs';
import { take, beats, cam, talk, shk } from '../kit.mjs';
import { person, anchors, toLocal, CAST, chair, chairBack, camera } from '../people.mjs';
import * as pl from '../places.mjs';
import * as fx from '../fx.mjs';
import * as e from '../ep6.mjs';
import * as q from '../ep7.mjs';
import { D, KP, DV, SM, NM, LH, PS, KL, CN, pp, warmLight, goldHour, sweat, stars, star, headOf, atHead, blush, sfx, room, monitor, deskFront, seat, banner, thoughtBubble, bokeh, fit } from './common.mjs';

// David's practice papers, scattered on his desk
const papers = (ctx, x, y, n, t) => { for (let i = 0; i < n; i++) { ctx.save(); ctx.translate(x + (hash(i) - 0.5) * 380, y - (i % 3) * 6); ctx.rotate((hash(i * 3) - 0.5) * 0.6); rrect(ctx, -46, -14, 92, 28, 3); paint(ctx, '#fffaf0', 3); for (let r = 0; r < 2; r++) { ctx.beginPath(); ctx.moveTo(-34, -4 + r * 9); ctx.lineTo(28 - r * 14, -4 + r * 9); paint(ctx, null, 2, '#9aa3b5'); } ctx.restore(); } };

// ============================================================ SCENE 10 — David rehearses alone, whispering; Kimlong's face changes
{
  const b = beats([0.6, 'd10a', 0.3, 'd10b', 0.4]), len = b.end + 0.2;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 1240, 660, 1.45);
    room(ctx, t, { hour: 15.2 });
    monitor(ctx, 1100, { screen: (c, x, y, w, h) => q.slide(c, x + 4, y + 4, w - 8, h - 8, 0) });
    const dO = seat(DV, 1240, { pose: lt > b.at.d10b ? 'scratch' : 'hold', facing: -0.1, expr: lt > b.at.d10b ? 'worried' : 'tired', look: [-0.2, 0.7], headY: 540 });
    pp(ctx, DV, t, dO);
    if (lt < b.at.d10b) { const h = anchors(DV, dO).handR; ctx.save(); ctx.translate(h[0] + 6, h[1] - 20); ctx.rotate(-0.1 + Math.sin(t * 9) * 0.03); rrect(ctx, -40, -54, 80, 104, 4); paint(ctx, '#fffaf0', 4); for (let r = 0; r < 5; r++) { ctx.beginPath(); ctx.moveTo(-28, -36 + r * 16); ctx.lineTo(26 - (r % 2) * 18, -36 + r * 16); paint(ctx, null, 2.5, '#9aa3b5'); } ctx.restore(); }
    deskFront(ctx, 1240, 240);
    papers(ctx, 1240, 728, 9, t);
    sweat(ctx, headOf(DV, dO)[0], headOf(DV, dO)[1] - 40, 1.2, t, lt > b.at.d10b ? 3 : 1);
    ctx.restore();
    warmLight(ctx, 0.2, '255,190,120');
  }, [[0, 'music', { id: 'm10', style: 'tension', gain: 0.18 }], [0, 'room_tone', { dur: len }], [0.2, 'page_flip'], ...b.cues, [b.at.d10b + 0.2, 'page_flip', { gain: 0.6 }]]);
}
{
  const b = beats([1.5, 'g10', 0.3]), DOWN = 0.8, len = b.end + 0.4;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 560, 640, 1.55);
    room(ctx, t, { hour: 15.2 });
    monitor(ctx, 380);
    const serious = lt > 0.45, down = lt > DOWN;
    const kO = seat(KL, 560, { pose: down ? 'hold' : 'film', hold: down ? null : [null, 'camera'], camera: down ? false : false, facing: 0.45, expr: serious ? 'determined' : 'grin', look: [1, 0.1], headY: 520, mouth: 0 });
    pp(ctx, KL, t, kO);
    deskFront(ctx, 560, 240);
    if (down) camera(ctx, 640, 700 - (1 - ease.out(seg(lt, DOWN, DOWN + 0.3))) * 60, 1.1, 0.05);
    ctx.restore();
    thoughtBubble(ctx, 1380, 330, seg(lt, b.at.g10 - 0.2, b.at.g10 + 0.3), () => { ctx.save(); oval(ctx, 0, 0, 146, 100); ctx.clip(); ctx.fillStyle = '#e8eef6'; ctx.fillRect(-150, -110, 300, 220); person(ctx, DV, { x: 0, y: atHead(DV, { s: 0.8, sit: true }, 0), s: 0.8, sit: true, pose: 'scratch', expr: 'worried', t }); ctx.restore(); }, -1, 1.1);
    warmLight(ctx, 0.2, '255,190,120');
  }, [[DOWN + 0.25, 'clunk', { gain: 0.4 }], [0.45, 'sting_tiny', { gain: 0.4 }], ...b.cues, [len - 0.2, 'music_end', { id: 'm10', how: 'fade', dur: 0.5 }]]);
}

// ---------------------------------------------------------------- the practice room
const AUD = { [SM]: 560, [NM]: 860, [KP]: 1160 }, AY = 1230;
const audience = (ctx, t, sat = 1, o = {}) => { for (const [who, x] of Object.entries(AUD)) { if (sat <= 0) continue; pp(ctx, who, t, { x, y: AY, s: 1.3, back: true, sit: true, phones: who === KP ? 'neck' : undefined, ...(o[who] || {}) }); chairBack(ctx, x, AY + 40, 0.78, '#6c7a96'); } };
const PRES = { x: 1010, y: 1030, s: 1.12 };

// ============================================================ SCENE 11 — tripod, chairs in a row, "you three are the professors!"
{
  const b = beats([1.8, 'g11a', 0.2, 'g11b', 0.3, 's11', 0.3]), len = b.end + 0.2;
  const CH = [0.2, 0.55, 0.9], TRI = 1.25, DIN = b.at.g11a + 0.4, SIT = b.at.g11b + D('g11b') * 0.5;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 960, 640, 1.1);
    q.meetingRoom(ctx, t, { slideN: 0, door: ease.out(seg(lt, DIN - 0.4, DIN)) });
    // David comes in and takes his place by the screen
    const dw = ease.out(seg(lt, DIN, DIN + 1.4));
    if (lt > DIN - 0.1) pp(ctx, DV, t, { x: lerp(1770, PRES.x, dw), y: PRES.y, s: PRES.s, facing: dw < 1 ? -0.5 : 0.2, pose: dw < 1 ? 'walk' : 'hold', ph: t * 2, expr: dw < 1 ? 'worried' : 'tired', look: [-0.4, 0] });
    // Kimlong: chairs, tripod, then the director's wave
    const kO = { x: 1500, y: 1060, s: 1.12, facing: -0.3, pose: lt < TRI ? 'present' : lt < b.at.g11b ? 'wave' : 'point', mirror: lt < TRI, expr: 'determined', look: [-1, 0] };
    if (lt > b.at.g11b) { kO.expr = 'grin'; kO.facing = 0.3; kO.mirror = false; }
    q.tripodSide(ctx, 1330, 1080, 0.95 * ease.back(seg(lt, TRI, TRI + 0.3)), t, { rec: false });
    pp(ctx, KL, t, kO);
    // the three take their seats as the "committee"
    const sat = lt > SIT ? 1 : 0, wk = ease.out(seg(lt, b.at.g11b, SIT));
    if (!sat && lt > b.at.g11b) for (const [i, [who, x]] of Object.entries(AUD).entries()) pp(ctx, who, t, { x: lerp(1900 + i * 120, x, wk), y: AY - 40, s: 1.25, facing: -0.5, pose: 'walk', ph: t * 2 + i, phones: who === KP ? 'neck' : undefined, expr: 'grin', look: [-1, 0] });
    CH.forEach((a, i) => { const x = Object.values(AUD)[i], k = ease.out(seg(lt, a, a + 0.3)); if (k > 0 && !sat) chairBack(ctx, lerp(2100, x, k), AY + 40, 0.78, '#6c7a96'); });
    audience(ctx, t, sat, { smey: { tilt: lt > b.at.s11 ? 0.05 : 0 } });
    ctx.restore();
    warmLight(ctx, 0.12);
  }, [[0, 'music', { id: 'm11', style: 'build', gain: 0.2 }], ...CH.map(a => [a, 'whoosh_by', { gain: 0.35 }]), ...CH.map(a => [a + 0.3, 'roll_stop', { gain: 0.5 }]), [TRI, 'pop', { f0: 700, f1: 1100 }], [TRI + 0.1, 'clunk', { gain: 0.4 }], [DIN - 0.4, 'creak', { i: 1 }], ...b.cues, [b.at.g11b + 0.2, 'footsteps', { n: 5, gap: 0.3 }]]);
}

// ============================================================ SCENE 12 — the rehearsal: through the viewfinder, the mock professor, Channy at the door
{
  const b = beats([0.4, 'd12a', 0.25, 'd12b', 0.3]), CALM = b.at.d12b, len = b.end;
  take(len, (ctx, lt, t) => {
    const [jx, jy] = shk(t, 2, 9);
    ctx.save(); cam(ctx, 960 + jx, 760 + jy, 1.6);
    q.meetingRoom(ctx, t, { slideN: lt > CALM ? 1 : 0 });
    const calm = lt > CALM + 0.3;
    const dO = { ...PRES, facing: 0.15, pose: calm ? 'presentL' : 'hold', expr: calm ? 'determined' : 'worried', look: calm ? [0.2, 0] : [0, 0.8] };
    pp(ctx, DV, t, dO);
    if (!calm) { const h = anchors(DV, dO).handR; rrect(ctx, h[0] - 30, h[1] - 60, 60, 78, 4); paint(ctx, '#fffaf0', 4); sweat(ctx, headOf(DV, dO)[0], headOf(DV, dO)[1] - 40, 1.2, t, 2); }
    ctx.restore();
    q.viewfinder(ctx, t, lt + 12);
  }, [[0, 'ping', { gain: 0.3 }], [0, 'room_tone', { dur: len }], ...b.cues]);
}
{
  const b = beats([0.3, 'm12', 0.3]), len = b.end;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 860, 620, 1.9);
    q.meetingRoom(ctx, t, { slideN: 1 });
    const nO = { x: 860, y: 1030, s: 1.15, sit: true, facing: -0.15, pose: lt < 0.8 ? 'glasses' : 'notebook', expr: 'determined', look: [-0.5, -0.1] };
    nO.y = atHead(NM, { ...nO, x: 0 }, 520);
    pp(ctx, NM, t, nO);
    ctx.restore();
    if (lt < 1.2) star(ctx, 960, 330, seg(lt, 0.4, 1.2), 1.4);
    e.tag(ctx, 1500, 860, 'សាស្ត្រាចារ្យ (សាកល្បង)', seg(lt, 0.3, 0.7), { size: 48, col: '#2d3a6b', ink: '#ffffff' });
    warmLight(ctx, 0.1);
  }, [[0.4, 'sparkle', { gain: 0.5 }], ...b.cues]);
}
{
  const b = beats([0.8, 'c12', 0.6]), len = b.end;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 1500, 640, 1.3);
    q.meetingRoom(ctx, t, { slideN: 1, door: 1 });
    const cO = { x: 1760, y: 1000, s: 1.0, facing: -0.5, pose: 'chin', expr: lt > b.at.c12 + D('c12') * 0.5 ? 'grin' : 'calm', look: [-1, 0.1], mouth: 0 };
    pp(ctx, CN, t, cO);
    if (lt > b.at.c12 + D('c12') * 0.5) blush(ctx, CN, cO, seg(lt, b.at.c12 + D('c12') * 0.5, b.at.c12 + D('c12') * 0.5 + 0.6));
    // Kimlong at work behind the tripod, the most serious face of the day
    q.tripodSide(ctx, 1240, 1110, 1.0, t);
    pp(ctx, KL, t, { x: 1400, y: 1110, s: 1.15, facing: -0.55, pose: 'reachL', reach: [-110, -330], expr: 'determined', look: [-1, -0.1] });
    ctx.restore();
    warmLight(ctx, 0.12);
  }, [[0, 'music_end', { id: 'm11', how: 'fade', dur: 0.6 }], [0.2, 'music', { id: 'luv4', style: 'love', gain: 0.18, bpm: 80 }], ...b.cues]);
}

// ============================================================ SCENE 13 — watching the recording: "look at the audience, and smile"
const playback = (ctx, x, y, w, h, t, paused) => {
  ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
  ctx.fillStyle = '#e8eef6'; ctx.fillRect(x, y, w, h);
  ctx.translate(x, y); ctx.scale(w / 1920, h / 1080); ctx.translate(960, 540); ctx.scale(1.6, 1.6); ctx.translate(-960, -760);
  q.meetingRoom(ctx, paused ? 3 : t, { slideN: 0 });
  pp(ctx, DV, paused ? 3 : t, { ...PRES, facing: 0.1, pose: 'hold', expr: 'worried', look: [0, 0.9], mouth: 0 });
  ctx.restore();
  ctx.save(); ctx.fillStyle = 'rgba(0,0,0,0.25)'; ctx.fillRect(x, y + h - 40, w, 40); ctx.fillStyle = '#ff3b3b'; ctx.fillRect(x + 16, y + h - 22, (w - 32) * 0.42, 6); ctx.restore();
  if (paused) { ctx.save(); ctx.globalAlpha = 0.85; ctx.translate(-w / 2 + 110, h / 2 - 120); circle(ctx, x + w / 2, y + h / 2, 70); ctx.fillStyle = 'rgba(0,0,0,0.45)'; ctx.fill(); for (const k of [-1, 1]) { rrect(ctx, x + w / 2 + k * 22 - 10, y + h / 2 - 32, 20, 64, 5); ctx.fillStyle = '#ffffff'; ctx.fill(); } ctx.restore(); }
};
{
  const b = beats([0.4, 'g13a', 0.2, 'g13b', 0.3]), PAUSE = 0.35, len = b.end;
  take(len, (ctx, lt, t) => {
    bokeh(ctx, t, '#d9c4a8');
    // a big laptop screen, over two shoulders
    rrect(ctx, 330, 90, 1260, 760, 30); paint(ctx, '#2a2633', 10);
    playback(ctx, 370, 130, 1180, 680, t, lt > PAUSE);
    rrect(ctx, 230, 850, 1460, 60, 20); paint(ctx, '#9aa3b5', 8);
    // David (left) and Kimlong (right) from behind; Kimlong points at David looking down at his paper
    pp(ctx, DV, t, { x: 560, y: 1520, s: 2.0, back: true, tilt: -0.05 });
    const kO = { x: 1360, y: 1540, s: 2.0, back: true, pose: lt > PAUSE + 0.3 ? 'reach' : 'stand', reach: [-150, -330], tilt: 0.04 };
    pp(ctx, KL, t, kO);
    if (lt > PAUSE + 0.5) { const k = seg(lt, PAUSE + 0.5, PAUSE + 0.9); ctx.save(); ctx.globalAlpha = k; ctx.lineWidth = 8; ctx.strokeStyle = '#ffd23f'; oval(ctx, 1010, 420, 130 + Math.sin(t * 6) * 6, 190); ctx.stroke(); ctx.restore(); e.tag(ctx, 1320, 230, 'មើលតែក្រដាស!', k, { size: 50, col: '#fff6e6', ink: '#e8433a' }); }
  }, [[PAUSE, 'click'], [PAUSE + 0.5, 'pop', { f0: 900, f1: 1300 }], [0, 'music_end', { id: 'luv4', how: 'fade', dur: 0.4 }], [0.1, 'music', { id: 'm13', style: 'warm', gain: 0.2 }], ...b.cues]);
}
{
  const b = beats([0.25, 'g13c', 0.3, 'd13', 0.2, 'k13', 0.25, 'g13d', 0.3]), WINK = b.at.g13c + D('g13c') * 0.55, len = b.end;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 960, 640, 1.3);
    q.meetingRoom(ctx, t, { slideN: 1 });
    pp(ctx, SM, t, { x: 380, y: 1000, s: 1.06, facing: 0.3, pose: 'stand', expr: lt > b.at.d13 ? 'laugh' : 'smile', look: [0.4, 0.2] });
    pp(ctx, NM, t, { x: 1540, y: 1000, s: 1.06, facing: -0.3, pose: 'stand', expr: lt > b.at.d13 ? 'laugh' : 'smile', look: [-0.4, 0.2] });
    const flirt = lt > b.at.g13c + D('g13c') * 0.3 && lt < b.at.d13;
    const kO = seat(KL, 640, { pose: flirt ? 'chest' : lt > b.at.g13d ? 'thumbs' : 'point', facing: 0.4, expr: flirt ? (lt > WINK ? 'wink' : 'grin') : lt > b.at.k13 && lt < b.at.g13d ? 'worried' : 'grin', look: [1, 0], headY: 560, s: 1.2 });
    const dO = seat(DV, 960, { pose: lt > b.at.d13 + 0.4 ? 'hold' : 'sitTalk', facing: lt > b.at.d13 ? -0.3 : -0.2, expr: lt > b.at.d13 - 0.1 ? 'laugh' : 'smile', look: [-1, 0], headY: 560, s: 1.2 });
    const sO = seat(KP, 1290, { pose: lt > b.at.k13 ? 'point' : 'sitTalk', mirror: lt > b.at.k13, facing: lt > b.at.k13 ? 0.3 : -0.3, expr: lt > b.at.k13 ? 'laugh' : 'grin', phones: 'neck', look: [-1, 0], headY: 570, s: 1.2 });
    pp(ctx, KL, t, kO); pp(ctx, DV, t, dO); pp(ctx, KP, t, sO);
    // the table with the laptop (its back to us)
    rrect(ctx, 380, 820, 1160, 40, 10); paint(ctx, '#c97a4a', 6); rrect(ctx, 420, 860, 1080, 300, 6); paint(ctx, '#a8653a', 6);
    rrect(ctx, 1000, 700, 300, 130, 12); paint(ctx, '#d6dbe4', 6); circle(ctx, 1150, 765, 16); paint(ctx, '#ffffff', 3);
    if (lt > b.at.d13 + 0.4) { const h = anchors(DV, dO).handR; e.thesis(ctx, h[0] + 10, h[1] - 10, 0.5, 0.2); }
    const hd = headOf(KL, kO);
    if (flirt) q.flirtFx(ctx, hd[0], hd[1], t, seg(lt, b.at.g13c + D('g13c') * 0.3, b.at.g13c + D('g13c') * 0.3 + 0.4), 0.7);
    ctx.restore();
    if (lt > WINK - 0.05 && lt < WINK + 0.6) q.sparkle(ctx, 960, 300, 40 * Math.sin(seg(lt, WINK, WINK + 0.6) * Math.PI));
    // «ចាញ់ ៣ ដង» with three broken hearts
    const tk = seg(lt, b.at.k13 + D('k13') * 0.5, b.at.k13 + D('k13') * 0.5 + 0.3) * (1 - seg(lt, b.at.g13d + 0.5, b.at.g13d + 0.8));
    if (tk > 0) { e.tag(ctx, 1460, 230, 'ចាញ់ ៣ ដង', tk, { size: 56, col: '#3d3a46', ink: '#ff8fab' }); for (let i = 0; i < 3; i++) { ctx.save(); ctx.translate(1300 + i * 110, 340); const s = ease.back(clamp(tk * 3 - i)) * 0.7; ctx.scale(s, s); e.ICON.broken(ctx); ctx.restore(); } }
    warmLight(ctx, 0.12);
  }, [...b.cues, [WINK, 'sparkle'], [b.at.d13 + 0.2, 'heh'], ...[0, 1, 2].map(i => [b.at.k13 + D('k13') * 0.5 + i * 0.12, 'pop', { f0: 500 - i * 60, f1: 200, gain: 0.4 }]), [len - 0.2, 'music_end', { id: 'm13', how: 'fade', dur: 0.5 }]]);
}

// ============================================================ SCENE 14 — golden hallway: a bear hug; Channy smiles (slow motion, sunflowers)
{
  const b = beats([0.9, 'g14a', 0.2]), HUG = 0.15, GO = b.at.g14a + 0.3, len = b.end + 1.2;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 900, 680, 1.35);
    pl.hallway(ctx, t, { gold: 1 });
    const hug = lt > HUG && lt < GO, w = ease.in(seg(lt, GO, len)), sq = hug ? Math.sin(seg(lt, HUG, HUG + 0.4) * Math.PI) * 0.08 : 0;
    const dO = { x: 760 - w * 900, y: 1010, s: 1.12, facing: w > 0 ? -0.5 : 0.3, pose: w > 0 ? 'walk' : 'stand', ph: t * 2.2, backpack: true, expr: hug ? 'laugh' : 'grin', look: w > 0 ? [-1, 0] : [1, 0], sq: -sq };
    const sO = { x: 1080 - w * 1000, y: 1010, s: 1.1, facing: w > 0 ? -0.5 : -0.3, pose: w > 0 ? 'wave' : 'stand', ph: t * 2.2 + 0.5, backpack: true, phones: 'neck', expr: hug ? 'laugh' : 'grin', look: w > 0 ? [-1, 0] : [-1, 0], sq: -sq };
    pp(ctx, DV, t, dO); pp(ctx, KP, t, sO);
    const kO = { x: hug ? 920 : 1260, y: 1030, s: 1.15, facing: hug ? 0 : -0.3, pose: hug ? 'reach2' : w > 0 ? 'wave' : 'stand', expr: hug ? 'laugh' : 'grin', look: [-1, 0] };
    if (hug) { kO.reach = toLocal(KL, kO, anchors(KP, sO).shR); kO.reachL = toLocal(KL, kO, anchors(DV, dO).shL); }
    pp(ctx, KL, t, kO);
    ctx.restore();
    sfx(ctx, 'SQUEEZE!', 900, 240, lt, HUG + 0.1, { size: 84, fill: '#ff8fab', dur: 1.0 });
    goldHour(ctx, 0.9);
  }, [[0, 'music', { id: 'm14', style: 'warm', gain: 0.2 }], [HUG, 'squish'], [HUG + 0.2, 'heh'], ...b.cues, [GO + 0.1, 'footsteps', { n: 5, gap: 0.35, gain: 0.6 }], [len - 0.3, 'music_end', { id: 'm14', how: 'fade', dur: 0.5 }]]);
}
{
  // slow motion while she speaks: everything moves at 30%, sunflowers fall, a dreamy glow
  const b = beats([1.3, 'c14a', 0.2, 'c14b', 0.5]), STOP = 1.1, PASS = b.end, len = PASS + 1.6;
  take(len, (ctx, lt, t) => {
    const slow = lt > STOP - 0.3 && lt < PASS, st = slow ? t * 0.3 : t;
    ctx.save(); cam(ctx, lerp(1050, 1000, ease.inOut(seg(lt, 0, len))), 690, lerp(1.4, 1.55, ease.inOut(seg(lt, STOP, PASS))));
    pl.hallway(ctx, st, { gold: 1, openB: 1 });
    const arrive = ease.out(seg(lt, 0, STOP)), leave = ease.inOut(seg(lt, PASS, len));
    const cO = { x: lerp(1450, 1180, arrive) - leave * 900, y: 1010, s: 1.08, facing: leave > 0 ? -0.6 : -0.35, pose: arrive < 1 || leave > 0 ? 'walk' : 'hold', ph: st * 1.7, expr: lt > STOP - 0.2 ? 'grin' : 'calm', look: [-1, 0], mouth: talk(CN, t) };
    const kO = { x: 860, y: 1010, s: 1.12, facing: 0.35, pose: 'stand', expr: lt > STOP + 0.2 ? 'surprised' : 'smile', look: [1, 0], t: lt > STOP + 0.2 && lt < PASS ? STOP : t };
    person(ctx, KL, { ...kO, mouth: 0 });
    pp(ctx, CN, st, cO); const h = anchors(CN, cO).handR; q.folder(ctx, h[0] + 8, h[1] - 6, 0.78, 0.12);
    if (lt > b.at.c14a) blush(ctx, KL, kO, seg(lt, b.at.c14a, b.at.c14a + 1));
    ctx.restore();
    goldHour(ctx, 0.9);
    q.dreamGlow(ctx, seg(lt, STOP - 0.3, STOP + 0.4) * (1 - seg(lt, PASS, PASS + 0.5)));
    q.sunflowers(ctx, st, seg(lt, STOP - 0.2, STOP + 0.6) * (1 - seg(lt, PASS + 0.3, PASS + 1.2)));
    if (lt > b.at.c14b + D('c14b')) sfx(ctx, '...!!!', 640, 280, lt, b.at.c14b + D('c14b'), { size: 100, fill: '#ffffff', dur: 1.6 });
  }, [[0, 'footsteps', { n: 3, gap: 0.4, gain: 0.5 }], [STOP - 0.3, 'whoosh_rev', { gain: 0.5 }], [STOP - 0.2, 'music', { id: 'luv5', style: 'love', gain: 0.32, bpm: 72 }], [STOP, 'heartbeat', { n: 4, gain: 0.5 }], ...b.cues, [PASS, 'music_end', { id: 'luv5', how: 'fade', dur: 1.2 }], [PASS + 0.2, 'footsteps', { n: 3, gap: 0.45, gain: 0.4 }]]);
}
{
  const b = beats([0.3, 'g14b', 0.2, 'k14', 0.3]), HOP = 0.25, len = b.end + 0.3;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 760, 640, 1.15);
    pl.hallway(ctx, t, { gold: 1, openB: 1 });
    // far away down the hallway (left), Sopheak turns and waves
    pp(ctx, KP, t, { x: 130, y: 930, s: 0.7, facing: 0.4, pose: lt > b.at.k14 - 0.2 ? 'wave2' : 'walk', ph: t * 2, backpack: true, phones: 'neck', expr: 'laugh', look: [1, 0] });
    const hop = Math.abs(Math.sin(seg(lt, HOP, len - 0.3) * Math.PI * 3)) * 120;
    pp(ctx, KL, t, { x: 900, y: 1030, s: 1.15, facing: -0.2, pose: 'jump', hop, expr: 'laugh', look: [-1, -0.2], sq: hop > 100 ? -0.05 : 0.04 });
    ctx.restore();
    goldHour(ctx, 0.9);
    stars(ctx, HOP, lt, [[660, 260], [1180, 220], [1300, 520], [520, 560]], 1.5);
  }, [[HOP, 'boing'], [HOP + 0.6, 'boing', { gain: 0.7 }], [HOP, 'music', { id: 'm14b', style: 'triumph', gain: 0.24 }], ...b.cues, [len - 0.2, 'music_end', { id: 'm14b', how: 'fade', dur: 0.6 }]]);
}

// ============================================================ SCENE 15 — the timer photo: «ម្នាក់ៗខុសគ្នា តែរួមគ្នាយើងខ្លាំង!» ... «ឆឹក!»
const LINE = [[PS, 260], [LH, 500], [KL, 760], [DV, 985], [KP, 1210], [SM, 1450], [NM, 1690]];
function family(ctx, t, lt, { kx = null, pose = 'heart', wink = false, laugh = false } = {}) {
  for (const [who, x] of LINE) {
    const o = { x: who === KL && kx != null ? kx : x, y: 1040, s: 1.06, facing: (960 - x) * 0.0003, pose, expr: laugh ? 'laugh' : 'grin', look: [0, 0], phones: who === KP ? 'neck' : undefined };
    if (who === KL) { o.expr = wink ? 'wink' : laugh ? 'laugh' : 'grin'; if (kx != null && kx !== x) { o.pose = 'walk'; o.ph = t * 3; o.facing = -0.5; } }
    if (who === KL && kx === x) { o.pose = 'reach'; o.reach = toLocal(KL, o, anchors(DV, { x: 985, y: 1040, s: 1.06 }).shL); }
    if (who === KP) { o.pose = 'reachL'; o.reach = toLocal(KP, o, anchors(DV, { x: 985, y: 1040, s: 1.06 }).shR); }
    pp(ctx, who, t, o);
  }
}
{
  const b = beats([0.4, 'g15a', 0.3]), TIMER = 0.5, RUN = b.at.g15a + D('g15a') * 0.35, IN = b.at.g15a + D('g15a') * 0.85;
  const ch = beats([b.end, 'a15g', 0, 'a15k', 0, 'a15d', 0, 'a15s', 0, 'a15m', 0, 'a15l', 0, 'a15p']);
  const CH = ch.at.a15g, CHEND = CH + Math.max(...['a15g', 'a15k', 'a15d', 'a15s', 'a15m', 'a15l', 'a15p'].map(D));
  const w = beats([CHEND + 0.4, 'g15b']), SNAP = w.at.g15b + D('g15b') + 0.1, len = SNAP + 7.2;
  // the chorus: all seven together (beats() would queue them one after another; put them all at CH)
  const chorus = ['a15g', 'a15k', 'a15d', 'a15s', 'a15m', 'a15l', 'a15p'].map(id => [CH, id, { sub: id === 'a15g' }]);
  take(len, (ctx, lt, t) => {
    const frozen = lt > SNAP, ft = frozen ? t - (lt - SNAP) : t, flt = frozen ? SNAP : lt;
    const pull = ease.inOut(seg(lt, SNAP + 0.5, SNAP + 2.6)), ps = lerp(1, 0.62, pull), py = lerp(0, 50, pull);
    if (frozen) bokeh(ctx, t, '#f2c98a');
    ctx.save();
    if (frozen) { ctx.translate(W / 2, H / 2 + py); ctx.rotate(-0.025 * pull); ctx.scale(ps, ps); ctx.translate(-W / 2, -H / 2); ctx.beginPath(); ctx.rect(0, 0, W, H); ctx.clip(); }
    ctx.save(); cam(ctx, 975, 700, 1.1);
    q.meetingRoom(ctx, ft, { slideN: 3, gold: 1 });
    const runK = ease.inOut(seg(flt, RUN, IN)), kx = flt < RUN ? 1650 : lerp(1650, 760, runK);
    family(ctx, ft, flt, { kx: flt < IN ? kx : 760, pose: flt > CH - 0.3 ? 'heart' : 'stand', wink: flt > w.at.g15b + D('g15b') * 0.5, laugh: flt > CH && flt < w.at.g15b });
    // the tripod in the foreground (right), its timer light blinking faster
    ctx.restore();
    goldHour(ctx, 0.75);
    if (frozen) { ctx.restore(); ctx.save(); ctx.translate(W / 2, H / 2 + py); ctx.rotate(-0.025 * pull); ctx.scale(ps, ps); ctx.translate(-W / 2, -H / 2); ctx.lineWidth = 34; ctx.strokeStyle = '#fffaf0'; ctx.strokeRect(-17, -17, W + 34, H + 34); ctx.lineWidth = 6; ctx.strokeStyle = INK; ctx.strokeRect(-34, -34, W + 68, H + 68); }
    ctx.restore();
    // the camera's self-timer light, blinking faster and faster
    if (!frozen && lt > TIMER) { const r = seg(lt, TIMER, SNAP), on = Math.sin((lt - TIMER) * (8 + r * 30)) > 0; ctx.save(); rrect(ctx, W - 200, 50, 150, 70, 35); ctx.fillStyle = 'rgba(42,38,51,0.75)'; ctx.fill(); circle(ctx, W - 160, 85, 18); ctx.fillStyle = on ? '#ff3b3b' : '#6b6875'; ctx.fill(); text(ctx, 'TIMER', W - 95, 87, { size: 26, font: 'Arial Black', fill: '#ffffff', lw: 0 }); ctx.restore(); }
    // countdown numbers while he runs
    const cd = ['៣', '២', '១']; cd.forEach((n, i) => { const a = b.at.g15a + D('g15a') * (0.45 + i * 0.17), k = seg(lt, a, a + 0.45); if (k > 0 && k < 1) { ctx.save(); ctx.globalAlpha = 1 - k; text(ctx, n, 1500, 330, { size: 200 + k * 120, fill: '#ffd23f', lw: 14 }); ctx.restore(); } });
    // the flash and «ឆឹក!»
    const fl = seg(lt, SNAP, SNAP + 0.5); if (fl > 0 && fl < 1) { ctx.save(); ctx.globalAlpha = 1 - fl; ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
    sfx(ctx, 'ឆឹក!', 1500, 260, lt, SNAP + 0.05, { size: 130, fill: '#ffffff', dur: 1.2 });
    // the closing line, then next time
    banner(ctx, null, 'ម្នាក់ៗខុសគ្នា តែរួមគ្នាយើងខ្លាំង!', 'Each of us is different, but together we\'re strong!', seg(lt, SNAP + 2.2, SNAP + 2.8), '#e8433a', 150);
    const tk = seg(lt, SNAP + 3.6, SNAP + 4.2);
    if (tk > 0) { ctx.save(); ctx.globalAlpha = tk; rrect(ctx, 460, 975, 1000, 80, 40); ctx.fillStyle = 'rgba(42,38,51,0.82)'; ctx.fill(); text(ctx, 'វគ្គក្រោយ៖ ថ្ងៃការពារសារណារបស់ដេវីត...', 960, 1012, { size: 44, fill: '#ffd23f', lw: 0 }); ctx.restore(); }
    const fo = seg(lt, len - 1.0, len); if (fo > 0) { ctx.save(); ctx.globalAlpha = fo; ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
  }, [[0, 'music', { id: 'm15', style: 'warm', gain: 0.2 }], [TIMER, 'alarm_beep', { gain: 0.3 }], ...b.cues, [RUN, 'whoosh_by'], [RUN + 0.1, 'footsteps', { n: 5, gap: 0.16, gain: 0.7 }],
    ...[0, 1, 2].map(i => [b.at.g15a + D('g15a') * (0.45 + i * 0.17), 'tick', { n: 1 }]), ...chorus, ...w.cues, [SNAP, 'shutter'], [SNAP + 0.02, 'music_end', { id: 'm15', how: 'cut' }],
    [SNAP + 0.6, 'music', { id: 'm15b', style: 'triumph', gain: 0.26 }], [SNAP + 2.2, 'title_whoosh'], [SNAP + 3.6, 'pop', { f0: 900, f1: 1300 }], [len - 1.0, 'music_end', { id: 'm15b', how: 'fade', dur: 1.0 }]]);
}
