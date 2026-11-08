// Headset-view capture helpers: enter the IWER emulator's immersive session, hide the emulator's own
// panels, look down at the desk like a seated player, and drive the right hand by pointing at things.
// Footage made with this is labelled as the emulator in the edit; it is not a Quest recording.
import fs from 'node:fs';
import path from 'node:path';

// IWSDK loads the hand model from the webxr-input-profiles CDN, which the capture sandbox cannot reach.
// Serve the same files from the npm package instead (npm pack @webxr-input-profiles/assets@1.0).
const PROFILES = process.env.PROFILES_DIR ?? '/tmp/wip/package/dist/profiles';
const CDN = 'https://cdn.jsdelivr.net/npm/@webxr-input-profiles/assets@1.0/dist/profiles/';

export async function serveHandModels(page) {
  await page.route(CDN + '**', async (route) => {
    const rel = route.request().url().slice(CDN.length).split('?')[0];
    const file = path.join(PROFILES, rel);
    if (!fs.existsSync(file)) return route.fulfill({status: 404, body: ''});
    const type = file.endsWith('.json') ? 'application/json' : 'model/gltf-binary';
    await route.fulfill({status: 200, contentType: type, body: fs.readFileSync(file), headers: {'access-control-allow-origin': '*'}});
  });
}

// INPUT=controller films the same actions with Quest Touch controllers: the trigger stands in for the pinch
export const INPUT = process.env.INPUT === 'controller' ? 'controller' : 'hand';
const DEVICE = INPUT === 'controller' ? 'controller-right' : 'hand-right';

/** Enter the emulated session with hands (or controllers), hide the emulator UI, recentre for a seated player. */
export async function enterVR(page) {
  await page.getByText('Enter XR').click();
  await page.waitForTimeout(8000);
  await page.evaluate((mode) => {
    const game = [...document.querySelectorAll('canvas')].find((c) => getComputedStyle(c).position !== 'fixed');
    let node = game;
    while (node && node !== document.body) {
      for (const sib of node.parentElement.children) {
        if (sib === node || sib.classList.contains('vh') || sib.tagName === 'SCRIPT') continue;
        sib.style.display = 'none';
      }
      node = node.parentElement;
    }
    window.IWER_DEVICE.primaryInputMode = mode;
  }, INPUT);
  await page.waitForTimeout(3000);
  return page.evaluate(() => { VR.recentreNow(); return VR.rig(); });
}

// The seated hand rests low and forward of the head (rig space). Aim it by turning the wrist.
export const HAND = [0.12, 1.32, -0.28];

/** Rig-space quaternion (yaw about y, then pitch about x) pointing from `from` to `to`. */
export function aimQ(from, to) {
  const d = to.map((v, k) => v - from[k]);
  const yaw = Math.atan2(-d[0], -d[2]);
  const pitch = Math.atan2(d[1], Math.hypot(d[0], d[2]));
  const cy = Math.cos(yaw / 2), sy = Math.sin(yaw / 2), cx = Math.cos(pitch / 2), sx = Math.sin(pitch / 2);
  return [cy * sx, sy * cx, -sy * sx, cy * cx];
}

/** Head pitch and yaw (degrees), and the right hand's pointing ray from `hand` (rig space) towards
 * world point `at`, through the emulator's remote control (the same calls as `iwsdk xr`). */
export async function pose(page, rig, at, pinch, head = {pitch: -24, yaw: 0}, hand = HAND) {
  const from = hand.map((v, k) => v + rig[k]);
  const d = at.map((v, k) => v - from[k]);
  const yaw = (Math.atan2(-d[0], -d[2]) * 180) / Math.PI;
  const pitch = (Math.atan2(d[1], Math.hypot(d[0], d[2])) * 180) / Math.PI;
  await page.evaluate(([h, ray, pinch, head, device]) => {
    const r = window.IWER_DEVICE.remote;
    // stay under programmatic control (it lapses to manual on a real-time timer, and the emulator's
    // own panel then resets the head and hands)
    r.activateCaptureMode();
    window.IWER_DEVICE.controlMode = 'programmatic';
    r.executeSetTransform({device: 'headset', orientation: {pitch: head.pitch, yaw: head.yaw, roll: 0}});
    r.executeSetTransform({device, position: {x: h[0], y: h[1], z: h[2]}, orientation: {pitch: ray.pitch, yaw: ray.yaw, roll: 0}});
    r.executeSetSelectValue({device, value: pinch});
    // the idle left controller rests low and to the side, out of the way
    if (device === 'controller-right') r.executeSetTransform({device: 'controller-left', position: {x: h[0] - 0.42, y: h[1] - 0.22, z: h[2] + 0.06}, orientation: {pitch: -35, yaw: 20, roll: 0}});
  }, [hand, {pitch, yaw}, pinch, head, DEVICE]);
}

/** Collects the game's '[VR] anchors' log line (world positions of Tiki, the sun, the play button,
 * the raft pieces and the sockets). Call before the page loads; await the returned getter later. */
export function watchAnchors(page) {
  let a = null;
  page.on('console', (m) => { const t = m.text(); if (t.includes('[VR] anchors')) a = JSON.parse(t.slice(t.indexOf('{'))); });
  return () => a;
}
export function watchLog(page, out = []) {
  page.on('console', (m) => { const t = m.text(); if (t.startsWith('[VR]')) out.push(t); });
  return out;
}
export const pieceAt = (page, kind, n = 0) => page.evaluate(([k, n]) => VR.pieceWorld(k, n), [kind, n]);
