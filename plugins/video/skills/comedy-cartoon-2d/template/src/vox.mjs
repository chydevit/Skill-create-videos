// Dialogue clips: loading, pause-tightening, real durations and lip-sync envelopes.
// `node src/vox.mjs` caches every available clip to build/vox/<id>.f32 + <id>.json and prints the timings.
// Shots read lineDur()/mouth data (so the timeline follows the real voices); audio.mjs mixes the samples.
import fs from 'node:fs';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const SR = 44100, FPS = 24;
export const VCFG = fs.existsSync('voices/lines.json') ? JSON.parse(fs.readFileSync('voices/lines.json', 'utf8')) : { voices: {}, lines: {} };
export const LINES = VCFG.lines || {};
export const whoSays = id => LINES[id]?.[0];

// VoxCPM leaves long pauses at "!" / "។" and sometimes a breath after the last word:
// shrink pauses over 0.22s to 0.15s, and drop a tail shorter than 0.2s that follows a long pause.
function tightenPauses(x) {
  const win = Math.round(0.01 * SR), nW = Math.floor(x.length / win), rms = new Float32Array(nW);
  let mx = 0;
  for (let w = 0; w < nW; w++) { let e = 0; for (let i = w * win; i < (w + 1) * win; i++) e += x[i] * x[i]; rms[w] = Math.sqrt(e / win); mx = Math.max(mx, rms[w]); }
  const loud = w => rms[w] > mx * 0.03;
  const runs = []; let st = -1;
  for (let w = 0; w <= nW; w++) { const q = w < nW && !loud(w); if (q && st < 0) st = w; if (!q && st >= 0) { runs.push([st, w]); st = -1; } }
  const keep = new Uint8Array(nW).fill(1);
  for (const [a, b] of runs) if (b - a > 22 && a > 0) { for (let w = a + 8; w < b - 7; w++) keep[w] = 0; if (b >= nW - 20 || nW - b < 20) for (let w = a + 8; w < nW; w++) keep[w] = 0; }
  const out = []; for (let w = 0; w < nW; w++) if (keep[w]) for (let i = w * win; i < (w + 1) * win; i++) out.push(x[i]);
  return Float32Array.from(out);
}
const VOICE_FX = {
  intercom: ',highpass=f=500,lowpass=f=2800,acrusher=bits=8:mix=0.25',
  radio: ',highpass=f=350,lowpass=f=3400,acompressor=threshold=0.1:ratio=6',
  phone: ',highpass=f=300,lowpass=f=3000',
  thought: ',aecho=0.8:0.55:70|140:0.35|0.18', // inner voice (lines.json "fx": { "<line id>": "thought" })
};
const srcWav = id => `build/vox/${id}.wav`;
// mouth openness per frame (0..1) from the clip's loudness
function envelope(x) {
  const n = Math.ceil(x.length / SR * FPS), hop = SR / FPS, env = new Float32Array(n);
  for (let f = 0; f < n; f++) { let e = 0, c = 0; for (let i = Math.floor(f * hop); i < Math.min(x.length, Math.floor((f + 1) * hop)); i++) { e += x[i] * x[i]; c++; } env[f] = Math.sqrt(e / Math.max(1, c)); }
  const sorted = Array.from(env).sort((a, b) => a - b), p95 = sorted[Math.floor(sorted.length * 0.95)] || 1e-4;
  for (let f = 0; f < n; f++) env[f] = Math.pow(Math.min(1, Math.max(0, (env[f] / p95 - 0.12) * 1.25)), 0.7);
  return env;
}
// Process one clip (cached by source mtime). Returns {dur, env:number[]} or null when the clip doesn't exist yet.
export function prepare(id) {
  const [who, text] = LINES[id], V = VCFG.voices[who] || {};
  let wav = srcWav(id), viaSay = false;
  if (!fs.existsSync(wav)) {
    if (!V.say) return null;
    wav = `build/vox/${id}.say.aiff`; viaSay = true;
    if (!fs.existsSync(wav)) execFileSync('say', ['-v', V.say.voice || 'Samantha', '-r', String(V.say.rate || 180), '-o', wav, text]);
  }
  const raw = `build/vox/${id}.f32`, meta = `build/vox/${id}.json`, mtime = fs.statSync(wav).mtimeMs;
  if (fs.existsSync(meta)) { const m = JSON.parse(fs.readFileSync(meta, 'utf8')); if (m.mtime === mtime && fs.existsSync(raw)) return m; }
  const af = (viaSay ? `asetrate=22050*${V.say.pitch || 1},` : '') + 'aresample=44100,highpass=f=70' + (VOICE_FX[VCFG.fx?.[id] || V.fx] || '');
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', wav, '-af', af, '-f', 'f32le', '-ac', '1', '-ar', '44100', raw]);
  const b = fs.readFileSync(raw);
  const x = tightenPauses(new Float32Array(b.buffer, b.byteOffset, b.length / 4).slice());
  let pk = 0; for (const v of x) pk = Math.max(pk, Math.abs(v));
  for (let i = 0; i < x.length; i++) x[i] *= 0.85 / Math.max(pk, 1e-4);
  fs.writeFileSync(raw, Buffer.from(x.buffer));
  const m = { mtime, dur: x.length / SR, env: Array.from(envelope(x), v => Math.round(v * 100) / 100) };
  fs.writeFileSync(meta, JSON.stringify(m));
  return m;
}
const META = {};
// cached metadata only (cheap; safe inside render workers)
export function meta(id) {
  if (id in META) return META[id];
  const p = `build/vox/${id}.json`;
  return (META[id] = fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, 'utf8')) : null);
}
// real duration, or an estimate from the text (~11 Khmer characters/s) until the clip exists
export const estimated = id => !meta(id);
export function lineDur(id) {
  const m = meta(id); if (m) return m.dur;
  const text = LINES[id]?.[3] || LINES[id]?.[1] || '';
  return 0.3 + text.replace(/\s/g, '').length / 11;
}
// processed samples for mixing
export function samples(id) {
  if (!prepare(id)) throw new Error(`missing ${srcWav(id)}: run \`npm run voices\` (VoxCPM2), or give voice "${whoSays(id)}" a "say" fallback`);
  const b = fs.readFileSync(`build/vox/${id}.f32`); return new Float32Array(b.buffer, b.byteOffset, b.length / 4).slice();
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  fs.mkdirSync('build/vox', { recursive: true });
  let have = 0;
  for (const id of Object.keys(LINES)) {
    const m = prepare(id); if (m) have++;
    console.log(`${id.padEnd(5)} ${m ? m.dur.toFixed(2) + 's' : ' --  '} ${LINES[id][0].padEnd(9)} ${LINES[id][1]}`);
  }
  console.log(`${have}/${Object.keys(LINES).length} clips ready`);
}
