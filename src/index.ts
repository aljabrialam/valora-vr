// VaLora: Two Watchers.
// A seated, hands-first puzzle on an architect's model. Two watchers look at the house: the sun,
// hour by hour, and the neighbour next door. Pick pieces from the tray (screen, tree, pergola,
// hedge), set them in the courtyard, drag the sun across the sky to see the shadows move, then
// live the day and see if the house works. Fewer pieces earn more stars. Every check is the same
// geometry the prover runs (src/sim/play.ts, scripts/prove2.ts).

import {
  Box3,
  Quaternion,
  type PerspectiveCamera,
  ConeGeometry,
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
import {buildModel, DESK, GARDEN, GARDEN_PH, GARDEN_SAFE, SCALE, setOverhang, WIND} from './model.ts';
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
// The old swinging screen: screens are now pieces from the raft. Removed, not just hidden, because a
// hidden mesh still catches hand rays and would block pinches on pieces behind it.
model.screen.removeFromParent();
const deskEntity = world.createTransformEntity(model.desk);
loadPlant(1.15).then((p) => model.marks.plant.add(p)).catch((e) => console.warn('[VR] plant', e));
// Each country has its own island and house where one has been modelled; the shared ones stand in.
const OWN_HOUSE = new Set(['ph', 'th', 'vn', 'my', 'id', 'sg']);
/** Height of the visible garden wall or fence top, site metres (Tiki sits on it). */
const wallTop = (id: string) => (OWN_HOUSE.has(id) ? COUNTRIES.find((c) => c.id === id)!.wallH : 2.24);
const countryArt: {island?: Group; house?: Group; trees?: Group; id?: string} = {};
function loadCountryArt(id: string) {
  if (countryArt.id === id) return;
  countryArt.id = id;
  loadIsland(id)
    .then((i) => {
      if (countryArt.id !== id) return;
      countryArt.island?.removeFromParent();
      countryArt.island = i;
      model.site.add(i);
    })
    .catch((e) => console.warn('[VR] island', e));
  loadTrees(id === 'ph' ? GARDEN_PH : OWN_HOUSE.has(id) ? GARDEN_SAFE : GARDEN)
    .then((t) => {
      if (countryArt.id !== id) return;
      countryArt.trees?.removeFromParent();
      countryArt.trees = t;
      model.site.add(t);
    })
    .catch((e) => console.warn('[VR] trees', e));
  loadHouse(id)
    .then((h) => {
      if (countryArt.id !== id) return;
      countryArt.house?.removeFromParent();
      countryArt.house = h;
      model.site.add(h);
      // a country house with its own roof and open veranda replaces the code-drawn ghost roof and glass
      const own = OWN_HOUSE.has(id);
      if (model.roof) model.roof.visible = !own;
      model.glass.visible = !own;
      // Thailand, Vietnam and Malaysia model the neighbour's ledge where the figure stands; the others keep the drawn one
      balcony.visible = id !== 'th' && id !== 'vn' && id !== 'my';
      placeTiki();
    })
    .catch((e) => console.warn('[VR] house', e));
}
loadCountryArt(COUNTRY.id);

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
card.mesh.position.set(-0.18, 0.5, -0.45); // headset: a little above eye height, beyond the board
const BUBBLE_AT = new Vector3(-0.18, DESK.y + 0.22, -0.25); // headset: Tiki's words, just below eye height
card.mesh.rotation.x = -10 * D;
model.desk.add(card.mesh);
const motes = new Motes(60);
model.desk.add(motes.points);

// ---------- Tiki ----------
const tiki = new Gecko();
// Tiki lives on the walls: he sits on the cap of the front garden wall, left of the gate gap, so he
// never stands inside a wall. (The baked garden walls are 2.2 m tall with a cap to 2.24 m.)
const TIKI_HOME = new Vector3();
function placeTiki() {
  model.desk.updateWorldMatrix(true, true);
  TIKI_HOME.copy(model.desk.worldToLocal(siteToWorld([-3.6, wallTop(COUNTRY.id), LAYOUT.court.z1 + LAYOUT.court.wallT / 2])));
  tiki.group.position.copy(TIKI_HOME);
}
tiki.group.scale.setScalar(0.62); // a gecko sized to the wall he lives on
placeTiki();
const tikiEntity = world.createTransformEntity(tiki.group, deskEntity);
tikiEntity.addComponent(RayInteractable);

// ---------- the tray: a walnut ledge on the front of the plinth ----------
// the tray is a little timber raft floating just in front of the island
const raft = new Group();
// a bamboo raft: poles lashed side by side over three cross poles, moored to two posts on the beach
{
  const tones = ['#d9b468', '#cfae63', '#e0bd72', '#c7a45c', '#bfa35a'];
  const poleGeo = new CylinderGeometry(0.0095, 0.0095, 1, 10);
  poleGeo.rotateZ(Math.PI / 2);
  for (let i = 0; i < 9; i++) {
    const len = 0.64 + ((i * 37) % 5) * 0.008;
    const m = new Mesh(poleGeo, new MeshStandardMaterial({color: tones[i % tones.length], roughness: 0.55}));
    m.scale.set(len, 1, 1);
    m.position.set(((i * 13) % 3) * 0.004 - 0.004, 0, -0.076 + i * 0.019);
    m.receiveShadow = m.castShadow = true;
    raft.add(m);
  }
  const cross = new CylinderGeometry(0.006, 0.006, 0.2, 8);
  cross.rotateX(Math.PI / 2);
  const dark = new MeshStandardMaterial({color: '#7a5631', roughness: 0.7});
  const rope = new MeshStandardMaterial({color: '#5b4128', roughness: 0.9});
  for (const x of [-0.27, 0, 0.27]) {
    const c = new Mesh(cross, dark);
    c.position.set(x, -0.011, 0);
    raft.add(c);
    const band = new Mesh(new BoxGeometry(0.012, 0.022, 0.18), rope);
    band.position.set(x, -0.002, 0);
    raft.add(band);
  }
}
// in front of the courtyard, nearest the seated player, so pieces are a short point away
const RAFT = new Vector3(-0.18, -0.006, 0.6);
raft.position.copy(RAFT);
model.desk.add(raft);
// mooring: two posts in the shallows behind the raft, with a rope to each end
{
  const post = new CylinderGeometry(0.007, 0.008, 0.08, 8);
  const wood = new MeshStandardMaterial({color: '#6b4428', roughness: 0.8});
  const rope = new MeshStandardMaterial({color: '#5b4128', roughness: 0.9});
  for (const sx of [-1, 1]) {
    const p = new Mesh(post, wood);
    p.position.set(RAFT.x + sx * 0.36, -0.02, RAFT.z - 0.13);
    p.castShadow = true;
    model.desk.add(p);
    const a = new Vector3(RAFT.x + sx * 0.36, 0.015, RAFT.z - 0.13);
    const b = new Vector3(RAFT.x + sx * 0.3, 0.0, RAFT.z - 0.07);
    const line = new Mesh(new CylinderGeometry(0.0018, 0.0018, a.distanceTo(b), 5), rope);
    line.position.copy(a).add(b).multiplyScalar(0.5);
    line.quaternion.setFromUnitVectors(new Vector3(0, 1, 0), b.clone().sub(a).normalize());
    model.desk.add(line);
  }
}
const KIND_ORDER: Kind[] = ['screen', 'hedge', 'tree', 'pergola'];
const TRAY_SCALE = 0.5; // pieces wait on the raft at half size
const traySlot = (kind: Kind, n: number) => new Vector3(RAFT.x - 0.225 + KIND_ORDER.indexOf(kind) * 0.15 + n * 0.014, 0.0, RAFT.z - n * 0.012);

// ---------- pieces: every copy in the tray is its own grabbable object ----------
const HIT_MAT = new MeshBasicMaterial({colorWrite: false, depthWrite: false});
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
  hand?: 'left' | 'right';
  grabOffset?: Vector3;
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
      const shape = pieceModel(kind);
      root.add(shape);
      // An invisible solid box around the shape: slatted screens and leafy trees have gaps a hand ray
      // slips through, so pinching anywhere on the piece should still catch it.
      shape.updateMatrixWorld(true);
      const bb = new Box3().setFromObject(shape);
      const hit = new Mesh(new BoxGeometry(...bb.getSize(new Vector3()).toArray()), HIT_MAT);
      bb.getCenter(hit.position);
      hit.name = 'hit';
      root.add(hit);
      root.scale.setScalar(SCALE * TRAY_SCALE);
      const entity = world.createTransformEntity(root);
      entity.addComponent(RayInteractable);
      entity.addComponent(DistanceGrabbable, {movementMode: MovementMode.MoveAtSource, translate: false, rotate: false, scale: false});
      const o: PieceObj = {kind, n, root, entity, socket: -1, rot: 0, target: new Vector3(), yaw: 0, held: false, heldAt: 0, heldFrom: new Vector3(), hand: undefined, grabOffset: new Vector3()};
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

/** A piece was let go: land on the nearest free socket, or go back to the tray. A pinch on a placed
 *  piece that barely moved it is a tap: it turns the piece. */
function release(o: PieceObj, now: number) {
  ghost.visible = false;
  const moved = o.root.position.distanceTo(o.heldFrom);
  console.info('[VR] release', o.kind, 'moved', moved.toFixed(3), 'held', (now - o.heldAt).toFixed(2));
  if (o.socket >= 0 && moved < 0.02) return rotate(o); // a pinch that does not move a placed piece turns it
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
sunEntity.addComponent(DistanceGrabbable, {movementMode: MovementMode.MoveAtSource, translate: false, rotate: false, scale: false});
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

let sunMoved = false; // set when the player drags the sun; the tutorial waits for it
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
playButton.position.copy(model.desk.localToWorld(new Vector3(RAFT.x + 0.4, 0.006, RAFT.z)));
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
  card.draw(levelIndex, level, res.results, solved, {used: design.pieces.length, par: level.par, stars});
  hud.level(levelIndex, LEVELS.length, level, res.results, solved, {used: design.pieces.length, par: level.par, stars, best: bestStars(level.id)});
  requestAnimationFrame(frameFlat);
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
  waving.local = res.results.some((r) => (r.rule.who === 'tower' || r.rule.who === 'boat' || r.rule.who === 'moto') && r.look.sees);
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
// ---------- the arrow: shows what to touch for the current tutorial step ----------
/** Video and stills: hide the tutorial arrow along with the page overlays (VR.chrome(false)). */
let hideGuides = false;
class Pointer {
  target: Look | null = null;
  readonly group = new Group();
  private at = new Vector3();
  constructor() {
    const mat = new MeshStandardMaterial({color: '#ff8a1f', emissive: '#ff6a00', emissiveIntensity: 0.6, roughness: 0.4});
    const head = new Mesh(new ConeGeometry(0.022, 0.045, 20), mat);
    head.rotation.x = Math.PI; // tip down
    const shaft = new Mesh(new CylinderGeometry(0.007, 0.007, 0.045, 12), mat);
    shaft.position.y = 0.045;
    for (const m of [head, shaft]) m.raycast = () => {};
    this.group.add(head, shaft);
    this.group.visible = false;
    world.scene.add(this.group);
  }
  update(time: number) {
    const p = this.target ? lookAt(this.target) : null;
    this.group.visible = !!p && !hideGuides;
    if (!p) return;
    this.at.copy(p);
    // ride above pieces and handles; bob so it catches the eye
    this.group.position.set(this.at.x, this.at.y + 0.09 + 0.02 * Math.sin(time * 5), this.at.z);
    this.group.rotation.y = time * 1.5;
  }
}
const pointer = new Pointer();

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
      pointer.target = null;
      return tiki.hide();
    }
    this.sayNow(now);
    sunMoved = false;
    tiki.look(st.look === 'tiki' ? null : lookAt(st.look)); // Tiki looks at what he talks about, not himself
    pointer.target = st.look ?? null;
    if (st.celebrate) tiki.celebrate();
  }
  sayNow(now: number) {
    const st = this.steps[this.i];
    if (!st) return;
    const text = forDevice(st.say);
    let hint = forDevice(st.hint ?? (st.until === 'tap' ? 'Pinch Tiki to continue' : ''));
    // VR mode in a computer browser is Meta's emulator: say how its controls stand in for hands
    if (inXR() && IN_EMULATOR()) hint = 'Emulator: drag a controller arrow to aim, then set Trig to 1 to pinch. Easier: exit VR and use the mouse.';
    setFlatView(!inXR());
    tiki.say(text, hint, now);
    // on a screen, Continue does the same as clicking Tiki, who may be small or off to one side
    hud.say(text, st.until === 'tap' ? hint.replace(/^Click Tiki to continue$/, 'Or click Tiki') : hint, st.until === 'tap');
    requestAnimationFrame(frameFlat);
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
    else if (st.until === 'placed' && design.pieces.length > 0) this.next(now);
    else if (st.until === 'sun' && sunMoved) this.next(now);
    else if (st.until === 'solved' && solved && !day.on) this.next(now);
  }
}

function lookAt(l: Look | undefined): Vector3 | null {
  switch (l) {
    case 'window':
      return siteToWorld(LAYOUT.neighbour.window);
    case 'tower':
    case 'boat':
    case 'moto': {
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
      return (pieceObjs.find((o) => o.socket < 0)?.root ?? raft).getWorldPosition(new Vector3());
    case 'sun':
      return sunHandle.getWorldPosition(new Vector3());
    case 'tiki':
      return tiki.hit.getWorldPosition(new Vector3());
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
  loadCountryArt(id);
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
  /** Video capture: drive the screen camera directly (null hands it back to the page layout). */
  cinema(shot: {pos: number[]; look: number[]; fov?: number} | null) {
    const cam = world.camera as PerspectiveCamera;
    cinemaOn = !!shot;
    if (!shot) return frameFlat();
    cam.clearViewOffset();
    cam.zoom = 1;
    if (shot.fov) cam.fov = shot.fov;
    cam.position.set(shot.pos[0], shot.pos[1], shot.pos[2]);
    cam.lookAt(shot.look[0], shot.look[1], shot.look[2]);
    cam.updateProjectionMatrix();
  },
  /** Video capture: show or hide the page panels and the Enter XR button. */
  chrome(show: boolean) {
    hud.visible = show;
    hideGuides = !show;
    document.querySelectorAll<HTMLElement>('button, a').forEach((b) => {
      if (/Enter XR/i.test(b.textContent ?? '')) b.style.visibility = show ? '' : 'hidden';
    });
  },
  rig: () => world.player.position.toArray(),
  /** Video capture: lean the seated player in (move the rig, in metres); returns the new rig position. */
  lean(dx: number, dy: number, dz: number) {
    world.player.position.add(new Vector3(dx, dy, dz));
    return world.player.position.toArray();
  },
  /** Video capture: recentre now (software rendering is too slow to wait for the frame count). */
  recentreNow() {
    recentreAt = -1;
    recentre(world.player.head.getWorldPosition(new Vector3()));
  },
  /** Video capture: tilt the seated view down by `deg` about the head (the emulator holds the head level). */
  tilt(deg: number) {
    const head = world.player.head.getWorldPosition(new Vector3());
    const q = new Quaternion().setFromAxisAngle(new Vector3(1, 0, 0), (-deg * Math.PI) / 180);
    world.player.position.sub(head).applyQuaternion(q).add(head);
    world.player.quaternion.premultiply(q);
    world.player.updateMatrixWorld(true);
  },
  /** Video capture: a world point in the player's rig space (where emulator poses live). */
  toRig: (p: number[]) => world.player.worldToLocal(new Vector3(p[0], p[1], p[2])).toArray(),
  pieceWorld(kind: Kind, n = 0) {
    const o = pieceObjs.find((x) => x.kind === kind && x.n === n);
    return o ? o.root.getWorldPosition(new Vector3()).toArray() : null;
  },
  socketWorld: (i: number) => siteToWorld(SOCKETS[i]).toArray(),
  boxOf(name: string) {
    const o = world.scene.getObjectByName(name);
    if (!o) return null;
    const b = new Box3().setFromObject(o);
    return {min: b.min.toArray().map((x) => +x.toFixed(3)), max: b.max.toArray().map((x) => +x.toFixed(3))};
  },
  pieceBox(kind: Kind, n = 0) {
    const o = pieceObjs.find((x) => x.kind === kind && x.n === n);
    if (!o) return null;
    const b = new Box3().setFromObject(o.root.getObjectByName('hit') ?? o.root);
    return {min: b.min.toArray().map((x) => +x.toFixed(3)), max: b.max.toArray().map((x) => +x.toFixed(3)), at: o.root.position.toArray().map((x) => +x.toFixed(3))};
  },
  rayHits(from: number[], to: number[]) {
    const r = new Raycaster(new Vector3(...from), new Vector3(...to).sub(new Vector3(...from)).normalize());
    return r.intersectObjects(world.scene.children, true).slice(0, 6).map((h) => {
      let o: Object3D | null = h.object;
      const path: string[] = [];
      while (o && path.length < 4) { if (o.name) path.push(o.name); o = o.parent; }
      return `${h.distance.toFixed(3)} ${h.object.type} ${path.join('<') || '(unnamed)'}`;
    });
  },
  socketScreen: (i: number) => toScreen(siteToWorld(SOCKETS[i])),
  worldPos(name: 'tiki' | 'sun' | 'overhang' | 'card') {
    const o = name === 'tiki' ? tiki.hit : name === 'sun' ? sunHandle : name === 'card' ? card.mesh : overhangHandle;
    return o.getWorldPosition(new Vector3()).toArray();
  },
};
let pendingTap = false;
let lastTime = 0;
local.set(COUNTRY);
goToLevel(levelIndex);
// Test anchors: world positions the emulator test aims hands at.
setTimeout(() => {
  const v = (o: Object3D) => o.getWorldPosition(new Vector3()).toArray().map((x) => +x.toFixed(4));
  console.info('[VR] anchors', JSON.stringify({
    tiki: v(tiki.hit), sun: v(sunHandle), play: v(playButton),
    pieces: pieceObjs.map((o) => ({kind: o.kind, n: o.n, at: v(o.root)})),
    sockets: SOCKETS.map((s) => siteToWorld(s).toArray().map((x) => +x.toFixed(4))),
  }));
}, 1500);
if (!startCountry) hud.showMap(COUNTRIES.map((c) => ({id: c.id, name: c.name, place: c.place, house: c.house})));


// ---------- seated hand rays ----------
// Held pieces and the sun follow where the hand points, not how far the hand travels, so a seated
// player covers the whole board with a small wrist turn instead of a long reach.
const handRay = {ray: new Raycaster().ray, dir: new Vector3(), to: new Vector3(), plane: new Plane(), hit: new Vector3(), lift: new Vector3(0, 0.01, 0)};
/** Point `handRay.ray` along whichever hand's target ray aims closest to `at`. */
function aimHandAt(at: Vector3, side?: 'left' | 'right'): 'left' | 'right' {
  let best: 'left' | 'right' = 'right';
  let bestCos = -2;
  for (const s of side ? [side] : (['left', 'right'] as const)) {
    const space = world.player.raySpaces[s];
    space.getWorldPosition(handRay.to);
    handRay.dir.set(0, 0, -1).transformDirection(space.matrixWorld);
    const c = handRay.dir.dot(handRay.to.subVectors(at, handRay.to).normalize());
    if (c > bestCos) {
      bestCos = c;
      best = s;
    }
  }
  const space = world.player.raySpaces[best];
  space.getWorldPosition(handRay.ray.origin);
  handRay.ray.direction.set(0, 0, -1).transformDirection(space.matrixWorld);
  return best;
}

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
  if (flat.drag === 'sun') {
    const h = hourNearestRay(flat.ray.ray);
    if (h !== viewHour) sunMoved = true;
    return setHour(h);
  }
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
  // headset: Tiki's words sit straight ahead just under the level card, where the eye already is
  if (flatView) tiki.anchorBubble(null);
  else tiki.anchorBubble(world.scene, BUBBLE_AT, 0.34);
  console.info('[VR] view', flatView ? 'flat' : 'headset');
}
hud.onPlay = () => startDay(lastTime);
hud.onNext = () => (pendingTap = true);
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
// A real headset browser, or Meta's emulator running in a computer browser.
// IWER (the emulator) reports a Quest user agent, so look for the device it installs instead.
const IN_EMULATOR = () => !!(window as any).IWER_DEVICE && !(window as any).__capture; // video capture labels footage itself
function forDevice(text: string): string {
  if (inXR()) return text;
  return text.replace(/Pinch and drag/g, 'Drag').replace(/pinch and drag/g, 'drag').replace(/Pinch/g, 'Click').replace(/pinch/g, 'click');
}

// ---------- per frame ----------

// ---------- fit the screen view into the space the page panels leave free ----------
// The level card sits on the left and Tiki's line along the bottom. Shift and widen the camera's view
// so the island and the raft land in the open area instead of behind the panels.
let cinemaOn = false;
function frameFlat() {
  const cam = world.camera as PerspectiveCamera;
  if (inXR() || cinemaOn) return;
  const W = innerWidth;
  const H = innerHeight;
  const a = hud.freeArea();
  const fit = Math.min((a.x1 - a.x0) / W, (a.y1 - a.y0) / H);
  cam.zoom = Math.min(1, Math.max(0.55, fit * 1.08));
  cam.setViewOffset(W, H, W / 2 - (a.x0 + a.x1) / 2, H / 2 - (a.y0 + a.y1) / 2, W, H);
  cam.updateProjectionMatrix();
}
addEventListener('resize', () => requestAnimationFrame(frameFlat));

// ---------- seated recentring ----------
// When a headset session starts, place the player just behind the courtyard so the board sits low in
// front of them, the raft at their lap and the level card at eye level. Done once per session: this is
// a recentre, not locomotion; nothing moves the player after it.
const SEAT_HEAD = new Vector3(-0.18, DESK.y + 0.3, 0.3);
let recentreAt = -1;
// counted in headset frames, not seconds: the session's frame clock can differ from the page's
world.renderer.xr.addEventListener('sessionstart', () => (recentreAt = 30));
world.renderer.xr.addEventListener('sessionend', () => {
  recentreAt = -1;
  world.player.position.set(0, 0, 0);
});
function recentre(head: Vector3) {
  world.player.position.add(new Vector3().subVectors(SEAT_HEAD, head));
  console.info('[VR] recentre', world.player.position.toArray().map((x) => +x.toFixed(3)).join(','));
}

class PlaySystem extends createSystem({}) {
  private wasPressed = false;
  private wasXR = false;
  private sunHand: 'left' | 'right' = 'right';
  private wasPlay = false;
  private head = new Vector3();
  private tmp = new Vector3();
  update(delta: number, time: number) {
    lastTime = time;
    const xr = inXR();
    // switch the words between the page (screen) and the world (headset) on the first frame that
    // actually renders in the new mode; session events can fire before presenting starts
    if (xr !== this.wasXR) {
      this.wasXR = xr;
      if (xr) {
        const cam = world.camera as PerspectiveCamera;
        cam.clearViewOffset();
        cam.zoom = 1;
        cam.updateProjectionMatrix();
      }
      tutorial.sayNow(time);
    }
    if (xr && recentreAt >= 0 && time >= recentreAt) {
      recentreAt = -1;
      recentre(world.player.head.getWorldPosition(this.tmp)); // the tracked head, not the page camera
    }
    pointer.update(time);
    const k = 1 - Math.exp(-delta * 14);

    // pieces: hands hold them in XR, the mouse holds them on a screen; otherwise they spring home
    for (const o of pieceObjs) {
      const grabbed = xr && o.entity.hasComponent(Grabbed);
      if (grabbed && !o.held) {
        o.held = true;
        o.heldAt = time;
        o.heldFrom.copy(o.root.position);
        o.hand = aimHandAt(o.root.position);
        handRay.plane.setFromNormalAndCoplanarPoint(handRay.lift.set(0, 1, 0), model.desk.localToWorld(handRay.hit.set(0, 0, 0)));
        // keep where the piece sat relative to the pointed spot, so a quick pinch does not make it jump
        if (handRay.ray.intersectPlane(handRay.plane, handRay.hit)) o.grabOffset!.subVectors(o.root.position, handRay.hit);
        else o.grabOffset!.set(0, 0.01, 0);
      }
      if (grabbed && o.hand) {
        aimHandAt(o.root.position, o.hand);
        if (handRay.ray.intersectPlane(handRay.plane, handRay.hit)) o.root.position.copy(handRay.hit).add(o.grabOffset!);
      }
      if (o.held && xr && !grabbed) {
        o.held = false;
        o.hand = undefined;
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
    if (sg) {
      aimHandAt(sunHandle.position, sunGrabbed ? this.sunHand : undefined);
      if (!sunGrabbed) {
        this.sunHand = aimHandAt(sunHandle.position);
        console.info('[VR] sun grab', viewHour);
      }
      const h = hourNearestRay(handRay.ray);
      if (h !== viewHour) sunMoved = true;
      setHour(h);
      arcPoint(viewHour, sunHandle.position);
    }
    if (sunGrabbed && !sg) {
      arcPoint(viewHour, sunHandle.position);
      console.info('[VR] sun release', viewHour);
    }
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
    (xr ? world.player.head : world.camera).getWorldPosition(this.head);
    tiki.update(delta, time, this.head);
    tutorial.tick(time, tapped);
  }
}
world.registerSystem(PlaySystem);
