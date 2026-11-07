// Proves every v2 level is solvable, does not start solved, and that its par (pieces for three
// stars) is the true minimum. Exact search up to 3 pieces; seeded random search beyond that.
//   node scripts/prove2.ts
import {evaluateLevel, LEVELS, PIECES, placements, type Design, type Kind, type Level, type Placed} from '../src/sim/play.ts';

function candidates(level: Level): Placed[] {
  return (Object.keys(level.tray) as Kind[]).flatMap((k) => placements(k));
}

function fits(level: Level, ps: Placed[]): boolean {
  const used = new Set<number>();
  const count: Partial<Record<Kind, number>> = {};
  for (const p of ps) {
    if (used.has(p.socket)) return false;
    used.add(p.socket);
    count[p.kind] = (count[p.kind] ?? 0) + 1;
    if (count[p.kind]! > (level.tray[p.kind] ?? 0)) return false;
  }
  return true;
}

const depths = (level: Level) => (level.overhang ? [0, 0.6, 1.2, 1.8, 2.4] : [0]);

function solve(level: Level, k: number, limit = 3): Design[] {
  const c = candidates(level);
  const found: Design[] = [];
  const pick = (start: number, chosen: Placed[]) => {
    if (found.length >= limit) return;
    if (chosen.length === k) {
      if (!fits(level, chosen)) return;
      for (const overhang of depths(level)) {
        const d = {pieces: chosen.slice(), overhang};
        if (evaluateLevel(level, d).solved) {
          found.push(d);
          return;
        }
      }
      return;
    }
    for (let i = start; i < c.length; i++) {
      chosen.push(c[i]);
      pick(i + 1, chosen);
      chosen.pop();
      if (found.length >= limit) return;
    }
  };
  pick(0, []);
  return found;
}

function randomSolve(level: Level, k: number, tries: number): Design | null {
  const c = candidates(level);
  let seed = 42;
  const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  for (let t = 0; t < tries; t++) {
    const ps: Placed[] = [];
    while (ps.length < k) ps.push(c[Math.floor(rnd() * c.length)]);
    if (!fits(level, ps)) continue;
    for (const overhang of depths(level)) {
      const d = {pieces: ps, overhang};
      if (evaluateLevel(level, d).solved) return d;
    }
  }
  return null;
}

const show = (d: Design) => d.pieces.map((p) => `${PIECES[p.kind].name}@${p.socket}${PIECES[p.kind].rots > 1 ? `/${p.rot * (p.kind === 'hedge' ? 90 : 45)}°` : ''}`).join(' + ') + (d.overhang ? ` + overhang ${d.overhang} m` : '');

let ok = true;
for (const level of LEVELS) {
  const empty = solve(level, 0, 1);
  let min = -1;
  let example: Design | null = null;
  for (let k = 1; k <= 3; k++) {
    const s = solve(level, k, 1);
    if (s.length) {
      min = k;
      example = s[0];
      break;
    }
  }
  if (min < 0) {
    for (let k = 4; k <= 5 && min < 0; k++) {
      const s = randomSolve(level, k, 400000);
      if (s) {
        min = k;
        example = s;
      }
    }
  }
  const good = !empty.length && min > 0 && min === level.par;
  if (!good) ok = false;
  console.log(`${good ? 'PASS' : 'FAIL'}  ${level.title.padEnd(16)} starts solved: ${empty.length ? 'YES' : 'no'}   fewest pieces: ${min < 0 ? 'none found' : min}   par: ${level.par}`);
  if (example) console.log(`      e.g. ${show(example)}`);
  if (min > 0 && min <= 2) {
    const all = solve(level, min, 1e9).length;
    const total = candidates(level).length;
    console.log(`      ${all} winning layouts with ${min} piece(s), out of about ${min === 1 ? total * depths(level).length : (total * total / 2) * depths(level).length} tries`);
  }
}
process.exit(ok ? 0 : 1);
