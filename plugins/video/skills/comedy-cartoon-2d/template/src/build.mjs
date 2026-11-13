// Final assembly + QC.
//   node src/build.mjs mux   -> film/<title>.mp4 (video + audio + soft subtitle tracks) and film/<title>.<lang>.srt
//   node src/build.mjs qc    -> film/qc/: contact sheet (every 4 s), spectrogram, loudness per 5 s window
import fs from 'node:fs';
import { execFileSync, spawnSync } from 'node:child_process';
import { DURATION } from './shots.mjs';

const film = JSON.parse(fs.readFileSync('film.json', 'utf8'));
const title = film.title || 'Cartoon';
const out = `film/${title}.mp4`;
const ISO3 = { km: 'khm', en: 'eng', th: 'tha', vi: 'vie', zh: 'zho', fr: 'fra', ja: 'jpn', ko: 'kor', es: 'spa' };
const NAME = { km: 'ខ្មែរ', en: 'English' };
fs.mkdirSync('film/qc', { recursive: true });
const ff = args => execFileSync('ffmpeg', ['-v', 'error', '-y', ...args]);
const mode = process.argv[2] || 'mux';

if (mode === 'mux') {
  const subs = fs.readdirSync('build').filter(f => /^subtitles_.*\.srt$/.test(f));
  // cover art (src/cover.mjs -> film/cover_1280.jpg) is embedded as the file's thumbnail
  const cover = fs.existsSync('film/cover_1280.jpg') ? 'film/cover_1280.jpg' : null;
  const args = ['-i', 'build/video.mp4', '-i', 'build/audio.wav', ...subs.flatMap(f => ['-i', `build/${f}`]), ...(cover ? ['-i', cover] : []), '-map', '0:v', '-map', '1:a'];
  subs.forEach((f, i) => {
    const lang = f.slice(10, -4);
    args.push('-map', String(i + 2), `-metadata:s:s:${i}`, `language=${ISO3[lang] || lang}`, `-metadata:s:s:${i}`, `title=${NAME[lang] || lang}`);
    fs.copyFileSync(`build/${f}`, `film/${title}.${lang}.srt`);
  });
  if (cover) args.push('-map', String(subs.length + 2), '-c:v:1', 'mjpeg', '-disposition:v:1', 'attached_pic');
  // -t, not -shortest: a subtitle track ends at the last line and would cut the film short
  ff([...args, '-c:v:0', 'copy', '-c:a', 'aac', '-b:a', '192k', '-c:s', 'mov_text', '-t', String(DURATION), '-movflags', '+faststart', out]);
  console.log(`-> ${out} (${DURATION}s, subtitles: ${subs.map(f => f.slice(10, -4)).join(', ') || 'none'})`);
} else if (mode === 'qc') {
  const v = fs.existsSync(out) ? out : 'build/video.mp4';
  const every = Math.max(48, Math.ceil(DURATION * 24 / 24)); // 24 tiles across the whole film, whatever its length
  ff(['-i', v, '-vf', `select='not(mod(n\\,${every}))',scale=384:216,tile=6x4`, '-frames:v', '1', 'film/qc/contact_sheet.png']);
  const levels = [];
  if (fs.existsSync('build/audio.wav')) {
    ff(['-i', 'build/audio.wav', '-lavfi', 'showspectrumpic=s=1800x300:legend=1:scale=log:fscale=log:stop=8000', 'film/qc/spectrogram.png']);
    for (let s = 0; s < DURATION; s += 5) {
      const r = spawnSync('ffmpeg', ['-v', 'info', '-ss', String(s), '-t', '5', '-i', 'build/audio.wav', '-af', 'volumedetect', '-f', 'null', '-'], { encoding: 'utf8' }).stderr || '';
      const m = /mean_volume: (-?[\d.]+)/.exec(r), x = /max_volume: (-?[\d.]+)/.exec(r);
      levels.push(`${String(s).padStart(3)}s  mean ${m ? m[1] : '?'} dB  max ${x ? x[1] : '?'} dB`);
    }
    fs.writeFileSync('film/qc/levels.txt', levels.join('\n') + '\n');
  }
  console.log(levels.join('\n'));
  console.log('-> film/qc/contact_sheet.png, film/qc/spectrogram.png, film/qc/levels.txt');
}
