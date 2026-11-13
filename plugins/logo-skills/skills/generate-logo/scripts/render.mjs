// Renders scene.html to PNG frames in headless Chrome over the DevTools protocol.
// usage: node render.mjs --config <cfg.json> --logo <image> --out <dir> [--transparent] [--fps 60] [--dur 5]
//                        [--times 0.5,1.2] [--info <info.json>]
// The page is served from this folder; the logo at /input/<name>, the config at /config.json.
import http from 'node:http';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const opt = (name, dflt) => (args.includes(name) ? args[args.indexOf(name) + 1] : dflt);
const outDir = path.resolve(opt('--out', 'frames'));
const cfgPath = path.resolve(opt('--config'));
const logoPath = path.resolve(opt('--logo'));
const transparent = args.includes('--transparent');
const fps = Number(opt('--fps', 60));
const DUR = Number(opt('--dur', 5));
const timesArg = opt('--times', null);
const infoPath = opt('--info', null);
const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
fs.mkdirSync(outDir, { recursive: true });

function findChrome() {
  const c = [process.env.CHROME_PATH,
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser',
    'C:/Program Files/Google/Chrome/Application/chrome.exe'];
  const hit = c.find(p => p && fs.existsSync(p));
  if (!hit) throw new Error('Chrome/Chromium not found: set CHROME_PATH');
  return hit;
}

const TYPES = { '.html': 'text/html', '.mjs': 'text/javascript', '.js': 'text/javascript', '.json': 'application/json',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.gif': 'image/gif' };
const server = http.createServer((req, res) => {
  const url = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  let p;
  if (url === '/config.json') p = cfgPath;
  else if (url.startsWith('/input/')) p = logoPath;
  else p = path.join(HERE, url);
  if (!p.startsWith(HERE) && p !== cfgPath && p !== logoPath) { res.writeHead(403); return res.end(); }
  if (!fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(p).toLowerCase()] || 'application/octet-stream', 'Cache-Control': 'no-store' });
  fs.createReadStream(p).pipe(res);
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const httpPort = server.address().port;

const debugPort = 9300 + Math.floor(Math.random() * 600);
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'genlogo-chrome-'));
const chrome = spawn(findChrome(), [
  '--headless=new', `--remote-debugging-port=${debugPort}`, '--remote-allow-origins=*',
  `--user-data-dir=${profile}`, '--no-first-run', '--no-default-browser-check',
  '--hide-scrollbars', '--force-device-scale-factor=1', `--window-size=${cfg.width || 1920},${cfg.height || 1080}`,
  'about:blank',
], { stdio: 'ignore' });

const cleanup = async () => {
  try { ws?.close(); } catch {}
  const exited = new Promise(r => chrome.once('exit', r));
  chrome.kill();
  await Promise.race([exited, new Promise(r => setTimeout(r, 3000))]);
  server.close();
  try { fs.rmSync(profile, { recursive: true, force: true }); } catch {}
};

let target, ws;
try {
  for (let i = 0; i < 100 && !target; i++) {
    try { target = (await (await fetch(`http://127.0.0.1:${debugPort}/json/list`)).json()).find(t => t.type === 'page'); } catch {}
    if (!target) await new Promise(r => setTimeout(r, 150));
  }
  if (!target) throw new Error('Chrome did not start');
  ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  let nextId = 1;
  const pending = new Map();
  ws.onmessage = ev => { const m = JSON.parse(ev.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } };
  const send = (method, params = {}) => new Promise(res => { const id = nextId++; pending.set(id, res); ws.send(JSON.stringify({ id, method, params })); });
  const evaluate = async expression => {
    const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
    if (r.result?.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails));
    return r.result?.result?.value;
  };

  await send('Page.navigate', { url: `http://127.0.0.1:${httpPort}/scene.html` });
  let ready = false;
  for (let i = 0; i < 600 && !ready; i++) {
    ready = await evaluate('window.ready === true').catch(() => false);
    const err = await evaluate('window.bootError || null').catch(() => null);
    if (err) throw new Error('scene failed: ' + err);
    if (!ready) await new Promise(r => setTimeout(r, 100));
  }
  if (!ready) throw new Error('scene did not become ready');
  const info = JSON.parse(await evaluate('JSON.stringify(window.info)'));
  if (infoPath) fs.writeFileSync(infoPath, JSON.stringify(info, null, 2));
  console.log(`analysed: ${info.parts} shapes (${info.textParts} text), scale ${info.scale}`);

  const times = timesArg ? timesArg.split(',').map(Number) : Array.from({ length: Math.round(DUR * fps) }, (_, i) => i / fps);
  const t0 = Date.now();
  for (let i = 0; i < times.length; i++) {
    const url = await evaluate(`render(${times[i]}, ${transparent}); document.getElementById('c').toDataURL('image/png')`);
    const name = timesArg ? `t_${times[i].toFixed(2)}.png` : `f_${String(i).padStart(4, '0')}.png`;
    fs.writeFileSync(path.join(outDir, name), Buffer.from(url.split(',')[1], 'base64'));
    if (!timesArg && i % 60 === 0) process.stdout.write(`  frame ${i}/${times.length}\r`);
  }
  console.log(`  ${times.length} frames in ${((Date.now() - t0) / 1000).toFixed(1)}s${transparent ? ' (transparent)' : ''}      `);
} catch (e) {
  console.error(String(e.message || e));
  process.exitCode = 1;
} finally {
  await cleanup();
}
