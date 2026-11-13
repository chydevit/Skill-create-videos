// Soundtrack: synthesized jazz score + cartoon SFX + dialogue, mixed to build/audio.wav, plus subtitles.
// Everything is driven by the cues in shots.mjs (see the skill's references/audio.md for the cue catalogue).
import fs from 'node:fs';
import { execFileSync } from 'node:child_process';
import { allCues, DURATION } from './shots.mjs';

const SR = 44100, N = Math.ceil((DURATION + 1) * SR), TAU = Math.PI * 2;
const mk = () => [new Float32Array(N), new Float32Array(N)];
const BUS = { music: mk(), sfx: mk(), vox: mk() };
const cues = allCues();
const UNKNOWN = new Set();

// ---------------------------------------------------------------- DSP basics
let seed = 12345;
const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
const noise = () => rnd() * 2 - 1;
const midi = m => 440 * Math.pow(2, (m - 69) / 12);
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
class Biquad {
  constructor(type, f, q = 0.707) { this.type = type; this.x1 = this.x2 = this.y1 = this.y2 = 0; this.set(f, q); }
  set(f, q = this.q) {
    this.q = q; f = clamp(f, 10, SR * 0.45);
    const w = TAU * f / SR, c = Math.cos(w), s = Math.sin(w), a = s / (2 * q);
    let b0, b1, b2, a0 = 1 + a, a1 = -2 * c, a2 = 1 - a;
    if (this.type === 'lp') { b0 = (1 - c) / 2; b1 = 1 - c; b2 = (1 - c) / 2; }
    else if (this.type === 'hp') { b0 = (1 + c) / 2; b1 = -(1 + c); b2 = (1 + c) / 2; }
    else { b0 = a; b1 = 0; b2 = -a; } // bandpass (0 dB peak)
    this.b0 = b0 / a0; this.b1 = b1 / a0; this.b2 = b2 / a0; this.a1 = a1 / a0; this.a2 = a2 / a0;
  }
  p(x) { const y = this.b0 * x + this.b1 * this.x1 + this.b2 * this.x2 - this.a1 * this.y1 - this.a2 * this.y2; this.x2 = this.x1; this.x1 = x; this.y2 = this.y1; this.y1 = y; return y; }
}
// band-limited saw via polyBLEP
function blep(t, dt) { if (t < dt) { t /= dt; return t + t - t * t - 1; } if (t > 1 - dt) { t = (t - 1) / dt; return t * t + t + t + 1; } return 0; }
class Saw { constructor() { this.ph = rnd(); } n(f) { const dt = f / SR; this.ph += dt; if (this.ph >= 1) this.ph -= 1; return 2 * this.ph - 1 - blep(this.ph, dt); } }
const buf = sec => new Float32Array(Math.max(1, Math.ceil(sec * SR)));
function mix(bus, t0, b, gain = 1, pan = 0) {
  const [L, R] = BUS[bus]; const i0 = Math.round(t0 * SR);
  const gl = gain * Math.cos((pan + 1) * Math.PI / 4) * Math.SQRT2, gr = gain * Math.sin((pan + 1) * Math.PI / 4) * Math.SQRT2;
  for (let i = 0; i < b.length; i++) { const k = i0 + i; if (k < 0 || k >= N) continue; L[k] += b[i] * gl; R[k] += b[i] * gr; }
}
const fadeEdges = (b, a = 0.004, r = 0.02) => { const na = a * SR, nr = r * SR; for (let i = 0; i < b.length; i++) { if (i < na) b[i] *= i / na; const j = b.length - i; if (j < nr) b[i] *= j / nr; } return b; };

// ---------------------------------------------------------------- instruments
function bassNote(f, dur, vel = 1) {
  const b = buf(dur + 0.25), lp = new Biquad('lp', 1100);
  for (let i = 0; i < b.length; i++) {
    const t = i / SR; let e = Math.exp(-t * 3.2) * Math.min(1, t * 400); if (t > dur) e *= Math.exp(-(t - dur) * 30);
    const x = Math.sin(TAU * f * t) + 0.55 * Math.sin(TAU * 2 * f * t) * Math.exp(-t * 7) + 0.3 * Math.sin(TAU * 3 * f * t) * Math.exp(-t * 12) + 0.25 * noise() * Math.exp(-t * 60);
    b[i] = lp.p(x) * e * vel * 0.55;
  }
  return b;
}
function kick(vel = 1) { const b = buf(0.4); for (let i = 0; i < b.length; i++) { const t = i / SR; b[i] = Math.sin(TAU * (45 * t + 65 / 25 * (1 - Math.exp(-t * 25)))) * Math.exp(-t * 9) * vel; } return b; }
function snare(vel = 1, tone = 190) { const b = buf(0.3), bp = new Biquad('bp', 2200, 0.7); for (let i = 0; i < b.length; i++) { const t = i / SR; b[i] = (bp.p(noise()) * 1.6 * Math.exp(-t * 16) + Math.sin(TAU * tone * t) * 0.5 * Math.exp(-t * 28)) * vel; } return b; }
function ride(vel = 1) { const b = buf(0.9), hp = new Biquad('hp', 5000, 0.7); for (let i = 0; i < b.length; i++) { const t = i / SR; b[i] = (hp.p(noise()) * 0.35 * Math.exp(-t * 6) + (Math.sin(TAU * 3250 * t) + 0.7 * Math.sin(TAU * 4870 * t) + 0.4 * Math.sin(TAU * 6120 * t)) * 0.12 * Math.exp(-t * 9)) * vel; } return b; }
function hat(vel = 1, len = 0.05) { const b = buf(len + 0.05), hp = new Biquad('hp', 7500, 0.7); for (let i = 0; i < b.length; i++) { const t = i / SR; b[i] = hp.p(noise()) * Math.exp(-t / len * 3) * vel; } return b; }
function crash(vel = 1, len = 2.2) { const b = buf(len), hp = new Biquad('hp', 3500, 0.6); for (let i = 0; i < b.length; i++) { const t = i / SR; b[i] = (hp.p(noise()) * 0.7 + Math.sin(TAU * 3870 * t + Math.sin(TAU * 517 * t) * 3) * 0.12) * Math.exp(-t * 2.4) * vel; } return b; }
function tom(f = 120, vel = 1) { const b = buf(0.6); for (let i = 0; i < b.length; i++) { const t = i / SR; b[i] = Math.sin(TAU * (f * t - f * 0.3 / 8 * (1 - Math.exp(-t * 8)))) * Math.exp(-t * 7) * vel + noise() * 0.1 * Math.exp(-t * 50); } return b; }
// brass section stab / sustained chord: detuned saws with a filter "blat"
function brass(notes, dur, { vel = 1, bright = 1, att = 0.012, fall = 0, wah = 0 } = {}) {
  const b = buf(dur + 0.15), lp = new Biquad('lp', 800, 1.1);
  const osc = notes.flatMap(m => [-7, 0, 6].map(c => ({ s: new Saw(), f: midi(m) * Math.pow(2, c / 1200) })));
  for (let i = 0; i < b.length; i++) {
    const t = i / SR;
    let e = Math.min(1, t / att) * (0.75 + 0.25 * Math.exp(-t * 10)); if (t > dur) e *= Math.exp(-(t - dur) * 28);
    const bend = fall > 0 && t > dur * 0.4 ? Math.pow(2, -fall * (t - dur * 0.4) / (dur * 0.6) / 12) : 1;
    let x = 0; for (const o of osc) x += o.s.n(o.f * bend);
    if (i % 32 === 0) lp.set((500 + 3600 * bright * Math.exp(-t * 9) + 900 * bright) * (wah ? 0.55 + 0.45 * Math.sin(TAU * wah * t) : 1), 1.1);
    b[i] = lp.p(x / osc.length) * e * vel * 0.9;
  }
  return b;
}
// solo trumpet line note
function trumpet(m, dur, vel = 1, { scoop = true, oct = 0 } = {}) {
  const b = buf(dur + 0.12), lp = new Biquad('lp', 2000, 1.3), s1 = new Saw(), s2 = new Saw();
  const f = midi(m + oct);
  for (let i = 0; i < b.length; i++) {
    const t = i / SR;
    const sc = scoop ? Math.pow(2, -0.8 * Math.exp(-t * 40) / 12) : 1;
    const vib = 1 + 0.006 * Math.sin(TAU * 5.6 * t) * Math.min(1, Math.max(0, t - 0.12) * 4);
    let e = Math.min(1, t / 0.015) * (0.85 + 0.15 * Math.exp(-t * 8)); if (t > dur) e *= Math.exp(-(t - dur) * 35);
    if (i % 32 === 0) lp.set(1200 + 2600 * e * vel);
    b[i] = lp.p(s1.n(f * sc * vib) * 0.7 + s2.n(f * sc * vib * 1.003) * 0.3) * e * vel * 0.8;
  }
  return b;
}
function xylo(m, vel = 1) { const b = buf(0.6), f = midi(m); for (let i = 0; i < b.length; i++) { const t = i / SR; b[i] = (Math.sin(TAU * f * t) * Math.exp(-t * 9) + 0.35 * Math.sin(TAU * f * 3.93 * t) * Math.exp(-t * 30) + 0.15 * Math.sin(TAU * f * 9.2 * t) * Math.exp(-t * 60)) * vel * 0.5; } return b; }
function rhodes(notes, dur, vel = 1) {
  const b = buf(dur + 0.6);
  for (const m of notes) { const f = midi(m); for (let i = 0; i < b.length; i++) { const t = i / SR; let e = Math.exp(-t * 1.6) * Math.min(1, t * 300); if (t > dur) e *= Math.exp(-(t - dur) * 8); const I = 1.4 * Math.exp(-t * 4); b[i] += Math.sin(TAU * f * t + I * Math.sin(TAU * f * t)) * e * (1 + 0.15 * Math.sin(TAU * 4.5 * t)) * vel * 0.18; } }
  return b;
}
// synth pluck (saw through a closing low-pass): arpeggios for the "tech" style
function pluck(f, dur = 0.25, vel = 1, bright = 1) {
  const b = buf(dur + 0.15), lp = new Biquad('lp', 3000, 2), s = new Saw(), s2 = new Saw();
  for (let i = 0; i < b.length; i++) {
    const t = i / SR; if (i % 32 === 0) lp.set(300 + 3800 * bright * Math.exp(-t * 18), 2);
    let e = Math.exp(-t * 7) * Math.min(1, t * 600); if (t > dur) e *= Math.exp(-(t - dur) * 40);
    b[i] = lp.p(s.n(f) * 0.6 + s2.n(f * 1.006) * 0.4) * e * vel * 0.5;
  }
  return b;
}
// soft synth pad (slow attack/release, filtered detuned saws)
function pad(notes, dur, vel = 1, cutoff = 1100) {
  const b = buf(dur + 1.0), lp = new Biquad('lp', cutoff, 0.7);
  const osc = notes.flatMap(m => [-8, 0, 7].map(c => ({ s: new Saw(), f: midi(m) * Math.pow(2, c / 1200) })));
  for (let i = 0; i < b.length; i++) {
    const t = i / SR; let e = Math.min(1, t / 0.6); if (t > dur) e *= Math.exp(-(t - dur) * 4);
    let x = 0; for (const o of osc) x += o.s.n(o.f);
    b[i] = lp.p(x / osc.length) * e * vel * 0.5;
  }
  return b;
}
function trombone(m0, m1, dur, { vel = 1, wah = 0 } = {}) {
  const b = buf(dur + 0.1), lp = new Biquad('lp', 900, 1.4), s = new Saw();
  for (let i = 0; i < b.length; i++) {
    const t = i / SR, k = t / dur;
    const f = midi(m0 + (m1 - m0) * Math.min(1, k * 1.3)) * (1 + 0.012 * Math.sin(TAU * 5 * t) * k);
    let e = Math.min(1, t / 0.03); if (t > dur) e *= Math.exp(-(t - dur) * 30);
    if (i % 32 === 0) lp.set(wah ? 350 + 1300 * (0.5 - 0.5 * Math.cos(TAU * wah * t)) : 1100);
    b[i] = lp.p(s.n(f)) * e * vel;
  }
  return b;
}

// ---------------------------------------------------------------- SFX synths
const SFX = {
  slide(f0, f1, dur, vel = 1) { const b = buf(dur + 0.05), bp = new Biquad('bp', f0, 6); let ph = 0; for (let i = 0; i < b.length; i++) { const t = i / SR, k = Math.min(1, t / dur); const f = f0 * Math.pow(f1 / f0, k) * (1 + 0.012 * Math.sin(TAU * 7 * t)); ph += f / SR; if (i % 32 === 0) bp.set(f, 6); const e = Math.min(1, t / 0.02) * (t > dur ? Math.exp(-(t - dur) * 60) : 1); b[i] = (Math.sin(TAU * ph) * 0.8 + bp.p(noise()) * 0.25) * e * vel * 0.5; } return b; },
  boing(pitch = 1, vel = 1) { const b = buf(0.7); let ph = 0; for (let i = 0; i < b.length; i++) { const t = i / SR; const f = 190 * pitch * (1 + 0.55 * Math.exp(-t * 5) * Math.sin(TAU * 16 * t)) * (1 + 0.4 * Math.exp(-t * 3)); ph += f / SR; const x = Math.sin(TAU * ph) + 0.35 * Math.sin(TAU * 2 * ph) + 0.2 * Math.sin(TAU * 3 * ph); b[i] = x * Math.exp(-t * 4.5) * Math.min(1, t * 300) * vel * 0.5; } return b; },
  whoosh(f0, f1, dur, vel = 1, q = 1.2) { const b = buf(dur), bp = new Biquad('bp', f0, q); for (let i = 0; i < b.length; i++) { const t = i / SR, k = t / dur; if (i % 32 === 0) bp.set(f0 * Math.pow(f1 / f0, k), q); b[i] = bp.p(noise()) * Math.sin(Math.PI * k) ** 1.5 * vel * 1.4; } return b; },
  whooshBy(dur = 0.6, vel = 1) { const b = buf(dur), bp = new Biquad('bp', 400, 1.5); for (let i = 0; i < b.length; i++) { const t = i / SR, k = t / dur; if (i % 32 === 0) bp.set(400 + 2600 * Math.sin(Math.PI * Math.min(1, k * 1.1)), 1.5); b[i] = bp.p(noise()) * Math.pow(Math.sin(Math.PI * k), 2) * vel * 1.6; } return b; },
  thud(f = 70, vel = 1, len = 0.5) { const b = buf(len), lp = new Biquad('lp', 500); for (let i = 0; i < b.length; i++) { const t = i / SR; b[i] = (Math.sin(TAU * (f * 0.6 * t + f * 0.4 / 10 * (1 - Math.exp(-t * 10)))) * Math.exp(-t * 9) + lp.p(noise()) * 0.6 * Math.exp(-t * 22)) * vel; } return b; },
  clang(freqs, vel = 1, dec = 4) { const b = buf(1.6); for (let i = 0; i < b.length; i++) { const t = i / SR; let x = 0; freqs.forEach((f, k) => { x += Math.sin(TAU * f * t) * Math.exp(-t * dec * (1 + k * 0.5)) / (1 + k * 0.4); }); b[i] = (x * 0.4 + noise() * 0.5 * Math.exp(-t * 60)) * vel; } return b; },
  bell(f = 2350, len = 1.8, vel = 1) { const b = buf(len), hp = new Biquad('hp', 3000); for (let i = 0; i < b.length; i++) { const t = i / SR; b[i] = ((Math.sin(TAU * f * t) + Math.sin(TAU * (f + 7) * t)) * 0.5 * Math.exp(-t * 2.2) + 0.5 * Math.sin(TAU * f * 2.24 * t) * Math.exp(-t * 4) + 0.3 * Math.sin(TAU * f * 3.4 * t) * Math.exp(-t * 7) + hp.p(noise()) * 0.6 * Math.exp(-t * 150)) * vel * 0.45; } return b; },
  alarm(dur) { const b = buf(dur); const f = 1450; for (let i = 0; i < b.length; i++) { const t = i / SR; const strike = Math.exp(-((t * 19) % 1) * 3.5); const x = Math.sin(TAU * f * t) + 0.6 * Math.sin(TAU * f * 2.31 * t) + 0.35 * Math.sin(TAU * f * 3.62 * t); b[i] = x * (0.35 + 0.65 * strike) * 0.32 * Math.min(1, t * 20) * Math.min(1, (dur - t) * 4); } return b; },
  siren(dur, period = 1.5, vel = 1) { const b = buf(dur), lp = new Biquad('lp', 3500); let ph = 0; for (let i = 0; i < b.length; i++) { const t = i / SR; const f = 640 + 560 * (0.5 - 0.5 * Math.cos(TAU * t / period)); ph += f / SR; const x = Math.sin(TAU * ph) + 0.35 * Math.sin(TAU * 3 * ph) + 0.15 * Math.sin(TAU * 5 * ph); b[i] = lp.p(x) * 0.3 * vel * Math.min(1, t * 3) * Math.min(1, (dur - t) * 3); } return b; },
  skid(dur = 0.9, vel = 1) { const b = buf(dur), bp = new Biquad('bp', 2100, 3); let ph = 0, f = 2000; for (let i = 0; i < b.length; i++) { const t = i / SR; if (i % 220 === 0) f = 1850 + rnd() * 500; ph += f / SR; const e = Math.min(1, t * 30) * Math.min(1, (dur - t) * 5); b[i] = (Math.sin(TAU * ph) * 0.4 + Math.sin(TAU * ph * 1.5) * 0.15 + bp.p(noise()) * 0.8) * e * vel * 0.6; } return b; },
  engine(dur, f0, f1, vel = 1, rattle = 1) { const b = buf(dur), lp = new Biquad('lp', 700, 1.2), bp = new Biquad('bp', 2600, 2); const s = new Saw(); for (let i = 0; i < b.length; i++) { const t = i / SR, k = t / dur; const f = (f0 + (f1 - f0) * k * k) * (1 + 0.05 * Math.sin(TAU * 7 * t)); const fire = 0.6 + 0.4 * Math.sin(TAU * f * 0.5 * t); const rat = rnd() < 0.002 * rattle ? 1 : 0; b[i] = (lp.p(s.n(f)) * fire * 0.8 + bp.p(rat * 8 + noise() * 0.05) * 0.5 * rattle) * vel * Math.min(1, t * 10) * Math.min(1, (dur - t) * 20); } return b; },
  quack(f0 = 420, len = 0.16, vel = 1) { const b = buf(len + 0.02), s = new Saw(), f1 = new Biquad('bp', 1100, 3), f2 = new Biquad('bp', 2600, 4); for (let i = 0; i < b.length; i++) { const t = i / SR, k = t / len; const x = s.n(f0 * (1 - 0.25 * k)) + noise() * 0.2; b[i] = (f1.p(x) * 1.2 + f2.p(x) * 0.6) * Math.min(1, t * 200) * Math.max(0, 1 - k) ** 0.6 * vel; } return b; },
  cricket(dur) { const b = buf(dur); for (let i = 0; i < b.length; i++) { const t = i / SR, c = t % 0.62; const pulse = c < 0.16 ? (Math.floor(c / 0.04) % 2 === 0 ? 1 : 0) : 0; b[i] = Math.sin(TAU * 4400 * t) * pulse * 0.12 * Math.min(1, (dur - t) * 4); } return b; },
  click(f = 2000, vel = 1) { const b = buf(0.03), hp = new Biquad('hp', 1500); for (let i = 0; i < b.length; i++) { const t = i / SR; b[i] = (Math.sin(TAU * f * t) * Math.exp(-t * 250) + hp.p(noise()) * Math.exp(-t * 600)) * vel * 0.6; } return b; },
  wood(f = 1100, vel = 1) { const b = buf(0.08); for (let i = 0; i < b.length; i++) { const t = i / SR; b[i] = (Math.sin(TAU * f * t) + 0.5 * Math.sin(TAU * f * 1.58 * t)) * Math.exp(-t * 70) * vel * 0.5; } return b; },
  pop(f0 = 900, f1 = 200, vel = 1) { const b = buf(0.12); let ph = 0; for (let i = 0; i < b.length; i++) { const t = i / SR; ph += (f1 + (f0 - f1) * Math.exp(-t * 40)) / SR; b[i] = Math.sin(TAU * ph) * Math.exp(-t * 35) * vel * 0.7; } return b; },
  hiss(dur, vel = 1, f = 3000) { const b = buf(dur), hp = new Biquad('hp', f); for (let i = 0; i < b.length; i++) { const t = i / SR; b[i] = hp.p(noise()) * Math.exp(-t / dur * 3) * Math.min(1, t * 40) * vel * 0.4; } return b; },
  rumble(dur, vel = 1) { const b = buf(dur), lp = new Biquad('lp', 160); for (let i = 0; i < b.length; i++) { const t = i / SR; b[i] = lp.p(noise()) * 2.5 * (1 - t / dur) * vel; } return b; },
  squeak(f0 = 1300, f1 = 1600, dur = 0.14, vel = 1) { const b = buf(dur); let ph = 0; for (let i = 0; i < b.length; i++) { const t = i / SR, k = t / dur; ph += (f0 + (f1 - f0) * k + (rnd() - 0.5) * 120) / SR; b[i] = (Math.sin(TAU * ph) + 0.3 * Math.sin(TAU * 2 * ph)) * Math.sin(Math.PI * k) * vel * 0.35; } return b; },
  creak(dur = 0.5, vel = 1, f = 70) { const b = buf(dur), bp = new Biquad('bp', 500, 5); const s = new Saw(); let g = 0; for (let i = 0; i < b.length; i++) { const t = i / SR; if (i % 300 === 0) g = rnd(); const x = s.n(f * (1 + 0.3 * Math.sin(TAU * 3 * t)) + g * 30); if (i % 64 === 0) bp.set(400 + 300 * Math.sin(TAU * 2 * t), 5); b[i] = bp.p(x) * Math.sin(Math.PI * t / dur) * vel * 1.2; } return b; },
  wind(dur, vel = 1) { const b = buf(dur), lp = new Biquad('bp', 600, 0.8); for (let i = 0; i < b.length; i++) { const t = i / SR; if (i % 64 === 0) lp.set(500 + 400 * Math.sin(TAU * 0.7 * t), 0.8); b[i] = lp.p(noise()) * (0.6 + 0.4 * Math.sin(TAU * 1.3 * t)) * Math.min(1, t * 2) * Math.min(1, (dur - t) * 2) * vel; } return b; },
  flutter(dur, vel = 1) { const b = buf(dur), bp = new Biquad('bp', 2800, 1.5); for (let i = 0; i < b.length; i++) { const t = i / SR; const am = Math.max(0, Math.sin(TAU * 19 * t + Math.sin(TAU * 1.3 * t) * 3)); b[i] = bp.p(noise()) * am * vel * 0.7 * Math.min(1, t * 3) * Math.min(1, (dur - t) * 3); } return b; },
  scratch(vel = 1) { const b = buf(0.4), bp = new Biquad('bp', 800, 2); const s = new Saw(); for (let i = 0; i < b.length; i++) { const t = i / SR, k = t / 0.4; const f = k < 0.4 ? 300 + 2600 * (k / 0.4) : 2900 - 2700 * ((k - 0.4) / 0.6); if (i % 32 === 0) bp.set(f, 2); b[i] = (bp.p(noise()) * 1.2 + s.n(f * 0.25) * 0.15) * vel * (1 - k * 0.6); } return b; },
  // formant voice: grunts, yawns, "hnnngh"
  voiceSynth(dur, f0fn, formants, ampfn, vel = 1) {
    const b = buf(dur), s = new Saw(), fs = formants.map(([f, q]) => new Biquad('bp', f, q));
    for (let i = 0; i < b.length; i++) {
      const t = i / SR, k = t / dur; const x = s.n(f0fn(k) * (1 + 0.02 * noise())) + noise() * 0.15;
      if (i % 64 === 0) formants.forEach(([f, q, f2], j) => fs[j].set(f2 ? f + (f2 - f) * k : f, q));
      let y = 0; fs.forEach((flt, j) => { y += flt.p(x) * (formants[j][3] ?? 1); });
      b[i] = y * ampfn(k) * vel;
    }
    return b;
  },
};
const grunt = (f0, vel = 1) => SFX.voiceSynth(0.42, k => f0 * (1.05 - 0.15 * k), [[300, 4, 650], [2100, 6, 1100], [2900, 8, 2500, 0.4]], k => Math.min(1, k * 12) * (k < 0.55 ? 0.45 : 1) * Math.min(1, (1 - k) * 6), vel * 1.4);
// a cartoon snore: a rumbling in-breath, then a whistling out-breath
function snore(vel = 1) {
  const b = buf(1.7), lp = new Biquad('lp', 500, 1.2); let ph = 0, ph2 = 0;
  for (let i = 0; i < b.length; i++) { const t = i / SR;
    if (t < 0.95) { const k = t / 0.95, env = Math.sin(Math.PI * k) ** 0.7; ph += TAU * (70 + 18 * k) / SR; b[i] = (lp.p(noise()) * 0.8 + Math.sign(Math.sin(ph)) * 0.12) * env * (0.7 + 0.3 * Math.sin(TAU * 26 * t)) * vel; }
    else { const k = (t - 0.95) / 0.75, env = Math.sin(Math.PI * Math.min(1, k)) * 0.7; ph2 += TAU * (1050 - 380 * k) / SR; b[i] = (Math.sin(ph2) * 0.35 + noise() * 0.06) * env * vel; } }
  return b;
}
// a room of people talking quietly (band-passed babble with syllable-rate wobble)
function murmur(dur) {
  const b = buf(dur), bp = new Biquad('bp', 700, 0.8), bp2 = new Biquad('bp', 1500, 1.2);
  const r = [3.1, 4.7, 5.9, 2.3].map(f => [f, rnd() * TAU]);
  for (let i = 0; i < b.length; i++) { const t = i / SR, am = r.reduce((a, [f, p]) => a + Math.max(0, Math.sin(TAU * f * t + p)), 0) / 2.2, env = Math.min(1, t / 0.4, (dur - t) / 0.5); b[i] = (bp.p(noise()) * 1.4 + bp2.p(noise()) * 0.5) * am * env; }
  return b;
}
const yawn = () => SFX.voiceSynth(1.15, k => 210 - 100 * k, [[750, 5, 450], [1200, 6, 800], [2600, 8, 2400, 0.3]], k => Math.sin(Math.PI * Math.min(1, k * 1.05)) * (k > 0.8 ? 0.5 : 1), 1.6);
const sadTrombone = () => { const out = buf(1.9); [[63, 0, 0.32], [62, 0.34, 0.32], [61, 0.68, 0.32], [60, 1.02, 0.8]].forEach(([m, at, d], i) => { const n = trombone(m, i === 3 ? m - 0.6 : m, d, { vel: 0.8, wah: i === 3 ? 6 : 3.2 }); const o = Math.round(at * SR); for (let j = 0; j < n.length && o + j < out.length; j++) out[o + j] += n[j]; }); return out; };

// ---------------------------------------------------------------- voices (see vox.mjs)
import { VCFG, LINES, samples } from './vox.mjs';
const SPOKEN = []; // for subtitles

// ---------------------------------------------------------------- SFX cue dispatch
function playCue(c) {
  const t = c.t, S = SFX;
  const m = (b, g = 1, pan = 0) => mix('sfx', t, b, g, pan);
  switch (c.name) {
    case 'title_whoosh': m(S.whoosh(300, 3000, 0.4), 0.5); break;
    case 'boing': m(S.boing(c.pitch || 1), 0.8); break;
    case 'zip_down': m(S.slide(2200, 500, 0.25), 0.5); break;
    case 'zip_up': m(S.slide(500, 2400, 0.16), 0.55); break;
    case 'slide_up': m(S.slide(500, 1800, 0.55), 0.55); break;
    case 'slide_up_fast': m(S.slide(700, 2600, 0.2), 0.45, -0.4); break;
    case 'slide_down_short': m(S.slide(1800, 450, 0.4), 0.55); break;
    case 'alarm': m(S.alarm(c.dur), 0.38, 0.3); break;
    case 'door_bam': m(S.thud(90, 1, 0.6), 1.0); m(S.clang([210, 330, 520], 0.4, 6), 0.6); break;
    case 'scramble': for (let k = 0; k < c.dur * 13; k++) mix('sfx', t + k / 13 + rnd() * 0.02, S.wood(k % 2 ? 900 : 1150, 0.7), 0.6, (k % 2) * 0.4 - 0.2); break;
    case 'car_bounce': m(S.boing(0.55, 0.8), 0.7); m(S.thud(60, 0.7, 0.3), 0.6); break;
    case 'stretch': m(S.squeak(400, 900, 0.32, 1), 0.8); break;
    case 'squish': { const b = buf(0.3), lp = new Biquad('lp', 2000); for (let i = 0; i < b.length; i++) { const tt = i / SR; if (i % 32 === 0) lp.set(2200 - 1900 * tt / 0.3); b[i] = lp.p(noise()) * Math.exp(-tt * 8) * 1.4 + Math.sin(TAU * (300 - 600 * tt) * tt) * 0.4 * Math.exp(-tt * 10); } m(b, 0.8); break; }
    case 'squeak_rubber': m(S.squeak(1000 * (c.pitch || 1), 1300 * (c.pitch || 1), 0.35, 1), 0.7); break;
    case 'thud': m(S.thud(55, 1.2, 0.7), 1.0); break;
    case 'car_groan': m(S.creak(0.7, 0.8, 60), 0.6); break;
    case 'zip_rope': m(S.whoosh(800, 4000, 0.1, 1, 2), 0.6); mix('sfx', t + 0.16, S.whoosh(800, 4000, 0.1, 1, 2), 0.6); break;
    case 'gulp': m(S.pop(700, 160, 1), 0.9); mix('sfx', t + 0.09, S.pop(260, 120, 0.7), 0.7); break;
    case 'heartbeat': for (let k = 0; k < (c.n || 2); k++) { mix('sfx', t + k * 0.75, S.thud(48, 0.9, 0.3), 0.9); mix('sfx', t + k * 0.75 + 0.2, S.thud(44, 0.6, 0.3), 0.9); } break;
    case 'stomp': m(S.thud(45, 1.4, 0.6), 1.1); m(S.clang([620, 980], 0.3, 12), 0.5); break;
    case 'engine_rev': m(S.engine(c.dur, 40, 135, 1, 1.5), 0.75); break;
    case 'drumroll': for (let k = 0; k < c.dur * 26; k++) { const v = 0.15 + 0.85 * (k / (c.dur * 26)) ** 2; mix('sfx', t + k / 26, snare(v * 0.5, 210), 0.5, 0.2); } break;
    case 'whoosh_rev': m(S.whoosh(3000, 400, 0.15, 1.2), 0.7); break;
    case 'crash': m(crash(1.2, 2.2), 0.9); m(S.thud(50, 1.5, 0.9), 1.0); m(S.clang([520, 1180, 1870, 2650, 3400], 1, 3), 0.8); break;
    case 'trash_clatter': for (let k = 0; k < 7; k++) mix('sfx', t + 0.1 + k * 0.17 + rnd() * 0.08, S.clang([900 + rnd() * 1500, 2300 + rnd() * 1500], 0.5 * (1 - k / 8), 14), 0.6, rnd() * 1.4 - 0.7); break;
    case 'cricket': m(S.cricket(c.dur), 0.8, 0.5); break;
    case 'lid_wobble': { const b = buf(1.9); for (let i = 0; i < b.length; i++) { const tt = i / SR, k = tt / 1.9; const rate = 6 + 34 * k * k; const am = 0.5 + 0.5 * Math.sin(TAU * (6 * tt + 34 * tt * k * k / 3)); b[i] = (Math.sin(TAU * 520 * tt) + 0.5 * Math.sin(TAU * 1310 * tt)) * am * (1 - k) * 0.25 * (rate > 0 ? 1 : 0); } m(b, 0.7, -0.4); break; }
    case 'blink': m(S.click(3200, 0.5), 0.6); break;
    case 'clunk': m(S.clang([180, 260, 410], 1, 10), 0.8); m(S.thud(80, 0.6, 0.2), 0.6); break;
    case 'zoom_off': m(S.engine(0.5, 70, 210, 1, 0.3), 0.7); m(S.whooshBy(0.6), 0.7); break;
    case 'skid_short': m(S.skid(0.35), 0.5); break;
    case 'skid': m(S.skid(1.0), 0.65); break;
    case 'siren': m(S.siren(c.dur, 1.5), 0.24, -0.2); break;
    case 'siren_slow': m(S.siren(c.dur, 2.4, 0.8), 0.32, -0.6); break;
    case 'whoosh_by': m(S.whooshBy(0.7), 0.8); break;
    case 'look_whip': m(S.whoosh(600, 2500, 0.15), 0.5); break;
    case 'honk': case 'meep': { const mk2 = d => { const b = buf(d), lp = new Biquad('lp', 2200); const a = new Saw(), bb = new Saw(); for (let i = 0; i < b.length; i++) { const tt = i / SR; b[i] = lp.p(Math.sign(a.n(470)) * 0.5 + Math.sign(bb.n(590)) * 0.5) * Math.min(1, tt * 200) * Math.min(1, (d - tt) * 60) * 0.25; } return b; }; m(mk2(0.16), 0.8); if (c.name === 'honk') mix('sfx', t + 0.22, mk2(0.2), 0.8); break; }
    case 'quack': for (let k = 0; k < c.n; k++) mix('sfx', t + k * c.gap + rnd() * 0.04, k === 0 ? SFX.quack(400, 0.18) : SFX.quack(880 + rnd() * 120, 0.09), k === 0 ? 0.7 : 0.45, -0.3 + k * 0.12); break;
    case 'quack_small': m(SFX.quack(950, 0.11), 0.6, 0.2); break;
    case 'drum_fingers': for (let k = 0; k < c.dur * 11; k++) mix('sfx', t + k / 11, S.wood(k % 3 === 0 ? 700 : 820, 0.5), 0.5); break;
    case 'facepalm_slap': m(S.thud(150, 0.6, 0.15), 0.7); m(S.hiss(0.06, 2, 900), 0.8); break;
    case 'rev_short': m(S.engine(0.6, 60, 160, 1, 0.5), 0.6); break;
    case 'blinker': for (let k = 0; k < c.dur * 3; k++) mix('sfx', t + k / 3, S.click(k % 2 ? 1500 : 2300, 1), 0.7); break;
    case 'flutter': m(S.flutter(c.dur), 0.35, -0.3); break;
    case 'snatch': m(S.pop(1400, 500, 0.8), 0.6, -0.3); m(S.whoosh(1000, 3500, 0.08, 1, 2), 0.4, -0.3); break;
    case 'register_ding': m(S.bell(2093, 1.0, 0.8), 0.5, 0.4); break;
    case 'munch': for (let k = 0; k < c.n; k++) mix('sfx', t + k * 0.2, S.hiss(0.08, 1.4, 1800), 0.6); break;
    case 'gull': for (let k = 0; k < c.n; k++) mix('sfx', t + 0.6 + k * 0.9, SFX.voiceSynth(0.42, q => 1700 - 600 * q, [[2400, 3], [3600, 5, 3200, 0.5]], q => Math.sin(Math.PI * q), 0.5), 0.35, 0.5); break;
    case 'putt': m(S.thud(65, 1, 0.4), 0.9); m(S.hiss(0.2, 1.2, 600), 0.6); m(S.pop(300, 80, 0.8), 0.7); break;
    case 'needle_drop': m(S.slide(900, 160, 0.3), 0.6); break;
    case 'roll_stop': m(S.rumble(1.0, 0.8), 0.7); mix('sfx', t + 0.7, S.squeak(900, 700, 0.18), 0.5); break;
    case 'steam_hiss': m(S.hiss(1.4, 1, 2500), 0.6, 0.3); break;
    case 'bike_squeak': for (let k = 0; k < c.n; k++) mix('sfx', t + k * c.gap, S.squeak(1250, 1500, 0.12, 0.8), 0.45, -0.3); break;
    case 'grunt': m(grunt((c.f0 || 150) + (c.i || 0) * 6, c.vel || 1), c.gain ?? 0.8, c.pan || 0); break; // f0 ~150 man, ~225 woman, ~320 kid
    case 'grunt_benny': m(grunt(150 + (c.i || 0) * 6), 0.85, -0.2); break;
    case 'grunt_marge': m(grunt(225 + (c.i || 0) * 8, 0.8), 0.55, 0.25); break;
    case 'creak': m(S.creak(0.4, 0.7, 75 + (c.i || 0) * 4), 0.45); break;
    case 'flop': m(S.thud(70, 0.8, 0.3), 0.8); mix('sfx', t + 0.05, SFX.pop(500, 150, 0.6), 0.6); break;
    case 'creak_long': m(S.creak(1.2, 0.9, 55), 0.6); break;
    case 'wind': m(S.wind(c.dur), 0.6); break;
    case 'land_thud': m(S.thud(55, 1.4, 0.7), 1.0); m(S.clang([320, 760], 0.4, 8), 0.4); break;
    case 'pan_up_whoosh': m(S.whoosh(300, 1500, 1.0, 0.8), 0.4); break;
    case 'record_scratch': m(S.scratch(1), 0.8); break;
    case 'brake_squeak': m(S.squeak(2800, 2600, 0.45, 1), 0.5); break;
    case 'bell': m(S.bell(2350, 2.6, 1.2), 1.0, -0.2); break;
    case 'sad_trombone': case 'iris_close': mix('music', t, sadTrombone(), 0.75); break;
    case 'iris_snap': m(S.pop(1200, 300, 0.7), 0.6); break;
    case 'yawn': case 'v_cop_yawn': mix('vox', t, yawn(), 0.6, c.pan ?? -0.1); break;
    case 'pour': m(S.hiss(c.dur || 1.5, 0.8, 1300), 0.28, 0.1); for (let k = 0; k < (c.dur || 1.5) * 7; k++) mix('sfx', t + k / 7 + rnd() * 0.05, S.pop(500 + rnd() * 400, 300, 0.4), 0.18, 0.1); break;
    case 'growl': m(S.rumble(c.dur || 0.8, 1.0), 0.9); mix('sfx', t + 0.3, S.squeak(260, 180, 0.35, 0.5), 0.3); break;
    case 'tiptoe': for (let k = 0; k < (c.n || 4); k++) mix('sfx', t + k * (c.gap || 0.3), S.wood(k % 2 ? 2100 : 2500, 0.6), 0.25, (k % 2) * 0.2 - 0.1); break;
    case 'snore': mix('vox', t, snore(c.vel ?? 1), 0.55, c.pan ?? 0); break;
    case 'murmur': m(murmur(c.dur || 2), c.gain ?? 0.5, 0); break;
    // ---- office / tech / city
    case 'typing': for (let k = 0; k < (c.dur || 1) * (c.rate || 14); k++) { const tt = t + k / (c.rate || 14) + rnd() * 0.03; mix('sfx', tt, S.click(1600 + rnd() * 1800, 0.8), 0.3 * (c.gain ?? 1), c.pan ?? 0.1); if (rnd() < 0.08) mix('sfx', tt, S.wood(520, 0.6), 0.25, 0.1); } break;
    case 'ping': for (let k = 0; k < (c.n || 1); k++) mix('sfx', t + k * (c.gap || 0.18), S.bell(k % 2 ? 1760 : 2093, 0.5, 0.6), 0.35 * (c.gain ?? 1), (rnd() - 0.5) * 0.8); break;
    case 'error_buzz': for (let k = 0; k < 2; k++) { const b = buf(0.28), a = new Saw(), lp = new Biquad('lp', 1800); for (let i = 0; i < b.length; i++) { const tt = i / SR; b[i] = lp.p(Math.sign(a.n(118))) * 0.35 * Math.min(1, tt * 100) * Math.min(1, (0.28 - tt) * 40); } mix('sfx', t + k * 0.36, b, 0.7); } break;
    case 'alarm_beep': for (let k = 0; k < (c.n || 4); k++) { const b = buf(0.12); for (let i = 0; i < b.length; i++) b[i] = Math.sign(Math.sin(TAU * 1040 * i / SR)) * 0.2 * Math.min(1, (0.12 - i / SR) * 50); mix('sfx', t + k * 0.24, b, 0.45, 0.2); } break;
    case 'party_pop': m(S.pop(1800, 400, 1), 0.7); m(S.hiss(0.7, 1.6, 4000), 0.5); for (let k = 0; k < 10; k++) mix('sfx', t + 0.05 + rnd() * 0.6, S.click(3000 + rnd() * 3000, 0.5), 0.25, rnd() * 1.6 - 0.8); break;
    case 'party_horn': { const b = buf(0.6), a = new Saw(), bp = new Biquad('bp', 1200, 2); for (let i = 0; i < b.length; i++) { const tt = i / SR; b[i] = bp.p(a.n(470 + 30 * Math.sin(TAU * 7 * tt))) * Math.min(1, tt * 30) * Math.min(1, (0.6 - tt) * 8) * 1.2; } m(b, 0.5, -0.3); break; }
    case 'chime_success': [84, 88, 91, 96].forEach((n, k) => mix('sfx', t + k * 0.11, S.bell(midi(n), 1.4, 0.7), 0.45, -0.2 + k * 0.15)); break;
    case 'highfive': m(S.hiss(0.05, 3, 1200), 0.9); m(S.thud(160, 0.7, 0.12), 0.6); [96, 100, 103].forEach((n, k) => mix('sfx', t + 0.05 + k * 0.05, xylo(n, 0.5), 0.35)); break;
    case 'notify': [88, 95].forEach((n, k) => mix('sfx', t + k * 0.12, S.bell(midi(n), 0.6, 0.7), 0.4 * (c.gain ?? 1), 0.2)); break;
    case 'buzz': for (let k = 0; k < (c.n || 2); k++) { const d = 0.45, b = buf(d), lp = new Biquad('lp', 400); for (let i = 0; i < b.length; i++) { const tt = i / SR; b[i] = lp.p(Math.sign(Math.sin(TAU * 160 * tt)) * (0.6 + 0.4 * Math.sin(TAU * 25 * tt))) * Math.min(1, tt * 60) * Math.min(1, (d - tt) * 30) * 0.8; } mix('sfx', t + k * (c.gap || 0.75), b, 0.6 * (c.gain ?? 1), 0.1); } break;
    case 'ring': for (let k = 0; k < (c.n || 2); k++) for (let j = 0; j < 8; j++) mix('sfx', t + k * 1.1 + j * 0.06, S.bell(j % 2 ? 1320 : 1568, 0.25, 0.5), 0.3 * (c.gain ?? 1), 0.25); break;
    case 'stamp': m(S.thud(90, 1.2, 0.35), 1.0); m(S.hiss(0.08, 2, 1500), 0.7); m(S.wood(300, 1), 0.6); break;
    case 'crack': m(S.clang([2100, 3400, 5200], 0.6, 25), 0.6); for (let k = 0; k < 6; k++) mix('sfx', t + 0.05 + k * 0.05 + rnd() * 0.03, S.click(2500 + rnd() * 3000, 1), 0.6, rnd() - 0.5); mix('sfx', t + 0.25, S.slide(1400, 300, 0.5), 0.4); break;
    case 'tick': for (let k = 0; k < (c.n || 4); k++) mix('sfx', t + k * (c.gap || 0.5), S.wood(k % 2 ? 1500 : 1900, 1), 0.55, 0.2); break;
    case 'correct': [84, 88, 91, 96].forEach((n, k) => mix('sfx', t + k * 0.09, xylo(n, 0.9), 0.55, -0.2 + k * 0.13)); mix('sfx', t + 0.36, S.bell(midi(96), 1.2, 0.8), 0.4); break;
    case 'denied': { const b = buf(0.5), a = new Saw(), lp = new Biquad('lp', 1400); for (let i = 0; i < b.length; i++) { const tt = i / SR; b[i] = lp.p(Math.sign(a.n(140)) + Math.sign(Math.sin(TAU * 147 * tt))) * 0.25 * Math.min(1, tt * 100) * Math.min(1, (0.5 - tt) * 30); } m(b, 0.7); break; }
    case 'bonk': m(S.clang([600, 950, 1500], 0.8, 14), 0.7); m(S.boing(0.8, 0.8), 0.6); break;
    case 'flashback': for (let k = 0; k < 12; k++) mix('music', t + k * 0.06, xylo(72 + [0, 2, 4, 7, 9, 12, 14, 16, 19, 21, 24, 26][c.down ? 11 - k : k], 0.5), 0.35, (k / 11) - 0.5); m(S.whoosh(400, 2600, 0.8, 0.6), 0.3); break;
    case 'heh': for (let k = 0; k < (c.n || 3); k++) mix('vox', t + k * 0.22, SFX.voiceSynth(0.16, q => 130 - 20 * q, [[600, 5], [1100, 6], [2500, 8, 2400, 0.4]], q => Math.sin(Math.PI * q), 0.9), 0.55, c.pan ?? 0.3); break;
    case 'slam': m(S.thud(70, 1.3, 0.5), 1.0); m(S.clang([180, 290], 0.5, 9), 0.5); m(S.hiss(0.15, 1, 1200), 0.4); break;
    case 'zap': m(S.slide(3000, 200, 0.3), 0.4); m(S.hiss(0.3, 1.5, 2500), 0.5); break;
    case 'scribble': for (let k = 0; k < (c.dur || 1) * 7; k++) mix('sfx', t + k / 7 + rnd() * 0.03, S.squeak(2600 + rnd() * 600, 3000 + rnd() * 500, 0.1, 0.5), 0.2, -0.2); break;
    case 'knock': for (let k = 0; k < (c.n || 3); k++) { mix('sfx', t + k * 0.22, S.wood(260, 1.2), 0.9, 0.1); mix('sfx', t + k * 0.22, S.thud(120, 0.6, 0.1), 0.6); } break;
    case 'applause': for (let k = 0; k < (c.dur || 2) * 26; k++) { const tt = t + rnd() * (c.dur || 2), f = 1 - (tt - t) / (c.dur || 2) * 0.6; mix('sfx', tt, S.hiss(0.05, 1.6 * f, 1200 + rnd() * 1500), 0.5 * (c.gain ?? 1), rnd() * 1.4 - 0.7); } break;
    case 'rain': { const d = c.dur || 3; for (let k = 0; k < d * 18; k++) mix('sfx', t + rnd() * d, S.click(3000 + rnd() * 3000, 0.4), 0.2 * (c.gain ?? 1), rnd() * 0.6 - 0.3); break; }
    case 'birds': for (let k = 0; k < (c.n || 4); k++) { const tt = t + k * 0.7 + rnd() * 0.3; for (let j = 0; j < 3; j++) mix('sfx', tt + j * 0.08, xylo(96 + (j % 2) * 3 + Math.floor(rnd() * 3), 0.4), 0.18, 0.4); } break;
    case 'tuktuk': m(S.engine(c.dur || 2, 70, 90, 0.8, 1.2), (c.gain ?? 0.45), c.pan || 0); break;
    case 'shutter': m(S.click(4200, 1.2), 0.9); mix('sfx', t + 0.05, S.hiss(0.12, 1.4, 2500), 0.6); mix('sfx', t + 0.09, S.click(2600, 1), 0.7); break;
    case 'swivel': m(S.whoosh(500, 2200, 0.45, 0.9), 0.5); m(S.squeak(700, 900, 0.3, 0.6), 0.25); break;
    case 'marker': for (let k = 0; k < (c.dur || 1) * 4; k++) mix('sfx', t + k * 0.25 + rnd() * 0.05, S.squeak(2100 + rnd() * 500, 2500 + rnd() * 400, 0.16, 0.5), 0.18, -0.2); break;
    case 'footsteps': for (let k = 0; k < (c.n || 4); k++) { mix('sfx', t + k * (c.gap || 0.45), S.thud(140, 0.4, 0.12), 0.45, (k % 2) * 0.3 - 0.15); mix('sfx', t + k * (c.gap || 0.45), S.wood(380, 0.4), 0.2); } break;
    case 'sip': { const b = buf(0.45), bp = new Biquad('bp', 1100, 4); for (let i = 0; i < b.length; i++) { const tt = i / SR; if (i % 64 === 0) bp.set(900 + 900 * tt / 0.45, 4); b[i] = bp.p(noise()) * Math.sin(Math.PI * tt / 0.45) * (0.6 + 0.4 * Math.sin(TAU * 30 * tt)) * 1.5; } m(b, 0.4); break; }
    case 'page_flip': m(S.whoosh(1500, 5000, 0.18, 1, 0.8), 0.5); m(S.hiss(0.12, 1, 3000), 0.3); break;
    case 'whoosh': m(S.whoosh(c.f0 || 400, c.f1 || 2500, c.dur || 0.35), c.gain ?? 0.5, c.pan || 0); break;
    case 'sparkle': [91, 95, 98, 103].forEach((n, k) => mix('sfx', t + k * 0.06, xylo(n, 0.5), 0.3, 0.3)); break;
    case 'motorbike': m(S.engine(c.dur || 2, 95, 120, 0.8, 0.4), (c.gain ?? 0.4), c.pan || 0); break;
    case 'city_amb': { const d = c.dur || 5, b = buf(d), lp = new Biquad('lp', 300); for (let i = 0; i < b.length; i++) { const tt = i / SR; b[i] = lp.p(noise()) * 1.4 * Math.min(1, tt) * Math.min(1, d - tt); } m(b, 0.35); for (let k = 0; k < d / 2.2; k++) mix('sfx', t + 0.8 + k * 2.2 + rnd(), S.engine(0.9, 80 + rnd() * 30, 100, 0.4, 0.2), 0.12, rnd() * 1.6 - 0.8); break; }
    case 'room_tone': { const d = c.dur || 5, b = buf(d), lp = new Biquad('lp', 500); for (let i = 0; i < b.length; i++) { const tt = i / SR; b[i] = (lp.p(noise()) * 0.6 + Math.sin(TAU * 120 * tt) * 0.02) * Math.min(1, tt * 2) * Math.min(1, (d - tt) * 2); } m(b, 0.25); break; }
    case 'night_amb': m(S.cricket(c.dur || 6), 0.45, 0.4); mix('sfx', t + 0.3, S.cricket((c.dur || 6) - 0.3), 0.3, -0.4); { const d = c.dur || 6, b = buf(d), lp = new Biquad('lp', 220); for (let i = 0; i < b.length; i++) { const tt = i / SR; b[i] = lp.p(noise()) * 1.2 * Math.min(1, tt) * Math.min(1, d - tt); } m(b, 0.25); } break;
    case 'clock_fast': for (let tt = 0, k = 0; tt < (c.dur || 2); k++) { mix('sfx', t + tt, S.click(k % 2 ? 1800 : 2600, 0.8), 0.35); tt += Math.max(0.05, 0.3 - tt * 0.12); } break;
    case 'server_hum': { const d = c.dur || 3, b = buf(d), hp = new Biquad('bp', 900, 1); for (let i = 0; i < b.length; i++) { const tt = i / SR; b[i] = (Math.sin(TAU * 60 * tt) * 0.2 + Math.sin(TAU * 120 * tt) * 0.1 + hp.p(noise()) * 0.25) * Math.min(1, tt * 3) * Math.min(1, (d - tt) * 3); } m(b, 0.35); break; }
    case 'nod': m(S.wood(700, 0.4), 0.15); break;
    case 'click': m(S.click(2600, 1), 0.8); mix('sfx', t + 0.07, S.click(1700, 0.7), 0.6); break;
    case 'pop': m(S.pop(c.f0 || 1100, c.f1 || 300, 1), c.gain ?? 0.7); break;
    case 'sting_title': mix('music', t, brass([50, 57, 62, 65, 69].map(n => n + (c.key || 0)), 0.5, { vel: 1 }), 0.6); mix('music', t, crash(0.8, 1.8), 0.4); mix('music', t, kick(1), 0.5); break;
    case 'ta_da': mix('music', t, brass([50, 57, 62, 66, 69, 74].map(n => n + (c.key || 0)), 1.1, { vel: 1 }), 0.7); mix('music', t, crash(1, 2.4), 0.5); mix('music', t, kick(1), 0.6); mix('music', t, bassNote(midi(38 + (c.key || 0)), 1.0), 0.9); break;
    case 'heave_hit': { const i = c.i || 0, lead = c.lead ?? 0.4; mix('music', t - lead, bassNote(midi(26 + i), 0.3, 1), 0.9); mix('music', t - lead, tom(80, 0.8), 0.5); mix('music', t, brass([50 + i, 57 + i, 62 + i], 0.35, { vel: 0.9, bright: 0.8 }), 0.55); mix('music', t, snare(0.8), 0.4); break; }
    case 'sting_det': mix('music', t, brass([50, 57, 62, 65, 68], 0.5, { vel: 0.9 }), 0.55); mix('music', t, tom(90, 1), 0.6); break;
    case 'sting_shock': mix('music', t, brass([62, 65, 68, 71], 0.6, { vel: 1, fall: 5 }), 0.55); mix('music', t, crash(0.7, 1.4), 0.5); break;
    case 'sting_tiny': [84, 88, 91].forEach((n, k) => mix('music', t + k * 0.09, xylo(n, 0.7), 0.5)); break;
    case 'sting_idea': [79, 83, 86, 91].forEach((n, k) => mix('music', t + k * 0.06, xylo(n, 0.8), 0.55)); break;
    case 'sting_panic': for (let k = 0; k < 8; k++) mix('music', t + k * 0.05, xylo(k % 2 ? 85 : 86, 0.6), 0.4); mix('music', t, brass([61, 62, 67, 68], 0.4, { vel: 0.7 }), 0.4); break;
    case 'ta_da_small': [74, 78, 81].forEach((n, k) => mix('music', t + k * 0.07, xylo(n + 12, 0.7), 0.5)); break;
    case 'end_button': mix('music', t, brass([50, 57, 62, 65, 69], 0.18, { vel: 1 }), 0.6); mix('music', t, kick(1), 0.5); mix('music', t + 0.36, brass([50, 57, 62, 65, 69], 0.5, { vel: 1 }), 0.65); mix('music', t + 0.36, kick(1), 0.5); mix('music', t + 0.36, crash(0.7, 1.5), 0.35); mix('music', t + 0.36, bassNote(midi(38), 0.5), 0.8); break;
    default:
      if (LINES[c.name]) {
        const [who, text, tr] = LINES[c.name], V = VCFG.voices[who] || {}, clip = fadeEdges(samples(c.name));
        mix('vox', t, clip, V.gain ?? 0.95, V.pan ?? 0);
        if (c.sub !== false) SPOKEN.push({ t, dur: clip.length / SR, who, text, tr }); // sub: false = a chorus voice (no extra subtitle)
      } else UNKNOWN.add(c.name);
  }
}

// ---------------------------------------------------------------- the score
// Music sections are cue pairs placed in shots:  [lt, 'music', {id, style, ...opts}]  ...  [lt, 'music_end', {id, how}]
// styles: chase (walking bass + swing drums + brass stabs; melody: true | 'shout'), sneak (heist pizzicato), tech (pluck arpeggio + pulse bass; dark, drums),
// love (harp glissando + dreamy waltz sting), game (chiptune), leak (upbeat squeezed through headphones),
//         muzak (quiet bossa e-piano), tension (accelerating low pulses + tremolo), vamp (happy major vamp)
// end how: 'cut' (default, 40 ms), 'fade' {dur}, 'tapestop' {dur} (record slows to a halt)
// common opts: gain, key (semitones from D minor), bpm, vel
const CH = { Dm7: { r: 38, v: [57, 60, 62, 65], t: [0, 3, 7, 10] }, Gm7: { r: 43, v: [58, 62, 65, 67], t: [0, 3, 7, 10] }, Bb7: { r: 34, v: [58, 62, 65, 68], t: [0, 4, 7, 10] }, A7: { r: 33, v: [57, 61, 64, 67], t: [0, 4, 7, 10] }, D: { r: 38, v: [57, 62, 66, 69], t: [0, 4, 7, 9] } };
const PROG = ['Dm7', 'Dm7', 'Gm7', 'Gm7', 'Dm7', 'Bb7', 'A7', 'Dm7'];
const THEME = [[0, 69, .5], [.5, 74, .5], [1, 72, .5], [1.5, 69, .5], [2, 65, .5], [2.5, 67, .5], [3, 68, .5], [3.5, 69, .5], [4, 74, 1.5], [5.5, 72, .5], [6, 69, 1], [7, 65, .5],
  [8, 70, .5], [8.5, 74, .5], [9, 77, .5], [9.5, 74, .5], [10, 70, .5], [10.5, 67, .5], [11, 69, .5], [11.5, 70, .5], [12, 72, 1.5], [13.5, 70, .5], [14, 67, 1.5],
  [16, 74, .5], [16.5, 77, .5], [17, 76, .5], [17.5, 74, .5], [18, 72, .5], [18.5, 69, .5], [19, 72, .5], [19.5, 74, .5], [20, 77, 1], [21, 74, .5], [21.5, 70, 1.5],
  [24, 73, .5], [24.5, 76, .5], [25, 79, .5], [25.5, 76, .5], [26, 73, .5], [26.5, 69, .5], [27, 67, .5], [27.5, 64, .5], [28, 62, 1], [29.5, 69, .5], [30, 74, .5], [30.5, 73, .5], [31, 72, .5]];
const swing = b => Math.floor(b) + ((b % 1) >= 0.49 ? 0.667 : 0);

// a section renders into its own buffer so it can be cut / faded / tape-stopped as a whole
function section(len) {
  const sec = { L: new Float32Array(Math.ceil((len + 1.5) * SR)), R: new Float32Array(Math.ceil((len + 1.5) * SR)), len };
  sec.put = (tt, b, g = 1, pan = 0) => { if (tt >= len || tt < 0) return; const i0 = Math.round(tt * SR); const gl = g * Math.cos((pan + 1) * Math.PI / 4) * Math.SQRT2, gr = g * Math.sin((pan + 1) * Math.PI / 4) * Math.SQRT2; for (let i = 0; i < b.length && i0 + i < sec.L.length; i++) { sec.L[i0 + i] += b[i] * gl; sec.R[i0 + i] += b[i] * gr; } };
  return sec;
}
const STYLES = {
  chase(len, { bpm = 176, melody = false, stabs = true, vel = 1, key = 0, bars0 = 0 } = {}) {
    const beat = 60 / bpm, sec = section(len), put = sec.put, nBars = Math.ceil(len / (beat * 4)) + 1;
    for (let bar = 0; bar < nBars; bar++) {
      const ch = CH[PROG[(bar + bars0) % 8]], nx = CH[PROG[(bar + bars0 + 1) % 8]], tb = bar * 4 * beat;
      const tones = [ch.r, ch.r + ch.t[1], ch.r + ch.t[2], nx.r + (rnd() < 0.5 ? 1 : -1)];
      tones.forEach((n, k) => put(tb + k * beat, bassNote(midi(n + key), beat * 0.9, k === 0 ? 1 : 0.8), 0.95, -0.1));
      [0, 1, 1.667, 2, 3, 3.667].forEach(b => put(tb + b * beat, ride(b % 1 ? 0.5 : 0.75), 0.32, 0.35));
      [1, 3].forEach(b => { put(tb + b * beat, hat(0.6, 0.04), 0.25, 0.3); put(tb + b * beat, snare(0.75), 0.45, 0.05); });
      [0, 2].forEach(b => put(tb + b * beat, kick(0.7), 0.6));
      for (const b of [0.667, 1.667, 2.667, 3.667]) if (rnd() < 0.35) put(tb + b * beat, snare(0.25), 0.4, 0.05);
      if (stabs) {
        const hits = (bar % 8 === 7) ? [0, 1.667, 3.667] : bar % 2 ? [1.667, 3] : [0, 2.667];
        hits.forEach(b => put(tb + b * beat, brass(ch.v.map(n => n + key), beat * 0.45, { vel: 0.9 }), 0.38 * vel, 0.15));
        if (bar % 4 === 3) put(tb + 3.667 * beat, crash(0.4, 1.2), 0.3, -0.3);
      }
    }
    if (melody) for (let l = 0; l < Math.ceil(nBars / 8); l++) for (const [b, m, d] of THEME) {
      const tt = (l * 32 + swing(b)) * beat; put(tt, trumpet(m + key, d * beat * 0.92, 0.95), 0.42 * vel, -0.15);
      if (melody === 'shout') put(tt, trumpet(m + key - 12, d * beat * 0.92, 0.8, { scoop: false }), 0.25 * vel, 0.2);
    }
    return sec;
  },
  sneak(len, { bpm = 176, key = 0 } = {}) {
    const bt = 60 / bpm, sec = section(len), pat = [38, 41, 44, 45];
    for (let k = 0; k * bt < len; k++) { sec.put(k * bt, bassNote(midi(pat[k % 4] + key), bt * 0.5, 0.9), 0.8); if (k % 2) sec.put(k * bt, hat(0.8, 0.03), 0.35); }
    return sec;
  },
  muzak(len, { bpm = 112, key = 0 } = {}) {
    const beat = 60 / bpm, sec = section(len), prog = [[48, [64, 67, 71, 74]], [45, [64, 67, 72, 76]], [50, [65, 69, 72, 76]], [43, [65, 67, 71, 74]]];
    for (let k = 0; k * beat * 2 < len; k++) { const [r, v] = prog[k % 4], tb = k * beat * 2; sec.put(tb, rhodes(v.map(n => n + key), beat * 0.9, 0.7), 0.35, 0.3); sec.put(tb, bassNote(midi(r + key), beat * 0.8, 0.5), 0.35); for (let e = 0; e < 4; e++) sec.put(tb + e * beat * 0.5, hat(0.3, 0.03), 0.15); }
    return sec;
  },
  tension(len, { key = 0 } = {}) {
    const sec = section(len);
    for (let tt = 0; tt < len; tt += 0.75 - 0.45 * (tt / len)) { sec.put(tt, bassNote(midi(26 + key), 0.25, 1), 0.9); sec.put(tt, tom(70, 0.7), 0.5); }
    const tr = buf(len), lp = new Biquad('lp', 900), s1 = new Saw(), s2 = new Saw();
    for (let i = 0; i < tr.length; i++) { const x = i / SR, kk = x / len; if (i % 64 === 0) lp.set(600 + 1400 * kk); tr[i] = lp.p(s1.n(midi(50 + key)) + s2.n(midi(51 + key))) * (0.5 + 0.5 * Math.sin(TAU * 12 * x)) * kk * 0.35; }
    sec.put(0, tr, 0.6);
    return sec;
  },
  // gentle styles for story films (F/C major, roneat-style pentatonic xylophone lines)
  warm(len, { bpm = 84, key = 0, melody = true } = {}) {
    const beat = 60 / bpm, sec = section(len), bar = beat * 4;
    const prog = [[41, [57, 60, 64, 65]], [38, [57, 60, 62, 65]], [46, [57, 62, 65, 69]], [36, [58, 60, 64, 67]]];
    const mel = [[0, 81], [1.5, 84], [2, 86], [3, 84], [4.5, 81], [5, 79], [6, 77], [8, 79], [9.5, 81], [10, 84], [12, 86], [13, 84], [14, 81], [15.5, 79]];
    for (let k = 0; k * bar < len; k++) {
      const [r, v] = prog[k % 4], tb = k * bar;
      sec.put(tb, rhodes(v.map(n => n + key), beat * 1.6, 0.8), 0.45, 0.2); sec.put(tb + beat * 2.5, rhodes(v.map(n => n + key), beat * 1.2, 0.5), 0.3, 0.2);
      sec.put(tb, bassNote(midi(r + key), beat * 1.8, 0.6), 0.5); sec.put(tb + beat * 2, bassNote(midi(r + 7 + key), beat * 1.6, 0.45), 0.45);
      for (let e = 0; e < 8; e++) sec.put(tb + e * beat / 2, hat(e % 2 ? 0.25 : 0.4, 0.03), 0.12, 0.3);
      if (melody && k % 4 >= 2) for (const [b, n] of mel) if (b >= (k % 2) * 8 && b < (k % 2) * 8 + 8) sec.put(tb + (b - (k % 2) * 8) * beat / 2, xylo(n + key, 0.55), 0.3, -0.2);
    }
    return sec;
  },
  upbeat(len, { bpm = 112, key = 0 } = {}) {
    const beat = 60 / bpm, sec = section(len), bar = beat * 4;
    const prog = [[48, [60, 64, 67, 72]], [43, [59, 62, 67, 71]], [45, [60, 64, 69, 72]], [41, [60, 65, 69, 72]]];
    for (let k = 0; k * bar < len; k++) {
      const [r, v] = prog[k % 4], tb = k * bar;
      for (let e = 0; e < 8; e++) sec.put(tb + e * beat / 2, xylo(v[[0, 1, 2, 3, 2, 1, 2, 3][e]] + 12 + key, 0.5), 0.28, 0.15);
      for (let q = 0; q < 4; q++) { sec.put(tb + q * beat, bassNote(midi(r + key + (q === 2 ? 7 : 0)), beat * 0.6, 0.7), 0.55); if (q % 2 === 0) sec.put(tb + q * beat, kick(0.6), 0.45); else sec.put(tb + q * beat, snare(0.5, 230), 0.3, 0.05); }
      for (let e = 0; e < 8; e++) sec.put(tb + e * beat / 2, hat(0.35, 0.03), 0.16, 0.3);
    }
    return sec;
  },
  build(len, { bpm = 120, key = 0 } = {}) {
    const beat = 60 / bpm, sec = section(len), s16 = beat / 4, notes = [57, 60, 64, 60, 69, 64, 60, 64];
    for (let k = 0; k * s16 < len; k++) {
      const tt = k * s16, ramp = 0.35 + 0.65 * (tt / len);
      sec.put(tt, xylo(notes[k % 8] + key, 0.45 * ramp), 0.3, (k % 2) * 0.3 - 0.15);
      if (k % 4 === 0) { sec.put(tt, kick(0.7 * ramp), 0.5); sec.put(tt, bassNote(midi(45 + key + ([0, 0, 3, 5][Math.floor(k / 32) % 4])), beat * 0.8, 0.7), 0.5); }
      if (k % 8 === 4) sec.put(tt, snare(0.5 * ramp, 220), 0.3);
      if (k % 2 === 1) sec.put(tt, hat(0.4 * ramp, 0.025), 0.15, 0.3);
    }
    for (let b = 0; b * beat * 8 < len; b++) sec.put(b * beat * 8, pad([57, 60, 64].map(n => n + key + [0, 0, 3, 5][b % 4]), beat * 7.5, 0.5, 700 + 900 * (b * beat * 8 / len)), 0.35);
    return sec;
  },
  triumph(len, { bpm = 120, key = 0 } = {}) {
    const beat = 60 / bpm, sec = section(len), bar = beat * 4;
    const prog = [[48, [60, 64, 67, 72]], [43, [62, 67, 71, 74]], [45, [64, 69, 72, 76]], [41, [65, 69, 72, 77]]];
    for (let k = 0; k * bar < len; k++) {
      const [r, v] = prog[k % 4], tb = k * bar;
      sec.put(tb, brass(v.map(n => n + key), beat * 1.4, { vel: 0.85, bright: 0.9 }), 0.4, 0.1); sec.put(tb + beat * 2.5, brass(v.map(n => n + key), beat * 0.4, { vel: 0.7 }), 0.3, 0.1);
      if (k % 4 === 0) sec.put(tb, crash(0.6, 1.6), 0.3, -0.3);
      for (let q = 0; q < 4; q++) { sec.put(tb + q * beat, bassNote(midi(r + key), beat * 0.7, 0.8), 0.6); sec.put(tb + q * beat, q % 2 ? snare(0.6) : kick(0.8), q % 2 ? 0.35 : 0.5); }
      for (let e = 0; e < 8; e++) sec.put(tb + e * beat / 2, xylo(v[e % 4] + 24 + key, 0.3), 0.2, -0.2);
    }
    return sec;
  },
  tender(len, { bpm = 72, key = 0 } = {}) {
    const beat = 60 / bpm, sec = section(len), bar = beat * 4;
    const prog = [[41, [57, 60, 64]], [45, [57, 60, 64]], [46, [58, 62, 65]], [48, [55, 60, 64]]];
    const mel = [81, 79, 77, 79, 81, 84, 81, 79];
    for (let k = 0; k * bar < len; k++) {
      const [r, v] = prog[k % 4], tb = k * bar;
      sec.put(tb, pad(v.map(n => n + key), bar * 0.95, 0.7, 900), 0.4, 0);
      sec.put(tb, bassNote(midi(r + key), bar * 0.9, 0.5), 0.4);
      [0, 1, 2, 1].forEach((ix, q) => sec.put(tb + q * beat, rhodes([v[ix] + 12 + key], beat * 0.9, 0.5), 0.3, 0.25));
      if (k % 2 === 1) [0, 1.5, 2, 3].forEach((b, q) => sec.put(tb + b * beat, xylo(mel[(k * 4 + q) % 8] + key, 0.45), 0.28, -0.2));
    }
    return sec;
  },
  // a short sweet "love" sting under a cheesy line: harp glissando up, then a dreamy waltz (rhodes + vibes + pad)
  love(len, { bpm = 96, key = 0 } = {}) {
    const beat = 60 / bpm, sec = section(len), bar = beat * 3;
    [60, 64, 67, 71, 72, 76, 79, 83, 84].forEach((n, i) => sec.put(i * 0.045, xylo(n + key, 0.6), 0.22, -0.4 + i * 0.1));
    const prog = [[48, [64, 67, 71]], [45, [64, 67, 72]], [41, [65, 69, 72]], [43, [62, 67, 71]]];
    const mel = [76, 79, 84, 83, 79, 76, 77, 81, 79, 76, 74, 79];
    for (let k = 0; k * bar < len; k++) {
      const [r, v] = prog[k % 4], tb = 0.4 + k * bar;
      sec.put(tb, pad(v.map(n => n + key), bar * 0.95, 0.6, 1100), 0.35, 0);
      sec.put(tb, bassNote(midi(r + key), beat * 0.9, 0.45), 0.35);
      [1, 2].forEach(q => sec.put(tb + q * beat, rhodes(v.map(n => n + key), beat * 0.8, 0.4), 0.22, 0.2));
      [0, 1, 2].forEach(q => sec.put(tb + q * beat, xylo(mel[(k * 3 + q) % 12] + 12 + key, 0.5), 0.2, -0.15));
    }
    return sec;
  },
  // light electronic "tech" bed: 16th-note pluck arpeggio, pulsing bass, soft four-on-the-floor (dark: minor, no claps)
  // chiptune "game time": square-wave lead, fast arpeggio, pulse bass, punchy 8-bit drums (bpm ~150)
  game(len, { bpm = 152, key = 0, lead = true } = {}) {
    const beat = 60 / bpm, sec = section(len), bar = beat * 4, s16 = beat / 4;
    const sqw = (m, dur, vel = 1, duty = 0.5) => { const b = buf(dur + 0.02), f = midi(m); for (let i = 0; i < b.length; i++) { const t = i / SR, ph = (f * t) % 1; b[i] = (ph < duty ? 1 : -1) * vel * Math.min(1, t * 400) * Math.max(0, 1 - Math.max(0, t - dur) * 50) * (1 - 0.35 * t / dur); } return b; };
    const prog = [[48, [60, 64, 67]], [45, [57, 60, 64]], [41, [57, 60, 65]], [43, [55, 59, 62]]];
    const MEL = [[0, 72, 1], [1, 76, 1], [2, 79, 1.5], [3.5, 77, .5], [4, 76, 1], [5, 74, 1], [6, 72, 2], [8, 69, 1], [9, 72, 1], [10, 76, 1.5], [11.5, 74, .5], [12, 72, 1], [13, 71, 1], [14, 67, 2]];
    for (let k = 0; k * bar < len; k++) {
      const [r, v] = prog[k % 4], tb = k * bar;
      for (let e = 0; e < 16; e++) sec.put(tb + e * s16, sqw(v[e % 3] + 12 + key, s16 * 0.8, 0.5, 0.25), 0.07, (e % 2) * 0.4 - 0.2);
      for (let e = 0; e < 8; e++) sec.put(tb + e * beat / 2, sqw(r + key + (e % 2 ? 12 : 0), beat * 0.4, 0.8, 0.5), 0.1);
      for (let q = 0; q < 4; q++) { sec.put(tb + q * beat, kick(0.7), 0.4); if (q % 2) sec.put(tb + q * beat, snare(0.6, 300), 0.26, 0.05); sec.put(tb + q * beat + beat / 2, hat(0.5, 0.02), 0.13, 0.3); }
    }
    if (lead) for (let ph = 0; ph * 16 * beat < len; ph++) for (const [b0, m, d] of MEL) sec.put(ph * 16 * beat + b0 * beat, sqw(m + key + (ph % 2 && b0 >= 8 ? 2 : 0), d * beat * 0.85, 0.6, 0.5), 0.085, 0.1);
    return sec;
  },
  // music leaking out of someone's headphones: the upbeat cue squeezed through a tinny band (1–4 kHz)
  leak(len, o = {}) {
    const sec = STYLES.upbeat(len, { ...o, bpm: o.bpm || 128 });
    for (const ch of [sec.L, sec.R]) { const f = [new Biquad('hp', 1000), new Biquad('hp', 1000), new Biquad('lp', 4000)]; for (let i = 0; i < ch.length; i++) ch[i] = f[2].p(f[1].p(f[0].p(ch[i]))) * 1.6; }
    return sec;
  },
  tech(len, { bpm = 104, key = 0, dark = false, drums = true } = {}) {
    const beat = 60 / bpm, sec = section(len), bar = beat * 4, s16 = beat / 4;
    const prog = dark ? [[45, [57, 60, 64, 69]], [45, [57, 60, 64, 69]], [41, [57, 60, 65, 69]], [40, [56, 59, 64, 68]]]
                      : [[45, [57, 60, 64, 69]], [41, [57, 60, 65, 69]], [48, [55, 60, 64, 67]], [43, [55, 59, 62, 67]]];
    const arp = [0, 1, 2, 3, 2, 1, 2, 3, 0, 1, 2, 3, 2, 3, 1, 2];
    for (let k = 0; k * bar < len; k++) {
      const [r, v] = prog[k % 4], tb = k * bar;
      for (let e = 0; e < 16; e++) sec.put(tb + e * s16, pluck(midi(v[arp[e]] + 12 + key), s16 * 1.5, e % 4 === 0 ? 0.9 : 0.6, dark ? 0.6 : 1), 0.2, (e % 2) * 0.5 - 0.25);
      for (let e = 0; e < 8; e++) sec.put(tb + e * beat / 2, bassNote(midi(r + key), beat * 0.4, e % 2 ? 0.5 : 0.8), 0.45);
      sec.put(tb, pad(v.slice(0, 3).map(n => n + key), bar * 0.95, 0.45, dark ? 700 : 1300), 0.25);
      if (drums) for (let q = 0; q < 4; q++) { sec.put(tb + q * beat, kick(0.55), 0.45); if (q % 2 && !dark) sec.put(tb + q * beat, snare(0.4, 260), 0.22, 0.05); sec.put(tb + q * beat + beat / 2, hat(0.5, 0.03), 0.16, 0.3); }
    }
    return sec;
  },
  vamp(len, { bpm = 188, key = 0 } = {}) {
    const beat = 60 / bpm, sec = section(len);
    for (let k = 0; k * beat < len - 0.05; k++) { const tt = k * beat; sec.put(tt, bassNote(midi([38, 42, 45, 47][k % 4] + key), beat * 0.8, 0.8), 0.7); sec.put(tt, ride(0.6), 0.25, 0.35); if (k % 2) sec.put(tt, snare(0.5), 0.3); if (k % 4 === 1) sec.put(tt + beat * 0.667, brass(CH.D.v.map(n => n + key), beat * 0.4, { vel: 0.8 }), 0.35); }
    return sec;
  },
};
// "tape stop": playback slows to a halt over `dur` starting at local time `at`
function tapeStop(sec, at, dur) {
  for (const ch of ['L', 'R']) {
    const src = sec[ch].slice(), out = sec[ch], i0 = Math.round(at * SR), n = Math.round(dur * SR);
    let pos = i0;
    for (let i = 0; i < out.length - i0; i++) {
      const k = i / n; const rate = k < 1 ? (1 - k) ** 1.6 : 0;
      const p = Math.floor(pos), fr = pos - p; out[i0 + i] = rate > 0 ? ((src[p] || 0) * (1 - fr) + (src[p + 1] || 0) * fr) * Math.min(1, (1 - k) * 4) : 0;
      pos += rate;
    }
  }
}
function endAt(sec, end, fade) { const e = Math.round(end * SR), nf = Math.max(1, Math.round(fade * SR)); for (let i = Math.max(0, e - nf); i < sec.L.length; i++) { const g = i < e ? (e - i) / nf : 0; sec.L[i] *= g; sec.R[i] *= g; } }
function musicSections() {
  for (const s of cues.filter(c => c.name === 'music')) {
    if (!STYLES[s.style]) { UNKNOWN.add(`music style "${s.style}"`); continue; }
    const e = cues.find(c => c.name === 'music_end' && c.id === s.id && c.t > s.t);
    if (!e) console.log(`WARNING music "${s.id}" has no music_end; it runs to the end`);
    const how = e?.how || 'cut', len = (e ? e.t : DURATION) - s.t;
    const sec = STYLES[s.style](len + (how === 'tapestop' ? (e.dur || 1) + 0.3 : 0), s);
    if (how === 'tapestop') { endAt(sec, len + (e.dur || 1) + 0.25, 0.05); tapeStop(sec, len, e.dur || 1); }
    else endAt(sec, len, how === 'fade' ? (e.dur || 1) : 0.04);
    const [L, R] = BUS.music, i0 = Math.round(s.t * SR), g = s.gain ?? 1;
    for (let i = 0; i < sec.L.length && i0 + i < N; i++) { L[i0 + i] += sec.L[i] * g; R[i0 + i] += sec.R[i] * g; }
  }
}

// ---------------------------------------------------------------- render
musicSections();
for (const c of cues) if (c.name !== 'music' && c.name !== 'music_end') playCue(c);
// small room reverb on music + sfx
function reverb(L, R, wet = 0.14) {
  const combs = [1557, 1617, 1491, 1422].map(d => ({ d, b: new Float32Array(d), i: 0, f: 0.78 }));
  const aps = [225, 556].map(d => ({ d, b: new Float32Array(d), i: 0 }));
  for (let n = 0; n < N; n++) {
    const x = (L[n] + R[n]) * 0.5; let y = 0;
    for (const c of combs) { const o = c.b[c.i]; c.b[c.i] = x + o * c.f; c.i = (c.i + 1) % c.d; y += o; }
    y *= 0.25;
    for (const a of aps) { const o = a.b[a.i]; const v = y + o * 0.5; a.b[a.i] = v; a.i = (a.i + 1) % a.d; y = o - v * 0.5; }
    L[n] += y * wet; R[n] += y * wet * 0.96;
  }
}
reverb(...BUS.music, 0.16); reverb(...BUS.sfx, 0.08);
const out = new Int16Array(N * 2);
let peak = 0;
const ML = new Float32Array(N), MR = new Float32Array(N);
// film.json "mix": { "music": 0.5, "sfx": 0.75, "voice": 1.1, "duck": 1 }. duck < 1 dips the music to that
// fraction while anyone speaks (smooth sidechain), so story films can play music fuller between lines.
const MIX = (() => { try { return { music: 0.5, sfx: 0.75, voice: 1.1, duck: 1, ...(JSON.parse(fs.readFileSync('film.json', 'utf8')).mix || {}) }; } catch { return { music: 0.5, sfx: 0.75, voice: 1.1, duck: 1 }; } })();
const duckEnv = new Float32Array(N);
{ let e = 0; const att = Math.exp(-1 / (0.03 * SR)), rel = Math.exp(-1 / (0.45 * SR)); // fast down, slow back up
  for (let i = 0; i < N; i++) { const v = Math.min(1, (Math.abs(BUS.vox[0][i]) + Math.abs(BUS.vox[1][i])) * 6); e = v > e ? v + (e - v) * att : v + (e - v) * rel; duckEnv[i] = e; } }
for (let i = 0; i < N; i++) {
  const mg = MIX.music * (1 - (1 - MIX.duck) * Math.min(1, duckEnv[i] * 1.5));
  ML[i] = BUS.music[0][i] * mg + BUS.sfx[0][i] * MIX.sfx + BUS.vox[0][i] * MIX.voice;
  MR[i] = BUS.music[1][i] * mg + BUS.sfx[1][i] * MIX.sfx + BUS.vox[1][i] * MIX.voice;
  peak = Math.max(peak, Math.abs(ML[i]), Math.abs(MR[i]));
}
const g = 0.9 / Math.max(peak, 1e-6);
for (let i = 0; i < N; i++) { out[i * 2] = Math.tanh(ML[i] * g * 1.2) / Math.tanh(1.2) * 32767 * 0.95; out[i * 2 + 1] = Math.tanh(MR[i] * g * 1.2) / Math.tanh(1.2) * 32767 * 0.95; }
const hdr = Buffer.alloc(44);
hdr.write('RIFF', 0); hdr.writeUInt32LE(36 + out.byteLength, 4); hdr.write('WAVE', 8); hdr.write('fmt ', 12); hdr.writeUInt32LE(16, 16); hdr.writeUInt16LE(1, 20); hdr.writeUInt16LE(2, 22); hdr.writeUInt32LE(SR, 24); hdr.writeUInt32LE(SR * 4, 28); hdr.writeUInt16LE(4, 32); hdr.writeUInt16LE(16, 34); hdr.write('data', 36); hdr.writeUInt32LE(out.byteLength, 40);
fs.writeFileSync('build/audio_raw.wav', Buffer.concat([hdr, Buffer.from(out.buffer)]));
execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', 'build/audio_raw.wav', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', '44100', 'build/audio.wav']);
// soft subtitle tracks timed to the actual clips: the spoken language + an optional translation
const srtT = x => { const ms = Math.round(x * 1000); const p = (n, w = 2) => String(n).padStart(w, '0'); return `${p(Math.floor(ms / 3600000))}:${p(Math.floor(ms / 60000) % 60)}:${p(Math.floor(ms / 1000) % 60)},${p(ms % 1000, 3)}`; };
SPOKEN.sort((a, b) => a.t - b.t);
const srt = key => SPOKEN.map((l, i) => `${i + 1}\n${srtT(l.t)} --> ${srtT(Math.min(l.t + Math.max(l.dur, 1.2) + 0.2, SPOKEN[i + 1]?.t ?? 1e9))}\n${l[key]}\n`).join('\n');
for (const f of fs.readdirSync('build')) if (/^subtitles_.*\.srt$/.test(f)) fs.unlinkSync(`build/${f}`);
if (SPOKEN.length) {
  fs.writeFileSync(`build/subtitles_${VCFG.lang || 'en'}.srt`, srt('text'));
  if (VCFG.translation && SPOKEN.some(l => l.tr)) fs.writeFileSync(`build/subtitles_${VCFG.translation}.srt`, srt('tr'));
}
const overlaps = SPOKEN.filter((l, i) => SPOKEN[i + 1] && l.t + l.dur > SPOKEN[i + 1].t).map(l => `${l.text} (${l.t.toFixed(2)}s +${l.dur.toFixed(2)}s)`);
if (overlaps.length) console.log('WARNING overlapping lines (move the next cue later or lengthen the shot):', overlaps.join('; '));
if (UNKNOWN.size) console.log('WARNING unknown cues (no sound):', [...UNKNOWN].join(', '));
console.log(SPOKEN.map(l => `${l.t.toFixed(2)}s ${l.dur.toFixed(2)}s ${l.who}: ${l.text}`).join('\n'));
console.log(`audio: ${DURATION}s, ${cues.length} cues, raw peak ${peak.toFixed(2)} -> build/audio.wav`);
