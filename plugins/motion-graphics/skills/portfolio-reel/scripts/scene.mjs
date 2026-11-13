// portfolio-reel scene (template "skill 2"): a ~30 s creator / freelancer intro reel on one 1920x1080 canvas.
//
//   hook      a gradient with two big soft circles and drifting bokeh; a small line types word by word, then the
//             big question pops up with a light sweep
//   wipe      a circle grows from the bottom (with two echo rings); the avatar pops in as a small disc
//   hero      the profile page: big round avatar with an orbiting dashed ring, badge pill, "Hello, I'm …" with a
//             highlighter swipe under the name, roles split by bars, a pill button that shines and pulses, an arrow
//             that flies up before the page scrolls (with motion blur)
//   sections  one page per work section ("01 / 03" label, gradient title, drawn underline) with 1-3 rounded cards
//             playing the user's clips (or showing pictures): they trail the scroll, float, and get a glare sweep
//   cta       a light wipe back to the gradient; two short lines word by word over a ticker of tags
//   card      a dark social profile card pops from a dot: avatar, handle, name, counting stats, two buttons; a cursor
//             clicks the first button (confetti, the label changes), then the card flips in 3D to its back
//   always    film grain and a vignette
//
// promo.json "style" picks a colour theme (STYLES below: mustard = the template, midnight, sunset, amber, mint);
// "colors" overrides single colours; "effects" turns effects off ({"grain": false, ...} or false for all).
// window.render(t) draws time t; window.DUR, window.CUES and window.SECTIONS feed audio.py (render.mjs --cues);
// window.PREVIEW_TIMES are the --preview stills. Inputs: /proj/promo.json and /proj/assets/manifest.json.
const W = 1920, H = 1080;
let X, CFG, MAN, TX, COL, FX, T, FONT, DUR, UI = 'classic';
const CUES = [], L = {}, CUR = new Map(), IMGC = new Map();
let BUF, CARDF, CARDB, TXT;

/* ------------------------------------------------------------------ helpers */
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lin = (t, a, b) => clamp((t - a) / (b - a));
const mix = (a, b, p) => a + (b - a) * p;
const eo3 = x => 1 - (1 - x) ** 3;
const eio3 = x => (x < 0.5 ? 4 * x ** 3 : 1 - (-2 * x + 2) ** 3 / 2);
const eoX = x => (x >= 1 ? 1 : 1 - 2 ** (-10 * x));
const eiX = x => (x <= 0 ? 0 : 2 ** (10 * x - 10));
const eoBack = (x, c = 1.6) => 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2;
const pad = (n, k) => String(n).padStart(k, '0');
function rng(seed) { let a = seed >>> 0; return () => { a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
function surf(w, h) { const c = document.createElement('canvas'); c.width = Math.round(w); c.height = Math.round(h); return { c, g: c.getContext('2d') }; }
function reset(g) {
  g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.globalCompositeOperation = 'source-over'; g.filter = 'none';
  g.shadowColor = 'transparent'; g.shadowBlur = 0; g.shadowOffsetX = 0; g.shadowOffsetY = 0; g.textAlign = 'left'; g.textBaseline = 'alphabetic';
  g.setLineDash([]);
}
function hexA(c, a) { const n = parseInt(String(c).replace('#', '').padEnd(6, '0').slice(0, 6), 16); return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`; }
const font = (wt, px) => `${wt} ${Math.max(1, Math.round(px))}px ${FONT}`;
const splitWords = s => String(s || '').split(/\s+/).filter(Boolean);
const iw = img => img.naturalWidth || img.width, ih = img => img.naturalHeight || img.height;
function drawCover(g, img, x, y, w, h, fy = 0.4, zoom = 1) {
  const s = Math.max(w / iw(img), h / ih(img)) * zoom, sw = w / s, sh = h / s;
  g.drawImage(img, (iw(img) - sw) / 2, (ih(img) - sh) * fy, sw, sh, x, y, w, h);
}
function loadImg(src) {
  if (IMGC.has(src)) return IMGC.get(src);
  const p = new Promise((res, rej) => { const i = new Image(); i.onload = () => res(i); i.onerror = () => rej(new Error('cannot load ' + src)); i.src = src; });
  IMGC.set(src, p);
  if (IMGC.size > 600) IMGC.delete(IMGC.keys().next().value);
  return p;
}
function fitPx(text, wt, px, maxW) { X.font = font(wt, px); const w = X.measureText(text).width; return w > maxW ? px * maxW / w : px; }
// a line of words that appear one by one (fade, rise and un-blur); align 'center' or 'left'. Returns the word boxes.
function words(g, text, x, y, t0, step, t, { wt = 500, px = 40, fill = '#fff', rise = 14, blur = 8, align = 'center', out = null, shadow = null, before = null } = {}) {
  const ws = splitWords(text); if (!ws.length) return [];
  g.font = font(wt, px); const sp = g.measureText(' ').width, wd = ws.map(s => g.measureText(s).width);
  const total = wd.reduce((a, b) => a + b, 0) + sp * (ws.length - 1);
  let cx = align === 'center' ? x - total / 2 : x;
  const boxes = ws.map((s, i) => { const b = { x: cx, w: wd[i], s, t0: t0 + i * step }; cx += wd[i] + sp; return b; });
  if (before) before(boxes);
  const o = out ? lin(t, out, out + 0.25) : 0;
  boxes.forEach(b => {
    const e = eo3(lin(t, b.t0, b.t0 + 0.32)), a = e * (1 - o);
    if (a > 0.004) {
      g.save(); g.globalAlpha = a; g.font = font(wt, px); g.fillStyle = fill;
      if (shadow) { g.shadowColor = shadow; g.shadowBlur = 18; }
      const bl = (1 - e) * blur + o * 10; if (bl > 0.3) g.filter = `blur(${bl.toFixed(2)}px)`;
      g.fillText(b.s, b.x, y + (1 - e) * rise - o * 10); g.restore();
    }
  });
  return boxes;
}
// a diagonal light band crossing the current clip region once, between t0 and t0 + dur
function shine(g, x, y, w, h, t0, t, dur = 0.7, alpha = 0.5) {
  if (!FX.shine) return;
  const p = lin(t, t0, t0 + dur); if (p <= 0 || p >= 1) return;
  const cx = mix(x - w * 0.4, x + w * 1.4, eio3(p)), q = g.createLinearGradient(cx - 120, y, cx + 120, y + h * 0.35);
  q.addColorStop(0, 'rgba(255,255,255,0)'); q.addColorStop(0.5, `rgba(255,255,255,${alpha})`); q.addColorStop(1, 'rgba(255,255,255,0)');
  g.save(); g.fillStyle = q; g.globalCompositeOperation = 'source-atop'; g.fillRect(x, y, w, h); g.restore();
}

/* ------------------------------------------------------------------ styles and defaults */
const STYLES = {
  mustard: { bg: ['#f3e83d', '#d4c81f', '#4b4607'], title: ['#8b8611', '#bdb423'], accent: '#ece02f', button: '#4c46f0', ink: '#111111', sub: '#2a2a2a',
    page: '#fbfbf8', grey: '#ebebe9', frame: '#ffffff', shade: 'rgba(40,40,30,0.10)', pill: '#0d0d0d', pillText: '#ffffff', card: ['#1d1d1d', '#0a0a0a'],
    glow: 'rgba(243,232,61,0.35)', confetti: ['#f3e83d', '#4c46f0', '#ffffff', '#111111'], dark: false },
  midnight: { bg: ['#4f46e5', '#1b1757', '#04050d'], title: ['#7dd3fc', '#c4b5fd'], accent: '#22d3ee', button: '#7c3aed', ink: '#f2f4ff', sub: '#b9bfdc',
    page: '#0b0e1d', grey: '#0f1326', frame: '#262c52', shade: 'grid', pill: '#f2f4ff', pillText: '#0b0e1d', card: ['#161a35', '#090b18'],
    glow: 'rgba(34,211,238,0.45)', confetti: ['#22d3ee', '#a855f7', '#f472b6', '#ffffff'], dark: true },
  sunset: { bg: ['#ffc06b', '#ff5e7e', '#3f0f3a'], title: ['#e2365b', '#ff8a4c'], accent: '#ff8a5c', button: '#ff3d77', ink: '#22111a', sub: '#4a2b38',
    page: '#fff7f2', grey: '#fbefe8', frame: '#ffffff', shade: 'rgba(140,50,40,0.09)', pill: '#22111a', pillText: '#ffffff', card: ['#2a1420', '#12070d'],
    glow: 'rgba(255,122,89,0.4)', confetti: ['#ffc06b', '#ff5e7e', '#ffffff', '#7c3aed'], dark: false },
  amber: { bg: ['#f7b733', '#7a4510', '#0a0907'], title: ['#f5a524', '#ffd27a'], accent: '#f5a524', button: '#f5a524', buttonText: '#141210', ink: '#f6f2e9', sub: '#cdc6b6',
    page: '#11100e', grey: '#151412', frame: '#2b2823', shade: 'grid', pill: '#f5a524', pillText: '#141210', card: ['#1c1a16', '#0b0a08'],
    glow: 'rgba(245,165,36,0.45)', confetti: ['#f5a524', '#ffd27a', '#ffffff', '#8b5cf6'], dark: true },
  mint: { bg: ['#86f5cf', '#22b89c', '#053a33'], title: ['#0e8a75', '#2fc39e'], accent: '#2fe0b0', button: '#0e8a75', ink: '#0b201c', sub: '#26443e',
    page: '#f5fffb', grey: '#e7f4ef', frame: '#ffffff', shade: 'rgba(10,70,55,0.09)', pill: '#0b201c', pillText: '#ffffff', card: ['#11231f', '#06100e'],
    glow: 'rgba(47,224,176,0.4)', confetti: ['#86f5cf', '#22b89c', '#ffffff', '#ffd166'], dark: false },
};
const EFFECTS = ['grain', 'bokeh', 'shine', 'marker', 'orbit', 'blur', 'labels', 'glare', 'ticker', 'confetti'];
const DEF_TEXT = {
  hook: ['Looking for a', 'Video editor?'],
  badge: 'Ideas, made visual',
  hello: "Hello, I'm Alex",
  roles: ['Video editor', 'Motion designer', 'Creative'],
  button: "Here's my work",
  cta: ["Let's turn that idea into visuals", "DM me, let's talk :)"],
};
const DEF_PROFILE = { handle: '@yourname', name: 'Your Name', stats: [['Posts', 40], ['Followers', 150], ['Following', 60]], buttons: ['Follow', 'Message'], clicked: 'Following', back: '@yourname' };

/* ------------------------------------------------------------------ timeline + sound cues */
const SEC = 4.6, SCROLL = 0.85;
function plan() {
  const nS = MAN.sections.length;
  T = { hook: 0.15, hookStep: 0.16 };
  T.big = T.hook + splitWords(TX.hook[0]).length * T.hookStep + 0.2; T.bigStep = 0.24;
  T.wipe = Math.max(2.3, T.big + splitWords(TX.hook[1]).length * T.bigStep + 0.7);
  T.avatar = T.wipe + 0.25; T.hero = T.wipe + 0.45;
  T.badge = T.hero + 0.15; T.hello = T.hero + 0.3; T.helloStep = 0.13;
  T.roles = T.hello + splitWords(TX.hello).length * T.helloStep + 0.1; T.rolesStep = 0.14;
  T.button = T.roles + TX.roles.length * T.rolesStep + 0.1;
  T.arrow = T.button + 0.6; T.heroOut = T.arrow + 1.5;
  T.secIn = Array.from({ length: nS }, (_, k) => T.heroOut + SCROLL + k * SEC);
  T.ctaWipe = nS ? T.secIn[nS - 1] + SEC - 0.5 : T.heroOut + 0.2;
  T.cta = T.ctaWipe + 0.7;
  T.cta2 = T.cta + Math.max(1.6, splitWords(TX.cta[0]).length * 0.15 + 1.0);
  T.card = T.cta2 + (TX.cta[1] ? Math.max(1.1, splitWords(TX.cta[1]).length * 0.15 + 0.8) : 0);
  T.cursor = T.card + 1.5; T.click = T.cursor + 0.85; T.flip = T.click + 1.0; T.end = T.flip + 0.9 + 1.5;
  DUR = T.end;
}
function buildCues() {
  const cue = (t, k, db, al = 'start', extra = {}) => CUES.push({ t: +t.toFixed(3), k, db, al, ...extra });
  splitWords(TX.hook[0]).forEach((_, i) => cue(T.hook + i * T.hookStep, 'tick', -25, 'start', { v: i }));
  const bw = splitWords(TX.hook[1]);
  bw.forEach((_, i) => cue(T.big + i * T.bigStep, 'pop', -19, 'start', { v: i }));
  cue(T.big + (bw.length - 1) * T.bigStep + 0.05, 'boom', -17, 'peak');
  if (FX.shine) cue(T.big + bw.length * T.bigStep + 0.25, 'sparkle', -27);
  cue(T.wipe + 0.3, 'whoosh', -17, 'peak'); cue(T.avatar, 'pop', -20, 'start', { v: 3 });
  cue(T.badge, 'tick', -24, 'start', { v: 5 });
  splitWords(TX.hello).forEach((_, i) => cue(T.hello + i * T.helloStep, 'key', -20, 'start', { v: i }));
  if (FX.marker) cue(L.markT, 'swish', -27, 'peak', { v: 7 });
  TX.roles.forEach((_, i) => cue(T.roles + i * T.rolesStep, 'tick', -25, 'start', { v: i + 7 }));
  cue(T.button, 'pop', -21, 'start', { v: 1 }); cue(T.arrow - 0.35, 'pop', -24, 'start', { v: 2 });
  cue(T.heroOut - 0.3, 'swish', -20, 'peak');
  T.secIn.forEach((s, k) => {
    const s0 = s - SCROLL;
    cue(s0 + 0.45, 'deepwhoosh', -17, 'peak', { v: k });
    splitWords(L.secs[k].title).forEach((_, i) => cue(s0 + 0.35 + i * 0.12, 'tick', -26, 'start', { v: i + 3 * k }));
    L.secs[k].clips.forEach((_, i) => cue(s0 + 0.55 + i * 0.12, 'swish', -23, 'peak', { v: i + k }));
    if (FX.glare) cue(s0 + 1.25, 'sparkle', -30, 'start', { v: k + 2 });
  });
  cue(T.ctaWipe + 0.4, 'reverse', -20, 'peak', { pre: 0.8 }); cue(T.ctaWipe + 0.45, 'airy', -18, 'peak');
  splitWords(TX.cta[0]).forEach((_, i) => cue(T.cta + i * 0.15, 'key', -23, 'start', { v: i + 2 }));
  splitWords(TX.cta[1]).forEach((_, i) => cue(T.cta2 + i * 0.15, 'key', -23, 'start', { v: i + 9 }));
  cue(T.card, 'pop', -16, 'start', { v: 4 }); cue(T.card + 0.15, 'boom', -17, 'peak');
  for (let t = T.card + 0.5; t < T.card + 1.6; t += 0.08) cue(t, 'tick', -33, 'start', { v: Math.round(t * 50) });
  cue(T.card + 0.9, 'pop', -24, 'start', { v: 5 }); cue(T.card + 1.02, 'pop', -24, 'start', { v: 6 });
  cue(T.cursor + 0.3, 'swish', -30, 'peak', { v: 9 });
  cue(T.click, 'click', -13); cue(T.click + 0.05, 'blip', -27);
  if (FX.confetti) cue(T.click + 0.04, 'sparkle', -22, 'start', { v: 5 });
  cue(T.flip + 0.45, 'whoosh', -17, 'peak', { v: 2 }); cue(T.flip + 0.9, 'hit', -18, 'peak');
  CUES.sort((a, b) => a.t - b.t);
}

/* ------------------------------------------------------------------ build */
function buildShade() {   // the section pages: soft window-light shadows (light styles) or a faint grid with glows (dark styles)
  const s = surf(W + 400, H + 300), g = s.g;
  if (COL.shade === 'grid') {
    g.strokeStyle = 'rgba(255,255,255,0.045)'; g.lineWidth = 1.5;
    for (let x = 0; x < W + 400; x += 80) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, H + 300); g.stroke(); }
    for (let y = 0; y < H + 300; y += 80) { g.beginPath(); g.moveTo(0, y); g.lineTo(W + 400, y); g.stroke(); }
    for (const [x, y, r] of [[260, 220, 700], [W + 120, H + 60, 800]]) {
      const q = g.createRadialGradient(x, y, 0, x, y, r); q.addColorStop(0, hexA(COL.accent, 0.13)); q.addColorStop(1, hexA(COL.accent, 0)); g.fillStyle = q; g.fillRect(0, 0, W + 400, H + 300);
    }
  } else {
    g.filter = 'blur(38px)'; g.fillStyle = COL.shade;
    for (let k = 0; k < 4; k++) {
      const x = 120 + k * 520;
      g.beginPath(); g.moveTo(x, -50); g.lineTo(x + 260, -50); g.lineTo(x + 700, H + 250); g.lineTo(x + 440, H + 250); g.closePath(); g.fill();
    }
    g.globalAlpha = 0.7;
    for (let k = 0; k < 3; k++) { const y = 260 + k * 330; g.beginPath(); g.moveTo(0, y); g.lineTo(W + 400, y - 160); g.lineTo(W + 400, y - 110); g.lineTo(0, y + 50); g.closePath(); g.fill(); }
  }
  L.shade = s.c;
}
function buildFx() {
  const r = rng(9);
  L.bokeh = Array.from({ length: 34 }, () => ({ x: r() * W, y: r() * H, r: 6 + r() ** 2 * 46, v: 12 + r() * 34, a: 0.06 + r() * 0.2, ph: r() * 6.28 }));
  L.grain = [0, 1, 2].map(k => {
    const s = surf(256, 256), d = s.g.createImageData(256, 256), q = rng(40 + k);
    for (let i = 0; i < d.data.length; i += 4) { const v = q() * 255; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 255; }
    s.g.putImageData(d, 0, 0); return X.createPattern(s.c, 'repeat');
  });
  const q = rng(77), cols = COL.confetti;
  L.confetti = Array.from({ length: 80 }, (_, i) => {
    const a = -Math.PI / 2 + (q() - 0.5) * 2.9, sp = 650 + q() * 1300;
    return { vx: Math.cos(a) * sp, vy: Math.sin(a) * sp, rot: q() * 6, vr: (q() - 0.5) * 14, w: 10 + q() * 10, h: 15 + q() * 12, col: cols[i % cols.length], life: 1.1 + q() * 0.7 };
  });
  const tags = (CFG.text?.tags) || [...TX.roles, ...MAN.sections.map(s => s.title)];
  L.ticker = tags.join('  ✦  ') + '  ✦  ';
}
function layout(clips) {   // 1-3 cards in a row under the title; portrait cards tall, landscape cards wide
  const asp = clips.map(c => c.w / c.h), n = clips.length;
  const lw = n === 1 ? 1100 : n === 2 ? 800 : 560, ph = n === 3 ? 600 : 640;
  let sz = asp.map(a => (a < 1 ? [ph * a, ph] : [lw, lw / a]));
  const gap = n === 2 ? 120 : 80, total = sz.reduce((s, [w]) => s + w, 0) + gap * (n - 1), k = Math.min(1, 1660 / total);
  sz = sz.map(([w, h]) => [w * k, h * k]);
  const offs = n === 1 ? [0] : n === 2 ? (asp[0] < 1 && asp[1] >= 1 ? [-30, 70] : [50, -20]) : [-10, 22, -6];
  let x = (W - (sz.reduce((s, [w]) => s + w, 0) + gap * k * (n - 1))) / 2;
  return sz.map(([w, h], i) => { const r = { x, y: 625 - h / 2 + offs[i], w, h }; x += w + gap * k; return r; });
}
async function buildSections() {
  L.secs = [];
  for (const [k, s] of MAN.sections.entries()) {
    const clips = [];
    for (const c of s.clips) clips.push(c.kind === 'image' ? { ...c, img: await loadImg('/proj/assets/' + c.src) } : { ...c });
    L.secs.push({ title: s.title, clips, rects: clips.length ? layout(clips) : [], k });
  }
}
function buildCardBack() {
  CARDB = surf(1300, 720); const g = CARDB.g;
  cardBase(g); g.font = font(500, fitPx(L.P.back, 500, 46, 1000)); g.fillStyle = '#ececec'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText(L.P.back, 650, 360);
  g.fillStyle = COL.accent; g.fillRect(650 - 40, 410, 80, 5); reset(g);
}

/* ------------------------------------------------------------------ drawing: gradient scenes */
function drawBokeh(g, t, a = 1) {
  if (!FX.bokeh) return;
  for (const b of L.bokeh) {
    const y = ((b.y - t * b.v) % (H + 120) + H + 120) % (H + 120) - 60, x = b.x + 26 * Math.sin(t * 0.6 + b.ph);
    const q = g.createRadialGradient(x, y, 0, x, y, b.r); q.addColorStop(0, `rgba(255,255,240,${(b.a * a).toFixed(3)})`); q.addColorStop(1, 'rgba(255,255,240,0)');
    g.fillStyle = q; g.beginPath(); g.arc(x, y, b.r, 0, 7); g.fill();
  }
}
function drawGrad(g, t) {
  const q = g.createRadialGradient(W * 0.62 + 60 * Math.sin(t * 0.3), H * 0.56, 40, W * 0.62, H * 0.56, W * 1.05);
  q.addColorStop(0, COL.bg[0]); q.addColorStop(0.45, COL.bg[1]); q.addColorStop(1, COL.bg[2]);
  g.fillStyle = q; g.fillRect(0, 0, W, H);
  const p = eo3(lin(t, 0, 1.3));
  for (const [c0, c1, cy, r] of [[-760, -340, 560, 720], [W + 760, W + 250, 470, 660]]) {
    const cx = mix(c0, c1, p) + 22 * Math.sin(t * 0.5 + r), gr = g.createRadialGradient(cx, cy, r * 0.2, cx, cy, r);
    gr.addColorStop(0, 'rgba(255,255,255,0.06)'); gr.addColorStop(0.93, 'rgba(0,0,0,0.13)'); gr.addColorStop(1, 'rgba(255,255,255,0.32)');
    g.fillStyle = gr; g.beginPath(); g.arc(cx, cy, r, 0, 7); g.fill();
  }
  drawBokeh(g, t);
}
function drawHook(g, t) {
  drawGrad(g, t);
  const up = eo3(lin(t, T.big, T.big + 0.45));
  words(g, TX.hook[0], W / 2, 500 - 70 * up, T.hook, T.hookStep, t, { wt: 500, px: 44, fill: '#ffffff', rise: 10 });
  // the big question, word by word, drawn on its own layer so the light sweep only touches the letters
  const tg = TXT.g; reset(tg); tg.clearRect(0, 0, W, 360);
  const bw = splitWords(TX.hook[1]); tg.font = font(900, L.bigPx);
  const sp = tg.measureText(' ').width, wd = bw.map(s => tg.measureText(s).width), total = wd.reduce((a, b) => a + b, 0) + sp * (bw.length - 1);
  let x = W / 2 - total / 2;
  bw.forEach((s, i) => {
    const e = lin(t, T.big + i * T.bigStep, T.big + i * T.bigStep + 0.4);
    if (e > 0) {
      const k = eoBack(e, 2.2);
      tg.save(); tg.globalAlpha = clamp(e * 3); tg.translate(x + wd[i] / 2, 240 + (1 - eo3(e)) * 60); tg.scale(mix(0.7, 1, k), mix(0.7, 1, k));
      tg.font = font(900, L.bigPx); tg.fillStyle = '#ffffff'; tg.textAlign = 'center'; tg.fillText(s, 0, 0); tg.restore();
    }
    x += wd[i] + sp;
  });
  shine(tg, W / 2 - total / 2 - 40, 60, total + 80, 260, T.big + bw.length * T.bigStep + 0.2, t, 0.8, 0.8);
  g.save(); g.shadowColor = 'rgba(0,0,0,0.28)'; g.shadowBlur = 26; g.shadowOffsetY = 6; g.drawImage(TXT.c, 0, 350); g.restore();
}

/* ------------------------------------------------------------------ drawing: hero page */
function drawAvatar(g, cx, cy, r, photo, t) {
  const q = g.createRadialGradient(cx - r * 0.35, cy - r * 0.4, r * 0.1, cx, cy, r);
  q.addColorStop(0, COL.bg[0]); q.addColorStop(1, COL.bg[1]);
  g.fillStyle = q; g.beginPath(); g.arc(cx, cy, r, 0, 7); g.fill();
  if (L.avatar && photo > 0) {
    g.save(); g.beginPath(); g.arc(cx, cy, r, 0, 7); g.clip(); g.globalAlpha = photo;
    if (CFG.avatarStyle === 'duotone') { g.filter = 'grayscale(1) contrast(1.15)'; g.globalCompositeOperation = 'multiply'; }
    drawCover(g, L.avatar, cx - r, cy - r, 2 * r, 2 * r, 0.3); g.restore();
    if (CFG.avatarStyle !== 'duotone') { g.save(); g.globalAlpha = photo; g.strokeStyle = COL.accent; g.lineWidth = Math.max(2, r * 0.045); g.beginPath(); g.arc(cx, cy, r - g.lineWidth / 2, 0, 7); g.stroke(); g.restore(); }
  }
  if (FX.orbit && photo > 0 && r > 100) {     // a dashed ring turning around the avatar, with three dots riding it
    const R = r + 34;
    g.save(); g.globalAlpha = photo * 0.85; g.strokeStyle = COL.accent; g.lineWidth = 3; g.setLineDash([16, 18]); g.lineDashOffset = -t * 50;
    g.beginPath(); g.arc(cx, cy, R, 0, 7); g.stroke(); g.setLineDash([]);
    for (let k = 0; k < 3; k++) { const a = t * 0.9 + k * 2.094; g.fillStyle = k === 1 ? COL.button : COL.accent; g.beginPath(); g.arc(cx + R * Math.cos(a), cy + R * Math.sin(a), 9, 0, 7); g.fill(); }
    g.restore();
  }
}
function star(g, cx, cy, r) {
  g.beginPath();
  for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * 0.45 : r; g.lineTo(cx + rr * Math.cos(a), cy + rr * Math.sin(a)); }
  g.closePath(); g.fill();
}
function arrowUp(g, cx, cy, s, col) {
  g.strokeStyle = col; g.lineWidth = s * 0.16; g.lineCap = 'round'; g.lineJoin = 'round';
  g.beginPath(); g.moveTo(cx, cy + s * 0.5); g.lineTo(cx, cy - s * 0.5); g.moveTo(cx - s * 0.36, cy - s * 0.14); g.lineTo(cx, cy - s * 0.5); g.lineTo(cx + s * 0.36, cy - s * 0.14); g.stroke();
}
function drawHero(g, t, dy) {
  g.fillStyle = COL.page; g.fillRect(0, dy, W, H);
  if (COL.dark) { const q = g.createRadialGradient(370, 540 + dy, 0, 370, 540 + dy, 900); q.addColorStop(0, hexA(COL.accent, 0.16)); q.addColorStop(1, hexA(COL.accent, 0)); g.fillStyle = q; g.fillRect(0, dy, W, H); }
  const pop = eoBack(lin(t, T.avatar, T.avatar + 0.35)), grow = eio3(lin(t, T.hero, T.hero + 0.55));
  const cx = mix(0.21 * W, 370, grow), cy = mix(0.34 * H, 540, grow) + dy, r = mix(62 * pop, 290, grow);
  if (r > 1) drawAvatar(g, cx, cy, r, lin(t, T.hero + 0.3, T.hero + 0.75), t);
  const bx = 1340;
  const bp = eo3(lin(t, T.badge, T.badge + 0.35));
  if (bp > 0) {
    g.save(); g.globalAlpha = bp; g.font = font(500, 30); const tw = g.measureText(TX.badge).width, bw = tw + 112, bh = 64;
    g.translate(bx, 300 + dy); g.scale(mix(0.9, 1, bp), mix(0.9, 1, bp));
    g.strokeStyle = COL.ink; g.lineWidth = 3; g.beginPath(); g.roundRect(-bw / 2, -bh / 2, bw, bh, bh / 2); g.stroke();
    g.fillStyle = COL.accent; star(g, -bw / 2 + 42, 0, 15); g.fillStyle = COL.ink; g.textBaseline = 'middle'; g.fillText(TX.badge, -bw / 2 + 72, 2); g.restore();
  }
  // greeting, with a highlighter swiped under the name
  const hy = 505 + dy, px = L.helloPx;
  words(g, TX.hello, bx, hy, T.hello, T.helloStep, t, { wt: 800, px, fill: COL.ink, rise: 16, blur: 6, before: boxes => {
    if (!FX.marker || boxes.length < 2) return;
    const hl = boxes.slice(L.markFrom), x0 = hl[0].x - 12, x1 = hl[hl.length - 1].x + hl[hl.length - 1].w + 12;
    const m = eo3(lin(t, L.markT, L.markT + 0.45)); if (m <= 0) return;
    g.save(); g.fillStyle = hexA(COL.accent, COL.dark ? 0.95 : 0.85);
    const y0 = COL.dark ? hy + px * 0.08 : hy - px * 0.34, hh = COL.dark ? px * 0.12 : px * 0.42;
    g.beginPath(); g.roundRect(x0, y0, (x1 - x0) * m, hh, hh / 2); g.fill(); g.restore();
  } });
  g.font = font(500, 36); const rw = TX.roles.map(s => g.measureText(s).width), gap = 44, total = rw.reduce((a, b) => a + b, 0) + gap * (rw.length - 1);
  let x = bx - total / 2;
  TX.roles.forEach((s, i) => {
    const e = eo3(lin(t, T.roles + i * T.rolesStep, T.roles + i * T.rolesStep + 0.3));
    if (e > 0) {
      g.save(); g.globalAlpha = e; g.font = font(500, 36); g.fillStyle = COL.sub; g.fillText(s, x, 592 + dy + (1 - e) * 10);
      if (i > 0) { g.fillStyle = COL.accent; g.fillRect(x - gap / 2 - 1.5, 556 + dy, 3, 46 * e); }
      g.restore();
    }
    x += rw[i] + gap;
  });
  const be = eoX(lin(t, T.button, T.button + 0.45));
  if (be > 0) {
    g.font = font(500, 32); const lw = g.measureText(TX.button).width, fw = lw + 160, bh = 88, w = mix(bh, fw, be);
    const left = bx - w / 2, cyb = 770 + dy;
    if (FX.shine && be >= 1) {     // a soft pulse ring every 1.2 s while the button waits
      const ph = ((t - T.arrow) % 1.2) / 1.2;
      if (t > T.arrow && t < T.heroOut - 0.5) { g.save(); g.strokeStyle = hexA(COL.accent, 0.6 * (1 - ph)); g.lineWidth = 3; g.beginPath(); g.roundRect(left - 14 * ph, cyb - bh / 2 - 14 * ph, w + 28 * ph, bh + 28 * ph, bh / 2 + 14 * ph); g.stroke(); g.restore(); }
    }
    g.fillStyle = COL.pill; g.beginPath(); g.roundRect(left, cyb - bh / 2, w, bh, bh / 2); g.fill();
    g.save(); g.beginPath(); g.roundRect(left, cyb - bh / 2, w, bh, bh / 2); g.clip();
    words(g, TX.button, left + 46, cyb + 11, T.button + 0.3, 0.1, t, { wt: 500, px: 32, fill: COL.pillText, align: 'left', rise: 6, blur: 4 });
    if (FX.shine) { const sx = mix(left - 200, left + w + 200, eio3(lin(t, T.arrow + 0.1, T.arrow + 0.8))); const q = g.createLinearGradient(sx - 90, 0, sx + 90, 0); q.addColorStop(0, 'rgba(255,255,255,0)'); q.addColorStop(0.5, 'rgba(255,255,255,0.35)'); q.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = q; g.fillRect(left, cyb - bh / 2, w, bh); }
    g.restore();
    const ae = eoBack(lin(t, T.arrow - 0.35, T.arrow));
    if (ae > 0) {
      const ax = left + w - 50, ar = 27 * ae;
      g.fillStyle = COL.pillText; g.beginPath(); g.arc(ax, cyb, ar, 0, 7); g.fill();
      const fly = eiX(lin(t, T.heroOut - 0.55, T.heroOut));
      arrowUp(g, ax, cyb - fly * 1100, 28 * ae, fly > 0.02 ? COL.ink : COL.pill);
    }
  }
}

/* ------------------------------------------------------------------ drawing: work sections */
function titleFill(g, y) { const q = g.createLinearGradient(0, y - 60, 0, y); q.addColorStop(0, COL.title[1]); q.addColorStop(1, COL.title[0]); return q; }
function drawCard(g, c, r, x, y, lt, glareT) {
  g.save();
  if (COL.dark) { g.shadowColor = COL.glow; g.shadowBlur = 44; } else { g.shadowColor = 'rgba(0,0,0,0.26)'; g.shadowBlur = 38; g.shadowOffsetY = 18; }
  g.fillStyle = COL.frame; g.beginPath(); g.roundRect(x, y, r.w, r.h, 26); g.fill(); g.restore();
  const img = c.kind === 'image' ? c.img : CUR.get(c.id);
  g.save(); g.beginPath(); g.roundRect(x + 6, y + 6, r.w - 12, r.h - 12, 21); g.clip();
  if (img) drawCover(g, img, x + 6, y + 6, r.w - 12, r.h - 12, 0.3, c.kind === 'image' ? 1 + 0.035 * Math.max(0, lt) : 1);
  else { g.fillStyle = '#222'; g.fillRect(x, y, r.w, r.h); }
  if (FX.glare) {      // one diagonal glare across the card after it lands
    const p = lin(lt, glareT, glareT + 0.65);
    if (p > 0 && p < 1) {
      const gx = mix(x - r.w * 0.5, x + r.w * 1.5, eio3(p)), q = g.createLinearGradient(gx - r.w * 0.25, y, gx + r.w * 0.25, y + r.h);
      q.addColorStop(0, 'rgba(255,255,255,0)'); q.addColorStop(0.5, 'rgba(255,255,255,0.32)'); q.addColorStop(1, 'rgba(255,255,255,0)');
      g.fillStyle = q; g.fillRect(x, y, r.w, r.h);
    }
  }
  g.restore();
}
function drawSection(g, k, t, dy) {
  const S = L.secs[k], s0 = T.secIn[k] - SCROLL, n = L.secs.length;
  g.save(); g.beginPath(); g.rect(0, dy, W, H); g.clip();
  g.fillStyle = COL.grey; g.fillRect(0, dy, W, H);
  g.drawImage(L.shade, -180 + 40 * Math.sin(t * 0.15), -120 + (COL.shade === 'grid' ? dy * 0.3 : 0));
  if (FX.labels) {
    const e = eo3(lin(t, s0 + 0.25, s0 + 0.6));
    if (e > 0) {
      g.save(); g.globalAlpha = e; g.font = font(700, 26); g.fillStyle = COL.title[0]; g.textAlign = 'center';
      g.fillText(`${pad(k + 1, 2)}  /  ${pad(n, 2)}`, W / 2, 92 + dy + (1 - e) * 10); g.restore();
    }
    const u = eo3(lin(t, s0 + 0.7, s0 + 1.2));
    if (u > 0) { g.fillStyle = COL.accent; g.beginPath(); g.roundRect(W / 2 - 70 * u, 196 + dy, 140 * u, 7, 3.5); g.fill(); }
  }
  words(g, S.title, W / 2, 168 + dy, s0 + 0.35, 0.12, t, { wt: 800, px: 70, fill: titleFill(g, 168 + dy), rise: 16, blur: 6 });
  S.rects.forEach((r, i) => {
    const e = eoBack(lin(t, s0 + 0.3 + i * 0.12, s0 + 1.0 + i * 0.12), 1.3);
    if (e <= 0) return;
    drawCard(g, S.clips[i], r, r.x, r.y + dy + (1 - e) * 420 + 8 * Math.sin(t * 1.4 + i * 1.9), t - s0, 1.25 + i * 0.15);
  });
  g.restore();
}
function scrollY(t) { let y = 0; for (const s of T.secIn) y += H * eio3(lin(t, s - SCROLL, s)); return y; }

/* ------------------------------------------------------------------ drawing: closing lines + profile card */
function drawTicker(g, t) {
  if (!FX.ticker) return;
  const a = lin(t, T.ctaWipe + 0.3, T.ctaWipe + 0.9) * (1 - lin(t, T.card - 0.3, T.card + 0.3));
  if (a <= 0) return;
  g.save(); g.globalAlpha = a; g.font = font(900, 120); g.lineWidth = 2.5; g.strokeStyle = 'rgba(255,255,255,0.32)';
  const tw = g.measureText(L.ticker).width;
  for (const [y, dir] of [[230, 1], [960, -1]]) {
    let x = (dir * t * 140) % tw; if (x > 0) x -= tw;
    for (let k = 0; k < 3; k++) g.strokeText(L.ticker, x + k * tw, y);
  }
  g.restore();
}
function drawCTA(g, t) {
  const two = !!TX.cta[1];
  drawTicker(g, t);
  words(g, TX.cta[0], W / 2, 555, T.cta, 0.15, t, { wt: 600, px: L.ctaPx, fill: '#ffffff', rise: 12, out: two ? T.cta2 - 0.3 : null, shadow: 'rgba(0,0,0,0.3)' });
  if (two) words(g, TX.cta[1], W / 2, 555, T.cta2, 0.15, t, { wt: 600, px: L.ctaPx, fill: '#ffffff', rise: 12, out: T.card - 0.25, shadow: 'rgba(0,0,0,0.3)' });
}
function cardBase(g) {
  const q = g.createLinearGradient(0, 0, 0, 720); q.addColorStop(0, COL.card[0]); q.addColorStop(1, COL.card[1]);
  g.fillStyle = q; g.beginPath(); g.roundRect(0, 0, 1300, 720, 60); g.fill();
  g.strokeStyle = hexA(COL.accent, 0.35); g.lineWidth = 2.5; g.stroke();
}
function drawCardFront(t) {
  const g = CARDF.g; reset(g); g.clearRect(0, 0, 1300, 720); cardBase(g);
  const a = lin(t, T.card + 0.4, T.card + 0.75), P = L.P;
  if (a <= 0) return;
  g.globalAlpha = a;
  g.fillStyle = '#ffffff'; g.beginPath(); g.arc(235, 360, 158, 0, 7); g.fill();
  g.strokeStyle = COL.accent; g.lineWidth = 6; g.stroke();
  const pic = L.logo || L.avatar;
  if (pic) {
    g.save(); g.beginPath(); g.arc(235, 360, L.logo ? 140 : 150, 0, 7); g.clip();
    if (L.logo) { const s = Math.min(240 / iw(pic), 240 / ih(pic)); g.drawImage(pic, 235 - iw(pic) * s / 2, 360 - ih(pic) * s / 2, iw(pic) * s, ih(pic) * s); }
    else drawCover(g, pic, 85, 210, 300, 300, 0.3);
    g.restore();
  }
  g.fillStyle = '#ffffff'; g.font = font(700, fitPx(P.handle, 700, 66, 820)); g.textAlign = 'center'; g.fillText(P.handle, 860, 175);
  g.textAlign = 'left'; g.font = font(500, 38); g.fillStyle = '#d6d6d6'; g.fillText(P.name, 470, 268);
  const cnt = eo3(lin(t, T.card + 0.5, T.card + 1.6));
  P.stats.slice(0, 3).forEach(([label, v], i) => {
    const x = 470 + i * 260, num = typeof v === 'number' ? String(Math.round(v * cnt)) : String(v);
    g.fillStyle = '#ffffff'; g.font = font(700, 48); g.fillText(num, x, 350);
    g.font = font(500, 30); g.fillStyle = '#e6e6e6'; g.fillText(label, x, 395);
  });
  const clicked = lin(t, T.click, T.click + 0.2);
  P.buttons.slice(0, 2).forEach((label, i) => {
    const e = eoX(lin(t, T.card + 0.9 + i * 0.12, T.card + 1.3 + i * 0.12)); if (e <= 0) return;
    const x = 470 + i * 360, w = 330 * e, y = 480, h = 82, done = i === 0 ? clicked : 0;
    g.fillStyle = done > 0.5 ? '#5d5d63' : COL.button; g.beginPath(); g.roundRect(x, y, w, h, 14); g.fill();
    g.save(); g.beginPath(); g.rect(x, y, w, h); g.clip(); g.fillStyle = done > 0.5 ? '#ffffff' : (COL.buttonText || '#ffffff'); g.font = font(600, 34); g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText(done > 0.5 ? P.clicked : label, x + 165, y + h / 2 + 2); g.restore();
  });
  g.globalAlpha = 1;
  g.save(); g.beginPath(); g.roundRect(0, 0, 1300, 720, 60); g.clip(); shine(g, 0, 0, 1300, 720, T.card + 0.75, t, 0.9, 0.22); g.restore();
}
function drawFlip(g, src, cx, cy, theta) {   // a card turning about its vertical axis, drawn in strips with perspective
  const cw = src.width, ch = src.height, D = 2400, N = 120, sw = cw / N, c = Math.cos(theta), s = Math.sin(theta);
  const proj = x => { const f = D / (D + x * s); return { X: cx + x * c * f, f }; };
  for (let i = 0; i < N; i++) {
    const a = proj(-cw / 2 + i * sw), b = proj(-cw / 2 + (i + 1) * sw), f = (a.f + b.f) / 2;
    g.drawImage(src, i * sw, 0, sw, ch, Math.min(a.X, b.X), cy - ch * f / 2, Math.abs(b.X - a.X) + 0.9, ch * f);
  }
}
function cursor(g, x, y, s) {
  g.save(); g.translate(x, y); g.scale(s, s);
  g.beginPath(); const P = [[0, 0], [0, 40], [10, 31], [17, 46], [24, 43], [17, 28], [30, 28]];
  P.forEach(([a, b], i) => (i ? g.lineTo(a, b) : g.moveTo(a, b))); g.closePath();
  g.fillStyle = '#ffffff'; g.shadowColor = 'rgba(0,0,0,0.35)'; g.shadowBlur = 8; g.shadowOffsetY = 3; g.fill();
  g.shadowColor = 'transparent'; g.strokeStyle = '#111'; g.lineWidth = 2.4; g.lineJoin = 'round'; g.stroke(); g.restore();
}
function drawConfetti(g, t, x0, y0) {
  if (!FX.confetti) return;
  const dt = t - T.click; if (dt <= 0) return;
  for (const p of L.confetti) {
    if (dt > p.life) continue;
    const x = x0 + p.vx * dt, y = y0 + p.vy * dt + 0.5 * 1500 * dt * dt;
    g.save(); g.globalAlpha = 1 - (dt / p.life) ** 2; g.translate(x, y); g.rotate(p.rot + p.vr * dt); g.scale(1, Math.abs(Math.cos(p.vr * dt * 0.7)) + 0.15);
    g.fillStyle = p.col; g.fillRect(-p.w / 2, -p.h / 2, p.w, p.h); g.restore();
  }
}
function drawCardScene(g, t) {
  drawGrad(g, t);
  const cx = W / 2, cy = H / 2, pw = eoBack(lin(t, T.card, T.card + 0.55), 1.4), ph = eoBack(lin(t, T.card + 0.12, T.card + 0.7), 1.4);
  const w = mix(24, 1300, pw), h = mix(24, 720, ph);
  if (pw <= 0) return;
  g.save(); g.shadowColor = COL.dark ? COL.glow : 'rgba(0,0,0,0.42)'; g.shadowBlur = 60; g.shadowOffsetY = COL.dark ? 0 : 26;
  const theta = Math.PI * eio3(lin(t, T.flip, T.flip + 0.9));
  if (theta <= 0) {
    drawCardFront(t);
    if (pw < 1 || ph < 1) { g.fillStyle = COL.card[1]; g.beginPath(); g.roundRect(cx - w / 2, cy - h / 2, w, h, Math.min(60, h / 2)); g.fill(); }
    else g.drawImage(CARDF.c, cx - 650, cy - 360);
  } else {
    g.shadowColor = 'transparent';
    if (theta < Math.PI / 2) { drawCardFront(t); drawFlip(g, CARDF.c, cx, cy, theta); } else drawFlip(g, CARDB.c, cx, cy, theta - Math.PI);
  }
  g.restore();
  const bx = cx - 650 + 470 + 150, by = cy - 360 + 525;
  drawConfetti(g, t, bx, by);
  const m = eio3(lin(t, T.cursor, T.click - 0.05)), gone = lin(t, T.flip - 0.3, T.flip);
  if (m > 0 && gone < 1) {
    const x = mix(1560, bx, m), y = mix(1060, by, m) + 10 * Math.sin(m * Math.PI), press = 1 - 0.18 * Math.sin(Math.PI * lin(t, T.click - 0.06, T.click + 0.1));
    const rp = lin(t, T.click, T.click + 0.45);
    if (rp > 0 && rp < 1) { g.strokeStyle = `rgba(255,255,255,${(0.7 * (1 - rp)).toFixed(3)})`; g.lineWidth = 4; g.beginPath(); g.arc(bx, by, 20 + 70 * eo3(rp), 0, 7); g.stroke(); }
    g.globalAlpha = 1 - gone; cursor(g, x, y, 1.6 * press); g.globalAlpha = 1;
  }
}

/* ================================================================== APP UI ("ui": "app")
   Same timeline, new screens: a search bar types the hook and a results dropdown appears; the cursor clicks the
   first result, which expands into a bento dashboard of glass tiles; the cursor clicks "Here's my work" and a
   horizontal carousel shows each section as device mockups (browser windows, phones) beside a big number and title;
   a chat screen brings the closing lines as message bubbles; a profile card with a cover banner gets the Follow
   click and flips to a QR code of the link. */
const SEG = new Intl.Segmenter(undefined, { granularity: 'grapheme' });
const graphemes = s => [...SEG.segment(String(s || ''))].map(x => x.segment);
let CARDA, CARDBA;
function buildApp() {
  const q = rng(23), cols = [COL.bg[0], COL.bg[1], COL.accent, COL.button];
  L.blobs = cols.map((c, i) => ({ c, x0: [300, 1600, 1100, 500][i], y0: [250, 300, 900, 850][i], rx: 160 + q() * 140, ry: 120 + q() * 120, r: 760 + q() * 260, sp: 0.18 + q() * 0.14, ph: q() * 6.28 }));
  L.query = [TX.hook[0], TX.hook[1]].filter(Boolean).join(' ');
  L.qChars = graphemes(L.query);
  L.qPx = fitPx(L.query, 500, 46, 860);
  T.qEnd = T.big + splitWords(TX.hook[1]).length * T.bigStep; T.drop = T.qEnd + 0.12;
  const n = Math.min(2, MAN.sections.length);
  L.rows = [{ kind: 'me' }, ...MAN.sections.slice(0, n).map((s, i) => ({ kind: 'sec', i, title: s.title, count: s.clips.length }))];
  L.search = { x: 410, y: 340, w: 1100, h: 110 };
  L.row0 = { x: 422, y: L.search.y + L.search.h + 28, w: 1076, h: 100 };
  L.site = (CFG.site || L.P.back || '').replace(/^https?:\/\//, '').replace(/\/$/, '');
  L.helloPxApp = fitPx(TX.hello, 800, CFG.lang === 'km' ? 84 : 96, 1060);
  L.secs.forEach((S, k) => {
    // the title wraps into at most 3 lines in the left column
    let px = 74, lines;
    for (; px > 40; px -= 4) {
      X.font = font(800, px); lines = []; let cur = '';
      for (const w of splitWords(S.title)) { const tryS = cur ? cur + ' ' + w : w; if (X.measureText(tryS).width > 540 && cur) { lines.push(cur); cur = w; } else cur = tryS; }
      if (cur) lines.push(cur);
      if (lines.length <= 3 && lines.every(l => (X.font = font(800, px), X.measureText(l).width <= 560))) break;
    }
    S.lines = lines; S.tpx = px;
    // devices: landscape work in a browser window, portrait work in a phone, cascading across the right area
    const nC = S.clips.length, A = { x: 700, y: 160, w: 1130, h: 830 };
    S.dev = S.clips.map((c, i) => {
      const a = c.w / c.h;
      if (a >= 1) { const bw = nC === 1 ? 1080 : nC === 2 ? 820 : 680; return { kind: 'browser', w: bw, h: bw / a + 56 }; }
      const ph = nC === 1 ? 770 : nC === 2 ? 720 : 620; return { kind: 'phone', w: (ph - 24) * a + 24, h: ph };
    });
    S.dev.forEach((d, i) => {
      if (nC === 1) { d.x = A.x + (A.w - d.w) / 2; d.y = A.y + (A.h - d.h) / 2; return; }
      const p = i / (nC - 1);
      d.x = mix(A.x, A.x + A.w - d.w, p); d.y = mix(A.y, A.y + A.h - d.h, p);
    });
    S.url = (L.site || 'portfolio') + '/' + S.title.toLowerCase().replace(/[^\p{L}\p{N}]+/gu, '-').replace(/^-|-$/g, '');
  });
  CARDA = surf(1100, 740); CARDBA = surf(1100, 740);
}
function slideX(t) { let x = 0; for (const s of T.secIn) x += W * eio3(lin(t, s - SCROLL, s)); return x + W * eio3(lin(t, T.ctaWipe, T.ctaWipe + SCROLL)); }
function meshBg(g, t) {
  g.fillStyle = COL.dark ? COL.page : COL.page; g.fillRect(0, 0, W, H);
  for (const b of L.blobs) {
    const x = b.x0 + b.rx * Math.sin(t * b.sp + b.ph), y = b.y0 + b.ry * Math.cos(t * b.sp * 0.8 + b.ph);
    const q = g.createRadialGradient(x, y, 0, x, y, b.r); q.addColorStop(0, hexA(b.c, COL.dark ? 0.42 : 0.36)); q.addColorStop(1, hexA(b.c, 0));
    g.fillStyle = q; g.fillRect(0, 0, W, H);
  }
  drawBokeh(g, t, COL.dark ? 0.6 : 0.9);
}
function glass(g, x, y, w, h, r, { fill = null, shadow = true } = {}) {
  const dark = COL.dark;
  g.save();
  if (shadow) { g.shadowColor = dark ? 'rgba(0,0,0,0.38)' : 'rgba(40,40,90,0.14)'; g.shadowBlur = 44; g.shadowOffsetY = 18; }
  g.fillStyle = fill || (dark ? 'rgba(255,255,255,0.075)' : 'rgba(255,255,255,0.68)');
  g.beginPath(); g.roundRect(x, y, w, h, r); g.fill(); g.shadowColor = 'transparent';
  const q = g.createLinearGradient(0, y, 0, y + Math.min(h, 220)); q.addColorStop(0, dark ? 'rgba(255,255,255,0.10)' : 'rgba(255,255,255,0.6)'); q.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = q; g.fill();
  g.strokeStyle = dark ? 'rgba(255,255,255,0.16)' : 'rgba(255,255,255,0.95)'; g.lineWidth = 2; g.stroke();
  g.restore();
}
function avatarCircle(g, cx, cy, r, ring = 0) {
  if (ring) { g.fillStyle = '#ffffff'; g.beginPath(); g.arc(cx, cy, r + ring, 0, 7); g.fill(); }
  g.save(); g.beginPath(); g.arc(cx, cy, r, 0, 7); g.clip();
  if (L.avatar) drawCover(g, L.avatar, cx - r, cy - r, 2 * r, 2 * r, 0.3);
  else { g.fillStyle = COL.accent; g.fill(); }
  g.restore();
}
function tileIn(g, t, t0, cx, cy) {   // pop a tile in around its centre: returns false while it is hidden
  const e = eoBack(lin(t, t0, t0 + 0.5), 1.2); if (e <= 0) return false;
  g.globalAlpha = clamp(e * 2); g.translate(cx, cy + (1 - e) * 30); g.scale(mix(0.94, 1, e), mix(0.94, 1, e)); g.translate(-cx, -cy);
  return true;
}

/* ---------------- search hook */
function drawSearch(g, t) {
  meshBg(g, t);
  const S = L.search, a = eo3(lin(t, 0, 0.35)), fade = 1 - lin(t, T.wipe + 0.1, T.wipe + 0.5);
  g.save(); g.globalAlpha = a * fade; g.translate(960, S.y + S.h / 2); g.scale(mix(0.94, 1, a), mix(0.94, 1, a)); g.translate(-960, -(S.y + S.h / 2));
  glass(g, S.x, S.y, S.w, S.h, S.h / 2);
  g.strokeStyle = COL.ink; g.lineWidth = 5; g.lineCap = 'round';
  g.beginPath(); g.arc(S.x + 62, S.y + 50, 18, 0, 7); g.stroke(); g.beginPath(); g.moveTo(S.x + 75, S.y + 63); g.lineTo(S.x + 88, S.y + 76); g.stroke();
  const n = L.qChars.length, k = t < T.hook ? 0 : Math.min(n, Math.floor((t - T.hook) / ((T.qEnd - T.hook) / n)) + 1);
  g.font = font(500, L.qPx); g.textBaseline = 'middle'; g.fillStyle = COL.ink;
  if (k === 0) { g.globalAlpha = a * fade * 0.4; g.fillText(CFG.lang === 'km' ? 'ស្វែងរក…' : 'Search…', S.x + 118, S.y + S.h / 2 + 2); g.globalAlpha = a * fade; }
  const s = L.qChars.slice(0, k).join(''); g.fillText(s, S.x + 118, S.y + S.h / 2 + 2);
  if (t < T.drop + 0.4 || (t * 2.2) % 1 < 0.6) { g.fillStyle = COL.accent; g.fillRect(S.x + 122 + g.measureText(s).width, S.y + 30, 4, S.h - 60); }
  g.restore();
  // the results dropdown
  const da = eo3(lin(t, T.drop, T.drop + 0.3)); if (da <= 0) return;
  const py = S.y + S.h + 16, ph = L.rows.length * 108 + 24;
  g.save(); g.globalAlpha = da * fade; glass(g, S.x, py + (1 - da) * 14, S.w, ph, 34); g.restore();
  L.rows.forEach((r, i) => {
    const e = eo3(lin(t, T.drop + 0.08 + i * 0.07, T.drop + 0.4 + i * 0.07)); if (e <= 0) return;
    const y = py + 12 + i * 108 + (1 - e) * 16, cy = y + 50;
    g.save(); g.globalAlpha = e * fade;
    const hover = i === 0 ? lin(t, T.wipe - 0.55, T.wipe - 0.35) : 0;
    if (hover > 0) { g.fillStyle = hexA(COL.accent, 0.2 * hover); g.beginPath(); g.roundRect(S.x + 12, y, S.w - 24, 100, 26); g.fill(); }
    if (r.kind === 'me') {
      avatarCircle(g, S.x + 78, cy, 36);
      g.fillStyle = COL.ink; g.font = font(700, 36); g.textBaseline = 'alphabetic'; g.fillText(L.P.name, S.x + 136, cy - 4);
      g.fillStyle = COL.sub; g.font = font(500, 24); g.fillText(TX.roles.join('  ·  '), S.x + 136, cy + 30);
    } else {
      g.fillStyle = hexA(COL.accent, 0.22); g.beginPath(); g.roundRect(S.x + 42, cy - 36, 72, 72, 20); g.fill();
      g.fillStyle = COL.ink; g.font = font(800, 26); g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(pad(r.i + 1, 2), S.x + 78, cy + 1);
      g.textAlign = 'left'; g.textBaseline = 'alphabetic'; g.font = font(700, 32); g.fillText(r.title, S.x + 136, cy - 2);
      g.fillStyle = COL.sub; g.font = font(500, 24); g.fillText(`${r.count} ${r.count === 1 ? 'work' : 'works'}`, S.x + 136, cy + 30);
    }
    g.strokeStyle = hexA(COL.ink, 0.5); g.lineWidth = 4; g.lineCap = 'round';
    g.beginPath(); g.moveTo(S.x + S.w - 82, cy); g.lineTo(S.x + S.w - 56, cy); g.moveTo(S.x + S.w - 66, cy - 10); g.lineTo(S.x + S.w - 56, cy); g.lineTo(S.x + S.w - 66, cy + 10); g.stroke();
    g.restore();
  });
  // the cursor picks the first result
  const m = eio3(lin(t, T.drop + 0.35, T.wipe - 0.15));
  if (m > 0 && fade > 0) {
    const tx = S.x + 560, ty = py + 12 + 50, press = 1 - 0.18 * Math.sin(Math.PI * lin(t, T.wipe - 0.16, T.wipe));
    g.save(); g.globalAlpha = fade; cursor(g, mix(1640, tx, m), mix(1040, ty, m), 1.6 * press); g.restore();
  }
}

/* ---------------- bento hero */
function drawHeroApp(g, t, dx) {
  g.save(); g.translate(dx, 0);
  // A: the photo tile
  g.save(); if (tileIn(g, t, T.hero - 0.15, 370, 540)) {
    g.save(); g.shadowColor = COL.dark ? 'rgba(0,0,0,0.45)' : 'rgba(40,40,90,0.18)'; g.shadowBlur = 44; g.shadowOffsetY = 18;
    g.fillStyle = COL.accent; g.beginPath(); g.roundRect(90, 90, 560, 900, 44); g.fill(); g.restore();
    g.save(); g.beginPath(); g.roundRect(90, 90, 560, 900, 44); g.clip();
    if (L.avatar) drawCover(g, L.avatar, 90, 90, 560, 900, 0.25, 1.04 - 0.03 * lin(t, T.hero, T.heroOut));
    const q = g.createLinearGradient(0, 600, 0, 990); q.addColorStop(0, 'rgba(0,0,0,0)'); q.addColorStop(1, 'rgba(0,0,0,0.7)'); g.fillStyle = q; g.fillRect(90, 90, 560, 900);
    g.fillStyle = '#ffffff'; g.font = font(800, fitPx(L.P.name, 800, 50, 480)); g.fillText(L.P.name, 130, 920);
    g.fillStyle = 'rgba(255,255,255,0.8)'; g.font = font(500, 28); g.fillText(L.P.handle, 130, 960);
    shine(g, 90, 90, 560, 900, T.hero + 0.6, t, 0.8, 0.3);
    g.restore();
  } g.restore();
  // B: greeting, badge and role chips
  g.save(); if (tileIn(g, t, T.hero - 0.02, 1254, 305)) {
    glass(g, 678, 90, 1152, 430, 44);
    const be = eo3(lin(t, T.badge, T.badge + 0.35));
    if (be > 0) {
      g.save(); g.globalAlpha *= be; g.font = font(500, 26); const bw = Math.min(1060, g.measureText(TX.badge).width + 96);
      g.strokeStyle = hexA(COL.ink, 0.6); g.lineWidth = 2.5; g.beginPath(); g.roundRect(722, 132, bw, 54, 27); g.stroke();
      g.fillStyle = COL.accent; star(g, 754, 159, 13); g.fillStyle = COL.ink; g.textBaseline = 'middle'; g.fillText(TX.badge, 778, 160, bw - 80); g.restore();
    }
    const px = L.helloPxApp, hy = 320;
    words(g, TX.hello, 722, hy, T.hello, T.helloStep, t, { wt: 800, px, fill: COL.ink, rise: 14, blur: 6, align: 'left', before: boxes => {
      if (!FX.marker || boxes.length < 2) return;
      const hl = boxes.slice(L.markFrom), x0 = hl[0].x - 10, x1 = hl[hl.length - 1].x + hl[hl.length - 1].w + 10, m = eo3(lin(t, L.markT, L.markT + 0.45));
      if (m <= 0) return;
      g.save(); g.fillStyle = hexA(COL.accent, COL.dark ? 0.95 : 0.8);
      const y0 = COL.dark ? hy + px * 0.08 : hy - px * 0.34, hh = COL.dark ? px * 0.12 : px * 0.42;
      g.beginPath(); g.roundRect(x0, y0, (x1 - x0) * m, hh, hh / 2); g.fill(); g.restore();
    } });
    let cx = 722;
    TX.roles.forEach((s, i) => {
      g.font = font(600, 28); const w = g.measureText(s).width + 48, e = eoBack(lin(t, T.roles + i * T.rolesStep, T.roles + i * T.rolesStep + 0.4), 1.6);
      if (e > 0) {
        g.save(); g.globalAlpha *= clamp(e * 2); g.translate(cx + w / 2, 440); g.scale(e, e);
        g.fillStyle = hexA(COL.accent, 0.22); g.beginPath(); g.roundRect(-w / 2, -28, w, 56, 28); g.fill();
        g.strokeStyle = hexA(COL.accent, 0.7); g.lineWidth = 2; g.stroke();
        g.fillStyle = COL.ink; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(s, 0, 2); g.restore();
      }
      cx += w + 16;
    });
  } g.restore();
  // C: stats
  g.save(); if (tileIn(g, t, T.roles + 0.1, 958, 769)) {
    glass(g, 678, 548, 560, 442, 44);
    g.fillStyle = hexA(COL.ink, 0.55); g.font = font(600, 24); g.fillText(CFG.lang === 'km' ? 'ទិដ្ឋភាពរួម' : 'AT A GLANCE', 722, 600);
    const cnt = eo3(lin(t, T.roles + 0.3, T.roles + 1.5));
    L.P.stats.slice(0, 3).forEach(([label, v], i) => {
      const y = 690 + i * 108, num = typeof v === 'number' ? String(Math.round(v * cnt)) : String(v);
      g.fillStyle = COL.accent; g.font = font(800, 64); g.fillText(num, 722, y);
      const nw = g.measureText(num).width; g.fillStyle = COL.sub; g.font = font(500, 28); g.fillText(label, 722 + Math.max(nw, 120) + 28, y - 6);
    });
  } g.restore();
  // D: the button tile the cursor clicks
  const click = T.heroOut - 0.45;
  g.save(); if (tileIn(g, t, T.button, 1548, 653)) {
    const pr = 1 - 0.04 * Math.sin(Math.PI * lin(t, click - 0.08, click + 0.12));
    g.translate(1548, 653); g.scale(pr, pr); g.translate(-1548, -653);
    g.save(); g.shadowColor = COL.glow; g.shadowBlur = 40; g.fillStyle = COL.pill; g.beginPath(); g.roundRect(1266, 548, 564, 210, 44); g.fill(); g.restore();
    g.save(); g.beginPath(); g.roundRect(1266, 548, 564, 210, 44); g.clip();
    g.fillStyle = COL.pillText; g.font = font(800, fitPx(TX.button, 800, 46, 360)); g.fillText(TX.button, 1310, 668);
    g.beginPath(); g.arc(1748, 653, 42, 0, 7); g.fill(); arrowRight(g, 1748, 653, 36, COL.pill);
    shine(g, 1266, 548, 564, 210, T.button + 0.5, t, 0.7, 0.4);
    g.restore();
  } g.restore();
  // E: the list of sections
  g.save(); if (tileIn(g, t, T.button + 0.15, 1548, 888)) {
    glass(g, 1266, 786, 564, 204, 44);
    g.fillStyle = hexA(COL.ink, 0.55); g.font = font(600, 22); g.fillText(CFG.lang === 'km' ? 'ស្នាដៃ' : 'WORK', 1306, 830);
    const nl = Math.min(4, L.secs.length), step = nl > 3 ? 31 : 40, fp = nl > 3 ? 22 : 26;
    L.secs.slice(0, nl).forEach((S, i) => {
      g.fillStyle = COL.accent; g.font = font(800, fp - 2); g.fillText(pad(i + 1, 2), 1306, 872 + i * step);
      g.fillStyle = COL.ink; g.font = font(600, fp); g.fillText(S.title, 1352, 872 + i * step, 440);
    });
  } g.restore();
  g.restore();
  // the cursor goes for the button and clicks it
  const m = eio3(lin(t, T.arrow, click - 0.05)), gone = lin(t, T.heroOut, T.heroOut + 0.3);
  if (m > 0 && gone < 1) {
    const bx = 1590 + dx, by = 668, press = 1 - 0.18 * Math.sin(Math.PI * lin(t, click - 0.06, click + 0.1)), rp = lin(t, click, click + 0.45);
    if (rp > 0 && rp < 1) { g.strokeStyle = `rgba(255,255,255,${(0.75 * (1 - rp)).toFixed(3)})`; g.lineWidth = 4; g.beginPath(); g.arc(bx, by, 20 + 80 * eo3(rp), 0, 7); g.stroke(); }
    g.save(); g.globalAlpha = 1 - gone; cursor(g, mix(1500, bx, m), mix(1060, by, m), 1.6 * press); g.restore();
  }
}
function arrowRight(g, cx, cy, s, col) {
  g.strokeStyle = col; g.lineWidth = s * 0.14; g.lineCap = 'round'; g.lineJoin = 'round';
  g.beginPath(); g.moveTo(cx - s * 0.42, cy); g.lineTo(cx + s * 0.42, cy); g.moveTo(cx + s * 0.08, cy - s * 0.34); g.lineTo(cx + s * 0.42, cy); g.lineTo(cx + s * 0.08, cy + s * 0.34); g.stroke();
}

/* ---------------- device-mockup carousel */
function drawDevice(g, d, c, x, y, lt, glareT) {
  const img = c.kind === 'image' ? c.img : CUR.get(c.id), dark = COL.dark;
  g.save(); g.shadowColor = dark ? COL.glow : 'rgba(30,30,70,0.28)'; g.shadowBlur = dark ? 50 : 44; g.shadowOffsetY = dark ? 0 : 22;
  if (d.kind === 'browser') {
    g.fillStyle = dark ? '#17181f' : '#ffffff'; g.beginPath(); g.roundRect(x, y, d.w, d.h, 24); g.fill(); g.restore();
    [['#ff5f57', 0], ['#febc2e', 1], ['#28c840', 2]].forEach(([col, i]) => { g.fillStyle = col; g.beginPath(); g.arc(x + 30 + i * 24, y + 28, 8, 0, 7); g.fill(); });
    const uw = Math.min(560, d.w - 260), ux = x + (d.w - uw) / 2;
    g.fillStyle = dark ? 'rgba(255,255,255,0.08)' : '#f0f0f4'; g.beginPath(); g.roundRect(ux, y + 12, uw, 32, 16); g.fill();
    g.fillStyle = dark ? 'rgba(255,255,255,0.65)' : '#6b6b78'; g.font = font(500, 18); g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText(c.url || '', ux + uw / 2, y + 29, uw - 30); g.textAlign = 'left'; g.textBaseline = 'alphabetic';
    g.save(); g.beginPath(); g.roundRect(x, y + 56, d.w, d.h - 56, [0, 0, 24, 24]); g.clip();
    if (img) drawCover(g, img, x, y + 56, d.w, d.h - 56, 0.25, c.kind === 'image' ? 1 + 0.03 * Math.max(0, lt) : 1);
    glareSweep(g, x, y + 56, d.w, d.h - 56, lt, glareT); g.restore();
  } else {
    const r = d.w * 0.15;
    g.fillStyle = '#0b0b0f'; g.beginPath(); g.roundRect(x, y, d.w, d.h, r); g.fill(); g.restore();
    g.strokeStyle = 'rgba(255,255,255,0.18)'; g.lineWidth = 2; g.beginPath(); g.roundRect(x + 1, y + 1, d.w - 2, d.h - 2, r); g.stroke();
    g.save(); g.beginPath(); g.roundRect(x + 12, y + 12, d.w - 24, d.h - 24, r - 10); g.clip();
    if (img) drawCover(g, img, x + 12, y + 12, d.w - 24, d.h - 24, 0.3, c.kind === 'image' ? 1 + 0.03 * Math.max(0, lt) : 1);
    glareSweep(g, x + 12, y + 12, d.w - 24, d.h - 24, lt, glareT); g.restore();
    g.fillStyle = '#000000'; g.beginPath(); g.roundRect(x + d.w / 2 - d.w * 0.16, y + 24, d.w * 0.32, 30, 15); g.fill();
  }
}
function glareSweep(g, x, y, w, h, lt, t0) {
  if (!FX.glare) return;
  const p = lin(lt, t0, t0 + 0.65); if (p <= 0 || p >= 1) return;
  const gx = mix(x - w * 0.5, x + w * 1.5, eio3(p)), q = g.createLinearGradient(gx - w * 0.25, y, gx + w * 0.25, y + h);
  q.addColorStop(0, 'rgba(255,255,255,0)'); q.addColorStop(0.5, 'rgba(255,255,255,0.3)'); q.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = q; g.fillRect(x, y, w, h);
}
function drawSectionApp(g, k, t, dx) {
  const S = L.secs[k], s0 = T.secIn[k] - SCROLL;
  g.save(); g.translate(dx, 0);
  const ne = eo3(lin(t, s0 + 0.2, s0 + 0.7));
  g.save(); g.globalAlpha = ne; g.font = font(900, 230); g.fillStyle = hexA(COL.ink, COL.dark ? 0.1 : 0.08); g.fillText(pad(k + 1, 2), 80, 400 - (1 - ne) * 30); g.restore();
  let ty = 520 - (S.lines.length - 1) * S.tpx * 0.55;
  S.lines.forEach((line, i) => { words(g, line, 92, ty + i * S.tpx * 1.08, s0 + 0.35 + i * 0.12, 0.1, t, { wt: 800, px: S.tpx, fill: COL.ink, align: 'left', rise: 16, blur: 6 }); });
  const uy = ty + (S.lines.length - 1) * S.tpx * 1.08 + 40, u = eo3(lin(t, s0 + 0.7, s0 + 1.2));
  if (u > 0) { g.fillStyle = COL.accent; g.beginPath(); g.roundRect(92, uy, 160 * u, 8, 4); g.fill(); }
  const se = eo3(lin(t, s0 + 0.8, s0 + 1.1));
  if (se > 0) { g.save(); g.globalAlpha = se; g.fillStyle = COL.sub; g.font = font(500, 28); const n = S.clips.length; g.fillText(CFG.lang === 'km' ? `${n} ស្នាដៃ` : `${n} ${n === 1 ? 'work' : 'works'}`, 92, uy + 62); g.restore(); }
  S.dev.forEach((d, i) => {
    const e = eoBack(lin(t, s0 + 0.35 + i * 0.13, s0 + 1.05 + i * 0.13), 1.2); if (e <= 0) return;
    g.save(); g.globalAlpha = clamp(e * 2);
    drawDevice(g, d, { ...S.clips[i], url: S.url }, d.x + (1 - e) * 360, d.y + 7 * Math.sin(t * 1.3 + i * 2), t - s0, 1.3 + i * 0.15);
    g.restore();
  });
  g.restore();
}
function drawProgress(g, t) {
  const n = L.secs.length; if (!n) return;
  const a = lin(t, T.secIn[0] - SCROLL, T.secIn[0] - SCROLL + 0.5) * (1 - lin(t, T.ctaWipe, T.ctaWipe + 0.4)); if (a <= 0) return;
  g.save(); g.globalAlpha = a;
  for (let k = 0; k < n; k++) {
    const x = 92 + k * 130, s0 = T.secIn[k] - SCROLL, f = lin(t, s0 + 0.4, s0 + SEC);
    g.fillStyle = hexA(COL.ink, 0.16); g.beginPath(); g.roundRect(x, 56, 116, 7, 3.5); g.fill();
    if (f > 0) { g.fillStyle = COL.accent; g.beginPath(); g.roundRect(x, 56, 116 * f, 7, 3.5); g.fill(); }
  }
  g.restore();
}

/* ---------------- chat */
function bubble(g, x, y, w, h, fill, t0, t) {
  const e = eoBack(lin(t, t0, t0 + 0.35), 1.8); if (e <= 0) return false;
  g.translate(x, y + h); g.scale(e, e); g.translate(-x, -(y + h)); g.globalAlpha *= clamp(e * 2);
  g.fillStyle = fill; g.beginPath(); g.roundRect(x, y, w, h, [28, 28, 28, 8]); g.fill();
  return true;
}
function wrapLines(text, px, maxW, wt = 500) {
  X.font = font(wt, px); const out = []; let cur = '';
  for (const w of splitWords(text)) { const s = cur ? cur + ' ' + w : w; if (X.measureText(s).width > maxW && cur) { out.push(cur); cur = w; } else cur = s; }
  if (cur) out.push(cur); return out;
}
function drawChatApp(g, t, dx) {
  const dark = COL.dark, px = 36;
  g.save(); g.translate(dx, 0);
  glass(g, 460, 180, 1000, 720, 48);
  avatarCircle(g, 540, 260, 40);
  g.fillStyle = '#2bd46b'; g.beginPath(); g.arc(570, 290, 11, 0, 7); g.fill(); g.strokeStyle = dark ? COL.page : '#ffffff'; g.lineWidth = 4; g.stroke();
  g.fillStyle = COL.ink; g.font = font(700, 34); g.fillText(L.P.name, 600, 254);
  g.fillStyle = COL.sub; g.font = font(500, 22); g.fillText(CFG.lang === 'km' ? 'កំពុងសកម្ម' : 'Active now', 600, 288);
  g.fillStyle = hexA(COL.ink, 0.12); g.fillRect(500, 334, 920, 2);
  let y = 380;
  const lines = [TX.cta[0], TX.cta[1]].filter(Boolean), at = [T.cta, T.cta2];
  lines.forEach((text, i) => {
    const ls = wrapLines(text, px, 640), bw = Math.max(...ls.map(l => (X.font = font(500, px), X.measureText(l).width))) + 64, bh = ls.length * px * 1.3 + 40;
    const dots = lin(t, at[i] - 0.65, at[i] - 0.6) * (1 - lin(t, at[i] - 0.05, at[i]));
    if (dots > 0) {   // typing…
      g.save(); g.globalAlpha = dots; g.fillStyle = dark ? 'rgba(255,255,255,0.12)' : '#ebedf3'; g.beginPath(); g.roundRect(560, y, 130, 70, [28, 28, 28, 8]); g.fill();
      for (let k = 0; k < 3; k++) { const b = Math.sin(t * 9 - k * 0.8) * 0.5 + 0.5; g.fillStyle = hexA(COL.ink, 0.35 + 0.4 * b); g.beginPath(); g.arc(598 + k * 27, y + 35 - b * 6, 7, 0, 7); g.fill(); }
      g.restore();
    }
    g.save();
    const accent = i === lines.length - 1 && lines.length > 1;
    if (bubble(g, 560, y, bw, bh, accent ? COL.button : (dark ? 'rgba(255,255,255,0.12)' : '#ebedf3'), at[i], t)) {
      g.fillStyle = accent ? (COL.buttonText || '#ffffff') : COL.ink; g.font = font(500, px);
      ls.forEach((l, j) => g.fillText(l, 592, y + 20 + px * 0.95 + j * px * 1.3));
      g.restore(); g.save(); g.globalAlpha = eo3(lin(t, at[i], at[i] + 0.3)); avatarCircle(g, 520, y + bh - 22, 22);
    }
    g.restore();
    y += bh + 28;
  });
  g.strokeStyle = hexA(COL.ink, 0.2); g.lineWidth = 2; g.beginPath(); g.roundRect(500, 806, 920, 66, 33); g.stroke();
  g.fillStyle = hexA(COL.ink, 0.4); g.font = font(500, 26); g.fillText(CFG.lang === 'km' ? 'សរសេរសារ…' : 'Message…', 536, 848);
  g.fillStyle = COL.accent; g.beginPath(); g.arc(1386, 839, 26, 0, 7); g.fill(); arrowRight(g, 1386, 839, 26, COL.dark ? COL.page : '#ffffff');
  g.restore();
}

/* ---------------- profile card with cover banner and a QR back */
function drawCardFrontApp(t) {
  const g = CARDA.g; reset(g); g.clearRect(0, 0, 1100, 740);
  const q = g.createLinearGradient(0, 0, 0, 740); q.addColorStop(0, COL.card[0]); q.addColorStop(1, COL.card[1]);
  g.fillStyle = q; g.beginPath(); g.roundRect(0, 0, 1100, 740, 48); g.fill();
  g.save(); g.beginPath(); g.roundRect(0, 0, 1100, 250, [48, 48, 0, 0]); g.clip();
  const b = g.createLinearGradient(0, 0, 1100, 250); b.addColorStop(0, COL.bg[0]); b.addColorStop(0.55, COL.accent); b.addColorStop(1, COL.button);
  g.fillStyle = b; g.fillRect(0, 0, 1100, 250);
  for (const [x, y, r, a] of [[180, 40, 260, 0.35], [880, 210, 300, 0.3]]) { const bl = g.createRadialGradient(x + 40 * Math.sin(t), y, 0, x, y, r); bl.addColorStop(0, `rgba(255,255,255,${a})`); bl.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = bl; g.fillRect(0, 0, 1100, 250); }
  g.restore();
  g.strokeStyle = hexA(COL.accent, 0.35); g.lineWidth = 2.5; g.beginPath(); g.roundRect(0, 0, 1100, 740, 48); g.stroke();
  const a = lin(t, T.card + 0.35, T.card + 0.7); if (a <= 0) return;
  g.globalAlpha = a;
  avatarCircle(g, 550, 250, 104, 10);
  const P = L.P;
  g.textAlign = 'center'; g.fillStyle = '#ffffff'; g.font = font(800, fitPx(P.handle, 800, 52, 900)); g.fillText(P.handle, 550, 420);
  g.fillStyle = '#c9c9d2'; g.font = font(500, 30); g.fillText(P.name, 550, 462);
  const cnt = eo3(lin(t, T.card + 0.5, T.card + 1.6)), st = P.stats.slice(0, 3);
  st.forEach(([label, v], i) => {
    const x = 550 + (i - (st.length - 1) / 2) * 250, num = typeof v === 'number' ? String(Math.round(v * cnt)) : String(v);
    g.fillStyle = '#ffffff'; g.font = font(800, 46); g.fillText(num, x, 548); g.fillStyle = '#b9b9c4'; g.font = font(500, 24); g.fillText(label, x, 584);
  });
  const clicked = lin(t, T.click, T.click + 0.2);
  P.buttons.slice(0, 2).forEach((label, i) => {
    const e = eoX(lin(t, T.card + 0.9 + i * 0.12, T.card + 1.3 + i * 0.12)); if (e <= 0) return;
    const x = 290 + i * 280, w = 240, y = 630, h = 76, done = i === 0 ? clicked > 0.5 : false;
    g.save(); g.translate(x + w / 2, y + h / 2); g.scale(e, e); g.translate(-(x + w / 2), -(y + h / 2));
    if (i === 0) { g.fillStyle = done ? '#5d5d63' : COL.button; g.beginPath(); g.roundRect(x, y, w, h, 38); g.fill(); }
    else { g.strokeStyle = 'rgba(255,255,255,0.7)'; g.lineWidth = 2.5; g.beginPath(); g.roundRect(x, y, w, h, 38); g.stroke(); }
    g.fillStyle = i === 0 && !done ? (COL.buttonText || '#ffffff') : '#ffffff'; g.font = font(700, 30); g.textBaseline = 'middle';
    g.fillText(done ? P.clicked : label, x + w / 2, y + h / 2 + 2); g.restore();
  });
  g.textAlign = 'left'; g.textBaseline = 'alphabetic'; g.globalAlpha = 1;
  g.save(); g.beginPath(); g.roundRect(0, 0, 1100, 740, 48); g.clip(); shine(g, 0, 0, 1100, 740, T.card + 0.75, t, 0.9, 0.22); g.restore();
}
function buildCardBackApp() {
  const g = CARDBA.g; reset(g);
  const q = g.createLinearGradient(0, 0, 0, 740); q.addColorStop(0, COL.card[0]); q.addColorStop(1, COL.card[1]);
  g.fillStyle = q; g.beginPath(); g.roundRect(0, 0, 1100, 740, 48); g.fill();
  g.strokeStyle = hexA(COL.accent, 0.35); g.lineWidth = 2.5; g.stroke();
  g.textAlign = 'center';
  if (L.qr) {
    g.fillStyle = '#ffffff'; g.beginPath(); g.roundRect(550 - 175, 90, 350, 350, 28); g.fill();
    g.imageSmoothingEnabled = false; g.drawImage(L.qr, 550 - 150, 115, 300, 300); g.imageSmoothingEnabled = true;
    g.fillStyle = '#ffffff'; g.font = font(700, fitPx(L.P.back, 700, 40, 900)); g.fillText(L.P.back, 550, 530);
    g.fillStyle = '#b9b9c4'; g.font = font(500, 26); g.fillText(CFG.lang === 'km' ? 'ស្កេនដើម្បីបើក' : 'Scan to open', 550, 578);
  } else { g.fillStyle = '#ffffff'; g.font = font(700, fitPx(L.P.back, 700, 54, 900)); g.textBaseline = 'middle'; g.fillText(L.P.back, 550, 370); }
  g.fillStyle = COL.accent; g.fillRect(550 - 40, 620, 80, 5);
  reset(g);
}
function drawCardSceneApp(g, t) {
  const pw = eoBack(lin(t, T.card + 0.05, T.card + 0.6), 1.5); if (pw <= 0) return;
  const cx = W / 2, cy = H / 2, theta = Math.PI * eio3(lin(t, T.flip, T.flip + 0.9));
  g.save();
  if (theta <= 0) {
    drawCardFrontApp(t);
    g.globalAlpha = clamp(pw * 2); g.translate(cx, cy); g.scale(mix(0.6, 1, pw), mix(0.6, 1, pw)); g.translate(-cx, -cy);
    g.shadowColor = COL.dark ? COL.glow : 'rgba(0,0,0,0.35)'; g.shadowBlur = 60; g.shadowOffsetY = COL.dark ? 0 : 24;
    g.drawImage(CARDA.c, cx - 550, cy - 370);
  } else if (theta < Math.PI / 2) { drawCardFrontApp(t); drawFlip(g, CARDA.c, cx, cy, theta); }
  else drawFlip(g, CARDBA.c, cx, cy, theta - Math.PI);
  g.restore();
  const bx = cx - 550 + 290 + 120, by = cy - 370 + 668;
  drawConfetti(g, t, bx, by);
  const m = eio3(lin(t, T.cursor, T.click - 0.05)), gone = lin(t, T.flip - 0.3, T.flip);
  if (m > 0 && gone < 1) {
    const press = 1 - 0.18 * Math.sin(Math.PI * lin(t, T.click - 0.06, T.click + 0.1)), rp = lin(t, T.click, T.click + 0.45);
    if (rp > 0 && rp < 1) { g.strokeStyle = `rgba(255,255,255,${(0.7 * (1 - rp)).toFixed(3)})`; g.lineWidth = 4; g.beginPath(); g.arc(bx, by, 20 + 70 * eo3(rp), 0, 7); g.stroke(); }
    g.save(); g.globalAlpha = 1 - gone; cursor(g, mix(1560, bx, m), mix(1060, by, m) + 10 * Math.sin(m * Math.PI), 1.6 * press); g.restore();
  }
}

/* ---------------- the app frame */
function appPages(g, t, sx) {
  meshBg(g, t);
  if (sx < W) drawHeroApp(g, t, -sx);
  L.secs.forEach((_, k) => { const dx = (k + 1) * W - sx; if (dx > -W && dx < W) drawSectionApp(g, k, t, dx); });
  const cdx = (L.secs.length + 1) * W - sx;
  if (cdx < W && t < T.card + 0.4) {
    const p = lin(t, T.card, T.card + 0.35);
    g.save(); g.globalAlpha = 1 - p; g.translate(960, 540); g.scale(1 - 0.08 * p, 1 - 0.08 * p); g.translate(-960, -540); drawChatApp(g, t, cdx); g.restore();
  }
}
function frameApp(g, t) {
  reset(g);
  if (t < T.wipe + 0.65) {
    drawSearch(g, t);
    const p = eio3(lin(t, T.wipe, T.wipe + 0.6));
    if (p > 0) {
      const r0 = L.row0, x = mix(r0.x, 0, p), y = mix(r0.y, 0, p), w = mix(r0.w, W, p), h = mix(r0.h, H, p);
      g.save(); g.beginPath(); g.roundRect(x, y, w, h, mix(26, 0, p)); g.clip(); appPages(g, t, 0);
      g.fillStyle = hexA(COL.accent, 0.28 * (1 - p)); g.fillRect(x, y, w, h); g.restore();
      g.save(); g.strokeStyle = `rgba(255,255,255,${(0.6 * (1 - p)).toFixed(3)})`; g.lineWidth = 3; g.beginPath(); g.roundRect(x, y, w, h, mix(26, 0, p)); g.stroke(); g.restore();
      const fa = 1 - lin(t, T.hero - 0.2, T.hero);
      if (fa > 0) { g.save(); g.globalAlpha = fa; avatarCircle(g, mix(r0.x + 56, 370, p), mix(r0.y + 50, 540, p), mix(36, 260, p), mix(0, 6, p)); g.restore(); }
    }
  } else {
    const sx = slideX(t), v = Math.abs(slideX(t + 1 / 120) - slideX(t - 1 / 120));
    if (FX.blur && v > 3) {      // horizontal motion blur while the carousel slides
      reset(BUF.g); appPages(BUF.g, t, sx);
      const len = Math.min(70, v * 0.7), n = Math.min(16, Math.max(3, Math.ceil(len / 3.5)));
      for (let k = 0; k < n; k++) { g.globalAlpha = 1 / (k + 1); g.drawImage(BUF.c, -len / 2 + (len * k) / (n - 1), 0); }
      g.globalAlpha = 1;
    } else appPages(g, t, sx);
    drawProgress(g, t);
    if (t >= T.card) drawCardSceneApp(g, t);
  }
}
function buildCuesApp() {
  const cue = (t, k, db, al = 'start', extra = {}) => CUES.push({ t: +t.toFixed(3), k, db, al, ...extra });
  const n = L.qChars.length, st = (T.qEnd - T.hook) / n;
  L.qChars.forEach((ch, i) => { if (ch.trim()) cue(T.hook + i * st, 'key', -22, 'start', { v: i }); });
  cue(T.drop, 'pop', -21, 'start', { v: 1 }); L.rows.forEach((_, i) => cue(T.drop + 0.1 + i * 0.07, 'tick', -28, 'start', { v: i }));
  cue(T.drop + 0.6, 'swish', -30, 'peak', { v: 2 }); cue(T.wipe - 0.1, 'click', -14);
  cue(T.wipe + 0.3, 'whoosh', -17, 'peak');
  [T.hero - 0.15, T.hero - 0.02, T.roles + 0.1, T.button, T.button + 0.15].forEach((x, i) => cue(x, 'pop', -22, 'start', { v: i + 2 }));
  splitWords(TX.hello).forEach((_, i) => cue(T.hello + i * T.helloStep, 'key', -21, 'start', { v: i + 30 }));
  if (FX.marker) cue(L.markT, 'swish', -27, 'peak', { v: 7 });
  TX.roles.forEach((_, i) => cue(T.roles + i * T.rolesStep, 'tick', -25, 'start', { v: i + 7 }));
  for (let x = T.roles + 0.3; x < T.roles + 1.4; x += 0.09) cue(x, 'tick', -34, 'start', { v: Math.round(x * 50) });
  cue(T.arrow + 0.3, 'swish', -30, 'peak', { v: 9 }); cue(T.heroOut - 0.45, 'click', -14, 'start', { v: 1 });
  T.secIn.forEach((s, k) => {
    const s0 = s - SCROLL;
    cue(s0 + 0.42, 'deepwhoosh', -17, 'peak', { v: k });
    L.secs[k].clips.forEach((_, i) => cue(s0 + 0.5 + i * 0.13, 'swish', -23, 'peak', { v: i + k }));
    if (FX.glare) cue(s0 + 1.3, 'sparkle', -30, 'start', { v: k + 2 });
  });
  cue(T.ctaWipe + 0.42, 'deepwhoosh', -18, 'peak', { v: 5 });
  [T.cta, T.cta2].forEach((x, i) => { if ([TX.cta[0], TX.cta[1]][i]) { cue(x - 0.6, 'tick', -32, 'start', { v: i }); cue(x, 'blip', -18, 'start', { v: i + 3 }); } });
  cue(T.card, 'whoosh', -22, 'peak', { v: 3 }); cue(T.card + 0.1, 'pop', -16, 'start', { v: 4 }); cue(T.card + 0.15, 'boom', -18, 'peak');
  for (let x = T.card + 0.5; x < T.card + 1.6; x += 0.08) cue(x, 'tick', -33, 'start', { v: Math.round(x * 50) });
  cue(T.card + 0.9, 'pop', -24, 'start', { v: 5 }); cue(T.card + 1.02, 'pop', -24, 'start', { v: 6 });
  cue(T.cursor + 0.3, 'swish', -30, 'peak', { v: 9 }); cue(T.click, 'click', -13); cue(T.click + 0.05, 'blip', -27);
  if (FX.confetti) cue(T.click + 0.04, 'sparkle', -22, 'start', { v: 5 });
  cue(T.flip + 0.45, 'whoosh', -17, 'peak', { v: 2 }); cue(T.flip + 0.9, 'hit', -18, 'peak');
  CUES.sort((a, b) => a.t - b.t);
}

/* ------------------------------------------------------------------ the frame */
function drawPages(g, t, sy) {
  if (sy < H) drawHero(g, t, -sy);
  L.secs.forEach((_, k) => { const dy = (k + 1) * H - sy; if (dy > -H && dy < H) drawSection(g, k, t, dy); });
}
function frame(g, t) {
  reset(g); g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
  if (UI === 'app') frameApp(g, t);
  else if (t < T.wipe + 0.6) {
    drawHook(g, t);
    const p = lin(t, T.wipe, T.wipe + 0.55);
    if (p > 0) {
      const R = 2400 * eio3(p);
      if (FX.shine) for (const [k, a] of [[1.12, 0.45], [1.26, 0.22]]) { g.strokeStyle = `rgba(255,255,255,${a})`; g.lineWidth = 10; g.beginPath(); g.arc(W / 2, H * 1.35, R * k, 0, 7); g.stroke(); }
      g.save(); g.beginPath(); g.arc(W / 2, H * 1.35, R, 0, 7); g.clip(); drawHero(g, t, 0); g.restore();
    }
  } else if (t < T.ctaWipe + 1) {
    const sy = scrollY(t), v = Math.abs(scrollY(t + 1 / 120) - scrollY(t - 1 / 120));   // px moved in one 60 fps frame
    if (FX.blur && v > 3) {      // vertical motion blur while the page scrolls: an average of close copies along the motion
      reset(BUF.g); BUF.g.fillStyle = '#000'; BUF.g.fillRect(0, 0, W, H); drawPages(BUF.g, t, sy);
      const len = Math.min(60, v * 0.7), n = Math.min(14, Math.max(3, Math.ceil(len / 3.5)));
      for (let k = 0; k < n; k++) { g.globalAlpha = 1 / (k + 1); g.drawImage(BUF.c, 0, -len / 2 + (len * k) / (n - 1)); }
      g.globalAlpha = 1;
    } else drawPages(g, t, sy);
    const p = lin(t, T.ctaWipe, T.ctaWipe + 0.9);     // a light blooms from the bottom-left and takes the frame
    if (p > 0) {
      const R = 2500 * eio3(p), ox = W * 0.12, oy = H * 1.15;
      reset(BUF.g); drawGrad(BUF.g, t); drawCTA(BUF.g, t);
      g.save(); g.beginPath(); g.arc(ox, oy, R, 0, 7); g.clip(); g.drawImage(BUF.c, 0, 0); g.restore();
      const gl = g.createRadialGradient(ox, oy, Math.max(0, R - 300), ox, oy, R + 60);
      gl.addColorStop(0, hexA(COL.bg[0], 0)); gl.addColorStop(0.82, hexA(COL.bg[0], 0.85)); gl.addColorStop(1, hexA(COL.bg[0], 0));
      g.fillStyle = gl; g.fillRect(0, 0, W, H);
    }
  } else if (t < T.card) { drawGrad(g, t); drawCTA(g, t); }
  else drawCardScene(g, t);
  if (FX.grain) {      // vignette + moving film grain over everything
    reset(g);
    const v = g.createRadialGradient(W / 2, H / 2, H * 0.45, W / 2, H / 2, H * 1.05); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.26)');
    g.fillStyle = v; g.fillRect(0, 0, W, H);
    const f = Math.floor(t * 24); g.globalCompositeOperation = 'overlay'; g.globalAlpha = 0.07; g.fillStyle = L.grain[f % 3];
    g.translate((f * 37) % 256, (f * 91) % 256); g.fillRect(-256, -256, W + 512, H + 512); reset(g);
  }
  const fo = lin(t, DUR - 0.35, DUR - 0.02);
  if (fo > 0) { reset(g); g.fillStyle = `rgba(0,0,0,${eio3(fo).toFixed(3)})`; g.fillRect(0, 0, W, H); }
}
async function prepare(t) {   // load the clip frames this frame shows
  CUR.clear();
  const app = UI === 'app', sy = app ? slideX(t) : scrollY(t), size = app ? W : H, jobs = [];
  L.secs.forEach((S, k) => {
    const dy = (k + 1) * size - sy; if (!(dy > -size - 150 && dy < size + 150) || t > T.ctaWipe + 1) return;
    const s0 = T.secIn[k] - SCROLL;
    for (const c of S.clips) if (c.kind === 'video') {
      const f = ((Math.floor(Math.max(0, t - s0) * 30) % c.n) + c.n) % c.n;
      jobs.push(loadImg(`/proj/assets/${c.dir}/${pad(f + 1, 4)}.jpg`).then(img => CUR.set(c.id, img)));
    }
  });
  await Promise.all(jobs);
}

/* ------------------------------------------------------------------ boot */
export async function boot() {
  X = document.getElementById('c').getContext('2d');
  window.bootStage = 'config';
  CFG = await (await fetch('/proj/promo.json', { cache: 'no-store' })).json();
  MAN = await (await fetch('/proj/assets/manifest.json', { cache: 'no-store' })).json();
  TX = { ...DEF_TEXT, ...(CFG.text || {}) };
  if (!Array.isArray(TX.hook)) TX.hook = [String(TX.hook), ''];
  if (!Array.isArray(TX.cta)) TX.cta = [String(TX.cta), ''];
  const style = STYLES[CFG.style] ? CFG.style : 'mustard';
  COL = { ...STYLES[style], ...(CFG.colors || {}) };
  FX = Object.fromEntries(EFFECTS.map(k => [k, CFG.effects === false ? false : (CFG.effects?.[k] ?? true)]));
  L.P = { ...DEF_PROFILE, ...(CFG.profile || {}) };
  UI = CFG.ui === 'app' ? 'app' : 'classic';
  FONT = CFG.lang === 'km' ? '"Kantumruy", sans-serif' : 'system-ui, -apple-system, "Helvetica Neue", Arial, "Kantumruy", sans-serif';
  window.bootStage = 'fonts';
  await Promise.all(['400', '500', '600', '700', '800', '900'].map(w => document.fonts.load(`${w} 40px "Kantumruy"`)));
  BUF = surf(W, H); CARDF = surf(1300, 720); TXT = surf(W, 360);
  window.bootStage = 'pictures';
  if (MAN.avatar) L.avatar = await loadImg('/proj/assets/' + MAN.avatar);
  if (MAN.logo) L.logo = await loadImg('/proj/assets/' + MAN.logo);
  if (MAN.qr) L.qr = await loadImg('/proj/assets/' + MAN.qr);
  await buildSections();
  plan();
  L.bigPx = fitPx(TX.hook[1], 900, CFG.lang === 'km' ? 120 : 140, 1500);
  L.helloPx = fitPx(TX.hello, 800, CFG.lang === 'km' ? 92 : 108, 980);
  L.ctaPx = Math.min(fitPx(TX.cta[0], 600, 50, 1500), fitPx(TX.cta[1] || ' ', 600, 50, 1500));
  const hw = splitWords(TX.hello);       // the highlighter goes under the name: text.highlight words, or everything after the 2nd word
  const hl = splitWords(CFG.text?.highlight || '');
  L.markFrom = hl.length ? Math.max(0, hw.length - hl.length) : Math.min(2, Math.max(0, hw.length - 1));
  L.markT = T.hello + hw.length * T.helloStep + 0.15;
  buildShade(); buildFx(); buildCardBack();
  if (UI === 'app') { buildApp(); buildCardBackApp(); buildCuesApp(); } else buildCues();
  window.bootStage = 'done';
  window.DUR = DUR;
  window.CUES = CUES;
  window.SECTIONS = { intro: 0, main: T.secIn.length ? T.secIn[0] - SCROLL : T.heroOut, cta: T.ctaWipe, card: T.card, end: DUR };
  window.PREVIEW_TIMES = UI === 'app'
    ? [0.75, T.drop + 0.55, T.wipe + 0.35, T.button + 0.6, T.heroOut - 0.42, ...T.secIn.map(s => s + 1.0), T.ctaWipe + 0.45, T.cta2 + 0.6, T.card + 1.25, T.click + 0.25, T.flip + 0.4, DUR - 0.6].slice(0, 16)
    : [0.9, T.big + 1.0, T.wipe + 0.35, T.arrow + 0.5, T.heroOut + 0.4, ...T.secIn.map(s => s + 0.95), T.ctaWipe + 0.45,
    T.cta + 1.0, T.click + 0.25, T.flip + 0.35, DUR - 0.6].slice(0, 16);
  window.render = async t => { await prepare(t); frame(X, t); };
}
