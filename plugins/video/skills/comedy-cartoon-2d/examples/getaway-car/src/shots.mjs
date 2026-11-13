// GETAWAY CAR — the example film: shot list, staging, camera, and audio cue markers.
import { W, H, C, INK, LW, TAU, paint, circle, oval, rrect, poly, smooth, hose, text, clamp, lerp, seg, ease, onTwos, hash, jit, wobble } from './core.mjs';
import { shot, setShift, duration, cam, shk, P, arc, titleCard, perspStreet, radialLines } from './kit.mjs';
import { benny, marge, copBike, car, carFront, duck, bag, bill, fries, hand, drop } from './chars.mjs';
import * as bg from './bg.mjs';
import * as fx from './fx.mjs';

// ---------------------------------------------------------------- helpers
const flick = t => (hash(Math.floor(t * 9) * 3.7) > 0.8 ? 0 : 1); // the one bad headlight

// One of Marge's long legs poking out of the rear window: knee up, striped sock, pointy shoe.
function margeLeg(ctx, t, i, amt, kick) {
  const kk = Math.sin(t * 13 + i * 2.2) * 10 * kick;
  const base = [-128 + i * 8, -186 + i * 14];
  const knee = P(base, [-206 + i * 10, -256 + i * 34 + kk * 0.3], amt);
  const foot = P(base, [-288 + i * 14, -212 + i * 40 + kk], amt);
  const col = i ? C.black : C.blackL;
  hose(ctx, [base, knee], 12, col, 5); hose(ctx, [knee, foot], 12, col, 5);
  const a = Math.atan2(foot[1] - knee[1], foot[0] - knee[0]);
  ctx.save(); ctx.translate(foot[0], foot[1]); ctx.rotate(a);
  rrect(ctx, -22, -9, 22, 18, 4); paint(ctx, '#fff', 4);
  ctx.fillStyle = C.red; ctx.fillRect(-18, -7, 5, 14); ctx.fillRect(-9, -7, 5, 14);
  ctx.rotate(-a + (i ? 0.3 : -0.1));
  ctx.beginPath(); ctx.moveTo(-6, -10); ctx.quadraticCurveTo(-30, -14, -40, 4); ctx.quadraticCurveTo(-20, 10, 4, 8); ctx.closePath(); paint(ctx, INK, 4);
  ctx.restore();
}
// Benny + Marge inside the car. Returns {crew, outside} callbacks for car().
function crew(o = {}) {
  const { t = 0, bE = 'worried', mE = 'smirk', bL = [1, 0], mL = [1, 0], sweat = 0.7, swapped = false, legs = 1, reach = null, held = 0, bPose = 'drive', mPose = 'stand', mHeadRot = 0.22, benny: hasB = true, marge: hasM = true, bennyLegs = 0, kick = 1 } = o;
  return {
    crew: ctx => {
      if (!swapped) {
        if (hasM) marge(ctx, { x: -96, y: 4, s: 0.6, pose: mPose, expr: mE, look: mL, t, headRot: mHeadRot });
        if (hasM && o.peel) bg.bananaPeel(ctx, -80, -222, 0.8, 0.15);
        if (hasB) {
          ctx.beginPath(); ctx.ellipse(106, -150, 7, 26, 0.25, 0, TAU); paint(ctx, null, 6, '#2a2a30');
          benny(ctx, { x: 46, y: -84, s: 0.6, pose: bPose, expr: bE, look: bL, sweat, t, wheel: [94, -112], holding: o.holding });
        }
      } else {
        if (hasB) benny(ctx, { x: -86, y: -88, s: 0.6, pose: bPose === 'drive' ? 'stand' : bPose, expr: bE, look: bL, sweat, t, ph: t * 2 });
        if (hasM) {
          ctx.beginPath(); ctx.ellipse(84, -168, 7, 26, 0.25, 0, TAU); paint(ctx, null, 6, '#2a2a30');
          marge(ctx, { x: -14, y: -26, s: 0.6, pose: 'steer', expr: mE, look: mL, t, headRot: o.mHeadRot ?? 0 });
        }
      }
    },
    outside: ctx => {
      if (hasM && legs > 0) {
        if (!swapped) for (let i = 0; i < 2; i++) margeLeg(ctx, t, i, legs, kick);
      }
      if (hasB && (swapped || bennyLegs > 0)) {
        for (let i = 0; i < 2; i++) {
          const kk = Math.sin(t * 16 + i * Math.PI) * 6;
          const base = [-124, -176 + i * 10], foot = [-196, -186 + i * 22 + kk];
          hose(ctx, [base, foot], 12, C.navyD, 5);
          oval(ctx, foot[0] - 6, foot[1], 12, 7); paint(ctx, INK, 0);
        }
      }
      if (reach) {
        const sh = [-96, -176], tg = reach;
        hose(ctx, [sh, [lerp(sh[0], tg[0], 0.5), Math.min(sh[1], tg[1]) - 30], tg], 9, C.black, 5);
        for (let i = 0; i < held; i++) bill(ctx, tg[0] - 6 + i * 5, tg[1] - 10 - i * 4, 0.26, -0.5 + i * 0.35, 1);
        circle(ctx, tg[0], tg[1], 8); paint(ctx, '#4a4458', 5);
      }
      if (o.extraOutside) o.extraOutside(ctx);
    },
  };
}
const carWith = (ctx, o, cr) => car(ctx, { ...o, crew: cr?.crew, outside: cr?.outside });

// ---------------------------------------------------------------- sets
const CX = 1520, CY = 950; // where the car is parked outside the bank
function setBank(ctx, t, o = {}) {
  bg.sky(ctx, { horizon: 790, cloudX: t * 12 });
  bg.farCity(ctx, 0, 690);
  bg.midCity(ctx, 260, 790);
  bg.shopRow(ctx, 640, 790);
  bg.bank(ctx, 760, 790, 0.9, { doors: o.doors || 0, alarm: o.alarm || 0, t });
  bg.street(ctx, 0, 860);
  bg.mailbox(ctx, 170, 836);
  bg.hydrant(ctx, 320, 846);
  bg.lamp(ctx, 1250, 830, 1.05);
}
function drivingSide(ctx, t, { scroll, speedBG = false, sp = 2600, groundY = 900 } = {}) {
  if (speedBG) { bg.speedBG(ctx, t, { speed: sp, groundY, horizon: groundY - 230 }); return; }
  bg.sky(ctx, { horizon: groundY - 70, cloudX: scroll * 0.05 });
  bg.farCity(ctx, scroll * 0.15, groundY - 170);
  bg.midCity(ctx, scroll * 0.4, groundY - 70);
  bg.shopRow(ctx, scroll * 0.9, groundY - 70);
  bg.street(ctx, scroll, groundY);
}
// ================================================================= SHOTS
// ---- S01 establishing + title + alarm -------------------------------------------------
shot(0.0, 3.5, (ctx, lt, t) => {
  ctx.save(); cam(ctx, 960, 540, 1 + lt * 0.012);
  setBank(ctx, t, { alarm: seg(lt, 2.7, 2.8) });
  bg.trashCan(ctx, 1160, 872, 0.95);
  carWith(ctx, { x: CX, y: CY, s: 1, face: 'sleepy', light: flick(t), t, bag: null }, null);
  fx.exhaust(ctx, CX - 214, CY - 57, t, { rate: 1.6 });
  fx.sfxText(ctx, 'RRRING!', 1180, 300, seg(lt, 2.75, 3.5), { size: 96, fill: C.red, rot: 0.12, wob: 1 });
  ctx.restore();
  titleCard(ctx, lt, 'GETAWAY CAR');
}, [[0.35, 'sting_title'], [1.1, 'music', { id: 'sneak', style: 'sneak' }], [0.3, 'title_whoosh'], [0.35, 'boing', { pitch: 1.3 }], [2.45, 'zip_down'], [2.7, 'alarm', { dur: 6.6 }]]);

// ---- S02 burst out, cram in ---------------------------------------------------------
shot(3.5, 6.2, (ctx, lt, t) => {
  const tc = onTwos(lt);
  ctx.save(); cam(ctx, 1110, 640, 1.12, 0);
  setBank(ctx, t, { doors: ease.back(seg(lt, 0.05, 0.16)), alarm: 1 });
  bg.trashCan(ctx, 1160, 872, 0.95);
  fx.dust(ctx, 760, 780, seg(lt, 0.08, 0.7), { n: 6, spread: 160, r: 44, dir: 1, seed: 2 });
  // Marge sprints with the loot
  const mK = seg(lt, 0.25, 1.5), bK = seg(lt, 0.4, 1.3);
  const benIn = seg(lt, 1.3, 1.45), margeIn = seg(lt, 1.55, 1.9);
  const carSq = wobble(lt - 1.45, 3, 6) * 0.06 + wobble(lt - 1.9, 2.5, 4) * 0.16;
  const legsK = ease.elastic(seg(lt, 1.95, 2.4));
  const cr = crew({ t, bE: 'panic', mE: 'smirk', benny: benIn >= 1, marge: margeIn >= 1, legs: legsK, reach: margeIn >= 1 ? [-236, -190] : null });
  cr.outside = (orig => c => { orig(c); if (margeIn >= 1) bag(c, -236, -110, 0.55, Math.sin(t * 6) * 0.08); })(cr.outside);
  carWith(ctx, { x: CX, y: CY, s: 1, face: margeIn > 0.9 ? 'grimace' : 'worried', light: flick(t), t, sq: carSq, bounce: carSq * 40 }, cr);
  if (mK > 0 && margeIn < 1) {
    let mx = lerp(780, 1360, ease.inOut(mK)), my = lerp(800, 862, mK), ms = 1, rot = 0, sq = 0;
    if (margeIn > 0) { const k = ease.in(margeIn); mx = lerp(1360, CX - 70, k); my = lerp(862, CY - 180, k); ms = lerp(1, 0.45, k); rot = -k * 1.1; sq = -0.35 * Math.sin(k * Math.PI); }
    if (mK < 1 || margeIn > 0) marge(ctx, { x: mx, y: my, s: ms * 0.98, rot, sq, pose: 'run', ph: tc * 2.6, expr: 'grin', bagHeld: true, t });
    else marge(ctx, { x: mx, y: my, s: 0.98, pose: 'stand', expr: 'smirk', bagHeld: true, t });
  }
  if (bK > 0 && benIn < 1) {
    let bx = lerp(760, 1600, ease.inOut(bK)), by = lerp(800, 870, bK), bs = 1, rot = 0, sq = 0;
    if (benIn > 0) { const k = ease.in(benIn); bx = lerp(1600, CX + 50, k); by = lerp(870, CY - 120, k); bs = lerp(1, 0.4, k); rot = k * 0.9; sq = -0.4 * Math.sin(k * Math.PI); }
    benny(ctx, { x: bx, y: by, s: bs, rot, sq, pose: 'run', ph: tc * 4.5, expr: 'panic', sweat: 1, t });
    if (bK < 1) fx.speedStreaks(ctx, bx - 70, by - 90, 140, 150, t, { n: 4, dir: -1, col: INK, alpha: 0.5, lw: 4 });
  }
  fx.sfxText(ctx, 'BAM!', 640, 520, seg(lt, 0.06, 0.8), { size: 120, fill: C.yellow, rot: -0.15 });
  fx.sfxText(ctx, 'SQUISH!', CX - 100, 600, seg(lt, 1.88, 2.6), { size: 80, fill: C.greenL, rot: 0.1 });
  ctx.restore();
  fx.sirenWash(ctx, t, 0); // (no cop yet)
}, [[0.0, 'music_end', { id: 'sneak' }], [0.0, 'music', { id: 'A', style: 'chase', vel: 0.9, gain: 0.85 }], [0.06, 'door_bam'], [0.3, 'scramble', { dur: 1.1 }], [1.42, 'zip_up'], [1.45, 'car_bounce'], [1.6, 'stretch'], [1.9, 'squish'], [1.95, 'boing', { pitch: 0.8 }], [0.4, 'v_benny_yelp']]);

// ---- S03 the bag won't fit -------------------------------------------------------------
shot(6.2, 10.0, (ctx, lt, t) => {
  const tc = onTwos(lt);
  ctx.save(); cam(ctx, CX - 120, CY - 200, 2.0);
  setBank(ctx, t, { doors: 1, alarm: 1 });
  bg.trashCan(ctx, 1160, 872, 0.95);
  // bag choreography in car coords
  let hand = [-236, -190], bagP = [-236, -110], bagSq = 0, bagRot = Math.sin(t * 6) * 0.08, reach = true, mE = 'smirk', onRoof = false;
  const s1 = seg(lt, 0.3, 0.8), p1 = seg(lt, 0.8, 1.05), s2 = seg(lt, 1.15, 1.55), up = seg(lt, 1.55, 2.15);
  if (s1 > 0 && p1 <= 0) { hand = P([-236, -190], [-150, -200], ease.inOut(s1)); bagP = [hand[0] + 4, hand[1] + 80]; bagSq = -0.4 * ease.in(seg(s1, 0.5, 1)); mE = 'strain'; }
  if (p1 > 0 && s2 <= 0) { hand = P([-150, -200], [-250, -190], ease.out(p1)); bagP = [hand[0], hand[1] + 80]; bagSq = -0.4 * (1 - p1) + wobble(lt - 0.8, 4, 4) * 0.3; bagRot = -0.4 * (1 - p1); mE = 'angry'; }
  if (s2 > 0 && up <= 0) { hand = P([-250, -190], [-150, -204], ease.in(s2)); bagP = [hand[0] + 4, hand[1] + 80]; bagSq = -0.55 * ease.in(seg(s2, 0.4, 1)); mE = 'strain'; }
  if (up > 0) {
    reach = up < 0.15; mE = up < 1 ? 'shock' : 'smirk';
    const k = up; bagP = [lerp(-150, -40, k), lerp(-124, -238, k) - Math.sin(k * Math.PI) * 330]; bagRot = k * TAU; bagSq = 0;
    if (up >= 1) onRoof = true;
  }
  const land = lt - 2.15;
  const carSq = (s2 > 0.5 && up <= 0 ? 0.04 : 0) + (land > 0 ? wobble(land, 2.6, 4) * 0.14 : 0);
  const look = lt > 2.9 ? [0.2, 0.2] : [1, 0];
  const strap = seg(lt, 2.4, 2.9);
  const cr = crew({ t, bE: lt > 3.3 ? 'gulp' : land > 0 ? 'shock' : 'worried', mE: lt > 2.9 ? 'smirk' : mE, mL: look, reach: reach ? hand : null });
  const bagState = onRoof ? { x: -40, y: -238, s: 0.62, sq: land > 0 ? wobble(land, 3, 5) * 0.3 : 0, strap } : null;
  carWith(ctx, { x: CX, y: CY, s: 1, face: land > 0 ? 'grimace' : 'worried', light: flick(t), t, sq: carSq, bounce: Math.max(0, carSq) * 60 + (land > 0 ? 6 : 0), bag: bagState }, cr);
  if (!onRoof) bag(ctx, CX + bagP[0], CY + bagP[1], 0.55, bagRot, bagSq);
  if (up > 0 && up < 1) fx.speedStreaks(ctx, CX + bagP[0], CY + bagP[1] - 40, 60, 80, t, { n: 3, dir: 1, col: INK, alpha: 0.4, lw: 4 });
  fx.sfxText(ctx, 'BOING!', CX - 330, CY - 330, seg(lt, 0.8, 1.4), { size: 60, fill: C.yellow, rot: -0.2 });
  fx.sfxText(ctx, 'THUD!', CX + 60, CY - 360, seg(lt, 2.15, 2.8), { size: 70, fill: C.orange, rot: 0.15 });
  if (land > 0 && land < 0.5) fx.stressMarks(ctx, CX + 200, CY - 170, 1.2, t);
  ctx.restore();
}, [[0.4, 'squeak_rubber'], [0.82, 'boing', { pitch: 1.0 }], [1.2, 'squeak_rubber', { pitch: 0.8 }], [1.55, 'boing', { pitch: 0.7 }], [1.6, 'slide_up'], [2.15, 'thud'], [2.18, 'car_groan'], [2.45, 'zip_rope'], [3.0, 'v_marge_hitit'], [3.45, 'gulp']]);

// ---- S04 close-up Benny: gulp ... determined ------------------------------------------
shot(10.0, 11.6, (ctx, lt, t) => {
  const z = 1 + lt * 0.05;
  ctx.save(); cam(ctx, 960, 560, z);
  // car interior: window to the street behind him
  ctx.fillStyle = C.interior; ctx.fillRect(-200, -200, W + 400, H + 400);
  rrect(ctx, 120, 80, 1200, 560, 60); paint(ctx, C.skyMid, 12);
  ctx.save(); rrect(ctx, 120, 80, 1200, 560, 60); ctx.clip(); bg.midCity(ctx, 700, 760, 5); ctx.restore();
  rrect(ctx, 120, 80, 1200, 560, 60); paint(ctx, null, 12);
  const ex = lt < 0.85 ? 'gulp' : 'determined';
  const sq = lt > 0.3 && lt < 0.5 ? -0.04 : lt > 0.85 && lt < 0.95 ? 0.06 : 0;
  const HS = [[-104, -84], [108, -84]], BS = 4.6, BO = [935, 1250];
  benny(ctx, { x: BO[0], y: BO[1], s: BS, pose: 'grip', hands: HS, expr: ex, sweat: 1, t, sq, look: lt < 0.85 ? [0.3, 0.4] : [1, 0.1] });
  // steering wheel rim in the foreground, knuckles over the top
  ctx.beginPath(); ctx.ellipse(960, 1200, 680, 330, 0, 0, TAU); paint(ctx, null, 80, INK);
  ctx.beginPath(); ctx.ellipse(960, 1200, 680, 330, 0, 0, TAU); paint(ctx, null, 56, '#3a3a44');
  const shake = lt > 0.85 ? Math.sin(t * 70) * 3 : 0;
  for (const [hx, hy] of HS) { ctx.save(); ctx.translate(BO[0] + hx * BS + shake, BO[1] + hy * BS); ctx.scale(BS, BS); hand(ctx, 0, 0, 12, true); ctx.restore(); }
  ctx.restore();
  if (lt > 0.85) fx.stressMarks(ctx, 640, 230, 2.4, t);
}, [[0.0, 'music_end', { id: 'A' }], [0.25, 'gulp'], [0.85, 'sting_det'], [0.0, 'heartbeat', { n: 2 }]]);

// ---- S04b foot stomps the pedal ---------------------------------------------------------
shot(11.6, 12.1, (ctx, lt, t) => {
  const [sx, sy] = shk(t, seg(lt, 0.12, 0.14) > 0 && lt < 0.4 ? 14 : 0);
  ctx.save(); ctx.translate(sx, sy);
  ctx.fillStyle = '#4f7078'; ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = '#3c5a61'; ctx.fillRect(0, 760, W, 400);
  fx.impact(ctx, 1080, 740, 420, seg(lt, 0.13, 0.5), { col: C.yellow });
  const dn = ease.in(seg(lt, 0, 0.13));
  // pedal
  ctx.save(); ctx.translate(1060, 760 + dn * 40); ctx.rotate(0.25 - dn * 0.15); rrect(ctx, -170, -40, 340, 70, 14); paint(ctx, C.metal, 9); ctx.restore();
  // foot
  const fy = lerp(-200, 690, dn);
  hose(ctx, [[1000, fy - 900], [1010, fy - 120]], 150, C.navyD, 10);
  ctx.beginPath(); ctx.ellipse(1080, fy, 210, 95, 0.2, 0, TAU); paint(ctx, INK, 10, '#fff8e0');
  ctx.beginPath(); ctx.ellipse(1040, fy - 40, 90, 30, 0.2, 0, TAU); paint(ctx, '#5a5060', 0);
  if (dn < 1) fx.speedStreaks(ctx, 1080, fy - 300, 0, 300, t, { n: 5, col: '#fff', alpha: 0.6 });
  fx.sfxText(ctx, 'STOMP!', 1500, 300, seg(lt, 0.13, 0.5), { size: 150, fill: C.red, rot: 0.1 });
  ctx.restore();
}, [[0.12, 'stomp']]);

// ---- S05 rattles in place ----------------------------------------------------------------
shot(12.1, 14.5, (ctx, lt, t) => {
  const tc = onTwos(lt);
  const rev = seg(lt, 0, 2.2);
  ctx.save(); cam(ctx, 1440, 760, 1.6);
  setBank(ctx, t, { doors: 1, alarm: 1 });
  bg.trashCan(ctx, 1160, 872, 0.95);
  const lean = -0.03 - rev * 0.04;
  const cr = crew({ t, bE: 'determined', mE: lt > 1.2 ? 'shock' : 'smirk', kick: 2.5 });
  carWith(ctx, { x: CX, y: CY, s: 1, face: 'strain', light: flick(t), t, wheel: t * 60, shake: 3 + rev * 6, tilt: lean, bag: { x: -40, y: -238, s: 0.62, rot: Math.sin(t * 40) * 0.06 } }, cr);
  // wheel smoke + exhaust
  fx.dust(ctx, CX - 130, CY - 10, (lt * 2.2) % 1, { n: 4, spread: 140, r: 46, col: '#d8d0c8', dir: -1, seed: Math.floor(lt * 2.2) });
  fx.dust(ctx, CX + 100, CY - 10, (lt * 2.2 + 0.5) % 1, { n: 3, spread: 120, r: 40, col: '#d8d0c8', dir: -1, seed: 7 + Math.floor(lt * 2.2) });
  fx.exhaust(ctx, CX - 214, CY - 57, t, { rate: 6, dark: true, n: 5, speed: 1.4 });
  fx.sfxText(ctx, 'VROOOM', CX - 20, CY - 430, seg(lt, 0.2, 1.4), { size: 90, fill: C.yellow, rot: -0.08, wob: 3 });
  fx.sfxText(ctx, 'RRRRR!', CX + 160, CY - 380, seg(lt, 1.3, 2.4), { size: 80, fill: C.orange, rot: 0.1, wob: 3 });
  ctx.restore();
}, [[0.0, 'engine_rev', { dur: 2.45 }], [0.0, 'drumroll', { dur: 2.4 }]]);

// ---- S06 ...launches BACKWARD into the trash can -----------------------------------------
shot(14.5, 16.2, (ctx, lt, t) => {
  const go = seg(lt, 0, 0.13), hit = lt - 0.13;
  const [sx, sy] = shk(t, hit > 0 && hit < 0.35 ? 22 * (1 - hit / 0.35) : 0);
  ctx.save(); ctx.translate(sx, sy); cam(ctx, 1300, 690, 1.2);
  setBank(ctx, t, { doors: 1, alarm: 1 });
  const x = lerp(CX, CX - 150, ease.in(go));
  // crushed can
  bg.trashCan(ctx, 1150, 872, 0.95, { crush: hit > 0 ? 1 : 0, lid: hit <= 0 });
  // ghost smear
  if (go > 0 && go < 1) for (let i = 1; i <= 3; i++) { ctx.save(); ctx.globalAlpha = 0.18; carWith(ctx, { x: x + i * 60, y: CY, s: 1, t, face: 'shock', bag: { x: -40, y: -238, s: 0.62 } }, null); ctx.restore(); }
  const csq = hit > 0 ? -0.18 * wobble(hit, 2.2, 4.5) * -1 : 0;
  const cr = crew({ t, bE: hit > 0 ? 'shock' : 'determined', mE: hit > 0 ? 'shock' : 'smirk', kick: 0.5 });
  carWith(ctx, { x, y: CY, s: 1, face: hit > 0.25 ? 'dizzy' : 'shock', light: hit > 0 ? (hash(Math.floor(t * 20)) > 0.5 ? 1 : 0) : 1, t, sq: -Math.abs(csq), bag: { x: -40, y: -238, s: 0.62, sq: hit > 0 ? wobble(hit, 3, 4) * 0.3 : 0 } }, cr);
  if (go > 0 && go < 1) fx.speedStreaks(ctx, x + 220, CY - 140, 240, 220, t, { n: 6, dir: 1, col: INK, alpha: 0.5 });
  // flying garbage
  if (hit > 0) {
    const k = clamp(hit / 1.4);
    bg.trashLid(ctx, 1150 + k * 80, 750 - Math.sin(k * Math.PI) * 520 + k * 120, 0.95, hit * 14);
    bg.fishBone(ctx, 1150 - k * 380, 760 - Math.sin(Math.min(1, k * 1.4) * Math.PI) * 300 + k * 100, 0.9, hit * 8);
    bg.tinCan(ctx, 1150 - k * 200, 760 - Math.sin(Math.min(1, k * 1.2) * Math.PI) * 420, 1.2, hit * 10);
    bg.tinCan(ctx, 1150 + k * 260, 760 - Math.sin(Math.min(1, k * 1.6) * Math.PI) * 260, 1.0, -hit * 12);
    // banana peel arcs onto Marge's head (rear window)
    const pk = clamp(hit / 0.9);
    const tgt = [x - 85, CY - 236];
    bg.bananaPeel(ctx, lerp(1150, tgt[0], pk), lerp(760, tgt[1], pk) - Math.sin(pk * Math.PI) * 300, 1.1, (1 - pk) * 9);
    fx.impact(ctx, 1170, 800, 210, seg(hit, 0, 0.7), { word: 'CRASH!', size: 100, col: C.yellow });
  }
  ctx.restore();
  fx.wash(ctx, '#fff', hit > 0 && hit < 0.05 ? 0.45 : 0);
}, [[0.0, 'whoosh_rev'], [0.13, 'crash'], [0.15, 'trash_clatter'], [0.9, 'slide_down_short']]);

// ---- S07 Marge: deadpan stare to camera ----------------------------------------------------
shot(16.2, 19.0, (ctx, lt, t) => {
  ctx.save(); cam(ctx, CX - 150 - 60, CY - 196, 4.0);
  setBank(ctx, t, { doors: 1, alarm: 0 });
  bg.trashCan(ctx, 1150, 872, 0.95, { crush: 1, lid: false });
  const blink = lt > 1.25 && lt < 1.36;
  const cr = crew({ t, bE: lt > 1.9 ? 'sheepish' : 'shock', bL: lt > 1.9 ? [-1, 0.3] : [1, 0], mE: blink ? 'blink' : 'deadpan', mL: [-0.2, 0.15], kick: 0, mHeadRot: 0.1, peel: true });
  carWith(ctx, { x: CX - 150, y: CY, s: 1, face: 'dizzy', light: 0, t, sq: 0, bag: { x: -40, y: -238, s: 0.62, strap: 1 } }, cr);
  // dizzy stars over the car's face
  for (let i = 0; i < 3; i++) { const a = t * 3 + i * TAU / 3; fx.puff(ctx, CX - 150 + 170 + Math.cos(a) * 40, CY - 170 + Math.sin(a) * 10, 6, C.yellow, 1); }
  ctx.restore();
}, [[0.2, 'cricket', { dur: 2.0 }], [0.3, 'lid_wobble'], [1.28, 'blink'], [2.0, 'v_benny_reverse']]);

// ---- S08 clunk ... ZOOM -----------------------------------------------------------------
shot(19.0, 20.0, (ctx, lt, t) => {
  ctx.save(); cam(ctx, 1300, 690, 1.2);
  setBank(ctx, t, { doors: 1, alarm: 1 });
  bg.trashCan(ctx, 1150, 872, 0.95, { crush: 1, lid: false });
  bg.trashLid(ctx, 1240, 935, 0.95, Math.sin(lt * 18) * 0.15 * (1 - lt));
  const go = seg(lt, 0.42, 0.62);
  const x0 = CX - 150, x = lerp(x0, x0 + 1300, ease.in3(go));
  const jolt = lt > 0.15 && lt < 0.42 ? wobble(lt - 0.15, 5, 8) * 0.04 : 0;
  const pre = seg(lt, 0.25, 0.42);
  const cr = crew({ t, bE: 'determined', mE: 'smirk', mL: [1, 0] });
  if (go > 0) for (let i = 1; i <= 4; i++) { ctx.save(); ctx.globalAlpha = 0.16; carWith(ctx, { x: x - i * 90, y: CY, s: 1, t, face: 'grimace', bag: { x: -40, y: -238, s: 0.62 } }, null); ctx.restore(); }
  carWith(ctx, { x, y: CY, s: 1, face: 'grimace', light: flick(t), t, sq: jolt - pre * 0.12 + (go > 0 ? 0.25 * (1 - go) : 0), tilt: pre * 0.05, bag: { x: -40, y: -238, s: 0.62 } }, cr);
  if (go > 0) { fx.dust(ctx, x0 - 120, CY - 40, seg(lt, 0.42, 1.0), { n: 7, spread: 260, r: 60, dir: -1, seed: 9 }); fx.speedStreaks(ctx, x - 220, CY - 140, 520, 220, t, { n: 7, dir: -1, col: INK, alpha: 0.5 }); }
  fx.sfxText(ctx, 'CLUNK', x0 - 120, CY - 330, seg(lt, 0.15, 0.5), { size: 70, fill: C.metal, rot: -0.1 });
  fx.sfxText(ctx, 'ZOOM!', 1500, 520, seg(lt, 0.45, 1.0), { size: 120, fill: C.yellow, rot: -0.15 });
  ctx.restore();
}, [[0.15, 'clunk'], [0.42, 'zoom_off'], [0.45, 'skid_short']]);

// ---- S09 low angle: the chase is ON -------------------------------------------------------
shot(20.0, 23.0, (ctx, lt, t) => {
  const tc = onTwos(lt);
  ctx.save(); const r = Math.sin(lt * 2.2) * 0.05; ctx.translate(W / 2, H / 2); ctx.rotate(r); ctx.translate(-W / 2, -H / 2);
  perspStreet(ctx, t, { spd: 40 });
  radialLines(ctx, t, 960, 690, { spd: 2.2 });
  const b = Math.abs(Math.sin(t * 9)) * -14;
  carFront(ctx, { x: 960 + Math.sin(lt * 3) * 60, y: 1030, s: 1.55, face: 'grimace', light: flick(t), t, bounce: b, bennyExpr: 'panic', margeExpr: lt > 1.2 ? 'yell' : 'grin', shake: 2 });
  fx.dust(ctx, 760, 1030, (lt * 3) % 1, { n: 4, spread: 160, r: 50, dir: -1, seed: Math.floor(lt * 3) });
  fx.dust(ctx, 1180, 1030, (lt * 3 + 0.5) % 1, { n: 4, spread: 160, r: 50, dir: 1, seed: 3 + Math.floor(lt * 3) });
  ctx.restore();
  fx.sirenWash(ctx, t, 0.9);
}, [[0.0, 'music', { id: 'main', style: 'chase', melody: true }], [0.0, 'siren', { dur: 7.4 }], [0.05, 'whoosh_by'], [1.2, 'v_marge_faster']]);

// ---- S10 the bike cop: slow, bored -------------------------------------------------------
shot(23.0, 25.2, (ctx, lt, t) => {
  const sc = t * 140;
  ctx.save(); cam(ctx, 960, 640, 1.2);
  drivingSide(ctx, t, { scroll: sc, groundY: 860 });
  const yawn = lt > 0.7 && lt < 1.6;
  copBike(ctx, { x: 930, y: 1010, s: 1.65, pedal: t * 0.55, wheel: t * 2.5, expr: yawn ? 'yawn' : 'bored', light: t, t });
  if (yawn) fx.zzz(ctx, 1030, 450, lt);
  ctx.restore();
  fx.sirenWash(ctx, t, 1);
}, [[0.75, 'v_cop_yawn'], [0.0, 'bike_squeak', { n: 3, gap: 0.8 }]]);

// ---- S11 ...and somehow he's right behind them -----------------------------------------------
shot(25.2, 27.4, (ctx, lt, t) => {
  ctx.save(); cam(ctx, 960, 560, 1);
  drivingSide(ctx, t, { speedBG: true, sp: 2800, groundY: 900 });
  const bob = Math.sin(t * 18) * 4;
  const looked = lt > 0.45, seen = lt > 1.15;
  const cr = crew({ t, bE: seen ? 'shock' : 'panic', bL: looked ? [-1, 0] : [1, 0], mE: seen ? 'shock' : 'grin', mL: seen ? [-1, 0] : [1, 0], sweat: 1 });
  carWith(ctx, { x: 1240, y: 900, s: 1.25, face: seen ? 'scared' : 'grimace', look: seen ? [-1, 0] : [1, 0], light: flick(t), t, wheel: t * 40, bounce: bob, bag: { x: -40, y: -238, s: 0.62, rot: Math.sin(t * 12) * 0.05 } }, cr);
  fx.speedStreaks(ctx, 1240 - 260, 760, 260, 240, t, { n: 6, dir: -1, alpha: 0.7 });
  // cop slides in from the left, pedalling lazily, keeping pace
  const ck = ease.out3(seg(lt, 0.55, 1.15));
  const cx = lerp(-300, 640, ck);
  copBike(ctx, { x: cx, y: 900, s: 1.1, pedal: t * 0.6, wheel: t * 30, expr: seen ? 'look' : 'bored', look: [1, 0], light: t, t });
  if (seen) fx.sfxText(ctx, '!!', 1180, 380, seg(lt, 1.15, 2.0), { size: 120, fill: C.red, rot: 0.1 });
  ctx.restore();
  fx.sirenWash(ctx, t, 1);
}, [[0.5, 'look_whip'], [1.15, 'sting_shock'], [1.18, 'v_benny_yelp2'], [1.4, 'honk']]);

// ---- S12a skid to a stop -------------------------------------------------------------------
const STOP_SC = 2600 * 0.32;
shot(27.4, 28.6, (ctx, lt, t) => {
  const k = seg(lt, 0, 0.6);
  const sc = 1200 + STOP_SC * ease.out(k) * 0.9;
  ctx.save(); cam(ctx, 960, 540, 1);
  drivingSide(ctx, t, { scroll: sc, groundY: 880 });
  // crosswalk (ahead of the car) + duck sign
  ctx.save(); ctx.translate(1600 - (sc - 1200), 0);
  for (let i = 0; i < 6; i++) { poly(ctx, [[i * 52, 896], [i * 52 + 30, 896], [i * 52 - 10, 1080], [i * 52 - 40, 1080]]); ctx.fillStyle = C.lane; ctx.fill(); }
  ctx.restore();
  duckSign(ctx, 1500 - (sc - 1200), 810);
  const tilt = k < 1 ? 0.07 * Math.sin(k * Math.PI) : wobble(lt - 0.6, 2, 5) * -0.04;
  const cr = crew({ t, bE: 'panic', mE: 'shock', sweat: 1 });
  carWith(ctx, { x: 1050, y: 990, s: 1.2, face: 'scared', light: flick(t), t, wheel: sc / 36, tilt, bag: { x: -40 + k * 30, y: -238, s: 0.62, rot: k * 0.3 * (1 - k) } }, cr);
  // skid marks + smoke
  ctx.fillStyle = 'rgba(30,25,35,0.6)'; ctx.fillRect(1050 - 160 - ease.out(k) * 700, 980, ease.out(k) * 700, 10); ctx.fillRect(1050 + 120 - ease.out(k) * 700, 980, ease.out(k) * 700, 10);
  fx.dust(ctx, 900, 985, seg(lt, 0, 0.9), { n: 7, spread: 300, r: 60, col: '#e6ded4', dir: -1, seed: 4 });
  fx.sfxText(ctx, 'SCREEECH!', 760, 480, seg(lt, 0.02, 1.1), { size: 110, fill: C.yellow, rot: -0.08, wob: 3 });
  ctx.restore();
  fx.sirenWash(ctx, t, 0.8);
}, [[0.0, 'skid'], [0.0, 'music_end', { id: 'main' }]]);
function duckSign(ctx, x, y) {
  ctx.save(); ctx.translate(x, y);
  rrect(ctx, -8, -300, 16, 300, 4); paint(ctx, C.metalD);
  ctx.save(); ctx.translate(0, -340); ctx.rotate(Math.PI / 4); rrect(ctx, -70, -70, 140, 140, 12); paint(ctx, C.yellow, 8); ctx.restore();
  duck(ctx, -6, -300, 0.7, 0, false, false);
  ctx.restore();
}

// ---- S12b ducks crossing, sirens wailing ----------------------------------------------------
function duckFront(ctx, lt, t, part) {
  const VX = 760;
  const cop = pr => {
    const z = lerp(230, 70, seg(t, 28.6, 33.0));
    const [x, y] = pr(-2.2, 0, z);
    copBike(ctx, { x, y, s: 950 / z * 0.03, pedal: t * 0.6, wheel: t * 3, expr: 'bored', light: t, t });
  };
  perspStreet(ctx, t, { spd: 0, z0: 40, vpy: 600, vpx: VX, h: 1.4, cop });
  // crosswalk stripes
  ctx.fillStyle = C.lane; for (let i = -9; i <= 9; i++) { const x = VX + 200 + i * 120; poly(ctx, [[x - 34, 900], [x + 34, 900], [x + 46, 1080], [x - 46, 1080]]); ctx.fill(); }
  carFront(ctx, { x: 1180, y: 880, s: 1.4, face: part === 'stare' ? 'happy' : 'worried', light: flick(t), t, bennyExpr: 'worried', margeExpr: 'deadpan', look: part === 'stare' ? [-0.3, 1] : [-0.4, 0.6] });
}
const ducklings = (ctx, lt, t, x0, spdPx, stopAt = null) => {
  // mama + 4 babies march left -> right in front of the car
  const ph = onTwos(t) * 2.4;
  const xs = [0, -210, -350, -480, -620];
  xs.forEach((off, i) => {
    let x = x0 + off + lt * spdPx, baby = i > 0, s = baby ? 1.0 : 1.6, look = 0, flip = false;
    if (stopAt && i === 4) { x = stopAt.x(lt); look = stopAt.look(lt); flip = stopAt.flip(lt); }
    duck(ctx, x, 1050, s, ph + i * 0.27, baby, flip, look);
  });
};
shot(28.6, 30.2, (ctx, lt, t) => {
  duckFront(ctx, lt, t, 'cross');
  ducklings(ctx, lt, t, 120, 300);
  fx.sirenWash(ctx, t, 1);
}, [[0.0, 'siren', { dur: 4.4 }], [0.2, 'quack', { n: 6, gap: 0.26 }]]);
shot(30.2, 31.0, (ctx, lt, t) => {
  // cut-in: Benny drums the wheel, Marge facepalms
  ctx.save(); cam(ctx, 940, 760, 2.4);
  drivingSide(ctx, t, { scroll: 1200 + STOP_SC * 0.9, groundY: 880 });
  const tap = Math.floor(t * 10) % 2;
  const cr = crew({ t, bE: 'worried', bL: [0.5, 0.6], mE: 'deadpan', mPose: 'facepalm', mHeadRot: 0.15, sweat: 1 });
  carWith(ctx, { x: 1050, y: 990, s: 1.2, face: 'worried', light: flick(t), t, bag: { x: -40, y: -238, s: 0.62 } }, cr);
  // drumming fingers
  for (let i = 0; i < 3; i++) circle(ctx, 1050 + 1.2 * 102 + i * 7, 990 - 1.2 * 151 - ((tap + i) % 2) * 6, 3.5);
  ctx.restore();
  fx.sirenWash(ctx, t, 1);
}, [[0.0, 'drum_fingers', { dur: 0.8 }], [0.35, 'facepalm_slap']]);
shot(31.0, 33.0, (ctx, lt, t) => {
  duckFront(ctx, lt, t, lt < 1.1 ? 'stare' : 'cross');
  const g = lt + 2.4;
  const stop = { x: l => (l < 0.25 ? 1060 + l * 400 : l < 1.1 ? 1160 : 1160 + (l - 1.1) * 600), look: l => (l > 0.3 && l < 1.0 ? -0.2 : 0), flip: l => l > 0.3 && l < 1.0 };
  ducklings(ctx, g, t, 120, 300, stop);
  if (lt > 0.4 && lt < 0.9) fx.sfxText(ctx, 'quack.', 1230, 880, seg(lt, 0.42, 0.95), { size: 56, fill: '#fff', rot: -0.1 });
  if (lt > 1.4) { fx.speedStreaks(ctx, 960, 700, 0, 500, t, { n: 0 }); }
  fx.sirenWash(ctx, t, 1);
}, [[0.45, 'quack_small'], [0.6, 'sting_tiny'], [1.5, 'rev_short'], [1.6, 'music', { id: 'B', style: 'chase', melody: true }]]);

// ---- S13 top-down: Benny signals politely at every turn ------------------------------------------
const BLOCKS = [
  [-300, -300, 900, 500, C.orange], [800, -300, 400, 500, C.teal], [1400, -300, 900, 500, C.brick],
  [-300, 400, 900, 260, C.mustard], [800, 400, 400, 260, null, true], [1400, 400, 900, 260, C.plum],
  [-300, 860, 900, 500, C.tealD], [800, 860, 400, 500, C.orangeL], [1400, 860, 900, 500, C.teal],
];
// car route: [time, x, y, heading, blinker]
const ROUTE = [[0, -140, 300, 0], [0.55, 700, 300, 0, 'R'], [0.95, 700, 300, Math.PI / 2, 'R'], [1.3, 700, 760, Math.PI / 2, 'L'], [1.7, 700, 760, 0, 'L'], [2.05, 1300, 760, 0, 'L'], [2.45, 1300, 760, -Math.PI / 2, 'L'], [2.8, 1300, 300, -Math.PI / 2, 'R'], [3.1, 1300, 300, 0, 'R'], [3.4, 1900, 300, 0]];
function routeAt(lt) {
  for (let i = 0; i < ROUTE.length - 1; i++) {
    const [a, x1, y1, h1, bl] = ROUTE[i], [b, x2, y2, h2] = ROUTE[i + 1];
    if (lt <= b) { const k = ease.inOut(seg(lt, a, b)); return { x: lerp(x1, x2, k), y: lerp(y1, y2, k), h: lerp(h1, h2, k), blink: x1 === x2 && y1 === y2 ? bl : (ROUTE[i + 1][4] && k > 0.55 ? ROUTE[i + 1][4] : null) }; }
  }
  const l = ROUTE[ROUTE.length - 1]; return { x: l[1], y: l[2], h: l[3], blink: null };
}
shot(33.0, 36.4, (ctx, lt, t) => {
  const r0 = routeAt(lt);
  ctx.save(); cam(ctx, lerp(960, r0.x, 0.55), lerp(540, r0.y, 0.55), 1.45);
  bg.topCity(ctx, { blocks: BLOCKS });
  // lane dashes
  ctx.fillStyle = C.lane;
  for (let x = -100; x < 2000; x += 90) { ctx.fillRect(x, 296, 46, 8); ctx.fillRect(x, 756, 46, 8); }
  for (let y = -100; y < 1200; y += 90) { ctx.fillRect(696, y, 8, 46); ctx.fillRect(1296, y, 8, 46); }
  const r = routeAt(lt);
  const on = Math.floor(t * 6) % 2 === 0;
  // the cop just pedals straight along the top road
  const cx = lerp(-150, 1700, lt / 3.4);
  bg.bikeTop(ctx, cx, 340, 1.3, 0, t);
  bg.carTop(ctx, r.x, r.y - 30, 1.3, r.h, { blink: r.blink, on, t });
  if (r.blink && on) fx.sfxText(ctx, r.blink === 'L' ? '< tick' : 'tick >', r.x + 30, r.y - 170, 0.5, { size: 62, fill: '#ffb000', rot: 0 });
  ctx.restore();
  fx.sirenWash(ctx, t, 0.5);
}, [[0.0, 'blinker', { dur: 3.4 }]]);

// ---- S13b Marge: "JUST DRIVE!" -----------------------------------------------------------------------
shot(36.4, 37.6, (ctx, lt, t) => {
  const [sx, sy] = shk(t, lt > 0.15 ? 10 : 0);
  ctx.save(); ctx.translate(sx, sy);
  bg.speedBG(ctx, t, { speed: 3000, horizon: 600, groundY: 900 });
  radialLines(ctx, t, 960, 420, { spd: 3, col: 'rgba(255,255,255,0.8)', n: 30, inner: 320 });
  const zin = ease.back(seg(lt, 0, 0.18));
  marge(ctx, { x: 820, y: 1950 - zin * 60, s: 4.2, pose: 'stand', expr: lt > 0.15 ? 'yell' : 'angry', look: [0, 0], t });
  fx.sfxText(ctx, 'បើកទៅចុះ!', 1380, 250, seg(lt, 0.15, 1.2), { size: 130, fill: C.red, rot: 0.08, wob: 4, font: 'Koulen' });
  ctx.restore();
}, [[0.12, 'v_marge_justdrive']]);

// ---- S14 money flies off the roof --------------------------------------------------------------------
const CAR14 = [1260, 940], CATCH = [1.25, 2.1, 2.95, 3.75];
const BILLS = []; for (let i = 0; i < 16; i++) BILLS.push({ t0: 0.4 + i * 0.3, seed: i, caught: CATCH.findIndex(c => Math.abs(c - (0.4 + i * 0.3 + 0.42)) < 0.16) });
function billPos(b, lt) {
  const k = (lt - b.t0) / 1.25; if (k < 0 || k > 1) return null;
  const sx = CAR14[0] - 52, sy = CAR14[1] - 400;
  const ex = 380 + 1.15 * 98 + (hash(b.seed) - 0.5) * 40, ey = 940 - 1.15 * 175;
  return { x: lerp(sx, ex, k), y: lerp(sy, ey, k) - Math.sin(k * Math.PI) * (140 + hash(b.seed * 3) * 90), rot: Math.sin(k * 18 + b.seed) * 0.7, fl: Math.cos(k * 22 + b.seed), k };
}
shot(37.6, 43.0, (ctx, lt, t) => {
  ctx.save(); cam(ctx, 960, 540, 1);
  drivingSide(ctx, t, { speedBG: true, sp: 2600, groundY: 920 });
  const bob = Math.sin(t * 18) * 4;
  // which catch is active?
  let reach = null, held = 0, mE = 'grin';
  CATCH.forEach((c, i) => {
    if (lt > c + 0.25) held = i + 1;
    const out = seg(lt, c - 0.2, c), back = seg(lt, c + 0.06, c + 0.25);
    if (out > 0 && back < 1) {
      const b = BILLS.find(bb => bb.caught === i), p = b ? billPos(b, c) : { x: 600, y: 600 };
      const tgt = [(p.x - CAR14[0]) / 1.3, (p.y - CAR14[1] - bob) / 1.3];
      const sh = [-96, -176];
      const k = back > 0 ? 1 - ease.in(back) : ease.out(out);
      reach = [lerp(sh[0], tgt[0], k), lerp(sh[1], tgt[1], k)]; mE = 'grin';
    }
  });
  const cr = crew({ t, bE: 'panic', bL: [-1, -0.4], mE, mL: [-1, -0.3], reach, held: reach ? held : 0, sweat: 1 });
  carWith(ctx, { x: CAR14[0], y: CAR14[1], s: 1.3, face: 'grimace', light: flick(t), t, wheel: t * 40, bounce: bob, bag: { x: -40, y: -238, s: 0.62, rot: Math.sin(t * 12) * 0.06, open: 1 } }, cr);
  fx.speedStreaks(ctx, CAR14[0] - 270, 760, 260, 280, t, { n: 5, dir: -1, alpha: 0.7 });
  // cop: bills keep landing in his basket
  copBike(ctx, { x: 380, y: 940, s: 1.15, pedal: t * 0.6, wheel: t * 30, expr: lt > 4.3 ? 'look' : 'bored', look: [0.3, 1], light: t, t });
  const inBasket = BILLS.filter(b => b.caught < 0 && lt > b.t0 + 1.25).length;
  for (let i = 0; i < Math.min(inBasket, 6); i++) bill(ctx, 380 + 1.15 * (84 + i * 6), 940 - 1.15 * (172 + (i % 2) * 6), 0.28, -0.6 + i * 0.25, 1);
  // flying bills
  for (const b of BILLS) {
    const p = billPos(b, lt); if (!p) continue;
    if (b.caught >= 0 && lt > CATCH[b.caught]) continue;
    bill(ctx, p.x, p.y, 0.55, p.rot, p.fl);
  }
  CATCH.forEach((c, i) => fx.sfxText(ctx, 'SNATCH!', 640 + i * 60, 360 + (i % 2) * 70, seg(lt, c, c + 0.5), { size: 60, fill: C.money, rot: -0.1 }));
  ctx.restore();
  fx.sirenWash(ctx, t, 0.8);
}, [[0.0, 'siren', { dur: 5.4 }], [0.4, 'flutter', { dur: 4.6 }], ...[1.25, 2.1, 2.95, 3.75].flatMap(c => [[c - 0.22, 'slide_up_fast'], [c, 'snatch']])]);

// ---- S15a: a drive-through!? -------------------------------------------------------------------------
shot(43.0, 44.2, (ctx, lt, t) => {
  ctx.save(); cam(ctx, 960, 540, 1);
  drivingSide(ctx, t, { speedBG: true, sp: 2600, groundY: 920 });
  // sign whizzes in from the right
  const sx = lerp(2300, 1350, ease.out3(seg(lt, 0, 0.45)));
  ctx.save(); ctx.translate(sx, 0);
  rrect(ctx, -10, 360, 20, 560, 4); paint(ctx, C.metalD);
  rrect(ctx, -230, 170, 460, 200, 22); paint(ctx, C.yellow, 9);
  text(ctx, 'BURGER BARN', 0, 236, { size: 70, fill: C.red, lw: 8 });
  text(ctx, 'DRIVE-THRU', -30, 316, { size: 56, fill: C.teal, lw: 7 });
  poly(ctx, [[150, 290], [200, 320], [150, 350]]); paint(ctx, C.red, 6);
  fries(ctx, 300, 260, 1.1);
  ctx.restore();
  const swerve = seg(lt, 0.55, 1.2);
  const cr = crew({ t, bE: lt > 0.35 ? 'happy' : 'panic', bL: [1, -1], mE: lt > 0.6 ? 'shock' : 'grin', sweat: lt > 0.35 ? 0 : 1 });
  carWith(ctx, { x: 980 + ease.in(swerve) * 900, y: 920 + ease.in(swerve) * 120, s: 1.1, face: 'happy', light: flick(t), t, wheel: t * 40, tilt: swerve * 0.25, bounce: Math.sin(t * 18) * 4, bag: { x: -40, y: -238, s: 0.62 } }, cr);
  if (lt > 0.35 && lt < 0.8) { text(ctx, '!', 1010, 520, { size: 120, fill: C.yellow, lw: 12 }); }
  if (swerve > 0) fx.dust(ctx, 900, 980, swerve, { n: 6, spread: 260, r: 50, seed: 8 });
  ctx.restore();
  fx.sirenWash(ctx, t, 0.6);
}, [[0.35, 'sting_idea'], [0.55, 'skid'], [0.6, 'music_end', { id: 'B' }]]);

// ---- S15b at the speaker ------------------------------------------------------------------------------
function driveSet(ctx, t, o = {}) {
  bg.sky(ctx, { horizon: 780, cloudX: t * 8 });
  bg.farCity(ctx, 300, 690);
  bg.midCity(ctx, 800, 780);
  bg.street(ctx, 0, 860, { lanes: false });
  bg.driveThru(ctx, 1700, 870, 1.0, { t });
  menuBoard(ctx, o, t);
}
const menuBoard = (ctx, o, t) => bg.menuBoard(ctx, 1010, 875, 1.0, { talk: o.talk || 0, t });
shot(44.2, 48.2, (ctx, lt, t) => {
  ctx.save(); cam(ctx, 1080, 650, 1.38);
  const talk = lt > 0.15 && lt < 1.85 ? 1 : 0;
  driveSet(ctx, t, { talk });
  const panic = lt > 1.9 && lt < 2.7, order = lt >= 2.7;
  const bL = panic ? [Math.sin(t * 30) > 0 ? 1 : -1, 0] : [1, 0];
  const cr = crew({ t, bE: order ? 'panic' : panic ? 'shock' : 'worried', bL, mE: lt > 3.2 ? 'deadpan' : 'angry', mL: lt > 3.2 ? [-0.3, 0.2] : [1, 0], mPose: lt > 3.4 ? 'facepalm' : 'stand', sweat: 1 });
  carWith(ctx, { x: 860, y: 960, s: 1, face: order ? 'grimace' : 'worried', light: flick(t), t, bag: { x: -40, y: -238, s: 0.62 } }, cr);
  if (order) fx.sfxText(ctx, 'ដំឡូងបំពងធំមួយ!', 560, 545, seg(lt, 2.7, 3.9), { size: 66, fill: C.yellow, rot: -0.06, wob: 3, font: 'Koulen' });
  if (panic) fx.stressMarks(ctx, 920, 720, 1.4, t);
  ctx.restore();
}, [[0.0, 'music', { id: 'mz', style: 'muzak' }], [0.15, 'v_speaker'], [1.9, 'v_benny_uh'], [1.9, 'sting_panic'], [2.7, 'v_benny_fries'], [3.45, 'facepalm_slap']]);
setShift(1.2);

// ---- S15c fries handed over; the cop is in line behind them ------------------------------------------------
shot(47.0, 48.2, (ctx, lt, t) => {
  ctx.save(); cam(ctx, 1320, 650, 1.3);
  driveSet(ctx, t, {});
  copBike(ctx, { x: 1000, y: 960, s: 1, pedal: 0.15, wheel: 0, expr: 'bored', look: [1, 0.3], light: t, t });
  const got = lt > 0.45;
  const cr = crew({ t, bE: got ? 'happy' : 'worried', bPose: got ? 'eat' : 'drive', holding: got ? 'fries' : null, mE: 'deadpan', mL: [0.2, 0.1], sweat: got ? 0 : 0.6 });
  carWith(ctx, { x: 1590, y: 960, s: 1, face: 'happy', light: flick(t), t, bag: { x: -40, y: -238, s: 0.62 } }, cr);
  // worker's arm hands fries out of the window, over the car
  if (!got) { const k = ease.out(seg(lt, 0.0, 0.4)); hose(ctx, [[1700, 680], [1700 - k * 50, 650 - k * 20]], 22, C.red); fries(ctx, 1690 - k * 50, 640 - k * 20, 0.7); }
  if (lt > 0.4 && lt < 0.9) fx.sfxText(ctx, 'DING!', 1800, 480, seg(lt, 0.4, 1.0), { size: 60, fill: C.yellow, rot: 0.1 });
  ctx.restore();
}, [[0.0, 'music_end', { id: 'mz', how: 'fade', dur: 0.3 }], [0.4, 'register_ding'], [0.5, 'munch', { n: 3 }]]);

// ---- S15d peel out ---------------------------------------------------------------------------------------
shot(48.2, 49.0, (ctx, lt, t) => {
  ctx.save(); cam(ctx, 1320, 650, 1.3);
  driveSet(ctx, t, {});
  const go = seg(lt, 0.1, 0.35);
  copBike(ctx, { x: 1000 + seg(lt, 0.45, 0.8) * 60, y: 960, s: 1, pedal: 0.15 + lt * 0.4, wheel: lt, expr: 'bored', light: t, t });
  const x = 1590 + ease.in3(go) * 1200;
  const cr = crew({ t, bE: 'happy', bPose: 'eat', holding: 'fries', mE: 'yell', sweat: 0 });
  if (go > 0) for (let i = 1; i <= 3; i++) { ctx.save(); ctx.globalAlpha = 0.15; carWith(ctx, { x: x - i * 90, y: 960, s: 1, t, face: 'grimace', bag: { x: -40, y: -238, s: 0.62 } }, null); ctx.restore(); }
  carWith(ctx, { x, y: 960, s: 1, face: 'grimace', light: 1, t, sq: go > 0 ? 0.2 * (1 - go) : -0.06, bag: { x: -40, y: -238, s: 0.62 } }, cr);
  fx.dust(ctx, 1420, 950, seg(lt, 0.12, 0.8), { n: 6, spread: 240, r: 50, seed: 12 });
  ctx.restore();
}, [[0.1, 'zoom_off'], [0.12, 'music', { id: 'C', style: 'chase', melody: true, bars0: 4, gain: 0.95 }]]);

// ---- S16 the bridge ---------------------------------------------------------------------------------------
const BR = { cx: 1200, base: 760, rise: 150, half: 1000 };
function bridgeScene(ctx, t, { camx = 960, small = true } = {}) {
  const g = ctx.createLinearGradient(0, 0, 0, 720); g.addColorStop(0, '#ff7f5a'); g.addColorStop(0.5, '#ffad5e'); g.addColorStop(1, '#ffe0a0');
  ctx.fillStyle = g; ctx.fillRect(-2000, -1000, 6000, 1720);
  circle(ctx, 1500, 610, 150); paint(ctx, '#fff0b8', 0);
  for (const [x, y, s] of [[300, 160, 1], [1100, 110, 0.8], [1800, 200, 1.1]]) bg.cloud(ctx, x, y, s);
  bg.skyline(ctx, 720, '#e08f6f');
  bg.sea(ctx, t, 720);
  // towers behind deck
  for (const tx of [BR.cx - 560, BR.cx + 560]) bg.bridgeTower(ctx, tx, bg.deckY(tx, BR.cx, BR.base, BR.rise, BR.half), 520, 1);
  // main cables
  ctx.save(); ctx.lineCap = 'round';
  for (const [a, b, sag] of [[-600, BR.cx - 560, -0.6], [BR.cx - 560, BR.cx + 560, 1], [BR.cx + 560, 3000, -0.6]]) {
    const ya = bg.deckY(a, BR.cx, BR.base, BR.rise, BR.half) - 520, yb = bg.deckY(b, BR.cx, BR.base, BR.rise, BR.half) - 520;
    ctx.beginPath(); ctx.moveTo(a, a < 0 ? 700 : ya); ctx.quadraticCurveTo((a + b) / 2, sag > 0 ? Math.max(ya, yb) + 330 : Math.min(ya, yb) + 200, b, b > 2000 ? 700 : yb); paint(ctx, null, 14); ctx.beginPath(); ctx.moveTo(a, a < 0 ? 700 : ya); ctx.quadraticCurveTo((a + b) / 2, sag > 0 ? Math.max(ya, yb) + 330 : Math.min(ya, yb) + 200, b, b > 2000 ? 700 : yb); paint(ctx, null, 7, C.red);
  }
  ctx.restore();
  // suspenders
  ctx.strokeStyle = C.redD; ctx.lineWidth = 4;
  for (let x = BR.cx - 520; x < BR.cx + 540; x += 60) {
    const u = (x - BR.cx) / 560, cy = lerp(bg.deckY(BR.cx - 560, BR.cx, BR.base, BR.rise, BR.half) - 520, bg.deckY(BR.cx, BR.cx, BR.base, BR.rise, BR.half) - 520 + 165, 1 - u * u);
    ctx.beginPath(); ctx.moveTo(x, cy); ctx.lineTo(x, bg.deckY(x, BR.cx, BR.base, BR.rise, BR.half) - 30); ctx.stroke();
  }
  // deck
  ctx.beginPath(); for (let x = -800; x <= 3200; x += 40) ctx.lineTo(x, bg.deckY(x, BR.cx, BR.base, BR.rise, BR.half)); for (let x = 3200; x >= -800; x -= 40) ctx.lineTo(x, bg.deckY(x, BR.cx, BR.base, BR.rise, BR.half) + 44); ctx.closePath(); paint(ctx, C.tealD, 6);
  ctx.beginPath(); for (let x = -800; x <= 3200; x += 40) ctx.lineTo(x, bg.deckY(x, BR.cx, BR.base, BR.rise, BR.half) - 30); paint(ctx, null, 5);
  for (let x = -800; x <= 3200; x += 50) { const y = bg.deckY(x, BR.cx, BR.base, BR.rise, BR.half); ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x, y - 30); paint(ctx, null, 4); }
}
const deckAt = x => bg.deckY(x, BR.cx, BR.base, BR.rise, BR.half);
const deckRot = x => Math.atan2(deckAt(x + 5) - deckAt(x - 5), 10);
shot(49.0, 52.6, (ctx, lt, t) => {
  ctx.save(); cam(ctx, lerp(900, 1060, lt / 3.6), 540, 1);
  bridgeScene(ctx, t);
  const cx = lerp(-100, 1000, ease.inOut(lt / 3.6));
  carWith(ctx, { x: cx, y: deckAt(cx), s: 0.36, rot: deckRot(cx), face: 'happy', light: 1, t, wheel: t * 30, bounce: Math.sin(t * 18) * 3, bag: { x: -40, y: -238, s: 0.62 } }, crew({ t, bE: 'happy', bPose: 'eat', holding: 'fries', mE: 'grin', sweat: 0 }));
  fx.dust(ctx, cx - 80, deckAt(cx) - 10, (lt * 2.5) % 1, { n: 3, spread: 80, r: 18, seed: Math.floor(lt * 2.5) });
  const kx = cx - 520;
  copBike(ctx, { x: kx, y: deckAt(kx), s: 0.34, rot: deckRot(kx), pedal: t * 0.6, wheel: t * 3, expr: 'bored', light: t, t });
  ctx.restore();
}, [[0.0, 'gull', { n: 2 }]]);
setShift(0.8);

// ---- S17 out of gas -----------------------------------------------------------------------------------------
function bridgeSide(ctx, t, scroll, rot = 0, gY = 900) {
  const g = ctx.createLinearGradient(0, 0, 0, 700); g.addColorStop(0, '#ff7f5a'); g.addColorStop(1, '#ffd590');
  ctx.fillStyle = g; ctx.fillRect(-1500, -1500, 5000, 2500);
  bg.skyline(ctx, 640, '#e08f6f');
  bg.sea(ctx, t, 640);
  ctx.save(); ctx.translate(W / 2, gY); ctx.rotate(rot); ctx.translate(-W / 2, -gY);
  // suspender cables + rail
  ctx.strokeStyle = INK; ctx.lineWidth = 13; ctx.lineCap = 'butt';
  for (let x = -((scroll * 1) % 160) - 1600; x < W + 1600; x += 160) { ctx.beginPath(); ctx.moveTo(x, -900); ctx.lineTo(x, gY - 40); ctx.stroke(); }
  ctx.strokeStyle = C.red; ctx.lineWidth = 7;
  for (let x = -((scroll * 1) % 160) - 1600; x < W + 1600; x += 160) { ctx.beginPath(); ctx.moveTo(x, -900); ctx.lineTo(x, gY - 40); ctx.stroke(); }
  rrect(ctx, -1600, gY - 70, W + 3200, 20, 6); paint(ctx, C.red);
  for (let x = -((scroll * 1) % 60) - 1600; x < W + 1600; x += 60) { ctx.beginPath(); ctx.moveTo(x, gY - 52); ctx.lineTo(x, gY); paint(ctx, null, 5); }
  ctx.fillStyle = C.road; ctx.fillRect(-1600, gY, W + 3200, 600);
  ctx.beginPath(); ctx.moveTo(-1600, gY); ctx.lineTo(W + 1600, gY); paint(ctx, null, 6);
  ctx.fillStyle = C.lane; for (let x = -((scroll * 1.1) % 260) - 1560; x < W + 1600; x += 260) { rrect(ctx, x, gY + 120, 130, 14, 7); ctx.fill(); }
  ctx.restore();
}
shot(53.0, 54.4, (ctx, lt, t) => {
  const sc = t * 900 * (1 - seg(lt, 0, 1.4) * 0.6);
  ctx.save(); cam(ctx, 960, 540, 1);
  bridgeSide(ctx, t, sc, -0.05);
  const coughs = [0.15, 0.55, 0.95];
  let buck = 0; coughs.forEach(c => { buck += lt > c ? wobble(lt - c, 4, 7) * 0.12 : 0; });
  const cr = crew({ t, bE: 'worried', bPose: 'eat', holding: 'fries', mE: 'deadpan', sweat: 0.5 });
  ctx.save(); ctx.translate(W / 2, 900); ctx.rotate(-0.05); ctx.translate(-W / 2, -900);
  carWith(ctx, { x: 1000, y: 900, s: 1.15, face: 'worried', light: flick(t), t, wheel: sc / 40, sq: buck, bounce: -Math.abs(buck) * 60, bag: { x: -40, y: -238, s: 0.62 } }, cr);
  coughs.forEach((c, i) => { if (lt > c) { fx.dust(ctx, 1000 - 250, 840, seg(lt, c, c + 0.8), { n: 4, spread: 160, r: 36, col: '#3e3846', seed: 20 + i }); fx.sfxText(ctx, i < 2 ? 'PUTT!' : 'PUTT...', 620 - i * 90, 520 + i * 40, seg(lt, c, c + 0.5), { size: 70, fill: C.metal, rot: -0.1 }); } });
  ctx.restore();
  ctx.restore();
}, [[0.1, 'music_end', { id: 'C', how: 'tapestop', dur: 1.0 }], ...[0.15, 0.55, 0.95].map(c => [c, 'putt'])]);
shot(54.4, 55.2, (ctx, lt, t) => {
  ctx.fillStyle = '#26363b'; ctx.fillRect(0, 0, W, H);
  rrect(ctx, 360, 160, 1200, 760, 80); paint(ctx, '#33494f', 12);
  circle(ctx, 960, 600, 330); paint(ctx, '#fff6dc', 14);
  // ticks + labels
  for (let i = 0; i <= 8; i++) { const a = Math.PI + i * Math.PI / 8; ctx.beginPath(); ctx.moveTo(960 + Math.cos(a) * 280, 600 + Math.sin(a) * 280); ctx.lineTo(960 + Math.cos(a) * (i % 4 ? 250 : 220), 600 + Math.sin(a) * (i % 4 ? 250 : 220)); paint(ctx, null, i % 4 ? 6 : 10); }
  text(ctx, 'E', 700, 560, { size: 90, fill: C.red, lw: 8 }); text(ctx, 'F', 1220, 560, { size: 90, fill: INK, lw: 0 });
  text(ctx, 'FUEL', 960, 760, { size: 50, fill: C.tealD, lw: 0, font: 'Arial Black' });
  const k = ease.in(seg(lt, 0.1, 0.35));
  const a = Math.PI + lerp(Math.PI * 0.22, 0, k) + (lt > 0.35 ? wobble(lt - 0.35, 4, 6) * 0.15 : 0) - 0.06;
  ctx.save(); ctx.translate(960, 600); ctx.rotate(a); poly(ctx, [[0, -14], [270, -4], [270, 4], [0, 14]]); paint(ctx, C.red, 7); ctx.restore();
  circle(ctx, 960, 600, 36); paint(ctx, INK, 0);
  if (lt > 0.35 && Math.floor(lt * 8) % 2) { circle(ctx, 1400, 300, 40); paint(ctx, C.red, 8); }
}, [[0.12, 'needle_drop'], [0.36, 'boing', { pitch: 0.55 }]]);
shot(55.2, 56.4, (ctx, lt, t) => {
  const k = seg(lt, 0, 0.8);
  const sc = 54.4 * 900 * 0.4 + ease.out(k) * 220;
  ctx.save(); cam(ctx, 960, 540, 1);
  bridgeSide(ctx, t, sc, -0.05);
  ctx.save(); ctx.translate(W / 2, 900); ctx.rotate(-0.05); ctx.translate(-W / 2, -900);
  const look = lt > 0.75 ? [-1, 0] : [1, 0];
  const cr = crew({ t, bE: lt > 0.75 ? 'shock' : 'worried', bL: lt > 0.75 ? [-1, 0] : [0, 0], mE: lt > 0.75 ? 'deadpan' : 'deadpan', mL: [1, 0], sweat: 0.6 });
  carWith(ctx, { x: 1000, y: 900, s: 1.15, face: 'dizzy', light: 0, t, wheel: sc / 40, tilt: k < 1 ? 0.03 * Math.sin(k * Math.PI) : 0, bag: { x: -40, y: -238, s: 0.62 } }, cr);
  // steam from the hood
  for (let i = 0; i < 3; i++) { const kk = (lt * 1.4 + i / 3) % 1; fx.puff(ctx, 1000 + 160 + i * 14, 900 - 180 - kk * 140, 16 + kk * 22, '#ffffff', (1 - kk) * 0.8); }
  ctx.restore();
  ctx.restore();
}, [[0.0, 'roll_stop'], [0.2, 'music', { id: 'T', style: 'tension' }], [0.5, 'steam_hiss'], [0.8, 'cricket', { dur: 0.6 }]]);

// ---- S18 the cop approaches, slowly ----------------------------------------------------------------------
shot(56.4, 57.8, (ctx, lt, t) => {
  ctx.save(); cam(ctx, 960, 560, 0.85);
  bridgeSide(ctx, t, 54.4 * 900 * 0.4 + 220, -0.05, 900);
  ctx.save(); ctx.translate(W / 2, 900); ctx.rotate(-0.05); ctx.translate(-W / 2, -900);
  carWith(ctx, { x: 1700, y: 900, s: 1.0, face: 'scared', look: [-1, 0], light: 0, t, bag: { x: -40, y: -238, s: 0.62 } }, crew({ t, bE: 'shock', bL: [-1, 0], mE: 'shock', mL: [-1, 0] }));
  copBike(ctx, { x: lerp(-260, 260, lt / 1.4), y: 900, s: 1.0, pedal: t * 0.55, wheel: t * 3, expr: 'bored', light: t, t });
  ctx.restore();
  ctx.restore();
  fx.sirenWash(ctx, t, 0.7);
}, [[0.0, 'siren_slow', { dur: 1.4 }], [0.2, 'bike_squeak', { n: 2, gap: 0.6 }]]);
shot(57.8, 59.0, (ctx, lt, t) => {
  ctx.save(); cam(ctx, 1000 - 50, 900 - 220, 2.6);
  bridgeSide(ctx, t, 54.4 * 900 * 0.4 + 220, 0, 900);
  const yell = lt > 0.45;
  carWith(ctx, { x: 1000, y: 900, s: 1.0, face: 'scared', look: [-1, 0], light: 0, t, bag: { x: -40, y: -238, s: 0.62 } }, crew({ t, bE: 'panic', bL: yell ? [-0.6, 0] : [-1, 0], mE: yell ? 'yell' : 'shock', mL: [-1, 0], sweat: 1 }));
  if (yell) fx.sfxText(ctx, 'រុញទៅ!', 840, 600, seg(lt, 0.45, 1.2), { size: 70, fill: C.red, rot: -0.1, wob: 3, font: 'Koulen' });
  ctx.restore();
  fx.sirenWash(ctx, t, 0.6);
}, [[0.45, 'v_marge_push']]);

// ---- S19 PUSH: up the bridge arch ------------------------------------------------------------------------
const PUSH_N = 6;
shot(59.0, 66.0, (ctx, lt, t) => {
  const crest = seg(lt, 5.6, 6.4);
  const rot = lerp(-0.13, 0, ease.inOut(crest));
  const cyc = lt / 0.92, ci = Math.floor(cyc), cp = cyc - ci; // push cycles
  const pushing = ci < PUSH_N;
  const adv = (Math.min(ci, PUSH_N) + (pushing ? ease.inOut(seg(cp, 0.35, 0.8)) : 0)) * 70;
  const zc = lerp(1.65, 1.15, ease.inOut(seg(lt, 5.2, 6.6)));
  ctx.save(); cam(ctx, lerp(900, 800, ease.inOut(seg(lt, 5.2, 6.6))), lerp(760, 640, ease.inOut(seg(lt, 5.2, 6.6))), zc, -rot * 0.4);
  bridgeSide(ctx, t, 54.4 * 900 * 0.4 + 220 + adv, rot, 900);
  ctx.save(); ctx.translate(W / 2, 900); ctx.rotate(rot); ctx.translate(-W / 2, -900);
  // the cop, way back, slowly gaining
  copBike(ctx, { x: lerp(-220, 120, lt / 7) - adv * 0.2, y: 900, s: 0.8, pedal: t * 0.5, wheel: t * 2, expr: 'bored', light: t, t });
  // squash/stretch: compress (wind up) then stretch (shove)
  const wind = pushing ? Math.sin(seg(cp, 0, 0.35) * Math.PI) : 0, shove = pushing ? Math.sin(seg(cp, 0.35, 0.85) * Math.PI) : 0;
  const carX = 1080;
  const done = lt > 5.6;
  const cr = crew({ t, swapped: true, benny: false, mE: done ? 'grin' : 'strain', mL: [1, 0], mHeadRot: -0.1 - shove * 0.25 });
  // Marge strains: neck stretch handled by headRot; car squashes on each shove
  carWith(ctx, { x: carX, y: 900, s: 1.05, face: done ? 'happy' : 'strain', light: 0, t, sq: shove * -0.05 + wind * 0.04, wheel: adv / 36, bag: { x: -40, y: -238, s: 0.62 } }, cr);
  if (!done) {
    const bsq = wind * 0.38 - shove * 0.34;
    benny(ctx, { x: carX - 1.05 * 200 - 70 - shove * 30 + wind * 26, y: 900, s: 1.0, pose: 'push', ph: t * 3, expr: 'strain', sweat: 1, t, sq: bsq });
    if (shove > 0.5) fx.speedStreaks(ctx, carX - 380, 860, 120, 60, t, { n: 3, dir: -1, col: INK, alpha: 0.4, lw: 4 });
    fx.dust(ctx, carX - 330, 895, cp, { n: 3, spread: 90, r: 26, seed: ci + 30 });
  } else {
    // pancake Benny on the road, wobbling back to shape later
    benny(ctx, { x: carX - 360, y: 900, s: 1.0, pose: 'stand', expr: 'strain', sq: 1.3 + wobble(lt - 5.6, 3, 4) * 0.3, t });
  }
  ctx.restore();
  ctx.restore();
  fx.sirenWash(ctx, t, 0.35);
}, [[0.0, 'music_end', { id: 'T' }], ...Array.from({ length: PUSH_N }, (_, i) => [[i * 0.92 + 0.42, 'heave_hit', { i }], [i * 0.92 + 0.35, 'grunt', { f0: 150, i, gain: 0.85, pan: -0.2 }], [i * 0.92 + 0.42, 'grunt', { f0: 225, i, vel: 0.8, gain: 0.55, pan: 0.25 }], [i * 0.92 + 0.45, 'creak', { i }]]).flat(), [5.6, 'flop'], [5.62, 'slide_down_short']]);

// ---- S20 over the crest... it rolls! -------------------------------------------------------------------------
shot(66.0, 70.0, (ctx, lt, t) => {
  ctx.save(); cam(ctx, BR.cx + 80 + ease.inOut(seg(lt, 1.2, 4)) * 260, 560, 1.55);
  bridgeScene(ctx, t);
  // car tips over the crest and rolls down the right side
  const roll = ease.in(seg(lt, 0.2, 4.0));
  const cx = BR.cx + 30 + roll * 900;
  const benK = seg(lt, 1.1, 1.75), dive = seg(lt, 1.75, 1.95);
  const inCar = dive >= 1;
  const cr = crew({ t, swapped: true, benny: inCar, bE: 'happy', mE: lt > 2.4 ? 'grin' : 'shock', sweat: 0 });
  carWith(ctx, { x: cx, y: deckAt(cx), s: 0.62, rot: deckRot(cx), face: lt > 2.2 ? 'happy' : 'shock', light: 0, t, wheel: roll * 40, bag: { x: -40, y: -238, s: 0.62 } }, cr);
  if (!inCar) {
    // Benny: un-pancakes, then sprints & dives in
    const bx0 = BR.cx - 220;
    let bx = bx0, s = 0.6, sq = 0, pose = 'stand', rot = 0, by;
    if (lt < 1.1) { sq = 1.3 * (1 - ease.elastic(seg(lt, 0.35, 1.05))); }
    else { pose = 'run'; bx = lerp(bx0, cx - 60, ease.in(benK)); if (dive > 0) { bx = lerp(cx - 60, cx - 40, dive); rot = 0.9 * dive; s = 0.6 * (1 - dive * 0.5); } }
    by = deckAt(bx) - (dive > 0 ? Math.sin(dive * Math.PI) * 60 + dive * 90 : 0);
    benny(ctx, { x: bx, y: by, s, sq, pose, ph: t * 4, rot: rot + deckRot(bx), expr: lt < 1.1 ? 'strain' : 'panic', sweat: 1, t });
  }
  const kx = lerp(BR.cx - 900, BR.cx - 240, seg(lt, 0.5, 4.0));
  copBike(ctx, { x: kx, y: deckAt(kx), s: 0.6, rot: deckRot(kx), pedal: t * 0.55, wheel: t * 3, expr: 'bored', light: t, t });
  if (lt > 2.4) fx.sfxText(ctx, 'យេ៎!', cx + 160, deckAt(cx) - 260, seg(lt, 2.4, 3.6), { size: 80, fill: C.yellow, rot: 0.1, font: 'Koulen' });
  ctx.restore();
}, [[0.2, 'creak_long'], [1.1, 'scramble', { dur: 0.7 }], [1.8, 'zip_up'], [1.95, 'car_bounce'], [2.3, 'music', { id: 'D', style: 'chase', bpm: 188, melody: 'shout', vel: 1.05 }], [2.4, 'v_wheee']]);

// ---- S21a downhill, gaining speed ------------------------------------------------------------------------
shot(70.0, 72.5, (ctx, lt, t) => {
  const rot = 0.16;
  ctx.save(); ctx.translate(W / 2, H / 2); ctx.rotate(rot); ctx.translate(-W / 2, -H / 2);
  bg.speedBG(ctx, t, { speed: 2400 + lt * 900, top: '#ff8f5a', mid: '#ffc46b', band: C.tealD, groundY: 900, horizon: 660 });
  const cr = crew({ t, swapped: true, bE: 'happy', mE: 'grin', sweat: 0 });
  carWith(ctx, { x: 980, y: 900, s: 1.55, face: 'happy', light: flick(t), t, wheel: t * 50, bounce: Math.sin(t * 22) * 5, tilt: -0.04, bag: { x: -40, y: -238, s: 0.62, rot: Math.sin(t * 14) * 0.08 } }, cr);
  fx.speedStreaks(ctx, 980 - 320, 740, 320, 320, t, { n: 7, dir: -1, alpha: 0.8 });
  ctx.restore();
}, [[0.0, 'wind', { dur: 2.5 }], [0.6, 'v_woohoo']]);
// ---- S21b head-on, flying down the hill --------------------------------------------------------------------
shot(72.5, 75.0, (ctx, lt, t) => {
  ctx.save(); ctx.translate(W / 2, H / 2); ctx.rotate(-0.08 + Math.sin(lt * 3) * 0.03); ctx.translate(-W / 2, -H / 2);
  perspStreet(ctx, t, { spd: 60, vpy: 560, h: 1.3 });
  radialLines(ctx, t, 960, 560, { spd: 3 });
  const z = ease.in3(seg(lt, 1.7, 2.5));
  carFront(ctx, { x: 960, y: 1020 + z * 900, s: 1.4 + z * 3.5, face: 'happy', light: flick(t), t, bounce: Math.abs(Math.sin(t * 10)) * -16, bennyExpr: 'happy', margeExpr: 'grin', shake: 2 });
  ctx.restore();
}, [[1.7, 'whoosh_by']]);

// ---- S22 into the parking lot: a PERFECT landing ----------------------------------------------------------
const PS = { x: 960, y: 700 };
function lotSet(ctx, t, { squads = true } = {}) {
  bg.sky(ctx, { horizon: 700, cloudX: t * 6, sun: false });
  bg.farCity(ctx, 100, 600);
  bg.midCity(ctx, 900, 700);
  bg.policeStation(ctx, PS.x, PS.y, 1.0, { t });
  ctx.fillStyle = '#6a7182'; ctx.fillRect(-1000, PS.y, 4000, 900);
  ctx.beginPath(); ctx.moveTo(-1000, PS.y); ctx.lineTo(3000, PS.y); paint(ctx, null, 6);
  // painted bays
  ctx.strokeStyle = C.lane; ctx.lineWidth = 9;
  for (let i = -3; i <= 4; i++) { const x = 960 + (i - 0.5) * 360; ctx.beginPath(); ctx.moveTo(x, PS.y + 30); ctx.lineTo(x - 30, PS.y + 330); ctx.stroke(); }
  if (squads) { bg.squadCar(ctx, 960 - 380, 960, 0.92, { t }); bg.squadCar(ctx, 960 + 380, 960, 0.92, { t, flip: true }); }
}
shot(75.0, 77.0, (ctx, lt, t) => {
  ctx.save(); cam(ctx, 960, 860, 1.5);
  lotSet(ctx, t, { squads: false });
  const fly = seg(lt, 0, 0.62), land = lt - 0.62;
  const p = arc([-160, 760], [960, 960], ease.out(fly), 280);
  const rot = fly < 1 ? lerp(-0.3, 0.12, fly) : wobble(land, 2, 5) * 0.06;
  const sq = land > 0 ? wobble(land, 2.6, 4.5) * 0.22 : -0.12 * fly;
  const cr = crew({ t, swapped: true, bE: land > 0.4 ? 'happy' : 'shock', mE: land > 0.4 ? 'grin' : 'shock', sweat: 0 });
  carWith(ctx, { x: p[0], y: p[1], s: 0.8, rot, sq, face: land > 0.5 ? 'happy' : 'shock', light: flick(t), t, wheel: lt * 30, bag: { x: -40, y: -238, s: 0.62, sq: land > 0 ? wobble(land, 3, 5) * 0.3 : 0 } }, cr);
  if (fly < 1) fx.speedStreaks(ctx, p[0] - 200, p[1] - 100, 220, 160, t, { n: 5, dir: -1, col: INK, alpha: 0.4 });
  fx.dust(ctx, 960, 960, seg(land, 0, 0.9), { n: 7, spread: 260, r: 50, seed: 15, dir: 1 });
  fx.dust(ctx, 960, 960, seg(land, 0, 0.9), { n: 7, spread: 260, r: 50, seed: 16, dir: -1 });
  fx.sfxText(ctx, 'BOING!', 960, 600, seg(land, 0, 0.7), { size: 80, fill: C.yellow, rot: 0.08 });
  if (land > 0.8) fx.sfxText(ctx, 'PERFECT.', 1180, 640, seg(land, 0.8, 1.38), { size: 54, fill: '#fff', rot: -0.05 });
  ctx.restore();
}, [[0.0, 'whoosh_by'], [0.62, 'land_thud'], [0.64, 'boing', { pitch: 0.75 }], [1.1, 'ta_da'], [1.1, 'music_end', { id: 'D' }]]);
shot(77.0, 78.6, (ctx, lt, t) => {
  ctx.save(); cam(ctx, 960 - 60, 960 - 170, 2.5);
  lotSet(ctx, t, { squads: false });
  const hop = Math.abs(Math.sin(lt * 9)) * -10;
  const cr = crew({ t, swapped: true, bE: 'happy', bL: [1, -0.5], mE: 'grin', mL: [-1, 0], sweat: 0 });
  carWith(ctx, { x: 960, y: 960, s: 0.8, face: 'happy', light: 1, t, bounce: hop, bag: { x: -40, y: -238, s: 0.62 } }, cr);
  fx.sfxText(ctx, 'ហ៊ូរ៉េ!', 960 + 40, 960 - 330, seg(lt, 0.3, 1.5), { size: 70, fill: C.yellow, rot: -0.08, wob: 3, font: 'Koulen' });
  for (let i = 0; i < 6; i++) { const k = (lt * 0.9 + i / 6) % 1, a = i * 1.05; fx.puff(ctx, 960 + Math.cos(a) * (120 + k * 60) - 20, 960 - 230 - k * 90 + Math.sin(a) * 30, 7, [C.yellow, C.red, C.tealL][i % 3], 1 - k); }
  ctx.restore();
}, [[0.1, 'music', { id: 'V', style: 'vamp', bpm: 188 }], [0.3, 'v_woohoo2'], [0.35, 'ta_da_small']]);
shot(78.6, 80.4, (ctx, lt, t) => {
  const k = ease.inOut(seg(lt, 0.0, 1.1));
  ctx.save(); cam(ctx, 960, lerp(790, 540, k), lerp(2.5, 0.92, k));
  lotSet(ctx, t, { squads: true });
  const fall = lt > 1.25;
  const cr = crew({ t, swapped: true, bE: fall ? 'shock' : 'happy', bL: [0.5, -1], mE: fall ? 'shock' : 'grin', mL: [0.3, -1], sweat: fall ? 1 : 0 });
  carWith(ctx, { x: 960, y: 960, s: 0.8, face: fall ? 'scared' : 'happy', look: fall ? [0.3, -1] : [1, 0], light: 1, t, bag: { x: -40, y: -238, s: 0.62 } }, cr);
  ctx.restore();
}, [[0.0, 'pan_up_whoosh'], [1.15, 'record_scratch'], [1.15, 'music_end', { id: 'V' }]]);

// ---- S23 the bike cop rolls in. Ding. ----------------------------------------------------------------------
const S23cam = lt => { const k = ease.inOut(seg(lt, 1.2, 2.5)); return [lerp(860, 830, k), lerp(720, 840, k), lerp(1.25, 1.8, k)]; };
shot(80.4, 85.0, (ctx, lt, t) => {
  const [ccx, ccy, cz] = S23cam(lt);
  ctx.save(); cam(ctx, ccx, ccy, cz);
  lotSet(ctx, t, { squads: true });
  const arrive = ease.out(seg(lt, 0.0, 1.3));
  const kx = lerp(-260, 640, arrive);
  const ring = lt > 2.55 && lt < 2.75 ? 1 : 0;
  const cr = crew({ t, swapped: true, bE: lt > 1.7 ? 'gulp' : 'shock', bL: [-1, 0], mE: lt > 1.9 ? 'grin' : 'shock', mL: [-1, 0], sweat: 1 });
  carWith(ctx, { x: 960, y: 960, s: 0.8, face: lt > 3.6 ? 'sad' : 'scared', look: [-1, 0], light: lt > 3.6 ? 0 : 1, t, bag: { x: -40, y: -238, s: 0.62 } }, cr);
  copBike(ctx, { x: kx, y: 1045, s: 0.95, pedal: 0.6 * Math.min(lt, 1.3) * (1 - seg(lt, 0.8, 1.3) * 0.5), wheel: arrive * 12, expr: lt > 1.6 ? 'look' : 'bored', look: [1, 0], light: t, bell: ring, t, sirenOn: false });
  if (lt > 2.6) {
    const life = seg(lt, 2.6, 3.8);
    const bx = kx + 0.95 * 58, by = 1045 - 0.95 * 196;
    ctx.save(); ctx.globalAlpha = 1 - life;
    for (let i = 0; i < 3; i++) { ctx.beginPath(); ctx.arc(bx, by, 26 + i * 18 + life * 40, -2.2, -0.9); paint(ctx, null, 5, C.yellow); }
    ctx.restore();
    fx.sfxText(ctx, 'ding.', bx + 40, by - 120, life, { size: 60, fill: C.yellow, rot: -0.05 });
  }
  ctx.restore();
}, [[0.0, 'bike_squeak', { n: 2, gap: 0.5 }], [1.1, 'brake_squeak'], [1.7, 'gulp'], [2.6, 'bell']]);

// ---- S24 iris out ---------------------------------------------------------------------------------------------
shot(85.0, 87.2, (ctx, lt, t) => {
  ctx.save(); cam(ctx, 830, 840, 1.8);
  lotSet(ctx, t, { squads: true });
  const cr = crew({ t, swapped: true, bE: 'sheepish', bL: [0, 0], mE: 'deadpan', mL: [-1, 0], sweat: 0.5 });
  const eyeLook = lt > 1.0 ? [0, 0.3] : [-1, 0];
  carWith(ctx, { x: 960, y: 960, s: 0.8, face: lt > 1.25 ? 'grimace' : 'sad', look: eyeLook, light: lt > 1.0 && lt < 1.12 ? 1 : 0, t, bag: { x: -40, y: -238, s: 0.62 } }, cr);
  copBike(ctx, { x: 640, y: 1045, s: 0.95, pedal: 0.6 * 1.3 * 0.5, wheel: 12, expr: 'look', look: [1, 0], light: t, t, sirenOn: false });
  ctx.restore();
  // iris on the car's face
  const ex = W / 2 + (960 + 0.8 * 168 - 830) * 1.8, ey = H / 2 + (960 - 0.8 * 122 - 840) * 1.8;
  const r = lt < 1.0 ? lerp(1900, 150, ease.inOut(lt / 1.0)) : lt < 1.75 ? 150 : lerp(150, 0, ease.in(seg(lt, 1.75, 2.0)));
  fx.iris(ctx, ex, ey, r);
}, [[0.1, 'sad_trombone'], [1.35, 'meep'], [1.78, 'iris_snap']]);
// ---- S25 the end ----------------------------------------------------------------------------------------------
shot(87.2, 89.2, (ctx, lt, t) => {
  ctx.fillStyle = '#0d0a10'; ctx.fillRect(0, 0, W, H);
  const k = ease.back(seg(lt, 0.25, 0.65));
  if (k > 0) {
    ctx.save(); ctx.globalAlpha = 1 - seg(lt, 1.6, 2.0); ctx.translate(960, 520); ctx.scale(k, k);
    text(ctx, 'THE END', 0, 0, { size: 170, fill: C.yellow, lw: 14 });
    ctx.restore();
  }
}, [[0.25, 'end_button']]);



export { drawFrame, allCues } from './kit.mjs';
export const DURATION = duration();
