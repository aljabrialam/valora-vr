// Renders one shot of the showcase video into video/frames/<shot>/f00000.jpg ...
// Usage: node scripts/video/shots.mjs <shot> [base url]
// Needs the dev server (npm run dev). Frames are exact 1/24 s steps of the page clock.
import fs from 'node:fs';
import {open, record as recordFull} from './clock.mjs';
const record = (page, dir, seconds, each, start) => recordFull(page, dir, process.env.PREVIEW ? 1 / 24 : seconds, each, start);

const shot = process.argv[2];
const BASE = process.argv[3] ?? 'https://localhost:8081/';
const OUT = `video/frames/${shot}`;
// PREVIEW=1 renders one frame per shot, to check framing before the long capture
const PREVIEW = !!process.env.PREVIEW;
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

async function load(path, wait = 22000, cleanUi = true) {
  const {browser, page} = await open(BASE + path, {w: +(process.env.VW || 1280), h: +(process.env.VH || 720)});
  await page.waitForTimeout(wait);
  if (cleanUi) await hideXrButton(page);
  return {browser, page};
}

/** The Enter XR button sits in a shadow-DOM host directly under <body>. */
async function hideXrButton(page) {
  await page.evaluate(() => {
    for (const el of document.body.children) if (el.shadowRoot) el.style.display = 'none';
  });
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
    await record(page, OUT, 3.2, async (t) => {
      await page.evaluate((h) => VR.setHour(Math.round(h * 4) / 4), 7.25 + t * 0.6);
      await move(page, {pos: [-1.35, 1.2, 0.35], look: ISLAND}, {pos: [-0.9, 1.12, 0.72], look: ISLAND}, 3.2)(t);
    });
    await browser.close();
  },
  async t_th() {
    const {browser, page} = await load('?country=th&level=1');
    await page.evaluate(() => VR.chrome(false));
    await record(page, OUT, 2.5, move(page, {pos: [1.05, 1.02, 0.45], look: [0.0, 0.8, -0.45]}, {pos: [0.85, 0.98, 0.62], look: [-0.05, 0.8, -0.45]}, 2.5, 40));
    await browser.close();
  },
  async t_id() {
    const {browser, page} = await load('?country=id&level=1');
    await page.evaluate(() => VR.chrome(false));
    await record(page, OUT, 2.5, move(page, {pos: [-0.95, 1.05, 0.05], look: ISLAND}, {pos: [-0.78, 0.99, 0.32], look: [0, 0.8, -0.5]}, 2.5, 40));
    await browser.close();
  },
  async t_sg() {
    const {browser, page} = await load('?country=sg&level=1');
    await page.evaluate(() => VR.chrome(false));
    await record(page, OUT, 2.5, move(page, {pos: [-0.55, 0.92, 0.25], look: [0.25, 1.0, -0.75]}, {pos: [-0.4, 0.88, 0.32], look: [0.3, 1.08, -0.8]}, 2.5, 44));
    await browser.close();
  },
  async t_vn() {
    const {browser, page} = await load('?country=vn&level=1');
    await page.evaluate(() => VR.chrome(false));
    await record(page, OUT, 2.5, move(page, {pos: [0.95, 0.98, 0.5], look: [0.02, 0.8, -0.42]}, {pos: [0.7, 0.95, 0.66], look: [-0.04, 0.8, -0.42]}, 2.5, 40));
    await browser.close();
  },
  async t_my() {
    const {browser, page} = await load('?country=my&level=1');
    await page.evaluate(() => VR.chrome(false));
    await record(page, OUT, 2.5, move(page, {pos: [-0.25, 1.05, 0.75], look: [-0.35, 1.0, -0.6]}, {pos: [-0.05, 1.0, 0.8], look: [-0.3, 0.98, -0.6]}, 2.5, 46));
    await browser.close();
  },
  async t_watch() {
    // over the neighbour's shoulder: the red line of sight lands on the reading chair
    const {browser, page} = await load('?country=ph&level=1');
    await page.evaluate(() => VR.chrome(false));
    await record(page, OUT, 2.8, move(page, {pos: [0.345, 1.0, -0.13], look: [-0.011, 0.872, -0.649]}, {pos: [0.32, 0.99, -0.16], look: [-0.02, 0.87, -0.65]}, 2.8, 40));
    await browser.close();
  },
  // ---------------- walkthrough ----------------
  async w_globe() {
    const {browser, page} = await load('', 18000);
    await cursor(page);
    const th = await page.locator('.vh-place[data-country="th"]').boundingBox();
    const ph = await page.locator('.vh-place[data-country="ph"]').boundingBox();
    const c = (b) => ({x: b.x + b.width * 0.4, y: b.y + b.height / 2});
    await record(page, OUT, 6, glide(page, [
      {t: 0, x: 900, y: 700}, {t: 0.8, ...c(th)}, {t: 2.4, ...c(th)}, {t: 3.0, ...c(ph)}, {t: 3.4, ...c(ph), down: true}, {t: 3.5, ...c(ph), up: true}, {t: 6, ...c(ph)},
    ]));
    await browser.close();
  },
  // the demo: choose a place on the globe (browser view, before entering VR), then point at Enter XR
  async d_globe() {
    const {browser, page} = await load('', 18000, false);
    await cursor(page);
    const box = async (id) => page.locator(`.vh-place[data-country="${id}"]`).boundingBox();
    const c = (b) => ({x: b.x + b.width * 0.4, y: b.y + b.height / 2});
    const vn = c(await box('vn')), my = c(await box('my')), ph = c(await box('ph'));
    const first = glide(page, [
      {t: 0, x: 900, y: 760}, {t: 0.9, ...vn}, {t: 2.3, ...vn}, {t: 2.9, ...my}, {t: 4.3, ...my}, {t: 4.9, ...ph}, {t: 5.3, ...ph, down: true}, {t: 5.4, ...ph, up: true}, {t: 7.4, ...ph},
    ]);
    const n = await record(page, OUT, 7.4, first);
    // the place opens on the desk; the Enter XR button waits bottom centre
    const xr = await page.evaluate(() => {
      for (const el of document.body.children) if (el.shadowRoot) { const b = el.shadowRoot.querySelector('button') ?? el; const r = b.getBoundingClientRect(); return {x: r.x + r.width / 2, y: r.y + r.height / 2}; }
      return {x: 640, y: 660};
    });
    // hover only: a real click would open the emulator's own panels; the headset shots take over from here
    await record(page, OUT, 2.0, glide(page, [{t: 0, ...ph}, {t: 1.3, ...xr}, {t: 2.0, ...xr}]), n);
    await browser.close();
  },
  async w_tiki() {
    const {browser, page} = await load('?country=ph&level=1');
    await cursor(page);
    const b = await page.locator('[data-act="next"]').boundingBox();
    const x = b.x + b.width / 2, y = b.y + b.height / 2;
    await record(page, OUT, 2.5, glide(page, [{t: 0, x: x + 300, y: y - 200}, {t: 1.0, x, y}, {t: 1.3, x, y, down: true}, {t: 1.4, x, y, up: true}, {t: 2.5, x: x - 60, y: y - 160}]));
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
    await record(page, OUT, 5, glide(page, [
      {t: 0, x: q.x + 150, y: q.y - 80}, {t: 0.7, ...q}, {t: 0.9, ...q, down: true}, {t: 2.3, ...z, down: true}, {t: 2.5, ...z, up: true}, {t: 3.3, ...z}, {t: 3.5, ...z, down: true}, {t: 3.6, ...z, up: true}, {t: 5, x: z.x + 90, y: z.y + 90},
    ]));
    await browser.close();
  },
  async w_sun() {
    const {browser, page} = await load('?country=ph&level=2');
    await cursor(page);
    await page.evaluate(() => { VR.tapTiki(); });
    const a = await page.evaluate(() => { const p = VR.worldPos('sun'); return VR.worldToScreen(p); });
    // sweep the sun from morning to late afternoon along its arc: follow the handle on screen
    await record(page, OUT, 3.5, async (t, i) => {
      if (i === 0) { await page.mouse.move(a.x, a.y); await page.mouse.down(); }
      const h = 9 + Math.min(1, t / 3.2) * 7;
      const at = await page.evaluate((h) => { VR.setHour(h); return VR.worldToScreen(VR.worldPos('sun')); }, h);
      await page.mouse.move(at.x, at.y);
      if (t > 3.4) await page.mouse.up();
    });
    await browser.close();
  },
  async w_day() {
    const {browser, page} = await load('?country=ph&level=1');
    await page.evaluate(() => { VR.place([{kind: 'screen', socket: 2, rot: 1}], 0); });
    await page.waitForTimeout(1500);
    await page.evaluate(() => VR.live());
    // time-lapse: two page frames per video frame (labelled 2x in the edit)
    await record(page, OUT, 4, async () => { await page.evaluate(() => window.__frame(1000 / 24)); await page.evaluate(() => window.__frame(1000 / 24)); });
    await browser.close();
  },
  async w_ph3() { await twist('ph', 2, [-0.95, 1.15, 0.3]); },
  async w_th1() { await twist('th', 0, [0.8, 1.0, 0.55]); },
  async w_id1() { await twist('id', 0, [-0.9, 1.1, 0.35]); },
  async w_sg1() { await twist('sg', 0, [-0.6, 1.05, 0.5]); },
  async w_vr() {
    const {browser, page} = await load('?country=ph&level=1', 18000, false);
    await page.getByText('Enter XR').click();
    await page.waitForTimeout(8000);
    // hide the emulator's panels, toolbar and gizmo overlay; keep the game's canvas and the page HUD
    // (the edit labels this footage as the emulator)
    await page.evaluate(() => {
      const game = [...document.querySelectorAll('canvas')].find((c) => getComputedStyle(c).position !== 'fixed');
      // walk up from the game's canvas: at each level, hide every sibling except the page HUD
      let node = game;
      while (node && node !== document.body) {
        for (const sib of node.parentElement.children) {
          if (sib === node || sib.classList.contains('vh') || sib.tagName === 'SCRIPT') continue;
          sib.style.display = 'none';
        }
        node = node.parentElement;
      }
      window.IWER_DEVICE.primaryInputMode = 'hand';
    });
    await page.waitForTimeout(3000);
    const ok = await page.evaluate(() => { VR.recentreNow(); return JSON.stringify(VR.rig()); });
    console.log('rig after recentre', ok);
    await page.evaluate(() => VR.tilt(26));
    const info = await page.evaluate(() => ({tiki: VR.toRig(VR.worldPos('tiki')), piece: VR.toRig(VR.pieceWorld('screen', 0)), sock: VR.toRig(VR.socketWorld(2))}));
    // the right hand rests low and forward of the head, in rig space; aim it at rig-space targets
    const HAND = [0.12, 1.3, -0.3];
    const aimQ = (from, to) => {
      const d = to.map((v, k) => v - from[k]);
      const yaw = Math.atan2(-d[0], -d[2]);
      const pitch = Math.atan2(d[1], Math.hypot(d[0], d[2]));
      const cy = Math.cos(yaw / 2), sy = Math.sin(yaw / 2), cx = Math.cos(pitch / 2), sx = Math.sin(pitch / 2);
      return [cy * sx, sy * cx, -sy * sx, cy * cx];
    };
    const handPose = async (target, pinch) => {
      const q = aimQ(HAND, target);
      await page.evaluate(([h, q, pinch]) => {
        const r = window.IWER_DEVICE.hands.right;
        r.position.set(h[0], h[1], h[2]);
        r.quaternion.set(q[0], q[1], q[2], q[3]);
        r.updatePinchValue(pinch);
      }, [HAND, q, pinch]);
    };
    const off = (p, dx) => [p[0] + dx, p[1], p[2]];
    await record(page, OUT, 6, async (t) => {
      if (t < 1.6) return handPose(lerp(off(info.tiki, 0.25), info.tiki, ease(t / 1.6)), 0);
      if (t < 2.2) return handPose(info.tiki, 1);
      if (t < 3.6) return handPose(lerp(info.tiki, info.piece, ease((t - 2.2) / 1.4)), 0);
      if (t < 4.0) return handPose(info.piece, 1);
      if (t < 5.3) return handPose(lerp(info.piece, info.sock, ease((t - 4.0) / 1.3)), 1);
      return handPose(info.sock, 0);
    });
    await browser.close();
  },
};

async function twist(country, level, pos) {
  const {browser, page} = await load(`?country=${country}&level=${level + 1}`);
  await page.evaluate(() => VR.tapTiki());
  await page.waitForTimeout(800);
  await record(page, OUT, 2, async () => {});
  await browser.close();
}

if (!shots[shot]) {
  console.log('shots:', Object.keys(shots).join(' '));
  process.exit(1);
}
const t0 = Date.now();
await shots[shot]();
console.log(shot, 'done in', Math.round((Date.now() - t0) / 1000), 's');
