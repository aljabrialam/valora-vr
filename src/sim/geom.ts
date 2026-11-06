// Pure geometry for the watcher checks. No three.js here so the same code runs in the
// headset and in Node for the solvability proof (npm run prove).

export type V3 = [number, number, number];

/** An oriented box: centre, half sizes, and a rotation about the vertical axis (radians). */
export type Box = {
  id: string;
  c: V3;
  h: V3;
  yaw: number;
};

export const box = (id: string, c: V3, h: V3, yaw = 0): Box => ({id, c, h, yaw});

/**
 * Does the straight segment from p to q pass through the box?
 * Slab test in the box's own frame. `eps` trims both ends so a target sitting on a
 * surface does not count as blocking itself.
 */
export function segmentHitsBox(p: V3, q: V3, b: Box, eps = 1e-4): boolean {
  return segmentEntry(p, q, b, eps) >= 0;
}

/** Where along p→q (0..1) the segment first enters the box, or -1 if it misses. */
export function segmentEntry(p: V3, q: V3, b: Box, eps = 1e-4): number {
  const cy = Math.cos(-b.yaw);
  const sy = Math.sin(-b.yaw);
  const toLocal = (v: V3): V3 => {
    const x = v[0] - b.c[0];
    const y = v[1] - b.c[1];
    const z = v[2] - b.c[2];
    return [x * cy + z * sy, y, -x * sy + z * cy];
  };
  const a = toLocal(p);
  const e = toLocal(q);
  let t0 = eps;
  let t1 = 1 - eps;
  for (let i = 0; i < 3; i++) {
    const d = e[i] - a[i];
    if (Math.abs(d) < 1e-12) {
      if (a[i] < -b.h[i] || a[i] > b.h[i]) return -1;
      continue;
    }
    let tn = (-b.h[i] - a[i]) / d;
    let tf = (b.h[i] - a[i]) / d;
    if (tn > tf) [tn, tf] = [tf, tn];
    t0 = Math.max(t0, tn);
    t1 = Math.min(t1, tf);
    if (t0 > t1) return -1;
  }
  return t0;
}

/** The first box the segment passes through, or null when the view is clear. */
export function firstBlocker(p: V3, q: V3, boxes: Box[]): {box: Box; t: number} | null {
  let best: {box: Box; t: number} | null = null;
  for (const b of boxes) {
    const t = segmentEntry(p, q, b);
    if (t >= 0 && (!best || t < best.t)) best = {box: b, t};
  }
  return best;
}
