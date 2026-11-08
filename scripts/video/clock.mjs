// Frame-exact capture: the page's clock and animation frames are driven from here, so footage is
// smooth at 30 fps however slowly software rendering draws each frame.
import {chromium} from '../../node_modules/playwright/index.mjs';

export const FPS = 24;
const CLOCK = `(() => {
  // capture only: no multisampling (very slow in software GL); frames are supersampled later instead
  const getContext = HTMLCanvasElement.prototype.getContext;
  HTMLCanvasElement.prototype.getContext = function (type, attrs) {
    if (type === 'webgl2' || type === 'webgl') attrs = {...(attrs || {}), antialias: false};
    return getContext.call(this, type, attrs);
  };
  let t = 0; const base = Date.now(); let q = []; let id = 0;
  const realRAF = window.requestAnimationFrame.bind(window);
  performance.now = () => t;
  Date.now = () => base + t;
  window.requestAnimationFrame = (cb) => { q.push([++id, cb]); return id; };
  window.cancelAnimationFrame = (n) => { q = q.filter((e) => e[0] !== n); };
  window.__frame = (dt) => { t += dt; const run = q; q = []; for (const [, cb] of run) { try { cb(t); } catch (e) { console.error(e); } } return t; };
  window.__free = () => { /* let the page run on real time again (used while loading) */ };
  // Run on real frames until the capture takes over, so loading code that waits on frames proceeds.
  let manual = false;
  window.__manual = () => { manual = true; };
  (function pump() { if (manual) return; window.__frame(1000 / 60); realRAF(pump); })();
})();`;

export async function open(url, {w = 1280, h = 720} = {}) {
  const browser = await chromium.launch({executablePath: '/opt/pw-browsers/chromium-1243/real/chrome-linux64/chrome', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-certificate-errors', '--no-sandbox']});
  const page = await browser.newPage({viewport: {width: w, height: h}, deviceScaleFactor: 1, ignoreHTTPSErrors: true});
  page.on('pageerror', (e) => console.log('pageerror', e.message));
  await page.addInitScript(CLOCK);
  await page.goto(url, {waitUntil: 'load', timeout: 90000});
  return {browser, page};
}

/** Take over the clock and record `seconds` of frames into dir/f%05d.jpg, calling each(t) before every frame. */
export async function record(page, dir, seconds, each = async () => {}, start = 0) {
  await page.evaluate(() => window.__manual());
  const n = Math.round(seconds * FPS);
  for (let i = 0; i < n; i++) {
    const t = i / FPS;
    await each(t, i);
    await page.evaluate((dt) => window.__frame(dt), 1000 / FPS);
    await page.screenshot({path: `${dir}/f${String(start + i).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 92});
  }
  return start + n;
}
