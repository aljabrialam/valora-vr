// Emulator end-to-end, hands only (gameplay v2). Requires `npx iwsdk dev up` with its managed browser.
// Steps: pinch Tiki through the intro, grab the screen piece off the raft with a pinch, carry it to
// socket 2, release, pinch it again briefly to turn it, then check the level reports solved.
// Also checks the sun handle can be grabbed and the play button pressed.
// Positions are read from the app's own "[VR] anchors" log line, not recomputed here.
import {execFileSync} from 'node:child_process';

const run = (args) => JSON.parse(execFileSync('npx', ['iwsdk', ...args], {encoding: 'utf8', cwd: process.cwd()}));
// The managed browser can relaunch under software GL; retry once after it does.
const cli = (...args) => {
  try { return run(args); } catch (e) {
    if (!/browser_relaunched/.test(String(e.stderr ?? e))) throw e;
    execFileSync('sleep', ['20']);
    return run(args);
  }
};
const sleep = (s) => execFileSync('sleep', [String(s)]);
const logs = () => cli('browser', 'logs').data.result.map((l) => l.message);
// Emulator poses are relative to the player rig, which the game recentres when the session starts,
// so world targets are aimed from the hand's world position and the pose is sent in rig space.
const HAND = [0.12, 1.32, -0.28]; // rig space: a seated hand, low and forward of the head
let RIG = [0, 0, 0]; // the recentre offset, read from the app's log
const aim = (t) => {
  const from = HAND.map((v, k) => v + RIG[k]);
  const d = [t[0] - from[0], t[1] - from[1], t[2] - from[2]];
  const yaw = (Math.atan2(-d[0], -d[2]) * 180) / Math.PI;
  const pitch = (Math.atan2(d[1], Math.hypot(d[0], d[2])) * 180) / Math.PI;
  return {position: HAND, orientation: {pitch, yaw, roll: 0}};
};
const pose = (position, orientation) => cli('xr', 'run-sequence', '--input-json', JSON.stringify({device: 'hand-right', idleHand: 'rest', body: 'fixed', steps: [{label: 'pose', anchor: 'target-ray', position, orientation, duration: 0.3}]}));
const pinch = (v) => cli('xr', 'set-select-value', '--input-json', JSON.stringify({device: 'hand-right', value: v}));
const tap = (t, hold = 2) => { const a = aim(t); pose(a.position, a.orientation); pinch(1); sleep(hold); pinch(0); sleep(3); };
const results = [];
const check = (name, ok, detail = '') => { results.push({name, ok}); console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}${detail ? '  ' + detail : ''}`); };

// Reload can exceed the 27 s command limit under software GL even though it completes; tolerate that.
try { cli('browser', 'reload'); } catch (e) { if (!/browser_command_timeout/.test(String(e.stderr ?? e))) throw e; }
let anchorLine;
for (let i = 0; i < 12 && !anchorLine; i++) {
  sleep(10);
  try { anchorLine = logs().filter((m) => m.includes('[VR] anchors')).pop(); } catch { /* page still loading */ }
}
if (!anchorLine) { console.log('FAIL  no anchors line; app did not load'); process.exit(1); }
const A = JSON.parse(anchorLine.slice(anchorLine.indexOf('{')));
cli('xr', 'enter');
cli('xr', 'set-input-mode', '--input-json', '{"mode":"hand"}');
pinch(0);
let rc;
for (let i = 0; i < 8 && !rc; i++) { sleep(4); rc = logs().filter((m) => m.includes('[VR] recentre')).pop(); }
if (!rc) { console.log('FAIL  no recentre in the headset session'); process.exit(1); }
RIG = rc.split(' ').pop().split(',').map(Number);
check('Seated recentre on entering VR', true, `rig ${RIG.join(',')}`);
const words = logs().filter((m) => m.includes('[VR] view')).pop() ?? '';
check('Words switch to the headset view', words.includes('headset'));

// 1. Tiki: hello is the only pinch-to-continue before the first action
tap(A.tiki);
let steps = logs().filter((m) => m.includes('[VR] step'));
check('Pinching Tiki starts the tutorial', steps.slice(-1)[0]?.includes('place'), steps.slice(-1)[0] ?? '');

// 2. Grab the screen piece and carry it to socket 2
const piece = A.pieces.find((p) => p.kind === 'screen' && p.n === 0).at;
const sock = A.sockets[2];
const a0 = aim(piece);
pose(a0.position, a0.orientation);
pinch(1); sleep(3);
const N = 6;
for (let i = 1; i <= N; i++) {
  const f = i / N;
  const t = piece.map((v, k) => v + (sock[k] - v) * f);
  pose(a0.position, aim(t).orientation); // wrist turn only; the hand stays put
}
sleep(3);
pinch(0); sleep(4);
let design = logs().filter((m) => m.includes('[VR] design')).pop() ?? '';
check('Hand grab places a raft piece on a socket', /"socket":2/.test(design), design.slice(0, 120));

steps = logs().filter((m) => m.includes('[VR] step'));
check('Placing a piece moves the tutorial on by itself', !steps.slice(-1)[0]?.includes('place'), steps.slice(-1)[0] ?? '');
tap(A.tiki); // the country twist line

// 3. Turn it with a short pinch (tap), then the level should be solved
tap(sock.map((v, k) => v + (k === 1 ? 0.05 : 0)), 1); // aim at the middle of the screen, not its foot
design = logs().filter((m) => m.includes('[VR] design')).pop() ?? '';
check('Short pinch turns the placed piece', /"rot":1/.test(design), design.slice(0, 120));
check('Level ph-1 solved with hands only', /solved true/.test(design));

// 4. Sun handle: grab and move it a little
const as = aim(A.sun);
pose(as.position, as.orientation);
pinch(1); sleep(3);
for (let i = 1; i <= 4; i++) pose(as.position, aim(A.sun.map((v, k) => v + (k === 0 ? 0.08 * i : 0))).orientation);
sleep(2); pinch(0); sleep(3);
const sunLines = logs().filter((m) => m.includes('[VR] sun '));
const g = sunLines.filter((m) => m.includes('grab')).pop(), r = sunLines.filter((m) => m.includes('release')).pop();
const h = (m) => (m ? +m.split(' ').pop() : NaN);
check('Sun handle follows the hand ray', !!g && !!r && Math.abs(h(r) - h(g)) >= 0.5, `hour ${h(g)} -> ${h(r)}`);
steps = logs().filter((m) => m.includes('[VR] step'));
check('Moving the sun moves the tutorial on', /-goal|-done/.test(steps.slice(-1)[0] ?? ''), steps.slice(-1)[0] ?? '');

// 5. Play button starts the day
tap(A.play);
check('Play button press starts the day', logs().some((m) => m.includes('[VR] day start')));

// 6. No uncaught errors
const errs = cli('browser', 'logs').data.result.filter((l) => l.level === 'error').map((l) => l.message).filter((m) => !/ERR_TUNNEL_CONNECTION_FAILED|ERR_ABORTED|Failed to load resource/.test(m)); // sandbox network: CDN hand models are blocked, and the dev server aborts module loads on reload
check('No console errors', errs.length === 0, errs.slice(0, 2).join(' | '));

const failed = results.filter((r) => !r.ok).length;
console.log(failed ? `${failed} check(s) failed` : 'ALL PASS (emulator, hands)');
process.exit(failed ? 1 : 0);
