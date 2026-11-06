// VaLora: Two Watchers.
// A seated, hands-only puzzle: swing the privacy screen and slide the overhang so the sun and the
// neighbour see only what they should. Tiki the house gecko guides you. Every rule is checked by
// the same geometry the solver proves (src/sim).

import {
  Color,
  createSystem,
  DirectionalLight,
  DistanceGrabbable,
  Grabbed,
  Mesh,
  MeshBasicMaterial,
  MeshStandardMaterial,
  MovementMode,
  Pressed,
  RayInteractable,
  SphereGeometry,
  TorusGeometry,
  Vector3,
  World,
  type Entity,
} from '@iwsdk/core';
import projectOptions from 'virtual:iwsdk-project';
import {buildModel, DESK, LEVER, SCALE, setOverhang} from './model.ts';
import {Beam, Label} from './feedback.ts';
import {LevelCard} from './panel.ts';
import {Gecko} from './mascot.ts';
import {LAYOUT, screenAngles, sunAt, type Design} from './sim/world.ts';
import {evaluateLevel, LEVELS} from './sim/levels.ts';
import {clock} from './sim/sun.ts';
import {chimeSound, clickSound, solveSound} from './sound.ts';
import {SCRIPT, type Look, type Step} from './tutorial.ts';

const D = Math.PI / 180;
const params = new URLSearchParams(location.search);
let levelIndex = Math.min(LEVELS.length - 1, Math.max(0, Number(params.get('level') ?? 1) - 1));
let level = LEVELS[levelIndex];
const design: Design = {...level.start};
let shownDeg = design.screenDeg;
let shownOverhang = design.overhang;
let solved = false;

const world = await World.create(document.getElementById('scene-container') as HTMLDivElement, projectOptions);

// ---------- the model ----------
const model = buildModel();
const deskEntity = world.createTransformEntity(model.desk);
setOverhang(model, design.overhang);

// ---------- the sun: one light, a tight shadow over the model ----------
const sunLight = new DirectionalLight(new Color(0xfff1dc), 2.8);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
Object.assign(sunLight.shadow.camera, {left: -0.75, right: 0.75, top: 0.75, bottom: -0.75, near: 0.1, far: 5});
sunLight.shadow.bias = -0.0004;
sunLight.shadow.normalBias = 0.012;
world.createTransformEntity(sunLight);
world.createTransformEntity(sunLight.target);
sunLight.target.position.set(0, DESK.y, DESK.z);


// ---------- the watchers' beams and labels (in site metres) ----------
const neighbourBeam = new Beam(0xa2452e, 0.07);
const sunBeams = new Map<string, Beam>();
const seatLabel = new Label();
const plantLabel = new Label();
model.site.add(neighbourBeam.group);
for (const l of [seatLabel, plantLabel]) {
  l.sprite.scale.multiplyScalar(1 / SCALE);
  model.site.add(l.sprite);
}
seatLabel.sprite.position.set(LAYOUT.seat[0], LAYOUT.seat[1] + 2.9, LAYOUT.seat[2]);
plantLabel.sprite.position.set(LAYOUT.plant[0], LAYOUT.plant[1] + 1.9, LAYOUT.plant[2]);

const card = new LevelCard(0.42);
card.mesh.position.set(0, 0.36, -0.5);
card.mesh.rotation.x = -10 * D;
model.desk.add(card.mesh);

// ---------- Tiki, the guide ----------
const tiki = new Gecko();
const TIKI_HOME = new Vector3(-0.38, 0.002, 0.3);
tiki.group.position.copy(TIKI_HOME);
model.desk.add(tiki.group);
model.desk.remove(tiki.group);
const tikiEntity = world.createTransformEntity(tiki.group, deskEntity);
tikiEntity.addComponent(RayInteractable);

// ---------- handles you pinch ----------
const handleMat = new MeshStandardMaterial({color: 0xa8835a, roughness: 0.35, metalness: 0.6, emissive: new Color(0x6b4a24), emissiveIntensity: 0.4});
function makeHandle(): {mesh: Mesh; entity: Entity} {
  const mesh = new Mesh(new SphereGeometry(0.024, 24, 16), handleMat);
  const ring = new Mesh(new TorusGeometry(0.036, 0.0035, 8, 40), handleMat);
  ring.rotation.x = Math.PI / 2;
  mesh.add(ring);
  const entity = world.createTransformEntity(mesh);
  entity.addComponent(RayInteractable);
  entity.addComponent(DistanceGrabbable, {movementMode: MovementMode.MoveAtSource, translate: true, rotate: false, scale: false});
  return {mesh, entity};
}
const screenHandle = makeHandle();
const overhangHandle = makeHandle();

function screenHandleHome(deg: number): Vector3 {
  const s = LAYOUT.screen;
  const a = deg * D;
  const rad = s.len + LEVER.reach;
  return model.site.localToWorld(new Vector3(s.pivot[0] + Math.cos(a) * rad, s.h + LEVER.rise, s.pivot[2] - Math.sin(a) * rad));
}
const OVERHANG_GRIP = {x: 0.5, y: 0.6, z: 0.45};
function overhangHandleHome(depth: number): Vector3 {
  const r = LAYOUT.room;
  return model.site.localToWorld(new Vector3(OVERHANG_GRIP.x, r.h + OVERHANG_GRIP.y, r.z1 + depth + OVERHANG_GRIP.z));
}

// ---------- evaluate and redraw ----------
function refresh() {
  setOverhang(model, design.overhang);
  const res = evaluateLevel(level, design);
  const wasSolved = solved;
  solved = res.solved;
  card.draw(levelIndex, level, res.results, solved);

  const used = new Set<string>();
  for (const r of res.results) {
    const look = r.look;
    if (r.rule.watcher === 'neighbour') {
      neighbourBeam.set(look.from, look.to, look.t);
      seatLabel.set(look.sees ? 'SEEN' : 'PRIVATE', look.sees ? 'eye' : 'eye-off', r.pass);
    } else {
      used.add(r.rule.id);
      let beam = sunBeams.get(r.rule.id);
      if (!beam) {
        beam = new Beam(0xf2b84b, 0.06);
        sunBeams.set(r.rule.id, beam);
        model.site.add(beam.group);
      }
      const k = 11 / 60; // draw the last 11 m of the sun's ray so it stays on the model
      const from: typeof look.from = [
        look.to[0] + (look.from[0] - look.to[0]) * k,
        look.to[1] + (look.from[1] - look.to[1]) * k,
        look.to[2] + (look.from[2] - look.to[2]) * k,
      ];
      beam.set(from, look.to, look.sees ? 1 : Math.max(0, (look.t - (1 - k)) / k));
      if (r.rule.target === 'plant') plantLabel.set(look.sees ? 'IN SUN' : 'SHADED', look.sees ? 'sun' : 'shade', r.pass);
      if (r.rule.target === 'seat' && r.rule.watcher === 'sun' && !level.rules.some((x) => x.watcher === 'neighbour'))
        seatLabel.set(look.sees ? 'IN SUN' : 'SHADED', look.sees ? 'sun' : 'shade', r.pass);
    }
  }
  for (const [id, beam] of sunBeams) beam.group.visible = used.has(id);
  plantLabel.sprite.visible = level.rules.some((r) => r.target === 'plant');
  overhangHandle.mesh.visible = level.tools.includes('overhang');

  // the light follows the first sun rule; each sun rule gets its own visible sun
  const hours = level.rules.filter((r) => r.watcher === 'sun').map((r) => r.hour ?? 12);
  placeSun(hours[0] ?? 10);
  placeSunDiscs(hours);

  if (solved && !wasSolved) solveSound();
  console.info('[VR] design', JSON.stringify(design), 'level', level.id, 'solved', solved);
  (window as any).VR.state = {level: level.id, design: {...design}, solved, step: tutorial.stepId(), results: res.results.map((r) => ({id: r.rule.id, pass: r.pass, blocker: r.look.blocker}))};
}

function placeSun(hour: number) {
  const s = sunAt(hour);
  sunLight.position.set(s.dir[0] * 2.5, DESK.y + s.dir[1] * 2.5, DESK.z + s.dir[2] * 2.5);
}

const discMat = new MeshBasicMaterial({color: new Color('#ffd27a'), toneMapped: false});
const discs: Mesh[] = [];
const discLabels: Label[] = [];
function placeSunDiscs(hours: number[]) {
  while (discs.length < hours.length) {
    const m = new Mesh(new SphereGeometry(0.55, 24, 16), discMat);
    model.site.add(m);
    discs.push(m);
    const l = new Label(0.07);
    l.sprite.scale.multiplyScalar(1 / SCALE);
    model.site.add(l.sprite);
    discLabels.push(l);
  }
  discs.forEach((m, i) => {
    const on = i < hours.length;
    m.visible = on;
    discLabels[i].sprite.visible = on;
    if (!on) return;
    const s = sunAt(hours[i]);
    const c = LAYOUT.plant;
    m.position.set(c[0] + s.dir[0] * 12, c[1] + s.dir[1] * 12, c[2] + s.dir[2] * 12);
    discLabels[i].set(clock(hours[i]), 'sun', true);
    discLabels[i].sprite.position.copy(m.position).add(new Vector3(0, 1.3, 0));
  });
}

// ---------- the tutorial ----------
class Tutorial {
  private steps: Step[] = [];
  private i = 0;
  private enteredAt = 0;
  start(levelIdx: number) {
    this.steps = SCRIPT[levelIdx] ?? [];
    this.i = 0;
    this.enter(0);
  }
  stepId() {
    return this.steps[this.i]?.id ?? 'none';
  }
  private enter(now: number) {
    const st = this.steps[this.i];
    this.enteredAt = now;
    console.info('[VR] step', st?.id ?? 'end');
    if (!st) return tiki.hide();
    tiki.say(st.say, st.hint ?? (st.until === 'tap' ? 'Pinch Tiki to continue' : ''), now);
    tiki.look(lookAt(st.look));
    if (st.celebrate) tiki.celebrate();
    if (st.hop) tiki.hopTo(st.hop === 'home' ? TIKI_HOME : new Vector3(st.hop[0], st.hop[1], st.hop[2]));
  }
  next(now: number) {
    const st = this.steps[this.i];
    if (st?.then === 'next-level') return goToLevel((levelIndex + 1) % LEVELS.length, now);
    this.i++;
    this.enter(now);
  }
  tick(now: number, tapped: boolean) {
    const st = this.steps[this.i];
    if (!st) return;
    if (now - this.enteredAt < 0.4) return; // ignore the pinch that advanced the previous step
    if (st.until === 'tap' && tapped) this.next(now);
    else if (st.until === 'solved' && solved) this.next(now);
    if (st.look === 'handle' || st.look === 'overhang') tiki.look(lookAt(st.look));
  }
}

function lookAt(l: Look | undefined): Vector3 | null {
  const site = (p: number[]) => model.site.localToWorld(new Vector3(p[0], p[1], p[2]));
  switch (l) {
    case 'window':
      return site(LAYOUT.neighbour.window);
    case 'seat':
      return site(LAYOUT.seat);
    case 'plant':
      return site(LAYOUT.plant);
    case 'handle':
      return screenHandle.mesh.getWorldPosition(new Vector3());
    case 'overhang':
      return overhangHandle.mesh.getWorldPosition(new Vector3());
    case 'sun':
      return discs[0] ? discs[0].getWorldPosition(new Vector3()) : null;
    default:
      return null;
  }
}

const tutorial = new Tutorial();

function goToLevel(i: number, now = 0) {
  levelIndex = i;
  level = LEVELS[i];
  Object.assign(design, level.start);
  solved = false;
  refresh();
  chimeSound();
  tutorial.start(i);
  void now;
}

(window as any).VR = {
  state: {},
  setDesign(d: Partial<Design>) {
    Object.assign(design, d);
    refresh();
  },
  setLevel(i: number) {
    goToLevel(i);
  },
  tapTiki() {
    pendingTap = true;
  },
  // test hooks: project points to screen pixels, used by scripts
  handleScreen() {
    const v = screenHandle.mesh.getWorldPosition(new Vector3()).project(world.camera);
    return {x: ((v.x + 1) / 2) * innerWidth, y: ((1 - v.y) / 2) * innerHeight};
  },
  worldPos(name: 'screenHandle' | 'overhangHandle' | 'tiki') {
    const o = name === 'tiki' ? tiki.hit : name === 'screenHandle' ? screenHandle.mesh : overhangHandle.mesh;
    return o.getWorldPosition(new Vector3()).toArray();
  },
};
let pendingTap = false;
refresh();
tutorial.start(levelIndex);

// ---------- per-frame: drags, springs, Tiki ----------
class PlaySystem extends createSystem({}) {
  private wasPressed = false;
  private head = new Vector3();
  private tmp = new Vector3();
  update(delta: number, time: number) {
    // screen: the handle position becomes a snapped angle about the hinge
    const sGrab = screenHandle.entity.hasComponent(Grabbed);
    if (sGrab) {
      const local = model.site.worldToLocal(screenHandle.mesh.getWorldPosition(this.tmp));
      const piv = LAYOUT.screen.pivot;
      const deg = Math.atan2(-(local.z - piv[2]), local.x - piv[0]) / D;
      let best = Infinity;
      let snapped = design.screenDeg;
      for (const a of screenAngles()) {
        const diff = Math.abs(((deg - a + 540) % 360) - 180);
        if (diff < best) {
          best = diff;
          snapped = a;
        }
      }
      if (snapped !== design.screenDeg) {
        design.screenDeg = snapped;
        clickSound();
        refresh();
      }
    }
    // overhang: the handle's distance out from the glass becomes a snapped depth
    const oGrab = overhangHandle.entity.hasComponent(Grabbed);
    if (oGrab && level.tools.includes('overhang')) {
      const local = model.site.worldToLocal(overhangHandle.mesh.getWorldPosition(this.tmp));
      const {min, max, step} = LAYOUT.overhang;
      const raw = local.z - LAYOUT.room.z1 - OVERHANG_GRIP.z;
      const snapped = +Math.min(max, Math.max(min, Math.round(raw / step) * step)).toFixed(2);
      if (snapped !== design.overhang) {
        design.overhang = snapped;
        clickSound();
        refresh();
      }
    }
    // springs towards the snapped values
    const k = 1 - Math.exp(-delta * 14);
    shownDeg += (((design.screenDeg - shownDeg + 540) % 360) - 180) * k;
    model.screen.rotation.y = shownDeg * D;
    shownOverhang += (design.overhang - shownOverhang) * k;
    setOverhang(model, shownOverhang);
    if (!sGrab) screenHandle.mesh.position.copy(screenHandleHome(shownDeg));
    if (!oGrab) overhangHandle.mesh.position.copy(overhangHandleHome(shownOverhang));
    handleMat.emissiveIntensity = sGrab || oGrab ? 1.2 : 0.4 + 0.25 * Math.sin(time * 2.5);

    neighbourBeam.pulse(time, !solved);
    for (const b of sunBeams.values()) b.pulse(time, false);

    // Tiki: pinch to continue
    const pressed = tikiEntity.hasComponent(Pressed);
    const tapped = (pressed && !this.wasPressed) || pendingTap;
    this.wasPressed = pressed;
    pendingTap = false;
    world.camera.getWorldPosition(this.head);
    tiki.update(delta, time, this.head);
    tutorial.tick(time, tapped);
  }
}
world.registerSystem(PlaySystem);
