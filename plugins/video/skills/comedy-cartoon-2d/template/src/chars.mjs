// Example cast (from Getaway Car): Benny, Marge, the Cop on his bike, the Car with a face, ducks, loot.
// Reuse them, or copy a rig as the starting point for a new character (references/engine.md §7).
import { C, INK, LW, TAU, paint, circle, oval, rrect, poly, smooth, hose, cel, clipTo, text, ik, clamp, lerp, jit, hash } from './core.mjs';

const BROW = '#4a2a1c';

// ---------------------------------------------------------------- loot
export function bag(ctx, x, y, s = 1, rot = 0, sq = 0, open = 0) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s * (1 + sq), s / (1 + sq));
  const body = () => smooth(ctx, [[0, -118], [38, -100], [70, -60], [74, -20], [52, 0], [0, 4], [-52, 0], [-74, -20], [-70, -60], [-38, -100]]);
  cel(ctx, body, C.sack, C.sackD, -10, -8);
  // patches & stitches
  ctx.save(); body(); ctx.clip();
  rrect(ctx, -60, -46, 26, 22, 4); paint(ctx, C.sackD, 4);
  ctx.restore();
  // neck + tie
  smooth(ctx, [[-16, -112], [0, -118], [16, -112], [22, -136], [0, -132], [-22, -136]]); paint(ctx, C.sack, LW * 0.8);
  rrect(ctx, -22, -122, 44, 12, 6); paint(ctx, C.redD, 5);
  if (open > 0) { for (let i = 0; i < 3; i++) bill(ctx, -12 + i * 12, -138 - open * 10, 0.35, -0.4 + i * 0.4, 1); }
  text(ctx, '$', 2, -46, { size: 70, font: 'Arial Black', fill: C.moneyD, lw: 7 });
  ctx.restore();
}
export function bill(ctx, x, y, s = 1, rot = 0, flipX = 1) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s * (Math.abs(flipX) < 0.08 ? 0.08 * Math.sign(flipX || 1) : flipX), s);
  rrect(ctx, -60, -30, 120, 60, 6); paint(ctx, C.money, 6);
  rrect(ctx, -48, -20, 96, 40, 4); paint(ctx, null, 3, C.moneyD);
  circle(ctx, 0, 0, 15); paint(ctx, C.moneyD, 0);
  text(ctx, '$', 0, 2, { size: 26, font: 'Arial Black', fill: C.money, lw: 0 });
  ctx.restore();
}

// ---------------------------------------------------------------- BENNY
// origin: feet center, facing right. ~200 tall at s=1
export function benny(ctx, o = {}) {
  const { x = 0, y = 0, s = 1, flip = false, rot = 0, sq = 0, pose = 'stand', expr = 'worried', look = [1, 0], ph = 0, sweat = 0, t = 0, blush = 0 } = o;
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s * (flip ? -1 : 1) * (1 + sq), s / (1 + sq));
  // ---- rig
  let bodyRot = 0, head = [6, -165], headRot = 0, legs = [[[-18, -34], [-22, 0]], [[18, -34], [24, 0]]];
  let arms = [[[-34, -112], [-54, -58]], [[30, -112], [54, -60]]], grip = false, armsBent = [null, null];
  if (pose === 'run') {
    const p = ph * TAU; bodyRot = 0.18;
    legs = [[[-14, -34], [Math.cos(p) * 38 - 4, -Math.max(0, Math.sin(p)) * 34]], [[16, -34], [-Math.cos(p) * 38 + 8, -Math.max(0, -Math.sin(p)) * 34]]];
    arms = [[[-30, -112], [-30 + Math.cos(p) * 40, -88 + Math.sin(p) * 14]], [[30, -112], [30 - Math.cos(p) * 40, -88 - Math.sin(p) * 14]]];
  } else if (pose === 'drive') {
    arms = [[[-24, -112], [o.wheel?.[0] ?? 70, o.wheel?.[1] ?? -112]], [[30, -110], [(o.wheel?.[0] ?? 70) + 16, (o.wheel?.[1] ?? -112) + 6]]];
    armsBent = [[20, -80], [40, -78]]; grip = true;
  } else if (pose === 'push') {
    bodyRot = 0.55; head = [30, -158];
    legs = [[[-20, -34], [-96, 0]], [[14, -34], [-40 + Math.sin(ph * TAU) * 16, -Math.max(0, Math.sin(ph * TAU)) * 10]]];
    arms = [[[-10, -118], [96, -128]], [[34, -112], [104, -112]]]; grip = true;
  } else if (pose === 'grip') { // close-up: both hands on the wheel rim
    arms = [[[-34, -112], o.hands[0]], [[30, -112], o.hands[1]]]; grip = true;
  } else if (pose === 'armsUp') {
    arms = [[[-34, -112], [-70, -200 + Math.sin(ph * TAU) * 14]], [[30, -112], [66, -204 - Math.sin(ph * TAU) * 14]]];
  } else if (pose === 'signal') {
    arms = [[[-24, -112], [70, -112]], [[30, -112], [100, -190]]]; armsBent = [[20, -80], [86, -110]];
  } else if (pose === 'eat') {
    arms = [[[-24, -112], [70, -112]], [[30, -112], [56, -146]]]; armsBent = [[20, -80], [70, -100]]; grip = true;
  } else if (pose === 'flat') { // squashed pancake after pushing
    bodyRot = 0; head = [40, -60]; headRot = 1.2;
  }
  const bodyC = [0, -82];
  ctx.save(); ctx.translate(0, -34); ctx.rotate(bodyRot); ctx.translate(0, 34);
  // back arm + back leg
  if (pose !== 'flat') {
    hose(ctx, armsBent[0] ? [arms[0][0], armsBent[0], arms[0][1]] : arms[0], 15, C.navy);
    hand(ctx, arms[0][1][0], arms[0][1][1], 12, grip);
  }
  ctx.restore();
  if (pose !== 'flat') for (const [hp, ft] of legs.slice(0, 1)) { hose(ctx, [hp, ft], 20, C.navyD); shoe(ctx, ft[0], ft[1], 1); }
  ctx.save(); ctx.translate(0, -34); ctx.rotate(bodyRot); ctx.translate(0, 34);
  // body: striped round shirt
  const bodyP = () => oval(ctx, bodyC[0], bodyC[1], 58, 58);
  ctx.save(); bodyP(); ctx.fillStyle = C.white; ctx.fill(); ctx.clip();
  ctx.fillStyle = C.navy; for (let yy = -150; yy < 0; yy += 22) ctx.fillRect(-80, yy, 160, 11);
  ctx.fillStyle = 'rgba(30,20,60,0.22)';
  ctx.beginPath(); ctx.rect(-100, -160, 200, 200); ctx.ellipse(bodyC[0] - 10, bodyC[1] - 10, 56, 56, 0, 0, TAU, true); ctx.fill();
  ctx.restore(); bodyP(); paint(ctx, null);
  ctx.restore();
  if (pose !== 'flat') for (const [hp, ft] of legs.slice(1)) { hose(ctx, [hp, ft], 20, C.navyD); shoe(ctx, ft[0], ft[1], 1); }
  ctx.save(); ctx.translate(0, -34); ctx.rotate(bodyRot); ctx.translate(0, 34);
  // head
  ctx.save(); ctx.translate(head[0], head[1]); ctx.rotate(headRot);
  bennyHead(ctx, expr, look, t, sweat, blush);
  ctx.restore();
  // front arm
  if (pose !== 'flat') {
    hose(ctx, armsBent[1] ? [arms[1][0], armsBent[1], arms[1][1]] : arms[1], 15, C.navy);
    hand(ctx, arms[1][1][0], arms[1][1][1], 12, grip, o.holding);
  }
  ctx.restore();
  ctx.restore();
}
function shoe(ctx, x, y, s = 1) { oval(ctx, x + 8 * s, y - 8, 20, 11); paint(ctx, INK, 0); oval(ctx, x + 4 * s, y - 11, 8, 4); paint(ctx, '#5a5060', 0); }
export function hand(ctx, x, y, r, grip = false, holding = null) {
  if (holding === 'fries') fries(ctx, x, y - 14, 0.5);
  circle(ctx, x, y, r); paint(ctx, C.skin, LW * 0.8);
  if (grip) { // white knuckles
    ctx.strokeStyle = '#fff'; ctx.lineWidth = 3.5; ctx.lineCap = 'round';
    for (let i = -1; i <= 1; i++) { ctx.beginPath(); ctx.arc(x + i * 6, y - 5, 3, Math.PI, TAU); ctx.stroke(); }
  }
}
export function fries(ctx, x, y, s = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const cols = [-22, -12, -2, 8, 18];
  cols.forEach((cx, i) => { rrect(ctx, cx - 5, -70 - (i % 2) * 10, 10, 60, 3); paint(ctx, C.yellow, 4); });
  poly(ctx, [[-34, -30], [34, -30], [26, 30], [-26, 30]]); paint(ctx, C.red, 6);
  text(ctx, 'BB', 0, 2, { size: 24, font: 'Arial Black', fill: C.yellow, lw: 0 });
  ctx.restore();
}
function bennyHead(ctx, expr, look, t, sweat, blush) {
  // ear
  oval(ctx, -44, 4, 12, 15); paint(ctx, C.skin);
  // head
  const hp = () => oval(ctx, 0, 0, 52, 50);
  cel(ctx, hp, C.skin, C.skinD, -8, -8);
  if (blush > 0 || expr === 'strain') { ctx.save(); hp(); ctx.clip(); ctx.fillStyle = `rgba(232,67,58,${expr === 'strain' ? 0.45 : blush * 0.4})`; ctx.fillRect(-60, -60, 120, 120); ctx.restore(); hp(); paint(ctx, null); }
  // stubble shadow
  ctx.save(); hp(); ctx.clip(); oval(ctx, 22, 34, 40, 18); ctx.fillStyle = 'rgba(80,60,90,0.18)'; ctx.fill(); ctx.restore();
  // eyes
  const lx = look[0] * 4, ly = look[1] * 4;
  const E = [[12, -10], [38, -8]];
  const big = expr === 'panic' || expr === 'shock' || expr === 'gulp' ? 1.25 : 1;
  if (expr === 'strain') {
    for (const [ex, ey] of E) { ctx.beginPath(); ctx.moveTo(ex - 10, ey - 6); ctx.lineTo(ex + 2, ey); ctx.lineTo(ex - 10, ey + 6); paint(ctx, null, 5); }
  } else {
    for (const [ex, ey] of E) {
      oval(ctx, ex, ey, 12 * big, 16 * big); paint(ctx, '#fff', 5);
      const pr = expr === 'shock' ? 3 : expr === 'panic' ? 4 : 5.5;
      circle(ctx, ex + 2 + lx, ey + 2 + ly, pr); paint(ctx, INK, 0);
      if (expr === 'sheepish' || expr === 'bored') { ctx.save(); oval(ctx, ex, ey, 12, 16); ctx.clip(); ctx.fillStyle = C.skinD; ctx.fillRect(ex - 14, ey - 18, 28, 14); ctx.restore(); oval(ctx, ex, ey, 12, 16); paint(ctx, null, 5); }
    }
  }
  // brows: big, bushy, sweaty
  const browA = { worried: 0.45, panic: 0.6, shock: 0.25, gulp: 0.5, determined: -0.5, strain: -0.35, sheepish: 0.35, happy: 0.2, flat: 0 }[expr] ?? 0.3;
  const browY = { panic: -40, shock: -44, happy: -36 }[expr] ?? -34;
  ctx.lineCap = 'round'; ctx.strokeStyle = BROW;
  for (const [i, [ex]] of E.entries()) {
    const dir = i === 0 ? -1 : 1;
    ctx.save(); ctx.translate(ex + (i === 0 ? -2 : 2), browY + (i === 0 ? 0 : 2)); ctx.rotate(dir * browA);
    ctx.lineWidth = 14 + 2 * LW / 2; ctx.strokeStyle = INK; ctx.beginPath(); ctx.moveTo(-12, 0); ctx.lineTo(12, 0); ctx.stroke();
    ctx.lineWidth = 12; ctx.strokeStyle = BROW; ctx.beginPath(); ctx.moveTo(-12, 0); ctx.lineTo(12, 0); ctx.stroke();
    ctx.restore();
  }
  // nose
  oval(ctx, 54, 6, 15, 13); paint(ctx, '#f19a86');
  oval(ctx, 50, 1, 5, 3); paint(ctx, 'rgba(255,255,255,0.7)', 0);
  // mouth
  ctx.save(); ctx.translate(30, 28);
  if (expr === 'panic' || expr === 'shock') { oval(ctx, 0, 4, 12, expr === 'shock' ? 14 : 11); paint(ctx, '#6a1f2a', 5); }
  else if (expr === 'strain' || expr === 'determined') { rrect(ctx, -14, -6, 28, 12, 4); paint(ctx, '#fff', 4.5); ctx.beginPath(); ctx.moveTo(-14, 0); ctx.lineTo(14, 0); for (let i = -7; i <= 7; i += 7) { ctx.moveTo(i, -6); ctx.lineTo(i, 6); } paint(ctx, null, 2.5); }
  else if (expr === 'happy') { ctx.beginPath(); ctx.moveTo(-14, -4); ctx.quadraticCurveTo(0, 20, 16, -4); ctx.closePath(); paint(ctx, '#6a1f2a', 5); }
  else if (expr === 'sheepish') { ctx.beginPath(); ctx.moveTo(-10, 0); ctx.quadraticCurveTo(2, 7, 12, -2); paint(ctx, null, 5); }
  else if (expr === 'gulp') { ctx.beginPath(); ctx.moveTo(-10, 0); ctx.lineTo(10, 0); paint(ctx, null, 5); }
  else { ctx.beginPath(); ctx.moveTo(-12, 2); ctx.quadraticCurveTo(-6, -4, 0, 2); ctx.quadraticCurveTo(6, 8, 12, 0); paint(ctx, null, 4.5); }
  ctx.restore();
  // tiny striped beanie perched on top
  ctx.save(); ctx.translate(-6, -46); ctx.rotate(-0.12);
  const bp = () => { ctx.beginPath(); ctx.moveTo(-26, 4); ctx.bezierCurveTo(-26, -30, 26, -30, 26, 4); ctx.closePath(); };
  ctx.save(); bp(); ctx.fillStyle = C.red; ctx.fill(); ctx.clip(); ctx.fillStyle = '#fff'; for (let yy = -28; yy < 6; yy += 10) ctx.fillRect(-30, yy, 60, 5); ctx.restore();
  bp(); paint(ctx, null, LW * 0.8);
  rrect(ctx, -29, -2, 58, 11, 5); paint(ctx, C.redD, LW * 0.8);
  circle(ctx, 2, -26, 9); paint(ctx, '#fff', LW * 0.7);
  ctx.restore();
  // sweat
  if (sweat > 0) {
    for (let i = 0; i < 3; i++) {
      const k = ((t * 2.2 + i / 3) % 1);
      const sx = (i - 1) * 40 + (i - 1) * k * 40, sy = -40 - Math.sin(k * Math.PI) * 30 + k * 50;
      ctx.globalAlpha = sweat * (1 - k * 0.6);
      drop(ctx, sx, sy, 0.8 + 0.3 * (i % 2), (i - 1) * 0.6);
      ctx.globalAlpha = 1;
    }
    drop(ctx, -36, -18, 0.9, -0.3); drop(ctx, 46, -26, 0.7, 0.4);
  }
}
export function drop(ctx, x, y, s = 1, rot = 0) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  ctx.beginPath(); ctx.moveTo(0, -14); ctx.bezierCurveTo(6, -4, 9, 2, 9, 6); ctx.arc(0, 6, 9, 0, Math.PI); ctx.bezierCurveTo(-9, 2, -6, -4, 0, -14); paint(ctx, '#9fe3f5', 4);
  oval(ctx, -3, 5, 2.5, 4); paint(ctx, '#fff', 0);
  ctx.restore();
}

// ---------------------------------------------------------------- MARGE
// origin: feet center, facing right. ~370 tall at s=1
export function marge(ctx, o = {}) {
  const { x = 0, y = 0, s = 1, flip = false, rot = 0, sq = 0, pose = 'stand', expr = 'smirk', look = [1, 0], ph = 0, t = 0, bagHeld = false } = o;
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s * (flip ? -1 : 1) * (1 + sq), s / (1 + sq));
  let hip = [0, -172], sh = [8, -282], headP = [18, -330], headRot = 0;
  let legs = [[[-6, -172], [-30, -86], [-26, 0]], [[8, -172], [24, -86], [26, 0]]];
  let arms = [[[-6, -276], [-34, -210], [-30, -150]], [[16, -276], [40, -214], [44, -152]]];
  if (pose === 'run') {
    const p = ph * TAU; hip = [0, -170]; sh = [30, -278]; headP = [44, -322];
    const leg = (q, off) => { const fx = Math.cos(q) * 80, fy = -Math.max(0, Math.sin(q)) * 60; return [[off, -170], [off + 30 + Math.cos(q) * 30, -100 - Math.max(0, Math.sin(q)) * 40], [fx + off, fy]]; };
    legs = [leg(p + Math.PI, -6), leg(p, 8)];
    arms = [[[24, -272], [0, -220], [-30 + Math.cos(p) * 30, -200]], [[36, -272], [70, -230], [90, -250 - Math.sin(p) * 10]]];
  } else if (pose === 'reach') { // long arm stretched out the window
    arms = [[[-6, -276], [-34, -210], [-30, -150]], [[16, -276], [lerp(60, o.reach[0] * 0.5, 0.5), lerp(-270, o.reach[1], 0.5) - 40], o.reach]];
  } else if (pose === 'facepalm') {
    arms = [[[-6, -276], [-34, -210], [-30, -150]], [[16, -276], [70, -250], [42, -334]]];
  } else if (pose === 'steer') { // seated, leaning forward
    sh = [40, -270]; headP = [62, -312];
    arms = [[[30, -264], [70, -230], [110, -222]], [[44, -262], [90, -240], [122, -214]]];
  } else if (pose === 'cheer') {
    arms = [[[-6, -276], [-50, -330], [-60, -400]], [[16, -276], [60, -340], [76, -404]]];
  }
  // back limbs
  hose(ctx, legs[0], 18, C.blackL); mshoe(ctx, legs[0][2][0], legs[0][2][1]);
  hose(ctx, arms[0], 14, C.blackL); glove(ctx, arms[0][2][0], arms[0][2][1]);
  // torso: lanky tapered
  const torso = () => smooth(ctx, [[hip[0] - 22, hip[1] + 6], [hip[0] + 24, hip[1] + 4], [(hip[0] + sh[0]) / 2 + 22, (hip[1] + sh[1]) / 2], [sh[0] + 30, sh[1] + 4], [sh[0], sh[1] - 12], [sh[0] - 28, sh[1] + 6], [(hip[0] + sh[0]) / 2 - 20, (hip[1] + sh[1]) / 2]]);
  cel(ctx, torso, C.black, '#1f1b27', -8, -6);
  // belt
  ctx.save(); torso(); ctx.clip(); ctx.fillStyle = '#5a3a2a'; ctx.fillRect(hip[0] - 40, hip[1] - 14, 80, 12); ctx.fillStyle = C.gold; ctx.fillRect(hip[0] - 6, hip[1] - 14, 12, 12); ctx.restore();
  hose(ctx, legs[1], 18, C.black); mshoe(ctx, legs[1][2][0], legs[1][2][1]);
  // neck + head
  hose(ctx, [[sh[0] + 2, sh[1]], [headP[0] - 8, headP[1] + 24]], 13, C.skin2);
  ctx.save(); ctx.translate(headP[0], headP[1]); ctx.rotate(headRot + (o.headRot || 0));
  margeHead(ctx, expr, look, t);
  ctx.restore();
  // front arm
  hose(ctx, arms[1], 14, C.black); glove(ctx, arms[1][2][0], arms[1][2][1]);
  if (bagHeld) bag(ctx, arms[1][2][0] + 30, arms[1][2][1] + 120, 0.75, 0.15);
  ctx.restore();
}
function mshoe(ctx, x, y) { ctx.beginPath(); ctx.moveTo(x - 12, y); ctx.quadraticCurveTo(x - 12, y - 16, x + 4, y - 16); ctx.quadraticCurveTo(x + 30, y - 10, x + 34, y); ctx.closePath(); paint(ctx, INK, 0); }
function glove(ctx, x, y) { circle(ctx, x, y, 11); paint(ctx, '#4a4458', LW * 0.8); }
function margeHead(ctx, expr, look, t) {
  // bun
  circle(ctx, -30, -34, 20); paint(ctx, C.hairRed);
  // head: long, pointy chin + long pointy nose
  const hp = () => smooth(ctx, [[-30, -10], [-22, -36], [6, -44], [30, -30], [36, -6], [32, 14], [18, 36], [4, 34], [-18, 22], [-30, 8]]);
  cel(ctx, hp, C.skin2, C.skin2D, -8, -6);
  // hair cap (back + fringe)
  ctx.save(); hp(); ctx.clip();
  smooth(ctx, [[-40, 10], [-34, -40], [10, -54], [36, -36], [26, -26], [4, -30], [-12, -18], [-18, 4]]); paint(ctx, C.hairRed, 0);
  ctx.restore(); hp(); paint(ctx, null);
  smooth(ctx, [[-36, 6], [-34, -34], [8, -48], [34, -32], [24, -24], [2, -30], [-14, -16], [-20, 6]], false); paint(ctx, null, LW * 0.6);
  // nose
  ctx.beginPath(); ctx.moveTo(30, -12); ctx.quadraticCurveTo(58, 4, 60, 10); ctx.quadraticCurveTo(46, 12, 32, 8); paint(ctx, C.skin2, LW * 0.8);
  // burglar mask
  ctx.save(); hp(); ctx.clip();
  ctx.beginPath(); ctx.moveTo(-40, -20); ctx.quadraticCurveTo(10, -30, 44, -22); ctx.lineTo(44, -2); ctx.quadraticCurveTo(10, -10, -40, 0); ctx.closePath(); ctx.fillStyle = INK; ctx.fill();
  ctx.restore();
  ctx.beginPath(); ctx.moveTo(-34, -16); ctx.lineTo(-52, -26); ctx.moveTo(-34, -8); ctx.lineTo(-54, -6); paint(ctx, null, 6);
  // eyes: half-lidded, overconfident
  const lx = look[0] * 3, ly = look[1] * 3;
  for (const ex of [6, 26]) {
    oval(ctx, ex, -13, 8, 6.5); paint(ctx, '#fff', 0);
    circle(ctx, ex + 2 + lx, -12 + ly, 3.6); paint(ctx, INK, 0);
    if (expr !== 'shock') { ctx.fillStyle = INK; ctx.fillRect(ex - 9, -21, 18, ({ deadpan: 7.5, angry: 6, blink: 15, strain: 11 })[expr] ?? 5); }
  }
  if (expr === 'angry') { ctx.beginPath(); ctx.moveTo(-2, -28); ctx.lineTo(16, -20); ctx.moveTo(20, -20); ctx.lineTo(36, -28); paint(ctx, null, 6, C.hairRedD); }
  // mouth
  ctx.save(); ctx.translate(14, 18);
  if (expr === 'smirk') { ctx.beginPath(); ctx.moveTo(-8, 2); ctx.quadraticCurveTo(6, 6, 16, -6); paint(ctx, null, 4.5); ctx.beginPath(); ctx.moveTo(14, -8); ctx.lineTo(19, -4); paint(ctx, null, 3); }
  else if (expr === 'deadpan' || expr === 'blink') { ctx.beginPath(); ctx.moveTo(-6, 2); ctx.lineTo(12, 2); paint(ctx, null, 4.5); }
  else if (expr === 'yell' || expr === 'angry') { oval(ctx, 4, 4, 12, 10); paint(ctx, '#6a1f2a', 4.5); rrect(ctx, -5, -5, 18, 5, 2); paint(ctx, '#fff', 0); }
  else if (expr === 'strain') { rrect(ctx, -8, -4, 24, 10, 3); paint(ctx, '#fff', 4); ctx.beginPath(); ctx.moveTo(-8, 1); ctx.lineTo(16, 1); paint(ctx, null, 2); }
  else if (expr === 'shock') { oval(ctx, 4, 4, 7, 10); paint(ctx, '#6a1f2a', 4.5); }
  else if (expr === 'grin') { ctx.beginPath(); ctx.moveTo(-8, -2); ctx.quadraticCurveTo(6, 14, 20, -6); ctx.closePath(); paint(ctx, '#fff', 4); }
  ctx.restore();
}

// ---------------------------------------------------------------- COP on bike
// origin: ground between wheels, facing right
export function copBike(ctx, o = {}) {
  const { x = 0, y = 0, s = 1, flip = false, rot = 0, pedal = 0, wheel = 0, expr = 'bored', bell = 0, light = 0, t = 0, look = [1, 0], sirenOn = true } = o;
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s * (flip ? -1 : 1), s);
  const RW = [-78, -56], FW = [84, -56], R = 56, crank = [0, -60];
  const a = pedal * TAU;
  const pf = [crank[0] + Math.cos(a) * 24, crank[1] + Math.sin(a) * 24];
  const pb = [crank[0] - Math.cos(a) * 24, crank[1] - Math.sin(a) * 24];
  const hip = [-26, -170];
  const legPts = p => { const k = ik(hip[0], hip[1], p[0], p[1] - 6, 70, 66, -1); return [hip, k, [p[0], p[1] - 6]]; };
  // back leg (behind frame)
  const lb = legPts(pb); limb2(ctx, lb, 18, C.copBlueD); cshoe(ctx, pb[0], pb[1]);
  // wheels
  for (const [cx, cy] of [RW, FW]) bikeWheel(ctx, cx, cy, R, wheel);
  // frame
  const seat = [-30, -150], head = [62, -150], bar = [54, -186];
  const frame = [[RW, crank], [crank, seat], [seat, RW], [crank, head], [seat, [head[0], head[1] - 6]], [head, FW], [head, bar]];
  for (const [p, q] of frame) hose(ctx, [p, q], 7, C.white, 4.5);
  circle(ctx, crank[0], crank[1], 14); paint(ctx, C.metal, 4.5);
  oval(ctx, seat[0] - 4, seat[1] - 6, 22, 8); paint(ctx, INK, 0);
  // basket + tiny siren beacon
  poly(ctx, [[70, -168], [126, -168], [118, -128], [78, -128]]); paint(ctx, '#c98a4a', 5);
  ctx.beginPath(); for (let i = 0; i < 4; i++) { ctx.moveTo(80 + i * 12, -166); ctx.lineTo(82 + i * 10, -130); } paint(ctx, null, 2.5);
  const flash = Math.floor(light * 8) % 2;
  if (sirenOn) {
    ctx.beginPath(); ctx.moveTo(84, -168); ctx.bezierCurveTo(84, -196, 112, -196, 112, -168); ctx.closePath(); paint(ctx, flash ? C.red : C.blue, 4.5);
    ctx.save(); ctx.globalAlpha = 0.35; circle(ctx, 98, -180, 34); ctx.fillStyle = flash ? C.red : C.blue; ctx.fill(); ctx.restore();
  }
  // handlebar
  hose(ctx, [[bar[0] - 8, bar[1]], [bar[0] + 22, bar[1] - 4]], 8, INK, 0);
  // bell
  ctx.save(); ctx.translate(bar[0] + 4, bar[1] - 10);
  ctx.beginPath(); ctx.arc(0, 0, 11, Math.PI, TAU); ctx.closePath(); paint(ctx, C.gold, 4);
  ctx.restore();
  // body
  const bodyP = () => smooth(ctx, [[-50, -160], [-60, -200], [-40, -250], [-4, -262], [20, -236], [24, -190], [8, -158]]);
  cel(ctx, bodyP, C.copBlue, C.copBlueD, -8, -6);
  ctx.fillStyle = INK; ctx.fillRect(-56, -176, 76, 12);
  star(ctx, 2, -228, 9);
  // front leg
  const lf = legPts(pf); limb2(ctx, lf, 18, C.copBlue); cshoe(ctx, pf[0], pf[1]);
  // arm to bar (thumb on bell)
  const hand = [bar[0] + (bell > 0 ? 6 : 0), bar[1] - (bell > 0 ? 6 + bell * 6 : 0)];
  hose(ctx, [[-14, -240], [30, -200], hand], 16, C.copBlue);
  circle(ctx, hand[0], hand[1], 12); paint(ctx, '#fff', LW * 0.8);
  // head
  ctx.save(); ctx.translate(-2, -292);
  copHead(ctx, expr, look, t);
  ctx.restore();
  ctx.restore();
}
function limb2(ctx, pts, w, col) {
  ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  const path = () => { ctx.beginPath(); ctx.moveTo(...pts[0]); ctx.lineTo(...pts[1]); ctx.lineTo(...pts[2]); };
  path(); ctx.strokeStyle = INK; ctx.lineWidth = w + LW * 2; ctx.stroke();
  path(); ctx.strokeStyle = col; ctx.lineWidth = w; ctx.stroke();
}
function cshoe(ctx, x, y) { oval(ctx, x + 6, y - 6, 16, 9); paint(ctx, INK, 0); }
function star(ctx, x, y, r) {
  ctx.beginPath(); for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * 0.45 : r; ctx.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); } ctx.closePath(); paint(ctx, C.gold, 3);
}
export function bikeWheel(ctx, cx, cy, R, ang) {
  circle(ctx, cx, cy, R); paint(ctx, null, 9);
  circle(ctx, cx, cy, R - 6); paint(ctx, null, 3, '#6b6875');
  ctx.save(); ctx.translate(cx, cy); ctx.rotate(ang);
  ctx.beginPath(); for (let i = 0; i < 8; i++) { const a = i * TAU / 8; ctx.moveTo(0, 0); ctx.lineTo(Math.cos(a) * (R - 6), Math.sin(a) * (R - 6)); } paint(ctx, null, 2, '#8a8794');
  ctx.restore();
  circle(ctx, cx, cy, 6); paint(ctx, C.metal, 3);
}
function copHead(ctx, expr, look, t) {
  oval(ctx, -30, 6, 10, 13); paint(ctx, C.skin);
  const hp = () => smooth(ctx, [[-30, -12], [0, -36], [32, -18], [38, 14], [20, 36], [-12, 34], [-32, 16]]);
  cel(ctx, hp, C.skin, C.skinD, -8, -6);
  // eyes: half-lidded, bored
  const lx = look[0] * 3, ly = look[1] * 2;
  for (const ex of [6, 26]) {
    oval(ctx, ex, -4, 8, 10); paint(ctx, '#fff', 4);
    circle(ctx, ex + 2 + lx, -1 + ly, 3.5); paint(ctx, INK, 0);
    const lid = expr === 'look' ? 4 : expr === 'yawn' ? 12 : 9;
    ctx.save(); oval(ctx, ex, -4, 8, 10); ctx.clip(); ctx.fillStyle = C.skinD; ctx.fillRect(ex - 10, -16, 20, lid); ctx.restore();
    ctx.beginPath(); ctx.moveTo(ex - 9, -16 + lid); ctx.lineTo(ex + 9, -16 + lid); paint(ctx, null, 4);
  }
  // nose
  oval(ctx, 40, 6, 13, 12); paint(ctx, '#f0a08a');
  // mouth / yawn
  if (expr === 'yawn') { oval(ctx, 20, 30, 12, 15); paint(ctx, '#6a1f2a', 4.5); }
  else { ctx.beginPath(); ctx.moveTo(14, 30); ctx.lineTo(30, 29); paint(ctx, null, 4); }
  // bushy mustache
  smooth(ctx, [[14, 18], [30, 12], [48, 18], [52, 28], [34, 24], [22, 26], [8, 30], [4, 22]]); paint(ctx, '#6b4a34', 4.5);
  // cap
  ctx.beginPath(); ctx.moveTo(-34, -14); ctx.lineTo(-30, -44); ctx.quadraticCurveTo(0, -60, 36, -42); ctx.lineTo(32, -16); ctx.closePath(); paint(ctx, C.navy);
  ctx.beginPath(); ctx.moveTo(18, -18); ctx.quadraticCurveTo(44, -22, 58, -12); ctx.lineTo(28, -12); ctx.closePath(); paint(ctx, INK, 4);
  ctx.fillStyle = '#1b2240'; ctx.fillRect(-32, -22, 64, 6);
  star(ctx, 10, -34, 8);
}

// ---------------------------------------------------------------- DUCKS
export function duck(ctx, x, y, s, ph, baby = false, flip = false, look = 0) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s * (flip ? -1 : 1), s);
  const w = Math.sin(ph * TAU) * 0.12, hop = Math.abs(Math.sin(ph * TAU)) * 6;
  // feet
  for (const k of [-1, 1]) { const fx = k * 12 + Math.sin(ph * TAU + (k > 0 ? 0 : Math.PI)) * 10; ctx.beginPath(); ctx.moveTo(fx - 8, 0); ctx.lineTo(fx + 16, 0); ctx.lineTo(fx + 2, -10); ctx.closePath(); paint(ctx, C.orange, 4); }
  ctx.translate(0, -hop); ctx.rotate(w);
  const body = baby ? '#ffe14d' : '#fff7e6', bodyD = baby ? '#e8b92a' : '#e8d8bf';
  const bp = () => smooth(ctx, [[-40, -30], [-10, -46], [30, -40], [40, -20], [24, -6], [-20, -6], [-48, -18], [-56, -40]]);
  cel(ctx, bp, body, bodyD, -6, -6);
  // wing
  smooth(ctx, [[-28, -30], [6, -36], [16, -22], [-14, -16]]); paint(ctx, bodyD, 4);
  // head
  ctx.save(); ctx.translate(30, -62); ctx.rotate(look);
  circle(ctx, 0, 0, 20); paint(ctx, body);
  ctx.beginPath(); ctx.moveTo(14, -2); ctx.quadraticCurveTo(40, -4, 40, 6); ctx.quadraticCurveTo(28, 12, 14, 8); ctx.closePath(); paint(ctx, C.orange, 4.5);
  circle(ctx, 6, -5, 4.5); paint(ctx, INK, 0);
  if (baby) { ctx.beginPath(); ctx.moveTo(-4, -20); ctx.quadraticCurveTo(0, -30, 6, -22); paint(ctx, null, 3.5); }
  ctx.restore();
  ctx.restore();
}

// ---------------------------------------------------------------- THE CAR (side view)
// origin: ground center between wheels, facing right. ~380 long, ~245 tall (without bag)
const carBody = ctx => {
  ctx.beginPath();
  ctx.moveTo(-180, -60);
  ctx.bezierCurveTo(-190, -100, -188, -140, -172, -162);
  ctx.bezierCurveTo(-160, -196, -150, -222, -122, -234);
  ctx.bezierCurveTo(-60, -246, 20, -246, 56, -234);
  ctx.bezierCurveTo(82, -224, 100, -190, 120, -160);
  ctx.bezierCurveTo(152, -154, 182, -146, 190, -120);
  ctx.bezierCurveTo(196, -100, 194, -76, 186, -58);
  ctx.lineTo(160, -56);
  ctx.arc(115, -48, 46, -0.15, Math.PI + 0.15, true);
  ctx.lineTo(-70, -56);
  ctx.arc(-115, -48, 46, -0.15, Math.PI + 0.15, true);
  ctx.closePath();
};
const REAR = [[-154, -164], [-140, -208], [-112, -224], [-60, -230], [-22, -230], [-22, -164]];
const FRONT = [[-6, -164], [-6, -230], [44, -228], [72, -212], [104, -166]];
const rearWin = (ctx, np = true) => smooth(ctx, REAR, true, 0.5, np);
const frontWin = (ctx, np = true) => smooth(ctx, FRONT, true, 0.5, np);
export const CAR = { rearWin, frontWin, body: carBody };

export function carWheel(ctx, cx, cy, ang, r = 36) {
  circle(ctx, cx, cy, r); paint(ctx, C.tire);
  circle(ctx, cx, cy, r * 0.48); paint(ctx, C.metal, 5);
  ctx.save(); ctx.translate(cx, cy); ctx.rotate(ang);
  for (let i = 0; i < 4; i++) { const a = i * TAU / 4; circle(ctx, Math.cos(a) * r * 0.27, Math.sin(a) * r * 0.27, 3); paint(ctx, C.metalD, 0); }
  ctx.beginPath(); ctx.moveTo(-r * 0.8, 0); ctx.arc(0, 0, r * 0.8, Math.PI, Math.PI * 1.35); paint(ctx, null, 3, C.tireL);
  ctx.restore();
}

// o: {x,y,s,flip,rot,sq, bounce (body offset y), wheel (angle), face, look, light (0..1), crew: {benny:{..}, marge:{..}} | null,
//     bag: {x,y,rot,sq,show}, legsOut, exhaust, muff (rattle t)}
export function car(ctx, o = {}) {
  const { x = 0, y = 0, s = 1, flip = false, rot = 0, sq = 0, bounce = 0, wheel = 0, face = 'neutral', look = [1, 0], light = 1, t = 0, tilt = 0, shake = 0 } = o;
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s * (flip ? -1 : 1), s);
  // ground shadow
  oval(ctx, 0, 0, 200, 14); ctx.fillStyle = 'rgba(40,20,40,0.25)'; ctx.fill();
  // wheels
  carWheel(ctx, -115, -36, wheel); carWheel(ctx, 115, -36, wheel);
  // body (squash about wheel line)
  ctx.save(); ctx.translate(0, -40 + bounce); ctx.rotate(tilt); ctx.translate(jit(t, 3, shake), jit(t, 5, shake) * 0.6); ctx.scale(1 + sq, 1 / (1 + sq)); ctx.translate(0, 40);
  // muffler (rattling)
  const mj = Math.sin(t * 50) * 3;
  ctx.save(); ctx.translate(0, mj); rrect(ctx, -214, -64, 46, 14, 6); paint(ctx, C.metalD, 5); oval(ctx, -214, -57, 5, 8); paint(ctx, INK, 0); ctx.restore();
  // body
  cel(ctx, () => carBody(ctx), C.green, C.greenD, 0, -14);
  // highlight strip on roof
  ctx.save(); carBody(ctx); ctx.clip();
  ctx.beginPath(); ctx.moveTo(-110, -236); ctx.bezierCurveTo(-60, -244, 10, -244, 44, -236); paint(ctx, null, 7, C.greenL);
  // rust patch + side trim
  ctx.beginPath(); ctx.moveTo(-176, -106); ctx.lineTo(186, -106); paint(ctx, null, 4, C.greenD);
  smooth(ctx, [[-150, -80], [-132, -88], [-124, -74], [-140, -68]]); paint(ctx, '#c46a2c', 0);
  ctx.restore();
  // windows: interior, crew, glass
  for (const w of [rearWin, frontWin]) { w(ctx); paint(ctx, C.interior, 0); }
  if (o.crew) clipTo(ctx, () => { rearWin(ctx); frontWin(ctx, false); }, () => {
    // seats
    rrect(ctx, -110, -214, 40, 70, 12); paint(ctx, '#8a3a2a', 0); rrect(ctx, 6, -214, 34, 70, 12); paint(ctx, '#8a3a2a', 0);
    o.crew(ctx);
  });
  for (const w of [rearWin, frontWin]) {
    ctx.save(); w(ctx); ctx.clip();
    ctx.fillStyle = 'rgba(191,232,230,0.16)'; ctx.fillRect(-200, -260, 400, 120);
    ctx.beginPath(); ctx.moveTo(-120, -150); ctx.lineTo(-80, -240); ctx.lineTo(-62, -240); ctx.lineTo(-102, -150); ctx.closePath();
    ctx.moveTo(78, -150); ctx.lineTo(112, -240); ctx.lineTo(120, -240); ctx.lineTo(86, -150); ctx.closePath();
    ctx.fillStyle = 'rgba(255,255,255,0.35)'; ctx.fill();
    ctx.restore(); w(ctx); paint(ctx, null, 6);
  }
  // door + dent
  ctx.beginPath(); ctx.moveTo(-14, -164); ctx.lineTo(-14, -62); ctx.moveTo(112, -158); ctx.quadraticCurveTo(118, -110, 104, -64); paint(ctx, null, 5);
  rrect(ctx, 0, -146, 26, 8, 4); paint(ctx, C.metal, 4);
  ctx.save(); ctx.translate(48, -96);
  smooth(ctx, [[-22, -6], [-6, -18], [16, -12], [22, 8], [2, 16], [-18, 10]]); paint(ctx, C.greenD, 0);
  ctx.beginPath(); ctx.moveTo(-14, -6); ctx.lineTo(-2, 2); ctx.lineTo(8, -8); ctx.moveTo(-6, 10); ctx.lineTo(4, 4); ctx.lineTo(14, 8); paint(ctx, null, 3.5);
  ctx.restore();
  // tail light + bumpers
  rrect(ctx, -192, -136, 16, 28, 5); paint(ctx, C.red, 5);
  rrect(ctx, -198, -76, 40, 18, 8); paint(ctx, C.metal, 5);
  rrect(ctx, 156, -78, 44, 18, 8); paint(ctx, C.metal, 5);
  // ---- the face: headlight eye + bumper mouth
  carSideFace(ctx, face, look, light, t);
  // things sticking out (legs out the window etc)
  if (o.outside) o.outside(ctx);
  // loot bag on roof
  if (o.bag?.show !== false && o.bag) {
    const b = o.bag;
    bag(ctx, b.x ?? -40, b.y ?? -238, b.s ?? 0.62, b.rot ?? 0, b.sq ?? 0, b.open ?? 0);
    const strap = b.strap ?? 1;
    if (strap > 0) {
      ctx.save(); ctx.setLineDash([240 * strap, 1000]);
      ctx.beginPath(); ctx.moveTo((b.x ?? -40) - 30, -262); ctx.quadraticCurveTo(-110, -236, -132, -196); paint(ctx, null, 5, '#8a5a2a');
      ctx.beginPath(); ctx.moveTo((b.x ?? -40) + 30, -262); ctx.quadraticCurveTo(10, -236, 22, -196); paint(ctx, null, 5, '#8a5a2a');
      ctx.restore();
    }
  }
  ctx.restore();
  ctx.restore();
}
function carSideFace(ctx, face, look, light, t) {
  const on = light > 0.5;
  // light beam
  if (on) { ctx.save(); ctx.globalAlpha = 0.18 * light; ctx.beginPath(); ctx.moveTo(186, -134); ctx.lineTo(420, -190); ctx.lineTo(420, -40); ctx.lineTo(186, -106); ctx.closePath(); ctx.fillStyle = '#fff3a8'; ctx.fill(); ctx.restore(); }
  const ex = 168, ey = -122;
  const big = face === 'scared' || face === 'shock' ? 1.15 : 1;
  oval(ctx, ex, ey, 19 * big, 22 * big); paint(ctx, on ? '#fffbe0' : '#d9cf9e', 6);
  if (face === 'dizzy') {
    ctx.beginPath(); for (let i = 0; i < 24; i++) { const a = i * 0.6 + t * 8, r = i * 0.7; ctx.lineTo(ex + Math.cos(a) * r, ey + Math.sin(a) * r); } paint(ctx, null, 3);
  } else if (face === 'strain' || face === 'squint') {
    ctx.beginPath(); ctx.moveTo(ex - 12, ey - 6); ctx.lineTo(ex + 6, ey); ctx.lineTo(ex - 12, ey + 8); paint(ctx, null, 5);
  } else {
    circle(ctx, ex + 5 + look[0] * 5, ey + 2 + look[1] * 5, face === 'shock' ? 4 : 7.5); paint(ctx, INK, 0);
    circle(ctx, ex + 2 + look[0] * 5, ey - 2 + look[1] * 5, 2.4); paint(ctx, '#fff', 0);
  }
  // lid / brow (hood crease)
  const lid = { grimace: 0.45, worried: 0.3, sad: 0.4, neutral: 0.15, happy: 0.1, strain: 0, squint: 0, scared: 0, shock: 0, dizzy: 0.2, sleepy: 0.6 }[face] ?? 0.15;
  if (lid > 0) {
    ctx.save(); oval(ctx, ex, ey, 19 * big, 22 * big); ctx.clip();
    ctx.fillStyle = C.green; const tiltL = face === 'worried' || face === 'sad' ? 0.35 : face === 'grimace' ? -0.25 : 0;
    ctx.translate(ex, ey - 22 + lid * 44); ctx.rotate(tiltL); ctx.fillRect(-30, -60, 60, 60);
    ctx.beginPath(); ctx.moveTo(-30, 0); ctx.lineTo(30, 0); paint(ctx, null, 5);
    ctx.restore(); oval(ctx, ex, ey, 19 * big, 22 * big); paint(ctx, null, 6);
  }
  const bA = { grimace: -0.4, worried: 0.45, sad: 0.5, scared: 0.6, shock: 0.3, strain: -0.5, happy: 0.15, neutral: 0, dizzy: 0.2, sleepy: 0 }[face] ?? 0;
  ctx.save(); ctx.translate(ex - 2, ey - 34 - (face === 'scared' || face === 'shock' ? 6 : 0)); ctx.rotate(-bA);
  ctx.beginPath(); ctx.moveTo(-16, 0); ctx.lineTo(16, 0); paint(ctx, null, 8, C.greenX);
  ctx.restore();
  // mouth on the bumper/front quarter
  ctx.save(); ctx.translate(160, -86);
  if (face === 'grimace' || face === 'strain') {
    smooth(ctx, [[-34, -6], [0, -12], [30, -12], [32, 10], [0, 10], [-34, 6]]); paint(ctx, '#fff', 5);
    ctx.beginPath(); ctx.moveTo(-34, 0); ctx.lineTo(32, -1); for (let i = -22; i <= 22; i += 11) { ctx.moveTo(i, -11); ctx.lineTo(i, 10); } paint(ctx, null, 3);
  } else if (face === 'scared' || face === 'shock') {
    oval(ctx, 4, 0, 22, 12); paint(ctx, '#5a1a22', 5); rrect(ctx, -10, -11, 26, 6, 2); paint(ctx, '#fff', 0);
  } else if (face === 'happy') {
    ctx.beginPath(); ctx.moveTo(-30, -8); ctx.quadraticCurveTo(0, 18, 30, -10); ctx.closePath(); paint(ctx, '#5a1a22', 5);
  } else if (face === 'worried' || face === 'sad' || face === 'dizzy') {
    ctx.beginPath(); ctx.moveTo(-28, 4); ctx.quadraticCurveTo(-14, -6, 0, 2); ctx.quadraticCurveTo(14, 10, 28, 0); paint(ctx, null, 5);
  } else if (face === 'sleepy') {
    ctx.beginPath(); ctx.moveTo(-20, 2); ctx.lineTo(24, 0); paint(ctx, null, 5);
  } else { ctx.beginPath(); ctx.moveTo(-26, -2); ctx.quadraticCurveTo(0, 8, 26, -4); paint(ctx, null, 5); }
  ctx.restore();
}

// ---------------------------------------------------------------- THE CAR (front view) for head-on shots
export function carFront(ctx, o = {}) {
  const { x = 0, y = 0, s = 1, rot = 0, sq = 0, bounce = 0, face = 'grimace', light = 1, t = 0, look = [0, 0], crew = true, bennyExpr = 'panic', margeExpr = 'smirk', shake = 0 } = o;
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  oval(ctx, 0, 0, 190, 16); ctx.fillStyle = 'rgba(40,20,40,0.25)'; ctx.fill();
  for (const k of [-1, 1]) { rrect(ctx, k * 120 - 26, -54, 52, 56, 12); paint(ctx, C.tire); }
  ctx.save(); ctx.translate(jit(t, 2, shake), -40 + bounce + jit(t, 4, shake) * 0.5); ctx.scale(1 + sq, 1 / (1 + sq)); ctx.translate(0, 40);
  // cabin
  const cab = () => smooth(ctx, [[-128, -150], [-112, -232], [-80, -256], [80, -256], [112, -232], [128, -150]]);
  cel(ctx, cab, C.green, C.greenD, 10, 0);
  const ws = () => smooth(ctx, [[-108, -158], [-94, -226], [-70, -242], [70, -242], [94, -226], [108, -158]]);
  ws(); paint(ctx, C.interior, 0);
  if (crew) clipTo(ctx, ws, () => {
    // Benny (driver) and Marge folded up beside him
    benny(ctx, { x: -44, y: -78, s: 0.62, pose: 'drive', expr: bennyExpr, t, sweat: 1, wheel: [40, -110] });
    ctx.save(); ctx.translate(48, -150); ctx.rotate(0.35);
    marge(ctx, { x: 0, y: 160, s: 0.5, expr: margeExpr, t });
    ctx.restore();
    circle(ctx, -36, -150, 26); paint(ctx, null, 7, '#3a3a40'); // steering wheel
  });
  ctx.save(); ws(); ctx.clip(); ctx.fillStyle = 'rgba(191,232,230,0.22)'; ctx.fillRect(-120, -250, 240, 100);
  poly(ctx, [[-70, -150], [-30, -250], [-10, -250], [-50, -150]]); ctx.fillStyle = 'rgba(255,255,255,0.3)'; ctx.fill(); ctx.restore();
  ws(); paint(ctx, null, 6);
  // mirrors (ears)
  for (const k of [-1, 1]) { oval(ctx, k * 150, -168, 18, 14); paint(ctx, C.green); }
  // lower body
  const body = () => rrect(ctx, -168, -158, 336, 112, 40);
  cel(ctx, body, C.green, C.greenD, 0, -12);
  // headlight eyes (left one flickers)
  for (const k of [-1, 1]) {
    const on = k < 0 ? light > 0.5 : true;
    const ex = k * 100, ey = -112;
    if (on) { ctx.save(); ctx.globalAlpha = 0.25; circle(ctx, ex, ey, 46); ctx.fillStyle = '#fff3a8'; ctx.fill(); ctx.restore(); }
    circle(ctx, ex, ey, 30); paint(ctx, on ? '#fffbe0' : '#d9cf9e', 6);
    if (face === 'squint') { ctx.beginPath(); ctx.moveTo(ex - 16 * k, ey - 10); ctx.lineTo(ex + 6 * k, ey); ctx.lineTo(ex - 16 * k, ey + 10); paint(ctx, null, 5); }
    else { circle(ctx, ex + look[0] * 8 - k * 4, ey + 2 + look[1] * 8, 11); paint(ctx, INK, 0); circle(ctx, ex + look[0] * 8 - k * 4 - 3, ey - 3 + look[1] * 8, 3.5); paint(ctx, '#fff', 0); }
    const lidAng = face === 'grimace' ? 0.3 * k : face === 'worried' || face === 'sad' ? -0.35 * k : 0;
    if (face !== 'scared') {
      ctx.save(); circle(ctx, ex, ey, 30); ctx.clip(); ctx.translate(ex, ey - 18); ctx.rotate(lidAng); ctx.fillStyle = C.green; ctx.fillRect(-40, -60, 80, 60); ctx.beginPath(); ctx.moveTo(-40, 0); ctx.lineTo(40, 0); paint(ctx, null, 5); ctx.restore();
      circle(ctx, ex, ey, 30); paint(ctx, null, 6);
    }
  }
  // grille mouth
  ctx.save(); ctx.translate(0, -78);
  if (face === 'grimace' || face === 'squint') {
    smooth(ctx, [[-56, -12], [0, -18], [56, -12], [52, 14], [0, 18], [-52, 14]]); paint(ctx, '#fff', 6);
    ctx.beginPath(); ctx.moveTo(-56, 0); ctx.lineTo(56, 0); for (let i = -40; i <= 40; i += 16) { ctx.moveTo(i, -16); ctx.lineTo(i, 16); } paint(ctx, null, 3.5);
  } else if (face === 'happy') { ctx.beginPath(); ctx.moveTo(-50, -10); ctx.quadraticCurveTo(0, 30, 50, -10); ctx.closePath(); paint(ctx, '#5a1a22', 6); }
  else if (face === 'scared') { oval(ctx, 0, 2, 34, 18); paint(ctx, '#5a1a22', 6); }
  else { ctx.beginPath(); ctx.moveTo(-44, 0); ctx.quadraticCurveTo(-20, -10, 0, 0); ctx.quadraticCurveTo(20, 10, 44, 0); paint(ctx, null, 6); }
  ctx.restore();
  // bumper + plate
  rrect(ctx, -176, -60, 352, 22, 10); paint(ctx, C.metal, 6);
  rrect(ctx, -40, -58, 80, 24, 4); paint(ctx, '#fff6dc', 4);
  text(ctx, 'GTAWAY', 0, -45, { size: 18, font: 'Arial Black', fill: C.navy, lw: 0 });
  // dent
  ctx.beginPath(); ctx.moveTo(126, -140); ctx.lineTo(138, -130); ctx.lineTo(128, -120); ctx.lineTo(142, -110); paint(ctx, null, 4);
  // bag on roof
  if (o.bag !== false) bag(ctx, 0, -250, 0.7, Math.sin(t * 9) * 0.05, 0);
  ctx.restore();
  ctx.restore();
}
