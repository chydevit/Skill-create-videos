// The cast (CAST): the Office series — Smey, Nimith, David, Sopheak, Leanghak, Pisey, Kimlong, Channy, Sreyneang,
// plus a boss, a coworker and a professor. Reuse them for a new episode, or spread an entry to make someone new.
// One person rig in the Getaway Car cartoon manner: big heads, round/lanky silhouettes, rubber-hose limbs,
// big eyes with small pupils, bushy brows, cartoon noses, a constant breathing bounce.
// Origin = feet centre. facing: 1 = 3/4 turned to screen-right, 0 = front, -1 = 3/4 left. back: true = seen from behind.
import { INK, LW, TAU, paint, circle, oval, rrect, poly, smooth, hose, cel, clamp, lerp, ik, hash } from './core.mjs';

const LWP = LW, HEAD = 1.32; // head scale: big heads read better and look friendlier
// two-segment limb with a real elbow/knee (rounded joins)
function limb(ctx, pts, w, col) {
  ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  const path = () => { ctx.beginPath(); ctx.moveTo(...pts[0]); for (let i = 1; i < pts.length; i++) ctx.lineTo(...pts[i]); };
  path(); ctx.strokeStyle = INK; ctx.lineWidth = w + LWP * 2; ctx.stroke();
  path(); ctx.strokeStyle = col; ctx.lineWidth = w; ctx.stroke();
}
export const P = {
  skin: '#e2ad85', skinD: '#c98f68', blush: 'rgba(232,80,80,0.32)', white: '#fffdf8', eye: '#3a2a22', mouth: '#7a3640', tongue: '#e0767a',
  tea: '#f7f2ea', teaIn: '#b5793c', coffee: '#7b4a2c', ice: '#e9f6f7', cupLid: '#ffffff', marker: '#4f86c6', notebook: '#fff6dc',
};
export const CAST = {
  smey: { // early 30s, tired but kind: medium-round, bulb nose
    H: 400, legs: 0.32, torso: 0.30, headS: 1.6, hx: 1.0, hy: 1.02, belly: 0.35, arm: 64, nose: 'bulb',
    sw: 52, ww: 54, skin: '#cf9468', skinD: '#ad744c', hair: '#221d24', gray: '#221d24',
    shirt: '#5aa8ec', shirtD: '#3f8bd0', collar: '#8cc6f7', pants: '#4a4f6b', pantsD: '#373b55', shoe: '#3a2a22', style: 'shirt', hairStyle: 'short', eyeSize: 1.1,
  },
  nimith: { // late 20s, confident: tall and lanky, glasses, white tee, pointy nose
    H: 470, legs: 0.47, torso: 0.29, headS: 1.42, hx: 0.9, hy: 1.12, belly: 0, arm: 80, nose: 'point', neck: 26,
    sw: 38, ww: 30, skin: '#e0a378', skinD: '#c4865c', hair: '#1f1a22', glasses: true,
    shirt: '#fbfbfb', shirtD: '#d6dbe4', collar: '#ffffff', pants: '#2f3e66', pantsD: '#22305a', shoe: '#ff5c5c', style: 'tee', hairStyle: 'neat', eyeSize: 1.1,
  },
  leanghak: { // mid 30s, new admin officer: bob with a hair clip, cream blouse, navy skirt, red lanyard ID card
    H: 390, legs: 0.40, torso: 0.29, headS: 1.55, hx: 0.95, hy: 1.05, belly: 0.05, arm: 62, nose: 'button', neck: 6,
    sw: 40, ww: 38, skin: '#d9a07a', skinD: '#bd8360', hair: '#1e1a22', gray: '#1e1a22',
    shirt: '#f8ecd4', shirtD: '#e4d2ae', collar: '#ffffff', pants: '#d9a07a', pantsD: '#bd8360', skirt: '#2f3e7a', shoe: '#8a2f3f',
    style: 'blouse', hairStyle: 'bob', clip: '#ff5c8a', lanyard: '#e8433a', eyeSize: 1.2, lashes: true, thinBrows: true,
  },
  pisey: { // mid 40s, new staff: short wavy hair, light green blouse, black trousers, glasses on a chain, red lanyard
    H: 385, legs: 0.38, torso: 0.30, headS: 1.5, hx: 1.0, hy: 1.02, belly: 0.3, arm: 62, nose: 'button', neck: 4,
    sw: 44, ww: 44, skin: '#c98f68', skinD: '#a8714c', hair: '#221d24', gray: '#221d24',
    shirt: '#a8e0b8', shirtD: '#86c99a', collar: '#ffffff', pants: '#2a2633', pantsD: '#1d1828', shoe: '#5a3a2a',
    style: 'blouse', hairStyle: 'wavy', lanyard: '#e8433a', chainGlasses: true, eyeSize: 1.1, lashes: true, thinBrows: true,
  },
  boss: { // her manager, 50s: round, grey temples, red tie
    H: 430, legs: 0.36, torso: 0.31, headS: 1.5, hx: 1.05, hy: 1.0, belly: 0.6, arm: 64, nose: 'bulb',
    sw: 52, ww: 54, skin: '#c98f68', skinD: '#a8714c', hair: '#3a3540', gray: '#b8b8c4',
    shirt: '#ffffff', shirtD: '#dfe3ea', collar: '#e9edf3', pants: '#3a3f5c', pantsD: '#2b2f48', shoe: '#2a1d1a', style: 'shirt', hairStyle: 'short', necktie: '#e8433a', eyeSize: 1.0,
  },
  coworker: { // friendly colleague, late 20s: ponytail, pink tee
    H: 370, legs: 0.38, torso: 0.29, headS: 1.55, hx: 0.95, hy: 1.03, belly: 0, arm: 60, nose: 'button',
    sw: 38, ww: 36, skin: '#e0a378', skinD: '#c4865c', hair: '#2a1d24', gray: '#2a1d24',
    shirt: '#ff8fab', shirtD: '#e86f8e', collar: '#ffc2d0', pants: '#3a4f8f', pantsD: '#2b3c70', shoe: '#3a2a22', style: 'tee', hairStyle: 'ponytail', tie: '#ffd23f', eyeSize: 1.15, lashes: true, thinBrows: true,
  },
  sopheak: { // 19, the new guy: slim, side-part hair, light yellow polo, khaki trousers, big black over-ear headphones
    H: 405, legs: 0.43, torso: 0.28, headS: 1.48, hx: 0.92, hy: 1.08, belly: 0, arm: 66, nose: 'button', neck: 8,
    sw: 38, ww: 32, skin: '#dba274', skinD: '#bf8556', hair: '#1b181f', gray: '#1b181f',
    shirt: '#ffe27a', shirtD: '#f2c94c', collar: '#fff4c4', pants: '#cdb27c', pantsD: '#ae935e', shoe: '#f4f1ea', style: 'polo', hairStyle: 'part', eyeSize: 1.1, phones: 'neck',
  },
  professor: { // late 50s university lecturer: grey hair, glasses, white shirt, dark tie, a little round
    H: 425, legs: 0.37, torso: 0.31, headS: 1.5, hx: 1.0, hy: 1.04, belly: 0.45, arm: 64, nose: 'bulb', neck: 4,
    sw: 50, ww: 50, skin: '#c98f68', skinD: '#a8714c', hair: '#b9b6c2', gray: '#9d99a8', glasses: true,
    shirt: '#ffffff', shirtD: '#dfe3ea', collar: '#e9edf3', pants: '#3a3f5c', pantsD: '#2b2f48', shoe: '#2a1d1a', style: 'shirt', hairStyle: 'receding', necktie: '#2d3a6b', eyeSize: 1.0, browCol: '#c9c6d2',
  },
  david: { // about 20, eager: short and round, giant head, grey hoodie
    H: 330, legs: 0.26, torso: 0.27, headS: 1.8, hx: 1.05, hy: 1.0, belly: 0.3, arm: 52, nose: 'button',
    sw: 46, ww: 50, skin: '#d4955f', skinD: '#b5773f', hair: '#1f1c22',
    shirt: '#9aa3b5', shirtD: '#7c8599', collar: '#c2c8d4', pants: '#3f6fbf', pantsD: '#2f569a', shoe: '#ffd23f', style: 'hoodie', hairStyle: 'messy', eyeSize: 1.35,
  },
  kimlong: { // 19, the new videographer and self-declared King of Flirting: chubby, round face, gelled spikes, open red flannel over a black tee, jeans, camera round his neck
    H: 385, legs: 0.34, torso: 0.30, headS: 1.62, hx: 1.12, hy: 0.98, belly: 0.6, arm: 58, nose: 'button', neck: 2,
    sw: 50, ww: 54, skin: '#cf9468', skinD: '#ad744c', hair: '#17141b',
    shirt: '#e8433a', shirtD: '#b8302a', collar: '#ff8a7a', tee: '#25222b', plaid: 'rgba(60,10,20,0.32)', pants: '#3b5a8f', pantsD: '#2d4673', shoe: '#f4f1ea',
    style: 'flannel', hairStyle: 'spiky', camera: true, eyeSize: 1.15,
  },
  channy: { // 22, works for Leanghak's company: tall, calm, long straight hair, white blouse, grey pencil skirt, red lanyard
    H: 425, legs: 0.45, torso: 0.28, headS: 1.46, hx: 0.92, hy: 1.08, belly: 0, arm: 66, nose: 'button', neck: 10,
    sw: 36, ww: 30, skin: '#e3ab84', skinD: '#c78e66', hair: '#141118', gray: '#141118',
    shirt: '#ffffff', shirtD: '#dde2ec', collar: '#ffffff', pants: '#e3ab84', pantsD: '#c78e66', skirt: '#8a8d99', pencil: true, shoe: '#2a2633',
    style: 'blouse', hairStyle: 'long', lanyard: '#e8433a', eyeSize: 1.1, lashes: true, thinBrows: true,
  },
  sreyneang: { // 21, the witty waitress next door: high bun, navy apron over a white tee
    H: 378, legs: 0.40, torso: 0.29, headS: 1.52, hx: 0.96, hy: 1.04, belly: 0.05, arm: 60, nose: 'button', neck: 6,
    sw: 38, ww: 36, skin: '#d39a6e', skinD: '#b67d52', hair: '#1d1820', gray: '#1d1820',
    shirt: '#ffffff', shirtD: '#dfe3ea', collar: '#ffffff', pants: '#2a2633', pantsD: '#1d1828', shoe: '#3a2a22',
    style: 'tee', hairStyle: 'bun', apron: '#2d3f73', eyeSize: 1.15, lashes: true, thinBrows: true,
  },
};
export function camera(ctx, x, y, s = 1, rot = 0, rec = false, t = 0) { // a mirrorless camera, lens to the viewer
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  rrect(ctx, -34, -22, 68, 44, 8); paint(ctx, '#2a2730', LWP * 0.8);
  rrect(ctx, -30, -30, 18, 10, 3); paint(ctx, '#2a2730', 3);
  circle(ctx, 4, 0, 18); paint(ctx, '#3d3a46', 4); circle(ctx, 4, 0, 11); paint(ctx, '#5b7fb0', 3); circle(ctx, 0, -4, 4); ctx.fillStyle = 'rgba(255,255,255,0.7)'; ctx.fill();
  circle(ctx, -24, -12, 3.5); ctx.fillStyle = rec && Math.sin(t * 8) > -0.3 ? '#ff3b3b' : '#6b6875'; ctx.fill();
  ctx.restore();
}

// ---------------------------------------------------------------- props
export function teaCup(ctx, x, y, s = 1, t = 0, steam = true) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  if (steam) { ctx.strokeStyle = 'rgba(255,255,255,0.75)'; ctx.lineWidth = 4; ctx.lineCap = 'round'; for (let k = 0; k < 2; k++) { ctx.beginPath(); const o = Math.sin(t * 3 + k) * 4; ctx.moveTo(-6 + k * 12, -30); ctx.bezierCurveTo(-12 + k * 12 + o, -42, 0 + k * 12 - o, -50, -6 + k * 12, -62); ctx.stroke(); } }
  ctx.beginPath(); ctx.moveTo(-16, -26); ctx.lineTo(16, -26); ctx.lineTo(12, 2); ctx.quadraticCurveTo(0, 8, -12, 2); ctx.closePath(); paint(ctx, P.tea, LWP * 0.8);
  ctx.beginPath(); ctx.ellipse(0, -26, 16, 4, 0, 0, TAU); paint(ctx, P.teaIn, 3);
  ctx.beginPath(); ctx.arc(18, -14, 7, -1.2, 1.2); paint(ctx, null, 4);
  ctx.restore();
}
export function icedCoffee(ctx, x, y, s = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.beginPath(); ctx.moveTo(4, -44); ctx.lineTo(12, -66); paint(ctx, null, 5, '#3fa76b');
  ctx.beginPath(); ctx.moveTo(-15, -40); ctx.lineTo(15, -40); ctx.lineTo(11, 4); ctx.lineTo(-11, 4); ctx.closePath(); paint(ctx, 'rgba(235,248,250,0.9)', LWP * 0.8);
  ctx.save(); ctx.beginPath(); ctx.moveTo(-15, -40); ctx.lineTo(15, -40); ctx.lineTo(11, 4); ctx.lineTo(-11, 4); ctx.closePath(); ctx.clip();
  ctx.fillStyle = P.coffee; ctx.fillRect(-20, -26, 40, 34); ctx.fillStyle = '#f2e6d6'; ctx.fillRect(-20, -30, 40, 6);
  ctx.fillStyle = 'rgba(255,255,255,0.6)'; ctx.fillRect(-9, -22, 8, 8); ctx.fillRect(3, -16, 7, 7); ctx.restore();
  rrect(ctx, -17, -46, 34, 7, 3); paint(ctx, P.cupLid, 3.5);
  ctx.restore();
}
export function marker(ctx, x, y, s = 1, rot = -0.6) { ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s); rrect(ctx, -5, -30, 10, 34, 3); paint(ctx, '#fdfdfd', 3.5); rrect(ctx, -5, -32, 10, 10, 3); paint(ctx, P.marker, 3); ctx.restore(); }
export function notebook(ctx, x, y, s = 1, open = 1, drawFn = null) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const w = 60 * open;
  rrect(ctx, -w - 4, -44, w * 2 + 8, 70, 6); paint(ctx, '#e07a5f', 4);
  rrect(ctx, -w, -40, w, 62, 3); paint(ctx, P.notebook, 3); rrect(ctx, 0, -40, w, 62, 3); paint(ctx, P.notebook, 3);
  if (drawFn && open > 0.9) drawFn(ctx);
  ctx.restore();
}
export function phone(ctx, x, y, s = 1) { ctx.save(); ctx.translate(x, y); ctx.scale(s, s); rrect(ctx, -14, -26, 28, 52, 6); paint(ctx, '#2c2a33', 3.5); rrect(ctx, -11, -22, 22, 42, 3); paint(ctx, '#9fd6e8', 0); ctx.restore(); }

// ---------------------------------------------------------------- hands
export function handShape(ctx, x, y, side, kind = 'open', rot = 0, skin = P.skin) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(side * 1.18, 1.18);
  if (kind === 'thumb') {
    rrect(ctx, -11, -8, 22, 20, 7); paint(ctx, skin, LWP * 0.8);
    rrect(ctx, -6, -26, 9, 22, 4.5); paint(ctx, skin, LWP * 0.8);
  } else if (kind === 'fist') { circle(ctx, 0, 0, 11); paint(ctx, skin, LWP * 0.8); }
  else if (kind === 'point') { rrect(ctx, 2, -5, 26, 10, 5); paint(ctx, skin, LWP * 0.7); circle(ctx, 0, 0, 11); paint(ctx, skin, LWP * 0.8); }
  else {
    oval(ctx, 0, 0, 11, 12); paint(ctx, skin, LWP * 0.8);
    ctx.beginPath(); ctx.ellipse(-9, -2, 4, 7, -0.6, 0, TAU); paint(ctx, skin, LWP * 0.7);
  }
  ctx.restore();
}

// ---------------------------------------------------------------- pose rig
// returns skeleton targets in local space (y up = negative)
function rig(c, o) {
  const H = c.H, f = o.facing ?? 0.4, ph = (o.ph || 0) * TAU;
  const HS = c.headS || HEAD, legs = c.legs ?? 0.44, torso = c.torso ?? 0.30;
  const R = { hipY: -legs * H, lean: 0, bodyY: 0, sit: false, HS }; R.shY = R.hipY - torso * H; R.headY = R.shY - 40 * HS * (c.hy || 1) - (c.neck || 0);
  const chest = R.shY + torso * H * 0.55;
  const sh = [[-c.sw, R.shY + 6], [c.sw, R.shY + 6]];
  let hands = [[-c.sw - 6, R.hipY + 4], [c.sw + 6, R.hipY + 4]], feet = [[-18, 0], [18, 0]], handKind = ['open', 'open'], handRot = [0, 0];
  const p = o.pose || 'stand';
  const arm = (side, x, y) => { hands[side] = [x, y]; };
  if (p === 'walk') {
    feet = [[-14 + Math.cos(ph) * 26, -Math.max(0, Math.sin(ph)) * 16], [14 - Math.cos(ph) * 26, -Math.max(0, -Math.sin(ph)) * 16]];
    hands = [[-c.sw - 4 - Math.cos(ph) * 14, R.hipY + 8], [c.sw + 4 + Math.cos(ph) * 14, R.hipY + 8]];
    R.bodyY = -Math.abs(Math.sin(ph)) * 5;
  }
  if (o.sit || p === 'type' || p === 'sitBack' || p === 'sitTalk') {
    R.sit = true; R.bodyY = legs * H * 0.42;
    feet = [[-20 + f * 18, 0], [20 + f * 18, 0]];
  }
  if (p === 'type') { const b = Math.sin((o.t || 0) * 30); arm(0, -26 + f * 40, R.hipY + 18 - Math.max(0, b) * 8); arm(1, 26 + f * 40, R.hipY + 18 - Math.max(0, -b) * 8); handKind = ['fist', 'fist']; }
  if (p === 'rub') { arm(1, 6 * HS + f * 10, R.headY - 22 * HS); handKind[1] = 'open'; handRot[1] = Math.sin((o.t || 0) * 10) * 0.25; }
  if (p === 'scratch') { arm(1, 30 * HS + f * 12, R.headY - 30 * HS + Math.sin((o.t || 0) * 22) * 5); handKind[1] = 'fist'; }
  if (p === 'point') { arm(1, c.sw + 84, R.shY - 30); handKind[1] = 'point'; }
  if (p === 'wag') { arm(1, c.sw + 40, R.shY - 70); handKind[1] = 'point'; handRot[1] = -Math.PI / 2 + Math.sin((o.t || 0) * 16) * 0.45; }
  if (p === 'phone') { arm(0, 14 + f * 56, R.shY + 62); if (o.reach) arm(1, o.reach[0], o.reach[1]); else arm(1, 22 + f * 40, R.shY + 62); } // phone in the left hand, right hand free to tap
  if (p === 'call') { arm(1, 34 * HS + f * 12, R.headY + 8 * HS); handKind[1] = 'fist'; }
  if (p === 'sampeah') { arm(0, -5 + f * 26, R.shY + 2); arm(1, 5 + f * 26, R.shY + 2); handRot = [0.25, -0.25]; } // palms together (Khmer greeting)
  if (p === 'clip') { arm(1, 34 * HS + f * 8, R.headY - 34 * HS); handKind[1] = 'fist'; }
  if (p === 'chin') { arm(1, 8 + f * 24, R.headY + 44 * HS); handKind[1] = 'fist'; }
  if (p === 'hug') { arm(0, 22 + f * 20, chest - 6); arm(1, -10 + f * 20, chest + 10); }
  if (p === 'thumbs') { arm(1, c.sw + 24, R.shY - 20); handKind[1] = 'thumb'; }
  if (p === 'wave') { arm(1, c.sw + 34, R.shY - 70); handRot[1] = Math.sin((o.t || 0) * 12) * 0.35; }
  if (p === 'draw') { arm(1, c.sw + 70 + (o.drawX || 0), R.shY - 40 + (o.drawY || 0)); handKind[1] = 'fist'; }
  if (p === 'glasses') { arm(1, 30 * HS + 6 + f * 14, R.headY - 6 * HS); handKind[1] = 'fist'; }
  if (p === 'present') { arm(1, c.sw + 90, R.shY + 24); handRot[1] = -0.3; }
  if (p === 'presentL') { arm(0, -c.sw - 90, R.shY + 24); handRot[0] = 0.3; }
  if (p === 'sip') { arm(1, 16 + f * 20, R.headY + 34 * HS); }
  if (p === 'clap') { const k = Math.abs(Math.sin((o.t || 0) * 9)); arm(0, -10 - k * 22, chest - 20); arm(1, 10 + k * 22, chest - 20); }
  if (p === 'hold') { arm(1, c.sw - 6, chest); }
  if (p === 'jump') { arm(0, -c.sw - 40, R.shY - 90); arm(1, c.sw + 40, R.shY - 90); feet = [[-26, -10], [26, -14]]; R.bodyY = -(o.hop || 0); }
  if (p === 'raise') { arm(1, c.sw + 6, R.shY - 110); }
  if (p === 'panic') { arm(0, -(40 * HS + 12), R.headY - 14 * HS); arm(1, 40 * HS + 12, R.headY - 14 * HS); handKind = ['open', 'open']; }
  if (p === 'reach' && o.reach) { arm(1, o.reach[0], o.reach[1]); }
  if (p === 'reachL' && o.reach) { arm(0, o.reach[0], o.reach[1]); }
  if (p === 'notebook') { arm(0, -40, chest + 10); arm(1, 40, chest + 10); }
  if (p === 'highfive') { arm(1, c.sw + 60, R.shY - 90); }
  if (p === 'sitBack') { arm(0, -c.sw - 10, R.hipY + 10); arm(1, c.sw + 10, R.hipY + 10); }
  if (p === 'cover') { arm(0, -15 + f * 20, R.headY - 6 * HS); arm(1, 15 + f * 20, R.headY - 6 * HS); handRot = [0.2, -0.2]; } // hands over the face (embarrassed)
  if (p === 'ears') { arm(0, -42 * HS + f * 8, R.headY + 8 * HS); arm(1, 42 * HS + f * 8, R.headY + 8 * HS); } // hands on the headphone cups
  if (p === 'shout') { arm(0, -22 + f * 26, R.headY + 30 * HS); arm(1, 22 + f * 26, R.headY + 30 * HS); handRot = [0.9, -0.9]; } // hands cupped round the mouth
  if (p === 'heart') { arm(0, -13 + f * 24, R.shY + 22); arm(1, 13 + f * 24, R.shY + 22); handRot = [0.7, -0.7]; } // hands make a heart in front of the chest
  if (p === 'wave2') { const w = Math.sin((o.t || 0) * 14); arm(0, -c.sw - 44 - w * 14, R.shY - 92); arm(1, c.sw + 44 + w * 14, R.shY - 92); handRot = [-w * 0.4, w * 0.4]; }
  if (p === 'bump') { arm(1, c.sw + 76, R.shY + 14); handKind[1] = 'fist'; }
  if (p === 'reach2') { if (o.reach) arm(1, o.reach[0], o.reach[1]); if (o.reachL) arm(0, o.reachL[0], o.reachL[1]); }
  if (p === 'slump') { R.sit = true; R.bodyY = legs * H * 0.42; arm(0, -34 + f * 30, R.shY + 30); arm(1, 34 + f * 30, R.shY + 30); handKind = ['fist', 'fist']; } // asleep on the desk (o.headDrop lowers the head onto the arms)
  if (p === 'stretch') { arm(0, -c.sw - 70, R.shY - 110); arm(1, c.sw + 70, R.shY - 110); handKind = ['fist', 'fist']; }
  if (p === 'cheer') { arm(0, -c.sw - 30, R.shY - 100); arm(1, c.sw + 30, R.shY - 100); }
  if (p === 'facepalm') { arm(1, 6 * HS + f * 12, R.headY - 2 * HS); handRot[1] = -0.5; } // palm flat over the eyes
  if (p === 'chest') { arm(1, -8 + f * 22, chest - 14); handRot[1] = 0.6; arm(0, -c.sw - 40, R.shY - 40); handRot[0] = -0.4; } // hand on the heart, the other arm flung out
  if (p === 'leanWall') { arm(0, -c.sw - 46, R.headY - 6 * HS); handRot[0] = 0.3; arm(1, c.sw - 4, R.hipY - 2); handKind[1] = 'fist'; feet = [[8, 0], [-10, -6]]; } // one hand on the wall, legs crossed
  if (p === 'belly') { arm(0, -18 + f * 20, R.hipY - 16); arm(1, 18 + f * 20, R.hipY - 16); handRot = [0.5, -0.5]; } // clutching the stomach, laughing
  if (p === 'film') { arm(0, -30 + f * 40, R.shY - 4); arm(1, 30 + f * 40, R.shY - 4); handKind = ['fist', 'fist']; } // camera held up in front, both hands
  if (p === 'fixHair') { const w = Math.sin((o.t || 0) * 18) * 6; arm(0, -36 * HS + f * 8, R.headY - 40 * HS + w); arm(1, 36 * HS + f * 8, R.headY - 40 * HS - w); handRot = [0.6, -0.6]; }
  // props in a hand keep the arm bent at the chest unless a pose says otherwise
  for (const side of [0, 1]) {
    const prop = o.hold?.[side];
    if (prop && ['stand', 'walk', 'sitTalk'].includes(p)) arm(side, (side ? 1 : -1) * (c.sw - 4), chest);
  }
  return { ...R, sh, hands, feet, handKind, handRot, f };
}

// ---------------------------------------------------------------- anchors (world positions for contact: hand on shoulder, high fives)
export function anchors(who, o = {}) {
  const c = typeof who === 'string' ? CAST[who] : who, s = o.s ?? 1, R = rig(c, o), m = o.mirror ? -1 : 1;
  const w = ([x, y]) => [(o.x || 0) + x * s * m, (o.y || 0) + (y + (y < R.hipY + 20 ? R.bodyY : 0)) * s];
  return { shL: w(R.sh[0]), shR: w(R.sh[1]), handL: w(R.hands[0]), handR: w(R.hands[1]), head: w([0, R.headY]), chest: w([0, R.shY + 40]) };
}
// world point -> a person's local space (for 'reach' targets)
export const toLocal = (who, o, [wx, wy]) => { const c = typeof who === 'string' ? CAST[who] : who, s = o.s ?? 1, R = rig(c, o); return [(wx - (o.x || 0)) / s * (o.mirror ? -1 : 1), (wy - (o.y || 0)) / s - R.bodyY]; };

// ---------------------------------------------------------------- the person
// o: { x, y, s, facing, back, pose, ph, t, expr, mouth (0..1 lip-sync), look:[x,y], hold:[leftProp, rightProp], tilt, nod, hop, sq, alpha }
export function person(ctx, who, o = {}) {
  const c = typeof who === 'string' ? CAST[who] : who, s = o.s ?? 1, t = o.t || 0; // a CAST key or a one-off look (extras)
  const R = rig(c, o);
  // cartoon life: a breathing bounce held on twos, and a little squash on every syllable
  const tw = Math.floor(t * 12) / 12, breath = Math.sin(tw * Math.PI * 2 * 0.75 + (c.H % 7)) * 0.018;
  const sq = (o.sq || 0) + breath + (o.mouth || 0) * 0.025;
  ctx.save(); ctx.translate(o.x || 0, o.y || 0); ctx.scale(s * (1 + sq) * (o.mirror ? -1 : 1), s / (1 + sq)); // mirror: flip the whole figure (use the opposite hand)
  if (o.rot) ctx.rotate(o.rot);
  const by = R.bodyY, HO = o.headOnly; // headOnly: redraw just the head (e.g. over a pillow drawn on top of the body)
  // legs
  const hips = [[-c.ww * 0.45, R.hipY + by + 8], [c.ww * 0.45, R.hipY + by + 8]];
  for (let i = 0; i < 2 && !HO; i++) {
    const hp = hips[i], ft = R.feet[i];
    if (R.sit && !o.back) { const kn = [hp[0] * 1.2 + R.f * 26, hp[1] + 34]; hose(ctx, [hp, kn], 26, c.pants, LWP); hose(ctx, [kn, [ft[0], ft[1] - 10]], 24, c.pantsD, LWP); }
    else if (R.sit && o.back) { hose(ctx, [hp, [hp[0] * 1.4, hp[1] + 30]], 26, c.pants, LWP); }
    else { const L = (-R.hipY - 8 - 8) / 2 * 1.04, kn = ik(hp[0], hp[1], ft[0], ft[1] - 8, L, L, i ? 1 : -1); hose(ctx, [hp, kn, [ft[0], ft[1] - 8]], 26, i ? c.pants : c.pantsD, LWP); }
    if (!(R.sit && o.back)) { ctx.beginPath(); ctx.ellipse(ft[0] + R.f * 8, ft[1] - 8, 21, 11, 0, 0, TAU); paint(ctx, c.shoe, LWP * 0.8); }
  }
  if (c.skirt && !HO) { const top = R.hipY + by + 2, len = R.sit ? 48 : -R.hipY * (c.pencil ? 0.58 : 0.52); poly(ctx, R.sit && !o.back ? [[-c.ww - 4, top], [c.ww + 4, top], [c.ww + 12 + R.f * 46, top + len], [-c.ww - 8 + R.f * 46, top + len]] : c.pencil ? [[-c.ww - 6, top], [c.ww + 6, top], [c.ww + 3, top + len], [-c.ww - 3, top + len]] : [[-c.ww - 2, top], [c.ww + 2, top], [c.ww + 16, top + len], [-c.ww - 16, top + len]]); paint(ctx, c.skirt, LWP); if (c.pencil && !R.sit) { ctx.beginPath(); ctx.moveTo(6, top + len - 26); ctx.lineTo(6, top + len); paint(ctx, null, 3); } }
  ctx.translate(0, by);
  // arms behind the body (back view)
  if (o.back && !HO) for (let i = 0; i < 2; i++) drawArm(ctx, c, R, i, o, t);
  // long straight hair hangs behind the shoulders, so it goes down before the torso (head space)
  if (c.hairStyle === 'long' && !o.back && !HO) { const sx = -R.f * 8; ctx.save(); ctx.translate((o.headDrop || 0) * 0.25, R.headY + (o.nod || 0) * 6 - (o.mouth || 0) * 1.25 + (o.headDrop || 0)); ctx.rotate((o.tilt || 0) + (o.nod || 0) * 0.05); ctx.scale(R.HS * (c.hx || 1), R.HS * (c.hy || 1)); smooth(ctx, [[sx - 46, -28], [sx - 30, -54], [sx, -60], [sx + 30, -54], [sx + 46, -28], [sx + 50, 30], [sx + 52, 92], [sx + 44, 124], [sx - 44, 124], [sx - 52, 92], [sx - 50, 30]]); paint(ctx, c.hair, LWP); ctx.restore(); }
  if (!HO) {
  // backpack body peeking out behind a turned torso
  const bag = o.backpack && (c.bag || '#2a2633');
  if (bag && !o.back && Math.abs(R.f) > 0.15) { const bx = -Math.sign(R.f) * (c.sw * 0.7 + 16); rrect(ctx, bx - 26, R.shY + 4, 52, 100, 16); paint(ctx, bag, LWP); }
  // torso
  const bel = (c.belly || 0) * 34, midY = lerp(R.shY, R.hipY, 0.62);
  const torso = () => smooth(ctx, [[-c.sw, R.shY + 4], [-c.sw * 0.55, R.shY - 6], [c.sw * 0.55, R.shY - 6], [c.sw, R.shY + 4], [c.ww + 4 + bel, midY], [c.ww, R.hipY + 14], [-c.ww, R.hipY + 14], [-c.ww - 4 - bel, midY]]);
  cel(ctx, torso, c.shirt, c.shirtD, -R.f * 8 - 4, -4, LWP);
  if (c.plaid) { ctx.save(); torso(); ctx.clip(); ctx.strokeStyle = c.plaid; for (let i = -4; i <= 4; i++) { ctx.lineWidth = i % 2 ? 4 : 9; ctx.beginPath(); ctx.moveTo(i * 22, R.shY - 20); ctx.lineTo(i * 22, R.hipY + 20); ctx.stroke(); } for (let yy = R.shY + 6; yy < R.hipY + 14; yy += 22) { ctx.lineWidth = ((yy - R.shY) / 22) % 2 ? 4 : 9; ctx.beginPath(); ctx.moveTo(-c.ww - 50, yy); ctx.lineTo(c.ww + 50, yy); ctx.stroke(); } ctx.restore(); torso(); paint(ctx, null, LWP); }
  if (!o.back) shirtDetails(ctx, c, R);
  if (c.apron && !o.back) { const y = R.shY + 22, bot = R.hipY + 70; for (const k of [-1, 1]) { ctx.beginPath(); ctx.moveTo(k * 22, y + 2); ctx.lineTo(k * 14, R.shY - 6); paint(ctx, null, 6, c.apron); } smooth(ctx, [[-24, y], [24, y], [26, R.hipY - 30], [c.ww + 8, R.hipY - 22], [c.ww + 10, bot], [0, bot + 4], [-c.ww - 10, bot], [-c.ww - 8, R.hipY - 22], [-26, R.hipY - 30]]); paint(ctx, c.apron, LWP); rrect(ctx, -24, R.hipY - 2, 48, 30, 6); paint(ctx, c.apron, 3.5, '#4a5c94'); ctx.beginPath(); ctx.moveTo(c.ww + 8, R.hipY - 22); ctx.quadraticCurveTo(c.ww + 26, R.hipY - 16, c.ww + 20, R.hipY + 8); paint(ctx, null, 5, c.apron); }
  if (c.camera && !o.back && o.camera !== false && !(o.hold || []).includes('camera')) { const y = R.shY; ctx.beginPath(); ctx.moveTo(-24, y - 4); ctx.lineTo(-12, y + 64); ctx.moveTo(24, y - 4); ctx.lineTo(12, y + 64); paint(ctx, null, 5, '#2a2730'); camera(ctx, R.f * 10, y + 80, 0.72, -0.05); }
  if (c.lanyard && !o.back && o.badge !== false) { const y = R.shY; for (const k of [-1, 1]) { ctx.beginPath(); ctx.moveTo(k * 18, y - 4); ctx.lineTo(k * 5, y + 58); ctx.lineWidth = 9; ctx.strokeStyle = INK; ctx.stroke(); ctx.lineWidth = 4.5; ctx.strokeStyle = c.lanyard; ctx.stroke(); } rrect(ctx, -16 + R.f * 8, y + 56, 32, 42, 5); paint(ctx, '#ffffff', LWP * 0.6); ctx.fillStyle = c.lanyard; ctx.fillRect(-14 + R.f * 8, y + 58, 28, 9); rrect(ctx, -9 + R.f * 8, y + 70, 12, 14, 3); paint(ctx, '#9fc3e8', 0); }
  if (c.chainGlasses && !o.back) { const y = R.shY; ctx.beginPath(); ctx.moveTo(-28, y - 6); ctx.quadraticCurveTo(-26, y + 22, -12, y + 30); ctx.moveTo(28, y - 6); ctx.quadraticCurveTo(26, y + 22, 12, y + 30); paint(ctx, null, 2.5, '#d9a441'); for (const k of [-1, 1]) { circle(ctx, k * 13, y + 34, 10); paint(ctx, 'rgba(255,255,255,0.45)', 3.5); } ctx.beginPath(); ctx.moveTo(-3, y + 34); ctx.lineTo(3, y + 34); paint(ctx, null, 3); }
  else if (c.style === 'hoodie') { smooth(ctx, [[-30, R.shY - 4], [0, R.shY - 18], [30, R.shY - 4], [24, R.shY + 30], [0, R.shY + 40], [-24, R.shY + 30]]); paint(ctx, c.shirtD, LWP * 0.8); }
  if (bag && o.back) { rrect(ctx, -36, R.shY + 8, 72, 108, 18); paint(ctx, bag, LWP); rrect(ctx, -24, R.shY + 62, 48, 36, 10); paint(ctx, '#3d3848', LWP * 0.7); }
  else if (bag) for (const k of [-1, 1]) { ctx.beginPath(); ctx.moveTo(k * c.sw * 0.62, R.shY - 4); ctx.quadraticCurveTo(k * c.sw * 0.9, R.shY + 40, k * c.sw * 0.8, R.shY + 86); ctx.lineCap = 'round'; ctx.lineWidth = 14; ctx.strokeStyle = INK; ctx.stroke(); ctx.lineWidth = 7; ctx.strokeStyle = bag; ctx.stroke(); }
  }
  // neck + head
  const ph = o.phones ?? c.phones;   // big headphones: 'on' (both ears), 'one' (one cup pushed up), 'neck', or 'off'
  const nod = o.nod || 0, talkBob = (o.mouth || 0) * 2.5;
  const drop = o.headDrop || 0;
  if (o.pose === 'slump' && !o.back && !HO) for (let i = 0; i < 2; i++) drawArm(ctx, c, R, i, o, t); // the folded arms are under the head
  if (drop < 12 && !HO) { rrect(ctx, -11, R.headY + 20, 22, R.shY - R.headY - 14, 8); paint(ctx, c.skinD, LWP * 0.6); }
  ctx.save(); ctx.translate(drop * 0.25, R.headY + nod * 6 - talkBob * 0.5 + drop); ctx.rotate((o.tilt || 0) + nod * 0.05); ctx.scale(R.HS * (c.hx || 1), R.HS * (c.hy || 1));
  if (o.back) headBack(ctx, c, R); else head(ctx, c, R, o, t);
  if (ph === 'on' || ph === 'one') phonesHead(ctx, c, R, ph, o.phonesLift ?? 1, o.back);
  ctx.restore();
  if (c.headphones && !o.back) headphones(ctx, R);
  if (ph === 'neck' && !o.back && !HO) phonesNeck(ctx, c, R);

  if (!o.back && o.pose !== 'slump' && !HO) for (let i = 0; i < 2; i++) drawArm(ctx, c, R, i, o, t);
  if (o.pose === 'heart' && !o.back) { const [a, b] = R.hands; ctx.save(); ctx.translate((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 22); ctx.scale(0.42, 0.42); ctx.beginPath(); ctx.moveTo(0, 30); ctx.bezierCurveTo(-60, -10, -30, -55, 0, -25); ctx.bezierCurveTo(30, -55, 60, -10, 0, 30); ctx.closePath(); paint(ctx, '#ff4d6d', 9); ctx.restore(); }
  ctx.restore();
}
function drawArm(ctx, c, R, i, o, t) {
  const shp = R.sh[i], hd = R.hands[i], side = i ? 1 : -1;
  // elbow: of the two IK solutions take the one that points outward and down (never across the face)
  const A = c.arm || 70, e1 = ik(shp[0], shp[1], hd[0], hd[1], A, A, 1), e2 = ik(shp[0], shp[1], hd[0], hd[1], A, A, -1);
  const score = e => e[0] * side + e[1] * 0.35, el = score(e1) >= score(e2) ? e1 : e2;
  if (c.style === 'tee' || c.style === 'blouse' || c.style === 'polo') { hose(ctx, [shp, el, hd], 17, c.skin, LWP); hose(ctx, [shp, [lerp(shp[0], el[0], 0.55), lerp(shp[1], el[1], 0.55)]], 25, i ? c.shirt : c.shirtD, LWP); }
  else if (c.style === 'flannel') { // sleeves rolled up to the elbow
    const cuff = [lerp(el[0], hd[0], 0.12), lerp(el[1], hd[1], 0.12)];
    hose(ctx, [shp, el, hd], 18, c.skin, LWP); hose(ctx, [shp, el, cuff], 24, i ? c.shirt : c.shirtD, LWP);
    circle(ctx, cuff[0], cuff[1], 13); paint(ctx, c.shirtD, LWP * 0.7);
  }
  else hose(ctx, [shp, el, hd], 20, i ? c.shirt : c.shirtD, LWP);
  if (c.style === 'hoodie') { const a = Math.atan2(hd[1] - el[1], hd[0] - el[0]); circle(ctx, hd[0] - Math.cos(a) * 13, hd[1] - Math.sin(a) * 13, 10); paint(ctx, c.collar, LWP * 0.8); }
  const prop = o.hold?.[i];
  if (prop === 'tea') teaCup(ctx, hd[0] + side * 4, hd[1] + 6, 1, t, o.steam !== false);
  if (prop === 'coffee') icedCoffee(ctx, hd[0], hd[1] + 18, 1);
  if (prop === 'notebook') {}
  let kind = R.handKind[i], rot = R.handRot[i];
  if (o.point && (o.pose === 'reach' || o.pose === 'phone' ? i === 1 : o.pose === 'reachL' ? i === 0 : false)) { kind = 'point'; const a = Math.atan2(hd[1] - el[1], hd[0] - el[0]); rot = side > 0 ? a : a + Math.PI; } // reach + point: the finger follows the forearm
  handShape(ctx, hd[0], hd[1], side, kind, rot, c.skin);
  if (prop === 'marker') marker(ctx, hd[0] + side * 6, hd[1] - 4, 1, side * -0.5);
  if (prop === 'phone') phone(ctx, hd[0] + side * 4, hd[1] - 14, 1);
  if (prop === 'camera' && i === 1) camera(ctx, (R.hands[0][0] + hd[0]) / 2, (R.hands[0][1] + hd[1]) / 2 - 8, 1.05, 0, o.rec, t); // two-handed: centred between the hands
}
function shirtDetails(ctx, c, R) {
  const y = R.shY;
  if (c.style === 'polo') {
    poly(ctx, [[-22, y - 6], [0, y + 18], [-6, y + 26], [-28, y + 6]]); paint(ctx, c.collar, LWP * 0.8);
    poly(ctx, [[22, y - 6], [0, y + 18], [6, y + 26], [28, y + 6]]); paint(ctx, c.collar, LWP * 0.8);
    ctx.beginPath(); ctx.moveTo(0, y + 18); ctx.lineTo(0, y + 54); paint(ctx, null, 3.5);
    for (const yy of [y + 30, y + 44]) { circle(ctx, 3, yy, 2.6); paint(ctx, '#e8e4da', 0); }
  } else if (c.style === 'shirt') {
    poly(ctx, [[-20, y - 6], [-2, y + 16], [-10, y + 24], [-26, y + 4]]); paint(ctx, c.collar, LWP * 0.8);
    poly(ctx, [[20, y - 6], [2, y + 16], [10, y + 24], [26, y + 4]]); paint(ctx, c.collar, LWP * 0.8);
    ctx.beginPath(); ctx.moveTo(0, y + 16); ctx.lineTo(0, R.hipY + 10); paint(ctx, null, 3);
    for (let yy = y + 32; yy < R.hipY; yy += 24) { circle(ctx, 4, yy, 2.4); paint(ctx, '#ffffff', 0); }
    if (c.necktie) { poly(ctx, [[-6, y + 10], [6, y + 10], [10, y + 60], [0, y + 74], [-10, y + 60]]); paint(ctx, c.necktie, LWP * 0.7); rrect(ctx, -8, y + 2, 16, 12, 3); paint(ctx, c.necktie, LWP * 0.7); }
  } else if (c.style === 'blouse') {
    for (const k of [-1, 1]) { ctx.beginPath(); ctx.moveTo(0, y + 6); ctx.quadraticCurveTo(k * 26, y + 20, k * 26, y - 4); ctx.quadraticCurveTo(k * 12, y - 8, 0, y + 6); paint(ctx, c.collar, LWP * 0.7); }
    for (let yy = y + 26; yy < R.hipY - 4; yy += 22) { circle(ctx, 0, yy, 2.6); paint(ctx, c.shirtD, 0); }
  } else if (c.style === 'flannel') { // open flannel: the black tee shows down the middle, collar points either side
    const f8 = R.f * 8;
    poly(ctx, [[-15 + f8, y - 8], [15 + f8, y - 8], [19 + f8, R.hipY + 13], [-19 + f8, R.hipY + 13]]); paint(ctx, c.tee, LWP * 0.8);
    ctx.beginPath(); ctx.moveTo(-14 + f8, y - 8); ctx.quadraticCurveTo(f8, y + 6, 14 + f8, y - 8); paint(ctx, null, 3, '#4a4652');
    for (const k of [-1, 1]) { poly(ctx, [[k * 15 + f8, y - 8], [k * 30 + f8, y - 4], [k * 21 + f8, y + 26]]); paint(ctx, c.shirtD, LWP * 0.7); }
  } else if (c.style === 'tee') {
    ctx.beginPath(); ctx.moveTo(-20, y - 4); ctx.quadraticCurveTo(0, y + 16, 20, y - 4); paint(ctx, null, 4);
  } else if (c.style === 'hoodie') {
    smooth(ctx, [[-30, y - 2], [0, y + 14], [30, y - 2], [22, y - 14], [0, y - 4], [-22, y - 14]]); paint(ctx, c.shirtD, LWP * 0.8);
    for (const k of [-1, 1]) { ctx.beginPath(); ctx.moveTo(k * 8, y + 10); ctx.lineTo(k * 10, y + 46); paint(ctx, null, 3, '#fff3e6'); circle(ctx, k * 10, y + 48, 3); paint(ctx, '#fff3e6', 2); }
    rrect(ctx, -28, R.hipY - 36, 56, 30, 10); paint(ctx, c.shirtD, LWP * 0.8);
  }
}
function headphones(ctx, R, col = '#6fc3b8', band = '#5b6b7a', sc = 1) { // resting round the neck
  const y = R.shY - 4;
  ctx.beginPath(); ctx.arc(0, y - 6, 34, 0.15 * Math.PI, 0.85 * Math.PI); paint(ctx, null, 7, band);
  for (const k of [-1, 1]) { rrect(ctx, k * 34 - 11 * sc, y - 6, 22 * sc, 26 * sc, 8); paint(ctx, col, LWP * 0.8); }
}
function phonesNeck(ctx, c, R) { // big headphones resting round the neck, cups on the collar
  const y = R.shY, col = c.phonesCol || '#2a2633';
  ctx.save(); ctx.lineCap = 'round'; ctx.beginPath(); ctx.arc(0, y + 6, 22, 0.05 * Math.PI, 0.95 * Math.PI);
  ctx.strokeStyle = INK; ctx.lineWidth = 15; ctx.stroke(); ctx.strokeStyle = col; ctx.lineWidth = 8; ctx.stroke(); ctx.restore();
  for (const k of [-1, 1]) { ctx.save(); ctx.translate(k * 24, y + 20); ctx.rotate(k * -0.25); rrect(ctx, -13, -16, 26, 32, 10); paint(ctx, col, LWP * 0.8); rrect(ctx, k > 0 ? 6 : -14, -12, 8, 24, 4); paint(ctx, '#5a5468', 0); ctx.restore(); }
}
// big over-ear headphones in head space (they follow nods and tilts). 'one': the `lift` side cup (1 = screen right) is pushed up off the ear
function phonesHead(ctx, c, R, mode, lift, back) {
  const f = back ? 0 : R.f, col = c.phonesCol || '#2a2633';
  ctx.save(); ctx.lineCap = 'round'; ctx.beginPath(); if (back) ctx.ellipse(0, 0, 44, 50, 0, Math.PI * 1.06, Math.PI * 1.94); else ctx.ellipse(-f * 6, -2, 47, 62, 0, Math.PI * 1.04, Math.PI * 1.96);
  ctx.strokeStyle = INK; ctx.lineWidth = 17; ctx.stroke(); ctx.strokeStyle = col; ctx.lineWidth = 9; ctx.stroke(); ctx.restore();
  for (const k of [-1, 1]) {
    if (!back && k * f < -0.55) continue;           // far cup hidden behind the head
    const up = mode === 'one' && k === lift;
    ctx.save(); ctx.translate(k * 45 - f * 8, up ? -42 : 6); if (up) ctx.rotate(k * 0.6);
    rrect(ctx, -14, -22, 28, 44, 11); paint(ctx, col, LWP * 0.8);
    rrect(ctx, k > 0 ? -14 : 6, -15, 8, 30, 4); paint(ctx, '#5a5468', 0);
    ctx.beginPath(); ctx.moveTo(k * 5, -12); ctx.lineTo(k * 5, 2); paint(ctx, null, 3, 'rgba(255,255,255,0.35)');
    ctx.restore();
  }
}
function headBack(ctx, c) {
  oval(ctx, 0, 0, 39, 46); paint(ctx, c.hair, LWP);
  if (c.hairStyle === 'short') { for (const k of [-1, 1]) { oval(ctx, k * 30, 8, 9, 18); paint(ctx, c.gray, 0); } }
  if (c.hairStyle === 'ponytail') { smooth(ctx, [[-10, -10], [10, -10], [14, 40], [6, 76], [-6, 76], [-14, 40]]); paint(ctx, c.hair, LWP); rrect(ctx, -10, -14, 20, 10, 4); paint(ctx, c.tie, 3); }
  if (c.hairStyle === 'wavy') { for (let i = 0; i < 12; i++) { const a = i * TAU / 12; circle(ctx, Math.cos(a) * 30, -4 + Math.sin(a) * 34, 15); paint(ctx, c.hair, LWP); } oval(ctx, 0, -4, 36, 40); paint(ctx, c.hair, 0); }
  if (c.hairStyle === 'bob') { smooth(ctx, [[-50, -10], [-40, -44], [0, -56], [40, -44], [50, -10], [52, 26], [58, 46], [-58, 46], [-52, 26]]); paint(ctx, c.hair, LWP); ctx.save(); ctx.translate(24, -38); ctx.rotate(0.6); rrect(ctx, -12, -5, 24, 10, 4); paint(ctx, c.clip || '#ff5c8a', 3.5); ctx.restore(); }
  if (c.hairStyle === 'receding') { oval(ctx, 0, -6, 37, 38); paint(ctx, c.skin, 0); smooth(ctx, [[-40, -6], [-34, 26], [0, 40], [34, 26], [40, -6], [26, 14], [0, 22], [-26, 14]]); paint(ctx, c.hair, LWP * 0.8); }
  if (c.hairStyle === 'neat') { ctx.beginPath(); ctx.moveTo(-30, 30); ctx.quadraticCurveTo(0, 40, 30, 30); paint(ctx, null, 3, '#3a3340'); }
  if (c.hairStyle === 'messy') { for (let k = -2; k <= 2; k++) { poly(ctx, [[k * 14 - 9, -36], [k * 14 + 4, -60 + Math.abs(k) * 6], [k * 14 + 10, -34]]); paint(ctx, c.hair, LWP * 0.7); } }
  if (c.hairStyle === 'spiky') { for (let k = -2; k <= 2; k++) { const a = k * 0.3, r1 = 62 - Math.abs(k) * 4; poly(ctx, [[Math.sin(a - 0.22) * 38, -Math.cos(a - 0.22) * 38], [Math.sin(a) * r1 * 0.8, -Math.cos(a) * r1 - 4], [Math.sin(a + 0.22) * 38, -Math.cos(a + 0.22) * 38]]); paint(ctx, c.hair, LWP * 0.7); } }
  if (c.hairStyle === 'long') { smooth(ctx, [[-46, -20], [-30, -50], [0, -56], [30, -50], [46, -20], [50, 40], [52, 96], [44, 124], [-44, 124], [-52, 96], [-50, 40]]); paint(ctx, c.hair, LWP); }
  if (c.hairStyle === 'bun') { circle(ctx, 0, -50, 21); paint(ctx, c.hair, LWP); rrect(ctx, -13, -36, 26, 8, 4); paint(ctx, '#ffd23f', 3); }
  for (const k of [-1, 1]) { oval(ctx, k * 40, 6, 7, 12); paint(ctx, c.skin, LWP * 0.8); }
}
function head(ctx, c, R, o, t) {
  const f = R.f, fx = f * 10, E = c.eyeSize || 1, expr = o.expr || 'smile';
  // ponytail behind
  if (c.hairStyle === 'ponytail') { const sw = Math.sin(t * 2.2) * 0.1; ctx.save(); ctx.translate(-f * 40 - (f >= 0 ? 6 : -6), -30); ctx.rotate(sw + (f >= 0 ? 0.55 : -0.55) * Math.min(1, Math.abs(f) * 2 + 0.3)); smooth(ctx, [[-11, -4], [11, -4], [17, 34], [9, 70], [-3, 76], [-15, 36]]); paint(ctx, c.hair, LWP); rrect(ctx, -11, -6, 22, 10, 4); paint(ctx, c.tie, 3); ctx.restore(); }
  // short wavy hair: a curly cloud around the head
  if (c.hairStyle === 'wavy') { for (let i = 0; i < 11; i++) { const a = Math.PI * (0.95 + i * 0.11); circle(ctx, Math.cos(a) * 38, -8 + Math.sin(a) * 40 + (i % 2) * 3, 15); paint(ctx, c.hair, LWP); } for (const k of [-1, 1]) { circle(ctx, k * 40, 10, 13); paint(ctx, c.hair, LWP); } }
  // high bun on the crown
  if (c.hairStyle === 'bun') { circle(ctx, -f * 6, -70, 21); paint(ctx, c.hair, LWP); ctx.beginPath(); ctx.arc(-f * 6, -70, 12, 3.6, 5.6); paint(ctx, null, 3, 'rgba(255,255,255,0.25)'); rrect(ctx, -f * 6 - 13, -56, 26, 8, 4); paint(ctx, '#ffd23f', 3); }
  // shoulder-length bob behind the face
  if (c.hairStyle === 'bob') { smooth(ctx, [[-46, -24], [-42, -48], [-10, -60], [24, -58], [46, -42], [48, 0], [50, 26], [56, 44], [36, 44], [26, 28], [-26, 28], [-36, 44], [-56, 44], [-50, 26], [-48, 0]]); paint(ctx, c.hair, LWP); }
  // ears
  for (const k of [-1, 1]) { if (k * f < -0.5) continue; oval(ctx, k * 38 - f * 8, 6, 8, 12); paint(ctx, c.skin, LWP * 0.8); }
  // face
  const face = () => smooth(ctx, [[-36, -18], [-30, -40], [0, -48], [30, -40], [36, -18], [34, 14], [20, 38], [0, 46], [-20, 38], [-34, 14]]);
  cel(ctx, face, c.skin, c.skinD, -f * 6 - 3, -2, LWP);
  // hair (front)
  if (c.hairStyle === 'short') {
    smooth(ctx, [[-38, 2], [-38, -30], [-20, -50], [10, -54], [34, -42], [40, -12], [32, -24], [10, -34], [-14, -32], [-30, -16]]); paint(ctx, c.hair, LWP);
    for (const k of [-1, 1]) { oval(ctx, k * 35, -6, 5, 12); paint(ctx, c.gray, 0); }
  } else if (c.hairStyle === 'ponytail') {
    smooth(ctx, [[-38, 4], [-36, -30], [-12, -52], [18, -52], [38, -32], [38, 0], [30, -26], [8, -38], [-4, -30], [-26, -26]]); paint(ctx, c.hair, LWP);
  } else if (c.hairStyle === 'wavy') { // soft curls over the forehead
    for (let i = 0; i < 6; i++) { const x = -30 + i * 12; circle(ctx, x, -40 + Math.abs(i - 2.5) * 3, 15); paint(ctx, c.hair, LWP * 0.8); }
    smooth(ctx, [[-38, 0], [-38, -30], [-14, -50], [16, -50], [38, -30], [38, 0], [30, -24], [10, -30], [-10, -30], [-30, -22]]); paint(ctx, c.hair, 0);
  } else if (c.hairStyle === 'bob') { // side-swept fringe + a little clip
    smooth(ctx, [[-40, 6], [-39, -30], [-16, -54], [16, -54], [38, -36], [40, 2], [32, -20], [20, -32], [0, -30], [-18, -36], [-30, -18]]); paint(ctx, c.hair, LWP);
    ctx.save(); ctx.translate(24, -38); ctx.rotate(0.6); rrect(ctx, -12, -5, 24, 10, 4); paint(ctx, c.clip || '#ff5c8a', 3.5); ctx.restore();
  } else if (c.hairStyle === 'neat') { // short, side-parted
    smooth(ctx, [[-38, 4], [-39, -26], [-26, -48], [0, -55], [26, -50], [40, -30], [40, -2], [34, -22], [22, -34], [4, -40], [-12, -38], [-26, -26], [-32, -10]]); paint(ctx, c.hair, LWP);
    ctx.beginPath(); ctx.moveTo(-16, -52); ctx.quadraticCurveTo(-12, -44, -8, -36); paint(ctx, null, 3, '#3a3340');
    ctx.beginPath(); ctx.moveTo(-6, -40); ctx.quadraticCurveTo(14, -46, 32, -30); paint(ctx, null, 3, '#3a3340');
  } else if (c.hairStyle === 'part') { // neat side part, glossy fringe swept to one side
    smooth(ctx, [[-38, 2], [-39, -28], [-26, -50], [0, -58], [26, -53], [40, -34], [41, -2], [34, -20], [22, -27], [6, -31], [-8, -38], [-14, -47], [-20, -36], [-30, -22], [-34, -8]]); paint(ctx, c.hair, LWP);
    ctx.beginPath(); ctx.moveTo(-14, -47); ctx.lineTo(-11, -57); paint(ctx, null, 3, '#3a3340');
    ctx.beginPath(); ctx.moveTo(-2, -48); ctx.quadraticCurveTo(16, -50, 30, -38); paint(ctx, null, 4, 'rgba(255,255,255,0.28)');
  } else if (c.hairStyle === 'receding') { // older man: bald crown with a shine, grey tufts over the ears, a few combed strands
    for (const k of [-1, 1]) { smooth(ctx, [[k * 30, -30], [k * 42, -14], [k * 42, 10], [k * 36, 16], [k * 33, -8], [k * 24, -26]]); paint(ctx, c.hair, LWP * 0.8); }
    for (const dx of [-8, 2, 12]) { ctx.beginPath(); ctx.moveTo(dx - 10, -44); ctx.quadraticCurveTo(dx, -50, dx + 10, -45); paint(ctx, null, 2.5, c.gray); }
    oval(ctx, -12, -36, 9, 4, -0.4); ctx.fillStyle = 'rgba(255,255,255,0.45)'; ctx.fill();
  } else if (c.hairStyle === 'spiky') { // gelled spikes standing straight up, with a shine
    for (let k = -2; k <= 2; k++) { const a = k * 0.3, b = -Math.cos(a), r0 = 40, r1 = 64 - Math.abs(k) * 4; poly(ctx, [[Math.sin(a - 0.22) * r0, b * r0 - 6], [Math.sin(a) * r1 * 0.8 + k * 3, -Math.cos(a) * r1 - 6], [Math.sin(a + 0.22) * r0, b * r0 - 6]]); paint(ctx, c.hair, LWP * 0.8); }
    smooth(ctx, [[-39, 2], [-38, -30], [-18, -50], [12, -52], [36, -38], [40, -2], [32, -22], [18, -32], [2, -36], [-16, -32], [-30, -18]]); paint(ctx, c.hair, LWP);
    for (const k of [-1, 1]) { ctx.beginPath(); ctx.moveTo(k * 10, -50); ctx.lineTo(k * 14, -66); paint(ctx, null, 3.5, 'rgba(255,255,255,0.35)'); }
  } else if (c.hairStyle === 'long') { // centre part, straight curtains framing the face down to the shoulders
    smooth(ctx, [[-44, 50], [-43, -24], [-26, -50], [0, -58], [26, -50], [43, -24], [44, 50], [36, 52], [35, 0], [24, -26], [3, -40], [0, -35], [-3, -40], [-24, -26], [-35, 0], [-36, 52]]); paint(ctx, c.hair, LWP);
    ctx.beginPath(); ctx.moveTo(-10, -50); ctx.quadraticCurveTo(-26, -36, -30, -6); paint(ctx, null, 3, 'rgba(255,255,255,0.22)');
  } else if (c.hairStyle === 'bun') { // pulled back tight, no fringe
    smooth(ctx, [[-38, 2], [-38, -30], [-18, -52], [0, -55], [18, -52], [38, -30], [38, 2], [33, -20], [16, -34], [0, -37], [-16, -34], [-33, -20]]); paint(ctx, c.hair, LWP);
    for (const dx of [-14, 0, 14]) { ctx.beginPath(); ctx.moveTo(dx * 1.6, -38); ctx.quadraticCurveTo(dx, -48, dx * 0.4, -54); paint(ctx, null, 2.5, 'rgba(255,255,255,0.22)'); }
  } else if (c.hairStyle === 'messy') {
    for (let k = -3; k <= 3; k++) { const a = k * 0.42, r0 = 40; poly(ctx, [[Math.sin(a - 0.25) * r0, -Math.cos(a - 0.25) * r0 - 4], [Math.sin(a) * (r0 + 22 + (k % 2) * 8), -Math.cos(a) * (r0 + 18 + (k % 2) * 8)], [Math.sin(a + 0.25) * r0, -Math.cos(a + 0.25) * r0 - 4]]); paint(ctx, c.hair, LWP * 0.8); }
    smooth(ctx, [[-38, 0], [-36, -32], [-10, -50], [20, -50], [38, -30], [38, 0], [26, -20], [14, -28], [2, -18], [-12, -28], [-26, -18]]); paint(ctx, c.hair, LWP);
  }
  // blink (auto) + eyes
  const seed = c.H * 0.37, cyc = (t + hash(seed) * 3) % 3.6;
  const closed = expr === 'proud' || expr === 'laugh' || expr === 'sleep' || (cyc > 3.45 && expr !== 'panic' && expr !== 'surprised' && expr !== 'wink');
  const lx = (o.look?.[0] ?? f * 0.6) * 4, ly = (o.look?.[1] ?? 0) * 3;
  const ey = -6, eyes = [-15 + fx, 15 + fx];
  for (const [i, ex] of eyes.entries()) {
    const shrink = (i === 0 && f > 0.4) || (i === 1 && f < -0.4) ? 0.85 : 1;
    if (expr === 'wink' && i === 1) { ctx.beginPath(); ctx.moveTo(ex - 10 * E, ey + 2); ctx.quadraticCurveTo(ex, ey - 9 * E, ex + 10 * E, ey + 2); paint(ctx, null, 5); continue; } // ^ closed eye
    if (expr === 'love') { const hs = 0.3 * E * (1 + Math.max(0, Math.sin(t * 10)) * 0.15); ctx.save(); ctx.translate(ex, ey); ctx.scale(hs, hs); ctx.beginPath(); ctx.moveTo(0, 30); ctx.bezierCurveTo(-60, -10, -30, -55, 0, -25); ctx.bezierCurveTo(30, -55, 60, -10, 0, 30); ctx.closePath(); paint(ctx, '#ff4d6d', 12); ctx.restore(); continue; } // heart eyes
    if (closed) { ctx.beginPath(); ctx.arc(ex, ey + 2, 8 * E, Math.PI * 1.1, Math.PI * 1.9); paint(ctx, null, 4); continue; }
    const big = expr === 'surprised' || expr === 'panic' ? 1.2 : 1;
    // cartoon eyes: big whites, small pupils (Getaway Car style)
    oval(ctx, ex, ey, 9.5 * E * shrink * big, 12 * E * big); paint(ctx, P.white, 4);
    circle(ctx, ex + lx * 1.4 + 1, ey + 1.5 + ly * 1.3, (expr === 'panic' || expr === 'surprised' ? 2.6 : 3.8) * E * shrink); paint(ctx, P.eye, 0);
    circle(ctx, ex + lx * 1.4 - 0.5, ey - 0.5 + ly * 1.3, 1.3 * E); paint(ctx, '#ffffff', 0);
    if (c.lashes) { const k = i ? 1 : -1; ctx.lineCap = 'round'; for (const [a, l] of [[0.35, 7], [0.8, 6]]) { ctx.beginPath(); ctx.moveTo(ex + k * Math.sin(a) * 9.5 * E, ey - Math.cos(a) * 12 * E); ctx.lineTo(ex + k * Math.sin(a) * (9.5 * E + l), ey - Math.cos(a) * (12 * E + l)); paint(ctx, null, 3.5); } }
  }
  // brows
  // tired: heavy half-closed lids + eye bags
  if (expr === 'tired' && !closed) for (const ex of eyes) {
    ctx.save(); oval(ctx, ex, ey, 9.5 * E, 12 * E); ctx.clip(); ctx.fillStyle = c.skinD; ctx.fillRect(ex - 14 * E, ey - 14 * E, 28 * E, 13 * E); ctx.restore();
    ctx.beginPath(); ctx.moveTo(ex - 10 * E, ey - 1); ctx.lineTo(ex + 10 * E, ey - 1); paint(ctx, null, 4);
    ctx.beginPath(); ctx.arc(ex, ey + 9 * E, 8 * E, 0.2 * Math.PI, 0.8 * Math.PI); paint(ctx, null, 2.5, c.skinD);
  }
  // tears welling up (o.tears 0..1): a wet shine over the lower lids, then a drop rolling down
  if (o.tears > 0) for (const [i, ex] of eyes.entries()) { ctx.save(); ctx.globalAlpha = Math.min(1, o.tears * 2); ctx.beginPath(); ctx.ellipse(ex, ey + 8 * E, 9 * E, 3.2 * E, 0, 0, Math.PI); paint(ctx, 'rgba(140,210,255,0.9)', 2.5); if (o.tears > 0.5) { const k = ((t * 0.8 + i * 0.4) % 1); ctx.beginPath(); const dx = ex + (i ? 9 : -9) * E, dy = ey + 12 * E + k * 26; ctx.moveTo(dx, dy - 7); ctx.quadraticCurveTo(dx + 5, dy + 2, dx, dy + 4); ctx.quadraticCurveTo(dx - 5, dy + 2, dx, dy - 7); paint(ctx, '#8fd3ff', 2); } ctx.restore(); }
  const bA = { worried: 0.3, sleep: 0.05, focus: -0.3, panic: 0.45, surprised: -0.1, thinking: 0, determined: -0.25, proud: -0.05, tired: 0.22 }[expr] ?? -0.08;
  // thick bushy brows with an ink outline; they carry the emotion
  for (const [i, ex] of eyes.entries()) { const k = i ? 1 : -1; ctx.save(); ctx.translate(ex, ey - 13 * E - 4 - (expr === 'surprised' || expr === 'panic' ? 5 : 0) - (expr === 'thinking' && i ? 6 : 0)); ctx.rotate(k * bA * 1.3); ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(-10, 0); ctx.lineTo(10, 0); ctx.strokeStyle = INK; ctx.lineWidth = c.thinBrows ? 7 : 11; ctx.stroke(); ctx.beginPath(); ctx.moveTo(-10, 0); ctx.lineTo(10, 0); ctx.strokeStyle = c.browCol || '#3d2b26'; ctx.lineWidth = c.thinBrows ? 3 : 6; ctx.stroke(); ctx.restore(); }
  // glasses
  if (c.glasses) { const gr = 14 * E; for (const ex of eyes) { circle(ctx, ex, ey, gr); paint(ctx, 'rgba(255,255,255,0.2)', 4); } ctx.beginPath(); ctx.moveTo(eyes[0] + gr, ey); ctx.lineTo(eyes[1] - gr, ey); paint(ctx, null, 4); }
  // nose + blush
  for (const ex of eyes) { oval(ctx, ex + (ex < fx ? -5 : 5), 14, 9, 5); ctx.fillStyle = P.blush; ctx.fill(); }
  const nx = fx + f * 9, dir = f >= 0 ? 1 : -1;
  if (c.nose === 'bulb') { oval(ctx, nx + 3, 9, 12, 10.5); paint(ctx, '#d98266', 4); oval(ctx, nx, 5, 3.5, 2.5); paint(ctx, 'rgba(255,255,255,0.65)', 0); }
  else if (c.nose === 'point') { ctx.beginPath(); ctx.moveTo(nx - dir * 2, -2); ctx.quadraticCurveTo(nx + dir * 22, 10, nx + dir * 24, 14); ctx.quadraticCurveTo(nx + dir * 10, 17, nx - dir * 1, 14); paint(ctx, c.skinD, 4); }
  else if (c.nose === 'button') { oval(ctx, nx + 2, 9, 7, 6); paint(ctx, '#e48f74', 3.5); }
  else { ctx.beginPath(); ctx.moveTo(fx + f * 6 + 2, 2); ctx.quadraticCurveTo(fx + f * 10 + 6, 12, fx + f * 4, 14); paint(ctx, null, 3.5, c.skinD); }
  // beard (Smei)
  if (c.beard) {
    smooth(ctx, [[-34, 8], [-30, 30], [-14, 46], [0, 52], [14, 46], [30, 30], [34, 8], [24, 22], [10, 30], [0, 32], [-10, 30], [-24, 22]]); paint(ctx, '#4b4545', LWP * 0.8);
    for (const [px, py] of [[-20, 30], [16, 34], [0, 44], [-8, 38], [24, 22]]) { circle(ctx, px, py, 1.6); paint(ctx, c.gray, 0); }
    smooth(ctx, [[fx - 15, 20], [fx - 7, 15], [fx, 17], [fx + 7, 15], [fx + 15, 20], [fx + 8, 22], [fx, 20], [fx - 8, 22]]); paint(ctx, '#3e3838', 3); // neat mustache (filled, not an arch: an arch reads as a frown)
  }
  // mouth: lip-sync overrides the resting shape
  const m = o.mouth || 0, mx = fx + f * 3, my = c.beard ? 30 : 27;
  if (m > 0.06) {
    const h = 4 + 14 * m, w = 11 + 4 * m;
    oval(ctx, mx, my + h * 0.3, w, h * 0.6 + 2); paint(ctx, P.mouth, 3.5);
    ctx.save(); oval(ctx, mx, my + h * 0.3, w, h * 0.6 + 2); ctx.clip(); oval(ctx, mx, my + h * 0.9, w * 0.7, h * 0.35); paint(ctx, P.tongue, 0); ctx.fillStyle = '#fff'; ctx.fillRect(mx - w, my + h * 0.3 - h * 0.6 - 2, w * 2, 4); ctx.restore();
  } else if (expr === 'grin' || expr === 'laugh' || expr === 'wink' || expr === 'love') {
    ctx.beginPath(); ctx.moveTo(mx - 14, my - 2); ctx.quadraticCurveTo(mx, my + 20, mx + 14, my - 2); ctx.closePath(); paint(ctx, P.mouth, 3.5);
    ctx.save(); ctx.beginPath(); ctx.moveTo(mx - 14, my - 2); ctx.quadraticCurveTo(mx, my + 20, mx + 14, my - 2); ctx.closePath(); ctx.clip(); ctx.fillStyle = '#fff'; ctx.fillRect(mx - 15, my - 4, 30, 6); ctx.restore();
  } else if (expr === 'surprised' || expr === 'panic') { oval(ctx, mx, my + 4, 7, 9); paint(ctx, P.mouth, 3.5); }
  else if (expr === 'sleep') { oval(ctx, mx + 2, my + 3, 5, 6); paint(ctx, P.mouth, 3); }
  else if (expr === 'focus') { ctx.beginPath(); ctx.moveTo(mx - 9, my + 2); ctx.lineTo(mx + 9, my + 1); paint(ctx, null, 3.5); oval(ctx, mx + 7, my + 7, 6, 7); paint(ctx, P.tongue, 3); } // tongue poking out in concentration
  else if (expr === 'worried') { ctx.beginPath(); ctx.moveTo(mx - 9, my + 4); ctx.quadraticCurveTo(mx, my - 2, mx + 9, my + 4); paint(ctx, null, 3.5); }
  else if (expr === 'thinking') { ctx.beginPath(); ctx.moveTo(mx - 7, my + 2); ctx.lineTo(mx + 7, my - 1); paint(ctx, null, 3.5); }
  else if (expr === 'tired') { ctx.beginPath(); ctx.moveTo(mx - 9, my + 3); ctx.quadraticCurveTo(mx - 3, my, mx, my + 3); ctx.quadraticCurveTo(mx + 4, my + 6, mx + 9, my + 2); paint(ctx, null, 3.5); }
  else { ctx.beginPath(); ctx.moveTo(mx - 10, my); ctx.quadraticCurveTo(mx, my + (expr === 'calm' ? 6 : 9), mx + 10, my); paint(ctx, null, 3.5); }
}

// ---------------------------------------------------------------- office chair (3/4 view)
export function chair(ctx, x, y, s = 1, rot = 0, col = '#6c7a96') {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  for (const a of [-1, -0.35, 0.35, 1]) { ctx.beginPath(); ctx.moveTo(0, -20); ctx.lineTo(a * 52, -4); paint(ctx, null, 6); circle(ctx, a * 52, -4, 6); paint(ctx, '#3b3b44', 3); }
  rrect(ctx, -5, -110, 10, 92, 4); paint(ctx, '#9aa3b5', 4);
  ctx.save(); ctx.rotate(rot * 0.15);
  rrect(ctx, -60, -128, 120, 26, 12); paint(ctx, col, LWP);
  ctx.restore();
  ctx.restore();
}
export function chairBack(ctx, x, y, s = 1, col = '#6c7a96') { ctx.save(); ctx.translate(x, y); ctx.scale(s, s); rrect(ctx, -54, -290, 108, 170, 26); paint(ctx, col, LWP); rrect(ctx, -6, -122, 12, 20, 4); paint(ctx, '#9aa3b5', 4); ctx.restore(); }
