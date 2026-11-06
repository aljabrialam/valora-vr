// The courtyard scene in real metres, and the two watchers.
// Everything the player can change lives in `Design`; everything the checks read is
// rebuilt from it by `occluders()`. The rendered model is built from the same numbers.

import {box, firstBlocker, type Box, type V3} from './geom.ts';
import {sunAt, type Sun} from './sun.ts';

const D = Math.PI / 180;

/** The choices the player makes with their hands. */
export type Design = {
  screenDeg: number; // privacy screen swing, degrees; 0 points east, 90 points north
  overhang: number; // roof overhang depth beyond the courtyard glass, metres
};

export const LAYOUT = {
  room: {x0: -5, x1: 5, z0: -7, z1: -3, h: 3.0, slab: 0.3},
  court: {x0: -5, x1: 5, z0: -3, z1: 4, wallH: 2.2, wallT: 0.2},
  screen: {pivot: [2.8, 0, -0.8] as V3, len: 2.2, h: 2.6, t: 0.08},
  overhang: {min: 0, max: 2.4, step: 0.6},
  screenSteps: {min: -165, max: 180, step: 15},
  neighbour: {window: [8.5, 3.6, 1.5] as V3, house: {x0: 7.8, x1: 12, z0: -4, z1: 2.4, h: 4.6}},
  seat: [1.6, 1.05, -3.5] as V3, // eye of someone sitting in the reading chair
  plant: [-1.5, 0.55, -2.4] as V3, // top of the courtyard plant
};

/** Angles the screen can actually swing to: its free end must stay inside the courtyard. */
export function screenFits(deg: number): boolean {
  const {screen: s, court: c} = LAYOUT;
  const a = (deg * Math.PI) / 180;
  const x = s.pivot[0] + Math.cos(a) * s.len;
  const z = s.pivot[2] - Math.sin(a) * s.len;
  const m = 0.25;
  return x > c.x0 + m && x < c.x1 - m && z > c.z0 + m && z < c.z1 - m;
}

export function screenAngles(): number[] {
  const {min, max, step} = LAYOUT.screenSteps;
  const out: number[] = [];
  for (let a = min; a <= max; a += step) if (screenFits(a)) out.push(a);
  return out;
}

export const START: Design = {screenDeg: 0, overhang: 0};

/** Fixed walls and roofs that never move. */
export function fixedBoxes(): Box[] {
  const {room: r, court: c, neighbour: n} = LAYOUT;
  const midX = (r.x0 + r.x1) / 2;
  const halfX = (r.x1 - r.x0) / 2;
  return [
    box('roof', [midX, r.h + r.slab / 2, (r.z0 + r.z1) / 2], [halfX + 0.2, r.slab / 2, (r.z1 - r.z0) / 2 + 0.1]),
    box('north wall', [midX, r.h / 2, r.z0], [halfX, r.h / 2, 0.15]),
    box('west wall', [r.x0, r.h / 2, (r.z0 + r.z1) / 2], [0.15, r.h / 2, (r.z1 - r.z0) / 2]),
    box('east wall', [r.x1, r.h / 2, (r.z0 + r.z1) / 2], [0.15, r.h / 2, (r.z1 - r.z0) / 2]),
    box('east garden wall', [c.x1 + c.wallT / 2, c.wallH / 2, (c.z0 + c.z1) / 2], [c.wallT / 2, c.wallH / 2, (c.z1 - c.z0) / 2]),
    box('south garden wall', [midX, c.wallH / 2, c.z1 + c.wallT / 2], [halfX, c.wallH / 2, c.wallT / 2]),
    box('west garden wall', [c.x0 - c.wallT / 2, c.wallH / 2, (c.z0 + c.z1) / 2], [c.wallT / 2, c.wallH / 2, (c.z1 - c.z0) / 2]),
    // the neighbour's house, minus the window they look out of (the window sits on its west face)
    box('neighbour house', [(n.house.x0 + n.house.x1) / 2 + 0.3, n.house.h / 2, (n.house.z0 + n.house.z1) / 2], [(n.house.x1 - n.house.x0) / 2, n.house.h / 2, (n.house.z1 - n.house.z0) / 2]),
  ];
}

/** The two pieces the player moves. */
export function movingBoxes(d: Design): Box[] {
  const {screen: s, room: r} = LAYOUT;
  const a = d.screenDeg * D;
  const dir: V3 = [Math.cos(a), 0, -Math.sin(a)];
  const out: Box[] = [
    box('privacy screen', [s.pivot[0] + (dir[0] * s.len) / 2, s.h / 2, s.pivot[2] + (dir[2] * s.len) / 2], [s.len / 2, s.h / 2, s.t / 2], a),
  ];
  if (d.overhang > 0.01) {
    out.push(box('overhang', [(r.x0 + r.x1) / 2, r.h + 0.08, r.z1 + d.overhang / 2], [(r.x1 - r.x0) / 2 + 0.2, 0.08, d.overhang / 2]));
  }
  return out;
}

export const occluders = (d: Design): Box[] => [...movingBoxes(d), ...fixedBoxes()];

export type Look = {
  sees: boolean;
  from: V3;
  to: V3;
  blocker: string | null; // what stopped the view, for the explanation text
  t: number; // where along from→to the view stops (1 when clear)
};

/** Can the neighbour see the target? */
export function neighbourSees(target: V3, d: Design): Look {
  const from = LAYOUT.neighbour.window;
  const hit = firstBlocker(from, target, occluders(d).filter((b) => b.id !== 'neighbour house'));
  return {sees: !hit, from, to: target, blocker: hit?.box.id ?? null, t: hit ? hit.t : 1};
}

/** Can the sun see the target? A sun that is below 2° counts as not seeing anything. */
export function sunSees(target: V3, d: Design, sun: Sun): Look {
  const far = 60;
  const from: V3 = [target[0] + sun.dir[0] * far, target[1] + sun.dir[1] * far, target[2] + sun.dir[2] * far];
  if (sun.el < 2) return {sees: false, from, to: target, blocker: 'horizon', t: 0};
  // the sun's view is traced from the target outwards; t is turned round so 0 is the sun's end
  const hit = firstBlocker(target, from, occluders(d));
  return {sees: !hit, from, to: target, blocker: hit?.box.id ?? null, t: hit ? 1 - hit.t : 1};
}

export {sunAt};
