// Render the portfolio-reel frame by frame in headless Chrome (DevTools protocol), PNG frames to disk.
// node render.mjs --project <dir> --out <frames dir> [--fps 60] [--from 0 --to N] | --times 1.2,3.4 (stills) | --cues <file.json>
// Serves the skill at /skill/ and the project (promo.json, assets/, build/) at /proj/.
import http from 'node:http';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const SKILL = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const args = process.argv.slice(2);
const opt = (n, d) => (args.includes(n) ? args[args.indexOf(n) + 1] : d);
const PROJ = path.resolve(opt('--project', '.'));
const outDir = path.resolve(opt('--out', path.join(PROJ, 'build/frames')));
const fps = Number(opt('--fps', 60));
const timesArg = opt('--times', null);
const cuesOut = opt('--cues', null);   // write {dur, cues, sections} from the scene's timeline and exit (no frames)
if (!cuesOut) fs.mkdirSync(outDir, { recursive: true });

function findChrome() {
  const c = [process.env.CHROME_PATH, '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium', '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser'];
  const hit = c.find(p => p && fs.existsSync(p));
  if (!hit) throw new Error('Chrome/Chromium not found: set CHROME_PATH');
  return hit;
}
const TYPES = { '.html': 'text/html', '.mjs': 'text/javascript', '.js': 'text/javascript', '.json': 'application/json',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.ttf': 'font/ttf', '.otf': 'font/otf' };
const server = http.createServer((req, res) => {
  const url = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  let root, rel;
  if (url.startsWith('/skill/')) { root = SKILL; rel = url.slice(7); } else if (url.startsWith('/proj/')) { root = PROJ; rel = url.slice(6); } else { res.writeHead(404); return res.end(); }
  const p = path.join(root, rel);
  if (!p.startsWith(root) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(p).toLowerCase()] || 'application/octet-stream', 'Cache-Control': 'no-store' });
  fs.createReadStream(p).pipe(res);
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const port = server.address().port;
const debugPort = 9300 + Math.floor(Math.random() * 600);
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'portfolioreel-chrome-'));
const chrome = spawn(findChrome(), [
  '--headless=new', `--remote-debugging-port=${debugPort}`, '--remote-allow-origins=*', `--user-data-dir=${profile}`,
  '--no-first-run', '--no-default-browser-check', '--hide-scrollbars', '--force-device-scale-factor=1',
  '--window-size=1920,1080', 'about:blank'], { stdio: 'ignore' });

let ws;
try {
  let target;
  for (let i = 0; i < 100 && !target; i++) {
    try { target = (await (await fetch(`http://127.0.0.1:${debugPort}/json/list`)).json()).find(t => t.type === 'page'); } catch {}
    if (!target) await new Promise(r => setTimeout(r, 150));
  }
  if (!target) throw new Error('Chrome did not start');
  ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  let id = 1; const pending = new Map();
  const pageErrors = [];   // uncaught page errors and failed module loads, reported if the scene never starts
  ws.onmessage = ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
    if (m.method === 'Runtime.exceptionThrown') pageErrors.push(m.params.exceptionDetails?.exception?.description || m.params.exceptionDetails?.text);
    if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error') pageErrors.push(`${m.params.entry.text} ${m.params.entry.url || ''}`);
  };
  const send = (method, params = {}) => new Promise(res => { const i = id++; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
  await send('Runtime.enable'); await send('Log.enable');
  const ev = async expression => {
    const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
    if (r.result?.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails).slice(0, 800));
    return r.result?.result?.value;
  };
  await send('Page.navigate', { url: `http://127.0.0.1:${port}/skill/scripts/index.html` });
  let ready = false;
  for (let i = 0; i < 400 && !ready; i++) {
    ready = await ev('window.ready === true').catch(() => false);
    const err = await ev('window.bootError || null').catch(() => null);
    if (err) throw new Error('scene failed to start: ' + err);
    if (!ready) await new Promise(r => setTimeout(r, 100));
  }
  if (!ready) throw new Error('scene did not become ready (stuck at: ' + (await ev('window.bootStage || "?"').catch(() => '?')) + ')' +
    (pageErrors.length ? '\n' + pageErrors.slice(0, 5).join('\n') : ''));
  const DUR = await ev('window.DUR');
  if (cuesOut) {
    const tl = await ev('JSON.stringify({ dur: window.DUR, fps: ' + fps + ', cues: window.CUES, sections: window.SECTIONS, beats: window.BEATS })');
    fs.mkdirSync(path.dirname(path.resolve(cuesOut)), { recursive: true });
    fs.writeFileSync(path.resolve(cuesOut), tl);
    console.log(`timeline -> ${cuesOut} (${DUR.toFixed(2)} s)`);
    throw { quiet: true };
  }
  const from = Number(opt('--from', 0)), to = Number(opt('--to', Math.round(DUR * fps)));
  const auto = timesArg === 'auto' ? await ev('window.PREVIEW_TIMES') : null;   // the scene's own preview stills
  const list = timesArg ? (auto || timesArg.split(',').map(Number)).map(x => (x < 0 ? DUR + x : x)) :   // negative = seconds before the end
    Array.from({ length: Math.max(0, to - from) }, (_, i) => (from + i) / fps);
  const t0 = Date.now();
  for (let i = 0; i < list.length; i++) {
    const name = timesArg ? `t_${list[i].toFixed(2).padStart(5, '0')}.png` : `f_${String(from + i).padStart(5, '0')}.png`;
    const file = path.join(outDir, name);
    if (!timesArg && fs.existsSync(file)) continue;
    const url = await ev(`render(${list[i]}).then(() => document.getElementById('c').toDataURL('image/png'))`);
    fs.writeFileSync(file + '.tmp', Buffer.from(url.split(',')[1], 'base64'));
    fs.renameSync(file + '.tmp', file);
    if (!timesArg && i % 300 === 0) console.log(`frame ${from + i} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
  }
  console.log(`done ${list.length} frames in ${((Date.now() - t0) / 1000).toFixed(1)}s (duration ${DUR.toFixed(2)} s)`);
} catch (e) {
  if (!e?.quiet) { console.error(String(e.message || e)); process.exitCode = 1; }
} finally {
  try { ws?.close(); } catch {}
  chrome.kill(); server.close();
  setTimeout(() => { try { fs.rmSync(profile, { recursive: true, force: true }); } catch {} process.exit(); }, 500);
}
