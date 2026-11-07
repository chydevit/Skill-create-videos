// Small synthesis kit for the logo stings: every sound is generated here, no samples.
import fs from 'node:fs';

export const SR = 48000;
export const smooth = x => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));

export function noise(seed) {
  let a = seed;
  return () => {
    a |= 0; a = a + 0x6D2B79F5 | 0;
    let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296 * 2 - 1;
  };
}
export function mulberry32(a) {
  return function () {
    a |= 0; a = a + 0x6D2B79F5 | 0;
    let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

export const track = dur => ({ L: new Float64Array(Math.round(dur * SR)), R: new Float64Array(Math.round(dur * SR)), n: Math.round(dur * SR) });
const panGains = p => [Math.cos((p + 1) * Math.PI / 4) * Math.SQRT2, Math.sin((p + 1) * Math.PI / 4) * Math.SQRT2];
function put(tr, i, v, pan) {
  if (i < 0 || i >= tr.n) return;
  const [gl, gr] = panGains(pan);
  tr.L[i] += v * gl; tr.R[i] += v * gr;
}

// Band-passed air noise: centre frequency fa -> fb (at the peak) -> fc, panned p0 -> p1.
export function whoosh(tr, t0, tp, t1, { gain = 0.2, fa = 300, fb = 2300, fc = 900, p0 = 0, p1 = 0, q = 0.85, body = 2.2, seed = 11 } = {}) {
  const nA = noise(seed), nB = noise(seed + 12), nC = noise(seed + 26);
  let lowL = 0, bandL = 0, lowR = 0, bandR = 0, bd = 0;
  for (let i = Math.floor(t0 * SR); i < Math.min(tr.n, Math.floor(t1 * SR)); i++) {
    const t = i / SR;
    const rise = smooth((t - t0) / (tp - t0)), fall = smooth((t - tp) / (t1 - tp));
    const env = t < tp ? Math.pow(rise, 1.7) : Math.pow(1 - fall, 2.2);
    const fcur = t < tp ? fa + (fb - fa) * rise : fb + (fc - fb) * fall;
    const f = 2 * Math.sin(Math.PI * fcur / SR);
    const common = nA(), inL = 0.7 * common + 0.3 * nB(), inR = 0.7 * common + 0.3 * nC();
    lowL += f * bandL; bandL += f * (inL - lowL - q * bandL);
    lowR += f * bandR; bandR += f * (inR - lowR - q * bandR);
    bd += 0.018 * (common - bd);
    const [gl, gr] = panGains(p0 + (p1 - p0) * smooth((t - t0) / (t1 - t0)));
    tr.L[i] += (bandL + body * bd) * env * gl * gain;
    tr.R[i] += (bandR + body * bd) * env * gr * gain;
  }
}

// Soft keyboard click: a short filtered tick plus a little body.
export function click(tr, t, { gain = 0.25, seed = 1, pan = 0, fc = 3200, bodyHz = 190, decay = 0.011, bodyGain = 0.5 } = {}) {
  const n = noise(seed);
  const s0 = Math.round(t * SR), len = Math.round(0.09 * SR);
  const f = 2 * Math.sin(Math.PI * fc / SR);
  let low = 0, band = 0;
  for (let i = 0; i < len; i++) {
    const tt = i / SR, att = Math.min(1, i / 20);
    low += f * band; band += f * (n() - low - 0.6 * band);
    const v = (band * Math.exp(-tt / decay) + bodyGain * Math.sin(2 * Math.PI * bodyHz * tt) * Math.exp(-tt / 0.02)) * att * gain;
    put(tr, s0 + i, v, pan);
  }
}

// Bell / pluck tone with a few partials.
export function tone(tr, t, freq, { gain = 0.2, pan = 0, attack = 0.004, tau = 0.5, partials = [[1, 1, 1], [2, 0.16, 0.55], [3, 0.05, 0.35], [4.2, 0.03, 0.22]] } = {}) {
  const s0 = Math.round(t * SR);
  for (const [ratio, amp, tauK] of partials) {
    const w = 2 * Math.PI * freq * ratio / SR, td = tau * tauK;
    const len = Math.min(tr.n - s0, Math.round(td * 7 * SR));
    for (let i = 0; i < len; i++) {
      const tt = i / SR;
      const att = tt < attack ? 0.5 - 0.5 * Math.cos(Math.PI * tt / attack) : 1;
      put(tr, s0 + i, gain * amp * att * Math.exp(-tt / td) * Math.sin(w * i), pan);
    }
  }
}

export function chime(tr, t, gain = 0.3) {
  tone(tr, t, 1318.51, { gain, pan: -0.15, tau: 0.6 });
  tone(tr, t + 0.055, 1975.53, { gain: gain * 0.55, pan: 0.2, tau: 0.55 });
  tone(tr, t, 659.25, { gain: gain * 0.25, tau: 0.7 });
}

// Low "hit": a sine whose pitch drops from f0 to f1.
export function sub(tr, t, { gain = 0.35, f0 = 95, f1 = 48, tau = 0.4, pan = 0 } = {}) {
  const s0 = Math.round(t * SR), len = Math.min(tr.n - s0, Math.round(tau * 6 * SR));
  let ph = 0;
  for (let i = 0; i < len; i++) {
    const tt = i / SR;
    ph += 2 * Math.PI * (f1 + (f0 - f1) * Math.exp(-tt / 0.07)) / SR;
    const att = Math.min(1, tt / 0.006);
    put(tr, s0 + i, gain * att * Math.exp(-tt / tau) * Math.sin(ph), pan);
  }
}

// Warm sustained chord: detuned sine pairs with a slow swell and gentle movement.
export function pad(tr, t0, t1, freqs, { gain = 0.06, attack = 2, release = 1.5, seed = 5 } = {}) {
  const rnd = mulberry32(seed);
  for (const f of freqs) for (const d of [-0.0035, 0.0035]) {
    const ph = rnd() * Math.PI * 2, lfo = 0.12 + rnd() * 0.15, pan = d < 0 ? -0.45 : 0.45;
    const w = 2 * Math.PI * f * (1 + d) / SR;
    for (let i = Math.floor(t0 * SR); i < Math.min(tr.n, Math.floor(t1 * SR)); i++) {
      const tt = i / SR - t0;
      const env = smooth(tt / attack) * (1 - smooth((i / SR - (t1 - release)) / release));
      const v = (Math.sin(w * i + ph) + 0.22 * Math.sin(2 * w * i + ph) + 0.06 * Math.sin(3 * w * i)) *
        (1 + 0.18 * Math.sin(2 * Math.PI * lfo * tt + ph));
      put(tr, i, v * env * gain, pan);
    }
  }
}

// Gliding sine (for "light" lines).
export function glide(tr, t0, t1, f0, f1, { gain = 0.08, pan = 0 } = {}) {
  let ph = 0;
  for (let i = Math.floor(t0 * SR); i < Math.min(tr.n, Math.floor(t1 * SR)); i++) {
    const u = (i / SR - t0) / (t1 - t0);
    ph += 2 * Math.PI * (f0 + (f1 - f0) * smooth(u)) / SR;
    const env = Math.sin(Math.PI * u);
    put(tr, i, gain * env * env * (Math.sin(ph) + 0.15 * Math.sin(2 * ph)), pan);
  }
}

function reverbChannel(x, combMs, apMs, n) {
  const y = new Float64Array(n);
  for (const ms of combMs) {
    const d = Math.round(ms * SR / 1000), buf = new Float64Array(d);
    let idx = 0, lp = 0;
    for (let i = 0; i < n; i++) {
      const o = buf[idx];
      lp = o * 0.6 + lp * 0.4;
      buf[idx] = x[i] + lp * 0.8;
      idx = (idx + 1) % d;
      y[i] += o / combMs.length;
    }
  }
  for (const ms of apMs) {
    const d = Math.round(ms * SR / 1000), buf = new Float64Array(d);
    let idx = 0;
    for (let i = 0; i < n; i++) {
      const b = buf[idx], v = y[i];
      buf[idx] = v + b * 0.5;
      y[i] = b - v * 0.5;
      idx = (idx + 1) % d;
    }
  }
  return y;
}

// Add room reverb, fade the tail out at the end, normalise to `peak` and write a 24-bit WAV.
export function finish(tr, path, { wet = 0.22, fadeFrom = null, peak = 0.7 } = {}) {
  const wl = reverbChannel(tr.L, [29.7, 37.1, 41.1, 43.7], [5.0, 1.7], tr.n);
  const wr = reverbChannel(tr.R, [31.3, 35.9, 40.3, 45.1], [5.3, 1.9], tr.n);
  const dur = tr.n / SR, f0 = fadeFrom ?? dur - 0.4;
  let m = 0;
  for (let i = 0; i < tr.n; i++) {
    const t = i / SR;
    const fade = t > f0 ? Math.cos(Math.PI / 2 * smooth((t - f0) / (dur - f0))) : 1;
    tr.L[i] = (tr.L[i] + wet * wl[i]) * fade;
    tr.R[i] = (tr.R[i] + wet * wr[i]) * fade;
    m = Math.max(m, Math.abs(tr.L[i]), Math.abs(tr.R[i]));
  }
  const g = peak / m;
  const data = Buffer.alloc(tr.n * 6);
  for (let i = 0; i < tr.n; i++) {
    data.writeIntLE(Math.max(-8388608, Math.min(8388607, Math.round(tr.L[i] * g * 8388607))), i * 6, 3);
    data.writeIntLE(Math.max(-8388608, Math.min(8388607, Math.round(tr.R[i] * g * 8388607))), i * 6 + 3, 3);
  }
  const hdr = Buffer.alloc(44);
  hdr.write('RIFF', 0); hdr.writeUInt32LE(36 + data.length, 4); hdr.write('WAVE', 8);
  hdr.write('fmt ', 12); hdr.writeUInt32LE(16, 16); hdr.writeUInt16LE(1, 20); hdr.writeUInt16LE(2, 22);
  hdr.writeUInt32LE(SR, 24); hdr.writeUInt32LE(SR * 6, 28); hdr.writeUInt16LE(6, 32); hdr.writeUInt16LE(24, 34);
  hdr.write('data', 36); hdr.writeUInt32LE(data.length, 40);
  fs.writeFileSync(path, Buffer.concat([hdr, data]));
}
