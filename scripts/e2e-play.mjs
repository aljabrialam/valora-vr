// Emulator end-to-end, hands only: pinch Tiki through the Level 1 tutorial, then swing the screen
// handle to a solving angle. Positions come from the same constants as src/model.ts.
// Requires `npm run dev` (IWSDK dev server with its managed browser).
import {execFileSync} from 'node:child_process';

const S = 1 / 18, DESK = [0, 0.72, -0.56], OFF = [-3.2 * S, 0.001, 1.4 * S];
const world = (p) => [DESK[0] + OFF[0] + p[0] * S, DESK[1] + OFF[1] + p[1] * S, DESK[2] + OFF[2] + p[2] * S];
const handleAt = (deg) => {const a = (deg * Math.PI) / 180, r = 2.2 + 0.9; return world([2.8 + Math.cos(a) * r, 2.6 + 0.55, -0.8 - Math.sin(a) * r]);};
const tiki = [DESK[0] - 0.38, DESK[1] + 0.002 + 0.04, DESK[2] + 0.3];

const cli = (...args) => JSON.parse(execFileSync('npx', ['iwsdk', ...args], {encoding: 'utf8', cwd: process.cwd()}));
// aim the right hand's target ray at `t` from a comfortable hand position in front of the chest
const aim = (t) => {
  const from = [0.16, 1.22, -0.22];
  const d = [t[0] - from[0], t[1] - from[1], t[2] - from[2]];
  const yaw = (Math.atan2(-d[0], -d[2]) * 180) / Math.PI;
  const pitch = (Math.atan2(d[1], Math.hypot(d[0], d[2])) * 180) / Math.PI;
  return {position: from, orientation: {pitch, yaw, roll: 0}};
};
const seq = (steps) => cli('xr', 'run-sequence', '--input-json', JSON.stringify({device: 'hand-right', idleHand: 'rest', body: 'fixed', steps}));

cli('browser', 'reload');
await new Promise((r) => setTimeout(r, 7000));
cli('xr', 'enter');
cli('xr', 'set-input-mode', '--input-json', '{"mode":"hand"}');

// three pinches on Tiki: hello -> watchers -> beam -> swing
for (let i = 0; i < 3; i++) {
  const a = aim(tiki);
  seq([{label: 'aim at Tiki', anchor: 'target-ray', ...a, duration: 0.5}, {label: 'pinch', pinch: 1, duration: 0.4}, {label: 'hold', duration: 1.5}, {label: 'release', pinch: 0, duration: 0.4}, {label: 'wait', duration: 2.5}]);
}
// swing the screen from -90° to 30°
const h0 = handleAt(-90), h1 = handleAt(30);
const a0 = aim(h0);
const delta = h1.map((v, i) => v - h0[i]);
seq([
  {label: 'aim at handle', anchor: 'target-ray', ...a0, duration: 0.6},
  {label: 'pinch', pinch: 1, duration: 0.4}, {label: 'hold', duration: 1.5},
  {label: 'swing', position: a0.position.map((v, i) => v + delta[i]), orientation: a0.orientation, duration: 6},
  {label: 'hold', duration: 2},
  {label: 'release', pinch: 0, duration: 0.2},
]);
const logs = cli('browser', 'logs');
const lines = JSON.stringify(logs).match(/\[VR\] (step|design)[^"]*/g) ?? [];
console.log(lines.slice(-6).join('\n'));
