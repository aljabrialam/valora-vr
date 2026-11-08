// The local watchers made visible, in site metres: a high-rise block with a figure on a balcony
// (Singapore), condo towers (Kuala Lumpur), motorbikes in the lane (Hanoi), long-tail boats passing on the sea (Thailand), wind streaks blowing in (Philippines),
// slanting rain (Indonesia), and the sea itself around the island. The checks are in
// src/sim/play.ts; this only draws them.

import {
  BoxGeometry,
  BufferGeometry,
  CircleGeometry,
  Color,
  CylinderGeometry,
  Float32BufferAttribute,
  Group,
  LineBasicMaterial,
  LineSegments,
  Mesh,
  MeshPhysicalMaterial,
  MeshStandardMaterial,
  type Object3D,
  SphereGeometry,
} from '@iwsdk/core';
import {scaleFigure} from './pieces.ts';
import type {Country} from './sim/countries.ts';
import type {V3} from './sim/geom.ts';

const SEA_Y = -0.9;

function std(color: string, rough = 0.8) {
  return new MeshStandardMaterial({color, roughness: rough});
}

/** Shallow turquoise water around the island, darker further out, with a gentle swell. */
function sea(): Mesh {
  const m = new MeshPhysicalMaterial({color: '#39b9c6', roughness: 0.12, clearcoat: 1, clearcoatRoughness: 0.08, transparent: true, opacity: 0.9});
  const g = new CircleGeometry(30, 96);
  g.rotateX(-Math.PI / 2);
  // vertex colours: pale turquoise near the island, deep teal at the edge
  const pos = g.attributes.position;
  const col: number[] = [];
  const near = new Color('#6fe0dc');
  const far = new Color('#1f7f95');
  for (let i = 0; i < pos.count; i++) {
    const d = Math.hypot(pos.getX(i) - 3.2, pos.getZ(i) + 1.4);
    const c = near.clone().lerp(far, Math.min(1, Math.max(0, (d - 9) / 14)));
    col.push(c.r, c.g, c.b);
  }
  g.setAttribute('color', new Float32BufferAttribute(col, 3));
  m.vertexColors = true;
  const mesh = new Mesh(g, m);
  mesh.position.set(3.2, SEA_Y, -1.4);
  mesh.receiveShadow = true;
  mesh.raycast = () => {};
  return mesh;
}

/** A tower block that faces the house: a Singapore point block (white, orange crown) or a Kuala
 *  Lumpur condo (glass, balcony bands). The figure stands on a balcony at the watcher's eye. */
function tower(c: V3, h: V3, eye: V3 | null, style: 'sg' | 'my'): Group {
  const g = new Group();
  const face = c[0] > 0 ? -1 : 1; // the side that looks at the house
  const body = new Mesh(new BoxGeometry(h[0] * 2, h[1] * 2, h[2] * 2), style === 'my' ? std('#e8e2d6', 0.4) : std('#f1ece2'));
  body.position.set(c[0], c[1], c[2]);
  body.castShadow = body.receiveShadow = true;
  g.add(body);
  const win = style === 'my' ? std('#3f7f95', 0.15) : std('#5c7d8f', 0.3);
  const ledge = std(style === 'my' ? '#f4f1ea' : '#f1ece2');
  for (let y = 1.2; y < h[1] * 2 - 0.5; y += style === 'my' ? 1.1 : 1.5) {
    const strip = new Mesh(new BoxGeometry(0.05, style === 'my' ? 0.62 : 0.55, h[2] * 1.7), win);
    strip.position.set(c[0] + face * (h[0] + 0.01), y, c[2]);
    g.add(strip);
    // the south face, towards the player, has windows too
    const south = new Mesh(new BoxGeometry(h[0] * 1.7, style === 'my' ? 0.62 : 0.55, 0.05), win);
    south.position.set(c[0], y, c[2] + h[2] + 0.01);
    g.add(south);
    if (style === 'my') {
      const band = new Mesh(new BoxGeometry(0.34, 0.07, h[2] * 2.05), ledge);
      band.position.set(c[0] + face * (h[0] + 0.15), y - 0.4, c[2]);
      const sband = new Mesh(new BoxGeometry(h[0] * 2.05, 0.07, 0.3), ledge);
      sband.position.set(c[0], y - 0.4, c[2] + h[2] + 0.13);
      g.add(band, sband);
    }
  }
  const top = new Mesh(new BoxGeometry(h[0] * 2 + 0.2, 0.4, h[2] * 2 + 0.2), std(style === 'my' ? '#2f6b7a' : '#d98a3b'));
  top.position.set(c[0], h[1] * 2 + 0.2, c[2]);
  g.add(top);
  if (eye) {
    const balcony = new Mesh(new BoxGeometry(0.9, 0.12, 1.6), ledge);
    balcony.position.set(eye[0] + face * 0.1, eye[1] - 1.62, eye[2]);
    g.add(balcony);
    const fig = scaleFigure(true);
    fig.position.set(eye[0], eye[1] - 1.56, eye[2]);
    fig.rotation.y = (face * Math.PI) / 2;
    fig.name = 'watcher';
    g.add(fig);
  }
  return g;
}

/** A motorbike with a helmeted rider, for the Hanoi lane. Faces +x. */
function moto(paint: string, helmet: string): Group {
  const g = new Group();
  const tyre = std('#2b2b2e', 0.9);
  for (const x of [-0.55, 0.55]) {
    const w = new Mesh(new CylinderGeometry(0.26, 0.26, 0.12, 18), tyre);
    w.rotation.x = Math.PI / 2;
    w.position.set(x, 0.26, 0);
    g.add(w);
  }
  const body = new Mesh(new BoxGeometry(1.0, 0.32, 0.36), std(paint, 0.45));
  body.position.set(0, 0.6, 0);
  const shield = new Mesh(new BoxGeometry(0.12, 0.62, 0.42), std(paint, 0.45));
  shield.position.set(0.5, 0.78, 0);
  shield.rotation.z = -0.25;
  const bars = new Mesh(new CylinderGeometry(0.025, 0.025, 0.6, 6), tyre);
  bars.rotation.x = Math.PI / 2;
  bars.position.set(0.48, 1.12, 0);
  const rider = scaleFigure(true);
  rider.position.set(-0.05, 0.1, 0);
  rider.rotation.y = -Math.PI / 2;
  rider.name = 'watcher';
  const hat = new Mesh(new SphereGeometry(0.235, 16, 10, 0, Math.PI * 2, 0, Math.PI / 2), std(helmet, 0.35));
  hat.position.y = 1.58;
  rider.add(hat);
  g.add(body, shield, bars, rider);
  for (const o of g.children) o.castShadow = true;
  return g;
}

/** A long-tail boat with a passenger standing to look. */
function boat(): Group {
  const g = new Group();
  const hull = new Mesh(new CylinderGeometry(0.45, 0.25, 4.2, 10, 1), std('#b0542f', 0.6));
  hull.rotation.z = Math.PI / 2;
  hull.scale.set(1, 1, 0.55);
  hull.position.y = 0.25;
  const trim = new Mesh(new BoxGeometry(4.0, 0.08, 0.6), std('#f2c14e', 0.5));
  trim.position.y = 0.55;
  const canopy = new Mesh(new BoxGeometry(1.6, 0.06, 0.8), std('#2f8fd6', 0.7));
  canopy.position.set(-0.6, 2.0, 0);
  const pole = new Mesh(new CylinderGeometry(0.03, 0.03, 1.5, 6), std('#6b4a2e'));
  pole.position.set(-0.6, 1.25, 0);
  const fig = scaleFigure(true);
  fig.position.set(0.6, 0.5, 0);
  fig.rotation.y = -Math.PI / 2;
  fig.name = 'watcher';
  g.add(hull, trim, canopy, pole, fig);
  for (const o of g.children) o.castShadow = true;
  return g;
}

/** Streaks along a direction: wind gusts or rain, moving towards the island. */
class Streaks {
  lines: LineSegments;
  private seeds: number[] = [];
  constructor(count: number, private dir: V3, private len: number, colour: string, private speed: number, private area: [number, number, number, number]) {
    const g = new BufferGeometry();
    g.setAttribute('position', new Float32BufferAttribute(new Float32Array(count * 6), 3));
    this.lines = new LineSegments(g, new LineBasicMaterial({color: colour, transparent: true, opacity: 0.55, depthWrite: false}));
    this.lines.raycast = () => {};
    let s = 3;
    for (let i = 0; i < count * 3; i++) this.seeds.push((s = (s * 16807) % 2147483647) / 2147483647);
  }
  update(time: number) {
    const p = this.lines.geometry.attributes.position as Float32BufferAttribute;
    const [x0, x1, z0, z1] = this.area;
    const n = p.count / 2;
    for (let i = 0; i < n; i++) {
      const u = (this.seeds[i * 3] + time * this.speed) % 1; // travel phase
      const x = x0 + this.seeds[i * 3 + 1] * (x1 - x0);
      const z = z0 + this.seeds[i * 3 + 2] * (z1 - z0);
      const travel = (1 - u) * 14;
      const ax = x + this.dir[0] * travel;
      const ay = 0.6 + this.dir[1] * travel + (this.dir[1] < 0.5 ? this.seeds[i * 3 + 2] * 2.4 : 0);
      const az = z + this.dir[2] * travel;
      p.setXYZ(i * 2, ax, ay, az);
      p.setXYZ(i * 2 + 1, ax + this.dir[0] * this.len, ay + this.dir[1] * this.len, az + this.dir[2] * this.len);
    }
    p.needsUpdate = true;
  }
}

export class LocalWatchers {
  group = new Group();
  private boats: {g: Group; phase: number}[] = [];
  private motos: {g: Group; phase: number; dir: number; z: number; speed: number}[] = [];
  private wind: Streaks | null = null;
  private rain: Streaks | null = null;
  private sea = sea();

  constructor() {
    this.group.add(this.sea);
  }

  /** Rebuild for a country. */
  set(c: Country) {
    for (const o of [...this.group.children]) if (o !== this.sea) this.group.remove(o);
    this.boats = [];
    this.motos = [];
    this.wind = this.rain = null;
    if (c.extra?.length && c.eyes.tower)
      c.extra.forEach((e, i) => this.group.add(tower(e.c, e.h, i === 0 ? c.eyes.tower![0] : null, c.id === 'my' ? 'my' : 'sg')));
    if (c.eyes.moto) {
      const looks: [string, string][] = [['#c8372d', '#f2f2f2'], ['#2f6fb5', '#f2c14e'], ['#e9e4d8', '#c8372d'], ['#2e8a5a', '#2b2b2e']];
      looks.forEach(([paint, helmet], i) => {
        const m = moto(paint, helmet);
        const dir = i % 2 ? -1 : 1;
        m.rotation.y = dir > 0 ? 0 : Math.PI;
        this.motos.push({g: m, phase: i * 0.27, dir, z: c.eyes.moto![0][2] + (dir > 0 ? 0.35 : -0.35), speed: 0.045 + i * 0.006});
        this.group.add(m);
      });
    }
    if (c.eyes.boat) {
      for (let i = 0; i < 2; i++) {
        const b = boat();
        this.boats.push({g: b, phase: i * 0.5});
        this.group.add(b);
      }
    }
    if (c.wind) {
      this.wind = new Streaks(90, c.wind, 1.6, '#ffffff', 0.35, [-5, 5, -3, 4]);
      this.group.add(this.wind.lines);
    }
    if (c.rain) {
      this.rain = new Streaks(260, c.rain, 0.9, '#cfe6ff', 0.9, [-9, 15, -8, 6]);
      this.group.add(this.rain.lines);
    }
  }

  /** Boats sail across from west to east along the water south of the island. */
  update(time: number) {
    for (const b of this.boats) {
      const u = ((time * 0.025 + b.phase) % 1);
      b.g.position.set(-14 + u * 32, SEA_Y + 0.05 + Math.sin(time * 1.3 + b.phase * 6) * 0.06, 7.2);
      b.g.rotation.z = Math.sin(time * 1.1 + b.phase) * 0.03;
    }
    for (const m of this.motos) {
      const u = (time * m.speed + m.phase) % 1;
      const x = -12 + u * 28;
      m.g.position.set(m.dir > 0 ? x : 4 - x, 0.02, m.z);
    }
    this.wind?.update(time);
    this.rain?.update(time);
  }

  /** The figures that can wave when they see something they should not. */
  figures(): Object3D[] {
    const out: Object3D[] = [];
    this.group.traverse((o) => {
      if (o.name === 'watcher') out.push(o);
    });
    return out;
  }
}
