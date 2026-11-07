// VaLora: Two Watchers, puzzle engine v2.
// The player places a few pieces from a tray onto sockets in the courtyard (privacy screen, tree,
// pergola, hedge) and may slide out the roof overhang. Watchers look at the house: the sun at
// given hours, the neighbour from his window, and the neighbour from his roof terrace. Each level
// asks for some views to be blocked and some to stay open. Everything here is plain geometry so
// the checks are exact and `scripts/prove.ts` can enumerate every layout.
//
// Site metres: +x east, -z north, +y up. The room is north of the courtyard; the neighbour's
// house is east of it.

import {box, firstBlocker, type Box, type V3} from './geom.ts';
import {sunAt, type Sun} from './sun.ts';
import {fixedBoxes, LAYOUT} from './world.ts';

const D = Math.PI / 180;

// ---------------------------------------------------------------- pieces

export type Kind = 'screen' | 'tree' | 'pergola' | 'hedge';

/** What each piece is, in words the player sees, and the boxes the watchers test against. */
export const PIECES: Record<Kind, {name: string; what: string; rots: number}> = {
  screen: {name: 'Screen', what: 'A tall timber screen. Blocks eyes and low sun.', rots: 4},
  tree: {name: 'Tree', what: 'A canopy high up. Blocks high sun and views from above, not eye level.', rots: 1},
  pergola: {name: 'Pergola', what: 'A slatted roof on posts. Shade from the midday sun.', rots: 1},
  hedge: {name: 'Hedge', what: 'Waist-high planting. Blocks only low views.', rots: 2},
};

export type Placed = {kind: Kind; socket: number; rot: number};
export type Design = {pieces: Placed[]; overhang: number};

/**
 * Sockets: a grid over the courtyard, skipping the pool and the plant. A piece stands centred on
 * its socket.
 */
export const SOCKETS: V3[] = (() => {
  const out: V3[] = [];
  const pool = {x0: -4.3, x1: -1.6, z0: 0.3, z1: 2.9};
  const plant = LAYOUT.plant;
  for (const z of [-2.2, -0.8, 0.6, 2.0, 3.3])
    for (const x of [-3.75, -2.25, -0.75, 0.75, 2.25, 3.75]) {
      const inPool = x > pool.x0 - 0.4 && x < pool.x1 + 0.4 && z > pool.z0 - 0.4 && z < pool.z1 + 0.4;
      const onPlant = Math.hypot(x - plant[0], z - plant[2]) < 0.9;
      const onScreenHinge = Math.hypot(x - LAYOUT.screen.pivot[0], z - LAYOUT.screen.pivot[2]) < 0.5;
      if (!inPool && !onPlant && !onScreenHinge) out.push([x, 0, z]);
    }
  return out;
})();

/** The boxes one placed piece adds. */
export function pieceBoxes(p: Placed): Box[] {
  const [x, , z] = SOCKETS[p.socket];
  const id = `${p.kind}@${p.socket}`;
  switch (p.kind) {
    case 'screen': {
      const a = p.rot * 45 * D;
      return [box(id, [x, 1.3, z], [1.0, 1.3, 0.05], a)];
    }
    case 'hedge': {
      const a = p.rot * 90 * D;
      return [box(id, [x, 0.6, z], [1.2, 0.6, 0.35], a)];
    }
    case 'tree':
      // the trunk is too thin to matter; the canopy is a broad, high crown
      return [box(id, [x, 3.2, z], [1.25, 1.0, 1.25])];
    case 'pergola':
      // slats are close enough to read as solid shade at this scale
      return [box(id, [x, 2.55, z], [1.3, 0.08, 1.3])];
  }
}

export function overhangBox(depth: number): Box[] {
  const r = LAYOUT.room;
  if (depth < 0.01) return [];
  return [box('overhang', [(r.x0 + r.x1) / 2, r.h + 0.08, r.z1 + depth / 2], [(r.x1 - r.x0) / 2 + 0.2, 0.08, depth / 2])];
}

export const occluders = (d: Design): Box[] => [...d.pieces.flatMap(pieceBoxes), ...overhangBox(d.overhang), ...fixedBoxes()];

// ---------------------------------------------------------------- watchers and targets

export const TARGETS = {
  seat: {at: LAYOUT.seat, name: 'reading chair'},
  plant: {at: LAYOUT.plant, name: 'plant'},
  pool: {at: [-2.95, 0.15, 1.6] as V3, name: 'pool'},
  table: {at: [2.6, 0.8, 2.6] as V3, name: 'garden table'},
} as const;
export type Target = keyof typeof TARGETS;

export const EYES = {
  window: {at: LAYOUT.neighbour.window, name: 'the neighbour at his window'},
  terrace: {at: [9.4, 6.0, 0.4] as V3, name: 'the neighbour on his roof terrace'},
} as const;
export type Eye = keyof typeof EYES;

export type Look = {sees: boolean; from: V3; to: V3; blocker: string | null; t: number};

export function eyeSees(eye: Eye, target: V3, d: Design): Look {
  const from = EYES[eye].at;
  const hit = firstBlocker(from, target, occluders(d).filter((b) => b.id !== 'neighbour house'));
  return {sees: !hit, from, to: target, blocker: hit?.box.id ?? null, t: hit ? hit.t : 1};
}

export function sunSees(target: V3, d: Design, sun: Sun): Look {
  const far = 60;
  const from: V3 = [target[0] + sun.dir[0] * far, target[1] + sun.dir[1] * far, target[2] + sun.dir[2] * far];
  if (sun.el < 2) return {sees: false, from, to: target, blocker: 'horizon', t: 0};
  const hit = firstBlocker(target, from, occluders(d));
  return {sees: !hit, from, to: target, blocker: hit?.box.id ?? null, t: hit ? 1 - hit.t : 1};
}

// ---------------------------------------------------------------- levels

export type Rule = {
  id: string;
  who: 'sun' | Eye;
  target: Target;
  want: 'sees' | 'blind';
  hour?: number; // the sun's hour; also when the moment plays in "live the day"
  text: string;
};

export type Level = {
  id: string;
  title: string;
  brief: string;
  tray: Partial<Record<Kind, number>>; // pieces available and how many of each
  overhang: boolean;
  par: number; // pieces for three stars
  rules: Rule[];
};

const R = {
  private: {id: 'private', who: 'window', target: 'seat', want: 'blind', hour: 9.5, text: 'The neighbour cannot see you reading'} as Rule,
  plantAm: {id: 'plant-am', who: 'sun', target: 'plant', want: 'sees', hour: 8.5, text: 'Morning sun on the plant at 8:30'} as Rule,
  seatPm: {id: 'seat-pm', who: 'sun', target: 'seat', want: 'blind', hour: 15.5, text: 'Shade on the reading chair at 3:30'} as Rule,
  lunch: {id: 'lunch', who: 'sun', target: 'table', want: 'blind', hour: 12.5, text: 'Shade on the garden table at lunch'} as Rule,
  lunchPrivate: {id: 'lunch-private', who: 'window', target: 'table', want: 'blind', hour: 12.5, text: 'Lunch out of the neighbour’s sight'} as Rule,
  swimSun: {id: 'swim-sun', who: 'sun', target: 'pool', want: 'sees', hour: 11, text: 'Sun on the pool for an 11:00 swim'} as Rule,
  swimPrivate: {id: 'swim-private', who: 'terrace', target: 'pool', want: 'blind', hour: 11, text: 'Swim unseen from the roof terrace'} as Rule,
};

export const LEVELS: Level[] = [
  {
    id: 'neighbour',
    title: 'The Neighbour',
    brief: 'He can see straight into your reading chair. Place a screen to block his view.',
    tray: {screen: 1},
    overhang: false,
    par: 1,
    rules: [R.private],
  },
  {
    id: 'morning',
    title: 'Morning Light',
    brief: 'Stay private, but the plant needs the morning sun from the east. A screen in the wrong place steals it.',
    tray: {screen: 2, hedge: 1},
    overhang: false,
    par: 1,
    rules: [R.private, R.plantAm],
  },
  {
    id: 'lunch',
    title: 'Lunch Outside',
    brief: 'Midday sun is almost overhead. Shade the garden table, and keep lunch private.',
    tray: {tree: 1, pergola: 1, hedge: 1},
    overhang: false,
    par: 1,
    rules: [R.lunch, R.lunchPrivate],
  },
  {
    id: 'swim',
    title: 'Morning Swim',
    brief: 'The neighbour likes his roof terrace. Hide the pool from above, but keep it sunny.',
    tray: {tree: 2, pergola: 1, hedge: 1},
    overhang: false,
    par: 1,
    rules: [R.swimPrivate, R.swimSun],
  },
  {
    id: 'afternoon',
    title: 'Afternoon Read',
    brief: 'Afternoon sun comes low from the west. Shade your chair without losing the morning light or your privacy.',
    tray: {screen: 1, tree: 2},
    overhang: true,
    par: 1,
    rules: [R.private, R.plantAm, R.seatPm],
  },
  {
    id: 'day',
    title: 'The Whole Day',
    brief: 'Morning plant, a private swim, shaded lunch, an afternoon read. Plan the whole day.',
    tray: {screen: 2, tree: 2, pergola: 1, hedge: 1},
    overhang: true,
    par: 2,
    rules: [R.plantAm, R.swimSun, R.swimPrivate, R.lunch, R.private, R.seatPm],
  },
];

// ---------------------------------------------------------------- checking

export type RuleResult = {rule: Rule; look: Look; pass: boolean};

export function evaluate(rule: Rule, d: Design, sun?: Sun): RuleResult {
  const target = TARGETS[rule.target].at;
  const look = rule.who === 'sun' ? sunSees(target, d, sun ?? sunAt(rule.hour ?? 12)) : eyeSees(rule.who, target, d);
  return {rule, look, pass: rule.want === 'sees' ? look.sees : !look.sees};
}

export function evaluateLevel(level: Level, d: Design) {
  const results = level.rules.map((r) => evaluate(r, d));
  const solved = results.every((r) => r.pass);
  return {results, solved, stars: solved ? starsFor(level, d.pieces.length) : 0};
}

export function starsFor(level: Level, used: number): number {
  return used <= level.par ? 3 : used <= level.par + 1 ? 2 : 1;
}

/** Every distinct placement of one piece of a kind. */
export function placements(kind: Kind): Placed[] {
  const out: Placed[] = [];
  for (let s = 0; s < SOCKETS.length; s++) for (let r = 0; r < PIECES[kind].rots; r++) out.push({kind, socket: s, rot: r});
  return out;
}
