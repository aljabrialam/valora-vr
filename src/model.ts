// The architectural model on the desk. Built from the same LAYOUT and boxes the checks
// use, so what you see is exactly what the watchers test against.

import {
  BoxGeometry,
  CircleGeometry,
  Color,
  CylinderGeometry,
  Group,
  Mesh,
  MeshStandardMaterial,
  PlaneGeometry,
  SphereGeometry,
  type Material,
} from 'three';
import {fixedBoxes, LAYOUT} from './sim/world.ts';
import type {Box, V3} from './sim/geom.ts';

/** 1:25 scale: the 17 m site becomes a 68 cm model, within easy seated reach. */
export const SCALE = 1 / 25;
/** Where real-world (0,0,0) of the site sits on the desk, in model metres before scaling. */
export const SITE_CENTRE: V3 = [3.4, 0, -1.6];

export const DESK = {y: 0.74, z: -0.52, w: 1.3, d: 0.78};

const mat = (hex: number, rough = 0.85, extra: Partial<MeshStandardMaterial> = {}) =>
  Object.assign(new MeshStandardMaterial({color: new Color(hex), roughness: rough, metalness: 0}), extra);

export const MATERIALS = {
  walnut: mat(0x4a3426, 0.55),
  basswood: mat(0xe9dfcb, 0.9),
  // the roof is lifted to a ghost so you can see the reading chair (the full lift-off comes later)
  roof: mat(0xe9dfcb, 0.9, {transparent: true, opacity: 0.22, depthWrite: false}),
  card: mat(0xcfc8bb, 0.95),
  neighbour: mat(0xc8a487, 0.95),
  courtyard: mat(0xd9cdb4, 0.95),
  lawn: mat(0x8d9b6a, 1),
  teak: mat(0xa06a3e, 0.6),
  glass: mat(0xbfd6dc, 0.1, {transparent: true, opacity: 0.28, depthWrite: false}),
  window: mat(0xf3d9a4, 0.4, {emissive: new Color(0xf0c674), emissiveIntensity: 0.6}),
  leaf: mat(0x5f7a3c, 0.9),
  pot: mat(0xb9784f, 0.8),
  chair: mat(0x7c8a92, 0.7),
};

function boxMesh(b: Box, m: Material): Mesh {
  const mesh = new Mesh(new BoxGeometry(b.h[0] * 2, b.h[1] * 2, b.h[2] * 2), m);
  mesh.position.set(b.c[0], b.c[1], b.c[2]);
  mesh.rotation.y = b.yaw;
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

export type Model = {
  desk: Group; // the desk and everything on it, in world metres
  site: Group; // the site in real metres, scaled down onto the desk
  screen: Group; // pivots about the screen hinge
  screenPanel: Mesh;
  overhang: Mesh;
  marks: {seat: Mesh; plant: Group; window: Mesh};
  roof: Mesh | null;
};

export function buildModel(): Model {
  const desk = new Group();
  desk.name = 'desk';
  desk.position.set(0, DESK.y, DESK.z);

  // the desk top, with a soft edge so it reads as furniture, not a plane
  const top = new Mesh(new BoxGeometry(DESK.w, 0.04, DESK.d), MATERIALS.walnut);
  top.position.y = -0.02;
  top.receiveShadow = true;
  desk.add(top);

  const site = new Group();
  site.name = 'site';
  site.scale.setScalar(SCALE);
  site.position.set(-SITE_CENTRE[0] * SCALE, 0.002, -SITE_CENTRE[2] * SCALE);
  desk.add(site);

  // base board under the whole site
  const base = new Mesh(new BoxGeometry(19, 0.2, 13), MATERIALS.basswood);
  base.position.set(3.4, -0.1, -1.6);
  base.receiveShadow = true;
  site.add(base);

  const {room: r, court: c} = LAYOUT;
  const courtFloor = new Mesh(new PlaneGeometry(c.x1 - c.x0, c.z1 - c.z0), MATERIALS.courtyard);
  courtFloor.rotation.x = -Math.PI / 2;
  courtFloor.position.set((c.x0 + c.x1) / 2, 0.02, (c.z0 + c.z1) / 2);
  courtFloor.receiveShadow = true;
  site.add(courtFloor);
  const lawn = new Mesh(new PlaneGeometry(4.2, 2.6), MATERIALS.lawn);
  lawn.rotation.x = -Math.PI / 2;
  lawn.position.set(-2.4, 0.04, 2.2);
  lawn.receiveShadow = true;
  site.add(lawn);

  let roof: Mesh | null = null;
  for (const b of fixedBoxes()) {
    const m = b.id === 'neighbour house' ? MATERIALS.neighbour : b.id === 'roof' ? MATERIALS.roof : MATERIALS.card;
    const mesh = boxMesh(b, m);
    if (b.id === 'roof') roof = mesh;
    site.add(mesh);
  }

  // courtyard glass along the room's south face (does not block the watchers)
  const glass = new Mesh(new PlaneGeometry(r.x1 - r.x0 - 0.3, r.h - 0.05), MATERIALS.glass);
  glass.position.set((r.x0 + r.x1) / 2, r.h / 2, r.z1);
  site.add(glass);

  // the reading chair, with its sitter's eye marked by the target point
  const chair = new Group();
  const seatBox = new Mesh(new BoxGeometry(0.8, 0.45, 0.8), MATERIALS.chair);
  seatBox.position.y = 0.225;
  const back = new Mesh(new BoxGeometry(0.8, 0.6, 0.15), MATERIALS.chair);
  back.position.set(0, 0.7, -0.33);
  for (const m of [seatBox, back]) {
    m.castShadow = true;
    m.receiveShadow = true;
    chair.add(m);
  }
  chair.position.set(LAYOUT.seat[0], 0, LAYOUT.seat[2] - 0.15);
  site.add(chair);
  const seatMark = new Mesh(new SphereGeometry(0.16, 20, 14), mat(0xffffff, 0.3, {emissive: new Color(0xffffff), emissiveIntensity: 0.25}));
  seatMark.position.set(...LAYOUT.seat);
  site.add(seatMark);

  // the courtyard plant
  const plant = new Group();
  const pot = new Mesh(new CylinderGeometry(0.28, 0.22, 0.4, 20), MATERIALS.pot);
  pot.position.y = 0.2;
  const leaves = new Mesh(new SphereGeometry(0.42, 20, 14), MATERIALS.leaf);
  leaves.position.y = 0.62;
  leaves.scale.set(1, 0.8, 1);
  for (const m of [pot, leaves]) {
    m.castShadow = true;
    m.receiveShadow = true;
    plant.add(m);
  }
  plant.position.set(LAYOUT.plant[0], 0, LAYOUT.plant[2]);
  site.add(plant);

  // the neighbour's window, lit warm so it reads as "someone is there"
  const nw = LAYOUT.neighbour.window;
  const win = new Mesh(new PlaneGeometry(1.4, 1.2), MATERIALS.window);
  win.position.set(LAYOUT.neighbour.house.x0 + 0.29, nw[1], nw[2]);
  win.rotation.y = -Math.PI / 2;
  site.add(win);

  // the privacy screen: a teak panel hinged at its pivot
  const {screen: s} = LAYOUT;
  const screen = new Group();
  screen.name = 'screen';
  screen.position.set(s.pivot[0], 0, s.pivot[2]);
  const panel = new Mesh(new BoxGeometry(s.len, s.h, s.t), MATERIALS.teak);
  panel.position.set(s.len / 2, s.h / 2, 0);
  panel.castShadow = true;
  panel.receiveShadow = true;
  screen.add(panel);
  const hinge = new Mesh(new CylinderGeometry(0.1, 0.1, s.h + 0.1, 16), MATERIALS.walnut);
  hinge.position.y = s.h / 2;
  screen.add(hinge);
  site.add(screen);

  // the overhang (depth set by the game)
  const overhang = new Mesh(new BoxGeometry(r.x1 - r.x0 + 0.4, 0.16, 1), MATERIALS.basswood);
  overhang.castShadow = true;
  overhang.receiveShadow = true;
  overhang.visible = false;
  site.add(overhang);

  // a soft contact shadow under the base so the model sits on the desk
  const contact = new Mesh(new CircleGeometry(0.5, 32), mat(0x000000, 1, {transparent: true, opacity: 0.18, depthWrite: false}));
  contact.rotation.x = -Math.PI / 2;
  contact.position.y = 0.001;
  contact.scale.set(1.1, 0.75, 1);
  desk.add(contact);

  return {desk, site, screen, screenPanel: panel, overhang, marks: {seat: seatMark, plant, window: win}, roof};
}

export function setOverhang(model: Model, depth: number) {
  const {room: r} = LAYOUT;
  model.overhang.visible = depth > 0.01;
  model.overhang.scale.z = Math.max(depth, 0.01);
  model.overhang.position.set((r.x0 + r.x1) / 2, r.h + 0.08, r.z1 + depth / 2);
}
