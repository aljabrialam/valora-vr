// Renders each artboard to a PNG at its real size, with local images and fonts.
//   python3 scripts/social/make.py && node scripts/social/export.mjs
// Needs Cormorant Garamond woff2 files: npm pack @fontsource/cormorant-garamond, unpack, and set
// CORMORANT_DIR to its files/ folder (default /tmp/fonts/package/files). Inter must be installed.
import {chromium} from '../../node_modules/playwright/index.mjs';
import fs from 'node:fs';
const R = new URL('.', import.meta.url).pathname.replace(/\/$/, '');
const DOCS = new URL('../../docs', import.meta.url).pathname;
const FONTS = process.env.CORMORANT_DIR ?? '/tmp/fonts/package/files';
const blobs = JSON.parse(fs.readFileSync(`${R}/blobs.json`, 'utf8'));
const canvas = JSON.parse(fs.readFileSync(`${R}/project/canvas.json`, 'utf8'));
const face = [500, 600, 700].map((w) => `@font-face{font-family:'Cormorant Garamond';font-weight:${w};src:url(file://${FONTS}/cormorant-garamond-latin-${w}-normal.woff2) format('woff2')}`).join('');
const browser = await chromium.launch({executablePath: '/opt/pw-browsers/chromium-1243/real/chrome-linux64/chrome', args: ['--no-sandbox', '--allow-file-access-from-files']});
for (const [file, b] of Object.entries(canvas.boards)) {
  let html = fs.readFileSync(`${R}/project/${file}`, 'utf8');
  for (const [name, url] of Object.entries(blobs)) html = html.split(url).join(name === 'logo' ? `file://${DOCS}/brand/valora-logo-horizontal.svg` : `file://${DOCS}/social/img/${name}.jpg`);
  html = html.replace(/<link[^>]*fonts\.g[^>]*>/g, '').replace('<script src="./support.js"></script>', `<style>${face}</style>`);
  const tmp = `${DOCS}/social/_${file}.html`;
  fs.writeFileSync(tmp, html);
  const page = await browser.newPage({viewport: {width: b.w, height: b.h}});
  await page.goto(`file://${tmp}`);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(400);
  const out = `${DOCS}/social/valora-${file.replace('.dc.html', '').toLowerCase()}-${b.w}x${b.h}.png`;
  await page.screenshot({path: out, clip: {x: 0, y: 0, width: b.w, height: b.h}});
  fs.unlinkSync(tmp);
  console.log(out);
}
await browser.close();
