// The three authored levels. Each rule is a question one watcher answers.
// `scripts/prove.ts` enumerates every snap position and proves each level is solvable
// and does not start solved.

import {LAYOUT, neighbourSees, screenAngles, sunAt, sunSees, type Design, type Look} from './world.ts';
import type {V3} from './geom.ts';

export type Watcher = 'sun' | 'neighbour';

export type Rule = {
  id: string;
  watcher: Watcher;
  target: 'seat' | 'plant';
  want: 'sees' | 'blind'; // what we want the watcher to experience
  hour?: number; // for the sun
  text: string; // shown to the player
};

export type Level = {
  id: string;
  title: string;
  brief: string;
  rules: Rule[];
  tools: Array<'screen' | 'overhang' | 'sun'>;
  start: Design;
};

export const TARGETS: Record<Rule['target'], V3> = {seat: LAYOUT.seat, plant: LAYOUT.plant};

export const LEVELS: Level[] = [
  {
    id: 'neighbour',
    title: 'The Neighbour',
    brief: 'Someone next door can see straight into the reading chair. Swing the screen to block their view.',
    tools: ['screen'],
    start: {screenDeg: -90, overhang: 0},
    rules: [{id: 'private', watcher: 'neighbour', target: 'seat', want: 'blind', text: 'Neighbour cannot see the seat'}],
  },
  {
    id: 'garden',
    title: 'Morning Garden',
    brief: 'Keep the seat private, but the plant needs the morning sun. Swing too far and you steal its light.',
    tools: ['screen', 'sun'],
    start: {screenDeg: 60, overhang: 0},
    rules: [
      {id: 'private', watcher: 'neighbour', target: 'seat', want: 'blind', text: 'Neighbour cannot see the seat'},
      {id: 'plant-am', watcher: 'sun', target: 'plant', want: 'sees', hour: 8.5, text: 'Sun reaches the plant at 8:30 a.m.'},
    ],
  },
  {
    id: 'day',
    title: 'The Whole Day',
    brief: 'Privacy, morning sun for the plant, and shade on the reading chair in the afternoon. Use the roof overhang too.',
    tools: ['screen', 'overhang', 'sun'],
    start: {screenDeg: 60, overhang: 0},
    rules: [
      {id: 'private', watcher: 'neighbour', target: 'seat', want: 'blind', text: 'Neighbour cannot see the seat'},
      {id: 'plant-am', watcher: 'sun', target: 'plant', want: 'sees', hour: 8.5, text: 'Sun reaches the plant at 8:30 a.m.'},
      {id: 'seat-pm', watcher: 'sun', target: 'seat', want: 'blind', hour: 15.5, text: 'Seat in shade at 3:30 p.m.'},
    ],
  },
];

export type RuleResult = {rule: Rule; look: Look; pass: boolean};

export function evaluate(rule: Rule, d: Design): RuleResult {
  const target = TARGETS[rule.target];
  const look = rule.watcher === 'neighbour' ? neighbourSees(target, d) : sunSees(target, d, sunAt(rule.hour ?? 12));
  const pass = rule.want === 'sees' ? look.sees : !look.sees;
  return {rule, look, pass};
}

export function evaluateLevel(level: Level, d: Design): {results: RuleResult[]; solved: boolean} {
  const results = level.rules.map((r) => evaluate(r, d));
  return {results, solved: results.every((r) => r.pass)};
}

/** Every snap position the player can reach with the tools a level gives them. */
export function allDesigns(level: Level): Design[] {
  const {overhang: o} = LAYOUT;
  const angles = screenAngles();
  const depths: number[] = [];
  if (level.tools.includes('overhang')) for (let v = o.min; v <= o.max + 1e-9; v += o.step) depths.push(+v.toFixed(2));
  else depths.push(level.start.overhang);
  const out: Design[] = [];
  for (const screenDeg of level.tools.includes('screen') ? angles : [level.start.screenDeg])
    for (const overhang of depths) out.push({screenDeg, overhang});
  return out;
}
