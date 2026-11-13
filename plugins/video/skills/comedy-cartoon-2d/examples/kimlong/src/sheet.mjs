// Model sheet for the cast: poses + expressions. `npm run sheet` -> build/stills/sheet.png
import { createCanvas } from '@napi-rs/canvas';
import fs from 'node:fs';
import { W, H } from './core.mjs';
import { person, chair, chairBack, notebook } from './people.mjs';
fs.mkdirSync('build/stills', { recursive: true });
const cv = createCanvas(W, H), ctx = cv.getContext('2d');
ctx.fillStyle = '#fbefe2'; ctx.fillRect(0, 0, W, H);
ctx.fillStyle = '#efd9c4'; ctx.fillRect(0, 540, W, 540);
const r1 = 520, r2 = 1060, t = 0.5;
// row 1: Kimlong
person(ctx, 'kimlong', { x: 130, y: r1, facing: 0.2, expr: 'smile', t });
person(ctx, 'kimlong', { x: 340, y: r1, facing: 0.3, expr: 'wink', pose: 'leanWall', t });
person(ctx, 'kimlong', { x: 560, y: r1, facing: 0.1, expr: 'love', pose: 'chest', t, mouth: 0.5 });
person(ctx, 'kimlong', { x: 780, y: r1, facing: 0, expr: 'grin', pose: 'cheer', t });
person(ctx, 'kimlong', { x: 1000, y: r1, facing: 0.2, expr: 'determined', pose: 'film', hold: [null, 'camera'], rec: true, t });
person(ctx, 'kimlong', { x: 1220, y: r1, facing: -0.4, expr: 'surprised', t });
person(ctx, 'kimlong', { x: 1430, y: r1, back: true, t });
person(ctx, 'kimlong', { x: 1650, y: r1, facing: 0.3, expr: 'laugh', pose: 'belly', t });
person(ctx, 'kimlong', { x: 1840, y: r1, facing: 0.2, expr: 'grin', pose: 'fixHair', t });
// row 2: Channy, Sreyneang, and the regulars' new poses
person(ctx, 'channy', { x: 130, y: r2, facing: 0.2, expr: 'calm', t });
person(ctx, 'channy', { x: 330, y: r2, facing: -0.4, expr: 'thinking', pose: 'hold', t });
person(ctx, 'channy', { x: 530, y: r2, facing: 0.3, expr: 'grin', t, mouth: 0.4 });
person(ctx, 'channy', { x: 720, y: r2, back: true, t });
person(ctx, 'sreyneang', { x: 910, y: r2, facing: 0.2, expr: 'grin', t });
person(ctx, 'sreyneang', { x: 1100, y: r2, facing: -0.4, expr: 'laugh', pose: 'wag', t });
person(ctx, 'sreyneang', { x: 1280, y: r2, back: true, t });
person(ctx, 'smey', { x: 1470, y: r2, facing: 0.2, expr: 'tired', pose: 'facepalm', t });
person(ctx, 'nimith', { x: 1650, y: r2, facing: -0.2, expr: 'tired', pose: 'facepalm', t });
person(ctx, 'sopheak', { x: 1830, y: r2, facing: -0.3, expr: 'laugh', pose: 'belly', t });
fs.writeFileSync('build/stills/sheet.png', cv.toBuffer('image/png'));
console.log('build/stills/sheet.png');
