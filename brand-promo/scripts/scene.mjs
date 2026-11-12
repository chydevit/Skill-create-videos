// brand-promo: a dark, kinetic studio showreel drawn on one canvas, frame by frame.
// Everything specific to a brand comes from the project: /proj/promo.json (texts, colours, works),
// /proj/assets/manifest.json (clips, stills, logo frames) and /proj/build/tm.json (narration timings).
// render(t) is deterministic in t, so frames can be rendered out of order or in parallel.
const W = 1920, H = 1080;
let CFG, MAN, TM, LEVELS, T, KM, N;
let SANS, DISPLAY;
const MONO = '"SF Mono", Menlo, Consolas, monospace';
let ROUND = '"Arial Rounded MT Bold", "Helvetica Neue", sans-serif';
const C = { text: '#ededed', white: '#ffffff', muted: '#a1a1a1', dim: '#5c5c5c', blue: '#0a84ff', cyan: '#01d4f7', orange: '#fe9a01' };

// the score's grid (scripts/music.py): 128 bpm, bars from 0.075 s; title drop bar 4; N spotlights of 3 bars from bar 5;
// break at bar 5+3N; clip rush; final hit at bar 9+3N as the liquid logo lands
const BPM = 128, BEAT = 60 / BPM, BAR = 4 * BEAT, T0 = 0.075, B = n => T0 + n * BAR;
const DROP = B(4);
let SPOT_T, BREAK, HIT, L0, DUR, GLOW, SECTIONS;

// ------------------------------------------------------------------ maths
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, k) => a + (b - a) * k;
const prog = (t, a, b) => clamp((t - a) / (b - a));
const eOut = k => 1 - Math.pow(1 - k, 3);
const eIn = k => k * k * k;
const eIO = k => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2);
const eExpo = k => (k >= 1 ? 1 : 1 - Math.pow(2, -10 * k));
const eBack = (k, s = 1.7) => (k <= 0 ? 0 : 1 + (s + 1) * Math.pow(k - 1, 3) + s * Math.pow(k - 1, 2));
function rng(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const pad = (n, w) => String(n).padStart(w, '0');
const hexA = (h, a) => { const n = parseInt(h.slice(1), 16); return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`; };
function keys(t, pts) {                          // piecewise-linear value over [time, value] points
  if (t <= pts[0][0]) return pts[0][1];
  for (let i = 1; i < pts.length; i++) if (t <= pts[i][0]) return lerp(pts[i - 1][1], pts[i][1], (t - pts[i - 1][0]) / Math.max(1e-6, pts[i][0] - pts[i - 1][0]));
  return pts[pts.length - 1][1];
}

// ------------------------------------------------------------------ assets
const cache = new Map();
function load(url) {
  let p = cache.get(url);
  if (p) { cache.delete(url); cache.set(url, p); return p; }
  p = new Promise((res, rej) => { const im = new Image(); im.onload = () => res(im); im.onerror = () => rej(new Error('load ' + url)); im.src = url; });
  cache.set(url, p);
  if (cache.size > 420) cache.delete(cache.keys().next().value);
  return p;
}
function clipImg(name, lt) {                     // clips loop
  const n = MAN.clips[name], f = ((Math.floor(lt * 30) % n) + n) % n;
  return load(`/proj/assets/clips/${name}/${pad(f + 1, 4)}.jpg`);
}
const stillImg = i => load(`/proj/assets/stills/s${pad(i, 2)}.jpg`);
const logoImg = lt => load(`/proj/assets/logo/${pad(clamp(Math.floor(lt * 60), 0, MAN.logo.frames - 1) + 1, 4)}.png`);   // 1000x1000, mark centred

// ------------------------------------------------------------------ drawing helpers
function rr(g, x, y, w, h, r) { g.beginPath(); g.roundRect(x, y, w, h, r); }
function cover(g, img, x, y, w, h) {
  const s = Math.max(w / img.width, h / img.height), iw = img.width * s, ih = img.height * s;
  g.drawImage(img, x + (w - iw) / 2, y + (h - ih) / 2, iw, ih);
}
function tw(g, str, size, weight = 500, font = SANS, letter = 0) {
  g.save(); g.font = `${weight} ${size}px ${font}`; g.letterSpacing = `${letter}px`; const w = g.measureText(str).width; g.restore(); return w;
}
function text(g, str, x, y, o = {}) {
  const { size = 60, weight = 500, font = SANS, fill = C.text, align = 'center', a = 1, blur = 0, s = 1, sx = 1, letter = 0, glow = null, glitch = 0, seed = 1 } = o;
  if (!str || a <= 0.004 || s <= 0.004) return;
  g.save(); g.globalAlpha = clamp(a); g.font = `${weight} ${size}px ${font}`; g.textAlign = align; g.textBaseline = 'middle';
  g.letterSpacing = `${letter}px`;
  g.translate(x, y); g.scale(s * sx, s);
  if (blur > 0.4) g.filter = `blur(${blur.toFixed(1)}px)`;
  if (glow) { g.shadowColor = glow; g.shadowBlur = size * 0.5; }
  if (glitch > 0.01) {                           // RGB split: two coloured ghosts either side
    const r = rng(seed), d = glitch * size * 0.08;
    g.globalCompositeOperation = 'lighter';
    g.fillStyle = hexA(C.cyan, 0.8); g.fillText(str, -d * (0.5 + r()), (r() - 0.5) * d);
    g.fillStyle = hexA(C.orange, 0.7); g.fillText(str, d * (0.5 + r()), (r() - 0.5) * d);
    g.globalCompositeOperation = 'source-over';
  }
  g.fillStyle = fill; g.fillText(str, 0, 0);
  g.restore();
}
// typing goes by whole clusters, so a Khmer stack (consonant + coeng + subscript + vowel signs) never shows half-built
const KHM_MARK = c => (c >= 0x17B4 && c <= 0x17D3) || c === 0x17DD;
function clusters(str) {
  const out = [];
  for (const ch of str) {
    const c = ch.codePointAt(0);
    if (out.length && (KHM_MARK(c) || out[out.length - 1].endsWith('្'))) out[out.length - 1] += ch; else out.push(ch);
  }
  return out;
}
const typed = (str, t, t0, cps = 24) => { const cl = clusters(str); return cl.slice(0, clamp(Math.floor((t - t0) * cps), 0, cl.length)).join(''); };
function caret(g, x, y, h, t, a = 1) {
  if (a <= 0.01 || Math.floor(t * 2.6) % 2) return;
  g.save(); g.globalAlpha = a; g.fillStyle = C.blue; g.fillRect(x + 6, y - h / 2, 4, h); g.restore();
}
// pooled offscreen canvases (one per key, reused every frame)
const pool = new Map();
function oc(key, w, h) {
  w = Math.round(w); h = Math.round(h);
  let c = pool.get(key);
  if (!c || c.width !== w || c.height !== h) { c = document.createElement('canvas'); c.width = w; c.height = h; pool.set(key, c); }
  const x = c.getContext('2d'); x.setTransform(1, 0, 0, 1, 0, 0); x.globalAlpha = 1; x.filter = 'none'; x.globalCompositeOperation = 'source-over';
  x.clearRect(0, 0, w, h); return [c, x];
}
function chip(x, label, px, py, dot = C.blue, size = 22) {
  x.save(); x.font = `600 ${size}px ${SANS}`; const w = x.measureText(label).width + size * 2.2, h = size * 1.9;
  rr(x, px, py, w, h, h / 2); x.fillStyle = 'rgba(0,0,0,0.6)'; x.fill(); x.lineWidth = 1.5; x.strokeStyle = 'rgba(255,255,255,0.16)'; x.stroke();
  x.beginPath(); x.arc(px + size * 0.85, py + h / 2, size * 0.26, 0, 7); x.fillStyle = dot; x.fill();
  x.fillStyle = C.text; x.textAlign = 'left'; x.textBaseline = 'middle'; x.fillText(label, px + size * 1.35, py + h / 2 + 1);
  x.restore();
}
// a card face drawn flat into its own canvas (image or drawing fn, glass sheen, hairline)
function face(key, img, w, h, o = {}) {
  const { r = 22, dim = 0, bg = '#0e0e10', after = null } = o;
  const [c, x] = oc(key, w, h);
  x.save(); rr(x, 0, 0, w, h, r); x.clip();
  x.fillStyle = bg; x.fillRect(0, 0, w, h);
  if (typeof img === 'function') img(x, w, h); else if (img) cover(x, img, 0, 0, w, h);
  if (dim > 0) { x.fillStyle = `rgba(0,0,0,${dim})`; x.fillRect(0, 0, w, h); }
  if (after) after(x, w, h);
  const sh = x.createLinearGradient(0, 0, 0, h * 0.45); sh.addColorStop(0, 'rgba(255,255,255,0.10)'); sh.addColorStop(1, 'rgba(255,255,255,0)');
  x.fillStyle = sh; x.fillRect(0, 0, w, h * 0.45);
  x.restore();
  rr(x, 0.75, 0.75, w - 1.5, h - 1.5, r); x.lineWidth = 1.5; x.strokeStyle = 'rgba(255,255,255,0.18)'; x.stroke();
  return c;
}
// a flat card turned about its vertical axis and seen in perspective (camera at the frame centre, focal f).
// World X/Y are pixels from the frame centre at depth Z = 0; Z grows away from the camera.
const LAYER = document.createElement('canvas'); LAYER.width = 3000; LAYER.height = 2000; const LX = 540, LY = 460;
const lg = LAYER.getContext('2d');
function persp(g, src, X, Y, Z, w, h, ry, o = {}) {
  const { a = 1, f = 1600, N: strips = 64, shadow = 0.55, rim = 0 } = o;
  const cs = Math.cos(ry), sn = Math.sin(ry);
  const proj = (u, v) => { const k = f / Math.max(80, f + Z + u * sn); return [960 + (X + u * cs) * k, 540 + (Y + v) * k, k]; };
  const tl = proj(-w / 2, -h / 2), tr = proj(w / 2, -h / 2), bl = proj(-w / 2, h / 2), br = proj(w / 2, h / 2);
  if (a <= 0.004 || !src) return;
  const quad = c => { c.beginPath(); c.moveTo(tl[0], tl[1]); c.lineTo(tr[0], tr[1]); c.lineTo(br[0], br[1]); c.lineTo(bl[0], bl[1]); c.closePath(); };
  g.save(); g.globalAlpha = clamp(a);
  if (shadow > 0) { g.save(); quad(g); g.fillStyle = '#000'; g.shadowColor = `rgba(0,0,0,${shadow})`; g.shadowBlur = 70; g.shadowOffsetY = 40 * tl[2]; g.fill(); g.restore(); }
  if (rim > 0) { g.save(); quad(g); g.lineWidth = 4; g.strokeStyle = C.blue; g.shadowColor = C.blue; g.shadowBlur = 46; g.globalAlpha = clamp(a * rim); g.stroke(); g.stroke(); g.restore(); }
  // strips go onto a shared layer at full opacity (no seams), then the layer is composited once with the card's alpha
  const xs = [tl[0], tr[0], bl[0], br[0]], ys = [tl[1], tr[1], bl[1], br[1]];
  const bx = Math.floor(Math.min(...xs)) - 2, by = Math.floor(Math.min(...ys)) - 2;
  const bw = Math.ceil(Math.max(...xs)) + 2 - bx, bh = Math.ceil(Math.max(...ys)) + 2 - by;
  lg.setTransform(1, 0, 0, 1, LX, LY); lg.clearRect(bx, by, bw, bh);
  const sw = src.width / strips;
  for (let i = 0; i < strips; i++) {
    const u0 = -w / 2 + i * w / strips, u1 = u0 + w / strips;
    const p0 = proj(u0, -h / 2), p1 = proj(u1, -h / 2), q0 = proj(u0, h / 2), q1 = proj(u1, h / 2);
    const dx = Math.min(p0[0], p1[0]), dw = Math.abs(p1[0] - p0[0]);
    if (dw < 0.05) continue;
    const top = (p0[1] + p1[1]) / 2, bot = (q0[1] + q1[1]) / 2;
    lg.drawImage(src, i * sw, 0, sw, src.height, dx, top, dw + 0.7, bot - top);
  }
  g.drawImage(LAYER, bx + LX, by + LY, bw, bh, bx, by, bw, bh);
  g.restore();
}
function veil(g, cx, cy, rx, ry, a) {           // soft black ellipse behind text
  if (a <= 0.01) return;
  g.save(); g.globalAlpha = a; g.translate(cx, cy); g.scale(rx / 100, ry / 100);
  const gr = g.createRadialGradient(0, 0, 0, 0, 0, 100); gr.addColorStop(0, 'rgba(0,0,0,0.92)'); gr.addColorStop(0.6, 'rgba(0,0,0,0.7)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = gr; g.fillRect(-100, -100, 200, 200); g.restore();
}

// ------------------------------------------------------------------ background: black, faint dot grid, accent glow from below
let dotPat;
function pulse(t) {
  const on = (t >= DROP && t < B(5) - 0.05) || (t >= B(6 + 3 * N) && t < B(8 + 3 * N));
  return on ? Math.exp(-((((t - T0) / BEAT) % 1 + 1) % 1) * 6) : 0;
}
function background(g, t) {
  g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
  g.save(); const off = (t * 9) % 60; g.translate(-off, -off * 0.5); g.fillStyle = dotPat; g.fillRect(0, 0, W + 60, H + 60); g.restore();
  const glow = keys(t, GLOW) * (1 + 0.2 * pulse(t));
  if (glow > 0.003) {
    g.save(); g.globalAlpha = clamp(glow); g.translate(960, 1210); g.scale(1.6, 1);
    const gr = g.createRadialGradient(0, 0, 0, 0, 0, 780);
    gr.addColorStop(0, hexA(C.blue, 0.9)); gr.addColorStop(0.3, hexA(C.blue, 0.45)); gr.addColorStop(0.62, hexA(C.blue, 0.12)); gr.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = gr; g.fillRect(-780, -780, 1560, 1560); g.restore();
    g.save(); g.globalAlpha = clamp(glow * 0.5); g.translate(960, 1130); g.scale(2.2, 0.5);    // a second-colour core along the floor
    const cg = g.createRadialGradient(0, 0, 0, 0, 0, 300); cg.addColorStop(0, hexA(C.cyan, 0.5)); cg.addColorStop(1, hexA(C.cyan, 0));
    g.fillStyle = cg; g.fillRect(-300, -300, 600, 600); g.restore();
  }
}

// ------------------------------------------------------------------ helpers for the sections
// eyebrow label: [01] FOLK TALE · 9:16 (mono, uppercase, muted, the number in the accent colour)
function eyebrow(g, num, label, x, y, a) {
  if (a <= 0.01) return;
  g.save(); g.globalAlpha = a; g.font = KM ? `500 26px ${SANS}` : `500 24px ${MONO}`; g.letterSpacing = KM ? '0px' : '3px'; g.textBaseline = 'middle'; g.textAlign = 'left';
  g.fillStyle = C.blue; g.fillText(`[${num}]`, x, y);
  const w = g.measureText(`[${num}] `).width; g.fillStyle = C.muted; g.fillText(label, x + w, y);
  g.restore();
}
// title block for a spotlight: eyebrow, big title, a muted second line (long lines shrink to fit maxW)
function titleBlock(g, t, t0, x, num, label, title, line, out, maxW = 9999) {
  const k1 = eOut(prog(t, t0, t0 + 0.5)), k2 = eOut(prog(t, t0 + 0.15, t0 + 0.65)), k3 = eOut(prog(t, t0 + 0.45, t0 + 0.95));
  const a = 1 - out;
  eyebrow(g, num, label, x, 380 + (1 - k1) * 20, k1 * a);
  const ts = Math.min(116, 116 * maxW / tw(g, title, 116, 600, SANS, KM ? 0 : -4)), ls = Math.min(50, 50 * maxW / tw(g, line, 50, 500, SANS, KM ? 0 : -1));
  text(g, title, x - 4, 470 + (1 - k2) * 24, { size: ts, weight: 600, letter: KM ? 0 : -4, align: 'left', fill: C.text, a: k2 * a, blur: out * 12 });
  text(g, line, x, (KM ? 575 : 560) + (1 - k3) * 24, { size: ls, weight: 500, letter: KM ? 0 : -1, align: 'left', fill: C.muted, a: k3 * a, blur: out * 12 });
}
// a phone with a screen drawn by `screen(g, x, y, w, h)`
function phone(g, cx, cy, PW, PH, rot, a, screen) {
  if (a <= 0.01) return;
  g.save(); g.translate(cx, cy); g.rotate(rot); g.globalAlpha = a;
  g.shadowColor = hexA(C.blue, 0.38); g.shadowBlur = 110; g.shadowOffsetY = 30;
  rr(g, -PW / 2, -PH / 2, PW, PH, PW * 0.16); g.fillStyle = '#0d0e12'; g.fill(); g.shadowColor = 'transparent';
  g.lineWidth = 3; g.strokeStyle = '#3c3d44'; g.stroke();
  const m = PW * 0.04;
  g.save(); rr(g, -PW / 2 + m, -PH / 2 + m, PW - 2 * m, PH - 2 * m, PW * 0.13); g.clip();
  g.fillStyle = '#000'; g.fillRect(-PW / 2, -PH / 2, PW, PH); screen(g, -PW / 2 + m, -PH / 2 + m, PW - 2 * m, PH - 2 * m);
  const sh = g.createLinearGradient(0, -PH / 2, 0, 0); sh.addColorStop(0, 'rgba(255,255,255,0.10)'); sh.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = sh; g.fillRect(-PW / 2, -PH / 2, PW, PH / 2);
  g.restore();
  rr(g, -PW * 0.14, -PH / 2 + m + 14, PW * 0.28, PW * 0.08, PW * 0.04); g.fillStyle = '#0d0e12'; g.fill();
  g.restore();
}
// "sound on" chip: speaker, five bars driven by the clip's real loudness, and a label
function soundChip(x, px, py, k, lv, label, size = 24) {
  if (k <= 0.01) return;
  x.save(); x.globalAlpha = clamp(k * 1.6);
  x.font = `600 ${size}px ${SANS}`; const tw0 = x.measureText(label).width, h = size * 2.1, w = size * 4.6 + tw0;
  x.translate(px, py); const sc = eBack(clamp(k), 1.6); x.translate(0, h / 2); x.scale(sc, sc); x.translate(0, -h / 2);
  rr(x, 0, 0, w, h, h / 2); x.fillStyle = 'rgba(0,0,0,0.68)'; x.fill(); x.lineWidth = 2; x.strokeStyle = hexA(C.blue, 0.9); x.stroke();
  const cy = h / 2, u = size * 0.42, sx0 = size * 0.7;
  x.fillStyle = '#fff'; x.beginPath(); x.moveTo(sx0, cy - u * 0.45); x.lineTo(sx0 + u * 0.55, cy - u * 0.45); x.lineTo(sx0 + u * 1.2, cy - u);
  x.lineTo(sx0 + u * 1.2, cy + u); x.lineTo(sx0 + u * 0.55, cy + u * 0.45); x.lineTo(sx0, cy + u * 0.45); x.closePath(); x.fill();
  const bx = sx0 + u * 1.9, bw = size * 0.2;
  for (let i = 0; i < 5; i++) {
    const v = clamp((lv(i) ?? 0) * (0.7 + 0.3 * ((i * 37) % 5) / 4)), bh = Math.max(3, v * h * 0.62);
    rr(x, bx + i * bw * 1.8, cy - bh / 2, bw, bh, bw / 2); x.fillStyle = i % 2 ? C.cyan : C.blue; x.fill();
  }
  x.fillStyle = C.text; x.textBaseline = 'middle'; x.textAlign = 'left'; x.fillText(label, bx + 5 * bw * 1.8 + size * 0.35, cy + 1);
  x.restore();
}

// ------------------------------------------------------------------ sections
async function s1(g, t) {                        // { Every story } / deserves to move.
  const str = T.typed, size = 64, full = tw(g, str, size, 500);
  const open = eOut(prog(t, 0.1, 0.4)), spread = eIO(prog(t, 0.25, 0.7)), out = eIn(prog(t, 3.05, 3.35));
  const half = lerp(36, full / 2 + 56, spread) + out * 600;
  text(g, '{', 960 - half, 492, { size: 68, weight: 300, a: open * (1 - out * 0.8), blur: out * 10 });
  text(g, '}', 960 + half, 492, { size: 68, weight: 300, a: open * (1 - out * 0.8), blur: out * 10 });
  const shown = typed(str, t, 0.5, 20);
  text(g, shown, 960 - full / 2, 496, { size, align: 'left', a: 1 - out, blur: out * 14 });
  if (t < 1.25) caret(g, 960 - full / 2 + tw(g, shown, size, 500), 496, 66, t, 1 - out);
  const k = eOut(prog(t, 1.25, 1.75)), [a, b] = T.line, wa = tw(g, a, 64, 500), wb = tw(g, b, 64, 700), x0 = 960 - (wa + wb) / 2;
  text(g, a, x0, 590 + (1 - k) * 20, { size: 64, align: 'left', fill: C.muted, a: k * (1 - out), blur: out * 14 });
  text(g, b, x0 + wa, 590 + (1 - k) * 20, { size: 64, weight: 700, align: 'left', fill: C.blue, glow: hexA(C.blue, 0.6), a: k * (1 - out), blur: out * 14 });
}

const RING_POS = [[-640, -300], [-250, -360], [260, -350], [650, -290], [-760, 20], [770, 40], [-600, 320], [-200, 360], [230, 350], [620, 320]];
let RING;
async function s2(g, t) {                        // a ring of cards from all the works: "Here are five of ours."
  const out = eIn(prog(t, 7.3, 7.6));
  for (let i = 0; i < RING.length; i++) {
    const c = RING[i], k = eExpo(prog(t, 3.25 + i * 0.05, 4.15 + i * 0.05));
    const w = c.vert ? 210 : 330, h = c.vert ? 373 : 186;
    const fc = face('s2c' + i, await stillImg(c.si), w, h, { r: 18, dim: 0.1 });
    const drift = 0.04 * prog(t, 4, 7.3);
    persp(g, fc, c.X * (1 + drift + out * 0.8), c.Y * (1 + drift + out * 0.8), lerp(c.z0, 0, k) - out * 500, w, h, c.ry + (1 - k) * 0.6, { a: clamp(k * 1.5) * (1 - out), shadow: 0.5 });
  }
  veil(g, 960, 540, 620, 170, 0.9 * (1 - out));
  const k = eOut(prog(t, 3.7, 4.2)), [a, b] = T.ring, wa = tw(g, a, 72, 600), wb = tw(g, b, 72, 700), x0 = 960 - (wa + wb) / 2;
  text(g, a, x0, 540 + (1 - k) * 20, { size: 72, weight: 600, align: 'left', a: k * (1 - out), blur: (1 - k) * 12 + out * 14 });
  text(g, b, x0 + wa, 540 + (1 - k) * 20, { size: 72, weight: 700, align: 'left', fill: C.blue, glow: hexA(C.blue, 0.6), a: k * (1 - out), blur: (1 - k) * 12 + out * 14 });
}

async function s4(g, t) {                        // the drop: SHOWREEL / [Brand name] / subline
  const k = eOut(prog(t, 7.62, 7.95)), out = eIn(prog(t, 9.27, 9.45)), bk = eExpo(prog(t, 7.75, 8.1));
  const name = CFG.brand.name.join(''), ns = Math.min(120, 1500 / Math.max(1, tw(g, name, 120, 400, ROUND)) * 120);
  const nw = tw(g, name, ns, 400, ROUND), bw = nw + 70, x0 = 960 - bw / 2;
  g.save(); g.globalAlpha = 1 - out; if (out > 0.02) g.filter = `blur(${(out * 14).toFixed(1)}px)`;
  const eb = T.eyebrow, ew = KM ? tw(g, eb, 30, 500, SANS, 0) : tw(g, eb, 26, 500, MONO, 10);
  g.font = KM ? `500 30px ${SANS}` : `500 26px ${MONO}`; g.letterSpacing = KM ? '0px' : '10px'; g.fillStyle = C.muted; g.textAlign = 'left'; g.textBaseline = 'middle';
  g.globalAlpha = k * (1 - out); g.fillText(eb, 960 - ew / 2, 400 + (1 - k) * 16); g.globalAlpha = 1 - out; g.letterSpacing = '0px';
  if (bk > 0) {
    g.save(); g.beginPath(); g.rect(x0 - 10, 450, (bw + 20) * bk, 180); g.clip();
    g.shadowColor = hexA(C.blue, 0.85); g.shadowBlur = 60; g.fillStyle = C.blue; g.fillRect(x0, 466, bw, 148); g.shadowColor = 'transparent';
    const gl = 1 - prog(t, 7.9, 8.35), jit = gl > 0 ? (rng(Math.floor(t * 30))() - 0.5) * 20 * gl : 0;
    text(g, name, x0 + 35 + jit, 544, { size: ns, weight: 400, font: ROUND, align: 'left', fill: '#fff', glitch: gl * 2.2, seed: Math.floor(t * 30) });
    g.restore();
  }
  const sk = eOut(prog(t, 8.2, 8.65));
  text(g, T.subline, 960, 690 + (1 - sk) * 20, { size: 46, weight: 500, fill: C.muted, a: sk * (1 - out) });
  g.restore();
}

let SPOTS;                                        // one per work, from promo.json + manifest
async function spot(g, t, k) {
  const S = SPOT_T[k], E = S + 3 * BAR, sp = SPOTS[k], bite = TM.bite[k], c0 = bite - 2.0;   // the clip's frame 0 sits 2 s before its sound
  const kin = eExpo(prog(t, S - 0.1, S + 0.6)), out = eIn(prog(t, E - 0.22, E + 0.03));
  const img = await clipImg(sp.clip, Math.max(0, t - c0));
  const BL = TM.blen[k], sk = !sp.sound || t < bite ? 0 : eOut(prog(t, bite, bite + 0.3)) * (1 - prog(t, bite + BL - 0.25, bite + BL));
  const lvArr = LEVELS[sp.clip] || [], fi = Math.floor((t - bite) * 30);
  const lv = i => (lvArr[clamp(fi - i * 2, 0, lvArr.length - 1)] || 0) * (t >= bite && t <= bite + BL ? 1 : 0);
  const lenLabel = sp.len ? T.fullVideo + sp.len : null;
  if (sp.vert) {                                    // a vertical work plays on a phone
    phone(g, 1240 + (1 - kin) * 260 + out * 200, 560 + (1 - kin) * 60 + Math.sin(t * 1.3) * 6, 380, 790, -0.05 + 0.015 * Math.sin(t * 0.8), clamp(kin * 1.6) * (1 - out),
      (gg, x, y, w, h) => { cover(gg, img, x, y, w, h); gg.save(); gg.translate(x, y); if (lenLabel) chip(gg, lenLabel, 20, 60, C.blue, 18); soundChip(gg, 20, h - 74, sk, lv, T.soundOn, 20); gg.restore(); });
    titleBlock(g, t, S + 0.05, 170, sp.num, sp.label, sp.title, sp.line, out, 820);
    return;
  }
  const CW = 920, CH = 518, side = sp.side, X = side * 285, ry = -side * 0.22;
  const fc = face('spot' + k, img, CW, CH, { r: 26, after: (x, w, h) => { if (lenLabel) chip(x, lenLabel, 22, 22, C.blue, 20); soundChip(x, 22, h - 76, sk, lv, T.soundOn, 24); } });
  persp(g, fc, X + (1 - kin) * side * 300 + out * side * 200, -10 + (1 - kin) * 160 + Math.sin(t * 1.2) * 5, (1 - kin) * 500 + out * 300, CW, CH, ry + 0.035 * Math.sin(t * 0.9),
    { a: clamp(kin * 1.6) * (1 - out), rim: 0.45 + 0.5 * sk });
  titleBlock(g, t, S + 0.05, side > 0 ? 140 : 1250, sp.num, sp.label, sp.title, sp.line, out, 600);
}

async function s8(g, t) {                        // the break: "Your story" ... "next."
  const [a0, a1] = TM.next, [w1, w2] = T.next;
  if (t < a1) {
    const k = eExpo(prog(t, a0, a0 + 0.2)), size = Math.min(KM ? 200 : 220, 1700 / Math.max(1, tw(g, w1, 220, KM ? 400 : 800, DISPLAY, KM ? 0 : -8)) * 220);
    text(g, w1, 960, 540, { size, weight: KM ? 400 : 800, font: DISPLAY, letter: KM ? 0 : -8, fill: C.text, s: lerp(1.3, 1, k), blur: (1 - k) * 20 });
  } else {
    const k = eExpo(prog(t, a1, a1 + 0.2)), out = eIn(prog(t, BREAK + 1.705, BREAK + 1.875));
    const size = Math.min(KM ? 240 : 300, 1700 / Math.max(1, tw(g, w2, 300, KM ? 400 : 800, DISPLAY, KM ? 0 : -10)) * 300);
    text(g, w2, 960, 540, { size, weight: KM ? 400 : 800, font: DISPLAY, letter: KM ? 0 : -10, fill: C.blue, glow: hexA(C.blue, 0.75), s: lerp(1.35, 1, k) * (1 + out * 0.3), blur: (1 - k) * 20 + out * 24, a: 1 - out });
  }
}

let RUSH;
async function s9(g, t) {                        // every clip rushing past: Written · Voiced · Animated
  const R0 = BREAK + 1.825, lt = t - R0, out = eIn(prog(t, HIT - 0.725, HIT - 0.525));
  const items = RUSH.map((c, i) => ({ ...c, i, z: c.Z - 1000 * lt - 150 * lt * lt })).filter(c => c.z > -1150).sort((a, b) => b.z - a.z);
  for (const c of items) {
    const kz = 1600 / (1600 + c.z), a = clamp((kz - 0.35) * 3) * clamp((2.6 - kz) / 1.2) * (1 - out) * eOut(prog(t, R0, R0 + 0.3));
    if (a <= 0.01) continue;
    const vert = MAN.vertical.includes(c.clip), w = vert ? 250 : 460, h = vert ? 444 : 259;
    const fc = face('s9c' + c.i, await clipImg(c.clip, lt + c.i * 0.3), w, h, { r: 18, dim: 0.15 });
    persp(g, fc, c.X, c.Y, c.z, w, h, c.ry, { a, shadow: 0.4, N: 40 });
  }
  veil(g, 960, 540, 820, 200, 0.88 * (1 - out));
  const words = T.rush, sep = '  ·  ';
  let size = KM ? 78 : 84;
  const fit = () => words.map(w => tw(g, w, size, 700)).reduce((a, b) => a + b, 0) + (words.length - 1) * tw(g, sep, size, 400);
  if (fit() > 1700) size *= 1700 / fit();
  const ws = words.map(w => tw(g, w, size, 700)), ss = tw(g, sep, size, 400), tot = ws.reduce((a, b) => a + b, 0) + (words.length - 1) * ss;
  let x = 960 - tot / 2;
  words.forEach((w, i) => {
    const at = TM.wva[i] ?? TM.wva[TM.wva.length - 1] + 0.4 * i, k = eOut(prog(t, at, at + 0.4)), last = i === words.length - 1;
    if (i > 0) text(g, sep, x - ss, 540, { size, weight: 400, align: 'left', fill: C.dim, a: k * (1 - out) });
    text(g, w, x, 540 + (1 - k) * 22, { size, weight: 700, align: 'left', fill: last ? C.blue : C.text, glow: last ? hexA(C.blue, 0.6) : null, a: k * (1 - out), blur: (1 - k) * 12 + out * 16 });
    x += ws[i] + ss;
  });
  const bk = eOut(prog(t, BREAK + 4.725, BREAK + 5.225));
  text(g, T.rushLine, 960, 640 + (1 - bk) * 18, { size: 42, weight: 500, fill: C.muted, a: bk * (1 - out) });
}

async function s15(g, t) {                       // the liquid logo reveal, the name, then what we make and the website
  const lt = t - L0, img = await logoImg(lt), WM = 156, GAP = 54;
  const MW = MAN.logo.w, MH = MAN.logo.h, MS = Math.min(371 / MH, 420 / MW);
  const [p1, p2] = CFG.brand.name, col = CFG.brand.colors;
  g.save(); g.font = `400 ${WM}px ${ROUND}`; let w1 = g.measureText(p1).width, w2 = g.measureText(p2 || '').width; g.restore();
  const fitK = Math.min(1, 1500 / (MW * MS + GAP + w1 + w2)), wm = WM * fitK; w1 *= fitK; w2 *= fitK;
  const total = MW * MS + GAP + w1 + w2, left = 960 - total / 2;
  const mv = eIO(prog(t, L0 + 2.55, L0 + 3.2)), s = lerp(Math.min(0.95, 560 / MH), MS, mv);
  const kx = lerp(960, left + MW * MS / 2, mv), ky = lerp(510, 470, mv);
  const rk = prog(t, HIT, HIT + 0.7);             // a bright ring where the drop lands
  if (rk > 0 && rk < 1) {
    g.save(); g.globalAlpha = (1 - rk) * 0.8; g.strokeStyle = C.cyan; g.lineWidth = 6 * (1 - rk); g.shadowColor = C.cyan; g.shadowBlur = 30;
    g.beginPath(); g.ellipse(960, 510, 60 + rk * 520, (60 + rk * 520) * 0.9, 0, 0, Math.PI * 2); g.stroke(); g.restore();
  }
  const wr = eOut(prog(t, L0 + 2.85, L0 + 3.45));  // the name wipes in as the mark slides left
  if (wr > 0) {
    const wx = left + MW * MS + GAP, y = 480, x = wx - 90 * (1 - wr);
    g.save(); g.beginPath(); g.rect(wx - 10, 300, (w1 + w2 + 40) * wr, 360); g.clip();
    g.font = `400 ${wm}px ${ROUND}`; g.textBaseline = 'middle'; g.textAlign = 'left'; g.shadowBlur = 40;
    let gr = g.createLinearGradient(x, y - 70, x + w1, y + 70); gr.addColorStop(0, col[0]); gr.addColorStop(1, col[1]);
    g.shadowColor = hexA(col[0], 0.65); g.fillStyle = gr; g.fillText(p1, x, y);
    if (p2) { gr = g.createLinearGradient(x + w1, y, x + w1 + w2, y); gr.addColorStop(0, col[2]); gr.addColorStop(1, col[3]);
      g.shadowColor = hexA(col[2], 0.55); g.fillStyle = gr; g.fillText(p2, x + w1, y); }
    g.restore();
  }
  const ox = MAN.logo.cx ?? 500, oy = MAN.logo.cy ?? 500;
  g.drawImage(img, kx - ox * s, ky - oy * s, 1000 * s, 1000 * s);
  const CH0 = L0 + 3.6, chips = T.chips || [], dots = [C.blue, C.cyan, C.orange, C.blue, C.cyan];
  g.save(); g.font = `600 30px ${SANS}`;
  const cws = chips.map(c => g.measureText(c).width + 70), tot = cws.reduce((a, b) => a + b, 0) + 20 * Math.max(0, chips.length - 1);
  let cx0 = 960 - tot / 2;
  chips.forEach((c, i) => {
    const k = eBack(prog(t, CH0 + i * 0.08, CH0 + 0.4 + i * 0.08), 1.5), cw = cws[i];
    if (k > 0.01) {
      g.save(); g.globalAlpha = clamp(k * 2); g.translate(cx0 + cw / 2, 750 + (1 - clamp(k)) * 24); g.scale(k, k);
      rr(g, -cw / 2, -31, cw, 62, 31); g.fillStyle = 'rgba(16,16,18,0.92)'; g.fill(); g.lineWidth = 1.5; g.strokeStyle = '#2e2e32'; g.stroke();
      g.beginPath(); g.arc(-cw / 2 + 28, 0, 7, 0, Math.PI * 2); g.fillStyle = dots[i % dots.length]; g.fill();
      g.fillStyle = C.text; g.textAlign = 'left'; g.textBaseline = 'middle'; g.fillText(c, -cw / 2 + 46, 2);
      g.restore();
    }
    cx0 += cw + 20;
  });
  g.restore();
  const uk = eOut(prog(t, CH0 + 0.6, CH0 + 1.05));
  if (CFG.brand.url) text(g, CFG.brand.url, 960, 860 + (1 - uk) * 16, { size: 40, weight: 500, fill: C.muted, a: uk, letter: 1 });
}

let g;
export async function render(t) {
  g.save(); g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.filter = 'none';
  background(g, t);
  for (const [a, b, fn] of SECTIONS) if (t >= a && t < b) { g.save(); await fn(g, t); g.restore(); }
  g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.filter = 'none'; g.globalCompositeOperation = 'source-over';
  const vg = g.createRadialGradient(960, 540, 560, 960, 540, 1200);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.55)');
  g.fillStyle = vg; g.fillRect(0, 0, W, H);
  g.restore();
}

const DEFAULT_TEXT = {
  typed: 'Every story', line: ['deserves to ', 'move.'], ring: ['Here are some of ', 'ours.'], eyebrow: 'SHOWREEL', subline: '',
  soundOn: 'Sound on', fullVideo: 'Full video · ', next: ['Your story', 'next.'], rush: ['Written', 'Voiced', 'Animated'],
  rushLine: 'all by our own team', chips: [],
};
export async function boot() {
  const c = document.getElementById('c');
  g = c.getContext('2d', { alpha: false });
  CFG = await (await fetch('/proj/promo.json')).json();
  MAN = await (await fetch('/proj/assets/manifest.json')).json();
  TM = await (await fetch('/proj/build/tm.json')).json();
  LEVELS = (await (await fetch('/proj/assets/bites/levels.json')).json()).levels || {};
  T = { ...DEFAULT_TEXT, ...(CFG.text || {}) };
  KM = CFG.lang === 'km';
  SANS = KM ? '"Kantumruy", "Helvetica Neue", sans-serif' : '"Helvetica Neue", Helvetica, Arial, sans-serif';
  DISPLAY = KM ? '"Koulen", "Kantumruy", sans-serif' : SANS;
  if (CFG.brand.font) ROUND = `"${CFG.brand.font}", ${ROUND}`;
  Object.assign(C, { blue: CFG.brand.accent || C.blue, cyan: CFG.brand.accent2 || C.cyan, orange: CFG.brand.warm || C.orange });
  N = MAN.works.length;
  SPOT_T = Array.from({ length: N }, (_, k) => B(5 + 3 * k));
  BREAK = B(5 + 3 * N); HIT = B(9 + 3 * N); L0 = HIT - 0.5; DUR = HIT + 6.425;
  GLOW = [[0, 0.12], [3.1, 0.12], [3.3, 0.3], [7.4, 0.3], [7.6, 0.6], [9.3, 0.5], [BREAK - 0.1, 0.5], [BREAK, 0.08], [BREAK + 1.8, 0.08],
    [BREAK + 1.95, 0.45], [HIT - 0.55, 0.45], [HIT - 0.05, 0.12], [HIT + 0.08, 0.8], [HIT + 1.6, 0.5], [DUR, 0.42]];
  let h = 0;
  SPOTS = MAN.works.map((w, k) => {
    const cw = CFG.works[k] || {};
    const side = w.vert ? 0 : (h++ % 2 ? -1 : 1);
    return { clip: w.clip, vert: w.vert, side, sound: w.sound, len: cw.length ?? w.len, num: pad(k + 1, 2), label: cw.label || '', title: cw.title || '', line: cw.line || '' };
  });
  const r = rng(21);
  RING = RING_POS.map(([X, Y], i) => { const si = MAN.ring[i % MAN.ring.length]; return { X, Y, si, vert: MAN.vertical_stills.includes(si), ry: (r() - 0.5) * 0.5, z0: 900 + r() * 900 }; });
  const rr2 = rng(808); RUSH = [];
  for (let i = 0; i < 22; i++) RUSH.push({ X: (rr2() - 0.5) * 2700, Y: (rr2() - 0.5) * 1500, Z: 400 + rr2() * 2900, ry: (rr2() - 0.5) * 0.7, clip: MAN.rush[i % MAN.rush.length] });
  SECTIONS = [[0, 3.4, s1], [3.2, 7.65, s2], [7.5, 9.5, s4],
    ...SPOT_T.map((s, k) => [s - 0.1, s + 3 * BAR + 0.05, (g2, t) => spot(g2, t, k)]),
    [BREAK - 0.075, BREAK + 1.925, s8], [BREAK + 1.775, HIT - 0.475, s9], [HIT - 0.575, 999, s15]];
  const dc = document.createElement('canvas'); dc.width = dc.height = 60; const dx = dc.getContext('2d');
  dx.fillStyle = 'rgba(255,255,255,0.10)'; dx.beginPath(); dx.arc(30, 30, 1.3, 0, Math.PI * 2); dx.fill();
  dotPat = g.createPattern(dc, 'repeat');
  await Promise.all([document.fonts.load(`500 60px "Helvetica Neue"`), document.fonts.load(`800 60px "Helvetica Neue"`), document.fonts.load(`400 60px ${ROUND}`),
    document.fonts.load(`500 60px "Kantumruy"`), document.fonts.load(`700 60px "Kantumruy"`), document.fonts.load(`400 60px "Koulen"`)]);
  await Promise.all([logoImg(4.99), stillImg(0)]);
  window.render = render;
  window.DUR = DUR;
}
