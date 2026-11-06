// Dust drifting slowly in the light above the model: a few hundred soft points, additive, no shadows.
// Cheap (one draw call) and it makes the air in the room feel warm and still.

import {AdditiveBlending, BufferAttribute, BufferGeometry, CanvasTexture, Points, PointsMaterial} from '@iwsdk/core';

function dot(): CanvasTexture {
  const c = document.createElement('canvas');
  c.width = c.height = 64;
  const g = c.getContext('2d')!;
  const grad = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  grad.addColorStop(0, 'rgba(255,240,210,1)');
  grad.addColorStop(0.4, 'rgba(255,225,170,0.5)');
  grad.addColorStop(1, 'rgba(255,220,160,0)');
  g.fillStyle = grad;
  g.fillRect(0, 0, 64, 64);
  return new CanvasTexture(c);
}

export class Motes {
  points: Points;
  private base: Float32Array;
  private phase: Float32Array;
  constructor(n: number, box = {w: 1.1, h: 0.45, d: 0.7}) {
    const pos = new Float32Array(n * 3);
    this.base = new Float32Array(n * 3);
    this.phase = new Float32Array(n);
    let s = 3;
    const r = () => ((s = (s * 16807) % 2147483647) / 2147483647);
    for (let i = 0; i < n; i++) {
      this.base[i * 3] = (r() - 0.5) * box.w;
      this.base[i * 3 + 1] = 0.05 + r() * box.h;
      this.base[i * 3 + 2] = (r() - 0.5) * box.d;
      this.phase[i] = r() * Math.PI * 2;
    }
    pos.set(this.base);
    const geo = new BufferGeometry();
    geo.setAttribute('position', new BufferAttribute(pos, 3));
    const mat = new PointsMaterial({size: 0.003, map: dot(), transparent: true, opacity: 0.35, depthWrite: false, blending: AdditiveBlending, sizeAttenuation: true, toneMapped: false});
    this.points = new Points(geo, mat);
    this.points.raycast = () => {}; // display only
    this.points.frustumCulled = false;
  }
  update(_dt: number, t: number) {
    const a = this.points.geometry.attributes.position as BufferAttribute;
    const p = a.array as Float32Array;
    for (let i = 0; i < this.phase.length; i++) {
      const ph = this.phase[i];
      p[i * 3] = this.base[i * 3] + Math.sin(t * 0.13 + ph) * 0.02;
      p[i * 3 + 1] = this.base[i * 3 + 1] + ((t * 0.006 + ph * 0.05) % 0.08);
      p[i * 3 + 2] = this.base[i * 3 + 2] + Math.cos(t * 0.11 + ph) * 0.02;
    }
    a.needsUpdate = true;
  }
}
