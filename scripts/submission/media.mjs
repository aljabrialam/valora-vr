// Devpost gallery images (3:2, 1500x1000, JPG under 5 MB) and the YouTube thumbnail (1280x720),
// composed from the game's own renders with the brand type. Output: docs/submission/
//   node scripts/submission/media.mjs
import fs from 'node:fs';
import path from 'node:path';
import {chromium} from 'playwright';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../..');
const OUT = path.join(ROOT, 'docs/submission');
fs.mkdirSync(OUT, {recursive: true});
const f = (p) => `data:image/jpeg;base64,${fs.readFileSync(path.join(ROOT, p)).toString('base64')}`;
const EMU = 'Headset view · Meta IWER emulator';

// [file, image, label pill (top left), caption (bottom), focus (CSS object-position)]
const GALLERY = [
  ['01-cover', 'docs/screens/vn-v3.jpg', null, null, 'center', 'cover'],
  ['02-play-hands', 'video/frames/v_ph/f00170.jpg', EMU, 'Pinch a piece on the raft, point it at the courtyard, let go.', 'center'],
  ['03-score', 'video/frames/v_score/f00400.jpg', EMU, 'Every rule DONE: three stars for two pieces, at par.', 'center'],
  ['04-controllers', 'video/frames/v_vn/f00110.jpg', EMU + ' · Touch controllers', 'Touch controllers work too: point, pull the trigger.', 'center'],
  ['05-sun', 'video/frames/v_sun/f00180.jpg', EMU, 'Drag the sun. Each capital has its own sun path.', 'center'],
  ['06-globe', 'video/frames/d_globe/f00060.jpg', 'Browser view · before entering VR', 'Choose a place on the globe, then Enter VR.', 'center'],
  ['07-manila', 'docs/screens/ph-v3.jpg', 'Manila · Philippines', 'Typhoon wind comes in low over the bamboo fence.', 'center'],
  ['08-bangkok', 'docs/screens/th-v3.jpg', 'Bangkok · Thailand', 'Long-tail boats pass on the canal.', 'center'],
  ['09-hanoi', 'docs/screens/vn-v3.jpg', 'Hanoi · Vietnam', 'Motorbikes stream down the lane.', 'center'],
  ['10-kuala-lumpur', 'docs/screens/my-v3.jpg', 'Kuala Lumpur · Malaysia', 'Condo towers look straight down.', 'center'],
  ['11-jakarta', 'docs/screens/id-v3.jpg', 'Jakarta · Indonesia', 'Monsoon rain slants in from the west.', 'center'],
  ['12-singapore', 'docs/screens/sg-v3.jpg', 'Singapore', 'The high-rise next door watches the pool.', 'center'],
  ['13-watching', 'video/frames/t_watch/f00050.jpg', null, 'Someone is always watching: the neighbour’s line of sight lands on the reading chair.', 'center'],
];

const css = `
  html,body{margin:0;overflow:hidden;font-family:Inter,-apple-system,system-ui,sans-serif;-webkit-font-smoothing:antialiased}
  .bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
  .pill{position:absolute;left:44px;top:40px;background:rgba(255,255,255,.92);color:#1d1d1f;font-weight:600;font-size:26px;padding:12px 22px;border-radius:999px;letter-spacing:-.01em}
  .cap{position:absolute;left:44px;right:44px;bottom:40px;display:flex;justify-content:center}
  .cap span{background:rgba(16,22,28,.78);color:#fff;font-weight:500;font-size:34px;line-height:1.25;padding:16px 28px;border-radius:18px;letter-spacing:-.01em;text-align:center}
  .shade{position:absolute;inset:0;background:linear-gradient(90deg,rgba(8,20,30,.82) 0%,rgba(8,20,30,.55) 42%,rgba(8,20,30,0) 70%)}
  .title{position:absolute;left:80px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center;color:#fff;max-width:760px}
  .title .k{font-size:26px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#e9c08a}
  .title .h{font-family:'Cormorant Garamond',Georgia,serif;font-weight:600;font-size:132px;line-height:.95;margin:18px 0 8px;letter-spacing:-.01em}
  .title .h2{font-size:52px;font-weight:600;letter-spacing:-.02em}
  .title .s{font-size:30px;font-weight:500;color:rgba(255,255,255,.85);margin-top:26px;line-height:1.35}
`;

function page(w, h, img, pill, cap, pos, kind) {
  if (kind === 'cover')
    return `<style>${css}</style><img class="bg" src="${f(img)}" style="object-position:${pos}"><div class="shade"></div>
      <div class="title"><div class="k">Meta VR Start Developer Competition 2026</div><div class="h">VaLora</div><div class="h2">Two Watchers</div>
      <div class="s">Let the sun in. Keep the watchers out.<br>A seated VR puzzle across six South-east Asian capitals.</div></div>`;
  if (kind === 'thumb')
    return `<style>${css}
      .title .h{font-size:150px}.title .h2{font-size:64px}.title .s{font-size:34px}</style>
      <img class="bg" src="${f(img)}" style="object-position:${pos}"><div class="shade"></div>
      <div class="title" style="left:70px"><div class="h">VaLora</div><div class="h2">Two Watchers</div><div class="s">A VR puzzle for Meta Quest</div></div>`;
  return `<style>${css}</style><img class="bg" src="${f(img)}" style="object-position:${pos}">
    ${pill ? `<div class="pill">${pill}</div>` : ''}${cap ? `<div class="cap"><span>${cap}</span></div>` : ''}`;
}

const browser = await chromium.launch({executablePath: process.env.CHROME ?? '/opt/pw-browsers/chromium-1243/real/chrome-linux64/chrome'});
async function shot(name, w, h, html) {
  const p = await browser.newPage({viewport: {width: w, height: h}});
  await p.setContent(html, {waitUntil: 'load'});
  await p.evaluate(() => document.fonts.ready);
  await p.screenshot({path: path.join(OUT, name), type: 'jpeg', quality: 90});
  await p.close();
  console.log(name, (fs.statSync(path.join(OUT, name)).size / 1e6).toFixed(2), 'MB');
}
for (const [name, img, pill, cap, pos, kind] of GALLERY) await shot(`gallery-${name}.jpg`, 1500, 1000, page(1500, 1000, img, pill, cap, pos, kind));
await shot('youtube-thumbnail-1280x720.jpg', 1280, 720, page(1280, 720, 'docs/screens/my-v3.jpg', null, null, '60% center', 'thumb'));
await browser.close();
