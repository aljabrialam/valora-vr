// What the player sees of the checks: a beam per watcher and a label that says what it
// means in words and a symbol, never colour alone.

import {
  CanvasTexture,
  Color,
  CylinderGeometry,
  Group,
  Mesh,
  MeshBasicMaterial,
  SphereGeometry,
  Sprite,
  SpriteMaterial,
  SRGBColorSpace,
  Vector3,
} from '@iwsdk/core';
import type {Look} from './sim/world.ts';
import type {V3} from './sim/geom.ts';

export const INK = '#1d1d1f';
export const PASS = '#2f6f4f';
export const FAIL = '#a2452e';
export const BRONZE = '#a8835a';

// ---------- symbols, drawn as paths so they stay crisp and need no icon font ----------

type Icon = 'eye' | 'eye-off' | 'sun' | 'shade' | 'check' | 'cross';

export function drawIcon(g: CanvasRenderingContext2D, icon: Icon, x: number, y: number, s: number, colour: string) {
  g.save();
  g.translate(x, y);
  g.scale(s / 100, s / 100);
  g.strokeStyle = colour;
  g.fillStyle = colour;
  g.lineWidth = 8;
  g.lineCap = 'round';
  g.lineJoin = 'round';
  const eye = () => {
    g.beginPath();
    g.moveTo(8, 50);
    g.quadraticCurveTo(50, 8, 92, 50);
    g.quadraticCurveTo(50, 92, 8, 50);
    g.closePath();
    g.stroke();
    g.beginPath();
    g.arc(50, 50, 13, 0, Math.PI * 2);
    g.fill();
  };
  switch (icon) {
    case 'eye':
      eye();
      break;
    case 'eye-off':
      eye();
      g.beginPath();
      g.moveTo(16, 84);
      g.lineTo(84, 16);
      g.stroke();
      break;
    case 'sun':
      g.beginPath();
      g.arc(50, 50, 18, 0, Math.PI * 2);
      g.fill();
      for (let i = 0; i < 8; i++) {
        const a = (i * Math.PI) / 4;
        g.beginPath();
        g.moveTo(50 + Math.cos(a) * 30, 50 + Math.sin(a) * 30);
        g.lineTo(50 + Math.cos(a) * 42, 50 + Math.sin(a) * 42);
        g.stroke();
      }
      break;
    case 'shade':
      g.beginPath();
      g.arc(50, 50, 30, 0, Math.PI * 2);
      g.stroke();
      g.beginPath();
      g.arc(50, 50, 30, Math.PI / 2, (3 * Math.PI) / 2);
      g.closePath();
      g.fill();
      break;
    case 'check':
      g.beginPath();
      g.arc(50, 50, 40, 0, Math.PI * 2);
      g.stroke();
      g.beginPath();
      g.moveTo(32, 52);
      g.lineTo(45, 64);
      g.lineTo(69, 38);
      g.stroke();
      break;
    case 'cross':
      g.beginPath();
      g.arc(50, 50, 40, 0, Math.PI * 2);
      g.stroke();
      g.beginPath();
      g.moveTo(36, 36);
      g.lineTo(64, 64);
      g.moveTo(64, 36);
      g.lineTo(36, 64);
      g.stroke();
      break;
  }
  g.restore();
}

export function roundRect(g: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) {
  g.beginPath();
  g.moveTo(x + r, y);
  g.arcTo(x + w, y, x + w, y + h, r);
  g.arcTo(x + w, y + h, x, y + h, r);
  g.arcTo(x, y + h, x, y, r);
  g.arcTo(x, y, x + w, y, r);
  g.closePath();
}

// ---------- a label that floats over a target and always faces you ----------

export class Label {
  sprite: Sprite;
  private canvas = document.createElement('canvas');
  private tex: CanvasTexture;
  private key = '';

  constructor(widthM = 0.085) {
    this.canvas.width = 512;
    this.canvas.height = 128;
    this.tex = new CanvasTexture(this.canvas);
    this.tex.colorSpace = SRGBColorSpace;
    this.tex.anisotropy = 4;
    this.sprite = new Sprite(new SpriteMaterial({map: this.tex, transparent: true, depthTest: false, toneMapped: false}));
    this.sprite.scale.set(widthM, widthM / 4, 1);
    this.sprite.renderOrder = 10;
    // display only: IWSDK's ray pointer cannot raycast sprites (it throws without a camera)
    this.sprite.raycast = () => {};
  }

  set(text: string, icon: Icon, good: boolean) {
    const key = `${text}|${icon}|${good}`;
    if (key === this.key) return;
    this.key = key;
    const g = this.canvas.getContext('2d')!;
    g.clearRect(0, 0, 512, 128);
    g.font = '600 52px Inter, -apple-system, "Segoe UI", sans-serif';
    const tw = g.measureText(text).width;
    const w = Math.min(500, tw + 150);
    const x = (512 - w) / 2;
    roundRect(g, x, 14, w, 100, 50);
    g.fillStyle = 'rgba(250,248,243,0.94)';
    g.fill();
    g.lineWidth = 6;
    g.strokeStyle = good ? PASS : FAIL;
    g.stroke();
    drawIcon(g, icon, x + 24, 30, 68, good ? PASS : FAIL);
    g.fillStyle = INK;
    g.textBaseline = 'middle';
    g.fillText(text, x + 108, 66);
    this.tex.needsUpdate = true;
  }
}

// ---------- a beam along a watcher's line of sight ----------

const UP = new Vector3(0, 1, 0);

export class Beam {
  group = new Group();
  private rod: Mesh;
  private stop: Mesh;
  private mat: MeshBasicMaterial;

  constructor(colour: number, radius: number) {
    this.mat = new MeshBasicMaterial({color: new Color(colour), transparent: true, opacity: 0.85, depthWrite: false});
    this.rod = new Mesh(new CylinderGeometry(radius, radius, 1, 10, 1, true), this.mat);
    this.stop = new Mesh(new SphereGeometry(radius * 3.2, 16, 12), new MeshBasicMaterial({color: new Color(FAIL)}));
    this.group.add(this.rod, this.stop);
  }

  /** Draw from `a` towards `b`, stopping at fraction `t` (1 = reaches b). */
  set(a: V3, b: V3, t: number) {
    const A = new Vector3(...a);
    const B = new Vector3(...b);
    const end = A.clone().lerp(B, t);
    const len = A.distanceTo(end);
    this.rod.position.copy(A).add(end).multiplyScalar(0.5);
    this.rod.scale.set(1, Math.max(len, 1e-3), 1);
    this.rod.quaternion.setFromUnitVectors(UP, end.clone().sub(A).normalize());
    this.stop.visible = t < 0.999;
    this.stop.position.copy(end);
  }

  pulse(time: number, strong: boolean) {
    this.mat.opacity = strong ? 0.65 + 0.3 * Math.sin(time * 4) : 0.55;
  }
}

/** Short, plain-language reason for the label under a beam. */
export function because(look: Look): string {
  if (look.sees) return '';
  return look.blocker ? `blocked by the ${look.blocker}` : '';
}
