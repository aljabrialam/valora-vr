// VaLora: Two Watchers.
// A seated, hands-first puzzle on an architect's model. Two watchers look at the house: the sun,
// hour by hour, and the neighbour next door. Pick pieces from the tray (screen, tree, pergola,
// hedge), set them in the courtyard, drag the sun across the sky to see the shadows move, then
// live the day and see if the house works. Fewer pieces earn more stars. Every check is the same
// geometry the prover runs (src/sim/play.ts, scripts/prove2.ts).

import {
  Color,
  createSystem,
  DirectionalLight,
  DistanceGrabbable,
  Grabbed,
  Group,
  Mesh,
  MeshBasicMaterial,
  MeshStandardMaterial,
  MovementMode,
  Plane,
  Pressed,
  Raycaster,
  RayInteractable,
  SphereGeometry,
  HemisphereLight,
  TorusGeometry,
  BoxGeometry,
  CylinderGeometry,
  Vector2,
  Vector3,
  World,
  type Entity,
  type Object3D,
} from '@iwsdk/core';
import projectOptions from 'virtual:iwsdk-project';
import {buildModel, DESK, GARDEN, SCALE, setOverhang, WIND} from './model.ts';
import {Motes} from './motes.ts';
import {loadHouse, loadIsland, loadPlant, loadTrees} from './look/assets.ts';
import {Clouds} from './clouds.ts';
import {Beam, Label} from './feedback.ts';
import {Hud} from './hud.ts';
import {LevelCard} from './panel.ts';
import {Gecko} from './mascot.ts';
import {MAT, pieceModel, scaleFigure} from './pieces.ts';
import {LAYOUT} from './sim/world.ts';
import {COUNTRIES, COUNTRY, countrySun, evaluate, evaluateLevel, eyePoints, LEVELS, PIECES, setCountry, SOCKETS, TARGETS, type Design, type Kind, type Placed, type RuleResult} from './sim/play.ts';
import {LocalWatchers} from './watchers.ts';
import {clock} from './sim/sun.ts';
import {chimeSound, clickSound, solveSound} from './sound.ts';
import {scriptFor, type Look, type Step} from './tutorial.ts';

const D = Math.PI / 180;
const params = new URLSearchParams(location.search);
const startCountry = params.get('country');
setCountry((startCountry ?? 'ph') as 'ph');
let firstLevelPlayed = true;
let levelIndex = Math.min(LEVELS.length - 1, Math.max(0, Number(params.get('level') ?? 1) - 1));
let level = LEVELS[levelIndex];
const design: Design = {pieces: [], overhang: 0};
let shownOverhang = 0;
let solved = false;
let stars = 0;
let viewHour = 10; // the hour the sun is showing; the player drags it

const world = await World.create(document.getElementById('scene-container') as HTMLDivElement, projectOptions);

// ---------- the model ----------
const model = buildModel();
model.screen.visible = false; // the old swinging screen: screens are now pieces from the tray
const deskEntity = world.createTransformEntity(model.desk);
loadPlant(1.15).then((p) => model.marks.plant.add(p)).catch((e) => console.warn('[VR] plant', e));
loadIsland().then((i) => model.site.add(i)).catch((e) => console.warn('[VR] island', e));
loadHouse().then((h) => model.site.add(h)).catch((e) => console.warn('[VR] house', e));
loadTrees(GARDEN).then((t) => model.site.add(t)).catch((e) => console.warn('[VR] trees', e));
const siteToWorld = (p: number[], out = new Vector3()) => model.site.localToWorld(out.set(p[0], p[1], p[2]));

// ---------- light: the sun casts the shadows; a gallery spot and a rim do the rest ----------
const sunLight = new DirectionalLight(new Color(0xfff0d6), 3.2);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
Object.assign(sunLight.shadow.camera, {left: -0.75, right: 0.75, top: 0.75, bottom: -0.75, near: 0.1, far: 5});
sunLight.shadow.bias = -0.0004;
sunLight.shadow.normalBias = 0.012;
sunLight.shadow.radius = 4;
world.createTransformEntity(sunLight);
world.createTransformEntity(sunLight.target);
sunLight.target.position.set(0, DESK.y, DESK.z);
// daylight: a blue sky fill from above and warm bounce from below; the sun owns the shadows
const sky = new HemisphereLight(new Color(0xbfdcff), new Color(0xf1d9b0), 0.9);
world.createTransformEntity(sky);
const clouds = new Clouds(14);
clouds.group.position.set(0, DESK.y - 0.1, DESK.z);
world.scene.add(clouds.group);

// ---------- what the watchers see: beams, labels and the two scale figures ----------
const beams = new Map<string, Beam>();
const labels = new Map<string, Label>();
const neighbourAtWindow = scaleFigure(true);
// he stands on a small balcony outside his window, so you can see him (and see him wave)
const nh = LAYOUT.neighbour.house;
const balcony = new Mesh(new BoxGeometry(1.0, 0.12, 2.0), MAT.card);
balcony.position.set(nh.x0 + 0.3 - 0.5, LAYOUT.neighbour.window[1] - 1.62, LAYOUT.neighbour.window[2]);
balcony.castShadow = balcony.receiveShadow = true;
const rail = new Mesh(new BoxGeometry(0.05, 0.9, 2.0), MAT.card);
rail.position.set(-0.48, 0.5, 0);
balcony.add(rail);
model.site.add(balcony);
neighbourAtWindow.position.set(nh.x0 + 0.3 - 0.45, LAYOUT.neighbour.window[1] - 1.56, LAYOUT.neighbour.window[2]);
neighbourAtWindow.rotation.y = -Math.PI / 2;
const neighbourOnTerrace = scaleFigure(true);
neighbourOnTerrace.position.set(9.4, 6.0 - 1.55, 0.4);
neighbourOnTerrace.visible = false;
neighbourOnTerrace.rotation.y = -Math.PI / 2 - 0.3;
const resident = scaleFigure(false); // stands where each moment of the day happens
resident.visible = false;
model.site.add(neighbourAtWindow, neighbourOnTerrace, resident);
const local = new LocalWatchers();
model.site.add(local.group);

const hud = new Hud();
const card = new LevelCard(0.42);
card.mesh.position.set(0, 0.36, -0.5);
card.mesh.rotation.x = -10 * D;
model.desk.add(card.mesh);
const motes = new Motes(60);
model.desk.add(motes.points);

// ---------- Tiki ----------
const tiki = new Gecko();
const TIKI_HOME = new Vector3(-0.38, 0.002, 0.3);
tiki.group.position.copy(TIKI_HOME);
const tikiEntity = world.createTransformEntity(tiki.group, deskEntity);
tikiEntity.addComponent(RayInteractable);

// ---------- the tray: a walnut ledge on the front of the plinth ----------
// the tray is a little timber raft floating just in front of the island
const raft = new Group();
const plankMat = new MeshStandardMaterial({color: '#c98a4b', roughness: 0.75});
for (let i = 0; i < 5; i++) {
  const plank = new Mesh(new BoxGeometry(0.66, 0.01, 0.03), plankMat);
  plank.position.set(0, 0, -0.068 + i * 0.034);
  plank.rotation.z = (i % 2 ? 1 : -1) * 0.006;
  plank.receiveShadow = plank.castShadow = true;
  raft.add(plank);
}
for (const x of [-0.3, 0, 0.3]) {
  const batten = new Mesh(new BoxGeometry(0.03, 0.008, 0.17), new MeshStandardMaterial({color: '#9a5a2c', roughness: 0.8}));
  batten.position.set(x, -0.009, 0);
  raft.add(batten);
}
raft.position.set(0.8, -0.006, 0.13);
raft.rotation.y = Math.PI / 2; // along the right side of the island, out of the boats' way
model.desk.add(raft);
const KIND_ORDER: Kind[] = ['screen', 'hedge', 'tree', 'pergola'];
const TRAY_SCALE = 0.5; // pieces wait on the raft at half size
const traySlot = (kind: Kind, n: number) => new Vector3(0.8 + n * 0.014, 0.0, 0.42 - KIND_ORDER.indexOf(kind) * 0.12 - n * 0.012);

// ---------- pieces: every copy in the tray is its own grabbable object ----------
type PieceObj = {
  kind: Kind;
  n: number; // which copy of this kind
  root: Group;
  entity: Entity;
  socket: number; // -1 in the tray
  rot: number;
  target: Vector3; // where it springs to (world)
  yaw: number;
  held: boolean;
  heldAt: number;
  heldFrom: Vector3;
};
let pieceObjs: PieceObj[] = [];
const ghost = new Mesh(new CylinderGeometry(1.0, 1.0, 0.06, 32), MAT.ghostOk);
ghost.visible = false;
model.site.add(ghost);

function buildTray() {
  for (const o of pieceObjs) o.entity.dispose();
  pieceObjs = [];
  for (const kind of KIND_ORDER) {
    const count = level.tray[kind] ?? 0;
    for (let n = 0; n < count; n++) {
      const root = new Group();
      root.name = `piece-${kind}-${n}`;
      root.add(pieceModel(kind));
      root.scale.setScalar(SCALE * TRAY_SCALE);
      const entity = world.createTransformEntity(root);
      entity.addComponent(RayInteractable);
      entity.addComponent(DistanceGrabbable, {movementMode: MovementMode.MoveAtSource, translate: true, rotate: false, scale: false});
      const o: PieceObj = {kind, n, root, entity, socket: -1, rot: 0, target: new Vector3(), yaw: 0, held: false, heldAt: 0, heldFrom: new Vector3()};
      homeInTray(o);
      root.position.copy(o.target);
      pieceObjs.push(o);
    }
  }
}

function homeInTray(o: PieceObj) {
  o.socket = -1;
  o.rot = 0;
  o.yaw = 0;
  model.desk.localToWorld(o.target.copy(traySlot(o.kind, o.n)));
}

function syncDesign() {
  design.pieces = pieceObjs.filter((o) => o.socket >= 0).map((o): Placed => ({kind: o.kind, socket: o.socket, rot: o.rot}));
}

/** The free socket nearest a world point, if the point is over the courtyard. */
function socketNear(world: Vector3, self: PieceObj): number {
  const p = model.site.worldToLocal(world.clone());
  const c = LAYOUT.court;
  if (p.x < c.x0 - 1.2 || p.x > c.x1 + 1.2 || p.z < c.z0 - 1.2 || p.z > c.z1 + 1.2) return -1;
  let best = -1;
  let bd = 1.6;
  SOCKETS.forEach((s, i) => {
    if (pieceObjs.some((o) => o !== self && o.socket === i)) return;
    const d = Math.hypot(s[0] - p.x, s[2] - p.z);
    if (d < bd) {
      bd = d;
      best = i;
    }
  });
  return best;
}

function placeAt(o: PieceObj, socket: number) {
  o.socket = socket;
  siteToWorld(SOCKETS[socket], o.target);
  o.yaw = o.rot * (o.kind === 'hedge' ? 90 : 45) * D;
}

function rotate(o: PieceObj) {
  const n = PIECES[o.kind].rots;
  if (n < 2 || o.socket < 0) return;
  o.rot = (o.rot + 1) % n;
  placeAt(o, o.socket);
  clickSound();
  syncDesign();
  refresh();
}

/** While a piece is held: show where it would land. */
function hover(o: PieceObj) {
  const s = socketNear(o.root.position, o);
  ghost.visible = s >= 0;
  if (s >= 0) ghost.position.set(SOCKETS[s][0], 0.04, SOCKETS[s][2]);
}

/** A piece was let go: land on the nearest free socket, or go back to the tray. A short pinch that
 *  barely moved is a tap: it turns a placed piece. */
function release(o: PieceObj, now: number) {
  ghost.visible = false;
  const moved = o.root.position.distanceTo(o.heldFrom);
  if (o.socket >= 0 && moved < 0.02 && now - o.heldAt < 0.45) return rotate(o);
  const s = socketNear(o.root.position, o);
  if (s >= 0) placeAt(o, s);
  else homeInTray(o);
  clickSound();
  syncDesign();
  refresh();
}

// ---------- the sun you can drag across the sky ----------
const ARC_R = 9; // site metres from the courtyard centre
const ARC_C: [number, number, number] = [0, 0, 0.5];
const arcPoint = (h: number, out = new Vector3()) => {
  const s = countrySun(h);
  return siteToWorld([ARC_C[0] + s.dir[0] * ARC_R, ARC_C[1] + s.dir[1] * ARC_R, ARC_C[2] + s.dir[2] * ARC_R], out);
};
const sunMat = new MeshBasicMaterial({color: new Color('#ffd27a'), toneMapped: false});
const sunHandle = new Mesh(new SphereGeometry(0.022, 24, 16), sunMat);
const sunRing = new Mesh(new TorusGeometry(0.034, 0.003, 8, 40), new MeshBasicMaterial({color: new Color('#ffd27a'), toneMapped: false, transparent: true, opacity: 0.6}));
sunHandle.add(sunRing);
const sunEntity = world.createTransformEntity(sunHandle);
sunEntity.addComponent(RayInteractable);
sunEntity.addComponent(DistanceGrabbable, {movementMode: MovementMode.MoveAtSource, translate: true, rotate: false, scale: false});
const sunLabel = new Label(0.07);
sunLabel.sprite.raycast = () => {};
world.scene.add(sunLabel.sprite);
// a faint dotted path for the sun's day
const arcDots = new Group();
for (let h = 7; h <= 18.5; h += 0.5) {
  const d = new Mesh(new SphereGeometry(0.003, 8, 6), new MeshBasicMaterial({color: new Color('#ffd27a'), transparent: true, opacity: 0.5, toneMapped: false}));
  arcPoint(h, d.position);
  d.raycast = () => {};
  arcDots.add(d);
}
world.scene.add(arcDots);

function hourNearest(p: Vector3): number {
  let best = viewHour;
  let bd = Infinity;
  const q = new Vector3();
  for (let h = 7; h <= 18.5; h += 0.25) {
    const d = arcPoint(h, q).distanceTo(p);
    if (d < bd) {
      bd = d;
      best = h;
    }
  }
  return best;
}
function hourNearestRay(ray: Raycaster['ray']): number {
  let best = viewHour;
  let bd = Infinity;
  const q = new Vector3();
  for (let h = 7; h <= 18.5; h += 0.25) {
    const d = ray.distanceSqToPoint(arcPoint(h, q));
    if (d < bd) {
      bd = d;
      best = h;
    }
  }
  return best;
}

function setHour(h: number) {
  if (h === viewHour) return;
  viewHour = h;
  showSun();
}
function showSun() {
  const s = countrySun(viewHour);
  sunLight.position.set(s.dir[0] * 2.5, DESK.y + s.dir[1] * 2.5, DESK.z + s.dir[2] * 2.5);
  sunLight.intensity = 3.2 * Math.min(1, Math.max(0.2, s.el / 20));
  sunLight.color.set(s.el < 15 ? 0xffc690 : 0xfff0d6);
  if (!sunGrabbed) arcPoint(viewHour, sunHandle.position);
  sunLabel.set(clock(viewHour), 'sun', true);
  sunLabel.sprite.position.copy(sunHandle.position).add(new Vector3(0, 0.05, 0));
}
let sunGrabbed = false;

// ---------- the overhang handle ----------
const handleMat = new MeshStandardMaterial({color: 0xb08a5c, roughness: 0.25, metalness: 0.85, emissive: new Color(0x6b4a24), emissiveIntensity: 0.4});
const overhangHandle = new Mesh(new SphereGeometry(0.02, 24, 16), handleMat);
const ohEntity = world.createTransformEntity(overhangHandle);
ohEntity.addComponent(RayInteractable);
ohEntity.addComponent(DistanceGrabbable, {movementMode: MovementMode.MoveAtSource, translate: true, rotate: false, scale: false});
const OH_GRIP = {x: 0.5, y: 0.6, z: 0.45};
const ohHome = (depth: number) => siteToWorld([OH_GRIP.x, LAYOUT.room.h + OH_GRIP.y, LAYOUT.room.z1 + depth + OH_GRIP.z]);
function setOverhangFrom(local: Vector3) {
  if (!level.overhang) return;
  const raw = local.z - LAYOUT.room.z1 - OH_GRIP.z;
  const v = +Math.min(2.4, Math.max(0, Math.round(raw / 0.6) * 0.6)).toFixed(2);
  if (v !== design.overhang) {
    design.overhang = v;
    clickSound();
    refresh();
  }
}

// ---------- the play-the-day button on the ledge ----------
const playButton = new Mesh(new CylinderGeometry(0.022, 0.024, 0.012, 32), handleMat);
playButton.position.copy(model.desk.localToWorld(new Vector3(0.8, 0.006, -0.17)));
const playEntity = world.createTransformEntity(playButton);
playEntity.addComponent(RayInteractable);

// ---------- evaluate and redraw ----------
function beamFor(id: string, colour: number) {
  let b = beams.get(id);
  if (!b) {
    b = new Beam(colour, colour === 0xa2452e ? 0.07 : 0.06);
    beams.set(id, b);
    model.site.add(b.group);
  }
  return b;
}
function labelFor(id: string) {
  let l = labels.get(id);
  if (!l) {
    l = new Label();
    l.sprite.scale.multiplyScalar(1 / SCALE);
    l.sprite.raycast = () => {};
    labels.set(id, l);
    model.site.add(l.sprite);
  }
  return l;
}

function drawResult(r: RuleResult, k: number) {
  const look = r.look;
  const who = r.rule.who;
  const isSun = who === 'sun' || who === 'wind' || who === 'rain';
  const b = beamFor(r.rule.id, who === 'sun' ? 0xf2b84b : who === 'wind' ? 0xffffff : who === 'rain' ? 0x6fa8ff : 0xa2452e);
  b.group.visible = true;
  if (isSun) {
    const f = who === 'sun' ? 11 / 60 : 9 / 40; // the last stretch of the ray, so it stays on the model
    const from = [0, 1, 2].map((i) => look.to[i] + (look.from[i] - look.to[i]) * f) as typeof look.from;
    b.set(from, look.to, look.sees ? 1 : Math.max(0, (look.t - (1 - f)) / f));
  } else b.set(look.from, look.to, look.t);
  const l = labelFor(r.rule.id);
  l.sprite.visible = true;
  const t = TARGETS[r.rule.target].at;
  l.sprite.position.set(t[0], t[1] + 2.4 + k * 1.1, t[2]);
  const word =
    who === 'sun'
      ? look.sees
        ? `SUN ${clock(r.rule.hour)}`
        : `SHADE ${clock(r.rule.hour)}`
      : who === 'wind'
        ? look.sees
          ? 'WINDY'
          : 'SHELTERED'
        : who === 'rain'
          ? look.sees
            ? 'WET'
            : 'DRY'
          : look.sees
            ? 'SEEN'
            : 'PRIVATE';
  l.set(word, who === 'sun' ? (look.sees ? 'sun' : 'shade') : isSun ? (look.sees ? 'cross' : 'check') : look.sees ? 'eye' : 'eye-off', r.pass);
}

function refresh() {
  setOverhang(model, design.overhang);
  const res = evaluateLevel(level, design);
  const was = solved;
  solved = res.solved;
  stars = res.stars;
  card.draw(levelIndex, level, res.results, solved);
  hud.level(levelIndex, LEVELS.length, level, res.results, solved, {used: design.pieces.length, par: level.par, stars, best: bestStars(level.id)});
  for (const b of beams.values()) b.group.visible = false;
  for (const l of labels.values()) l.sprite.visible = false;
  const perTarget = new Map<string, number>();
  for (const r of res.results) {
    const k = perTarget.get(r.rule.target) ?? 0;
    perTarget.set(r.rule.target, k + 1);
    drawResult(r, k);
  }
  const winRules = res.results.filter((r) => r.rule.who === 'window');
  const terrRules = res.results.filter((r) => r.rule.who === 'terrace');
  neighbourAtWindow.visible = winRules.length > 0 || COUNTRY.id === 'ph';
  neighbourOnTerrace.visible = terrRules.length > 0;
  waving.window = winRules.some((r) => r.look.sees);
  waving.terrace = terrRules.some((r) => r.look.sees);
  waving.local = res.results.some((r) => (r.rule.who === 'tower' || r.rule.who === 'boat') && r.look.sees);
  overhangHandle.visible = level.overhang;
  if (solved && !was) {
    solveSound();
    saveStars(level.id, stars);
  }
  console.info('[VR] design', JSON.stringify(design), 'level', level.id, 'solved', solved, 'stars', stars);
  (window as any).VR.state = {level: level.id, design: JSON.parse(JSON.stringify(design)), solved, stars, step: tutorial.stepId(), results: res.results.map((r) => ({id: r.rule.id, pass: r.pass, blocker: r.look.blocker}))};
}
const waving = {window: false, terrace: false, local: false};

function bestStars(id: string): number {
  try {
    return Number(localStorage.getItem(`valora-stars-${id}`) ?? 0);
  } catch {
    return 0;
  }
}
function saveStars(id: string, n: number) {
  try {
    if (n > bestStars(id)) localStorage.setItem(`valora-stars-${id}`, String(n));
  } catch {
    /* storage can be unavailable; stars are a convenience */
  }
}

// ---------- live the day: a time-lapse from morning to evening ----------
type Moment = {hour: number; result: RuleResult};
const day = {on: false, t: 0, moments: [] as Moment[], next: 0, pauseUntil: 0, hour: 7};
function startDay(now: number) {
  if (day.on) return;
  const moments = level.rules.map((rule) => ({hour: rule.hour ?? 12, result: evaluate(rule, design)})).sort((a, b) => a.hour - b.hour);
  Object.assign(day, {on: true, t: now, moments, next: 0, pauseUntil: 0, hour: 7});
  hud.say('Living the day…', '');
  chimeSound();
  console.info('[VR] day start');
}
function tickDay(now: number, dt: number) {
  if (!day.on) return;
  if (now < day.pauseUntil) return;
  const m = day.moments[day.next];
  if (m && day.hour >= m.hour) {
    // a moment of the day: the resident steps in, the watcher looks, the stamp lands
    const t = TARGETS[m.result.rule.target].at;
    resident.visible = true;
    resident.position.set(t[0] + 0.5, m.result.rule.target === 'pool' ? -0.2 : 0.05, t[2] + 0.4);
    if (m.result.rule.target === 'seat') resident.position.set(t[0], 0.05, t[2] + 0.5);
    for (const b of beams.values()) b.group.visible = false;
    for (const l of labels.values()) l.sprite.visible = false;
    drawResult(m.result, 0);
    hud.say(`${clock(m.hour)}: ${m.result.rule.text}`, m.result.pass ? 'Works' : 'Not yet');
    (m.result.pass ? clickSound : chimeSound)();
    day.next++;
    day.pauseUntil = now + 1.6;
    return;
  }
  day.hour += dt * 1.1; // about ten seconds for the day
  setHour(Math.round(day.hour * 4) / 4);
  if (day.hour > 18.6 && day.next >= day.moments.length) {
    day.on = false;
    resident.visible = false;
    refresh();
    const ok = day.moments.every((x) => x.result.pass);
    hud.say(ok ? `The house works all day. ${'★'.repeat(stars)}${'☆'.repeat(3 - stars)}` : 'Not quite. Move a piece and live the day again.', ok ? 'Click Tiki for the next level' : '');
    if (ok) tiki.celebrate();
    console.info('[VR] day end', ok);
  }
}

// ---------- the tutorial ----------
class Tutorial {
  private steps: Step[] = [];
  private i = 0;
  private enteredAt = 0;
  start(levelIdx: number) {
    this.steps = scriptFor(COUNTRY, levelIdx, LEVELS[levelIdx], firstLevelPlayed);
    firstLevelPlayed = false;
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
    if (!st) {
      hud.say('', '');
      return tiki.hide();
    }
    this.sayNow(now);
    tiki.look(lookAt(st.look));
    if (st.celebrate) tiki.celebrate();
  }
  sayNow(now: number) {
    const st = this.steps[this.i];
    if (!st) return;
    const text = forDevice(st.say);
    const hint = forDevice(st.hint ?? (st.until === 'tap' ? 'Pinch Tiki to continue' : ''));
    setFlatView(!inXR());
    tiki.say(text, hint, now);
    hud.say(text, hint);
  }
  next(now: number) {
    const st = this.steps[this.i];
    if (st?.then === 'next-level') return advance();
    this.i++;
    this.enter(now);
  }
  tick(now: number, tapped: boolean) {
    const st = this.steps[this.i];
    if (!st) {
      if (tapped && solved) advance();
      return;
    }
    if (now - this.enteredAt < 0.4) return;
    if (st.until === 'tap' && tapped) this.next(now);
    else if (st.until === 'solved' && solved && !day.on) this.next(now);
  }
}

function lookAt(l: Look | undefined): Vector3 | null {
  switch (l) {
    case 'window':
      return siteToWorld(LAYOUT.neighbour.window);
    case 'tower':
    case 'boat': {
      const p = eyePoints(l)[0];
      return p ? siteToWorld(p) : null;
    }
    case 'seat':
    case 'plant':
    case 'pool':
    case 'table':
    case 'deck':
      return siteToWorld(TARGETS[l].at);
    case 'tray':
      return model.desk.localToWorld(new Vector3(0.86, 0.03, 0.1));
    case 'sun':
      return sunHandle.getWorldPosition(new Vector3());
    case 'overhang':
      return overhangHandle.getWorldPosition(new Vector3());
    case 'play':
      return playButton.getWorldPosition(new Vector3());
    default:
      return null;
  }
}

const tutorial = new Tutorial();

/** After a level: the next one in this country, or the first level of the next country. */
function advance() {
  if (levelIndex + 1 < LEVELS.length) return goToLevel(levelIndex + 1);
  const next = COUNTRIES[(COUNTRIES.findIndex((c) => c.id === COUNTRY.id) + 1) % COUNTRIES.length];
  goToCountry(next.id, 0);
}

function goToCountry(id: typeof COUNTRY.id, i = 0) {
  setCountry(id);
  local.set(COUNTRY);
  goToLevel(i);
}

function goToLevel(i: number) {
  hud.country(COUNTRY.name);
  levelIndex = i;
  level = LEVELS[i];
  design.overhang = 0;
  design.pieces = [];
  solved = false;
  day.on = false;
  resident.visible = false;
  buildTray();
  syncDesign();
  const firstSun = level.rules.find((r) => r.who === 'sun');
  viewHour = -1;
  setHour(firstSun?.hour ?? 10);
  refresh();
  chimeSound();
  tutorial.start(i);
  history.replaceState(null, '', `?country=${COUNTRY.id}&level=${i + 1}`);
  hud.country(COUNTRY.name);
}

// ---------- test and debug hooks ----------
const toScreen = (v: Vector3) => {
  v.project(world.camera);
  return {x: ((v.x + 1) / 2) * innerWidth, y: ((1 - v.y) / 2) * innerHeight};
};
(window as any).VR = {
  state: {},
  stats() {
    const i = world.renderer.info;
    return {calls: i.render.calls, triangles: i.render.triangles, textures: i.memory.textures, geometries: i.memory.geometries};
  },
  setLevel: (i: number) => goToLevel(i),
  setCountry: (id: string, i = 0) => goToCountry(id as typeof COUNTRY.id, i),
  tapTiki() {
    pendingTap = true;
  },
  /** Put pieces straight onto sockets (tests): [{kind, socket, rot}] */
  place(ps: Placed[], overhang = 0) {
    for (const o of pieceObjs) homeInTray(o);
    for (const p of ps) {
      const o = pieceObjs.find((x) => x.kind === p.kind && x.socket < 0);
      if (!o) continue;
      o.rot = p.rot;
      placeAt(o, p.socket);
    }
    design.overhang = overhang;
    syncDesign();
    refresh();
  },
  live: () => startDay(lastTime),
  setHour: (h: number) => setHour(h),
  siteToScreen: (p: number[]) => toScreen(siteToWorld(p)),
  worldToScreen: (p: number[]) => toScreen(new Vector3(p[0], p[1], p[2])),
  pieceScreen: (kind: Kind, n = 0) => {
    const o = pieceObjs.find((x) => x.kind === kind && x.n === n);
    return o ? toScreen(o.root.position.clone()) : null;
  },
  socketScreen: (i: number) => toScreen(siteToWorld(SOCKETS[i])),
  worldPos(name: 'tiki' | 'sun' | 'overhang') {
    const o = name === 'tiki' ? tiki.hit : name === 'sun' ? sunHandle : overhangHandle;
    return o.getWorldPosition(new Vector3()).toArray();
  },
};
let pendingTap = false;
let lastTime = 0;
local.set(COUNTRY);
goToLevel(levelIndex);
if (!startCountry) hud.showMap(COUNTRIES.map((c) => ({id: c.id, name: c.name, place: c.place, house: c.house})));

// ---------- play on a screen with a mouse or touch ----------
// Outside an immersive session the hand-ray system has nothing to drive, so the page pointer does
// the same jobs. IWSDK's input layer stops pointer events before they reach the canvas, so listen on
// the window in the capture phase. In a headset this stands aside.
const canvas = world.renderer.domElement;
const flat = {ray: new Raycaster(), ndc: new Vector2(), plane: new Plane(), hit: new Vector3(), up: new Vector3(0, 1, 0), drag: null as null | PieceObj | 'sun' | 'overhang', downAt: 0, downX: 0, downY: 0};
function inXR() {
  return world.renderer.xr.isPresenting;
}
const within = (o: Object3D | null, root: Object3D) => {
  for (; o; o = o.parent) if (o === root) return true;
  return false;
};
function aimFlat(e: PointerEvent) {
  const r = canvas.getBoundingClientRect();
  flat.ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
  flat.ray.setFromCamera(flat.ndc, world.camera);
}
const pickables = () => [tiki.hit, sunHandle, playButton, ...(level.overhang ? [overhangHandle] : []), ...pieceObjs.map((o) => o.root)];
window.addEventListener('pointerdown', (e) => {
  if (e.target !== canvas || inXR()) return;
  aimFlat(e);
  const h = flat.ray.intersectObjects(pickables(), true)[0];
  if (!h) return;
  if (within(h.object, tiki.hit)) return void (pendingTap = true);
  if (within(h.object, playButton)) return startDay(lastTime);
  flat.downAt = lastTime;
  flat.downX = e.clientX;
  flat.downY = e.clientY;
  if (within(h.object, sunHandle)) flat.drag = 'sun';
  else if (within(h.object, overhangHandle)) {
    flat.drag = 'overhang';
    flat.plane.setFromNormalAndCoplanarPoint(flat.up, h.point);
  } else {
    const o = pieceObjs.find((x) => within(h.object, x.root));
    if (!o) return;
    flat.drag = o;
    o.held = true;
    o.heldAt = lastTime;
    o.heldFrom.copy(o.root.position);
    // drag across the board's surface
    flat.plane.setFromNormalAndCoplanarPoint(flat.up, model.desk.localToWorld(new Vector3(0, 0.0, 0)));
  }
  canvas.setPointerCapture(e.pointerId);
  canvas.style.cursor = 'grabbing';
  e.preventDefault();
}, true);
window.addEventListener('pointermove', (e) => {
  if (inXR() || (e.target !== canvas && !flat.drag)) return;
  aimFlat(e);
  if (!flat.drag) {
    canvas.style.cursor = flat.ray.intersectObjects(pickables(), true).length ? 'pointer' : '';
    return;
  }
  if (flat.drag === 'sun') return setHour(hourNearestRay(flat.ray.ray));
  if (!flat.ray.ray.intersectPlane(flat.plane, flat.hit)) return;
  if (flat.drag === 'overhang') return setOverhangFrom(model.site.worldToLocal(flat.hit.clone()));
  const o = flat.drag;
  o.root.position.copy(flat.hit).add(new Vector3(0, 0.01, 0));
  hover(o);
}, true);
function endFlat(e: PointerEvent) {
  const d = flat.drag;
  flat.drag = null;
  canvas.style.cursor = '';
  if (!d || d === 'sun' || d === 'overhang') return;
  d.held = false;
  // a click without movement turns a placed piece (judged by the pointer, not the clock, so a
  // slow frame never turns a click into a drag)
  if (Math.hypot(e.clientX - flat.downX, e.clientY - flat.downY) < 6) {
    d.root.position.copy(d.heldFrom);
    ghost.visible = false;
    if (d.socket >= 0) return rotate(d);
  }
  release(d, lastTime);
}
window.addEventListener('pointerup', endFlat, true);
window.addEventListener('pointercancel', endFlat, true);

/** On a flat screen the page overlay carries the words; in the headset the room does. */
function setFlatView(flatView: boolean) {
  hud.visible = flatView;
  card.mesh.visible = !flatView;
  tiki.bubbleShown = !flatView;
}
world.renderer.xr.addEventListener('sessionstart', () => tutorial.sayNow(0));
world.renderer.xr.addEventListener('sessionend', () => tutorial.sayNow(0));
hud.onPlay = () => startDay(lastTime);
hud.onReset = () => {
  for (const o of pieceObjs) homeInTray(o);
  design.overhang = 0;
  syncDesign();
  refresh();
};
hud.onLevel = (i: number) => goToLevel(i);
hud.onCountry = (id: string) => goToCountry(id as typeof COUNTRY.id, 0);
hud.onMap = () => hud.showMap(COUNTRIES.map((c) => ({id: c.id, name: c.name, place: c.place, house: c.house})));

/** Tiki's words for the device in use: pinch in a headset, click or drag on a screen. */
function forDevice(text: string): string {
  if (inXR()) return text;
  return text.replace(/Pinch and drag/g, 'Drag').replace(/pinch and drag/g, 'drag').replace(/Pinch/g, 'Click').replace(/pinch/g, 'click');
}

// ---------- per frame ----------
class PlaySystem extends createSystem({}) {
  private wasPressed = false;
  private wasPlay = false;
  private head = new Vector3();
  private tmp = new Vector3();
  update(delta: number, time: number) {
    lastTime = time;
    const xr = inXR();
    const k = 1 - Math.exp(-delta * 14);

    // pieces: hands hold them in XR, the mouse holds them on a screen; otherwise they spring home
    for (const o of pieceObjs) {
      const grabbed = xr && o.entity.hasComponent(Grabbed);
      if (grabbed && !o.held) {
        o.held = true;
        o.heldAt = time;
        o.heldFrom.copy(o.root.position);
      }
      if (o.held && xr && !grabbed) {
        o.held = false;
        release(o, time);
      }
      const full = o.held || o.socket >= 0;
      o.root.scale.setScalar(o.root.scale.x + ((full ? SCALE : SCALE * TRAY_SCALE) - o.root.scale.x) * k);
      if (o.held) {
        hover(o);
        o.root.rotation.y += (o.yaw - o.root.rotation.y) * k;
        continue;
      }
      o.root.position.lerp(o.target, k);
      o.root.rotation.y += (o.yaw - o.root.rotation.y) * k;
    }

    // the sun
    const sg = xr && sunEntity.hasComponent(Grabbed);
    if (sg) setHour(hourNearest(sunHandle.position));
    if (sunGrabbed && !sg) arcPoint(viewHour, sunHandle.position);
    sunGrabbed = sg;
    sunRing.rotation.z = time * 0.6;
    sunRing.scale.setScalar(1 + 0.08 * Math.sin(time * 2));

    // the overhang
    const og = xr && ohEntity.hasComponent(Grabbed);
    if (og) setOverhangFrom(model.site.worldToLocal(overhangHandle.getWorldPosition(this.tmp)));
    shownOverhang += (design.overhang - shownOverhang) * k;
    setOverhang(model, shownOverhang);
    if (!og) overhangHandle.position.copy(ohHome(shownOverhang));
    handleMat.emissiveIntensity = 0.4 + 0.25 * Math.sin(time * 2.5);

    // the play button
    const play = playEntity.hasComponent(Pressed);
    if (play && !this.wasPlay) startDay(time);
    this.wasPlay = play;
    tickDay(time, delta);

    // the neighbours wave when they can see what they should not
    const wave = (g: Group, on: boolean) => {
      const arm = g.getObjectByName('arm');
      if (arm) arm.rotation.z = on ? 2.6 + 0.4 * Math.sin(time * 9) : 0.1;
    };
    wave(neighbourAtWindow, waving.window);
    for (const f of local.figures()) wave(f as Group, waving.local);
    local.update(time);
    wave(neighbourOnTerrace, waving.terrace);

    WIND.value = time;
    motes.update(delta, time);
    clouds.update(delta);
    for (const b of beams.values()) b.pulse(time, !solved);

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
