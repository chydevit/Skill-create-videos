// Builds the sound for one render from the events the style reported (info.json -> "events").
// usage: node sfx.mjs <info.json> <out.wav>
// Every sound is synthesised (audio.mjs); event types are listed in SOUNDS below.
import fs from 'node:fs';
import { SR, track, whoosh, click, tone, chime, sub, pad, glide, finish, noise, mulberry32 } from './audio.mjs';

const [infoPath, out] = process.argv.slice(2);
const info = JSON.parse(fs.readFileSync(infoPath, 'utf8'));
const tr = track(5);
const gains = pan => [Math.cos((pan + 1) * Math.PI / 4) * Math.SQRT2, Math.sin((pan + 1) * Math.PI / 4) * Math.SQRT2];
const add = (i, v, pan = 0) => { if (i < 0 || i >= tr.n) return; const [l, r] = gains(pan); tr.L[i] += v * l; tr.R[i] += v * r; };
const rnd = mulberry32(17);

// Pitched pop / water-drop "plop": a sine whose pitch springs from f0 up to f1.
function plop({ t, gain = 0.2, f0 = 360, f1 = 1000, rise = 0.04, tau = 0.06, pan = 0 }) {
  const s0 = Math.round(t * SR), len = Math.round((rise + tau * 7) * SR);
  let ph = 0;
  for (let i = 0; i < len; i++) {
    const tt = i / SR;
    ph += 2 * Math.PI * f0 * Math.pow(f1 / f0, Math.min(1, tt / rise)) / SR;
    add(s0 + i, gain * Math.min(1, tt / 0.0015) * Math.exp(-tt / tau) * (Math.sin(ph) + 0.1 * Math.sin(2 * ph)), pan);
  }
}
// Electric zap: band-passed noise burst with a little mains buzz.
function zap({ t, gain = 0.1, dur = 0.08, fc = 3200, pan = 0 }) {
  const n = noise(Math.round(t * 1000) + 7), s0 = Math.round(t * SR), len = Math.round(dur * 3 * SR);
  const f = 2 * Math.sin(Math.PI * fc / SR);
  let low = 0, band = 0;
  for (let i = 0; i < len; i++) {
    const tt = i / SR;
    low += f * band; band += f * (n() - low - 0.5 * band);
    add(s0 + i, gain * Math.min(1, tt / 0.002) * Math.exp(-tt / (dur * 0.5)) * (band + 0.25 * Math.sign(Math.sin(2 * Math.PI * 120 * tt))), pan);
  }
}
// Neon transformer hum.
function hum({ t0, t1, level = 0.008, boostAt = null }) {
  for (let i = Math.floor(t0 * SR); i < Math.min(tr.n, Math.floor(t1 * SR)); i++) {
    const t = i / SR, w = 2 * Math.PI * 120 * t;
    const env = level * Math.min(1, (t - t0) / 0.5) * (boostAt != null && t > boostAt ? 1.6 + 0.6 * Math.exp(-(t - boostAt) * 3) : 1);
    const v = Math.sin(w) + 0.5 * Math.sin(2 * w) + 0.3 * Math.sin(3 * w + 0.4) + 0.18 * Math.sin(5 * w) + 0.1 * Math.sin(7 * w);
    add(i, env * v * (1 + 0.08 * Math.sin(2 * Math.PI * 7 * t)));
  }
}
function crackle({ t0, t1, pan = 0 }) {
  for (let t = t0; t < t1; t += 0.025 + rnd() * 0.05)
    click(tr, t, { gain: 0.03 + rnd() * 0.03, seed: 50 + Math.floor(rnd() * 999), fc: 5000 + rnd() * 3000, bodyGain: 0, pan: pan - 0.2 + rnd() * 0.4 });
}
const PADS = { warm: [220, 277.18, 329.63, 440], bright: [261.63, 329.63, 392, 523.25], dark: [110, 164.81, 220, 329.63], calm: [146.83, 220, 293.66, 369.99] };

const SOUNDS = {
  whoosh: e => whoosh(tr, e.t0, e.tp, e.t1, e),
  plop: e => plop(e),
  sub: e => sub(tr, e.t, e),
  click: e => click(tr, e.t, { seed: Math.round(e.t * 997), ...e }),
  tock: e => click(tr, e.t, { gain: e.gain ?? 0.25, seed: Math.round(e.t * 991), fc: 2300, bodyHz: e.bodyHz ?? 420, decay: 0.02, bodyGain: 0.9, pan: e.pan ?? 0 }),
  glide: e => glide(tr, e.t0, e.t1, e.f0, e.f1, e),
  tone: e => tone(tr, e.t, e.f, { partials: [[1, 1, 1], [2.01, 0.15, 0.4]], ...e }),
  zap: e => zap(e),
  hum: e => hum(e),
  crackle: e => crackle(e),
  shimmer: e => [1318.51, 1661.22, 1975.53, 2637.02].forEach((f, i) =>
    tone(tr, e.t + i * 0.07, f, { gain: e.gain ?? 0.035, tau: 0.32, pan: -0.35 + i * 0.22, partials: [[1, 1, 1], [2, 0.1, 0.5]] })),
  sparkle: e => { for (let i = 0; i < (e.n ?? 6); i++) tone(tr, e.t + i * 0.045 + rnd() * 0.02, 2200 + rnd() * 1800, { gain: e.gain ?? 0.018, tau: 0.08, pan: (e.pan ?? 0) - 0.25 + rnd() * 0.5, partials: [[1, 1, 1]] }); },
  ping: e => { click(tr, e.t - 0.02, { gain: 0.12, seed: 61, fc: 4200, bodyHz: 240, decay: 0.012, bodyGain: 0.4, pan: e.pan ?? 0 });
    tone(tr, e.t, 1046.5, { gain: 0.07, tau: 0.8, pan: e.pan ?? 0, partials: [[1, 1, 1], [2, 0.08, 0.4], [3, 0.03, 0.25]] });
    sub(tr, e.t, { gain: 0.12, f0: 75, f1: 46, tau: 0.6, pan: (e.pan ?? 0) * 0.7 }); },
  chime: e => { chime(tr, e.t, e.gain ?? 0.3); sub(tr, e.t, { gain: 0.08, f0: 82, f1: 52, tau: 0.6 }); },
  pad: e => pad(tr, e.t0, e.t1 ?? 5, PADS[e.mood] || PADS.warm, { gain: e.gain ?? 0.02, attack: e.attack ?? 1.4, release: 1.2, seed: 31 }),
};

for (const e of info.events || []) {
  const f = SOUNDS[e.type];
  if (!f) { console.warn('unknown sound event', e.type); continue; }
  f(e);
}
finish(tr, out, { wet: 0.26, fadeFrom: (info.times && info.times.fadeFrom) || 4.5 });
console.log('wrote', out);
