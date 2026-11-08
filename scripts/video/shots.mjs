// Renders one shot of the showcase video into video/frames/<shot>/f00000.jpg ...
// Usage: node scripts/video/shots.mjs <shot> [base url]
// Needs the dev server (npm run dev). Frames are exact 1/24 s steps of the page clock.
import fs from 'node:fs';
import {open, record} from './clock.mjs';

const shot = process.argv[2];
const BASE = process.argv[3] ?? 'https://localhost:8081/';
const OUT = `video/frames/${shot}`;
fs.rmSync(OUT, {recursive: true, force: true});
fs.mkdirSync(OUT, {recursive: true});

const lerp = (a, b, k) => a.map((v, i) => v + (b[i] - v) * k);
const ease = (k) => k * k * (3 - 2 * k);
const ISLAND = [0, 0.8, -0.56];

/** A camera move from one framing to another over the shot. */
const move = (page, from, to, seconds, fov = 38) => async (t) => {
  const k = ease(Math.min(1, t / seconds));
  await page.evaluate(([p, l, f]) => VR.cinema({pos: p, look: l, fov: f}), [lerp(from.pos, to.pos, k), lerp(from.look, to.look, k), fov]);
};

async function load(path, wait = 22000) {
  const {browser, page} = await open(BASE + path);
  await page.waitForTimeout(wait);
  return {browser, page};
}

/** A soft cursor drawn into the page so mouse actions read on video. */
async function cursor(page) {
  await page.evaluate(() => {
    const c = document.createElement('div');
    c.id = 'vcursor';
    c.innerHTML = '<svg width="26" height="26" viewBox="0 0 26 26"><path d="M3 2l18 9-8 2-3 8z" fill="#1d1d1f" stroke="#fff" stroke-width="2" stroke-linejoin="round"/></svg><span></span>';
    c.style.cssText = 'position:fixed;left:-50px;top:-50px;z-index:99999;pointer-events:none;transform:translate(-3px,-2px)';
    const ring = c.querySelector('span');
    ring.style.cssText = 'position:absolute;left:-14px;top:-14px;width:30px;height:30px;border-radius:50%;border:3px solid #c8643c;opacity:0;transition:none';
    document.body.append(c);
    addEventListener('pointermove', (e) => { c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px'; }, true);
    addEventListener('pointerdown', () => { ring.style.opacity = '1'; ring.style.transform = 'scale(.6)'; }, true);
    addEventListener('pointerup', () => { ring.style.opacity = '0'; }, true);
  });
}

/** Glide the mouse between points over n frames (called once per frame). */
function glide(page, path) {
  // path: [{t, x, y, down?, up?}] keyframes in seconds; position eased between them
  let pressed = false;
  return async (t) => {
    let i = 0;
    while (i < path.length - 1 && path[i + 1].t <= t) i++;
    const a = path[i];
    const b = path[Math.min(i + 1, path.length - 1)];
    const k = b.t > a.t ? ease(Math.min(1, Math.max(0, (t - a.t) / (b.t - a.t)))) : 1;
    await page.mouse.move(a.x + (b.x - a.x) * k, a.y + (b.y - a.y) * k);
    const want = path.filter((p) => p.t <= t).reduce((s, p) => (p.down ? true : p.up ? false : s), false);
    if (want && !pressed) await page.mouse.down();
    if (!want && pressed) await page.mouse.up();
    pressed = want;
  };
}

const shots = {
  // ---------------- trailer ----------------
  async t_ph() {
    const {browser, page} = await load('?country=ph&level=1');
    await page.evaluate(() => { VR.chrome(false); VR.setHour(7.25); });
    await record(page, OUT, 3.5, async (t) => {
      await page.evaluate((h) => VR.setHour(Math.round(h * 4) / 4), 7.25 + t * 0.6);
      await move(page, {pos: [-1.35, 1.2, 0.35], look: ISLAND}, {pos: [-0.85, 1.12, 0.75], look: ISLAND}, 3.5)(t);
    });
    await browser.close();
  },
  async t_th() {
    const {browser, page} = await load('?country=th&level=1');
    await page.evaluate(() => VR.chrome(false));
    await record(page, OUT, 3, move(page, {pos: [0.95, 0.86, 0.45], look: [-0.1, 0.79, -0.25]}, {pos: [0.55, 0.84, 0.55], look: [-0.25, 0.79, -0.3]}, 3, 36));
    await browser.close();
  },
  async t_id() {
    const {browser, page} = await load('?country=id&level=1');
    await page.evaluate(() => VR.chrome(false));
    await record(page, OUT, 3, move(page, {pos: [-0.95, 1.05, 0.05], look: ISLAND}, {pos: [-0.75, 0.98, 0.35], look: [0, 0.8, -0.5]}, 3, 40));
    await browser.close();
  },
  async t_sg() {
    const {browser, page} = await load('?country=sg&level=1');
    await page.evaluate(() => VR.chrome(false));
    await record(page, OUT, 3, move(page, {pos: [-0.55, 0.9, 0.25], look: [0.3, 1.02, -0.75]}, {pos: [-0.35, 0.86, 0.32], look: [0.35, 1.12, -0.8]}, 3, 42));
    await browser.close();
  },
  async t_watch() {
    // over the neighbour's shoulder: the red line of sight lands on the reading chair
    const {browser, page} = await load('?country=ph&level=1');
    await page.evaluate(() => VR.chrome(false));
    await record(page, OUT, 3, move(page, {pos: [0.62, 1.04, -0.28], look: [-0.12, 0.8, -0.66]}, {pos: [0.5, 1.0, -0.34], look: [-0.12, 0.8, -0.66]}, 3, 34));
    await browser.close();
  },
  // ---------------- walkthrough ----------------
  async w_globe() {
    const {browser, page} = await load('', 18000);
    await cursor(page);
    const th = await page.locator('.vh-place[data-country="th"]').boundingBox();
    const ph = await page.locator('.vh-place[data-country="ph"]').boundingBox();
    const c = (b) => ({x: b.x + b.width * 0.4, y: b.y + b.height / 2});
    await record(page, OUT, 6.5, glide(page, [
      {t: 0, x: 900, y: 700}, {t: 0.8, ...c(th)}, {t: 2.4, ...c(th)}, {t: 3.0, ...c(ph)}, {t: 3.4, ...c(ph), down: true}, {t: 3.5, ...c(ph), up: true}, {t: 6.5, ...c(ph)},
    ]));
    await browser.close();
  },
  async w_tiki() {
    const {browser, page} = await load('?country=ph&level=1');
    await cursor(page);
    const b = await page.locator('[data-act="next"]').boundingBox();
    const x = b.x + b.width / 2, y = b.y + b.height / 2;
    await record(page, OUT, 4.5, glide(page, [{t: 0, x: 1000, y: 380}, {t: 1.6, x, y}, {t: 2.0, x, y, down: true}, {t: 2.1, x, y, up: true}, {t: 4.5, x: x - 60, y: y - 160}]));
    await browser.close();
  },
  async w_place() {
    const {browser, page} = await load('?country=ph&level=1');
    await cursor(page);
    await page.evaluate(() => { VR.tapTiki(); });
    await page.waitForTimeout(1500);
    const p = await page.evaluate(() => VR.pieceScreen('screen', 0));
    const s = await page.evaluate(() => VR.socketScreen(2));
    const q = {x: p.x, y: p.y - 10};
    const z = {x: s.x, y: s.y - 9};
    await record(page, OUT, 7, glide(page, [
      {t: 0, x: 980, y: 560}, {t: 1.0, ...q}, {t: 1.3, ...q, down: true}, {t: 2.9, ...z, down: true}, {t: 3.1, ...z, up: true}, {t: 4.3, ...z}, {t: 4.5, ...z, down: true}, {t: 4.6, ...z, up: true}, {t: 7, x: z.x + 120, y: z.y + 120},
    ]));
    await browser.close();
  },
  async w_sun() {
    const {browser, page} = await load('?country=ph&level=2');
    await cursor(page);
    await page.evaluate(() => { VR.tapTiki(); });
    const a = await page.evaluate(() => { const p = VR.worldPos('sun'); return VR.worldToScreen(p); });
    // sweep the sun from morning to late afternoon along its arc: follow the handle on screen
    await record(page, OUT, 5.5, async (t, i) => {
      if (i === 0) { await page.mouse.move(a.x, a.y); await page.mouse.down(); }
      const h = 9 + Math.min(1, t / 5) * 7;
      const at = await page.evaluate((h) => { VR.setHour(h); return VR.worldToScreen(VR.worldPos('sun')); }, h);
      await page.mouse.move(at.x, at.y);
      if (t > 5.3) await page.mouse.up();
    });
    await browser.close();
  },
  async w_day() {
    const {browser, page} = await load('?country=ph&level=1');
    await page.evaluate(() => { VR.place([{kind: 'screen', socket: 2, rot: 1}], 0); });
    await page.waitForTimeout(1500);
    await page.evaluate(() => VR.live());
    // time-lapse: two page frames per video frame (labelled 2x in the edit)
    await record(page, OUT, 6.5, async () => { await page.evaluate(() => window.__frame(1000 / 24)); });
    await browser.close();
  },
  async w_ph3() { await twist('ph', 2, [-0.95, 1.15, 0.3]); },
  async w_th1() { await twist('th', 0, [0.8, 1.0, 0.55]); },
  async w_id1() { await twist('id', 0, [-0.9, 1.1, 0.35]); },
  async w_sg1() { await twist('sg', 0, [-0.6, 1.05, 0.5]); },
  async w_vr() {
    const {browser, page} = await load('?country=ph&level=1', 18000);
    await page.getByText('Enter XR').click();
    await page.waitForTimeout(6000);
    // hide the emulator's control panels for a clean view; the badge in the edit says it is the emulator
    await page.evaluate(() => {
      for (const el of document.body.children) if (!el.id?.includes('scene') && !el.classList.contains('vh') && el.tagName !== 'CANVAS' && el.tagName !== 'SCRIPT') el.style.visibility = 'hidden';
      const d = window.IWER_DEVICE;
      d.primaryInputMode = 'hand';
      const pitch = (-24 * Math.PI) / 180;
      d.quaternion.set(Math.sin(pitch / 2), 0, 0, Math.cos(pitch / 2));
    });
    await page.waitForTimeout(4000);
    const A = await page.evaluate(() => {
      const v = (n) => VR.worldPos(n);
      return {tiki: v('tiki'), piece: VR.pieceWorld ? VR.pieceWorld('screen', 0) : null, rig: null};
    });
    // aim the right hand at world points from a seated hand position (rig space)
    const HAND = [0.12, 1.3, -0.3];
    const aimQ = (from, to) => {
      const d = to.map((v, k) => v - from[k]);
      const yaw = Math.atan2(-d[0], -d[2]);
      const pitch = Math.atan2(d[1], Math.hypot(d[0], d[2]));
      const cy = Math.cos(yaw / 2), sy = Math.sin(yaw / 2), cx = Math.cos(pitch / 2), sx = Math.sin(pitch / 2);
      return [cy * sx, sy * cx, -sy * sx, cy * cx];
    };
    const info = await page.evaluate(() => {
      const rig = VR.rig();
      return {rig, tiki: VR.worldPos('tiki'), piece: VR.pieceWorld('screen', 0), sock: VR.socketWorld(2)};
    });
    const world = (p) => p.map((v, k) => v - info.rig[k]); // world target -> rig space
    const handPose = async (target, pinch) => {
      const q = aimQ(HAND, world(target));
      await page.evaluate(([h, q, pinch]) => {
        const r = window.IWER_DEVICE.hands.right;
        r.position.set(h[0], h[1], h[2]);
        r.quaternion.set(q[0], q[1], q[2], q[3]);
        r.updatePinchValue(pinch);
      }, [HAND, q, pinch]);
    };
    await record(page, OUT, 8, async (t) => {
      if (t < 1.6) return handPose(lerp([info.tiki[0] + 0.2, info.tiki[1], info.tiki[2]], info.tiki, ease(t / 1.6)), 0);
      if (t < 2.2) return handPose(info.tiki, 1);
      if (t < 3.6) return handPose(lerp(info.tiki, info.piece, ease((t - 2.2) / 1.4)), 0);
      if (t < 4.0) return handPose(info.piece, 1);
      if (t < 5.6) return handPose(lerp(info.piece, info.sock, ease((t - 4.0) / 1.6)), 1);
      return handPose(info.sock, 0);
    });
    await browser.close();
  },
};

async function twist(country, level, pos) {
  const {browser, page} = await load(`?country=${country}&level=${level + 1}`);
  await page.evaluate(() => VR.tapTiki());
  await page.waitForTimeout(800);
  await record(page, OUT, 3.2, async () => {});
  await browser.close();
}

if (!shots[shot]) {
  console.log('shots:', Object.keys(shots).join(' '));
  process.exit(1);
}
const t0 = Date.now();
await shots[shot]();
console.log(shot, 'done in', Math.round((Date.now() - t0) / 1000), 's');
