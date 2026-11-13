// Renderer.
//   node src/render.mjs stills 1.0 5.2 ...      -> build/stills/t_XX.png + build/stills/sheet_*.png
//   node src/render.mjs video [workers]          -> build/video.mp4 (silent, rendered in parallel segments)
//   node src/render.mjs segment <f0> <f1> <out>  -> one segment (used by video)
import { createCanvas } from '@napi-rs/canvas';
import { spawn, execFileSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import { fileURLToPath } from 'node:url';
import { W, H, FPS } from './core.mjs';
import { drawFrame, DURATION } from './shots.mjs';

const [mode, ...args] = process.argv.slice(2);
fs.mkdirSync('build/stills', { recursive: true });
fs.mkdirSync('build/seg', { recursive: true });

function frameCanvas() { const cv = createCanvas(W, H); return [cv, cv.getContext('2d')]; }

if (mode === 'stills') {
  const [cv, ctx] = frameCanvas();
  const files = [];
  for (const a of args) {
    const t = parseFloat(a);
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, W, H);
    drawFrame(ctx, t);
    const f = `build/stills/t_${t.toFixed(2)}.png`;
    fs.writeFileSync(f, cv.toBuffer('image/png'));
    files.push(f);
  }
  // contact sheets of up to 9 (3x3)
  for (let i = 0; i < files.length; i += 9) {
    const grp = files.slice(i, i + 9);
    const inputs = grp.flatMap(f => ['-i', f]);
    const n = grp.length, cols = Math.min(3, n), rows = Math.ceil(n / 3);
    const scaled = grp.map((_, k) => `[${k}:v]scale=640:360[s${k}]`).join(';');
    const layout = grp.map((_, k) => `${(k % 3) * 640}_${Math.floor(k / 3) * 360}`).join('|');
    const out = `build/stills/sheet_${i / 9}.png`;
    const filter = n === 1 ? `[0:v]scale=640:360` : `${scaled};${grp.map((_, k) => `[s${k}]`).join('')}xstack=inputs=${n}:layout=${layout}:fill=black`;
    execFileSync('ffmpeg', ['-v', 'error', '-y', ...inputs, '-filter_complex', filter, out]);
    console.log(out, grp.map(f => f.replace('build/stills/t_', '').replace('.png', '')).join(' '));
  }
} else if (mode === 'segment') {
  const [f0, f1, out] = [parseInt(args[0]), parseInt(args[1]), args[2]];
  const [cv, ctx] = frameCanvas();
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', `${W}x${H}`, '-r', `${FPS}`, '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-g', '48', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const write = buf => new Promise(res => (ff.stdin.write(buf) ? res() : ff.stdin.once('drain', res)));
  for (let f = f0; f < f1; f++) {
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, W, H);
    drawFrame(ctx, f / FPS);
    await write(Buffer.from(cv.data()));
  }
  ff.stdin.end();
  await new Promise(res => ff.on('close', res));
} else if (mode === 'video') {
  const total = Math.round(DURATION * FPS);
  const nW = parseInt(args[0] || Math.max(2, os.cpus().length - 1));
  const per = Math.ceil(total / nW);
  const self = fileURLToPath(import.meta.url);
  const t0 = Date.now();
  const jobs = [];
  for (let i = 0; i < nW; i++) {
    const f0 = i * per, f1 = Math.min(total, (i + 1) * per);
    if (f0 >= f1) break;
    const out = `build/seg/seg_${String(i).padStart(2, '0')}.mp4`;
    jobs.push({ out, p: new Promise((res, rej) => { const c = spawn('node', [self, 'segment', f0, f1, out], { stdio: 'inherit' }); c.on('close', code => (code ? rej(new Error('segment ' + i)) : res())); }) });
  }
  await Promise.all(jobs.map(j => j.p));
  fs.writeFileSync('build/seg/list.txt', jobs.map(j => `file '${j.out.replace('build/seg/', '')}'`).join('\n'));
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'build/seg/list.txt', '-c', 'copy', 'build/video.mp4']);
  console.log(`rendered ${total} frames (${DURATION}s) in ${((Date.now() - t0) / 1000).toFixed(1)}s -> build/video.mp4`);
}
