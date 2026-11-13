// Cover / thumbnail: `node src/cover.mjs` -> film/cover.png (1920x1080) + film/cover_1280.jpg (YouTube size)
import { createCanvas } from '@napi-rs/canvas';
import fs from 'node:fs';
import { execFileSync } from 'node:child_process';
import { W, H, INK, TAU, rrect, paint, poly, oval, circle, text } from './core.mjs';
import { person, anchors, CAST } from './people.mjs';
import { radialLines } from './kit.mjs';
import * as pl from './places.mjs';
import * as e from './ep6.mjs';
import * as q from './ep7.mjs';
import * as fx from './fx.mjs';

const film = JSON.parse(fs.readFileSync('film.json', 'utf8'));
const cv = createCanvas(W, H), ctx = cv.getContext('2d');
const t = 1.3;

// the hallway in golden light, a pink burst behind Kimlong, sunflowers drifting
ctx.save(); ctx.translate(960, 600); ctx.scale(1.25, 1.25); ctx.translate(-960, -600); pl.hallway(ctx, t, { openB: 1, gold: 0.6 }); ctx.restore();
ctx.save(); ctx.globalAlpha = 0.85; radialLines(ctx, t, 960, 640, { n: 24, spd: 0, col: 'rgba(255,143,171,0.45)', inner: 220 }); ctx.restore();
q.sunflowers(ctx, 4.2, 1, 14);

const at = (who, o, headY) => ({ ...o, y: headY - anchors(who, { ...o, x: 0, y: 0 }).head[1] });
// Sopheak (left) — the same-age friend, fist out
const kO = at('sopheak', { x: 370, s: 1.75, facing: 0.35, pose: 'bump', expr: 'laugh', phones: 'neck' }, 770);
person(ctx, 'sopheak', { ...kO, t });
// Channy (right) — one eyebrow up, folder in hand
const cO = at('channy', { x: 1570, s: 1.7, facing: -0.35, pose: 'hold', expr: 'thinking' }, 660);
person(ctx, 'channy', { ...cO, t });
{ const h = anchors('channy', cO).handR; q.folder(ctx, h[0] + 14, h[1] - 10, 1.4, 0.12); }
// Kimlong (centre) — the wink, hand on heart, crown on the spikes
const gO = at('kimlong', { x: 960, s: 2.15, facing: 0.1, pose: 'chest', expr: 'wink' }, 640);
person(ctx, 'kimlong', { ...gO, t });
const hd = anchors('kimlong', gO).head;
q.flirtFx(ctx, hd[0], hd[1], 0.7, 1, 1.6);
ctx.save(); ctx.translate(hd[0] + 10, hd[1] - 230); ctx.rotate(-0.12); ctx.scale(2.0, 2.0); e.ICON.crown(ctx); ctx.restore();
fx.sfxText(ctx, 'ប្លុក!', 1620, 360, 0.5, { size: 110, fill: '#a4aab8', rot: 0.1 });
// tags
e.tag(ctx, 430, 360, 'ស្ដេចញ៉ែ', 1, { icon: 'crown', col: '#fff6e6', ink: '#e8433a', size: 70, rot: -0.06 });
e.tag(ctx, 420, 520, 'អ្នកថតវីដេអូ', 1, { icon: 'cam', col: '#fff6e6', ink: '#2d3a6b', size: 52, rot: -0.03 });
// title banner
ctx.save(); ctx.translate(960, 150); ctx.rotate(-0.02);
rrect(ctx, -700, -110, 1400, 220, 60); paint(ctx, '#fff6e6', 10);
text(ctx, 'គីមឡុង ស្ដេចញ៉ែ', 0, -22, { size: 108, fill: '#e8433a', lw: 14 });
text(ctx, 'Episode 7: Kimlong, the King of Flirting', 0, 66, { size: 42, font: 'Arial Black', fill: '#2d3a6b', lw: 0 });
ctx.restore();

fs.mkdirSync('film', { recursive: true });
fs.writeFileSync('film/cover.png', cv.toBuffer('image/png'));
execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', 'film/cover.png', '-vf', 'scale=1280:720', '-q:v', '2', 'film/cover_1280.jpg']);
console.log(`-> film/cover.png, film/cover_1280.jpg (${film.title})`);
