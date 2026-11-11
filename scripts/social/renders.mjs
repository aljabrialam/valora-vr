// Renders the stills for the social graphics from the running game.
//   node scripts/social/renders.mjs [name ...]      (needs npm run dev; BASE=https://host:port/ to override)
// VR.chrome(false) hides the page overlays and the tutorial arrow; each level is shown solved.
import {open} from '../video/clock.mjs';
import fs from 'node:fs';

const OUT = new URL('../../docs/social/img', import.meta.url).pathname;
const BASE = process.env.BASE ?? 'https://localhost:8081/';
fs.mkdirSync(OUT, {recursive: true});
const HERO = {pos: [-1.05, 1.22, 0.5], look: [0, 0.8, -0.56], fov: 34};
const SOLVE = {ph: {kind: 'screen', socket: 2, rot: 0}, th: {kind: 'hedge', socket: 22, rot: 0}, id: {kind: 'pergola', socket: 15, rot: 0}, sg: {kind: 'tree', socket: 1, rot: 0}, vn: {kind: 'hedge', socket: 22, rot: 0}, my: {kind: 'tree', socket: 6, rot: 0}};

const SHOTS = {
  hero_ph: {c: 'ph', w: 1920, h: 1080, cam: HERO, solve: true},
  hero_th: {c: 'th', w: 1920, h: 1080, cam: HERO, solve: true},
  hero_id: {c: 'id', w: 1920, h: 1080, cam: HERO, solve: true},
  hero_sg: {c: 'sg', w: 1920, h: 1080, cam: HERO, solve: true},
  hero_vn: {c: 'vn', w: 1920, h: 1080, cam: HERO, solve: true},
  hero_my: {c: 'my', w: 1920, h: 1080, cam: HERO, solve: true},
  story_th: {c: 'th', w: 1080, h: 1920, cam: {pos: [-0.62, 1.5, 0.95], look: [0.0, 0.8, -0.42], fov: 52}, solve: true},
  how_raft: {c: 'th', w: 1280, h: 720, cam: {pos: [-0.08, 1.02, 0.46], look: [-0.12, 0.75, -0.02], fov: 46}},
  how_sun: {c: 'ph', w: 1280, h: 720, cam: {pos: [0.5, 1.06, 0.28], look: [-0.02, 0.9, -0.42], fov: 42}, hour: 15.5, solve: true},
  how_day: {c: 'sg', w: 1280, h: 720, cam: {pos: [-0.7, 1.1, 0.3], look: [0.0, 0.8, -0.55], fov: 38}, solve: true, live: true},
};

const want = process.argv.slice(2);
for (const [name, s] of Object.entries(SHOTS)) {
  if (want.length && !want.includes(name)) continue;
  const {browser, page} = await open(`${BASE}?country=${s.c}&level=1`, {w: s.w, h: s.h});
  await page.waitForTimeout(+(process.env.WAIT || 26000));
  await page.evaluate(([solve, hour]) => {
    VR.chrome(false);
    for (const el of document.body.children) if (el.shadowRoot) el.style.display = 'none';
    window.__manual();
    if (solve) VR.place([solve], 0);
    if (hour) VR.setHour(hour);
  }, [s.solve ? SOLVE[s.c] : null, s.hour ?? 0]);
  if (s.live) {
    await page.evaluate(() => VR.live());
    for (let i = 0; i < 70; i++) await page.evaluate(() => window.__frame(1000 / 24));
  }
  await page.evaluate((cam) => { VR.cinema(cam); window.__frame(33); window.__frame(33); window.__frame(33); }, s.cam);
  const cdp = await page.context().newCDPSession(page);
  const r = await cdp.send('Page.captureScreenshot', {format: 'jpeg', quality: 92});
  fs.writeFileSync(`${OUT}/${name}.jpg`, Buffer.from(r.data, 'base64'));
  console.log('wrote', name);
  await browser.close();
}
