// VaLora: Two Watchers — prototype.
// One screen, one neighbour, one sun. Pinch the bronze handle and swing the screen;
// the beams and the level card update from the same checks the solver proves.

import {
  createSystem,
  DistanceGrabbable,
  Grabbed,
  MovementMode,
  RayInteractable,
  World,
} from '@iwsdk/core';
import projectOptions from 'virtual:iwsdk-project';
import {
  Color,
  DirectionalLight,
  Mesh,
  MeshStandardMaterial,
  SphereGeometry,
  TorusGeometry,
  Vector3,
} from 'three';
import {buildModel, DESK, SCALE, setOverhang} from './model.ts';
import {Beam, Label} from './feedback.ts';
import {LevelCard} from './panel.ts';
import {LAYOUT, screenAngles, sunAt, type Design} from './sim/world.ts';
import {evaluateLevel, LEVELS} from './sim/levels.ts';
import {clickSound} from './sound.ts';

const D = Math.PI / 180;
const params = new URLSearchParams(location.search);
let levelIndex = Math.min(LEVELS.length - 1, Math.max(0, Number(params.get('level') ?? 1) - 1));
let level = LEVELS[levelIndex];
const design: Design = {...level.start};
let shownDeg = design.screenDeg;

const world = await World.create(document.getElementById('scene-container') as HTMLDivElement, projectOptions);

// ---------- the model ----------
const model = buildModel();
world.createTransformEntity(model.desk);
setOverhang(model, design.overhang);

// ---------- the sun: one light, a tight shadow over the model ----------
const sunLight = new DirectionalLight(new Color(0xfff1dc), 2.6);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
const cam = sunLight.shadow.camera;
cam.left = -0.5;
cam.right = 0.5;
cam.top = 0.5;
cam.bottom = -0.5;
cam.near = 0.1;
cam.far = 4;
sunLight.shadow.bias = -0.0004;
sunLight.shadow.normalBias = 0.01;
world.scene.add(sunLight, sunLight.target);
sunLight.target.position.set(0, DESK.y, DESK.z);

function placeSun(hour: number) {
  const s = sunAt(hour);
  sunLight.position.set(s.dir[0] * 2, DESK.y + s.dir[1] * 2, DESK.z + s.dir[2] * 2);
}

// ---------- the watchers' beams and labels, in site metres ----------
const neighbourBeam = new Beam(0xa2452e, 0.07);
const sunBeams = new Map<string, Beam>();
const seatLabel = new Label();
const plantLabel = new Label();
model.site.add(neighbourBeam.group);
for (const l of [seatLabel, plantLabel]) model.desk.add(l.sprite);

const card = new LevelCard();
card.mesh.position.set(0, 0.3, -0.42);
card.mesh.rotation.x = -12 * D;
model.desk.add(card.mesh);

// ---------- the handle you pinch ----------
const handleMat = new MeshStandardMaterial({color: 0xa8835a, roughness: 0.35, metalness: 0.6, emissive: new Color(0x6b4a24), emissiveIntensity: 0.4});
const handle = new Mesh(new SphereGeometry(0.022, 24, 16), handleMat);
const ring = new Mesh(new TorusGeometry(0.034, 0.003, 8, 40), handleMat);
ring.rotation.x = Math.PI / 2;
handle.add(ring);
const handleEntity = world.createTransformEntity(handle);
handleEntity.addComponent(RayInteractable);
handleEntity.addComponent(DistanceGrabbable, {
  movementMode: MovementMode.MoveAtSource,
  translate: true,
  rotate: false,
  scale: false,
});

function handleHome(deg: number) {
  const s = LAYOUT.screen;
  const a = deg * D;
  const p = new Vector3(s.pivot[0] + Math.cos(a) * s.len, s.h + 0.9, s.pivot[2] - Math.sin(a) * s.len);
  return model.site.localToWorld(p);
}

// ---------- evaluate and redraw ----------
function refresh() {
  setOverhang(model, design.overhang);
  const {results, solved} = evaluateLevel(level, design);
  card.draw(levelIndex, level, results, solved);

  const used = new Set<string>();
  for (const r of results) {
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
      // draw only the last 9 m of the sun's ray so it stays on the model
      const k = 9 / 60;
      const from: typeof look.from = [
        look.to[0] + (look.from[0] - look.to[0]) * k,
        look.to[1] + (look.from[1] - look.to[1]) * k,
        look.to[2] + (look.from[2] - look.to[2]) * k,
      ];
      const t = look.sees ? 1 : Math.max(0, (look.t - (1 - k)) / k);
      beam.set(from, look.to, t);
      if (r.rule.target === 'plant') plantLabel.set(look.sees ? 'IN SUN' : 'SHADED', look.sees ? 'sun' : 'shade', r.pass);
    }
  }
  for (const [id, beam] of sunBeams) beam.group.visible = used.has(id);
  plantLabel.sprite.visible = level.rules.some((r) => r.target === 'plant');

  const sunRule = level.rules.find((r) => r.watcher === 'sun');
  placeSun(sunRule?.hour ?? 10);
  console.info('[VR] design', JSON.stringify(design), 'solved', solved);
  (window as any).VR.state = {level: level.id, design: {...design}, solved, results: results.map((r) => ({id: r.rule.id, pass: r.pass, blocker: r.look.blocker}))};
}

function placeLabels() {
  const toDesk = (p: number[]) =>
    new Vector3((p[0] - 3.4) * SCALE, p[1] * SCALE, (p[2] + 1.6) * SCALE);
  seatLabel.sprite.position.copy(toDesk(LAYOUT.seat)).add(new Vector3(0, 0.17, 0));
  plantLabel.sprite.position.copy(toDesk(LAYOUT.plant)).add(new Vector3(0, 0.1, 0));
}

(window as any).VR = {
  // test hooks: project a world point to screen pixels, used by scripts/e2e
  handleScreen() {
    const v = handle.getWorldPosition(new Vector3()).project(world.camera);
    return {x: ((v.x + 1) / 2) * innerWidth, y: ((1 - v.y) / 2) * innerHeight};
  },
  worldToScreen(p: [number, number, number]) {
    const v = model.site.localToWorld(new Vector3(...p)).project(world.camera);
    return {x: ((v.x + 1) / 2) * innerWidth, y: ((1 - v.y) / 2) * innerHeight};
  },
  setDesign(d: Partial<Design>) {
    Object.assign(design, d);
    shownDeg = design.screenDeg;
    refresh();
  },
  setLevel(i: number) {
    levelIndex = i;
    level = LEVELS[i];
    Object.assign(design, level.start);
    shownDeg = design.screenDeg;
    refresh();
  },
};
placeLabels();
refresh();

// ---------- the drag: handle position becomes a snapped screen angle ----------
class ScreenDragSystem extends createSystem({}) {
  update(delta: number, time: number) {
    const grabbed = handleEntity.hasComponent(Grabbed);
    if (grabbed) {
      const local = model.site.worldToLocal(handle.getWorldPosition(new Vector3()));
      const piv = LAYOUT.screen.pivot;
      const deg = Math.atan2(-(local.z - piv[2]), local.x - piv[0]) / D;
      // nearest angle the screen can physically reach (it cannot swing through the glass or a wall)
      let snapped = design.screenDeg;
      let best = Infinity;
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
    // the screen settles towards the snapped angle with a critically damped spring
    const k = 1 - Math.exp(-delta * 14);
    shownDeg += (((design.screenDeg - shownDeg + 540) % 360) - 180) * k;
    model.screen.rotation.y = shownDeg * D;
    if (!grabbed) handle.position.copy(handleHome(shownDeg));
    handleMat.emissiveIntensity = grabbed ? 1.2 : 0.4 + 0.25 * Math.sin(time * 2.5);
    neighbourBeam.pulse(time, true);
    for (const b of sunBeams.values()) b.pulse(time, false);
  }
}
world.registerSystem(ScreenDragSystem);
