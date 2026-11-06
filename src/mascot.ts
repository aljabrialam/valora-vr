// Tiki, the house gecko who guides the tutorial. Original character, built from simple shapes in code
// (no imported art). Tiki sits on the front of the desk, looks at whatever it is talking about,
// blinks, breathes, sways its tail and hops when it moves. Pinch Tiki to continue.

import {
  CanvasTexture,
  Color,
  CylinderGeometry,
  Group,
  Mesh,
  MeshBasicMaterial,
  MeshStandardMaterial,
  SphereGeometry,
  Sprite,
  SpriteMaterial,
  SRGBColorSpace,
  Vector3,
} from '@iwsdk/core';
import {BRONZE, INK, roundRect} from './feedback.ts';

const skin = new MeshStandardMaterial({color: new Color('#d6c095'), roughness: 0.7});
const belly = new MeshStandardMaterial({color: new Color('#eadcbc'), roughness: 0.75});
const spots = new MeshStandardMaterial({color: new Color('#a5885c'), roughness: 0.8});
const eyeWhite = new MeshStandardMaterial({color: new Color('#fbf8f1'), roughness: 0.25});
const pupil = new MeshStandardMaterial({color: new Color('#2a2018'), roughness: 0.2});
const shine = new MeshBasicMaterial({color: '#ffffff'});
const blush = new MeshStandardMaterial({color: new Color('#e3a58b'), roughness: 0.9, transparent: true, opacity: 0.6});

function ball(r: number, mat: MeshStandardMaterial | MeshBasicMaterial, sx = 1, sy = 1, sz = 1): Mesh {
  const m = new Mesh(new SphereGeometry(r, 20, 14), mat);
  m.scale.set(sx, sy, sz);
  m.castShadow = true;
  return m;
}

export class Gecko {
  group = new Group(); // place this on the desk; +z faces the player
  body = new Group();
  private head = new Group();
  private lids: Mesh[] = [];
  private tail: Group[] = [];
  private legs: Group[] = [];
  private bubble: Sprite;
  private canvas = document.createElement('canvas');
  private tex: CanvasTexture;
  private lookTarget: Vector3 | null = null;
  private hop: {from: Vector3; to: Vector3; t: number} | null = null;
  private nextBlink = 2;
  private talkUntil = 0;
  private wave = 0;
  hit: Mesh; // generous invisible pinch target

  constructor() {
    const g = this.group;
    g.name = 'tiki';
    g.add(this.body);
    this.body.scale.setScalar(1.7); // about 24 cm nose to tail: big enough to read at arm's length

    // body and belly
    const torso = ball(0.024, skin, 1, 0.62, 1.55);
    torso.position.set(0, 0.016, 0);
    const tummy = ball(0.02, belly, 1, 0.45, 1.4);
    tummy.position.set(0, 0.011, 0.002);
    this.body.add(torso, tummy);
    for (const [x, z, r] of [[0.009, -0.012, 0.005], [-0.008, 0.004, 0.006], [0.006, 0.018, 0.004], [-0.004, -0.024, 0.004]] as const) {
      const s = ball(r, spots, 1, 0.35, 1);
      s.position.set(x, 0.0295, z);
      this.body.add(s);
    }

    // head: big round eyes on top, a little blush
    this.head.position.set(0, 0.026, 0.042);
    this.body.add(this.head);
    const skull = ball(0.025, skin, 1.15, 0.8, 1.15);
    this.head.add(skull);
    for (const side of [-1, 1]) {
      const eye = ball(0.0115, eyeWhite);
      eye.position.set(side * 0.016, 0.013, 0.01);
      const p = ball(0.0072, pupil);
      p.position.set(side * 0.0175, 0.0135, 0.0175);
      const s = new Mesh(new SphereGeometry(0.0019, 8, 6), shine);
      s.position.set(side * 0.0152, 0.0172, 0.0228);
      const lid = ball(0.0122, skin, 1, 0.08, 1);
      lid.position.set(side * 0.016, 0.0225, 0.01);
      this.lids.push(lid);
      const b = ball(0.0045, blush, 1, 0.4, 1);
      b.position.set(side * 0.017, -0.002, 0.016);
      this.head.add(eye, p, s, lid, b);
    }

    // legs with round toe pads, splayed like a gecko on a wall
    for (const [x, z, fwd] of [[0.022, 0.022, 1], [-0.022, 0.022, 1], [0.022, -0.02, -1], [-0.022, -0.02, -1]] as const) {
      const leg = new Group();
      leg.position.set(x, 0.012, z);
      const limb = new Mesh(new CylinderGeometry(0.0045, 0.0045, 0.022, 8), skin);
      limb.rotation.z = Math.sign(x) * 1.0;
      limb.position.set(Math.sign(x) * 0.008, -0.004, 0);
      limb.castShadow = true;
      leg.add(limb);
      for (let k = -1; k <= 1; k++) {
        const toe = ball(0.0042, skin, 1, 0.5, 1);
        toe.position.set(Math.sign(x) * 0.018 + k * 0.004 * fwd, -0.01, k * 0.005 + fwd * 0.004);
        leg.add(toe);
      }
      this.legs.push(leg);
      this.body.add(leg);
    }

    // tail: a chain of shrinking segments that sways
    let parent: Group = this.body;
    let z = -0.036;
    for (let i = 0; i < 7; i++) {
      const seg = new Group();
      seg.position.set(0, i === 0 ? 0.012 : 0, z);
      const r = 0.0095 * (1 - i / 8.5);
      const b = ball(r, skin, 1, 0.75, 1.25);
      seg.add(b);
      parent.add(seg);
      this.tail.push(seg);
      parent = seg;
      z = -r * 1.55;
    }

    // speech card above Tiki
    this.canvas.width = 1024;
    this.canvas.height = 420;
    this.tex = new CanvasTexture(this.canvas);
    this.tex.colorSpace = SRGBColorSpace;
    this.tex.anisotropy = 8;
    this.bubble = new Sprite(new SpriteMaterial({map: this.tex, transparent: true, depthTest: false, toneMapped: false}));
    this.bubble.scale.set(0.3, 0.123, 1);
    this.bubble.position.set(0.1, 0.2, 0); // nudged towards the middle of the view
    this.bubble.renderOrder = 20;
    this.bubble.raycast = () => {}; // display only; Tiki's hit sphere takes the pinch
    g.add(this.bubble);

    // invisible pinch target, larger than Tiki
    this.hit = new Mesh(new SphereGeometry(0.08, 12, 8), new MeshBasicMaterial({transparent: true, opacity: 0, depthWrite: false}));
    this.hit.position.set(0, 0.04, 0);
    g.add(this.hit);
  }

  /** Show a line of speech. `hint` is the small action line under it. */
  say(text: string, hint = '', now = 0) {
    const g = this.canvas.getContext('2d')!;
    const W = 1024;
    const H = 420;
    g.clearRect(0, 0, W, H);
    roundRect(g, 10, 10, W - 20, H - 70, 46);
    g.fillStyle = 'rgba(250,248,243,0.96)';
    g.fill();
    g.lineWidth = 4;
    g.strokeStyle = 'rgba(168,131,90,0.55)';
    g.stroke();
    // tail of the bubble pointing down at Tiki
    g.beginPath();
    g.moveTo(W / 2 - 34, H - 62);
    g.lineTo(W / 2, H - 14);
    g.lineTo(W / 2 + 34, H - 62);
    g.closePath();
    g.fillStyle = 'rgba(250,248,243,0.96)';
    g.fill();
    g.fillStyle = BRONZE;
    g.font = '600 30px Inter, -apple-system, sans-serif';
    g.fillText('TIKI', 56, 74);
    g.fillStyle = INK;
    g.font = '500 44px Inter, -apple-system, sans-serif';
    let y = 136;
    let line = '';
    for (const word of text.split(' ')) {
      const t = line ? `${line} ${word}` : word;
      if (g.measureText(t).width > W - 112 && line) {
        g.fillText(line, 56, y);
        line = word;
        y += 56;
      } else line = t;
    }
    if (line) g.fillText(line, 56, y);
    if (hint) {
      g.fillStyle = '#6b6a66';
      g.font = '500 30px Inter, -apple-system, sans-serif';
      g.fillText(hint, 56, H - 92);
    }
    this.tex.needsUpdate = true;
    this.talkUntil = now + 1.2;
    this.bubble.visible = true;
  }

  hide() {
    this.bubble.visible = false;
  }

  /** Turn to look at a point (world space), or at the player when null. */
  look(target: Vector3 | null) {
    this.lookTarget = target;
  }

  /** Hop to a new spot on the desk (desk-local coordinates). */
  hopTo(p: Vector3) {
    this.hop = {from: this.group.position.clone(), to: p.clone(), t: 0};
  }

  /** A little front-foot wave, for celebrations. */
  celebrate() {
    this.wave = 1.2;
  }

  update(dt: number, t: number, playerHead: Vector3) {
    // hop along an arc
    if (this.hop) {
      this.hop.t = Math.min(1, this.hop.t + dt * 1.6);
      const k = this.hop.t;
      const e = k * k * (3 - 2 * k);
      this.group.position.lerpVectors(this.hop.from, this.hop.to, e);
      this.group.position.y = this.hop.to.y + Math.sin(Math.PI * k) * 0.06;
      if (k >= 1) this.hop = null;
    }
    // breathe, sway, blink
    const talking = t < this.talkUntil;
    this.body.scale.y = 1.7 * (1 + Math.sin(t * 2.2) * 0.03);
    this.tail.forEach((seg, i) => (seg.rotation.y = Math.sin(t * 2.4 - i * 0.55) * (0.12 + i * 0.02)));
    if (t > this.nextBlink) {
      const b = t - this.nextBlink;
      const open = b < 0.08 ? 1 - b / 0.08 : b < 0.16 ? (b - 0.08) / 0.08 : 1;
      for (const lid of this.lids) lid.scale.y = 0.08 + (1 - open) * 0.95;
      if (b > 0.16) this.nextBlink = t + 2.5 + Math.random() * 2.5;
    }
    this.head.rotation.x = talking ? Math.sin(t * 9) * 0.06 : 0;
    // wave the front-right foot when celebrating
    if (this.wave > 0) {
      this.wave -= dt;
      this.legs[0].rotation.z = Math.sin(t * 14) * 0.5 - 0.4;
      this.legs[0].position.y = 0.022;
    } else {
      this.legs[0].rotation.z = 0;
      this.legs[0].position.y = 0.012;
    }
    // turn the whole body towards what Tiki is looking at (yaw only), the head a little more
    const world = this.group.getWorldPosition(new Vector3());
    const tgt = this.lookTarget ?? playerHead;
    const want = Math.atan2(tgt.x - world.x, tgt.z - world.z);
    const cur = this.body.rotation.y;
    const d = ((want - cur + Math.PI * 3) % (Math.PI * 2)) - Math.PI;
    this.body.rotation.y = cur + d * (1 - Math.exp(-dt * 5));
    this.head.rotation.y = Math.max(-0.5, Math.min(0.5, d * 0.5));
  }
}
