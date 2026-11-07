// Puffy toy clouds drifting slowly around and below the floating island. Each cloud is a few soft
// spheres merged into one mesh; all share one material. Scenery only: they never take rays.

import {Group, IcosahedronGeometry, Mesh, MeshStandardMaterial, type BufferGeometry} from '@iwsdk/core';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';

const MAT = new MeshStandardMaterial({color: '#ffffff', roughness: 1, emissive: '#dfeaff', emissiveIntensity: 0.35, transparent: true, opacity: 0.95});

export class Clouds {
  group = new Group();
  private items: {m: Mesh; speed: number; r: number; a: number; y: number}[] = [];

  constructor(count: number) {
    let seed = 11;
    const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
    for (let i = 0; i < count; i++) {
      const parts: BufferGeometry[] = [];
      const n = 4 + Math.floor(rnd() * 4);
      for (let k = 0; k < n; k++) {
        const g = new IcosahedronGeometry(0.05 + rnd() * 0.05, 2);
        g.scale(1, 0.7, 1);
        g.translate((k - n / 2) * 0.055 + rnd() * 0.02, rnd() * 0.03, rnd() * 0.04);
        parts.push(g);
      }
      const m = new Mesh(mergeGeometries(parts)!, MAT);
      m.raycast = () => {};
      const s = 0.8 + rnd() * 1.4;
      m.scale.setScalar(s);
      // a ring around the island, mostly level with or below it so they never block the play
      const item = {m, speed: 0.012 + rnd() * 0.02, r: 1.8 + rnd() * 1.4, a: rnd() * Math.PI * 2, y: -0.9 + rnd() * 0.75};
      if (item.y > -0.1 && item.r < 1.8) item.r += 1.0;
      this.items.push(item);
      this.group.add(m);
    }
    this.update(0);
  }

  update(dt: number) {
    for (const c of this.items) {
      c.a += c.speed * dt;
      c.m.position.set(Math.cos(c.a) * c.r, c.y, Math.sin(c.a) * c.r * 0.8 - 0.9);
      c.m.rotation.y = -c.a;
    }
  }
}
