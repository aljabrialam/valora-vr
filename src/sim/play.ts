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
import {COUNTRIES, DECL_NOV_8, type Country, type CountryLevel, type CountryRule} from './countries.ts';

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

/** Fixed buildings for the current country: garden walls at its height, plus any extra block. */
export function countryBoxes(): Box[] {
  const c = COUNTRY;
  const out = fixedBoxes().map((b) => {
    if (!b.id.includes('garden wall') || c.wallH === LAYOUT.court.wallH) return b;
    return box(b.id, [b.c[0], c.wallH / 2, b.c[2]], [b.h[0], c.wallH / 2, b.h[2]], b.yaw);
  });
  for (const e of c.extra ?? []) out.push(box(e.id, e.c, e.h));
  return out;
}

export const occluders = (d: Design): Box[] => [...d.pieces.flatMap(pieceBoxes), ...overhangBox(d.overhang), ...countryBoxes()];

// ---------------------------------------------------------------- watchers and targets

export const TARGETS = {
  seat: {at: LAYOUT.seat, name: 'reading chair'},
  plant: {at: LAYOUT.plant, name: 'plant'},
  pool: {at: [-2.95, 0.15, 1.6] as V3, name: 'pool'},
  table: {at: [2.6, 0.8, 2.6] as V3, name: 'garden table'},
  deck: {at: [1.2, 0.8, -2.5] as V3, name: 'deck'},
} as const;
export type Target = keyof typeof TARGETS;

export type Look = {sees: boolean; from: V3; to: V3; blocker: string | null; t: number};

export type Eye = 'window' | 'terrace' | 'tower' | 'boat' | 'moto';

/** Where an eye watcher looks from in the current country (a boat has several positions). */
export function eyePoints(eye: Eye): V3[] {
  return COUNTRY.eyes[eye] ?? [];
}

/** An eye watcher sees the target if it can from any of its positions (a passing boat). */
export function eyeSees(eye: Eye, target: V3, d: Design): Look {
  const boxes = occluders(d).filter((b) => b.id !== 'neighbour house' && !(eye === 'tower' && b.id === 'tower'));
  let first: Look | null = null;
  for (const from of eyePoints(eye)) {
    const hit = firstBlocker(from, target, boxes);
    const look: Look = {sees: !hit, from, to: target, blocker: hit?.box.id ?? null, t: hit ? hit.t : 1};
    if (look.sees) return look;
    first ??= look;
  }
  return first ?? {sees: false, from: target, to: target, blocker: null, t: 0};
}

/** Weather from a fixed direction: wind or rain reaches the target unless something blocks it. */
export function weatherSees(dirTo: V3, target: V3, d: Design): Look {
  const far = 40;
  const from: V3 = [target[0] + dirTo[0] * far, target[1] + dirTo[1] * far, target[2] + dirTo[2] * far];
  const hit = firstBlocker(target, from, occluders(d));
  return {sees: !hit, from, to: target, blocker: hit?.box.id ?? null, t: hit ? 1 - hit.t : 1};
}

/** The sun in the current country at a clock hour. */
export const countrySun = (hour: number) => sunAt(hour, DECL_NOV_8, COUNTRY.solarNoon, COUNTRY.lat);

export function sunSees(target: V3, d: Design, sun: Sun): Look {
  const far = 60;
  const from: V3 = [target[0] + sun.dir[0] * far, target[1] + sun.dir[1] * far, target[2] + sun.dir[2] * far];
  if (sun.el < 2) return {sees: false, from, to: target, blocker: 'horizon', t: 0};
  const hit = firstBlocker(target, from, occluders(d));
  return {sees: !hit, from, to: target, blocker: hit?.box.id ?? null, t: hit ? 1 - hit.t : 1};
}

// ---------------------------------------------------------------- levels

export type Rule = CountryRule;
export type Level = CountryLevel;

/** The country being played; levels, eyes, weather, walls and sun all come from it. */
export let COUNTRY: Country = COUNTRIES[3];
export let LEVELS: Level[] = COUNTRY.levels;
export function setCountry(id: Country['id']) {
  COUNTRY = COUNTRIES.find((c) => c.id === id) ?? COUNTRIES[3];
  LEVELS = COUNTRY.levels;
}
export {COUNTRIES};

// ---------------------------------------------------------------- checking

export type RuleResult = {rule: Rule; look: Look; pass: boolean};

export function evaluate(rule: Rule, d: Design, sun?: Sun): RuleResult {
  const target = TARGETS[rule.target].at;
  const look =
    rule.who === 'sun'
      ? sunSees(target, d, sun ?? countrySun(rule.hour))
      : rule.who === 'wind'
        ? weatherSees(COUNTRY.wind!, target, d)
        : rule.who === 'rain'
          ? weatherSees(COUNTRY.rain!, target, d)
          : eyeSees(rule.who, target, d);
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
