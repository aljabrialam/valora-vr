// The headset-view demo shots: a seated player's view in Meta's IWER emulator, the right hand
// pointing and pinching. Each shot is a timeline of segments; the hand's ray target, the pinch and
// the head's pitch and yaw ease from one segment to the next, one frame at a time.
//   node scripts/video/vrshots.mjs <shot> [base url]      -> video/frames/<shot>/f00000.jpg ...
//   TEST=1 renders at quarter size and keeps every 24th frame, to check the actions land.
import fs from 'node:fs';
import {open, record} from './clock.mjs';
import {serveHandModels, enterVR, pose as poseAt, watchAnchors, watchLog} from './vr.mjs';
// the right hand rests above the desk, forward and right of the head (rig space): its ray must come
// down onto the desk plane for a carried piece to follow it
const HAND = process.env.INPUT === 'controller' ? [0.22, 1.36, -0.3] : [0.14, 1.44, -0.24];
const pose = (page, rig, at, pinch, head) => poseAt(page, rig, at, pinch, head, HAND);

const shot = process.argv[2];
const BASE = process.argv[3] ?? 'https://localhost:8081/';
const OUT = `video/frames/${shot}`;
const TEST = !!process.env.TEST;
const W = TEST ? 480 : +(process.env.VW || 960), H = TEST ? 270 : +(process.env.VH || 540);

const lerp = (a, b, k) => a.map((v, i) => v + (b[i] - v) * k);
const ease = (k) => k * k * (3 - 2 * k);
const up = (p, dy) => [p[0], p[1] + dy, p[2]];
const HEAD = {pitch: -27, yaw: 0};
const LOOK_RAFT = HEAD; // the emulated hand moves with the head: keep the head still while the hand works
// leaning in to read the level card at the back of the desk
const CARD_LEAN = JSON.parse(process.env.CARD_LEAN ?? '[0, 0.16, -0.86]');
const CARD_HEAD = JSON.parse(process.env.CARD_HEAD ?? '{"pitch": 8, "yaw": 0}');

/**
 * Plays segments [{d: seconds, to: worldPoint, pinch: 0|1, head?: {pitch, yaw}, hold?: true}];
 * each segment eases from the previous segment's end state to its own `to` and `head`.
 */
async function play(page, rig, segs, start = {at: segs[0].to, head: HEAD}, first = 0) {
  const total = segs.reduce((s, x) => s + x.d, 0);
  let st = {at: start.at, head: start.head, lean: start.lean ?? LEANED.cur.slice()};
  const ends = [];
  for (const s of segs) {
    const from = st;
    const to = {at: s.to ?? from.at, head: s.head ?? from.head, pinch: s.pinch ?? 0, lean: s.lean ?? from.lean};
    ends.push({from, to, d: s.d});
    st = to;
  }
  const next = await record(page, TEST ? `${OUT}-all` : OUT, total, async (t) => {
    let acc = 0;
    for (const e of ends) {
      if (t < acc + e.d || e === ends[ends.length - 1]) {
        const k = ease(Math.min(1, (t - acc) / e.d));
        const at = lerp(e.from.at, e.to.at, k);
        const head = {pitch: e.from.head.pitch + (e.to.head.pitch - e.from.head.pitch) * k, yaw: e.from.head.yaw + (e.to.head.yaw - e.from.head.yaw) * k};
        // leaning in (to read the level card): move the player, and the hand with it
        const want = lerp(e.from.lean, e.to.lean, k);
        const dl = want.map((v, i) => v - LEANED.cur[i]);
        if (dl.some((v) => Math.abs(v) > 1e-5)) {
          await page.evaluate((d) => VR.lean(d[0], d[1], d[2]), dl);
          LEANED.cur = want;
        }
        await pose(page, rig.map((v, i) => v + LEANED.cur[i]), at, e.to.pinch, head);
        return;
      }
      acc += e.d;
    }
  }, first);
  if (TEST) {
    // keep one frame a second for checking
    const dir = `${OUT}-all`;
    for (const f of fs.readdirSync(dir)) {
      const n = +f.slice(1, 6);
      if (n % 24 === 0) fs.renameSync(`${dir}/${f}`, `${OUT}/${f}`);
    }
    fs.rmSync(dir, {recursive: true, force: true});
  }
  return next;
}
// how far the player has leaned from where the shot started (site of the rig returned by setup)
const LEANED = {cur: [0, 0, 0]};

async function setup(path) {
  const {browser, page} = await open(BASE + path, {w: W, h: H});
  await serveHandModels(page);
  const A = watchAnchors(page);
  const log = watchLog(page);
  await page.reload({waitUntil: 'load', timeout: 90000});
  await page.waitForTimeout(24000);
  await enterVR(page);
  // a seated player leans in over the desk model: closer, so the pieces read on video
  const rig = await page.evaluate(([dy, dz]) => VR.lean(0, dy, dz), [+(process.env.LEAN_Y ?? 0), +(process.env.LEAN_Z ?? -0.14)]);
  await page.evaluate(() => window.__manual());
  // settle the pose before the first recorded frame
  for (let i = 0; i < 6; i++) {
    await pose(page, rig, A().tiki, 0, HEAD);
    await page.evaluate(() => window.__frame(1000 / 24));
  }
  const piece = async (kind, n = 0) => page.evaluate(([k, n]) => VR.pieceWorld(k, n), [kind, n]);
  return {browser, page, rig, A: A(), log, piece};
}

/** One country's level 1 solved with one piece: pick it off the raft, carry it to its socket. */
async function countrySolve(country, kind, socket, rot = 0, extra = []) {
  const {browser, page, rig, A, log, piece} = await setup(`?country=${country}&level=1`);
  // this is the first level played in this page, so the tutorial says hello first: pinch Tiki
  const p = await piece(kind);
  const s = A.sockets[socket];
  await play(page, rig, [
    {d: 0.8, to: A.tiki},
    {d: 0.5, to: A.tiki, pinch: 1},
    {d: 0.6, to: A.tiki},
    {d: 1.3, to: p, head: LOOK_RAFT},
    {d: 0.6, to: p, pinch: 1},
    {d: 1.8, to: s, pinch: 1},
    {d: 0.5, to: s, pinch: 1},
    {d: 0.7, to: s, head: HEAD},
    ...extra,
    {d: 1.0, to: up(s, 0.06)},
    {d: 2.0, to: up(s, 0.06), head: {pitch: -22, yaw: 0}},
  ]);
  console.log(log.filter((l) => /design|step/.test(l)).slice(-3).join('\n'));
  await browser.close();
}

const shots = {
  // Manila: look down at the desk, pinch Tiki, carry the screen to its socket, turn it: solved
  async v_ph() {
    const {browser, page, rig, A, log, piece} = await setup('?country=ph&level=1');
    const p = await piece('screen');
    const s = A.sockets[2];
    await play(page, rig, [
      {d: 1.2, to: A.tiki, head: {pitch: -8, yaw: 10}},
      {d: 1.6, to: A.tiki, head: HEAD},
      {d: 0.5, to: A.tiki, pinch: 1},
      {d: 1.0, to: A.tiki},
      {d: 1.4, to: p, head: LOOK_RAFT},
      {d: 0.6, to: p, pinch: 1},
      {d: 2.2, to: s, pinch: 1},
      {d: 0.5, to: s, pinch: 1},
      {d: 1.2, to: s, head: HEAD},
      {d: 0.6, to: A.tiki},
      {d: 0.4, to: A.tiki, pinch: 1},
      {d: 0.8, to: A.tiki},
      {d: 0.9, to: up(s, 0.05)},
      {d: 0.35, to: up(s, 0.05), pinch: 1},
      {d: 2.5, to: up(s, 0.05)},
    ], {at: A.tiki, head: {pitch: -4, yaw: 18}});
    console.log(log.filter((l) => /design|step|release/.test(l)).slice(-6).join('\n'));
    await browser.close();
  },
  // Manila, level 2 opened fresh: pinch Tiki, then drag the sun from morning to afternoon
  async v_sun() {
    const {browser, page, rig, A, log} = await setup('?country=ph&level=2');
    const arc = await page.evaluate(() => {
      const pts = [];
      for (const h of [7.5, 9, 10.5, 12, 13.5, 15, 16.5]) { VR.setHour(h); pts.push(VR.worldPos('sun')); }
      VR.setHour(10);
      return pts;
    });
    const sun0 = await page.evaluate(() => VR.worldPos('sun'));
    await play(page, rig, [
      {d: 0.6, to: A.tiki},
      {d: 0.4, to: A.tiki, pinch: 1},
      {d: 0.8, to: A.tiki},
      {d: 1.2, to: sun0, head: {pitch: -14, yaw: 0}},
      {d: 0.5, to: sun0, pinch: 1},
      {d: 1.4, to: arc[0], pinch: 1, head: {pitch: -14, yaw: 6}},
      ...arc.slice(1).map((p, i) => ({d: 0.75, to: p, pinch: 1, head: {pitch: -14, yaw: 6 - i * 2.5}})),
      {d: 0.5, to: arc[arc.length - 1]},
      {d: 2.0, to: arc[arc.length - 1], head: {pitch: -24, yaw: 0}},
    ]);
    console.log(log.filter((l) => /sun|step/.test(l)).slice(-4).join('\n'));
    await browser.close();
  },
  // Manila level 1 solved by script, then the hand presses play and the day runs (two frames per frame)
  async v_day() {
    const {browser, page, rig, A, log} = await setup('?country=ph&level=1');
    await page.evaluate(() => { VR.tapTiki(); VR.place([{kind: 'screen', socket: 2, rot: 1}], 0); });
    await play(page, rig, [
      {d: 1.0, to: A.play},
      {d: 0.4, to: A.play, pinch: 1},
      {d: 0.6, to: A.play},
    ]);
    const n = fs.readdirSync(OUT).length;
    await record(page, OUT, TEST ? 2 : 9, async () => { await pose(page, rig, A.play, 0, {pitch: -20, yaw: 0}); await page.evaluate(() => window.__frame(1000 / 24)); }, n);
    console.log(log.filter((l) => /day|step/.test(l)).slice(-3).join('\n'));
    await browser.close();
  },
  async v_th() { await countrySolve('th', 'hedge', 22); },
  // Bangkok: a seated look around the desk model (the hand rests), then back down to the courtyard
  async v_look() {
    const {browser, page, rig, A} = await setup('?country=th&level=1');
    await play(page, rig, [
      {d: 2.2, to: A.tiki, head: {pitch: -14, yaw: 26}},
      {d: 2.6, to: A.tiki, head: {pitch: -12, yaw: -24}},
      {d: 1.8, to: A.tiki, head: HEAD},
      {d: 0.8, to: A.tiki},
    ], {at: A.tiki, head: {pitch: -20, yaw: 6}});
    await browser.close();
  },
  // Bangkok level 2, Lunch by the Water: two screens, each carried to its socket and turned
  async v_th2() {
    const {browser, page, rig, A, log, piece} = await setup('?country=th&level=2');
    const p0 = await piece('screen', 0);
    const s16 = A.sockets[16], s22 = A.sockets[22];
    const tap = (s) => [{d: 0.6, to: up(s, 0.05)}, {d: 0.3, to: up(s, 0.05), pinch: 1}, {d: 0.55, to: up(s, 0.05)}];
    const n = await play(page, rig, [
      {d: 0.8, to: A.tiki},
      {d: 0.5, to: A.tiki, pinch: 1},
      {d: 0.6, to: A.tiki},
      {d: 1.2, to: up(p0, 0.02)},
      {d: 0.5, to: up(p0, 0.02), pinch: 1},
      {d: 1.6, to: s16, pinch: 1},
      {d: 0.4, to: s16, pinch: 1},
      {d: 0.5, to: s16},
      ...tap(s16), ...tap(s16),
    ]);
    // the second screen waits on the raft where the first one was stacked: find it now
    const p1 = await piece('screen', 1);
    await play(page, rig, [
      {d: 1.2, to: up(p1, 0.02)},
      {d: 0.5, to: up(p1, 0.02), pinch: 1},
      {d: 1.6, to: s22, pinch: 1},
      {d: 0.4, to: s22, pinch: 1},
      {d: 0.5, to: s22},
      ...tap(s22),
      {d: 2.6, to: up(s22, 0.08)},
    ], {at: up(s16, 0.05), head: HEAD}, n);
    console.log(log.filter((l) => /design|release/.test(l)).slice(-6).join('\n'));
    await browser.close();
  },

  // a quick check of where Tiki's words sit in the default seated view (TEST=1)
  async v_bubble() {
    const {browser, page, rig, A} = await setup('?country=ph&level=1');
    await play(page, rig, [{d: 0.6, to: A.tiki}, {d: 0.4, to: A.tiki, pinch: 1}, {d: 1.2, to: A.tiki}, {d: 1.0, to: A.tiki, head: {pitch: -8, yaw: 10}}, {d: 1.1, to: A.tiki}]);
    await browser.close();
  },
  // a quick check of the lean-in framing for the level card (TEST=1)
  async v_cardprobe() {
    const {browser, page, rig, A} = await setup('?country=vn&level=2');
    const card = await page.evaluate(() => VR.worldPos('card'));
    console.log('rig', rig, 'card', card);
    await play(page, rig, [{d: 1.0, to: up(card, -0.08), head: CARD_HEAD, lean: CARD_LEAN}, {d: 1.1, to: up(card, -0.08)}]);
    await browser.close();
  },
  async v_id() { await countrySolve('id', 'pergola', 15); },
  // Hanoi: hide the garden table from the motorbikes in the lane (film with INPUT=controller for Touch)
  async v_vn() { await countrySolve('vn', 'hedge', 22); },
  // Kuala Lumpur: a tree's canopy hides the table from the condo towers
  async v_my() { await countrySolve('my', 'tree', 6); },
  // Hanoi level 2, two watchers at once: a screen for the neighbour, a hedge for the riders. Both
  // rules turn to DONE, the card fills three stars (two pieces, par two), then the hand presses play.
  async v_score() {
    const {browser, page, rig, A, log, piece} = await setup('?country=vn&level=2');
    const sc = await piece('screen'), he = await piece('hedge');
    const s2 = A.sockets[2], s22 = A.sockets[22];
    const card = await page.evaluate(() => VR.worldPos('card'));
    const n = await play(page, rig, [
      {d: 0.7, to: A.tiki},
      {d: 0.4, to: A.tiki, pinch: 1},
      {d: 0.6, to: A.tiki},
      {d: 1.3, to: up(card, -0.08), head: CARD_HEAD, lean: CARD_LEAN},
      {d: 2.2, to: up(card, -0.08)},
      {d: 1.3, to: sc, head: HEAD, lean: [0, 0, 0]},
      {d: 0.5, to: sc, pinch: 1},
      {d: 1.7, to: s2, pinch: 1},
      {d: 0.4, to: s2, pinch: 1},
      {d: 0.6, to: s2},
    ]);
    const he2 = await piece('hedge');
    const m = await play(page, rig, [
      {d: 1.2, to: he2},
      {d: 0.5, to: he2, pinch: 1},
      {d: 1.7, to: s22, pinch: 1},
      {d: 0.4, to: s22, pinch: 1},
      {d: 0.6, to: s22},
      {d: 1.3, to: up(card, -0.08), head: CARD_HEAD, lean: CARD_LEAN},
      {d: 3.0, to: up(card, -0.08)},
      {d: 1.3, to: A.play, head: HEAD, lean: [0, 0, 0]},
      {d: 0.4, to: A.play, pinch: 1},
      {d: 0.5, to: A.play},
    ], {at: s2, head: HEAD}, n);
    await record(page, OUT, TEST ? 2 : 6, async () => { await pose(page, rig, A.play, 0, {pitch: -20, yaw: 0}); await page.evaluate(() => window.__frame(1000 / 24)); }, m);
    console.log(log.filter((l) => /design|day|step/.test(l)).slice(-5).join('\n'));
    await browser.close();
  },
  async v_sg() { await countrySolve('sg', 'tree', 1); },
};

if (!shots[shot]) {
  console.log('shots:', Object.keys(shots).join(' '));
  process.exit(1);
}
fs.rmSync(OUT, {recursive: true, force: true});
fs.mkdirSync(OUT, {recursive: true});
const t0 = Date.now();
await shots[shot]();
console.log(`${shot} done in ${Math.round((Date.now() - t0) / 1000)} s`);
