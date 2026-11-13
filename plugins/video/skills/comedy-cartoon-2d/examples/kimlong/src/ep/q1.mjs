// PART 1 (scenes 1-5): Kimlong arrives, flirts with Channy in the hallway, shouts hello, shakes every hand,
// finds a same-age friend in Sopheak, asks about "the girl next door" and shows off a 30-second office film.
import { W, H, INK, TAU, paint, circle, oval, rrect, poly, text, clamp, lerp, seg, ease, hash } from '../core.mjs';
import { take, beats, cam, talk, shk } from '../kit.mjs';
import { person, anchors, toLocal, CAST, camera } from '../people.mjs';
import * as pl from '../places.mjs';
import * as fx from '../fx.mjs';
import * as e from '../ep6.mjs';
import * as q from '../ep7.mjs';
import { D, KP, DV, SM, NM, LH, PS, KL, CN, pp, warmLight, sweat, stars, headOf, atHead, blush, titleKh, thoughtBubble, sfx, room, monitor, deskFront, bokeh, editScreen } from './common.mjs';

// Channy's folder sits in her right hand
const withFolder = (ctx, o) => { const h = anchors(CN, o).handR; q.folder(ctx, h[0] + 8, h[1] - 6, 0.78 * (o.s || 1), 0.12); };
// loud-voice rings coming out of Kimlong's mouth (dir -1: to the left)
const shoutRings = (ctx, hd, t, k, dir = -1, s = 1) => { if (k <= 0) return; ctx.save(); ctx.lineCap = 'round'; for (let i = 0; i < 3; i++) { const p = (t * 2.4 + i / 3) % 1, r = (70 + p * 230) * s; ctx.globalAlpha = (1 - p) * k; ctx.beginPath(); ctx.arc(hd[0], hd[1] + 30 * s, r, dir < 0 ? Math.PI * 0.8 : -Math.PI * 0.2, dir < 0 ? Math.PI * 1.2 : Math.PI * 0.2); paint(ctx, null, 9 * s, '#ffd23f'); } ctx.restore(); };

// ============================================================ SCENE 1 — the hallway: a new face, and a girl with a folder
{
  const b = beats([3.3, 'n1a', 0.3, 'n1b', 0.2]), len = b.end + 0.3, OUT = b.at.n1b + D('n1b') * 0.5;
  take(len, (ctx, lt, t) => {
    const k = ease.inOut(seg(lt, 0, len));
    ctx.save(); cam(ctx, lerp(880, 980, k), 560, lerp(1.0, 1.08, k));
    pl.hallway(ctx, t, { openB: ease.out(seg(lt, OUT - 0.5, OUT)), gold: 0.25 });
    if (lt > OUT - 0.2) { const cw = ease.out(seg(lt, OUT - 0.2, len)), cO = { x: lerp(1380, 1300, cw), y: 1010, s: 1.08, facing: -0.35, pose: cw < 1 ? 'walk' : 'hold', ph: t * 1.6, expr: 'calm', look: [-0.6, 0.3] }; pp(ctx, CN, t, cO); withFolder(ctx, cO); }
    const w = ease.out(seg(lt, 0.5, len - 0.1)), kO = { x: lerp(-220, 720, w), y: 1010, s: 1.08, facing: 0.5, pose: w < 0.97 ? 'walk' : 'stand', ph: t * 2.1, expr: lt > OUT + 0.3 ? 'surprised' : 'grin', look: lt > OUT ? [1, 0] : [0.5, -0.3] };
    pp(ctx, KL, t, kO);
    ctx.restore();
    titleKh(ctx, lt, 0.2, 3.0, 'វគ្គទី ៧៖ គីមឡុង ស្ដេចញ៉ែ', 'Episode 7: Kimlong, the King of Flirting');
    warmLight(ctx, 0.12);
  }, [[0, 'room_tone', { dur: len }], [0.2, 'sting_title'], [0.3, 'music', { id: 'm1', style: 'vamp', gain: 0.22, bpm: 160 }], [0.6, 'footsteps', { n: 8, gap: 0.42 }], [OUT - 0.5, 'creak', { i: 2 }], ...b.cues, [len - 0.1, 'music_end', { id: 'm1', how: 'cut' }]]);
}
{
  const b = beats([1.3, 'g1a', 0.15, 'g1b', 0.35, 'c1a', 0.2, 'g1c', 0.35, 'c1b', 0.1]);
  const FIX = 0.25, LEAN = 1.05, PASS = b.end + 0.25, GONE = PASS + 1.4, len = GONE + 1.5;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 1000, 690, 1.5);
    pl.hallway(ctx, t, { openB: 1, gold: 0.25 });
    // Channy walks up, stops, raises an eyebrow, swallows a laugh and walks on past him
    const arrive = ease.out(seg(lt, 0, 0.9)), leave = ease.inOut(seg(lt, PASS, GONE)), walking = arrive < 1 || (leave > 0 && leave < 1);
    const hide = lt > b.at.c1b - 0.15 && lt < PASS + 0.2;
    const cO = { x: lerp(1300, 1200, arrive) - leave * 1200, y: 1010, s: 1.08, facing: leave > 0 ? -0.6 : -0.3, pose: walking ? 'walk' : hide ? 'chin' : 'hold', ph: t * 1.7, expr: lt > b.at.c1a - 0.3 && lt < b.at.c1b - 0.15 ? 'thinking' : hide ? 'grin' : 'calm', look: leave > 0 ? [-1, 0] : [-1, 0.1] };
    // Kimlong: frozen, then a quick hair fix, then the cool lean on the door frame
    const fixing = lt > FIX && lt < LEAN, leaning = lt >= LEAN, gone = lt > GONE - 0.1, slide = ease.in(seg(lt, GONE + 0.1, GONE + 0.6));
    const ex = lt < FIX ? 'surprised' : fixing ? 'grin' : lt < b.at.g1b ? 'wink' : lt < b.at.c1a ? 'love' : lt > b.at.g1c && lt < b.at.c1b ? 'grin' : gone ? 'worried' : 'wink';
    const kO = { x: 820, y: 1010 + slide * 40, s: 1.08, facing: 0.4, rot: leaning ? -0.07 + slide * 0.05 : 0, pose: fixing ? 'fixHair' : leaning ? (lt > b.at.g1c && lt < b.at.g1c + D('g1c') + 0.2 ? 'thumbs' : 'leanWall') : 'stand', expr: ex, look: leave > 0.3 ? [-1, 0] : [1, 0], sq: lt < FIX ? Math.sin(seg(lt, 0, FIX) * Math.PI) * 0.06 : slide * 0.08 };
    if (leave > 0.45) { pp(ctx, CN, t, cO); withFolder(ctx, cO); pp(ctx, KL, t, kO); } else { pp(ctx, KL, t, kO); pp(ctx, CN, t, cO); withFolder(ctx, cO); }
    const hd = headOf(KL, kO);
    q.flirtFx(ctx, hd[0], hd[1], t, seg(lt, b.at.g1b - 0.2, b.at.g1b + 0.5) * (1 - seg(lt, b.at.c1a, b.at.c1a + 0.4)), 0.85);
    if (lt > b.at.g1a && lt < b.at.g1a + 0.6) q.sparkle(ctx, hd[0] + 50, hd[1] - 20, 30 * Math.sin(seg(lt, b.at.g1a, b.at.g1a + 0.6) * Math.PI));
    if (fixing) for (let i = 0; i < 3; i++) q.sparkle(ctx, hd[0] + (i - 1) * 60, hd[1] - 120 + Math.sin(t * 12 + i) * 10, 14);
    ctx.restore();
    if (lt < FIX + 0.5) sfx(ctx, '!', 980, 220, lt, 0.05, { size: 140, fill: '#ff5c8a', dur: 0.6 });
    q.nameCard(ctx, 1290, 190, 'ចាន់នី', 'បុគ្គលិកក្រុមហ៊ុនបងស្រីលាងហាក់', seg(lt, b.at.c1a - 0.5, b.at.c1a) * (1 - seg(lt, PASS, PASS + 0.3)), { size: 46, icon: 'heart' });
    q.plok(ctx, 760, 300, lt, GONE - 0.05);
    warmLight(ctx, 0.12);
  }, [[FIX, 'zip_up', { gain: 0.5 }], [FIX + 0.3, 'sparkle'], [LEAN - 0.4, 'music', { id: 'luv1', style: 'love', gain: 0.32 }], [b.at.g1a + 0.1, 'sparkle', { gain: 0.6 }], ...b.cues, [PASS + 0.1, 'footsteps', { n: 3, gap: 0.42, gain: 0.6 }],
    [GONE - 0.1, 'record_scratch'], [GONE - 0.08, 'music_end', { id: 'luv1', how: 'cut' }], [GONE + 0.05, 'pop', { f0: 520, f1: 110, gain: 0.6 }], [GONE + 0.15, 'slide_down_short', { gain: 0.6 }], [GONE + 0.5, 'sad_trombone', { gain: 0.45 }]]);
}

// ============================================================ SCENE 2 — the door bursts open: "HELLO!!!"
{
  const b = beats([0.75, 'g2a', 0.15, 'g2b', 0.3, 'm2', 0.25, 's2']), BAM = 0.25, len = b.end + 0.9;
  take(len, (ctx, lt, t) => {
    const loud = lt > b.at.g2a && lt < b.at.m2 - 0.1, [sx, sy] = loud ? shk(t, 6) : [0, 0];
    ctx.save(); cam(ctx, 980 + sx, 650 + sy, 1.15);
    room(ctx, t, { door: ease.out(seg(lt, BAM - 0.08, BAM + 0.08)), hour: 8.3 });
    const jk = seg(lt, BAM + 0.05, BAM + 0.55), hop = jk < 1 ? Math.sin(jk * Math.PI) * 70 : 0, scared = lt > BAM && lt < b.at.g2b + 0.3;
    const row = { [SM]: 400, [NM]: 660, [DV]: 920, [KP]: 1170 };
    for (const [who, x] of Object.entries(row)) {
      const o = { x, y: 1040, hop, s: 1.1, facing: 0.45, pose: scared ? 'panic' : 'stand', expr: scared ? 'surprised' : 'smile', look: [1, 0], sq: scared ? 0.04 : 0 };
      o.y -= hop;
      if (who === KP) { o.phones = lt > b.at.g2b - 0.2 ? 'on' : 'neck'; if (lt > b.at.g2b - 0.4 && lt < b.at.g2b + 0.1) o.pose = 'ears'; else if (lt > b.at.g2b) { o.pose = 'stand'; o.expr = 'calm'; o.look = [1, 0]; } }
      if (who === NM && lt > b.at.m2 - 0.1 && lt < b.at.s2) { o.pose = 'ears'; o.expr = 'tired'; }
      if (who === SM && lt > b.at.s2 - 0.1) { o.pose = 'present'; o.expr = 'grin'; }
      if (who === DV && lt > b.at.g2b + 0.3) { o.expr = 'grin'; }
      pp(ctx, who, t, o);
    }
    const w = ease.out(seg(lt, BAM, BAM + 0.55)), kO = { x: lerp(1860, 1500, w), y: 1040, s: 1.12, facing: -0.35, pose: lt < b.at.m2 ? 'cheer' : 'wave', expr: 'grin', look: [-1, 0], sq: loud ? Math.sin(t * 30) * 0.02 : 0 };
    pp(ctx, KL, t, kO);
    shoutRings(ctx, headOf(KL, kO), t, loud ? 1 : 0, -1, 1.1);
    ctx.restore();
    sfx(ctx, 'BAM!', 1700, 260, lt, BAM, { size: 110, fill: '#ffd23f', rot: 0.1 });
    q.nameCard(ctx, 1240, 210, 'គីមឡុង (១៩ ឆ្នាំ)', 'អ្នកថតវីដេអូ & ស្ដេចញ៉ែ', seg(lt, b.at.g2b, b.at.g2b + 0.4) * (1 - seg(lt, len - 0.4, len)), { icon: 'cam', icon2: 'cool', size: 50 });
    warmLight(ctx, 0.1);
  }, [[0, 'room_tone', { dur: len }], [BAM, 'door_bam'], [BAM + 0.05, 'boing', { gain: 0.5 }], [BAM + 0.1, 'music', { id: 'm2', style: 'upbeat', gain: 0.26, bpm: 120 }], ...b.cues, [b.at.g2b + 0.1, 'pop', { f0: 900, f1: 1300 }], [b.at.s2 + D('s2') - 0.1, 'applause', { gain: 0.35, dur: 1.2 }]]);
}

// ============================================================ SCENE 3 — sampeah, then handshakes that are far too strong; a same-age fist bump
{
  const b = beats([0.35, 'g3a', 0.1, 'g3b', 0.15, 'd3', 0.3]), len = b.end;
  const ROW = [[SM, 200], [NM, 650], [DV, 1100]], g3b = b.at.g3b, d = D('g3b');
  const shakeAt = [g3b - 0.15, g3b + d * 0.33, g3b + d * 0.66];
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 790, 700, 1.3);
    room(ctx, t, { hour: 8.35 });
    let i = -1; shakeAt.forEach((a, j) => { if (lt > a) i = j; });
    const hard = i === 2 && lt < b.at.d3 + D('d3') + 0.1;
    // Kimlong slides from shake to shake
    const kx = i < 0 ? lerp(1560, 1380, ease.out(seg(lt, 0, 0.5))) : lerp(i === 0 ? 1380 : ROW[i - 1][1] + 230, ROW[i][1] + 230, ease.inOut(seg(lt, shakeAt[i], shakeAt[i] + 0.2)));
    const kO = { x: kx, y: 1050, s: 1.12, facing: -0.35, pose: i < 0 ? 'sampeah' : 'reachL', expr: hard ? 'laugh' : 'grin', look: [-1, 0] };
    for (const [j, [who, x]] of ROW.entries()) {
      const o = { x, y: 1050, s: who === DV ? 1.12 : 1.1, facing: 0.4, pose: i < 0 ? 'sampeah' : 'stand', expr: 'smile', look: [1, 0] };
      if (j === i) {
        const amp = hard ? 30 : 16, base = anchors(who, o).chest, M = [(x + kx) / 2, base[1] + 20 + Math.sin(t * 30) * amp];
        if (hard) { const [jx, jy] = shk(t, 9, 3); o.x += jx; o.rot = Math.sin(t * 31) * 0.05; o.sq = Math.sin(t * 29) * 0.05; o.expr = 'surprised'; M[0] += jx * 0.5; }
        o.pose = 'reach'; o.reach = toLocal(who, o, M); kO.reach = toLocal(KL, kO, M);
      } else if (j < i) { o.pose = 'stand'; o.expr = 'worried'; o.look = [0.6, 0.6]; o.sq = Math.sin(t * 18 + j) * 0.015; }
      pp(ctx, who, t, o);
    }
    pp(ctx, KL, t, kO);
    if (hard) { const hd = headOf(DV, { x: 1100, y: 1050, s: 1.12, facing: 0.4 }); for (let k = 0; k < 4; k++) { ctx.save(); ctx.globalAlpha = 0.6; ctx.lineCap = 'round'; ctx.beginPath(); const yy = hd[1] - 60 + k * 50; ctx.moveTo(hd[0] - 150, yy); ctx.lineTo(hd[0] - 120, yy + 10); paint(ctx, null, 6); ctx.moveTo(hd[0] + 120, yy); ctx.lineTo(hd[0] + 150, yy + 10); paint(ctx, null, 6); ctx.restore(); } }
    ctx.restore();
    if (i >= 0 && !hard) sfx(ctx, 'SHAKE!', 420 + i * 560, 200, lt, shakeAt[i] + 0.15, { size: 70, fill: '#ffd23f', dur: 0.6 });
    if (hard) sfx(ctx, 'SHAKE SHAKE SHAKE!', 1100, 240, lt, shakeAt[2] + 0.2, { size: 74, fill: '#ff8fab', dur: 2.0 });
    warmLight(ctx, 0.1);
  }, [...b.cues, ...shakeAt.map((a, j) => [a + 0.15, 'squeak_rubber', { gain: 0.4 + j * 0.15 }]), [shakeAt[2] + 0.2, 'lid_wobble', { gain: 0.6, dur: D('d3') }]]);
}
{
  const b = beats([0.3, 'g3c', 0.25, 'k3a', 0.25, 'g3d', 0.2, 'k3b', 0.1]), BUMP = b.end + 0.15, len = BUMP + 2.4;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 1110, 620, 1.32);
    room(ctx, t, { hour: 8.4 });
    const off = lt > b.at.k3a - 0.35, lifting = lt > b.at.k3a - 0.45 && lt < b.at.k3a - 0.05, bump = lt > BUMP - 0.15;
    const kO = { x: 960, y: 1060, s: 1.14, facing: 0.35, phones: off ? 'neck' : 'on', pose: lifting ? 'ears' : bump ? 'bump' : 'stand', expr: lt > b.at.g3d ? 'grin' : 'smile', look: [1, 0] };
    const same = lt > b.at.g3d && lt < b.at.g3d + 0.5, hopK = Math.sin(seg(lt, b.at.g3d, b.at.g3d + 0.45) * Math.PI);
    const gO = { x: 1270, y: 1060 - hopK * 50, s: 1.12, facing: 0.35, mirror: true, pose: bump ? 'bump' : lt < b.at.k3a ? 'chin' : lt > b.at.g3d ? 'point' : 'stand', expr: same ? 'surprised' : lt > b.at.k3a + D('k3a') ? 'laugh' : 'smile', look: [1, 0] };
    pp(ctx, KP, t, kO); pp(ctx, KL, t, gO);
    // «១៩» over both heads when they notice
    const nk = seg(lt, b.at.g3d - 0.1, b.at.g3d + 0.3) * (1 - seg(lt, BUMP - 0.3, BUMP));
    if (nk > 0) for (const [who, o] of [[KP, kO], [KL, gO]]) { const hd = headOf(who, o); e.tag(ctx, hd[0], hd[1] - 175, '១៩', nk, { size: 52, col: '#ffd23f', ink: '#2d3a6b' }); }
    const bk = seg(lt, BUMP, BUMP + 0.5); if (bk > 0 && bk < 1) fx.impact(ctx, 1112, anchors(KP, kO).handR[1], 110, bk, { col: '#ffd23f' });
    ctx.restore();
    sfx(ctx, 'ប៉ុក!', 1100, 420, lt, BUMP, { size: 120, fill: '#ffd23f', dur: 1.0 });
    e.tag(ctx, 960, 180, 'អាយុដូចគ្នា = មិត្តភ្លាម!', seg(lt, BUMP + 0.2, BUMP + 0.6), { icon: 'fist', size: 62, col: '#fff6e6', ink: '#e8433a' });
    warmLight(ctx, 0.1);
  }, [[b.at.k3a - 0.4, 'zip_up', { gain: 0.4 }], ...b.cues, [b.at.g3d + 0.05, 'boing', { gain: 0.5 }], [BUMP, 'highfive'], [BUMP + 0.02, 'bonk', { gain: 0.5 }], [BUMP + 0.3, 'ta_da_small'], [len - 0.3, 'music_end', { id: 'm2', how: 'fade', dur: 0.6 }]]);
}

// ============================================================ SCENE 4 — non-stop questions about the girl next door; two facepalms
const ASK = { g4a: 'ឈ្មោះអី?', g4b: 'មានសង្សារ?', g4c: 'កាហ្វេ ឬ តែ?' };
{
  const b = beats([0.3, 'g4a', 0.1, 'g4b', 0.1, 'g4c', 0.3]), len = b.end;
  take(len, (ctx, lt, t) => {
    const z = lt < b.at.g4b ? 1.3 : lt < b.at.g4c ? 1.5 : 1.72;
    ctx.save(); cam(ctx, 930, 740 - (z - 1.3) * 160, z);
    room(ctx, t, { hour: 8.6 });
    const kO = { x: 880, y: 1050, s: 1.12, facing: 0.35, pose: 'point', expr: lt > b.at.g4b ? 'love' : 'grin', look: [1, -0.2] };
    pp(ctx, KL, t, kO);
    ctx.restore();
    // a dreamy little Channy in a thought bubble
    thoughtBubble(ctx, 1440, 330, seg(lt, b.at.g4a, b.at.g4a + 0.4), () => { ctx.save(); oval(ctx, 0, 0, 146, 100); ctx.clip(); ctx.fillStyle = '#ffe3ec'; ctx.fillRect(-150, -110, 300, 220); person(ctx, CN, { x: 0, y: atHead(CN, { s: 0.85, facing: -0.2 }, 6), s: 0.85, facing: -0.2, expr: 'calm', t, look: [-0.5, 0] }); ctx.restore(); for (const [x, y] of [[-110, -60], [110, 50]]) { ctx.save(); ctx.translate(x, y); ctx.scale(0.3, 0.3); e.ICON.heart(ctx); ctx.restore(); } }, 1, 1.1);
    Object.entries(ASK).forEach(([id, s], i) => e.tag(ctx, 1460, 640 + i * 130, s, seg(lt, b.at[id], b.at[id] + 0.3), { size: 56, rot: (i % 2 ? 0.04 : -0.04), col: '#fff6e6', ink: '#e8433a' }));
    warmLight(ctx, 0.1);
  }, [[0, 'music', { id: 'm4', style: 'muzak', gain: 0.24 }], ...b.cues, ...Object.keys(ASK).map(id => [b.at[id], 'whoosh', { gain: 0.35 }]), ...Object.keys(ASK).map(id => [b.at[id] + 0.1, 'pop', { f0: 1000, f1: 1500 }])]);
}
{
  const b = beats([0.85, 's4', 0.2]), SLAP = 0.3, len = b.end + 0.2;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 965, 700, 1.5);
    room(ctx, t, { hour: 8.6 });
    const palm = lt > SLAP;
    pp(ctx, SM, t, { x: 780, y: 1050, s: 1.12, facing: 0.2, pose: palm ? 'facepalm' : 'stand', expr: 'tired', look: [0.5, 0] });
    pp(ctx, NM, t, { x: 1150, y: 1050, s: 1.12, facing: -0.2, pose: palm ? 'facepalm' : 'stand', expr: 'tired', look: [-0.5, 0] });
    ctx.restore();
    sfx(ctx, 'SLAP!', 960, 260, lt, SLAP, { size: 110, fill: '#ffffff', dur: 0.8 });
    warmLight(ctx, 0.1);
  }, [[SLAP, 'facepalm_slap'], [SLAP + 0.04, 'facepalm_slap', { gain: 0.8 }], ...b.cues]);
}
{
  const b = beats([0.2, 'd4', 0.2]), CROWN = b.at.d4 + D('d4') * 0.62, len = b.end + 1.2;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 900, 720, 1.32);
    room(ctx, t, { hour: 8.6 });
    pp(ctx, DV, t, { x: 470, y: 1050, s: 1.12, facing: 0.35, pose: 'belly', expr: 'laugh', look: [1, 0], sq: Math.sin(t * 20) * 0.02 });
    pp(ctx, KP, t, { x: 730, y: 1050, s: 1.12, facing: 0.35, pose: 'belly', expr: 'laugh', phones: 'neck', look: [1, 0], sq: Math.sin(t * 22 + 1) * 0.02 });
    const crowned = lt > CROWN + 0.35, kO = { x: 1320, y: 1050, s: 1.12, facing: -0.3, pose: crowned ? 'chest' : 'stand', expr: crowned ? 'wink' : 'surprised', look: [-1, -0.3] };
    pp(ctx, KL, t, kO);
    const hd = headOf(KL, kO), dk = ease.in(seg(lt, CROWN, CROWN + 0.35)), bounce = Math.sin(seg(lt, CROWN + 0.35, CROWN + 0.7) * Math.PI) * 18;
    if (lt > CROWN) { ctx.save(); ctx.translate(hd[0] + 6, lerp(-200, hd[1] - 128, dk) - bounce); ctx.rotate(-0.12); ctx.scale(1.25, 1.25); e.ICON.crown(ctx); ctx.restore(); }
    if (crowned) stars(ctx, CROWN + 0.4, lt, [[hd[0] - 150, hd[1] - 150], [hd[0] + 150, hd[1] - 120], [hd[0] + 120, hd[1] + 60]]);
    ctx.restore();
    warmLight(ctx, 0.1);
  }, [...b.cues, [CROWN, 'slide_down_short', { gain: 0.4 }], [CROWN + 0.35, 'register_ding'], [CROWN + 0.45, 'sparkle'], [len - 0.3, 'music_end', { id: 'm4', how: 'fade', dur: 0.5 }]]);
}

// ============================================================ SCENE 5 — the desk next door, and the 30-second office film
const welcome = (ctx, x, y, w, h) => { ctx.fillStyle = '#fff6e6'; ctx.fillRect(x, y, w, h); text(ctx, 'សូមស្វាគមន៍!', x + w / 2, y + h * 0.45, { size: 24, fill: '#e8433a', lw: 0 }); for (let i = 0; i < 5; i++) { circle(ctx, x + 20 + i * 26, y + h * 0.8, 5); ctx.fillStyle = ['#ff5c8a', '#3fb3ff', '#46c34f', '#ffd23f', '#a07bff'][i]; ctx.fill(); } };
{
  const b = beats([0.4, 'k5a', 0.15, 'k5b', 0.3, 'g5a', 0.2]), len = b.end + 0.3;
  take(len, (ctx, lt, t) => {
    ctx.save(); cam(ctx, 1000, 700, 1.28);
    room(ctx, t, { hour: 9.2 });
    monitor(ctx, 380, { screen: editScreen(0.5) }); monitor(ctx, 1100, { screen: welcome });
    deskFront(ctx, 520); deskFront(ctx, 1240);
    rrect(ctx, 1170, 690, 140, 40, 6); paint(ctx, '#fff6e6', 4); text(ctx, 'គីមឡុង', 1240, 712, { size: 26, fill: '#e8433a', lw: 0 });
    pp(ctx, KP, t, { x: 800, y: 1080, s: 1.18, facing: 0.45, pose: lt < b.at.k5b ? 'present' : 'thumbs', phones: 'neck', expr: 'grin', look: [1, 0] });
    pp(ctx, KL, t, { x: 1560, y: 1080, s: 1.18, facing: lt > b.at.g5a - 0.2 ? -0.35 : 0.3, pose: lt > b.at.g5a - 0.1 ? 'thumbs' : 'stand', mirror: lt > b.at.g5a - 0.1, expr: lt > b.at.k5a + 0.4 ? 'grin' : 'surprised', look: lt > b.at.g5a - 0.2 ? [1, 0] : [0.6, -0.3] });
    ctx.restore();
    warmLight(ctx, 0.1);
  }, [[0, 'music', { id: 'm5', style: 'warm', gain: 0.24 }], [0, 'room_tone', { dur: len }], ...b.cues, [b.at.k5a + 0.3, 'pop', { f0: 900, f1: 1200 }]]);
}
// what Kimlong's camera sees as he films the office: everybody poses
{
  const len = 2.8;
  take(len, (ctx, lt, t) => {
    const [jx, jy] = shk(t, 3, 5), k = ease.inOut(seg(lt, 0, len));
    ctx.save(); cam(ctx, lerp(520, 1400, k) + jx, 560 + jy, 1.3);
    room(ctx, t, { hour: 9.2 });
    pp(ctx, SM, t, { x: 420, y: 1050, s: 1.1, facing: 0, pose: 'wave', expr: 'grin', look: [0, 0] });
    pp(ctx, NM, t, { x: 760, y: 1050, s: 1.1, facing: 0, pose: 'thumbs', expr: 'grin', look: [0, 0] });
    pp(ctx, DV, t, { x: 1080, y: 1050, s: 1.12, facing: 0, pose: 'cheer', expr: 'laugh', look: [0, 0] });
    pp(ctx, KP, t, { x: 1400, y: 1050, s: 1.1, facing: 0, pose: 'heart', phones: 'neck', expr: 'grin', look: [0, 0] });
    ctx.restore();
    q.viewfinder(ctx, t, lt);
  }, [[0, 'ping', { gain: 0.4 }], [0.1, 'whoosh', { gain: 0.3, dur: 2.4 }], [1.2, 'shutter', { gain: 0.3 }]]);
}
// the camera's screen: a cinematic little film; five heads lean in
function clip(ctx, x, y, w, h, t, p) {
  ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
  const g = ctx.createLinearGradient(0, y, 0, y + h); g.addColorStop(0, '#ff9a5a'); g.addColorStop(0.6, '#ffd08a'); g.addColorStop(1, '#6b4a7a'); ctx.fillStyle = g; ctx.fillRect(x, y, w, h);
  circle(ctx, x + w * 0.7, y + h * 0.5, h * 0.16); ctx.fillStyle = '#fff3c4'; ctx.fill();
  for (let i = 0; i < 9; i++) { const bw = w * 0.09, bh = h * (0.25 + hash(i) * 0.4), bx = x + (i * w * 0.12 - p * w * 0.15) % (w * 1.08); ctx.fillStyle = '#3d2c4e'; ctx.fillRect(bx, y + h * 0.82 - bh, bw, bh); ctx.fillStyle = 'rgba(255,230,140,0.7)'; for (let r = 0; r < 4; r++) ctx.fillRect(bx + bw * 0.25, y + h * 0.82 - bh + 10 + r * bh * 0.2, bw * 0.18, 6); }
  ctx.fillStyle = '#2a1f33'; ctx.fillRect(x, y + h * 0.82, w, h * 0.18);
  ctx.fillStyle = '#000'; ctx.fillRect(x, y, w, h * 0.1); ctx.fillRect(x, y + h * 0.9, w, h * 0.1);
  text(ctx, 'OFFICE  ·  ៣០ វិនាទី', x + w / 2, y + h * 0.3, { size: h * 0.1, fill: '#ffffff', lw: 0 });
  ctx.fillStyle = 'rgba(255,255,255,0.35)'; ctx.fillRect(x + 20, y + h * 0.95, w - 40, 5); ctx.fillStyle = '#ff3b3b'; ctx.fillRect(x + 20, y + h * 0.95, (w - 40) * p, 5);
  ctx.restore();
}
{
  const b = beats([0.3, 'g5b', 0.3, 'm5', 0.2]), WOW = b.at.m5 - 0.15, len = b.end + 0.7;
  take(len, (ctx, lt, t) => {
    bokeh(ctx, t, '#e9c993');
    const lean = ease.out(seg(lt, 0.1, 0.8)), wow = lt > WOW;
    const heads = [[NM, 300, 0.5, 360], [SM, 1620, -0.5, 380], [DV, 640, 0.25, 330], [KP, 1280, -0.25, 330], [KL, 960, 0, 290]];
    for (const [who, x, f, hy] of heads) {
      const o = { x: x + (960 - x) * 0.06 * lean, s: who === SM ? 2.0 : 1.6, facing: f, pose: 'stand', expr: who === KL ? (lt > b.at.m5 ? 'wink' : 'grin') : wow ? (lt > b.at.m5 + 0.8 ? 'grin' : 'surprised') : 'smile', look: [0, 0.9], phones: who === KP ? 'neck' : undefined, tilt: (960 - x) * 0.0002 * lean, camera: false };
      o.y = atHead(who, { ...o, x: 0 }, hy + 30 * lean);
      pp(ctx, who, t, o);
    }
    // the camera back with its flip screen, Kimlong's hands on either side
    rrect(ctx, 520, 600, 880, 520, 40); paint(ctx, '#2a2730', 8);
    rrect(ctx, 570, 640, 780, 440, 16); paint(ctx, '#111', 5);
    clip(ctx, 586, 656, 748, 408, t, clamp(lt / len));
    for (const k of [-1, 1]) { circle(ctx, 960 + k * 470, 860, 46); paint(ctx, CAST.kimlong.skin, 6); }
    if (wow) for (let i = 0; i < 5; i++) q.sparkle(ctx, 560 + i * 200, 610 + (i % 2) * 40 + Math.sin(t * 8 + i) * 8, 22 * ease.back(seg(lt, WOW + i * 0.08, WOW + 0.4 + i * 0.08)));
    sfx(ctx, 'WOW!', 1650, 300, lt, WOW, { size: 120, fill: '#ffd23f', dur: 1.2 });
  }, [...b.cues, [WOW, 'sparkle'], [WOW + 0.1, 'applause', { gain: 0.3, dur: 1.0 }], [len - 0.3, 'music_end', { id: 'm5', how: 'fade', dur: 0.6 }]]);
}
