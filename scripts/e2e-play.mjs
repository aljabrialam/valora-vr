// Emulator end-to-end, hands only: pinch Tiki through the Level 1 tutorial, then swing the screen
// handle to a solving angle. Positions come from the same constants as src/model.ts.
// Requires `npm run dev` (IWSDK dev server with its managed browser).
import {execFileSync} from 'node:child_process';

const S = 1 / 18, DESK = [0, 0.75, -0.56], OFF = [-3.2 * S, 0.001, 1.4 * S];
const world = (p) => [DESK[0] + OFF[0] + p[0] * S, DESK[1] + OFF[1] + p[1] * S, DESK[2] + OFF[2] + p[2] * S];
const handleAt = (deg) => {const a = (deg * Math.PI) / 180, r = 2.2 + 0.9; return world([2.8 + Math.cos(a) * r, 2.6 + 0.55, -0.8 - Math.sin(a) * r]);};
const tiki = [DESK[0] - 0.38, DESK[1] + 0.002 + 0.04, DESK[2] + 0.3];

const run = (args) => JSON.parse(execFileSync('npx', ['iwsdk', ...args], {encoding: 'utf8', cwd: process.cwd()}));
// The managed browser can relaunch under software GL; the CLI then reports browser_relaunched and
// asks for a fresh command, so retry once (the relaunched page has already loaded the app).
const cli = (...args) => {
  try { return run(args); } catch (e) {
    if (!/browser_relaunched/.test(String(e.stderr ?? e))) throw e;
    execFileSync('sleep', ['20']);
    return run(args);
  }
};
// aim the right hand's target ray at `t` from a comfortable hand position in front of the chest
const aim = (t) => {
  const from = [0.16, 1.22, -0.22];
  const d = [t[0] - from[0], t[1] - from[1], t[2] - from[2]];
  const yaw = (Math.atan2(-d[0], -d[2]) * 180) / Math.PI;
  const pitch = (Math.atan2(d[1], Math.hypot(d[0], d[2])) * 180) / Math.PI;
  return {position: from, orientation: {pitch, yaw, roll: 0}};
};
// Each emulator command must finish inside the dev server's 27 s command limit, and software GL
// runs the emulator far slower than real time. So poses are set with short sequences, the pinch is
// held with set-select-value, and waits happen here in wall-clock time.
const pose = (position, orientation) => cli('xr', 'run-sequence', '--input-json', JSON.stringify({device: 'hand-right', idleHand: 'rest', body: 'fixed', steps: [{label: 'pose', anchor: 'target-ray', position, orientation, duration: 0.3}]}));
const pinch = (v) => cli('xr', 'set-select-value', '--input-json', JSON.stringify({device: 'hand-right', value: v}));
const sleep = (s) => execFileSync('sleep', [String(s)]);

cli('browser', 'reload');
sleep(25); // the baked house and HDRI take a while under software GL
cli('xr', 'enter');
cli('xr', 'set-input-mode', '--input-json', '{"mode":"hand"}');
pinch(0);

// three pinches on Tiki: hello -> watchers -> beam -> swing
for (let i = 0; i < 3; i++) {
  const a = aim(tiki);
  pose(a.position, a.orientation);
  pinch(1); sleep(3);
  pinch(0); sleep(4);
}
// swing the screen from -90 to 30 degrees: pinch the handle, then carry the hand along the arc
const a0 = aim(handleAt(-90));
pose(a0.position, a0.orientation);
pinch(1); sleep(4);
const h0 = handleAt(-90);
for (let deg = -80; deg <= 30; deg += 10) {
  const h = handleAt(deg);
  pose(a0.position.map((v, i) => v + h[i] - h0[i]), a0.orientation);
}
sleep(6);
pinch(0); sleep(3);
const lines = cli('browser', 'logs').data.result.map((l) => l.message).filter((m) => /\[VR\] (step|design)/.test(m));
console.log(lines.slice(-6).join('\n'));
const ok = lines.some((m) => m.includes('[VR] step l1-done'));
console.log(ok ? 'PASS: Tiki tutorial and screen swing solved Level 1 with hands only' : 'FAIL: Level 1 not solved');
process.exit(ok ? 0 : 1);
