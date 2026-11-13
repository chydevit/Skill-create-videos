// Quick look at every location: `node src/setsheet.mjs` -> build/stills/sets.png
import { createCanvas } from '@napi-rs/canvas';
import fs from 'node:fs';
import { execFileSync } from 'node:child_process';
import { W, H } from './core.mjs';
import * as st from './sets.mjs';
import { person } from './people.mjs';
import './cast.mjs';
fs.mkdirSync('build/stills', { recursive: true });
const shots = {
  skyline: c => { st.sunsetSky(c); st.skyline(c, 0); st.officeTower(c, 0); },
  office: c => { st.office(c, 0, { board: 1 }); },
  devitDesk: c => { st.office(c, 0, {}); person(c, 'devit', { x: 760, y: 1080, s: 1.4, facing: 0.6, pose: 'type', t: 0.2 }); st.desk(c, 960, 960, 1500, { monitorX: 300, t: 1 }); st.flyingCode(c, 1260, 700, 0.5); },
  meeting: c => { st.meetingRoom(c, 0); st.meetingTable(c, 960, 930); },
  phone: c => { c.fillStyle = '#ffe2d4'; c.fillRect(0, 0, W, H); st.phoneScreen(c, 960, 540, 1.1, 0, { orders: 6 }); },
  phoneErr: c => { c.fillStyle = '#ffe2d4'; c.fillRect(0, 0, W, H); st.phoneScreen(c, 960, 540, 1.1, 0, { orders: 9, error: 1 }); },
  servers: c => { c.fillStyle = '#3b3550'; c.fillRect(0, 0, W, H); st.serverRack(c, 700, 960, 1.4, 0.5, { smoke: 1, n: 3 }); st.redWash(c, 0.5, 1); },
  dash: c => { c.fillStyle = '#f8e6d6'; c.fillRect(0, 0, W, H); st.dashboard(c, 260, 140, 1400, 800, 1, { servers: 4, lb: 1, bars: 0.7, status: 1 }); },
  street: c => { st.sunsetSky(c, { horizon: 900 }); st.shophouses(c, 200); st.rider(c, 900, 1000, 1.3, 0.3); },
  rooftop: c => { st.nightSky(c, 0); st.skyline(c, 0, { night: 1 }); st.rooftop(c, 0); },
};
const files = [];
for (const [k, fn] of Object.entries(shots)) { const cv = createCanvas(W, H), c = cv.getContext('2d'); fn(c); const f = `build/stills/set_${k}.png`; fs.writeFileSync(f, cv.toBuffer('image/png')); files.push(f); }
const sel = files.slice(0, 9);
execFileSync('ffmpeg', ['-v', 'error', '-y', ...sel.flatMap(f => ['-i', f]), '-filter_complex', sel.map((_, i) => `[${i}:v]scale=640:360[s${i}]`).join(';') + ';' + sel.map((_, i) => `[s${i}]`).join('') + `xstack=inputs=${sel.length}:layout=` + sel.map((_, i) => `${(i % 3) * 640}_${Math.floor(i / 3) * 360}`).join('|'), 'build/stills/sets.png']);
console.log('build/stills/sets.png +', files[9]);
