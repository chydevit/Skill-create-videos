// saas-promo scene: a ~10.8 s kinetic SaaS / startup promo, every frame drawn on one 1920x1080 canvas in headless Chrome.
//
//   0.00  scene 1  glyph flashes + neon shapes (purple / lime) on a dim dot-matrix glyph field
//   0.50  scene 2  the typed word with a cursor; a 3D swirl of cards (halftone first, then the real picture) orbits it
//   3.30  scene 3  painted meadow; cards slide in and build a bento wall; words type inside three cards; zoom into the last
//   6.45  scene 4  dark dot-wave field, a glowing gradient orb, the headline word by word, the subline wipes in
//   8.45  scene 5  glitch into the hero: long-exposure flower on a blue→orange sky, flying symbols, "From …" then "To …"
//
// Long mode (promo.json "chapters"): the same four scene types repeat as beats of 1.5 bars (finale 2 bars):
//   open → wall → orb (intro), then per chapter [open] → wall → orb, then the finale. With "music", the first cut
//   lands on the song's drop and every cut on its bar grid (assets.py measures bpm and drop: manifest "music").
// Each beat carries its own timings (T), texts (TX), colours (COL) and built pieces (L); use(beat) swaps them in.
// window.render(t) draws time t (s); window.DUR is the length; window.CUES / window.SECTIONS feed audio.py
// (render.mjs --cues writes them to build/cues.json); window.PREVIEW_TIMES are the stills for --preview.
// Inputs: /proj/promo.json and /proj/assets/manifest.json.
const W = 1920, H = 1080;
let X, CFG, MAN, TX, COL, T, FONT, DUR = 0, WALLBG = 'meadow';
let BEATS = [];
const L = {};
const CUES = [];
let BUF, BUF2, HALF;

/* ------------------------------------------------------------------ helpers */
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lin = (t, a, b) => clamp((t - a) / (b - a));
const mix = (a, b, p) => a + (b - a) * p;
const eo3 = x => 1 - (1 - x) ** 3;
const eio3 = x => (x < 0.5 ? 4 * x ** 3 : 1 - (-2 * x + 2) ** 3 / 2);
const eoX = x => (x >= 1 ? 1 : 1 - 2 ** (-10 * x));
const eoBack = x => { const c = 1.5; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2; };
function rng(seed) {
  let a = seed >>> 0;
  return () => { a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
const hash = (i, j = 0) => { let h = (Math.imul(i | 0, 374761393) + Math.imul(j | 0, 668265263)) | 0; h = Math.imul(h ^ (h >>> 13), 1274126177); return ((h ^ (h >>> 16)) >>> 0) / 4294967296; };
function surf(w, h) { const c = document.createElement('canvas'); c.width = Math.max(1, Math.round(w)); c.height = Math.max(1, Math.round(h)); return { c, g: c.getContext('2d', { willReadFrequently: false }) }; }
function reset(g) {
  g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.globalCompositeOperation = 'source-over'; g.filter = 'none';
  g.shadowColor = 'transparent'; g.shadowBlur = 0; g.shadowOffsetX = 0; g.shadowOffsetY = 0;
  g.textAlign = 'left'; g.textBaseline = 'alphabetic';
}
function clear(s) { reset(s.g); s.g.clearRect(0, 0, s.c.width, s.c.height); }
const font = (wt, px) => `${wt} ${Math.max(1, Math.round(px))}px ${FONT}`;
const SEG = new Intl.Segmenter(undefined, { granularity: 'grapheme' });
const graphemes = s => [...SEG.segment(String(s))].map(x => x.segment);
const splitWords = s => String(s).split(/\s+/).filter(Boolean);
const iw = img => img.naturalWidth || img.width, ih = img => img.naturalHeight || img.height;
function drawCover(g, img, x, y, w, h, fy = 0.35) {
  const s = Math.max(w / iw(img), h / ih(img)), sw = w / s, sh = h / s;
  g.drawImage(img, (iw(img) - sw) / 2, (ih(img) - sh) * fy, sw, sh, x, y, w, h);
}
function loadImg(src) { return new Promise((res, rej) => { const i = new Image(); i.onload = () => res(i); i.onerror = () => rej(new Error('cannot load ' + src)); i.src = src; }); }
// draw `src` (a full frame) blurred via a half-size buffer, so big blurs stay cheap
function soft(g, src, px, alpha = 1, extra = '') {
  reset(g); g.globalAlpha = alpha;
  if (px < 0.4 && !extra) { g.drawImage(src, 0, 0); g.globalAlpha = 1; return; }
  const h = HALF.g, pad = Math.min(60, px * 0.8);
  reset(h); h.clearRect(0, 0, W / 2, H / 2);
  h.filter = `${px >= 0.4 ? `blur(${(px / 2).toFixed(2)}px)` : ''} ${extra}`.trim();
  h.drawImage(src, -pad / 2, -pad / 2, W / 2 + pad, H / 2 + pad);
  h.filter = 'none';
  g.drawImage(HALF.c, 0, 0, W, H); g.globalAlpha = 1;
}
// type `str` one grapheme at a time from t0 (step s each), with a blinking cursor bar after the last letter
function typeText(g, str, t0, step, t, x, y, px, cursor) {
  const gs = graphemes(str), k = t < t0 ? 0 : Math.min(gs.length, Math.floor((t - t0) / step) + 1);
  const s = gs.slice(0, k).join('');
  if (s) g.fillText(s, x, y);
  const done = t > t0 + gs.length * step + 0.08;
  if (t >= t0 - 0.05 && (!done || (t * 2.4) % 1 < 0.62)) {
    const cw = s ? g.measureText(s).width : 0, keep = g.fillStyle;
    g.shadowColor = 'transparent'; g.fillStyle = cursor;
    g.fillRect(x + cw + px * 0.07, y - px * 0.8, Math.max(3, px * 0.075), px * 0.96);
    g.fillStyle = keep;
  }
}
function hexA(c, a) { const n = parseInt(String(c).replace('#', '').padEnd(6, '0').slice(0, 6), 16); return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`; }
function fitPx(text, wt, px, maxW) { X.font = font(wt, px); const w = X.measureText(text).width; return w > maxW ? px * maxW / w : px; }

/* ------------------------------------------------------------------ defaults */
const DEF_TEXT = {
  typed: 'SaaS.',
  glyphs: '#<@!?*',
  bento: ['Build', 'Ask an AI agent', 'a prototype'],
  headline: 'Make Your Product Impossible to Ignore',
  sub: 'Launch videos that explain your product, earn trust and turn visitors into users',
  from: 'From a rough idea',
  to: 'To a Launch Film',
  labels: ['Ask anything…', 'Approvals', 'Dashboard', 'Launch', 'Analytics', 'Forms'],
  url: '',
};
const DEF_COL = {
  neon: ['#b62bff', '#c8ff1f'],
  orb: ['#16e0c4', '#c4f53b', '#a54dff', '#6b3cff'],
  sky: ['#0d5fc8', '#3f8fe0', '#e9a96a', '#f2861e'],
  symbols: ['#ff6a00', '#2f8bff'],
  accent: '#4f7cff',
};

/* ------------------------------------------------------------------ timeline + sound cues */
function plan() {
  const tg = graphemes(TX.typed), hw = splitWords(TX.headline);
  const step = (s, total, max) => Math.min(max, total / Math.max(1, graphemes(s).length));
  T = {
    glyphEnd: 0.46, type: 0.5, typeStep: Math.min(0.12, 0.5 / Math.max(1, tg.length)),
    cloud: 0.3, cloudOut: 2.85, cut1: 3.3, stack: 3.32, grid: 3.58,
    w0: 4.3, w0Step: step(TX.bento[0], 0.5, 0.09), w1: 4.62, w1Step: step(TX.bento[1], 0.7, 0.07),
    swapA: 5.0, swapB: 5.32, w2: 5.48, w2Step: step(TX.bento[2], 0.42, 0.065), zoom: 5.98, cut2: 6.45,
    orb: 6.38, words: 6.72, wordStep: Math.min(0.14, 0.7 / Math.max(1, hw.length - 1)),
  };
  T.sub = T.words + (hw.length - 1) * T.wordStep + 0.2;
  T.out4 = Math.max(8.2, T.sub + 0.85); T.cut3 = T.out4 + 0.3;
  T.from = T.cut3 + 0.33; T.fromOut = T.cut3 + 0.85; T.to = T.cut3 + 1.05; T.end = T.cut3 + 2.35 + (TX.url ? 0.45 : 0);
}
const cue = (t, k, db, al = 'start', extra = {}) => CUES.push({ t: +t.toFixed(3), k, db, al, ...extra });
function cuesFor(B, next) {   // the sound cues of one beat (globals already swapped in with use(B))
  const v0 = B.i * 11;
  if (B.type === 'open') {
    for (let i = 0; B.t0 + 0.02 + i * 0.08 < T.glyphEnd; i++) cue(B.t0 + 0.02 + i * 0.08, 'glyph', -17, 'start', { v: i });
    L.neon.forEach((e, i) => { if (i % 3 === 0) cue(e.t0, 'blip', -31, 'start', { v: i + v0 }); });
    graphemes(TX.typed).forEach((_, i) => cue(T.type + i * T.typeStep, 'key', -14, 'start', { v: i + v0 }));
    cue(T.cloud + 0.32, 'whoosh', -21, 'peak', { v: B.i });
    if (B.first) cue(T.cut1 - 0.03, 'riser', -19, 'peak', { pre: 2.3 });
    cue(T.cut1 - 0.04, 'deepwhoosh', -17, 'peak', { v: B.i });
    cue(T.cut1, B.first ? 'impact' : 'hit', B.first ? -11 : -19, 'peak', { v: B.i });
  } else if (B.type === 'wall') {
    [0, 1, 2].forEach(i => cue(T.stack + 0.06 + i * 0.08, 'swish', -25, 'peak', { v: i + v0 }));
    L.slots.filter(sl => !sl.stack).forEach(sl => { if (sl.order % 2 === 0) cue(T.grid + sl.order * 0.04 + 0.12, 'tick', -29, 'start', { v: sl.order }); });
    [[TX.bento[0], T.w0, T.w0Step], [TX.bento[1], T.w1, T.w1Step], [TX.bento[2], T.w2, T.w2Step]].forEach(([str, t0, st], j) =>
      graphemes(str).forEach((_, i) => { if (st > 0.05 || i % 2 === 0) cue(t0 + i * st, 'key', -23, 'start', { v: i + j * 7 + v0 }); }));
    cue(T.swapA + 0.1, 'swish', -24, 'peak', { v: 3 + v0 }); cue(T.swapB + 0.1, 'swish', -24, 'peak', { v: 4 + v0 });
    cue(T.cut2 - 0.02, 'reverse', -17, 'peak', { pre: 0.9, v: B.i });
    cue(T.cut2, 'deepwhoosh', -18, 'peak', { v: B.i + 1 }); cue(T.cut2 + 0.03, 'boom', -15, 'peak', { v: B.i });
  } else if (B.type === 'orb') {
    splitWords(TX.headline).forEach((_, i) => cue(T.words + i * T.wordStep, 'tick', -27, 'start', { v: i + v0 }));
    cue(T.sub, 'sparkle', -26, 'start', { v: B.i });
    if (next && next.type !== 'finale') cue(T.cut3 - 0.02, 'reverse', -20, 'peak', { pre: 0.6, v: B.i + 1 });
  } else {
    cue(T.cut3 - 0.02, 'reverse', -19, 'peak', { pre: 0.7 });
    cue(T.cut3, 'glitch', -17, 'start', { max: 0.4 });
    cue(T.cut3 + 0.22, 'impact', -12, 'peak', { v: 1 }); cue(T.cut3 + 0.22, 'hit', -17, 'peak');
    cue(T.cut3 + 0.35, 'sparkle', -22, 'start', { v: 1 });
    splitWords(TX.from).forEach((_, i) => cue(T.from + i * 0.1, 'tick', -28, 'start', { v: i + 3 }));
    cue(T.to, 'boom', -13, 'peak'); cue(T.to, 'hit', -18, 'peak', { v: 1 });
    splitWords(TX.to).forEach((_, i) => cue(T.to + i * 0.15, 'tick', -27, 'start', { v: i + 9 }));
    if (L.logo) cue(T.to + 0.6, 'pop', -22);
    if (TX.url) cue(T.to + 0.5, 'tick', -24, 'start', { v: 2 });
  }
}

/* ------------------------------------------------------------------ beats: the timeline as a list of scenes */
const SPAN = { open: [null, 'cut1'], wall: ['cut1', 'cut2'], orb: ['cut2', 'cut3'], finale: ['cut3', 'end'] };
function mapT(N, type, t0, dur) {   // the classic timeline's times for one scene type, moved to t0 and stretched to dur
  const a = SPAN[type][0] ? N[SPAN[type][0]] : 0, b = N[SPAN[type][1]];
  const k = type === 'finale' ? 1 : dur / (b - a), out = {};
  for (const [key, v] of Object.entries(N)) out[key] = /Step$/.test(key) ? v * k : t0 + (v - a) * k;
  if (type === 'finale') out.end = t0 + dur;
  out.k = k;
  return out;
}
function use(B) { T = B.T; TX = B.TX; COL = B.COL; WALLBG = B.bg || 'meadow'; Object.assign(L, B.L || {}); }
const PICK = { open: ['glyphs', 'typedPx', 'neon', 'cloud'], wall: ['slots', 'zoomK', 'px0', 'px1', 'px2'], orb: ['hl'], finale: ['sym', 'fpx'] };
function beatSpecs() {
  if (!CFG.chapters?.length) {            // classic ~11 s: the template's four scenes, at their own lengths
    plan(); const N = T;
    return [{ type: 'open', t0: 0, dur: N.cut1, first: true }, { type: 'wall', t0: N.cut1, dur: N.cut2 - N.cut1, bg: CFG.wall },
      { type: 'orb', t0: N.cut2, dur: N.cut3 - N.cut2 }, { type: 'finale', t0: N.cut3, dur: N.end - N.cut3 }];
  }
  const bar = MAN.music?.bpm ? 240 / MAN.music.bpm : 2.2, specs = []; let t = 0;
  const add = (type, bars, o = {}) => { specs.push({ type, t0: t, dur: bars * bar, ...o }); t += bars * bar; };
  add('open', 1.5, { first: true }); add('wall', 1.5, { bg: CFG.wall }); add('orb', 1.5);
  for (const ch of CFG.chapters) {
    const o = { ch, tag: ch.tag };
    if (ch.typed) add('open', 1.5, o);
    add('wall', 1.5, { ...o, bg: ch.wall }); add('orb', 1.5, o);
  }
  add('finale', 2);
  return specs;
}
function buildBeats(users, phs, classicPool) {
  const baseTX = TX, baseCOL = COL;
  BEATS = beatSpecs().map((B, i) => ({ ...B, i }));
  for (const B of BEATS) {
    const ch = B.ch || {};
    B.TX = { ...baseTX };
    for (const k of ['typed', 'headline', 'sub', 'labels']) if (ch[k]) B.TX[k] = ch[k];
    B.TX.bento = [0, 1, 2].map(i => (ch.bento || [])[i] || baseTX.bento[i]);
    B.COL = { ...baseCOL, ...(ch.colors || {}), ...(ch.orb ? { orb: ch.orb } : {}) };
    TX = B.TX; COL = B.COL; plan();
    B.T = mapT(T, B.type, B.t0, B.dur);
    if (B.type === 'open' && !B.first) { B.T.glyphEnd = B.t0; B.T.type = B.t0 + 0.35; }   // chapter openers: no glyph flashes
    T = B.T; window.bootStage = `beat ${B.i} ${B.type}`;
    if (B.type === 'open') {
      L.glyphs = graphemes(TX.glyphs); L.typedPx = fitPx(TX.typed, 500, 132, 900);
      buildNeon(B.t0, T.k, B.first ? 38 : 22, 5 + B.i);
      buildCloud(B.tag ? poolFor(users, phs, B.tag) : classicPool, 21 + B.i);
    }
    if (B.type === 'wall') {
      const wall = users.filter(c => c.wall);
      buildSlots(B.tag ? [...wall.filter(c => c.tag === B.tag), ...wall.filter(c => c.tag !== B.tag)] : wall, B.tag);
    }
    if (B.type === 'orb') buildHeadline();
    if (B.type === 'finale') buildFinaleText();
    B.L = Object.fromEntries(PICK[B.type].map(k => [k, L[k]]));
  }
  BEATS[BEATS.length - 1].last = true;
  const last = BEATS[BEATS.length - 1];
  DUR = last.t0 + last.dur;
  BEATS.forEach((B, i) => { use(B); cuesFor(B, BEATS[i + 1]); });
  CUES.sort((a, b) => a.t - b.t);
}
function poolFor(users, phs, tag) {   // a chapter's swirl: its own pictures twice as often as the rest
  const mine = users.filter(c => c.tag === tag), rest = users.filter(c => c.tag !== tag), pool = [];
  for (let i = 0; pool.length < 18; i++) {
    if (mine.length) pool.push(mine[i % mine.length]);
    if (i % 2 === 1) pool.push(rest.length ? rest[((i - 1) / 2) % rest.length] : phs[i % phs.length]);
    if (!mine.length && !rest.length) pool.push(phs[i % phs.length]);
  }
  return pool;
}

/* ------------------------------------------------------------------ placeholder UI cards (used when the user gave too few pictures) */
function placeholder(kind, w, h, label, seed) {
  const s = surf(w, h), g = s.g, r = rng(seed), u = Math.min(w, h);
  const lg = (x0, y0, x1, y1, stops) => { const q = g.createLinearGradient(x0, y0, x1, y1); stops.forEach(([o, c]) => q.addColorStop(o, c)); return q; };
  const blob = (x, y, rad, col) => { const q = g.createRadialGradient(x, y, 0, x, y, rad); q.addColorStop(0, col); q.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = q; g.fillRect(0, 0, w, h); };
  const center = (txt, px, col, wt = 600) => { g.font = font(wt, fitPx(txt, wt, px, w * 0.8)); g.fillStyle = col; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(txt, w / 2, h / 2); g.textAlign = 'left'; };
  switch (kind) {
    case 'search': {
      g.fillStyle = lg(0, 0, w * 0.35, h, [[0, '#18257a'], [0.55, '#4a62de'], [1, '#f0bcd2']]); g.fillRect(0, 0, w, h);
      const pw = w * 0.74, ph = Math.max(26, u * 0.17), px = (w - pw) / 2, py = h * 0.55 - ph / 2;
      g.fillStyle = 'rgba(255,255,255,0.9)'; g.beginPath(); g.roundRect(px, py, pw, ph, ph / 2); g.fill();
      g.fillStyle = '#8a8fa3'; g.font = font(400, ph * 0.38); g.textBaseline = 'middle'; g.fillText(label, px + ph * 0.5, py + ph / 2);
      g.fillStyle = '#3b5bff'; g.beginPath(); g.arc(px + pw - ph / 2, py + ph / 2, ph * 0.32, 0, 7); g.fill();
      break;
    }
    case 'form': {
      g.fillStyle = '#f6f5f1'; g.fillRect(0, 0, w, h);
      g.fillStyle = '#23242a'; g.font = font(600, u * 0.11); g.textBaseline = 'top'; g.fillText(label, w * 0.08, h * 0.12);
      g.fillStyle = '#dcdbd5'; for (let i = 0; i < 3; i++) g.fillRect(w * 0.08, h * (0.4 + i * 0.1), w * (0.55 - i * 0.12), u * 0.028);
      g.strokeStyle = '#d6d5cf'; g.lineWidth = Math.max(1.5, u * 0.008); g.beginPath(); g.roundRect(w * 0.08, h * 0.72, w * 0.6, h * 0.15, u * 0.04); g.stroke();
      g.fillStyle = '#3b6bff'; g.beginPath(); g.arc(w * 0.85, h * 0.795, u * 0.065, 0, 7); g.fill();
      break;
    }
    case 'aurora':
      g.fillStyle = '#231852'; g.fillRect(0, 0, w, h);
      blob(w * 0.25, h * 0.45, u * 0.95, 'rgba(118,86,255,0.95)'); blob(w * 0.78, h * 0.6, u * 0.7, 'rgba(232,222,255,0.85)');
      center(label, u * 0.16, '#ffffff'); break;
    case 'peach':
      g.fillStyle = lg(0, 0, 0, h, [[0, '#f4b48c'], [0.55, '#e9b6c5'], [1, '#93b8f3']]); g.fillRect(0, 0, w, h);
      blob(w * 0.5, h * 0.55, u * 0.42, 'rgba(255,255,255,0.95)'); break;
    case 'pill': {
      g.fillStyle = '#050507'; g.fillRect(0, 0, w, h);
      const pw = u * 0.2, ph = h * 0.62;
      g.shadowColor = 'rgba(255,190,215,0.9)'; g.shadowBlur = u * 0.25;
      g.fillStyle = lg(0, h * 0.2, 0, h * 0.8, [[0, '#ffffff'], [1, '#ffb0c8']]);
      g.beginPath(); g.roundRect(w / 2 - pw / 2, h / 2 - ph / 2, pw, ph, pw / 2); g.fill(); g.shadowColor = 'transparent';
      break;
    }
    case 'chart': {
      g.fillStyle = lg(0, 0, 0, h, [[0, '#0d1322'], [1, '#18233f']]); g.fillRect(0, 0, w, h);
      g.fillStyle = '#8e9ab8'; g.font = font(500, u * 0.08); g.textBaseline = 'top'; g.fillText(label, w * 0.08, h * 0.08);
      const n = 9, bw = w * 0.84 / n;
      for (let i = 0; i < n; i++) { const bh = h * (0.18 + 0.5 * r()); g.fillStyle = i === 6 ? '#5b8cff' : 'rgba(255,255,255,0.85)'; g.fillRect(w * 0.08 + i * bw + bw * 0.2, h * 0.9 - bh, bw * 0.6, bh); }
      break;
    }
    case 'cream':
      g.fillStyle = '#efebe2'; g.fillRect(0, 0, w, h); blob(w * 0.5, h * 0.5, u * 0.16, 'rgba(105,145,255,0.95)'); break;
    case 'dark': {
      g.fillStyle = lg(0, 0, 0, h, [[0, '#0a0f1e'], [1, '#162248']]); g.fillRect(0, 0, w, h);
      g.strokeStyle = 'rgba(150,180,255,0.9)'; g.lineWidth = Math.max(2, u * 0.012); g.shadowColor = '#7aa2ff'; g.shadowBlur = u * 0.08;
      g.beginPath(); g.ellipse(w / 2, h * 1.25, w * 0.75, h * 0.62, 0, Math.PI, 2 * Math.PI); g.stroke(); g.shadowColor = 'transparent';
      center(label, u * 0.1, '#e8ecff', 500); break;
    }
    case 'letter': {
      g.fillStyle = '#5a3df0'; g.fillRect(0, 0, w, h);
      g.fillStyle = '#e5532d'; g.beginPath(); g.arc(w * 0.55, h * 0.5, u * 0.36, 0, 7); g.fill();
      g.font = font(700, u * 0.3); g.fillStyle = '#fff'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(graphemes(label)[0] || 'A', w * 0.55, h * 0.52); g.textAlign = 'left';
      break;
    }
    default: { // 'mountain'
      g.fillStyle = lg(0, 0, 0, h, [[0, '#7fb0e6'], [0.65, '#f3d9c4'], [1, '#e7b48f']]); g.fillRect(0, 0, w, h);
      blob(w * 0.7, h * 0.35, u * 0.3, 'rgba(255,248,230,0.95)');
      const ridge = (base, amp, col, seed2) => { const q = rng(seed2); g.fillStyle = col; g.beginPath(); g.moveTo(0, h); for (let x = 0; x <= w; x += w / 24) g.lineTo(x, h * base - amp * h * (0.5 + 0.5 * Math.sin(x / w * 7 + q() * 6)) * q()); g.lineTo(w, h); g.fill(); };
      ridge(0.68, 0.3, '#5d6f9e', seed + 1); ridge(0.82, 0.18, '#34446c', seed + 2); ridge(0.95, 0.08, '#1e2946', seed + 3);
    }
  }
  return s.c;
}
const PH_KINDS = ['search', 'aurora', 'cream', 'chart', 'peach', 'form', 'pill', 'dark', 'letter', 'mountain'];

/* ------------------------------------------------------------------ build: scene 1-2 */
function buildGrid() {
  const gw = W + 240, gh = H + 240, cell = 52, r = rng(11);
  const base = surf(gw, gh), hot = [surf(gw, gh), surf(gw, gh), surf(gw, gh)];
  const chars = [...'AEFZKRXH#<>@!?*+=%&$:;/{}[]▷◁□○◇☰✱✦⌘∞≡'];
  for (const s of [base, ...hot]) { s.g.fillStyle = '#fff'; s.g.textAlign = 'center'; s.g.textBaseline = 'middle'; }
  for (let y = cell / 2; y < gh; y += cell) for (let x = cell / 2; x < gw; x += cell) {
    if (r() < 0.42) continue;
    const ch = chars[Math.floor(r() * chars.length)], sz = Math.round(22 + r() * 18);
    base.g.font = `700 ${sz}px Menlo, "Courier New", monospace`; base.g.fillText(ch, x, y);
    if (r() < 0.2) { const s = hot[Math.floor(r() * 3)].g; s.font = base.g.font; s.fillText(ch, x, y); }
  }
  const pat = surf(4, 4); pat.g.fillStyle = '#fff'; pat.g.fillRect(0, 0, 2, 2);   // dot-matrix look
  for (const s of [base, ...hot]) { s.g.globalCompositeOperation = 'destination-in'; s.g.fillStyle = s.g.createPattern(pat.c, 'repeat'); s.g.fillRect(0, 0, gw, gh); s.g.globalCompositeOperation = 'source-over'; }
  L.grid = base.c; L.hot = hot.map(s => s.c);
}
function buildNeon(base = 0, stretch = 1, n = 38, seed = 5) {
  const r = rng(seed), ev = [];
  for (let i = 0; i < n; i++) {
    const t0 = base + stretch * 1.72 * r() ** 1.35, d = 0.1 + r() * 0.3;
    let x, y; do { x = 60 + r() * (W - 120); y = 50 + r() * (H - 100); } while (Math.abs(x - 960) < 380 && Math.abs(y - 540) < 200);
    const k = r(), kind = k < 0.32 ? 'star' : k < 0.58 ? 'hbar' : k < 0.8 ? 'vbar' : 'sq';
    const e = { t0, d, x, y, kind, col: r() < 0.55 ? COL.neon[0] : COL.neon[1], rot: r() < 0.8 ? 0 : (r() - 0.5) * 0.3 };
    if (kind === 'star') e.s = 26 + r() * 50;
    if (kind === 'hbar') { e.w = 110 + r() * 130; e.h = 24 + r() * 26; }
    if (kind === 'vbar') { e.w = 26 + r() * 32; e.h = 90 + r() * 110; }
    if (kind === 'sq') { e.w = e.h = 36 + r() * 56; }
    ev.push(e);
  }
  L.neon = ev.sort((a, b) => a.t0 - b.t0);
}
function halftone(src) {
  const w = src.width, h = src.height, cell = 7;
  const d = src.getContext('2d').getImageData(0, 0, w, h).data;
  const o = surf(w, h); o.g.fillStyle = '#0b0e0b'; o.g.fillRect(0, 0, w, h);
  for (let y = 0; y < h; y += cell) for (let x = 0; x < w; x += cell) {
    const i = (Math.min(h - 1, y + 3) * w + Math.min(w - 1, x + 3)) * 4, R = d[i], G = d[i + 1], B = d[i + 2];
    const lum = (0.3 * R + 0.59 * G + 0.11 * B) / 255;
    o.g.fillStyle = `rgb(${Math.round(R * 0.75 + 45)},${Math.round(G * 0.8 + 48)},${Math.round(B * 0.65 + 35)})`;
    o.g.beginPath(); o.g.arc(x + cell / 2, y + cell / 2, cell * 0.56 * Math.sqrt(lum) + 0.5, 0, 6.283); o.g.fill();
  }
  return o.c;
}
function buildCloud(pool, seed = 21) {
  const r = rng(seed), n = 26; L.cloud = [];
  for (let i = 0; i < n; i++) {
    const card = pool[i % pool.length], asp = clamp(card.w / card.h, 0.75, 1.45), base = 118 + r() * 72;
    const w = base * Math.sqrt(asp), h = base / Math.sqrt(asp);
    const th = surf(w * 1.6, h * 1.6); drawCover(th.g, card.img, 0, 0, th.c.width, th.c.height);
    L.cloud.push({ th: th.c, ht: halftone(th.c), w, h, a: (i / n) * Math.PI * 2 + (r() - 0.5) * 0.35, R: 390 + r() * 170, yo: (r() - 0.5) * 90,
      ph: r() * 6.28, t0: T.cloud + i * 0.022 + r() * 0.08, dither: r() < 0.4 ? 0.8 + r() * 0.9 : 0.3 });
  }
}

/* ------------------------------------------------------------------ build: scene 3 */
const SLOTS = [ // x, y, w, h inside a 1600 x 922 box, role, flag
  [0, 0, 610, 200, 'type'],            // the white card: word 3 types here, then the camera zooms into it
  [628, 0, 380, 200, 'img'],
  [1026, 0, 300, 200, 'img'],
  [1344, 0, 256, 200, 'img', 'stack'],
  [0, 218, 610, 440, 'hero'],          // picture + word 1
  [628, 218, 380, 704, 'glass'],       // tall glass card, word 2 typed vertically
  [1026, 218, 300, 440, 'img', 'swapA'],
  [1344, 218, 256, 300, 'img', 'stack'],
  [0, 676, 296, 246, 'img'],
  [314, 676, 296, 246, 'img', 'swapB'],
  [1026, 676, 300, 246, 'img'],
  [1344, 536, 256, 386, 'img', 'stack'],
];
function buildSlots(users, tag = null) {
  const left = users.slice(), ox = 160, oy = 87; let ph = 0;
  const hi = left.findIndex(c => c.w / c.h >= 1.2);                 // the big hero card: first landscape picture in the list
  const heroImg = hi >= 0 ? left.splice(hi, 1)[0].img : null;
  const take = asp => {
    if (!left.length) return null;
    const mine = tag && left.some(c => c.tag === tag);        // a chapter's own pictures first, then the rest
    let bi = 0, bd = 1e9; left.forEach((c, i) => { if (mine && c.tag !== tag) return; const d = Math.abs(Math.log(c.w / c.h / asp)); if (d < bd) { bd = d; bi = i; } });
    return left.splice(bi, 1)[0].img;
  };
  const fallback = (w, h, kind) => { ph++; return placeholder(kind || PH_KINDS[ph % PH_KINDS.length], w * 1.5, h * 1.5, TX.labels[ph % TX.labels.length], 100 + ph); };
  L.slots = SLOTS.map(([x, y, w, h, role, flag], i) => {
    const s = { i, x: ox + x, y: oy + y, w, h, cx: ox + x + w / 2, cy: oy + y + h / 2, role, stack: flag === 'stack' };
    if (role === 'hero') s.img = heroImg || take(w / h) || fallback(w, h, 'mountain');
    if (role === 'img') s.img = take(w / h) || fallback(w, h);
    if (flag === 'swapA' || flag === 'swapB') { s.swapAt = flag === 'swapA' ? T.swapA : T.swapB; s.img2 = take(w / h) || fallback(w, h); }
    return s;
  });
  L.slots.filter(s => s.stack).forEach((s, k) => { s.si = k; });
  L.slots.filter(s => !s.stack).sort((a, b) => (b.cx + b.cy) - (a.cx + a.cy)).forEach((s, k) => { s.order = k; });
  const s0 = L.slots[0];
  L.zoomK = W * 1.3 / s0.w;
  L.px0 = fitPx(TX.bento[0], 600, 84, L.slots[4].w - 90);
  L.px1 = fitPx(TX.bento[1], 500, 62, L.slots[5].h - 190);
  L.px2 = fitPx(TX.bento[2], 500, 64, s0.w - 110);
}
function buildMeadow() {
  const MW = 2300, MH = 1300, r = rng(31);
  const sky = surf(MW, MH), g = sky.g;
  let q = g.createLinearGradient(0, 0, 0, MH * 0.62);
  q.addColorStop(0, '#2c6fcf'); q.addColorStop(0.45, '#6aa6e6'); q.addColorStop(0.8, '#b9d6f2'); q.addColorStop(1, '#eaf1f8');
  g.fillStyle = q; g.fillRect(0, 0, MW, MH);
  q = g.createRadialGradient(MW * 0.22, MH * 0.06, 0, MW * 0.22, MH * 0.06, 950); q.addColorStop(0, 'rgba(255,255,255,0.5)'); q.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = q; g.fillRect(0, 0, MW, MH);
  const cl = surf(MW + 300, MH * 0.62), c = cl.g;
  for (let k = 0; k < 9; k++) {
    const cx = (k + 0.25 + r() * 0.5) * (MW + 300) / 9, cy = 150 + r() * 360, sw = 170 + r() * 250, sh = 55 + r() * 70;
    for (let i = 0; i < 46; i++) {
      const dx = (r() - 0.5) * 2, px = cx + dx * sw, py = cy - r() * sh * (1 - Math.abs(dx) * 0.6), rad = 26 + r() * 70 * (1 - Math.abs(dx) * 0.6);
      const pink = py > cy - sh * 0.25, rg = c.createRadialGradient(px, py, 0, px, py, rad);
      rg.addColorStop(0, pink ? 'rgba(250,220,236,0.85)' : 'rgba(255,255,255,0.95)'); rg.addColorStop(0.6, pink ? 'rgba(244,208,230,0.45)' : 'rgba(255,255,255,0.55)'); rg.addColorStop(1, 'rgba(255,255,255,0)');
      c.fillStyle = rg; c.beginPath(); c.arc(px, py, rad, 0, 7); c.fill();
    }
  }
  const hl = surf(MW, MH), h = hl.g;
  const ridge = (base, amps, seed) => { const rr = rng(seed); const ws = amps.map(a => [a, 0.0014 + rr() * 0.004, rr() * 6.28]); return x => base + ws.reduce((s, [a, f, p]) => s + a * Math.sin(x * f + p), 0); };
  const layer = (fy, stops, grassN, grassLen) => {
    h.beginPath(); h.moveTo(0, MH); for (let x = 0; x <= MW; x += 6) h.lineTo(x, fy(x)); h.lineTo(MW, MH); h.closePath();
    const gq = h.createLinearGradient(0, fy(MW / 2) - 90, 0, MH); stops.forEach(([o, col]) => gq.addColorStop(o, col)); h.fillStyle = gq; h.fill();
    for (let i = 0; i < grassN; i++) {
      const x = r() * MW, y0 = fy(x), y = y0 + 3 + r() * (MH - y0), depth = (y - y0) / (MH - y0 + 1), len = grassLen * (0.35 + depth * 1.5) * (0.5 + r());
      h.strokeStyle = `hsl(${88 + r() * 28},${52 + r() * 28}%,${24 + r() * 32}%)`; h.lineWidth = 0.8 + depth * 2.2;
      h.beginPath(); h.moveTo(x, y); h.lineTo(x + (r() - 0.5) * len * 0.5, y - len); h.stroke();
    }
  };
  const far = ridge(MH * 0.555, [26, 14, 8], 3), mid = ridge(MH * 0.615, [38, 20, 10], 4), near = ridge(MH * 0.7, [44, 22, 9], 5);
  layer(far, [[0, '#93bcab'], [1, '#6f9f86']], 0, 0);
  q = h.createLinearGradient(0, MH * 0.5, 0, MH * 0.66); q.addColorStop(0, 'rgba(235,242,248,0)'); q.addColorStop(0.5, 'rgba(235,242,248,0.35)'); q.addColorStop(1, 'rgba(235,242,248,0)');
  h.fillStyle = q; h.fillRect(0, MH * 0.5, MW, MH * 0.16);
  layer(mid, [[0, '#64b24b'], [1, '#3f8c2e']], 5000, 5);
  layer(near, [[0, '#55c437'], [0.5, '#3aa526'], [1, '#2a861c']], 16000, 14);
  for (let i = 0; i < 700; i++) {
    const x = r() * MW, y0 = near(x), y = y0 + (MH - y0) * (0.3 + 0.7 * r()), d = (y - y0) / (MH - y0);
    h.fillStyle = r() < 0.75 ? 'rgba(255,255,250,0.92)' : (r() < 0.5 ? '#ffd9f0' : '#fff3a0');
    h.beginPath(); h.arc(x, y, 0.8 + d * 3.4 * r(), 0, 7); h.fill();
  }
  L.sky = sky.c; L.clouds = cl.c; L.hills = hl.c;
  L.birds = Array.from({ length: 10 }, () => ({ x: r() * W, y: 70 + r() * 300, vx: -(25 + r() * 40), s: 9 + r() * 8, fr: 9 + r() * 5, ph: r() * 6.28 }));
  L.flies = Array.from({ length: 3 }, (_, i) => ({ x: [260, 1650, 420][i], y: 820 + r() * 140, ph: r() * 6.28 }));
}

/* ------------------------------------------------------------------ build: scene 4-5 */
function buildDots() {
  const sp = 9, pts = [];
  for (let y = 4, j = 0; y < H; y += sp, j++) for (let x = (j % 2) * sp / 2; x < W; x += sp) pts.push(x, y);
  L.dots = new Float32Array(pts);
  L.orbBuf = surf(640, 640);
}
function buildHeadline() {
  const hw = splitWords(TX.headline), r = 190, gap = 50, margin = 150;
  let px = CFG.lang === 'km' ? 56 : 64, spx = CFG.lang === 'km' ? 22 : 24;
  const measure = () => {
    X.font = font(500, px); const sw = X.measureText(' ').width;
    let x = 0; const words = hw.map(s => { const o = { s, x }; x += X.measureText(s).width + sw; return o; });
    X.font = font(400, spx); return { words, textW: x - sw, subW: X.measureText(TX.sub).width };
  };
  let m = measure(); const avail = W - 2 * margin - 2 * r - gap;
  if (Math.max(m.textW, m.subW) > avail) { const k = avail / Math.max(m.textW, m.subW); px *= k; spx *= k; m = measure(); }
  const blockW = 2 * r + gap + Math.max(m.textW, m.subW), ox = (W - blockW) / 2 + r;
  L.hl = { ...m, px, spx, r, ox, tx: ox + r + gap };
}
function buildFlower() {
  L.fb = surf(W / 2, H / 2); L.fb2 = surf(W / 2, H / 2);
  const P = [[-60, 560, 118], [57, 540, 118], [-31, 690, 128], [27, 670, 128], [-6, 730, 116], [-43, 440, 146], [38, 430, 146], [9, 410, 136]];
  L.petals = P.map(([a, len, w], i) => ({ a, len, w, ph: i * 1.7, echo: [[0.1, 0.1], [-0.08, 0.12], [0.045, 0.22], [0, 0.9]] }));
}
function buildFinaleText() {
  const r = rng(77), chars = [...'!@#$%*?<>+^&~/'];
  L.sym = Array.from({ length: 30 }, (_, i) => ({
    ch: i % 9 === 0 ? '✱' : chars[Math.floor(r() * chars.length)], col: COL.symbols[i % 2],
    x0: 900 + (r() - 0.5) * 760, y0: 470 + (r() - 0.5) * 440, vx: (r() - 0.5) * 420, vy: (r() - 0.5) * 300 - 40,
    rot: (r() - 0.5) * 0.8, vr: (r() - 0.5) * 4, sz: i % 9 === 0 ? 90 + r() * 30 : 30 + r() * 44,
    t0: T.cut3 + 0.15 + r() * 0.8, life: 0.45 + r() * 0.5,
  }));
  const fx = CFG.lang === 'km' ? 70 : 80;
  L.fpx = Math.min(fitPx(TX.from, 600, fx, W * 0.8), fitPx(TX.to, 600, fx, W * 0.8));
}

/* ------------------------------------------------------------------ scene 1-2: glyphs, neon, typed word, card swirl */
function star(g, s) { const k = s * 0.12; g.beginPath(); g.moveTo(0, -s); g.quadraticCurveTo(k, -k, s, 0); g.quadraticCurveTo(k, k, 0, s); g.quadraticCurveTo(-k, k, -s, 0); g.quadraticCurveTo(-k, -k, 0, -s); g.fill(); }
function drawNeon(g, t) {
  for (const e of L.neon) {
    if (t < e.t0 || t > e.t0 + e.d) continue;
    const p = (t - e.t0) / e.d, a = p < 0.12 ? p / 0.12 : p > 0.8 ? (1 - p) / 0.2 : 1;
    g.save(); g.translate(e.x, e.y); g.rotate(e.rot); g.fillStyle = e.col;
    for (const [alpha, blur] of [[a, 60], [a * 0.6, 0]]) {
      g.globalAlpha = alpha; g.shadowColor = blur ? e.col : 'transparent'; g.shadowBlur = blur;
      if (e.kind === 'star') star(g, e.s); else g.fillRect(-e.w / 2, -e.h / 2, e.w, e.h);
      g.globalCompositeOperation = 'lighter';
    }
    g.restore();
  }
}
function drawTypedWord(g, t) {
  if (t < T.type - 0.05) return;
  const px = L.typedPx; g.font = font(500, px); g.fillStyle = '#ffffff'; g.textBaseline = 'alphabetic'; g.textAlign = 'left';
  g.shadowColor = 'rgba(0,0,0,0.85)'; g.shadowBlur = 40;
  const full = g.measureText(TX.typed).width;
  typeText(g, TX.typed, T.type, T.typeStep, t, 960 - full / 2, 540 + px * 0.36, px, '#ffffff');
}
function drawCloud(g, t) {
  const F = 1000, out = lin(t, T.cloudOut, T.cut1), q = out * out * out;
  const spin = 0.75 * t + 2.4 * Math.max(0, t - T.cloudOut) ** 2;
  const cx = 960 + 40 * Math.sin(t * 0.8), cy = 540 + 22 * Math.sin(t * 0.6 + 1);
  const items = [];
  for (const c of L.cloud) {
    const life = t - c.t0; if (life < 0) continue;
    const pin = eoX(clamp(life / 0.7)), a = c.a + spin, R = c.R + 25 * Math.sin(t * 1.3 + c.ph);
    let x = R * Math.cos(a) * 1.12, y = R * Math.sin(a) * 0.5 + c.yo, z = -R * Math.sin(a) * 0.7 + (1 - pin) * 2600;
    z -= q * 1500; x *= 1 + q * 1.6; y *= 1 + q * 1.6;
    if (F + z < 60) continue;
    const k = F / (F + z);
    items.push({ c, sx: cx + x * k, sy: cy + y * k, k, z, life });
  }
  items.sort((p, q2) => q2.z - p.z);
  for (const { c, sx, sy, k, z, life } of items) {
    const w = c.w * k, h = c.h * k, x = sx - w / 2, y = sy - h / 2;
    const real = lin(life, c.dither * 0.6, c.dither);
    if (real < 1) { g.globalAlpha = 1; g.drawImage(c.ht, x, y, w, h); }
    if (real > 0) { g.globalAlpha = real; g.drawImage(c.th, x, y, w, h); }
    g.globalAlpha = 1;
    if (z > 0) { g.fillStyle = `rgba(0,0,0,${clamp(z / 900) * 0.45})`; g.fillRect(x, y, w, h); }
  }
}
function drawIntro(g, t) {
  reset(g); g.fillStyle = '#020203'; g.fillRect(0, 0, W, H);
  const dx = -110 + 25 * Math.sin(t * 0.5), dy = -110 - t * 8;
  g.globalAlpha = 0.3; g.drawImage(L.grid, dx, dy);
  g.globalAlpha = 0.55; g.drawImage(L.hot[Math.floor(t * 14) % 3], dx, dy); g.globalAlpha = 1;
  drawNeon(g, t);
  drawCloud(g, t);
  if (t < T.glyphEnd) {
    const i = Math.floor(t / 0.08), ch = L.glyphs[i % L.glyphs.length];
    g.font = font(400, 190); g.fillStyle = '#fff'; g.textAlign = 'center'; g.textBaseline = 'alphabetic';
    g.fillText(ch, 960 + (hash(i, 1) - 0.5) * 90, 540 + 66 + (hash(i, 2) - 0.5) * 60); g.textAlign = 'left';
  }
  drawTypedWord(g, t);
}

/* ------------------------------------------------------------------ scene 3: meadow + bento wall */
function camMeadow(t) {
  const base = mix(0.95, 1.035, eio3(lin(t, T.cut1, T.zoom)));
  let cx = 960 + mix(-14, 14, lin(t, T.cut1, T.zoom)), cy = 548, k = base;
  const z = lin(t, T.zoom, T.cut2 + 0.05) ** 3;
  if (z > 0) { const s0 = L.slots[0]; cx = mix(cx, s0.cx, z); cy = mix(cy, s0.cy, z); k = base * Math.exp(Math.log(L.zoomK / base) * z); }
  return { cx, cy, k, z };
}
function drawBirds(g, t) {
  g.strokeStyle = '#1b2430'; g.lineCap = 'round';
  for (const b of L.birds) {
    const x = (((b.x + b.vx * t) % (W + 200)) + W + 200) % (W + 200) - 100, y = b.y + 14 * Math.sin(t * 0.9 + b.ph), f = Math.sin(t * b.fr + b.ph), s = b.s;
    g.lineWidth = s * 0.17; g.beginPath(); g.moveTo(x - s, y - f * s * 0.5); g.quadraticCurveTo(x - s * 0.4, y - s * 0.3, x, y); g.quadraticCurveTo(x + s * 0.4, y - s * 0.3, x + s, y - f * s * 0.5); g.stroke();
  }
  for (const b of L.flies) {
    const x = b.x + 40 * Math.sin(0.9 * t + b.ph), y = b.y + 22 * Math.sin(1.7 * t + b.ph), o = Math.abs(Math.sin(t * 14 + b.ph));
    g.fillStyle = '#3c6fe2';
    for (const sd of [-1, 1]) { g.beginPath(); g.ellipse(x + sd * 6 * o, y, 7 * o + 1, 9, sd * 0.4, 0, 7); g.fill(); }
  }
}
function drawGlass(g, x, y, w, h, t) {
  let q = g.createLinearGradient(0, y, 0, y + h); q.addColorStop(0, '#6f9cee'); q.addColorStop(0.55, '#a9c6f6'); q.addColorStop(1, '#f2c4bb');
  g.fillStyle = q; g.fillRect(x, y, w, h);
  const pw = w * 0.62, px = -pw / 2, py = y + 26, ph = h - 52;
  q = g.createLinearGradient(px, 0, px + pw, 0); q.addColorStop(0, 'rgba(255,255,255,0.12)'); q.addColorStop(0.5, 'rgba(255,255,255,0.55)'); q.addColorStop(1, 'rgba(255,255,255,0.12)');
  g.fillStyle = q; g.beginPath(); g.roundRect(px, py, pw, ph, pw / 2); g.fill();
  g.strokeStyle = 'rgba(255,255,255,0.75)'; g.lineWidth = 2; g.stroke();
  g.strokeStyle = '#ffffff'; g.lineWidth = 3.5; g.beginPath(); g.moveTo(-16, y + h - 82); g.lineTo(16, y + h - 82); g.moveTo(0, y + h - 98); g.lineTo(0, y + h - 66); g.stroke();
  g.save(); g.rotate(-Math.PI / 2);
  const px1 = L.px1; g.font = font(500, px1); g.fillStyle = '#ffffff'; g.shadowColor = 'rgba(25,55,170,0.6)'; g.shadowBlur = 16;
  typeText(g, TX.bento[1], T.w1, T.w1Step, t, -(h / 2) + 130, px1 * 0.36, px1, COL.accent);
  g.restore();
}
function drawSlot(g, s, t) {
  let dx = 0, dy = 0, sc = 1, rot = 0, a = 1;
  if (s.stack) { const p = eoX(lin(t, T.stack + s.si * 0.08, T.stack + s.si * 0.08 + 0.55)); if (p <= 0) return; dx = (1 - p) * 900; }
  else {
    const t0 = T.grid + s.order * 0.04, p = eoX(lin(t, t0, t0 + 0.6)); if (p <= 0) return;
    dx = (1 - p) * 260; dy = (1 - p) * 560; sc = mix(0.75, 1, p); rot = (1 - p) * 0.12; a = clamp(p * 3);
  }
  const w = s.w, h = s.h, x = -w / 2, y = -h / 2;
  g.save(); g.globalAlpha = a; g.translate(s.cx + dx, s.cy + dy); g.rotate(rot); g.scale(sc, sc);
  g.shadowColor = 'rgba(16,40,8,0.30)'; g.shadowBlur = 30; g.shadowOffsetY = 14;
  g.fillStyle = '#ffffff'; g.beginPath(); g.roundRect(x, y, w, h, 18); g.fill();
  g.shadowColor = 'transparent'; g.shadowBlur = 0; g.shadowOffsetY = 0;
  g.clip();
  if (s.role === 'img') {
    if (s.swapAt && t > s.swapAt) { const q = eo3(lin(t, s.swapAt, s.swapAt + 0.45)); drawCover(g, s.img, x, y - q * h, w, h); drawCover(g, s.img2, x, y + (1 - q) * h, w, h); }
    else drawCover(g, s.img, x, y, w, h);
  } else if (s.role === 'hero') {
    drawCover(g, s.img, x, y, w, h);
    const q = g.createLinearGradient(0, y + h * 0.4, 0, y + h); q.addColorStop(0, 'rgba(0,0,0,0)'); q.addColorStop(1, 'rgba(0,0,0,0.5)');
    g.fillStyle = q; g.fillRect(x, y, w, h);
    g.font = font(600, L.px0); g.fillStyle = '#ffffff'; g.shadowColor = 'rgba(0,0,0,0.35)'; g.shadowBlur = 18;
    typeText(g, TX.bento[0], T.w0, T.w0Step, t, x + 40, y + h - 44, L.px0, '#ffffff');
  } else if (s.role === 'glass') drawGlass(g, x, y, w, h, t);
  else {
    g.fillStyle = '#f7f6f2'; g.fillRect(x, y, w, h);
    ['#ff5f57', '#febc2e', '#28c840'].forEach((c, i) => { g.fillStyle = c; g.beginPath(); g.arc(x + 28 + i * 20, y + 26, 6, 0, 7); g.fill(); });
    g.font = font(500, L.px2); g.fillStyle = '#1d1d22';
    typeText(g, TX.bento[2], T.w2, T.w2Step, t, x + 44, y + h / 2 + 12 + L.px2 * 0.35, L.px2, COL.accent);
  }
  if (WALLBG === 'dark') { g.strokeStyle = 'rgba(255,255,255,0.16)'; g.lineWidth = 2; g.beginPath(); g.roundRect(x + 1, y + 1, w - 2, h - 2, 17); g.stroke(); }   // keep dark cards apart from the dark wall
  g.restore();
}
function drawMeadow(g, t) {
  reset(g);
  const u = t - T.cut1, cam = camMeadow(t), dark = WALLBG === 'dark', dusk = WALLBG === 'dusk';
  const grade = dark ? 1 : eo3(lin(t, T.cut1, T.cut1 + 0.5));
  const bk = (1 + 0.012 * u) * (1 + cam.z * 0.35);
  g.save(); g.translate(960, 540); g.scale(bk, bk);
  if (dark) {     // dark wall: the dot-wave field with two soft glows in the orb colours
    g.translate(-960, -540); g.fillStyle = '#060608'; g.fillRect(-60, -60, W + 120, H + 120); drawDots(g, t, 0.8);
    for (const [x, y, c] of [[240, 920, COL.orb[0]], [1700, 140, COL.orb[2] || COL.orb[1]]]) {
      const q = g.createRadialGradient(x, y, 0, x, y, 950); q.addColorStop(0, hexA(c, 0.3)); q.addColorStop(1, hexA(c, 0)); g.fillStyle = q; g.fillRect(-60, -60, W + 120, H + 120);
    }
  } else if (L.backdrop) drawCover(g, L.backdrop, -W * 0.56, -H * 0.56, W * 1.12, H * 1.12, 0.5);
  else {
    const f = (grade < 1 ? `saturate(${(0.3 + 0.7 * grade).toFixed(3)}) brightness(${(1.18 - 0.18 * grade).toFixed(3)}) hue-rotate(${(-30 * (1 - grade)).toFixed(1)}deg) ` : '') +
      (dusk ? 'saturate(1.15)' : '');
    if (f) g.filter = f.trim();
    g.drawImage(L.sky, -L.sky.width / 2, -L.sky.height / 2);
    g.drawImage(L.clouds, -L.clouds.width / 2 + 60 - u * 22, -L.sky.height / 2 + 40);
    g.drawImage(L.hills, -L.hills.width / 2, -L.hills.height / 2);
    g.filter = 'none';
    if (dusk) {     // sunset: a warm-to-violet multiply over everything and a glow on the horizon
      const hh = L.sky.height, q = g.createLinearGradient(0, -hh / 2, 0, hh / 2);
      q.addColorStop(0, '#ff8f5c'); q.addColorStop(0.42, '#ffc08e'); q.addColorStop(0.56, '#e79ac2'); q.addColorStop(1, '#6f5a9e');
      g.globalCompositeOperation = 'multiply'; g.globalAlpha = 0.85; g.fillStyle = q; g.fillRect(-L.sky.width / 2, -hh / 2, L.sky.width, hh);
      const gl = g.createRadialGradient(300, 20, 0, 300, 20, 800); gl.addColorStop(0, 'rgba(255,190,110,0.55)'); gl.addColorStop(1, 'rgba(255,190,110,0)');
      g.globalCompositeOperation = 'screen'; g.globalAlpha = 1; g.fillStyle = gl; g.fillRect(-L.sky.width / 2, -hh / 2, L.sky.width, hh);
      g.globalCompositeOperation = 'source-over';
    }
    g.translate(-960, -540); drawBirds(g, t);
  }
  g.restore();
  if (grade < 1) {
    const q = g.createLinearGradient(0, 0, W, H); q.addColorStop(0, '#d8c4ff'); q.addColorStop(0.5, '#ffd3bd'); q.addColorStop(1, '#fff0b0');
    g.globalCompositeOperation = 'screen'; g.globalAlpha = 0.55 * (1 - grade); g.fillStyle = q; g.fillRect(0, 0, W, H); reset(g);
  }
  g.save(); g.translate(960, 540); g.scale(cam.k, cam.k); g.translate(-cam.cx, -cam.cy);
  for (const s of L.slots) drawSlot(g, s, t);
  g.restore();
}

/* ------------------------------------------------------------------ scene 4: dot waves, orb, headline */
function drawDots(g, t, a) {
  if (a <= 0) return;
  const B = 6, paths = Array.from({ length: B }, () => new Path2D()), D = L.dots;
  for (let i = 0; i < D.length; i += 2) {
    const x = D[i], y = D[i + 1];
    const ph = x * 0.0105 + y * 0.0165 + 1.7 * Math.sin(x * 0.0041 - y * 0.0063 + t * 0.4) + t * 0.8;
    const v = 0.5 + 0.5 * Math.sin(ph * 1.9 + Math.sin(y * 0.01 + t * 0.3));
    paths[Math.min(B - 1, Math.floor(v * B))].rect(x + 3.6 * Math.sin(ph), y + 3.6 * Math.cos(ph * 0.83 + 0.5), 1.7, 1.7);
  }
  for (let b = 0; b < B; b++) { g.fillStyle = `rgba(190,196,210,${((0.08 + 0.42 * b / (B - 1)) * a).toFixed(3)})`; g.fill(paths[b]); }
}
function drawOrb(g, x, y, r, t, a) {
  if (r < 1 || a <= 0) return;
  const rot = t * 1.3, o = L.orbBuf.g; reset(o); o.clearRect(0, 0, 640, 640);
  const cg = o.createConicGradient(rot, 320, 320), oc = COL.orb;
  oc.forEach((c, i) => cg.addColorStop(i / oc.length, c)); cg.addColorStop(1, oc[0]);
  o.fillStyle = cg; o.beginPath(); o.arc(320, 320, 200, 0, 7); o.fill();
  const ang = -rot * 0.8 + 2.4, kx = 320 + 46 * Math.cos(ang), ky = 320 + 46 * Math.sin(ang);
  const rg = o.createRadialGradient(kx, ky, 0, kx, ky, 215);
  rg.addColorStop(0, 'rgba(6,6,9,1)'); rg.addColorStop(0.55, 'rgba(6,6,9,0.93)'); rg.addColorStop(0.82, 'rgba(6,6,9,0.36)'); rg.addColorStop(1, 'rgba(6,6,9,0)');
  o.save(); o.beginPath(); o.arc(320, 320, 200, 0, 7); o.clip(); o.fillStyle = rg; o.fillRect(0, 0, 640, 640); o.restore();
  const k = r / 200, s = 640 * k;
  g.save(); g.globalCompositeOperation = 'lighter'; g.globalAlpha = a * 0.7; g.filter = `blur(${(34 * k).toFixed(1)}px)`;
  g.drawImage(L.orbBuf.c, x - s / 2, y - s / 2, s, s);
  g.filter = 'none'; g.globalCompositeOperation = 'source-over'; g.globalAlpha = a;
  g.drawImage(L.orbBuf.c, x - s / 2, y - s / 2, s, s);
  g.restore();
}
function drawOrbScene(g, t) {
  reset(g); g.fillStyle = '#060607'; g.fillRect(0, 0, W, H);
  drawDots(g, t, lin(t, T.orb - 0.1, T.orb + 0.3));
  const hl = L.hl, cy = 540, drift = 50 * eio3(lin(t, T.words, T.out4 + 0.3));
  const ox = hl.ox - drift, tx = hl.tx - drift, mv = eio3(lin(t, T.orb + 0.2, T.words + 0.1));
  drawOrb(g, mix(960, ox, mv), cy, hl.r * Math.max(0, eoBack(clamp((t - T.orb) / 0.5))), t, clamp((t - T.orb) / 0.2));
  g.font = font(500, hl.px); g.fillStyle = '#f4f4f6'; g.textBaseline = 'alphabetic';
  hl.words.forEach((w, i) => {
    const t0 = T.words + i * T.wordStep, e = eo3(lin(t, t0, t0 + 0.42)); if (e <= 0) return;
    g.save(); g.globalAlpha = e; if (e < 0.98) g.filter = `blur(${((1 - e) * 12).toFixed(2)}px)`;
    g.fillText(w.s, tx + w.x + (1 - e) * 34, cy + hl.px * 0.18); g.restore();
  });
  const sp = lin(t, T.sub, T.sub + 0.7);
  if (sp > 0) {
    g.font = font(400, hl.spx);
    const q = g.createLinearGradient(tx, 0, tx + hl.subW, 0), edge = sp * 1.25, c1 = 'rgba(196,198,206,1)', c0 = 'rgba(196,198,206,0)';
    q.addColorStop(0, c1); q.addColorStop(clamp(edge - 0.25), c1); q.addColorStop(clamp(edge), c0); q.addColorStop(1, c0);
    g.fillStyle = q; g.fillText(TX.sub, tx, cy + hl.px * 0.18 + hl.spx * 2.0);
  }
}

/* ------------------------------------------------------------------ scene 5: flower hero, symbols, from → to */
function drawPetal(f, p, ang, alpha) {
  f.save(); f.rotate(ang); f.globalAlpha = alpha;
  const Lp = p.len, w = p.w, path = new Path2D();
  path.moveTo(0, 0); path.bezierCurveTo(-w * 0.95, -Lp * 0.28, -w * 0.78, -Lp * 0.98, 0, -Lp); path.bezierCurveTo(w * 0.78, -Lp * 0.98, w * 0.95, -Lp * 0.28, 0, 0);
  let q = f.createLinearGradient(0, 0, 0, -Lp);
  q.addColorStop(0, 'rgba(14,44,160,0.96)'); q.addColorStop(0.25, 'rgba(40,98,222,0.82)'); q.addColorStop(0.55, 'rgba(126,172,246,0.55)'); q.addColorStop(0.82, 'rgba(226,238,255,0.72)'); q.addColorStop(1, 'rgba(255,255,255,0.9)');
  f.fillStyle = q; f.fill(path);
  q = f.createLinearGradient(-w, 0, w, 0); q.addColorStop(0, 'rgba(255,255,255,0.35)'); q.addColorStop(0.5, 'rgba(255,255,255,0)'); q.addColorStop(1, 'rgba(255,255,255,0.12)');
  f.fillStyle = q; f.fill(path);
  f.strokeStyle = 'rgba(205,225,255,0.75)'; f.lineWidth = 3; f.stroke(path);
  f.strokeStyle = 'rgba(255,255,255,0.22)'; f.lineWidth = 1.6;
  for (let v = -2; v <= 2; v++) { f.beginPath(); f.moveTo(0, -Lp * 0.08); f.quadraticCurveTo(v * w * 0.25, -Lp * 0.55, v * w * 0.18, -Lp * 0.93); f.stroke(); }
  f.restore();
}
function drawFlower(t) {
  const f = L.fb.g; reset(f); f.clearRect(0, 0, W / 2, H / 2);
  f.setTransform(0.5, 0, 0, 0.5, 0, 0);
  const sc = 1 + 0.03 * (t - T.cut3);
  f.translate(870, 760); f.scale(sc, sc); f.rotate(0.02 * Math.sin(t * 0.7));
  f.strokeStyle = '#0b1736'; f.lineCap = 'round'; f.lineWidth = 30;
  f.beginPath(); f.moveTo(0, -20); f.bezierCurveTo(8, 120, 30, 220, 26, 460); f.stroke();
  for (const p of L.petals) {
    const sway = (p.a + 3.2 * Math.sin(t * 1.25 + p.ph)) * Math.PI / 180;
    for (const [da, al] of p.echo) drawPetal(f, p, sway + da, al);
  }
  const o = L.fb2.g; reset(o); o.clearRect(0, 0, W / 2, H / 2);
  o.filter = 'blur(1.4px)'; o.drawImage(L.fb.c, 0, 0);
  o.filter = 'blur(14px)'; o.globalAlpha = 0.28; o.globalCompositeOperation = 'screen'; o.drawImage(L.fb.c, 0, 0);
  reset(o);
}
function drawRain(g, t) {
  const a = lin(t, T.cut3 + 0.05, T.cut3 + 0.2) * (1 - lin(t, T.cut3 + 0.75, T.cut3 + 1.05)); if (a <= 0) return;
  const u = t - T.cut3; g.fillStyle = '#ffffff';
  for (let c = 0; c < 46; c++) {
    if (hash(c, 9) < 0.35) continue;
    const x = 470 + c * 22, sp = 160 + 260 * hash(c, 3), off = hash(c, 4) * 400;
    for (let k = 0; k < 16; k++) {
      const y = 540 + ((k * 36 + off + u * sp) % 560), fy = (y - 540) / 540;
      g.globalAlpha = a * 0.5 * fy * (0.5 + 0.5 * hash(c, k)); g.fillRect(x, y, 2, 11);
    }
  }
  g.globalAlpha = 1;
}
function drawSymbols(g, t) {
  for (const s of L.sym) {
    const p = (t - s.t0) / s.life; if (p <= 0 || p >= 1) continue;
    const dt = t - s.t0;
    g.save(); g.globalAlpha = Math.sin(Math.PI * p) ** 0.7; g.translate(s.x0 + s.vx * dt, s.y0 + s.vy * dt); g.rotate(s.rot + s.vr * dt);
    g.font = `700 ${Math.round(s.sz)}px ${FONT}`; g.fillStyle = s.col; g.shadowColor = s.col; g.shadowBlur = 12;
    g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(s.ch, 0, 0); g.restore();
  }
}
function drawLine(g, text, t0, step, t, outT, y, px) {
  const ws = splitWords(text); g.font = font(600, px);
  const sw = g.measureText(' ').width, widths = ws.map(s => g.measureText(s).width);
  let x = 960 - (widths.reduce((a, b) => a + b, 0) + sw * (ws.length - 1)) / 2;
  const out = outT ? lin(t, outT, outT + 0.18) : 0;
  ws.forEach((s, i) => {
    const e = eo3(lin(t, t0 + i * step, t0 + i * step + 0.35)), a = e * (1 - out);
    if (a > 0.003) {
      g.save(); g.globalAlpha = a; const b = (1 - e) * 14 + out * 16; if (b > 0.3) g.filter = `blur(${b.toFixed(2)}px)`;
      const q = g.createLinearGradient(0, y - px, 0, y); q.addColorStop(0, '#ffffff'); q.addColorStop(1, '#dbe6f5');
      g.fillStyle = q; g.shadowColor = 'rgba(4,22,70,0.7)'; g.shadowBlur = 30; g.fillText(s, x, y);
      g.shadowColor = 'rgba(4,22,70,0.55)'; g.shadowBlur = 6; g.shadowOffsetY = 3; g.fillText(s, x, y);
      g.shadowColor = 'rgba(255,255,255,0.5)'; g.shadowBlur = 18; g.shadowOffsetY = 0; g.fillText(s, x, y);
      g.restore();
    }
    x += widths[i] + sw;
  });
}
function drawFinale(g, t) {
  reset(g);
  if (L.hero) { const s = 1.04 + 0.025 * (t - T.cut3); g.save(); g.translate(960, 540); g.scale(s, s); drawCover(g, L.hero, -960, -540, W, H, 0.5); g.restore(); }
  else {
    const q = g.createLinearGradient(0, 0, 0, H), c = COL.sky;
    q.addColorStop(0, c[0]); q.addColorStop(0.45, c[1]); q.addColorStop(0.8, c[2]); q.addColorStop(1, c[3]);
    g.fillStyle = q; g.fillRect(0, 0, W, H);
    drawFlower(t); g.drawImage(L.fb2.c, 0, 0, W, H);
  }
  drawRain(g, t); drawSymbols(g, t);
  const y = 545 + L.fpx * 0.35;
  drawLine(g, TX.from, T.from, 0.1, t, T.fromOut, y, L.fpx);
  drawLine(g, TX.to, T.to, 0.15, t, null, y, L.fpx);
  if (TX.url) {
    const p = eo3(lin(t, T.to + 0.45, T.to + 0.8));
    if (p > 0) {
      g.save(); g.globalAlpha = p; g.font = font(500, 34); g.textAlign = 'center'; g.fillStyle = '#ffffff';
      g.shadowColor = 'rgba(4,22,70,0.65)'; g.shadowBlur = 16;
      g.fillText(TX.url, 960, y + (L.logo ? 176 : 78) + (1 - p) * 12); g.restore();
    }
  }
  if (L.logo) {
    const p = eo3(lin(t, T.to + 0.55, T.to + 0.9)), lh = 84, lw = lh * iw(L.logo) / ih(L.logo);
    if (p > 0) {
      const lx = 960 - lw / 2, ly = y + 40 + (1 - p) * 16;
      g.save(); g.globalAlpha = p;
      if (L.logoOpaque) { g.shadowColor = 'rgba(0,20,60,0.3)'; g.shadowBlur = 20; g.beginPath(); g.roundRect(lx, ly, lw, lh, lh * 0.22); g.fill(); g.clip(); g.shadowColor = 'transparent'; }
      g.drawImage(L.logo, lx, ly, lw, lh); g.restore();
    }
  }
}

/* ------------------------------------------------------------------ the frame */
function drawBeat(g, B, t) {
  use(B);
  if (B.type === 'open') {
    const q = lin(t, T.cloudOut + 0.12, T.cut1);
    if (q > 0) { clear(BUF); drawIntro(BUF.g, t); soft(g, BUF.c, 30 * q * q, 1 - 0.75 * q * q); } else drawIntro(g, t);
  } else if (B.type === 'wall') {
    const q = lin(t, T.cut2 - 0.2, T.cut2 + 0.05);
    if (q > 0) { clear(BUF); drawMeadow(BUF.g, t); soft(g, BUF.c, 22 * q * q); } else drawMeadow(g, t);
  } else if (B.type === 'orb') {
    const q = lin(t, T.out4, T.cut3);
    if (q > 0) { clear(BUF); drawOrbScene(BUF.g, t); soft(g, BUF.c, 26 * q * q, 1 - 0.3 * q); } else drawOrbScene(g, t);
  } else {
    const q = lin(t, T.cut3, T.cut3 + 0.24);
    if (q < 1) {
      clear(BUF); drawFinale(BUF.g, t);
      soft(g, BUF.c, 18 * (1 - q), 1, `hue-rotate(${Math.round(140 * (1 - q))}deg) saturate(${(1 + 0.6 * (1 - q)).toFixed(2)})`);
      if (q < 0.85) {
        const fi = Math.floor(t * 40);
        for (let k = 0; k < 10; k++) { const yy = hash(fi, k) * H, hh = 6 + hash(fi, k + 20) * 70, dx = (hash(fi, k + 40) - 0.5) * 180; g.drawImage(X.canvas, 0, yy, W, hh, dx, yy, W, hh); }
        for (let k = 0; k < 7; k++) { g.globalAlpha = 0.65; g.fillStyle = COL.neon[k % 2]; g.fillRect(hash(fi, k + 60) * W, hash(fi, k + 70) * H, 20 + hash(fi, k + 80) * 90, 10 + hash(fi, k + 90) * 40); }
        g.globalAlpha = 1;
      }
      if (q > 0.7) { g.fillStyle = `rgba(255,255,255,${(0.35 * (1 - q) / 0.3).toFixed(3)})`; g.fillRect(0, 0, W, H); }
    } else drawFinale(g, t);
  }
}
function frame(g, t) {
  reset(g); g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
  let i = BEATS.findIndex(b => t < b.t0 + b.dur); if (i < 0) i = BEATS.length - 1;
  let B = BEATS[i], N = BEATS[i + 1];
  const P = BEATS[i - 1];
  if (B.type === 'orb' && P && P.type === 'wall' && t < B.t0 + 0.1) { N = B; B = P; }   // the wall runs on under the incoming orb
  drawBeat(g, B, t);
  if (N && N.type === 'orb' && B.type === 'wall' && t > N.t0 - 0.06) {
    clear(BUF2); drawBeat(BUF2.g, N, t); reset(g); g.globalAlpha = eo3(lin(t, N.t0 - 0.06, N.t0 + 0.1)); g.drawImage(BUF2.c, 0, 0); reset(g);
  }
  const fo = lin(t, DUR - 0.35, DUR - 0.02);
  if (fo > 0) { reset(g); g.fillStyle = `rgba(0,0,0,${eio3(fo).toFixed(3)})`; g.fillRect(0, 0, W, H); }
}

/* ------------------------------------------------------------------ boot */
export async function boot() {
  X = document.getElementById('c').getContext('2d');
  window.bootStage = 'config';
  CFG = await (await fetch('/proj/promo.json', { cache: 'no-store' })).json();
  MAN = await (await fetch('/proj/assets/manifest.json', { cache: 'no-store' })).json();
  TX = { ...DEF_TEXT, ...(CFG.text || {}) };
  TX.bento = [0, 1, 2].map(i => (CFG.text?.bento || [])[i] || DEF_TEXT.bento[i]);
  COL = { ...DEF_COL, ...(CFG.colors || {}) };
  FONT = CFG.lang === 'km' ? '"Kantumruy", sans-serif' : 'system-ui, -apple-system, "Helvetica Neue", Arial, "Kantumruy", sans-serif';
  window.bootStage = 'fonts';
  await Promise.all(['400', '500', '600', '700'].map(w => document.fonts.load(`${w} 40px "Kantumruy"`)));
  BUF = surf(W, H); BUF2 = surf(W, H); HALF = surf(W / 2, H / 2);
  window.bootStage = 'pictures';
  const users = [];
  for (const c of MAN.cards || []) users.push({ img: await loadImg('/proj/assets/' + c.src), w: c.w, h: c.h, wall: c.wall !== false, tag: c.tag || null });
  for (const k of ['hero', 'backdrop', 'logo']) if (MAN[k]) L[k] = await loadImg('/proj/assets/' + MAN[k]);
  if (L.logo) { const s = surf(8, 8); s.g.drawImage(L.logo, 0, 0, 8, 8); L.logoOpaque = s.g.getImageData(0, 0, 1, 1).data[3] > 250; }   // no transparency: show it as a rounded app icon
  const nPh = Math.max(6, 14 - users.length), pool = [];
  const phs = Array.from({ length: nPh }, (_, i) => ({ img: placeholder(PH_KINDS[i % PH_KINDS.length], 300, 230, TX.labels[i % TX.labels.length], 40 + i), w: 300, h: 230 }));
  for (let i = 0; i < Math.max(users.length, phs.length); i++) { if (users[i]) pool.push(users[i]); if (phs[i] && (i % 2 === 0 || users.length < 8)) pool.push(phs[i]); }
  const steps = { buildGrid, buildMeadow, buildDots, buildFlower, buildBeats: () => buildBeats(users, phs, pool) };
  for (const [k, f] of Object.entries(steps)) { window.bootStage = k; const t0 = performance.now(); f(); (window.bootTimes ||= {})[k] = Math.round(performance.now() - t0); }
  window.bootStage = 'done';
  const fin = BEATS[BEATS.length - 1], w1 = BEATS[1];
  window.DUR = DUR;
  window.CUES = CUES;
  window.BEATS = BEATS.map(b => ({ type: b.type, t0: +b.t0.toFixed(3), dur: +b.dur.toFixed(3), tag: b.tag || null }));
  window.SECTIONS = CFG.chapters?.length
    ? { intro: 0, meadow: w1.t0, orb: w1.t0 + 0.55 * (fin.t0 - w1.t0), fin: fin.t0 + 0.2, end: DUR }
    : { intro: 0, meadow: BEATS[1].t0, orb: BEATS[2].t0, fin: fin.t0 + 0.2, end: DUR };
  window.PREVIEW_TIMES = CFG.chapters?.length
    ? [...BEATS.map(b => b.t0 + b.dur * { open: 0.6, wall: 0.72, orb: 0.75, finale: 0.3 }[b.type]), DUR - 0.7]
    : [0.30, 1.10, 2.30, 3.10, 3.62, 4.55, 5.75, 6.25, 7.20, DUR - 2.85, DUR - 1.75, DUR - 0.6];
  window.render = async t => { frame(X, t); };
}
