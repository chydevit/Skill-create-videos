// portfolio-reel scene (template "skill 2"): a ~30 s creator / freelancer intro reel on one 1920x1080 canvas.
//
//   hook      mustard gradient with two big soft circles; a small line types word by word, then the big question pops up
//   wipe      a white circle grows from the bottom; the avatar pops in as a small yellow disc
//   hero      white page: big round avatar, outlined badge pill, "Hello, I'm …", roles split by bars, black button
//             "Here's my work" with an arrow that flies up before the page scrolls
//   sections  the page scrolls through 1-4 work sections on light grey with soft window-light shadows: a gradient title
//             and 1-3 rounded cards playing the user's clips (or showing pictures), trailing the scroll, then floating
//   cta       a yellow light wipe back to the gradient; two short lines, word by word
//   card      a black social profile card pops from a dot: avatar, handle, name, counting stats, two buttons; a cursor
//             clicks the first button (it turns grey and changes its label), then the card flips in 3D to its back
//
// window.render(t) draws time t; window.DUR, window.CUES and window.SECTIONS feed audio.py (render.mjs --cues);
// window.PREVIEW_TIMES are the --preview stills. Inputs: /proj/promo.json and /proj/assets/manifest.json.
const W = 1920, H = 1080;
let X, CFG, MAN, TX, COL, T, FONT, DUR;
const CUES = [], L = {}, CUR = new Map(), IMGC = new Map();
let BUF, CARDF, CARDB;

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
function surf(w, h) { const c = document.createElement('canvas'); c.width = Math.round(w); c.height = Math.round(h); return { c, g: c.getContext('2d') }; }
function reset(g) {
  g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.globalCompositeOperation = 'source-over'; g.filter = 'none';
  g.shadowColor = 'transparent'; g.shadowBlur = 0; g.shadowOffsetX = 0; g.shadowOffsetY = 0; g.textAlign = 'left'; g.textBaseline = 'alphabetic';
}
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
// a line of words that appear one by one (fade, rise and un-blur); align 'center' or 'left'
function words(g, text, x, y, t0, step, t, { wt = 500, px = 40, fill = '#fff', rise = 14, blur = 8, align = 'center', out = null, shadow = null } = {}) {
  const ws = splitWords(text); if (!ws.length) return 0;
  g.font = font(wt, px); const sp = g.measureText(' ').width, wd = ws.map(s => g.measureText(s).width);
  const total = wd.reduce((a, b) => a + b, 0) + sp * (ws.length - 1);
  let cx = align === 'center' ? x - total / 2 : x;
  const o = out ? lin(t, out, out + 0.25) : 0;
  ws.forEach((s, i) => {
    const e = eo3(lin(t, t0 + i * step, t0 + i * step + 0.32)), a = e * (1 - o);
    if (a > 0.004) {
      g.save(); g.globalAlpha = a; g.font = font(wt, px); g.fillStyle = fill;
      if (shadow) { g.shadowColor = shadow; g.shadowBlur = 18; }
      const b = (1 - e) * blur + o * 10; if (b > 0.3) g.filter = `blur(${b.toFixed(2)}px)`;
      g.fillText(s, cx, y + (1 - e) * rise - o * 10); g.restore();
    }
    cx += wd[i] + sp;
  });
  return total;
}

/* ------------------------------------------------------------------ defaults */
const DEF_TEXT = {
  hook: ['Looking for a', 'Video editor?'],
  badge: 'Ideas, made visual',
  hello: "Hello, I'm Alex",
  roles: ['Video editor', 'Motion designer', 'Creative'],
  button: "Here's my work",
  cta: ["Let's turn that idea into visuals", "DM me, let's talk :)"],
};
const DEF_PROFILE = { handle: '@yourname', name: 'Your Name', stats: [['Posts', 40], ['Followers', 150], ['Following', 60]], buttons: ['Follow', 'Message'], clicked: 'Following', back: '@yourname' };
const DEF_COL = { bg: ['#f3e83d', '#d4c81f', '#4b4607'], title: ['#8b8611', '#bdb423'], button: '#4c46f0', ink: '#111111', page: '#fbfbf8', grey: '#ebebe9' };

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
  cue(T.wipe + 0.3, 'whoosh', -17, 'peak'); cue(T.avatar, 'pop', -20, 'start', { v: 3 });
  cue(T.badge, 'tick', -24, 'start', { v: 5 });
  splitWords(TX.hello).forEach((_, i) => cue(T.hello + i * T.helloStep, 'key', -20, 'start', { v: i }));
  TX.roles.forEach((_, i) => cue(T.roles + i * T.rolesStep, 'tick', -25, 'start', { v: i + 7 }));
  cue(T.button, 'pop', -21, 'start', { v: 1 }); cue(T.arrow - 0.35, 'pop', -24, 'start', { v: 2 });
  cue(T.heroOut - 0.3, 'swish', -20, 'peak');
  T.secIn.forEach((s, k) => {
    const s0 = s - SCROLL;
    cue(s0 + 0.45, 'deepwhoosh', -17, 'peak', { v: k });
    splitWords(L.secs[k].title).forEach((_, i) => cue(s0 + 0.35 + i * 0.12, 'tick', -26, 'start', { v: i + 3 * k }));
    L.secs[k].clips.forEach((_, i) => cue(s0 + 0.55 + i * 0.12, 'swish', -23, 'peak', { v: i + k }));
  });
  cue(T.ctaWipe + 0.4, 'reverse', -20, 'peak', { pre: 0.8 }); cue(T.ctaWipe + 0.45, 'airy', -18, 'peak');
  splitWords(TX.cta[0]).forEach((_, i) => cue(T.cta + i * 0.15, 'key', -23, 'start', { v: i + 2 }));
  splitWords(TX.cta[1]).forEach((_, i) => cue(T.cta2 + i * 0.15, 'key', -23, 'start', { v: i + 9 }));
  cue(T.card, 'pop', -16, 'start', { v: 4 }); cue(T.card + 0.15, 'boom', -17, 'peak');
  for (let t = T.card + 0.5; t < T.card + 1.6; t += 0.08) cue(t, 'tick', -33, 'start', { v: Math.round(t * 50) });
  cue(T.card + 0.9, 'pop', -24, 'start', { v: 5 }); cue(T.card + 1.02, 'pop', -24, 'start', { v: 6 });
  cue(T.cursor + 0.3, 'swish', -30, 'peak', { v: 9 });
  cue(T.click, 'click', -13); cue(T.click + 0.05, 'blip', -27);
  cue(T.flip + 0.45, 'whoosh', -17, 'peak', { v: 2 }); cue(T.flip + 0.9, 'hit', -18, 'peak');
  CUES.sort((a, b) => a.t - b.t);
}

/* ------------------------------------------------------------------ build */
function buildShade() {   // soft window-light shadows for the grey section pages
  const s = surf(W + 400, H + 300), g = s.g;
  g.filter = 'blur(38px)'; g.fillStyle = 'rgba(40,40,30,0.10)';
  for (let k = 0; k < 4; k++) {
    const x = 120 + k * 520;
    g.beginPath(); g.moveTo(x, -50); g.lineTo(x + 260, -50); g.lineTo(x + 700, H + 250); g.lineTo(x + 440, H + 250); g.closePath(); g.fill();
  }
  g.fillStyle = 'rgba(40,40,30,0.07)';
  for (let k = 0; k < 3; k++) { const y = 260 + k * 330; g.beginPath(); g.moveTo(0, y); g.lineTo(W + 400, y - 160); g.lineTo(W + 400, y - 110); g.lineTo(0, y + 50); g.closePath(); g.fill(); }
  L.shade = s.c;
}
function layout(clips) {   // 1-3 cards in a row under the title; portrait cards tall, landscape cards wide
  const asp = clips.map(c => c.w / c.h), n = clips.length;
  const lw = n === 1 ? 1100 : n === 2 ? 800 : 560, ph = n === 3 ? 600 : 640;
  let sz = asp.map(a => (a < 1 ? [ph * a, ph] : [lw, lw / a]));
  const gap = n === 2 ? 120 : 80, total = sz.reduce((s, [w]) => s + w, 0) + gap * (n - 1), k = Math.min(1, 1660 / total);
  sz = sz.map(([w, h]) => [w * k, h * k]);
  const offs = n === 1 ? [0] : n === 2 ? (asp[0] < 1 && asp[1] >= 1 ? [-30, 70] : [50, -20]) : [-10, 22, -6];
  let x = (W - (sz.reduce((s, [w]) => s + w, 0) + gap * k * (n - 1))) / 2;
  return sz.map(([w, h], i) => { const r = { x, y: 610 - h / 2 + offs[i], w, h }; x += w + gap * k; return r; });
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
  cardBase(g); g.font = font(500, fitPx(L.P.back, 500, 46, 1000)); g.fillStyle = '#e8e8e8'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText(L.P.back, 650, 360); reset(g);
}

/* ------------------------------------------------------------------ drawing: backgrounds */
function drawYellow(g, t) {
  const q = g.createRadialGradient(W * 0.62 + 60 * Math.sin(t * 0.3), H * 0.56, 40, W * 0.62, H * 0.56, W * 1.05);
  q.addColorStop(0, COL.bg[0]); q.addColorStop(0.45, COL.bg[1]); q.addColorStop(1, COL.bg[2]);
  g.fillStyle = q; g.fillRect(0, 0, W, H);
  const p = eo3(lin(t, 0, 1.3));
  for (const [c0, c1, cy, r] of [[-760, -340, 560, 720], [W + 760, W + 250, 470, 660]]) {
    const cx = mix(c0, c1, p) + 22 * Math.sin(t * 0.5 + r), gr = g.createRadialGradient(cx, cy, r * 0.2, cx, cy, r);
    gr.addColorStop(0, 'rgba(255,250,170,0.10)'); gr.addColorStop(0.93, 'rgba(110,102,0,0.20)'); gr.addColorStop(1, 'rgba(255,248,160,0.40)');
    g.fillStyle = gr; g.beginPath(); g.arc(cx, cy, r, 0, 7); g.fill();
  }
}
function drawHook(g, t) {
  drawYellow(g, t);
  const up = eo3(lin(t, T.big, T.big + 0.45));
  words(g, TX.hook[0], W / 2, 500 - 70 * up, T.hook, T.hookStep, t, { wt: 500, px: 44, fill: '#ffffff', rise: 10 });
  const bw = splitWords(TX.hook[1]); g.font = font(900, L.bigPx);
  const sp = g.measureText(' ').width, wd = bw.map(s => g.measureText(s).width), total = wd.reduce((a, b) => a + b, 0) + sp * (bw.length - 1);
  let x = W / 2 - total / 2;
  bw.forEach((s, i) => {
    const e = lin(t, T.big + i * T.bigStep, T.big + i * T.bigStep + 0.4);
    if (e > 0) {
      const k = eoBack(e, 2.2);
      g.save(); g.globalAlpha = clamp(e * 3); g.translate(x + wd[i] / 2, 590 + (1 - eo3(e)) * 60); g.scale(mix(0.7, 1, k), mix(0.7, 1, k));
      g.font = font(900, L.bigPx); g.fillStyle = '#ffffff'; g.textAlign = 'center'; g.shadowColor = 'rgba(70,64,0,0.35)'; g.shadowBlur = 24; g.shadowOffsetY = 6;
      g.fillText(s, 0, 0); g.restore();
    }
    x += wd[i] + sp;
  });
}

/* ------------------------------------------------------------------ drawing: hero page */
function drawAvatar(g, cx, cy, r, photo) {
  const q = g.createRadialGradient(cx - r * 0.35, cy - r * 0.4, r * 0.1, cx, cy, r);
  q.addColorStop(0, COL.bg[0]); q.addColorStop(1, COL.bg[1]);
  g.fillStyle = q; g.beginPath(); g.arc(cx, cy, r, 0, 7); g.fill();
  if (L.avatar && photo > 0) {
    g.save(); g.beginPath(); g.arc(cx, cy, r, 0, 7); g.clip(); g.globalAlpha = photo;
    if (CFG.avatarStyle === 'duotone') { g.filter = 'grayscale(1) contrast(1.15)'; g.globalCompositeOperation = 'multiply'; }
    drawCover(g, L.avatar, cx - r, cy - r, 2 * r, 2 * r, 0.3); g.restore();
    if (CFG.avatarStyle !== 'duotone') { g.save(); g.globalAlpha = photo; g.strokeStyle = COL.bg[0]; g.lineWidth = Math.max(2, r * 0.045); g.beginPath(); g.arc(cx, cy, r - g.lineWidth / 2, 0, 7); g.stroke(); g.restore(); }
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
  // avatar: pops as a small disc during the wipe, then grows into place
  const pop = eoBack(lin(t, T.avatar, T.avatar + 0.35)), grow = eio3(lin(t, T.hero, T.hero + 0.55));
  const cx = mix(0.21 * W, 370, grow), cy = mix(0.34 * H, 540, grow) + dy, r = mix(62 * pop, 290, grow);
  if (r > 1) drawAvatar(g, cx, cy, r, lin(t, T.hero + 0.3, T.hero + 0.75));
  const bx = 1350;
  // badge
  const bp = eo3(lin(t, T.badge, T.badge + 0.35));
  if (bp > 0) {
    g.save(); g.globalAlpha = bp; g.font = font(500, 30); const tw = g.measureText(TX.badge).width, bw = tw + 112, bh = 64;
    g.translate(bx, 300 + dy); g.scale(mix(0.9, 1, bp), mix(0.9, 1, bp));
    g.strokeStyle = COL.ink; g.lineWidth = 3; g.beginPath(); g.roundRect(-bw / 2, -bh / 2, bw, bh, bh / 2); g.stroke();
    g.fillStyle = COL.ink; star(g, -bw / 2 + 42, 0, 15); g.textBaseline = 'middle'; g.fillText(TX.badge, -bw / 2 + 72, 2); g.restore();
  }
  words(g, TX.hello, bx, 505 + dy, T.hello, T.helloStep, t, { wt: 800, px: L.helloPx, fill: COL.ink, rise: 16, blur: 6 });
  // roles, split by thin bars
  g.font = font(500, 36); const rw = TX.roles.map(s => g.measureText(s).width), gap = 44, total = rw.reduce((a, b) => a + b, 0) + gap * (rw.length - 1);
  let x = bx - total / 2;
  TX.roles.forEach((s, i) => {
    const e = eo3(lin(t, T.roles + i * T.rolesStep, T.roles + i * T.rolesStep + 0.3));
    if (e > 0) {
      g.save(); g.globalAlpha = e; g.font = font(500, 36); g.fillStyle = '#2a2a2a'; g.fillText(s, x, 592 + dy + (1 - e) * 10);
      if (i > 0) { g.fillStyle = COL.ink; g.fillRect(x - gap / 2 - 1, 556 + dy, 2.5, 46 * e); }
      g.restore();
    }
    x += rw[i] + gap;
  });
  // button: a black pill that grows from a dot, its label, then the arrow in a white circle
  const be = eoX(lin(t, T.button, T.button + 0.45));
  if (be > 0) {
    g.font = font(500, 32); const lw = g.measureText(TX.button).width, fw = lw + 160, bh = 88, w = mix(bh, fw, be);
    const left = bx - w / 2, cyb = 770 + dy;
    g.fillStyle = '#0d0d0d'; g.beginPath(); g.roundRect(left, cyb - bh / 2, w, bh, bh / 2); g.fill();
    g.save(); g.beginPath(); g.roundRect(left, cyb - bh / 2, w, bh, bh / 2); g.clip();
    words(g, TX.button, left + 46, cyb + 11, T.button + 0.3, 0.1, t, { wt: 500, px: 32, fill: '#ffffff', align: 'left', rise: 6, blur: 4 });
    g.restore();
    const ae = eoBack(lin(t, T.arrow - 0.35, T.arrow));
    if (ae > 0) {
      const ax = left + w - 50, ar = 27 * ae;
      g.fillStyle = '#ffffff'; g.beginPath(); g.arc(ax, cyb, ar, 0, 7); g.fill();
      const fly = eiX(lin(t, T.heroOut - 0.55, T.heroOut));     // the arrow leaves the button and shoots up
      arrowUp(g, ax, cyb - fly * 1100, 28 * ae, fly > 0.02 ? COL.ink : '#0d0d0d');
    }
  }
}

/* ------------------------------------------------------------------ drawing: work sections */
function titleFill(g, y) { const q = g.createLinearGradient(0, y - 60, 0, y); q.addColorStop(0, COL.title[1]); q.addColorStop(1, COL.title[0]); return q; }
function drawCard(g, c, r, x, y, lt) {
  g.save(); g.shadowColor = 'rgba(0,0,0,0.26)'; g.shadowBlur = 38; g.shadowOffsetY = 18;
  g.fillStyle = '#ffffff'; g.beginPath(); g.roundRect(x, y, r.w, r.h, 26); g.fill(); g.restore();
  const img = c.kind === 'image' ? c.img : CUR.get(c.id);
  g.save(); g.beginPath(); g.roundRect(x + 6, y + 6, r.w - 12, r.h - 12, 21); g.clip();
  if (img) drawCover(g, img, x + 6, y + 6, r.w - 12, r.h - 12, 0.3, c.kind === 'image' ? 1 + 0.035 * Math.max(0, lt) : 1);
  else { g.fillStyle = '#222'; g.fillRect(x, y, r.w, r.h); }
  g.restore();
}
function drawSection(g, k, t, dy) {
  const S = L.secs[k], s0 = T.secIn[k] - SCROLL;
  g.save(); g.beginPath(); g.rect(0, dy, W, H); g.clip();
  g.fillStyle = COL.grey; g.fillRect(0, dy, W, H);
  g.drawImage(L.shade, -180 + 40 * Math.sin(t * 0.15), -120);
  words(g, S.title, W / 2, 168 + dy, s0 + 0.35, 0.12, t, { wt: 800, px: 70, fill: titleFill(g, 168 + dy), rise: 16, blur: 6 });
  S.rects.forEach((r, i) => {
    const e = eoBack(lin(t, s0 + 0.3 + i * 0.12, s0 + 1.0 + i * 0.12), 1.3);
    if (e <= 0) return;
    drawCard(g, S.clips[i], r, r.x, r.y + dy + (1 - e) * 420 + 8 * Math.sin(t * 1.4 + i * 1.9), t - s0);
  });
  g.restore();
}
function scrollY(t) { let y = 0; for (const s of T.secIn) y += H * eio3(lin(t, s - SCROLL, s)); return y; }

/* ------------------------------------------------------------------ drawing: profile card */
function cardBase(g) {
  const q = g.createLinearGradient(0, 0, 0, 720); q.addColorStop(0, '#1d1d1d'); q.addColorStop(1, '#0a0a0a');
  g.fillStyle = q; g.beginPath(); g.roundRect(0, 0, 1300, 720, 60); g.fill();
  g.strokeStyle = 'rgba(255,255,255,0.07)'; g.lineWidth = 2; g.stroke();
}
function drawCardFront(t) {
  const g = CARDF.g; reset(g); g.clearRect(0, 0, 1300, 720); cardBase(g);
  const a = lin(t, T.card + 0.4, T.card + 0.75), P = L.P;
  if (a <= 0) return;
  g.globalAlpha = a;
  g.fillStyle = '#ffffff'; g.beginPath(); g.arc(235, 360, 158, 0, 7); g.fill();
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
    g.save(); g.beginPath(); g.rect(x, y, w, h); g.clip(); g.fillStyle = '#ffffff'; g.font = font(500, 34); g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText(done > 0.5 ? P.clicked : label, x + 165, y + h / 2 + 2); g.restore();
  });
  g.globalAlpha = 1;
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
function drawCardScene(g, t) {
  drawYellow(g, t);
  const cx = W / 2, cy = H / 2, pw = eoBack(lin(t, T.card, T.card + 0.55), 1.4), ph = eoBack(lin(t, T.card + 0.12, T.card + 0.7), 1.4);
  const w = mix(24, 1300, pw), h = mix(24, 720, ph);
  if (pw <= 0) return;
  g.save(); g.shadowColor = 'rgba(40,36,0,0.45)'; g.shadowBlur = 60; g.shadowOffsetY = 26;
  const theta = Math.PI * eio3(lin(t, T.flip, T.flip + 0.9));
  if (theta <= 0) {
    drawCardFront(t);
    if (pw < 1 || ph < 1) {    // still popping: a black rounded shape, then the face once it is full size
      g.fillStyle = '#101010'; g.beginPath(); g.roundRect(cx - w / 2, cy - h / 2, w, h, Math.min(60, h / 2)); g.fill();
    } else g.drawImage(CARDF.c, cx - 650, cy - 360);
  } else {
    g.shadowColor = 'transparent';
    if (theta < Math.PI / 2) { drawCardFront(t); drawFlip(g, CARDF.c, cx, cy, theta); } else drawFlip(g, CARDB.c, cx, cy, theta - Math.PI);
  }
  g.restore();
  // the cursor glides to the first button, clicks it (ripple), then leaves before the flip
  const m = eio3(lin(t, T.cursor, T.click - 0.05)), gone = lin(t, T.flip - 0.3, T.flip);
  if (m > 0 && gone < 1) {
    const bx = cx - 650 + 470 + 150, by = cy - 360 + 525;
    const x = mix(1560, bx, m), y = mix(1060, by, m) + 10 * Math.sin(m * Math.PI), press = 1 - 0.18 * Math.sin(Math.PI * lin(t, T.click - 0.06, T.click + 0.1));
    const rp = lin(t, T.click, T.click + 0.45);
    if (rp > 0 && rp < 1) { g.strokeStyle = `rgba(255,255,255,${(0.7 * (1 - rp)).toFixed(3)})`; g.lineWidth = 4; g.beginPath(); g.arc(bx, by, 20 + 70 * eo3(rp), 0, 7); g.stroke(); }
    g.globalAlpha = 1 - gone; cursor(g, x, y, 1.6 * press); g.globalAlpha = 1;
  }
}

/* ------------------------------------------------------------------ the frame */
function frame(g, t) {
  reset(g); g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
  if (t < T.wipe + 0.6) {
    drawHook(g, t);
    const p = lin(t, T.wipe, T.wipe + 0.55);
    if (p > 0) { g.save(); g.beginPath(); g.arc(W / 2, H * 1.35, 2400 * eio3(p), 0, 7); g.clip(); drawHero(g, t, 0); g.restore(); }
  } else if (t < T.ctaWipe + 1) {
    const sy = scrollY(t);
    if (sy < H) drawHero(g, t, -sy);
    L.secs.forEach((_, k) => { const dy = (k + 1) * H - sy; if (dy > -H && dy < H) drawSection(g, k, t, dy); });
    const p = lin(t, T.ctaWipe, T.ctaWipe + 0.9);     // a yellow light blooms from the bottom-left and takes the frame
    if (p > 0) {
      const R = 2500 * eio3(p), ox = W * 0.12, oy = H * 1.15;
      reset(BUF.g); drawYellow(BUF.g, t); drawCTA(BUF.g, t, false);
      g.save(); g.beginPath(); g.arc(ox, oy, R, 0, 7); g.clip(); g.drawImage(BUF.c, 0, 0); g.restore();
      const gl = g.createRadialGradient(ox, oy, Math.max(0, R - 300), ox, oy, R + 60);
      gl.addColorStop(0, 'rgba(248,238,80,0)'); gl.addColorStop(0.82, 'rgba(250,242,110,0.85)'); gl.addColorStop(1, 'rgba(250,242,110,0)');
      g.fillStyle = gl; g.fillRect(0, 0, W, H);
    }
  } else if (t < T.card) { drawYellow(g, t); drawCTA(g, t, true); }
  else drawCardScene(g, t);
  const fo = lin(t, DUR - 0.35, DUR - 0.02);
  if (fo > 0) { reset(g); g.fillStyle = `rgba(0,0,0,${eio3(fo).toFixed(3)})`; g.fillRect(0, 0, W, H); }
}
function drawCTA(g, t) {
  const two = !!TX.cta[1];
  words(g, TX.cta[0], W / 2, 555, T.cta, 0.15, t, { wt: 500, px: L.ctaPx, fill: '#ffffff', rise: 12, out: two ? T.cta2 - 0.3 : null, shadow: 'rgba(70,64,0,0.35)' });
  if (two) words(g, TX.cta[1], W / 2, 555, T.cta2, 0.15, t, { wt: 500, px: L.ctaPx, fill: '#ffffff', rise: 12, out: T.card - 0.25, shadow: 'rgba(70,64,0,0.35)' });
}
async function prepare(t) {   // load the clip frames this frame shows
  CUR.clear();
  const sy = scrollY(t), jobs = [];
  L.secs.forEach((S, k) => {
    const dy = (k + 1) * H - sy; if (!(dy > -H && dy < H) || t > T.ctaWipe + 1) return;
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
  COL = { ...DEF_COL, ...(CFG.colors || {}) };
  L.P = { ...DEF_PROFILE, ...(CFG.profile || {}) };
  FONT = CFG.lang === 'km' ? '"Kantumruy", sans-serif' : 'system-ui, -apple-system, "Helvetica Neue", Arial, "Kantumruy", sans-serif';
  window.bootStage = 'fonts';
  await Promise.all(['400', '500', '700', '800', '900'].map(w => document.fonts.load(`${w} 40px "Kantumruy"`)));
  BUF = surf(W, H); CARDF = surf(1300, 720);
  window.bootStage = 'pictures';
  if (MAN.avatar) L.avatar = await loadImg('/proj/assets/' + MAN.avatar);
  if (MAN.logo) L.logo = await loadImg('/proj/assets/' + MAN.logo);
  await buildSections();
  plan();
  L.bigPx = fitPx(TX.hook[1], 900, CFG.lang === 'km' ? 120 : 140, 1500);
  L.helloPx = fitPx(TX.hello, 800, CFG.lang === 'km' ? 92 : 108, 1000);
  L.ctaPx = Math.min(fitPx(TX.cta[0], 500, 46, 1500), fitPx(TX.cta[1] || ' ', 500, 46, 1500));
  buildShade(); buildCardBack(); buildCues();
  window.bootStage = 'done';
  window.DUR = DUR;
  window.CUES = CUES;
  window.SECTIONS = { intro: 0, main: T.secIn.length ? T.secIn[0] - SCROLL : T.heroOut, cta: T.ctaWipe, card: T.card, end: DUR };
  window.PREVIEW_TIMES = [0.9, T.big + 0.9, T.wipe + 0.35, T.arrow + 0.5, ...T.secIn.map(s => s + 0.9), T.ctaWipe + 0.45,
    T.cta + 1.0, T.card + 1.2, T.click + 0.4, T.flip + 0.45, DUR - 0.6].slice(0, 16);
  window.render = async t => { await prepare(t); frame(X, t); };
}
