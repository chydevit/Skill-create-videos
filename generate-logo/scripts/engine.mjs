// Engine for the generate-logo scenes: config, logo analysis (alpha, parts, palette, text row),
// layout, easing, distance fields and frame helpers shared by every style in styles/.
export const DUR = 5;
export let W = 1920, H = 1080, CX = 960, CY = 540;
export const CFG = {};
export let L = null;          // the analysed logo (see analyse())

// ---------- maths ----------
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, t) => a + (b - a) * t;
export const prog = (t, [a, b]) => clamp((t - a) / (b - a));
export const smooth = x => { x = clamp(x); return x * x * (3 - 2 * x); };
export function bezier(x1, y1, x2, y2) {
  const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx;
  const cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
  const sx = s => ((ax * s + bx) * s + cx) * s;
  const sy = s => ((ay * s + by) * s + cy) * s;
  return x => {
    if (x <= 0) return 0;
    if (x >= 1) return 1;
    let lo = 0, hi = 1, s = x;
    for (let i = 0; i < 40; i++) { if (sx(s) < x) lo = s; else hi = s; s = (lo + hi) / 2; }
    return sy(s);
  };
}
export const easeInOut = bezier(0.65, 0, 0.35, 1);
export const easeOut = bezier(0.2, 0, 0, 1);
export const easeIn = bezier(0.5, 0, 0.9, 0.5);
export const back = (x, s = 1.6) => { x = clamp(x); if (x >= 1) return 1; const u = x - 1; return 1 + (s + 1) * u * u * u + s * u * u; };
export const spring = (t, t0, amp, freq, decay) => t < t0 ? 0 : amp * Math.exp(-(t - t0) * decay) * Math.sin(2 * Math.PI * freq * (t - t0));
export const BOUNCE_HITS = [1 / 2.75, 2 / 2.75, 2.5 / 2.75, 1];
export function bounceOut(x) {
  x = clamp(x);
  const n = 7.5625, d = 2.75;
  if (x < 1 / d) return n * x * x;
  if (x < 2 / d) return n * (x -= 1.5 / d) * x + 0.75;
  if (x < 2.5 / d) return n * (x -= 2.25 / d) * x + 0.9375;
  return n * (x -= 2.625 / d) * x + 0.984375;
}
export function mulberry32(a) {
  return function () {
    a |= 0; a = a + 0x6D2B79F5 | 0;
    let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}
export function canvas(w, h) { const cv = document.createElement('canvas'); cv.width = Math.max(1, Math.ceil(w)); cv.height = Math.max(1, Math.ceil(h)); return cv; }
export function load(src) { return new Promise((res, rej) => { const i = new Image(); i.onload = () => res(i); i.onerror = () => rej(new Error('could not load ' + src)); i.src = src; }); }
export const rgb = c => `rgb(${c.map(v => Math.round(v)).join(',')})`;
export const rgba = (c, a) => `rgba(${c.map(v => Math.round(v)).join(',')},${a})`;
export const lum = c => (0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]) / 255;
export const mix = (a, b, t) => a.map((v, i) => lerp(v, b[i], t));
export const panOf = x => clamp((x - CX) / CX * 0.7, -0.8, 0.8);

// ---------- distance fields + colour fill ----------
const INF = 1e20;
function edt1d(f, n, d, v, z) {
  let k = 0; v[0] = 0; z[0] = -INF; z[1] = INF;
  for (let q = 1; q < n; q++) {
    let s;
    do { const p = v[k]; s = ((f[q] + q * q) - (f[p] + p * p)) / (2 * q - 2 * p); } while (s <= z[k] && --k >= 0);
    k++; v[k] = q; z[k] = s; z[k + 1] = INF;
  }
  k = 0;
  for (let q = 0; q < n; q++) { while (z[k + 1] < q) k++; const p = v[k]; d[q] = (q - p) * (q - p) + f[p]; }
}
// Exact Euclidean distance to the nearest seed pixel (Felzenszwalb & Huttenlocher).
export function edt(seed, w, h) {
  const g = new Float64Array(w * h), n = Math.max(w, h);
  for (let i = 0; i < w * h; i++) g[i] = seed[i] ? 0 : INF;
  const f = new Float64Array(n), d = new Float64Array(n), v = new Int32Array(n), z = new Float64Array(n + 1);
  for (let x = 0; x < w; x++) {
    for (let y = 0; y < h; y++) f[y] = g[y * w + x];
    edt1d(f, h, d, v, z);
    for (let y = 0; y < h; y++) g[y * w + x] = d[y];
  }
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) f[x] = g[y * w + x];
    edt1d(f, w, d, v, z);
    for (let x = 0; x < w; x++) g[y * w + x] = Math.sqrt(d[x]);
  }
  return g;
}
// Pull-push: spread known colours (weight 1) smoothly into unknown pixels.
function pullPush(col, wt, w, h) {
  if (w === 1 && h === 1) { const s = wt[0] || 1; return Float32Array.of(col[0] / s, col[1] / s, col[2] / s); }
  const w2 = Math.ceil(w / 2), h2 = Math.ceil(h / 2);
  const c2 = new Float32Array(w2 * h2 * 3), a2 = new Float32Array(w2 * h2);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const i = y * w + x, j = (y >> 1) * w2 + (x >> 1);
    a2[j] += wt[i]; c2[j * 3] += col[i * 3]; c2[j * 3 + 1] += col[i * 3 + 1]; c2[j * 3 + 2] += col[i * 3 + 2];
  }
  for (let j = 0; j < w2 * h2; j++) if (a2[j] > 1) { const k = 1 / a2[j]; a2[j] = 1; c2[j * 3] *= k; c2[j * 3 + 1] *= k; c2[j * 3 + 2] *= k; }
  const coarse = pullPush(c2, a2, w2, h2);
  const out = new Float32Array(w * h * 3);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const i = y * w + x;
    const u = clamp((x - 0.5) / 2, 0, w2 - 1), v = clamp((y - 0.5) / 2, 0, h2 - 1);
    const u0 = Math.floor(u), v0 = Math.floor(v), u1 = Math.min(w2 - 1, u0 + 1), v1 = Math.min(h2 - 1, v0 + 1);
    const fu = u - u0, fv = v - v0, a = clamp(wt[i]);
    for (let c = 0; c < 3; c++) {
      const up = lerp(lerp(coarse[(v0 * w2 + u0) * 3 + c], coarse[(v0 * w2 + u1) * 3 + c], fu),
        lerp(coarse[(v1 * w2 + u0) * 3 + c], coarse[(v1 * w2 + u1) * 3 + c], fu), fv);
      out[i * 3 + c] = col[i * 3 + c] + (1 - a) * up;
    }
  }
  return out;
}

// ---------- logo analysis ----------
function maxFilter(src, w, h, r) {
  const tmp = new Float32Array(w * h), out = new Float32Array(w * h);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    let m = 0;
    for (let k = Math.max(0, x - r); k <= Math.min(w - 1, x + r); k++) m = Math.max(m, src[y * w + k]);
    tmp[y * w + x] = m;
  }
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    let m = 0;
    for (let k = Math.max(0, y - r); k <= Math.min(h - 1, y + r); k++) m = Math.max(m, tmp[k * w + x]);
    out[y * w + x] = m;
  }
  return out;
}

// Straight-alpha colours + alpha for the logo. Uses the PNG's alpha if it has one; otherwise keys out the
// flat background (median border colour), estimating edge coverage against the nearby solid colour.
function extractAlpha(px, w, h) {
  const N = w * h, A = new Float32Array(N), F = new Float32Array(N * 3);
  let transp = 0;
  for (let i = 0; i < N; i++) if (px[i * 4 + 3] < 250) transp++;
  if (transp > N * 0.01) {
    for (let i = 0; i < N; i++) { A[i] = px[i * 4 + 3] / 255; F[i * 3] = px[i * 4]; F[i * 3 + 1] = px[i * 4 + 1]; F[i * 3 + 2] = px[i * 4 + 2]; }
    return { A, F, keyed: null };
  }
  const border = [[], [], []];
  const band = Math.max(2, Math.round(Math.min(w, h) * 0.01));
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    if (x >= band && y >= band && x < w - band && y < h - band) continue;
    const i = (y * w + x) * 4;
    border[0].push(px[i]); border[1].push(px[i + 1]); border[2].push(px[i + 2]);
  }
  const med = a => { a.sort((p, q) => p - q); return a[a.length >> 1]; };
  const B = border.map(med);
  let noise = 0, nb = 0;
  for (let y = 0; y < h; y += 3) for (const x of [0, w - 1]) { const i = (y * w + x) * 4; noise += Math.max(...[0, 1, 2].map(c => Math.abs(px[i + c] - B[c]))); nb++; }
  noise /= Math.max(1, nb);
  const D = new Float32Array(N);
  for (let i = 0; i < N; i++) D[i] = Math.hypot(px[i * 4] - B[0], px[i * 4 + 1] - B[1], px[i * 4 + 2] - B[2]);
  const lo = Math.min(60, 3 * noise + 8);
  const Dm = maxFilter(D, w, h, 2);
  for (let i = 0; i < N; i++) {
    const a = clamp((D[i] - lo) / (Math.max(Dm[i], lo + 25) - lo));
    A[i] = a;
    for (let c = 0; c < 3; c++) F[i * 3 + c] = a > 0 ? clamp(B[c] + (px[i * 4 + c] - B[c]) / a, 0, 255) : B[c];
  }
  return { A, F, keyed: B };
}

function toCanvas(A, F, w, h, x0 = 0, y0 = 0, cw = w, ch = h) {
  const cv = canvas(cw, ch), g = cv.getContext('2d'), img = g.createImageData(cw, ch), d = img.data;
  for (let y = 0; y < ch; y++) for (let x = 0; x < cw; x++) {
    const s = (y + y0) * w + (x + x0), o = (y * cw + x) * 4;
    d[o] = F[s * 3]; d[o + 1] = F[s * 3 + 1]; d[o + 2] = F[s * 3 + 2]; d[o + 3] = A[s] * 255;
  }
  g.putImageData(img, 0, 0);
  return cv;
}

function palette(A, F, n) {
  const pts = [];
  for (let i = 0; i < n; i += 3) if (A[i] > 0.9) pts.push([F[i * 3], F[i * 3 + 1], F[i * 3 + 2]]);
  if (!pts.length) return [[40, 40, 40]];
  const k = Math.min(5, pts.length), rnd = mulberry32(3);
  let cen = Array.from({ length: k }, () => pts[Math.floor(rnd() * pts.length)].slice());
  let cnt;
  for (let it = 0; it < 12; it++) {
    const sum = cen.map(() => [0, 0, 0]); cnt = cen.map(() => 0);
    for (const p of pts) {
      let best = 0, bd = Infinity;
      cen.forEach((c, j) => { const d = (p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2 + (p[2] - c[2]) ** 2; if (d < bd) { bd = d; best = j; } });
      sum[best][0] += p[0]; sum[best][1] += p[1]; sum[best][2] += p[2]; cnt[best]++;
    }
    cen = cen.map((c, j) => cnt[j] ? sum[j].map(v => v / cnt[j]) : c);
  }
  return cen.map((c, j) => ({ c, w: cnt[j] / pts.length })).filter(o => o.w > 0.03).sort((a, b) => b.w - a.w).map(o => o.c);
}

// Optional wordmark: "Pharm|Kulen" sets the two segments in two colours.
async function composeText(logoCv, cfg, pal, dark) {
  const font = cfg.font || 'Arial', weight = cfg.fontWeight || 'bold';
  await document.fonts.load(`${weight} 100px ${JSON.stringify(font)}`).catch(() => {});
  const segs = String(cfg.text).split('|');
  const sat = c => (Math.max(...c) - Math.min(...c)) / 255;
  const byDark = pal.slice().sort((a, b) => lum(a) - lum(b));
  const bright = pal.slice().sort((a, b) => (sat(b) + lum(b)) - (sat(a) + lum(a)))[0];
  const cols = cfg.textColors && cfg.textColors.length ? cfg.textColors
    : dark ? ['#ffffff', rgb(bright)] : [rgb(byDark[0]), rgb(bright)];
  const lh = logoCv.height, m = canvas(10, 10).getContext('2d');
  m.font = `${weight} 100px ${JSON.stringify(font)}`;
  const cap100 = m.measureText('H').actualBoundingBoxAscent || 72;
  const size = lh * (cfg.textScale || 0.37) / cap100 * 100;
  m.font = `${weight} ${size}px ${JSON.stringify(font)}`;
  const widths = segs.map(s => m.measureText(s).width);
  const tw = widths.reduce((a, b) => a + b, 0), gap = lh * 0.18;
  const desc = Math.max(...segs.map(s => m.measureText(s).actualBoundingBoxDescent || 0));
  const out = canvas(logoCv.width + gap + tw + 8, Math.max(lh, lh / 2 + size * 0.75 + desc + 8));
  const g = out.getContext('2d');
  g.drawImage(logoCv, 0, (out.height - lh) / 2);
  g.font = m.font; g.textBaseline = 'alphabetic';
  const cap = m.measureText('H').actualBoundingBoxAscent;
  let x = logoCv.width + gap;
  segs.forEach((s, i) => { g.fillStyle = cols[i % cols.length]; g.fillText(s, x, out.height / 2 + cap / 2); x += widths[i]; });
  return out;
}

// Connected shapes (8-connected, alpha >= 0.5), edge pixels joined to their neighbours, specks merged.
function findParts(A, w, h) {
  const N = w * h, lab = new Int32Array(N).fill(-1), areas = [];
  const q = new Int32Array(N);
  for (let s = 0; s < N; s++) {
    if (lab[s] >= 0 || A[s] < 0.5) continue;
    const id = areas.length; let head = 0, tail = 0, area = 0;
    q[tail++] = s; lab[s] = id;
    while (head < tail) {
      const i = q[head++], x = i % w, y = (i / w) | 0; area++;
      for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
        const xx = x + dx, yy = y + dy;
        if (xx < 0 || yy < 0 || xx >= w || yy >= h) continue;
        const j = yy * w + xx;
        if (lab[j] < 0 && A[j] >= 0.5) { lab[j] = id; q[tail++] = j; }
      }
    }
    areas.push(area);
  }
  for (let pass = 0; pass < 3; pass++) {                // soft edge pixels take a neighbour's label
    const next = lab.slice();
    for (let i = 0; i < N; i++) {
      if (lab[i] >= 0 || A[i] <= 0) continue;
      const x = i % w, y = (i / w) | 0;
      for (let dy = -1; dy <= 1 && next[i] < 0; dy++) for (let dx = -1; dx <= 1; dx++) {
        const xx = x + dx, yy = y + dy;
        if (xx >= 0 && yy >= 0 && xx < w && yy < h && lab[yy * w + xx] >= 0) { next[i] = lab[yy * w + xx]; break; }
      }
    }
    lab.set(next);
  }
  const total = areas.reduce((a, b) => a + b, 0), keep = areas.map(a => a >= Math.max(12, total * 0.0004));
  const stats = areas.map(() => ({ x0: w, y0: h, x1: 0, y1: 0, sx: 0, sy: 0, sw: 0 }));
  for (let i = 0; i < N; i++) {
    const l = lab[i]; if (l < 0) continue;
    const s = stats[l], x = i % w, y = (i / w) | 0;
    s.x0 = Math.min(s.x0, x); s.x1 = Math.max(s.x1, x); s.y0 = Math.min(s.y0, y); s.y1 = Math.max(s.y1, y);
    s.sx += x * A[i]; s.sy += y * A[i]; s.sw += A[i];
  }
  const remap = areas.map((a, i) => {                   // merge specks into the nearest kept shape
    if (keep[i]) return i;
    const cx = stats[i].sx / stats[i].sw, cy = stats[i].sy / stats[i].sw;
    let best = i, bd = Infinity;
    areas.forEach((b, j) => { if (!keep[j]) return; const s = stats[j]; const d = Math.hypot(clamp(cx, s.x0, s.x1) - cx, clamp(cy, s.y0, s.y1) - cy); if (d < bd) { bd = d; best = j; } });
    return best;
  });
  for (let i = 0; i < N; i++) if (lab[i] >= 0) lab[i] = remap[lab[i]];
  return { lab, ids: areas.map((_, i) => i).filter(i => keep[i]) };
}

function buildPart(id, lab, A, F, w, h, margin) {
  let x0 = w, y0 = h, x1 = 0, y1 = 0, sx = 0, sy = 0, sw = 0, lsum = 0;
  for (let i = 0; i < w * h; i++) {
    if (lab[i] !== id) continue;
    const x = i % w, y = (i / w) | 0;
    x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y);
    sx += x * A[i]; sy += y * A[i]; sw += A[i];
    lsum += A[i] * lum([F[i * 3], F[i * 3 + 1], F[i * 3 + 2]]);
  }
  const rx = x0 - margin, ry = y0 - margin, pw = x1 - x0 + 1 + 2 * margin, ph = y1 - y0 + 1 + 2 * margin;
  const PA = new Float32Array(pw * ph), PF = new Float32Array(pw * ph * 3);
  for (let y = 0; y < ph; y++) for (let x = 0; x < pw; x++) {
    const gx = x + rx, gy = y + ry;
    if (gx < 0 || gy < 0 || gx >= w || gy >= h) continue;
    const s = gy * w + gx, o = y * pw + x;
    if (lab[s] !== id) continue;
    PA[o] = A[s]; PF[o * 3] = F[s * 3]; PF[o * 3 + 1] = F[s * 3 + 1]; PF[o * 3 + 2] = F[s * 3 + 2];
  }
  return {
    id, x0, y0, x1, y1, bw: x1 - x0 + 1, bh: y1 - y0 + 1, area: sw, cx: sx / sw, cy: sy / sw, lum: lsum / sw,
    rx, ry, w: pw, h: ph, A: PA, F: PF, sprite: toCanvas(PA, PF, pw, ph),
  };
}

// The palette colour that covers most of a part.
export function mainColour(p) {
  const cnt = L.palette.map(() => 0);
  for (let i = 0; i < p.w * p.h; i += 2) {
    if (p.A[i] < 0.9) continue;
    let best = 0, bd = Infinity;
    L.palette.forEach((c, j) => { const d = (p.F[i * 3] - c[0]) ** 2 + (p.F[i * 3 + 1] - c[1]) ** 2 + (p.F[i * 3 + 2] - c[2]) ** 2; if (d < bd) { bd = d; best = j; } });
    cnt[best]++;
  }
  return L.palette[cnt.indexOf(Math.max(...cnt))];
}

// Text row: 3+ smaller shapes of similar height lined up on one row, beside or below the main shape
// (a small shape tucked inside the main shape's area, like a dot in a symbol, stays part of the mark).
function markText(parts) {
  const maxA = Math.max(...parts.map(p => p.area));
  const main = parts.find(p => p.area === maxA);
  const outside = p => p.x0 > main.x1 || p.x1 < main.x0 || p.y0 > main.y1 || p.y1 < main.y0;
  const small = parts.filter(p => p.area < maxA * 0.35 && outside(p));
  if (small.length < 3) return;
  const hs = small.map(p => p.bh).sort((a, b) => a - b), mh = hs[hs.length >> 1];
  const rowY = small.map(p => p.y1).sort((a, b) => a - b)[small.length >> 1];
  const row = small.filter(p => p.bh > mh * 0.45 && p.bh < mh * 1.9 && Math.abs(p.y1 - rowY) < mh * 0.45);
  if (row.length >= 3) row.forEach(p => { p.text = true; });
}

// Distance field + filled colour field for a part (used by liquid and neon). Cached.
export function field(p) {
  if (p.sdf) return p;
  const n = p.w * p.h, inside = new Uint8Array(n), outside = new Uint8Array(n), wt = new Float32Array(n), col = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) {
    inside[i] = p.A[i] >= 0.5; outside[i] = p.A[i] < 0.5;
    if (p.A[i] >= 0.5) { wt[i] = 1; col[i * 3] = p.F[i * 3]; col[i * 3 + 1] = p.F[i * 3 + 1]; col[i * 3 + 2] = p.F[i * 3 + 2]; }
  }
  const dOut = edt(inside, p.w, p.h), dIn = edt(outside, p.w, p.h);
  const sdf = new Float32Array(n);
  let deep = 0, dx = 0, dy = 0;
  for (let i = 0; i < n; i++) {
    sdf[i] = inside[i] ? -(dIn[i] - 0.5) : dOut[i] - 0.5;
    if (dIn[i] > deep) { deep = dIn[i]; dx = i % p.w; dy = (i / p.w) | 0; }
  }
  const s2 = new Float32Array(n);
  for (let y = 0; y < p.h; y++) for (let x = 0; x < p.w; x++) {
    let s = 0, c = 0;
    for (let j = -1; j <= 1; j++) for (let k = -1; k <= 1; k++) {
      const xx = x + k, yy = y + j;
      if (xx >= 0 && yy >= 0 && xx < p.w && yy < p.h) { s += sdf[yy * p.w + xx]; c++; }
    }
    s2[y * p.w + x] = s / c;
  }
  p.sdf = s2;
  p.C = pullPush(col, wt, p.w, p.h);
  p.deep = { x: dx + p.rx, y: dy + p.ry, d: deep };
  p.cvs = canvas(p.w, p.h);
  p.ctx = p.cvs.getContext('2d', { willReadFrequently: true });
  p.img = p.ctx.createImageData(p.w, p.h);
  p.sinX = new Float32Array(p.w); p.sinY = new Float32Array(p.h);
  return p;
}

// Paint a part as a circle (centre cx,cy radius r, logo px) morphed toward its own shape by m (0..1);
// `exact` (0..1) blends to the real alpha so the last frames are the logo's own pixels;
// `tint` (rgb) mixed in by `tk` paints it one solid colour (a plain drop before it takes the logo's colours).
export function morphPart(p, cx, cy, r, m, wob, t, exact, tint = null, tk = 0) {
  field(p);
  const { w, h, rx, ry, sdf, A, C, img, sinX, sinY } = p, d = img.data, lx = cx - rx, ly = cy - ry;
  for (let x = 0; x < w; x++) sinX[x] = Math.sin(0.031 * (x + rx) / L.res + 6.2 * t);
  for (let y = 0; y < h; y++) sinY[y] = Math.sin(0.027 * (y + ry) / L.res - 4.9 * t);
  const aa = 1.1 * L.res;
  for (let y = 0; y < h; y++) {
    const dy = y - ly, dy2 = dy * dy, sy = sinY[y], row = y * w;
    for (let x = 0; x < w; x++) {
      const i = row + x, dx = x - lx;
      let cov;
      if (exact >= 1) cov = A[i];
      else {
        const sc = Math.sqrt(dx * dx + dy2) - r;
        let s = sc + (sdf[i] - sc) * m;
        if (wob) s += wob * sinX[x] * sy;
        cov = clamp(0.5 - s / aa);
        if (exact > 0) cov += (A[i] - cov) * exact;
      }
      const o = i * 4;
      if (cov <= 0) { d[o + 3] = 0; continue; }
      if (tk > 0) { d[o] = C[i * 3] + (tint[0] - C[i * 3]) * tk; d[o + 1] = C[i * 3 + 1] + (tint[1] - C[i * 3 + 1]) * tk; d[o + 2] = C[i * 3 + 2] + (tint[2] - C[i * 3 + 2]) * tk; }
      else { d[o] = C[i * 3]; d[o + 1] = C[i * 3 + 1]; d[o + 2] = C[i * 3 + 2]; }
      d[o + 3] = cov * 255;
    }
  }
  p.ctx.putImageData(img, 0, 0);
  return p.cvs;
}

// Load + analyse the logo named in the config; lay it out in the frame.
export async function analyse() {
  const img = await load('/input/' + encodeURIComponent(CFG.logoFile));
  const nw = img.naturalWidth || img.width, nh = img.naturalHeight || img.height;
  let s = Math.min(1, 2000 / Math.max(nw, nh));        // high enough that the logo is never upscaled on screen
  if (Math.max(nw, nh) * s < 800) s = 800 / Math.max(nw, nh);
  const w0 = Math.round(nw * s), h0 = Math.round(nh * s);
  const c0 = canvas(w0, h0), g0 = c0.getContext('2d', { willReadFrequently: true });
  g0.imageSmoothingQuality = 'high';
  g0.drawImage(img, 0, 0, w0, h0);
  const ex = extractAlpha(g0.getImageData(0, 0, w0, h0).data, w0, h0);
  let bx0 = w0, by0 = h0, bx1 = 0, by1 = 0;
  for (let i = 0; i < w0 * h0; i++) if (ex.A[i] > 0.03) { const x = i % w0, y = (i / w0) | 0; bx0 = Math.min(bx0, x); bx1 = Math.max(bx1, x); by0 = Math.min(by0, y); by1 = Math.max(by1, y); }
  if (bx1 < bx0) throw new Error('no logo found in the image (it looks empty)');
  const pad = 4;
  bx0 = Math.max(0, bx0 - pad); by0 = Math.max(0, by0 - pad); bx1 = Math.min(w0 - 1, bx1 + pad); by1 = Math.min(h0 - 1, by1 + pad);
  let logoCv = toCanvas(ex.A, ex.F, w0, h0, bx0, by0, bx1 - bx0 + 1, by1 - by0 + 1);
  let pal = palette(ex.A, ex.F, w0 * h0);
  // background: neon is always dark; 'auto' picks dark for very light logos, light otherwise
  if (CFG.style === 'neon') CFG.theme = 'dark';
  else if (!CFG.theme || CFG.theme === 'auto') {
    let ls = 0, ws = 0;
    for (let i = 0; i < w0 * h0; i += 4) if (ex.A[i] > 0.5) { ls += lum([ex.F[i * 3], ex.F[i * 3 + 1], ex.F[i * 3 + 2]]); ws++; }
    CFG.theme = ws && ls / ws > 0.78 ? 'dark' : 'light';
  }
  const dark = CFG.theme === 'dark';
  if (CFG.text) logoCv = await composeText(logoCv, CFG, pal, dark);

  const w = logoCv.width, h = logoCv.height;
  const px = logoCv.getContext('2d', { willReadFrequently: true }).getImageData(0, 0, w, h).data;
  const A = new Float32Array(w * h), F = new Float32Array(w * h * 3);
  for (let i = 0; i < w * h; i++) { A[i] = px[i * 4 + 3] / 255; F[i * 3] = px[i * 4]; F[i * 3 + 1] = px[i * 4 + 1]; F[i * 3 + 2] = px[i * 4 + 2]; }
  if (CFG.text) pal = palette(A, F, w * h);
  const { lab, ids } = findParts(A, w, h);
  const res = Math.max(w, h) / 900;                      // logo px per "design unit" (keeps effects scale-free)
  const parts = ids.map(id => buildPart(id, lab, A, F, w, h, Math.round(40 * res)));
  markText(parts);
  parts.sort((a, b) => b.area - a.area);
  parts.forEach((p, i) => { p.rank = i; });
  const reading = parts.slice().sort((a, b) => (a.text === b.text ? 0 : a.text ? 1 : -1) || a.x0 - b.x0 || a.y0 - b.y0);

  const landscape = W >= H;
  const S = Math.min((landscape ? 0.78 : 0.84) * W / w, (landscape ? 0.56 : 0.5) * H / h);
  const OX = CX - w * S / 2, OY = CY - h * S / 2;
  const avgLum = parts.reduce((a, p) => a + p.lum * p.area, 0) / parts.reduce((a, p) => a + p.area, 0);
  L = {
    canvas: logoCv, w, h, A, F, parts, reading, palette: pal, res, S, OX, OY, avgLum, keyed: ex.keyed,
    toFrame: (x, y) => [OX + x * S, OY + y * S],
    box: { x0: OX, y0: OY, x1: OX + w * S, y1: OY + h * S, w: w * S, h: h * S },
    main: parts[0],
  };
  return L;
}

// ---------- frame helpers ----------
export function pushIn(t, hold) { return 1 + 0.018 * easeInOut(clamp((t - (hold - 0.3)) / (DUR - hold + 0.3))); }
export function applyPush(g, push) { g.translate(CX, CY); g.scale(push, push); g.translate(-CX, -CY); }
// Logo-space transform: (0,0) of the analysed logo canvas lands at its frame position.
export function logoSpace(g) { g.translate(L.OX, L.OY); g.scale(L.S, L.S); }

export function paintBg(ctx, t, theme) {
  const [c1, c2] = [L.palette[0] || [60, 140, 200], L.palette[1] || L.palette[0] || [60, 140, 200]];
  if (theme === 'dark') {
    const base = mix(L.palette.slice().sort((a, b) => lum(a) - lum(b))[0], [4, 8, 12], 0.82);
    ctx.fillStyle = rgb(base); ctx.fillRect(0, 0, W, H);
    const g = ctx.createRadialGradient(CX, CY, 0, CX, CY, Math.max(W, H) * 0.6);
    g.addColorStop(0, rgb(mix(base, c1, 0.12))); g.addColorStop(1, rgb(base));
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    return;
  }
  if (theme && theme.startsWith('#')) { ctx.fillStyle = theme; ctx.fillRect(0, 0, W, H); }
  else { ctx.fillStyle = '#f7f8f8'; ctx.fillRect(0, 0, W, H); }
  const gl = smooth((t - 0.3) / 2.2);
  if (gl > 0) {
    const g = ctx.createRadialGradient(CX, CY + 10, 0, CX, CY + 10, Math.max(W, H) * 0.5);
    g.addColorStop(0, rgba(c1, 0.11 * gl)); g.addColorStop(0.45, rgba(c2, 0.045 * gl)); g.addColorStop(1, rgba(c2, 0));
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  }
  const v = ctx.createRadialGradient(CX, CY, Math.min(W, H) * 0.4, CX, CY, Math.max(W, H) * 0.65);
  v.addColorStop(0, 'rgba(10,30,40,0)'); v.addColorStop(1, 'rgba(10,30,40,0.07)');
  ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
}

export function gloss(g, t, range, peak = 0.38) {
  const gs = prog(t, range);
  if (gs <= 0 || gs >= 1) return;
  const e = easeInOut(gs), ang = -0.95;
  const nx = Math.cos(ang + Math.PI / 2), ny = Math.sin(ang + Math.PI / 2);
  const span = (L.box.w * Math.abs(nx) + L.box.h * Math.abs(ny)) / 2 + 260;
  const pos = lerp(-span, span, e), bx = CX + nx * pos, by = CY + ny * pos, k = Math.sin(Math.PI * gs);
  const gr = g.createLinearGradient(bx - nx * 150, by - ny * 150, bx + nx * 150, by + ny * 150);
  gr.addColorStop(0, 'rgba(255,255,255,0)');
  gr.addColorStop(0.42, `rgba(255,255,255,${peak * 0.37 * k})`);
  gr.addColorStop(0.5, `rgba(255,255,255,${peak * k})`);
  gr.addColorStop(0.58, `rgba(255,255,255,${peak * 0.37 * k})`);
  gr.addColorStop(1, 'rgba(255,255,255,0)');
  g.save(); g.setTransform(1, 0, 0, 1, 0, 0); g.globalCompositeOperation = 'source-atop'; g.fillStyle = gr; g.fillRect(0, 0, W, H); g.restore();
}

let shadowScratch = null;
export function shadowPass(ctx, layer, a) {
  if (a <= 0) return;
  shadowScratch = shadowScratch || canvas(W, H);
  const sg = shadowScratch.getContext('2d');
  sg.setTransform(1, 0, 0, 1, 0, 0);
  sg.globalCompositeOperation = 'source-over';
  sg.clearRect(0, 0, W, H);
  sg.drawImage(layer, 0, 0);
  sg.globalCompositeOperation = 'source-in';
  const darkest = L.palette.slice().sort((p, q) => lum(p) - lum(q))[0];
  sg.fillStyle = rgb(mix(darkest, [0, 0, 0], 0.45)); sg.fillRect(0, 0, W, H);
  sg.globalCompositeOperation = 'source-over';
  const k = Math.min(W, H) / 1080;
  ctx.save(); ctx.globalAlpha = 0.17 * a; ctx.filter = `blur(${32 * k}px)`; ctx.drawImage(shadowScratch, 0, 24 * k); ctx.restore();
  ctx.save(); ctx.globalAlpha = 0.1 * a; ctx.filter = `blur(${6 * k}px)`; ctx.drawImage(shadowScratch, 0, 5 * k); ctx.restore();
}

export function ripple(c, x, y, t, t0, { r0, r1, dur = 1.2, color = [40, 120, 160], a = 0.3, lw = 3 }) {
  const u = clamp((t - t0) / dur);
  if (u <= 0 || u >= 1) return;
  c.save();
  c.strokeStyle = rgba(color, a * Math.pow(1 - u, 1.5));
  c.lineWidth = lerp(lw, 0.8, u);
  c.beginPath(); c.arc(x, y, lerp(r0, r1, easeOut(u)), 0, Math.PI * 2); c.stroke();
  c.restore();
}

// ---------- boot ----------
// scene.html calls this: loads config + logo, runs the style's setup(), exposes render(t, transparent).
export async function boot() {
  Object.assign(CFG, await (await fetch('/config.json')).json());
  W = CFG.width || 1920; H = CFG.height || 1080; CX = W / 2; CY = H / 2;
  const cv = document.getElementById('c');
  cv.width = W; cv.height = H;
  await analyse();
  const style = await import(`./styles/${CFG.style}.mjs`);
  const scene = await style.setup(cv.getContext('2d'));
  window.info = {
    style: CFG.style, theme: CFG.theme, size: [W, H], logo: [L.w, L.h], scale: +L.S.toFixed(4),
    parts: L.parts.length, textParts: L.parts.filter(p => p.text).length, keyedBackground: L.keyed,
    palette: L.palette.map(c => c.map(Math.round)), events: scene.events || [], times: scene.times || {},
  };
  window.render = scene.render;
  window.ready = true;
  if (location.hash === '#play') {
    const start = performance.now();
    const loop = () => { scene.render(((performance.now() - start) / 1000) % (DUR + 0.8), false); requestAnimationFrame(loop); };
    loop();
  } else scene.render(DUR, false);
}
