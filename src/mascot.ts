// Tiki, the house gecko who guides the tutorial. Original character, a glazed ceramic figurine built
// in code from turned (lathe) forms. Tiki sits on the front of the desk, looks at whatever it is talking about,
// blinks, breathes, sways its tail and hops when it moves. Pinch Tiki to continue.

import {
  type Object3D,
  CanvasTexture,
  Color,
  CylinderGeometry,
  Group,
  Mesh,
  MeshBasicMaterial,
  LatheGeometry,
  MeshPhysicalMaterial,
  type Material,
  Vector2,
  SphereGeometry,
  Sprite,
  SpriteMaterial,
  SRGBColorSpace,
  Vector3,
} from '@iwsdk/core';
import {BRONZE, INK, roundRect} from './feedback.ts';

// Tiki is a glazed ceramic figurine, in keeping with the architect's model: a celadon glaze with a
// clear coat, bronze-glaze spots, small glossy bead eyes. One smooth body, not a string of balls.
const skin = new MeshPhysicalMaterial({color: new Color('#6cc04a'), roughness: 0.3, clearcoat: 1, clearcoatRoughness: 0.08});
const belly = new MeshPhysicalMaterial({color: new Color('#f6e27a'), roughness: 0.35, clearcoat: 1, clearcoatRoughness: 0.1});
const spots = new MeshPhysicalMaterial({color: new Color('#f08a2b'), roughness: 0.35, metalness: 0.0, clearcoat: 1, clearcoatRoughness: 0.1});
// low environment reflection: a bright studio rim on the beads read as cartoon eye whites
const eyeBead = new MeshPhysicalMaterial({color: new Color('#16130f'), roughness: 0.15, envMapIntensity: 0.25});

function ball(r: number, mat: Material, sx = 1, sy = 1, sz = 1): Mesh {
  const m = new Mesh(new SphereGeometry(r, 24, 16), mat);
  m.scale.set(sx, sy, sz);
  m.castShadow = true;
  return m;
}

/** A smooth body turned on a lathe along +z: `radii` are sampled evenly from back to front. */
function turned(length: number, radii: number[], mat: Material, flatten = 1): Mesh {
  const pts = radii.map((r, i) => new Vector2(Math.max(r, 0.0001), (i / (radii.length - 1)) * length));
  const geo = new LatheGeometry(pts, 32);
  geo.rotateX(Math.PI / 2); // lathe axis y -> z (back to front)
  geo.scale(1, flatten, 1);
  geo.computeVertexNormals();
  const m = new Mesh(geo, mat);
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
  /** False on a flat screen, where the page overlay shows Tiki's words instead. */
  bubbleShown = true;

  constructor() {
    const g = this.group;
    g.name = 'tiki';
    g.add(this.body);
    this.body.scale.setScalar(1.7); // about 24 cm nose to tail: big enough to read at arm's length

    // body: one turned, flattened form from hips to shoulders, a paler belly glaze beneath
    const torso = turned(0.078, [0.004, 0.011, 0.017, 0.02, 0.021, 0.019, 0.015, 0.011, 0.008], skin, 0.58);
    torso.position.set(0, 0.016, -0.04);
    const tummy = turned(0.07, [0.004, 0.012, 0.018, 0.02, 0.019, 0.015, 0.009], belly, 0.42);
    tummy.position.set(0, 0.0115, -0.036);
    this.body.add(torso, tummy);
    for (const [x, z, r] of [[0.009, -0.014, 0.0045], [-0.008, 0.002, 0.0055], [0.006, 0.017, 0.0038], [-0.005, -0.027, 0.0035], [0.0, 0.03, 0.003]] as const) {
      const s = ball(r, spots, 1, 0.3, 1);
      s.position.set(x, 0.0298, z);
      this.body.add(s);
    }

    // head: a wedge-shaped turned head with a rounded snout, bead eyes set on the sides
    this.head.position.set(0, 0.024, 0.036);
    this.body.add(this.head);
    const skull = turned(0.056, [0.01, 0.017, 0.0195, 0.019, 0.0165, 0.013, 0.009, 0.0055, 0.001], skin, 0.62);
    skull.position.set(0, 0, -0.008);
    skull.scale.x = 1.12;
    this.head.add(skull);
    for (const side of [-1, 1]) {
      const eye = ball(0.0068, eyeBead);
      eye.position.set(side * 0.0168, 0.0068, 0.008);
      const lid = ball(0.0074, skin, 1, 0.08, 1);
      lid.position.set(side * 0.0168, 0.0114, 0.008);
      this.lids.push(lid);
      this.head.add(eye, lid);
    }

    // legs with round toe pads, splayed like a gecko on a wall
    for (const [x, z, fwd] of [[0.022, 0.022, 1], [-0.022, 0.022, 1], [0.022, -0.02, -1], [-0.022, -0.02, -1]] as const) {
      const leg = new Group();
      leg.position.set(x, 0.012, z);
      const limb = new Mesh(new CylinderGeometry(0.0034, 0.0042, 0.022, 12), skin);
      limb.rotation.z = Math.sign(x) * 1.0;
      limb.position.set(Math.sign(x) * 0.008, -0.004, 0);
      limb.castShadow = true;
      leg.add(limb);
      for (let k = -1; k <= 1; k++) {
        const toe = ball(0.0034, skin, 1, 0.5, 1.2);
        toe.position.set(Math.sign(x) * 0.018 + k * 0.004 * fwd, -0.01, k * 0.005 + fwd * 0.004);
        leg.add(toe);
      }
      this.legs.push(leg);
      this.body.add(leg);
    }

    // tail: a chain of shrinking segments that sways
    let parent: Group = this.body;
    let z = -0.038;
    for (let i = 0; i < 9; i++) {
      const seg = new Group();
      seg.position.set(0, i === 0 ? 0.014 : 0, z);
      const r = 0.0088 * (1 - i / 10.5);
      const b = ball(r, skin, 1, 0.68, 1.5);
      seg.add(b);
      parent.add(seg);
      this.tail.push(seg);
      parent = seg;
      z = -r * 1.15; // segments overlap so the glaze reads as one tapering tail
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
      g.font = '500 28px Inter, -apple-system, sans-serif';
      // up to two lines, bottom-aligned above the tail
      const lines: string[] = [];
      let cur = '';
      for (const word of hint.split(' ')) {
        const t = cur ? `${cur} ${word}` : word;
        if (g.measureText(t).width > W - 112 && cur) {
          lines.push(cur);
          cur = word;
        } else cur = t;
      }
      if (cur) lines.push(cur);
      lines.slice(0, 2).forEach((l, i, a) => g.fillText(l, 56, H - 92 - (a.length - 1 - i) * 34));
    }
    this.tex.needsUpdate = true;
    this.talkUntil = now + 1.2;
    this.bubble.visible = this.bubbleShown;
  }

  /** Show the speech bubble at a fixed place in the world (headset: straight ahead) or back over Tiki. */
  anchorBubble(parent: Object3D | null, at?: Vector3, width = 0.3) {
    const home = parent ?? this.group;
    if (this.bubble.parent !== home) home.add(this.bubble);
    if (parent && at) this.bubble.position.copy(at);
    else this.bubble.position.set(0.1, 0.2, 0);
    this.bubble.scale.set(width, width * 0.41, 1);
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
      for (const lid of this.lids) {
        lid.scale.y = 0.08 + (1 - open) * 0.95;
        lid.visible = open < 0.9; // only during a blink
      }
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
