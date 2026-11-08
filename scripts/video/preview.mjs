// Quick stills of a country for art review.
//   node scripts/video/preview.mjs <country> [out.png] [cam json]   (needs npm run dev)
import {open} from './clock.mjs';
import fs from 'node:fs';
const [c = 'vn', out = `/tmp/preview-${c}.png`, camArg] = process.argv.slice(2);
const BASE = process.env.BASE ?? 'https://localhost:8081/';
const cam = camArg ? JSON.parse(camArg) : {pos: [-1.05, 1.22, 0.5], look: [0, 0.8, -0.56], fov: 34};
const {browser, page} = await open(`${BASE}?country=${c}&level=${process.env.LEVEL ?? 1}`, {w: +(process.env.W ?? 1600), h: +(process.env.H ?? 900)});
await page.waitForTimeout(+(process.env.WAIT || 26000));
await page.evaluate((hour) => {
  VR.chrome(false);
  for (const el of document.body.children) if (el.shadowRoot) el.style.display = 'none';
  window.__manual();
  if (hour) VR.setHour(hour);
}, +(process.env.HOUR ?? 0));
await page.evaluate((cam) => { VR.cinema(cam); for (let i = 0; i < 40; i++) window.__frame(33); }, cam);
const cdp = await page.context().newCDPSession(page);
const r = await cdp.send('Page.captureScreenshot', {format: 'png'});
fs.writeFileSync(out, Buffer.from(r.data, 'base64'));
await browser.close();
console.log(out);
