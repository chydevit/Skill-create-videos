// STARTER FILM — a ~9 s demo of the patterns. Replace it with your film's shots.
// Each shot: shot(start, end, draw(ctx, lt, t), cues). lt = time inside the shot, t = film time.
import { W, H, C, INK, TAU, paint, circle, clamp, lerp, seg, ease, onTwos, hash, wobble } from './core.mjs';
import { shot, setShift, duration, cam, shk, P, arc, titleCard, toScreen } from './kit.mjs';
import { benny, car } from './chars.mjs';
import * as bg from './bg.mjs';
import * as fx from './fx.mjs';

// helper: the car with Benny at the wheel (crew draws inside the windows, clipped by them)
const bennyCar = (ctx, o, bE = 'worried') => car(ctx, {
  ...o, crew: c => { c.beginPath(); c.ellipse(106, -150, 7, 26, 0.25, 0, TAU); paint(c, null, 6, '#2a2a30'); benny(c, { x: 46, y: -84, s: 0.6, pose: 'drive', expr: bE, sweat: 1, t: o.t, wheel: [94, -112] }); },
});

// ---- S01 establishing: street, title card, the car idles --------------------------------
shot(0.0, 3.0, (ctx, lt, t) => {
  ctx.save(); cam(ctx, 960, 540, 1 + lt * 0.015);
  bg.sky(ctx, { horizon: 790, cloudX: t * 12 });
  bg.farCity(ctx, 0, 690); bg.midCity(ctx, 260, 790); bg.shopRow(ctx, 640, 790);
  bg.street(ctx, 0, 860); bg.lamp(ctx, 1250, 830);
  const hop = Math.abs(Math.sin(onTwos(lt) * 6)) * -6;            // idle shiver, held on twos
  bennyCar(ctx, { x: 1200, y: 950, s: 1, face: 'worried', t, bounce: hop, bag: { x: -40, y: -238, s: 0.62 } });
  fx.exhaust(ctx, 1200 - 214, 950 - 57, t, { rate: 1.6 });
  ctx.restore();
  titleCard(ctx, lt, 'STARTER TOON', { outAt: 2.3 });
}, [[0.3, 'sting_title'], [0.35, 'boing', { pitch: 1.3 }], [2.3, 'zip_down'], [1.0, 'music', { id: 'm1', style: 'sneak' }]]);

// ---- S02 close-up: Benny gulps, then says his line ----------------------------------------
shot(3.0, 6.0, (ctx, lt, t) => {
  const [sx, sy] = shk(t, lt > 1.2 && lt < 1.5 ? 8 : 0);
  ctx.save(); ctx.translate(sx, sy);
  bg.speedBG(ctx, t, { speed: 400, horizon: 640, groundY: 900 });
  const ex = lt < 1.2 ? 'gulp' : 'panic';
  const pop = lt > 1.2 ? wobble(lt - 1.2, 3, 6) * 0.12 : 0;        // squash & stretch on the reaction
  benny(ctx, { x: 960, y: 1500, s: 4.2, expr: ex, sweat: 1, t, sq: pop, look: [0.3, 0.2] });
  fx.sfxText(ctx, 'ម៉ែអើយ!', 1450, 300, seg(lt, 1.25, 2.6), { size: 120, fill: C.yellow, rot: 0.08, wob: 3 });
  ctx.restore();
}, [[0.0, 'music_end', { id: 'm1' }], [0.3, 'gulp'], [1.2, 'sting_shock'], [1.25, 'v_starter_yelp']]);

// ---- S03 the car zooms off (anticipation, smear, dust), iris out ------------------------------
shot(6.0, 9.0, (ctx, lt, t) => {
  ctx.save(); cam(ctx, 960, 540, 1);
  bg.sky(ctx, { horizon: 790, cloudX: t * 12 });
  bg.farCity(ctx, 0, 690); bg.midCity(ctx, 260, 790); bg.shopRow(ctx, 640, 790);
  bg.street(ctx, 0, 860);
  const wind = seg(lt, 0.2, 0.6), go = seg(lt, 0.6, 0.85);
  const x = lerp(1200, 3200, ease.in3(go));
  if (go > 0 && go < 1) for (let i = 1; i <= 4; i++) { ctx.save(); ctx.globalAlpha = 0.16; bennyCar(ctx, { x: x - i * 110, y: 950, s: 1, t, face: 'grimace' }); ctx.restore(); }
  bennyCar(ctx, { x: x - wind * 40, y: 950, s: 1, t, face: 'grimace', sq: go > 0 ? 0.25 * (1 - go) : -0.12 * wind, tilt: wind * 0.05, bag: { x: -40, y: -238, s: 0.62 } }, 'determined');
  fx.dust(ctx, 1080, 930, seg(lt, 0.6, 1.4), { n: 7, spread: 260, r: 60, seed: 3 });
  fx.sfxText(ctx, 'ZOOM!', 1300, 520, seg(lt, 0.62, 1.3), { size: 120 });
  ctx.restore();
  const [ix, iy] = toScreen(1060, 900, 960, 540, 1);
  fx.iris(ctx, ix, iy, lt < 1.6 ? 2000 : lerp(2000, 0, ease.inOut(seg(lt, 1.6, 2.6))));
}, [[0.2, 'engine_rev', { dur: 0.45 }], [0.6, 'zoom_off'], [0.62, 'skid_short'], [0.6, 'music', { id: 'm2', style: 'chase', melody: true }], [2.2, 'music_end', { id: 'm2', how: 'fade', dur: 0.6 }], [2.4, 'end_button']]);

export { drawFrame, allCues } from './kit.mjs';
export const DURATION = duration();
