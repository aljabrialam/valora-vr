// Renders title cards (JPEG) and caption overlays (transparent PNG) frame by frame on the page clock.
// Usage: node scripts/video/titles.mjs <out-dir> <seconds> <query>   e.g. "scene=logo" or "scene=ov&chip=Play&cap=..."
import fs from 'node:fs';
import path from 'node:path';
import {chromium} from '../../node_modules/playwright/index.mjs';
import {FPS} from './clock.mjs';

const [out, seconds, query] = process.argv.slice(2);
fs.rmSync(out, {recursive: true, force: true});
fs.mkdirSync(out, {recursive: true});
const overlay = /scene=(ov|place)/.test(query);
const browser = await chromium.launch({executablePath: '/opt/pw-browsers/chromium-1243/real/chrome-linux64/chrome', args: ['--no-sandbox']});
const page = await browser.newPage({viewport: {width: 1280, height: 720}, deviceScaleFactor: 1});
await page.addInitScript(`(() => {
  let t = 0; let q = [];
  performance.now = () => t;
  window.requestAnimationFrame = (cb) => { q.push(cb); return q.length; };
  window.__frame = (dt) => { t += dt; const run = q; q = []; run.forEach((cb) => cb(t)); };
})();`);
await page.goto('file://' + path.resolve('scripts/video/titles.html') + '?' + query);
await page.waitForTimeout(400);
const cdp = await page.context().newCDPSession(page);
if (overlay) await cdp.send('Emulation.setDefaultBackgroundColorOverride', {color: {r: 0, g: 0, b: 0, a: 0}});
const n = Math.round(+seconds * FPS);
for (let i = 0; i < n; i++) {
  await page.evaluate((dt) => window.__frame(dt), 1000 / FPS);
  const shot = await cdp.send('Page.captureScreenshot', overlay ? {format: 'png'} : {format: 'jpeg', quality: 94});
  fs.writeFileSync(`${out}/f${String(i).padStart(5, '0')}.${overlay ? 'png' : 'jpg'}`, Buffer.from(shot.data, 'base64'));
}
await browser.close();
console.log(out, n, 'frames');
