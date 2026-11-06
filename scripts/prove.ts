// Proof that every level can be solved with the real geometry, and none starts solved.
// Run: npm run prove   (exits non-zero on failure, so CI can gate on it)

import {LEVELS, allDesigns, evaluateLevel} from '../src/sim/levels.ts';

let failed = false;
const lines: string[] = [];

for (const level of LEVELS) {
  const designs = allDesigns(level);
  const solutions = designs.filter((d) => evaluateLevel(level, d).solved);
  const startSolved = evaluateLevel(level, level.start).solved;
  const ok = solutions.length > 0 && !startSolved;
  if (!ok) failed = true;
  const list = solutions.map((d) => `${d.screenDeg}°/${d.overhang} m`).join(', ');
  lines.push(
    `${ok ? 'PASS' : 'FAIL'}  ${level.title.padEnd(16)} ${String(solutions.length).padStart(3)} of ${String(designs.length).padStart(3)} snap positions solve it` +
      `${startSolved ? '  (starts solved!)' : ''}\n      solutions: ${list || 'none'}`,
  );
}

console.log(lines.join('\n'));
process.exit(failed ? 1 : 0);
