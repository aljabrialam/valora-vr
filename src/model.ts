// The VaLora courtyard on the desk, dressed like the VaLora website: board-formed concrete, teak,
// timber deck, stone, a reflecting pool and tropical planting. Everything the watchers test against
// comes from the same LAYOUT and boxes as the checks, so what you see is what is checked.
// Plants are decoration only and are kept out of every sightline the levels use.

import {
  BoxGeometry,
  BufferAttribute,
  BufferGeometry,
  CanvasTexture,
  RepeatWrapping,
  CatmullRomCurve3,
  Color,
  CylinderGeometry,
  DoubleSide,
  Group,
  Mesh,
  MeshBasicMaterial,
  MeshPhysicalMaterial,
  MeshStandardMaterial,
  PlaneGeometry,
  SphereGeometry,
  SRGBColorSpace,
  TubeGeometry,
  Vector3,
  type Material,
} from '@iwsdk/core';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';
import * as TX from './look/textures.ts';
import {fixedBoxes, LAYOUT} from './sim/world.ts';
import type {Box} from './sim/geom.ts';

/** 1:18 scale: the site becomes a model about 95 cm across, all within seated reach. */
export const SCALE = 1 / 18;
/** The site point that sits over the middle of the desk, in site metres. */
export const SITE_CENTRE = new Vector3(3.2, 0, -1.4);
export const DESK = {y: 0.75, z: -0.56, w: 1.5, d: 0.92}; // y matches the baked room's table top

let seed = 7;
const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
const rr = (a: number, b: number) => a + (b - a) * rnd();

/** World-space UVs so every texture keeps its real-world size on any box. */
function worldUV(geo: BufferGeometry, offset = new Vector3()): BufferGeometry {
  const p = geo.attributes.position;
  const n = geo.attributes.normal;
  const uv = new Float32Array(p.count * 2);
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i) + offset.x;
    const y = p.getY(i) + offset.y;
    const z = p.getZ(i) + offset.z;
    if (Math.abs(n.getY(i)) > 0.5) {
      uv[i * 2] = x;
      uv[i * 2 + 1] = z;
    } else if (Math.abs(n.getX(i)) > 0.5) {
      uv[i * 2] = z;
      uv[i * 2 + 1] = y;
    } else {
      uv[i * 2] = x;
      uv[i * 2 + 1] = y;
    }
  }
  geo.setAttribute('uv', new BufferAttribute(uv, 2));
  return geo;
}

function slab(x0: number, x1: number, y0: number, y1: number, z0: number, z1: number): BufferGeometry {
  const g = new BoxGeometry(x1 - x0, y1 - y0, z1 - z0);
  g.translate((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2);
  return worldUV(g);
}

function boxGeo(b: Box): BufferGeometry {
  const g = new BoxGeometry(b.h[0] * 2, b.h[1] * 2, b.h[2] * 2);
  worldUV(g, new Vector3(b.c[0], b.c[1], b.c[2]));
  g.rotateY(b.yaw);
  g.translate(b.c[0], b.c[1], b.c[2]);
  return g;
}

function addMerged(parent: Group, mat: Material, geos: BufferGeometry[], cast = true, receive = true): Mesh | null {
  if (!geos.length) return null;
  const merged = mergeGeometries(geos, false);
  if (!merged) return null;
  const m = new Mesh(merged, mat);
  m.castShadow = cast;
  m.receiveShadow = receive;
  parent.add(m);
  return m;
}

const std = (o: ConstructorParameters<typeof MeshStandardMaterial>[0]) => new MeshStandardMaterial({roughness: 0.85, metalness: 0, ...o});

function buildMaterials() {
  const T = {
    concrete: TX.concrete(),
    roof: TX.roof(),
    slate: TX.slate(),
    deck: TX.deck(),
    stone: TX.stone(),
    grass: TX.grass(),
    oak: TX.oak(),
    frond: TX.frond(),
    broad: TX.foliage('broad'),
    mid: TX.foliage('mid'),
    fine: TX.foliage('fine'),
  };
  return {
    T,
    concrete: std({map: T.concrete, roughness: 0.92}),
    plaster: std({color: new Color('#d9cfbf'), roughness: 0.95}),
    roofGhost: std({map: T.roof, transparent: true, opacity: 0.18, depthWrite: false}),
    deck: std({map: T.deck, roughness: 0.75}),
    stone: std({map: T.stone, roughness: 0.8}),
    cork: std({map: cork(), roughness: 0.95}),
    oak: std({map: T.oak, roughness: 0.6}),
    slate: std({map: T.slate, roughness: 0.7}),
    teak: new MeshPhysicalMaterial({color: '#9c6a3f', roughness: 0.5, clearcoat: 0.25, clearcoatRoughness: 0.4}),
    fabric: std({color: '#d9d2c3', roughness: 0.95}),
    frame: std({color: '#2b2a28', roughness: 0.5, metalness: 0.3}),
    glass: new MeshPhysicalMaterial({color: '#dbe8ea', roughness: 0.02, metalness: 0, transparent: true, opacity: 0.2, depthWrite: false, clearcoat: 1, envMapIntensity: 1.6}),
    water: waterMaterial(),
    poolIn: std({color: '#2f4a4a', roughness: 0.5}),
    window: std({color: '#f7dfae', emissive: new Color('#f0c674'), emissiveIntensity: 1.4, roughness: 0.4}),
    pot: std({color: '#b9784f', roughness: 0.8}),
    trunk: std({color: '#7a6c5c', roughness: 0.95}),
    walnut: new MeshPhysicalMaterial({color: '#3a271c', roughness: 0.42, clearcoat: 0.5, clearcoatRoughness: 0.25}),
    // gallery presentation: an ebonised walnut top on a charcoal pedestal, a dark polished floor
    plinthTop: std({color: '#2a1d15', roughness: 0.75, envMapIntensity: 0.12}),
    pedestal: std({color: '#1b1a19', roughness: 0.9, envMapIntensity: 0.2}),
    floor: std({color: '#0d0c0b', roughness: 0.9, envMapIntensity: 0.15}),
    edge: std({color: '#efe9df', roughness: 0.9, envMapIntensity: 0.3}),
  };
}

export type Model = {
  desk: Group; // the desk and everything on it, in world metres
  site: Group; // the site in real metres, scaled down onto the desk
  screen: Group; // pivots about the screen hinge
  screenPanel: Mesh;
  lever: Group; // the bronze lever arm on the screen, which carries the handle's resting point
  overhang: Mesh;
  roof: Mesh | null;
  glass: Mesh;
  marks: {seat: Mesh; plant: Group; window: Mesh};
};

export function buildModel(): Model {
  const M = buildMaterials();
  const desk = new Group();
  desk.name = 'desk';
  desk.position.set(0, DESK.y, DESK.z);

  // Sunny floating island: the island itself is modelled in Blender (art/blender/island.py) and
  // loaded into the site group by src/look/assets.ts. Nothing else stands under the model.

  const site = new Group();
  site.name = 'site';
  site.scale.setScalar(SCALE);
  site.position.set(-SITE_CENTRE.x * SCALE, 0.001, -SITE_CENTRE.z * SCALE);
  desk.add(site);

  const {room: r, court: c, neighbour: n} = LAYOUT;
  const ground = {x0: -9.0, x1: 15.4, z0: -8.6, z1: 5.8}; // fits the plinth at 1:18

  // The static house (room, deck, paving, pool coping, walls, furniture, neighbour) is modelled and
  // baked in Blender (art/blender/house.py) and loaded by src/look/assets.ts into this group.
  // Code keeps only what moves, glows, is see-through, or is tiled: lawn, water, glass, ghost roof.
  void ground;
  const pool = {x0: -4.3, x1: -1.6, z0: 0.3, z1: 2.9};
  const water = new Mesh(new PlaneGeometry(pool.x1 - pool.x0, pool.z1 - pool.z0), M.water);
  water.rotation.x = -Math.PI / 2;
  water.position.set((pool.x0 + pool.x1) / 2, 0.06, (pool.z0 + pool.z1) / 2); // above the paving bed
  water.receiveShadow = true;
  site.add(water);
  let roof: Mesh | null = null;
  for (const b of fixedBoxes()) {
    if (b.id !== 'roof') continue;
    roof = new Mesh(boxGeo(b), M.roofGhost);
    roof.renderOrder = 2;
    site.add(roof);
  }
  const glass = new Mesh(new PlaneGeometry(r.x1 - r.x0 - 0.3, r.h - 0.15), M.glass);
  glass.position.set((r.x0 + r.x1) / 2, r.h / 2, r.z1);
  glass.renderOrder = 3;
  site.add(glass);

  const seatMark = new Mesh(new SphereGeometry(0.14, 20, 14), new MeshBasicMaterial({color: '#ffffff', transparent: true, opacity: 0.9}));
  seatMark.position.set(...LAYOUT.seat);
  site.add(seatMark);

  // the courtyard plant in a terracotta pot
  const plant = new Group();
  plant.position.set(LAYOUT.plant[0], 0.05, LAYOUT.plant[2]);
  site.add(plant);

  // the neighbour's window, lit warm with a dark frame, so it reads as "someone is there"
  const win = new Mesh(new PlaneGeometry(1.4, 1.2), M.window);
  win.position.set(n.house.x0 + 0.25, n.window[1], n.window[2]);
  win.rotation.y = -Math.PI / 2;
  site.add(win);

  // the privacy screen: a teak panel of vertical battens on a dark hinge, with a bronze lever
  const {screen: s} = LAYOUT;
  const screen = new Group();
  screen.name = 'screen';
  screen.position.set(s.pivot[0], 0, s.pivot[2]);
  const battens: BufferGeometry[] = [];
  for (let x = 0.12; x < s.len; x += 0.16) battens.push(slab(x - 0.055, x + 0.055, 0.05, s.h, -s.t / 2, s.t / 2));
  battens.push(slab(0.05, s.len, s.h - 0.1, s.h, -s.t / 2 - 0.02, s.t / 2 + 0.02));
  battens.push(slab(0.05, s.len, 0.05, 0.15, -s.t / 2 - 0.02, s.t / 2 + 0.02));
  const panel = addMerged(screen, M.teak, battens)!;
  const hinge = new Mesh(new CylinderGeometry(0.09, 0.09, s.h + 0.1, 16), M.frame);
  hinge.position.y = s.h / 2;
  hinge.castShadow = true;
  screen.add(hinge);
  const lever = new Group();
  lever.name = 'lever';
  const bronze = std({color: '#b08a5c', roughness: 0.28, metalness: 0.85});
  const armStart = new Vector3(s.len, s.h, 0);
  const armEnd = new Vector3(s.len + LEVER.reach, s.h + LEVER.rise, 0);
  const arm = new Mesh(new CylinderGeometry(0.05, 0.05, armStart.distanceTo(armEnd), 10), bronze);
  arm.position.copy(armStart).add(armEnd).multiplyScalar(0.5);
  arm.quaternion.setFromUnitVectors(new Vector3(0, 1, 0), armEnd.clone().sub(armStart).normalize());
  arm.castShadow = true;
  lever.add(arm);
  screen.add(lever);
  site.add(screen);

  // the overhang (depth set by the game)
  const overhang = new Mesh(new BoxGeometry(r.x1 - r.x0 + 0.4, 0.16, 1), M.concrete);
  overhang.castShadow = true;
  overhang.receiveShadow = true;
  overhang.visible = false;
  site.add(overhang);

  return {desk, site, screen, screenPanel: panel, lever, overhang, roof, glass, marks: {seat: seatMark, plant, window: win}};
}

/**
 * Pool water: bright turquoise, glossy, with a moving ripple in the normals and sparkles where the
 * ripple crests catch the light. Driven by the shared WIND clock.
 */
function waterMaterial(): MeshPhysicalMaterial {
  const m = new MeshPhysicalMaterial({color: '#3cc6d6', roughness: 0.08, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.03, transparent: true, opacity: 0.88, envMapIntensity: 1.4});
  m.onBeforeCompile = (sh) => {
    sh.uniforms.uWind = WIND;
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec2 vWUv;').replace('#include <uv_vertex>', '#include <uv_vertex>\nvWUv = position.xy;');
    sh.fragmentShader = sh.fragmentShader
      .replace('#include <common>', '#include <common>\nuniform float uWind;\nvarying vec2 vWUv;')
      .replace(
        '#include <normal_fragment_maps>',
        `#include <normal_fragment_maps>
        vec2 q = vWUv * 2.6;
        float w1 = sin(q.x * 1.7 + uWind * 1.6) + sin(q.y * 2.3 - uWind * 1.2);
        float w2 = sin((q.x + q.y) * 3.1 + uWind * 2.2);
        normal = normalize(normal + vec3(cos(q.x * 1.7 + uWind * 1.6) * 0.12 + cos((q.x + q.y) * 3.1 + uWind * 2.2) * 0.06, cos(q.y * 2.3 - uWind * 1.2) * 0.12, 0.0));`,
      )
      .replace(
        '#include <dithering_fragment>',
        `#include <dithering_fragment>
        float crest = smoothstep(1.55, 1.95, sin(vWUv.x * 7.0 + uWind * 2.0) + sin(vWUv.y * 9.0 - uWind * 1.7) + sin((vWUv.x - vWUv.y) * 5.0 + uWind));
        gl_FragColor.rgb += vec3(0.9, 1.0, 1.0) * crest * 0.55;`,
      );
  };
  m.customProgramCacheKey = () => 'pool-water';
  return m;
}

/** A radial gradient, dark in the middle, for contact shadows. */
/** Cork sheet: warm tan with dark and light granules, tiled across the site board. */
function cork(): CanvasTexture {
  const n = 512;
  const c = document.createElement('canvas');
  c.width = c.height = n;
  const g = c.getContext('2d')!;
  g.fillStyle = '#c4a47d';
  g.fillRect(0, 0, n, n);
  let seed = 7;
  const r = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  for (let i = 0; i < 18000; i++) {
    const x = r() * n;
    const y = r() * n;
    const s = 0.5 + r() * 1.4;
    const k = r();
    g.fillStyle = k < 0.45 ? `rgba(120,88,58,${0.15 + r() * 0.25})` : k < 0.8 ? `rgba(222,200,168,${0.15 + r() * 0.3})` : `rgba(160,128,94,${0.15 + r() * 0.25})`;
    g.beginPath();
    g.ellipse(x, y, s, s * (0.6 + r() * 0.6), r() * Math.PI, 0, Math.PI * 2);
    g.fill();
  }
  const t = new CanvasTexture(c);
  t.colorSpace = SRGBColorSpace;
  t.wrapS = t.wrapT = RepeatWrapping;
  t.repeat.set(0.5, 0.5); // uv is in site metres: one tile per 2 m of site, about 11 cm on the board
  t.anisotropy = 8;
  return t;
}

function radial(): CanvasTexture {
  const c = document.createElement('canvas');
  c.width = c.height = 256;
  const g = c.getContext('2d')!;
  const grad = g.createRadialGradient(128, 128, 20, 128, 128, 128);
  grad.addColorStop(0, 'rgba(0,0,0,0.85)');
  grad.addColorStop(0.7, 'rgba(0,0,0,0.35)');
  grad.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = grad;
  g.fillRect(0, 0, 256, 256);
  return new CanvasTexture(c);
}

/** Shared clock for the breeze in the planting; the game advances it every frame. */
export const WIND = {value: 0};

function addWind(m: MeshStandardMaterial, amount: number): MeshStandardMaterial {
  m.onBeforeCompile = (sh) => {
    sh.uniforms.uWind = WIND;
    sh.vertexShader = sh.vertexShader
      .replace('#include <common>', '#include <common>\nuniform float uWind;')
      .replace(
        '#include <begin_vertex>',
        `#include <begin_vertex>
        float h = max(position.y - 0.6, 0.0);
        float ph = position.x * 0.35 + position.z * 0.27;
        transformed.x += sin(uWind * 1.3 + ph) * ${amount.toFixed(3)} * h;
        transformed.z += cos(uWind * 1.1 + ph * 1.3) * ${(amount * 0.7).toFixed(3)} * h;`,
      );
  };
  m.customProgramCacheKey = () => `wind-${amount}`;
  return m;
}

/** How far the lever's grip sits beyond the screen's free end, in site metres. */
export const LEVER = {reach: 0.9, rise: 0.55};

export function setOverhang(model: Model, depth: number) {
  const {room: r} = LAYOUT;
  model.overhang.visible = depth > 0.01;
  model.overhang.scale.z = Math.max(depth, 0.01);
  model.overhang.position.set((r.x0 + r.x1) / 2, r.h + 0.08, r.z1 + depth / 2);
}

// ---------------------------------------------------------------- planting
// Leaf cards with alpha, tinted by vertex colour, merged into one mesh per leaf texture
// (the website's technique, without its grow-in shader). Kept out of the levels' sightlines.

type Mats = ReturnType<typeof buildMaterials>;

function tint(g: BufferGeometry, c: Color): BufferGeometry {
  const count = g.attributes.position.count;
  const col = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    col[i * 3] = c.r;
    col[i * 3 + 1] = c.g;
    col[i * 3 + 2] = c.b;
  }
  g.setAttribute('color', new BufferAttribute(col, 3));
  return g;
}

const green = (h: number, s: number, l: number) => new Color().setHSL(h / 360, s, l);

/**
 * Where the modelled trees stand, in site metres (art/blender/trees.py makes them). Plants are
 * scenery: the watcher checks never test them. [variant, x, z, size]: size is height for a palm
 * and radius for a shrub.
 */
/** The Philippines island plants its own banana, papaya and gumamela in its model; these palms stand
 *  where their shadows cannot reach the yard during the levels' hours. */
export const GARDEN_PH: [string, number, number, number][] = [
  ['palm-a', -7.6, -7.4, 6.2],
  ['palm-a', 14.4, -2.4, 5.4],
  ['palm-b', 13.6, -6.8, 6.0],
  ['shrub-c', 12.8, 2.2, 0.9],
  ['shrub-b', 7.0, 4.6, 0.8],
];
export const GARDEN: [string, number, number, number][] = [
  // courtyard: palms in the west corners, foam planting along the south bed and the west edge
  ['shrub-a', -4.3, 3.55, 0.6],
  ['shrub-c', -3.1, 3.5, 0.55],
  ['shrub-b', -1.9, 3.55, 0.5],
  ['shrub-a', -0.6, 3.5, 0.6],
  ['shrub-c', 0.7, 3.55, 0.52],
  ['shrub-b', 1.9, 3.5, 0.58],
  ['shrub-a', 3.1, 3.55, 0.5],
  ['shrub-c', 4.3, 3.5, 0.56],
  ['shrub-b', -4.65, 0.6, 0.36],
  ['shrub-b', -4.65, 1.6, 0.32],
  ['shrub-b', -4.65, 2.5, 0.34],
  // outside: palms and clumps on the board, clear of the neighbour's sightline and the sun paths
  ['palm-a', -7.6, -7.4, 6.2],
  ['palm-b', -7.8, 4.6, 5.6],
  ['palm-b', -6.6, -1.2, 5.0],
  ['palm-a', 14.4, -2.4, 5.4],
  ['palm-b', 13.6, -6.8, 6.0],
  ['shrub-c', -7.4, 2.6, 1.1],
  ['shrub-c', 6.2, -6.0, 0.9],
  ['shrub-b', 7.0, 4.6, 0.8],
  ['shrub-c', 12.8, 2.2, 0.9],
  ['shrub-b', -5.6, -8.0, 0.8],
  ['shrub-a', -8, -2, 1.0],
  ['shrub-c', -3, -7.8, 0.9],
  ['shrub-a', 6.5, -7.9, 1.0],
  ['shrub-c', 13.8, -7.6, 0.9],
  ['shrub-b', 2, 5.0, 0.7],
  ['shrub-a', -8.2, 1.5, 0.8],
];

/** The earlier code-built palms and shrubs, kept for reference; GARDEN and the Blender trees replace them. */
export function plantGarden(site: Group, M: Mats) {
  const cards: Record<'frond' | 'broad' | 'mid' | 'fine' | 'red', BufferGeometry[]> = {frond: [], broad: [], mid: [], fine: [], red: []};
  const trunks: BufferGeometry[] = [];

  const palm = (x: number, z: number, H: number) => {
    const lean = rr(0, Math.PI * 2);
    const lx = Math.cos(lean) * H * 0.1;
    const lz = Math.sin(lean) * H * 0.1;
    const curve = new CatmullRomCurve3([new Vector3(x, 0, z), new Vector3(x + lx * 0.3, H * 0.5, z + lz * 0.3), new Vector3(x + lx, H, z + lz)]);
    const tg = new TubeGeometry(curve, 10, 0.13, 7);
    tg.deleteAttribute('uv');
    trunks.push(tg);
    const top = new Vector3(x + lx, H, z + lz);
    const n = 12;
    for (let i = 0; i < n; i++) {
      const L = rr(2.1, 2.8);
      const g = new PlaneGeometry(1.4, L, 1, 8);
      const pos = g.attributes.position;
      const a0 = rr(0.5, 1.1);
      for (let k = 0; k < pos.count; k++) {
        const u = pos.getX(k);
        const tt = (pos.getY(k) + L / 2) / L;
        let rx = 0;
        let ry = 0;
        const steps = 8;
        for (let s2 = 0; s2 < steps; s2++) {
          const a = a0 - ((s2 + 0.5) / steps) * tt * 1.5;
          rx += (Math.cos(a) * L * tt) / steps;
          ry += (Math.sin(a) * L * tt) / steps;
        }
        pos.setXYZ(k, u * (1 - tt * 0.5), ry + Math.abs(u) * 0.25, rx);
      }
      g.computeVertexNormals();
      g.rotateY((i / n) * Math.PI * 2 + rr(-0.2, 0.2));
      g.translate(top.x, top.y, top.z);
      cards.frond.push(tint(g, green(rr(70, 95), rr(0.35, 0.55), rr(0.55, 0.72))));
    }
  };

  const shrub = (x: number, z: number, rad: number, kind: keyof typeof cards, hue: [number, number], light: [number, number], y = 0.06) => {
    const n = Math.round(6 + rad * 7);
    const col = green(rr(...hue), rr(0.35, 0.6), rr(...light) * 1.9);
    for (let i = 0; i < n; i++) {
      const sz = rad * rr(1.0, 1.6);
      const g = new PlaneGeometry(sz, sz);
      g.rotateX(rr(-1.3, -0.2));
      g.rotateY(rr(0, Math.PI * 2));
      const a = rr(0, Math.PI * 2);
      const d = Math.sqrt(rnd()) * rad * 0.6;
      g.translate(x + Math.cos(a) * d, y + rad * rr(0.45, 0.95), z + Math.sin(a) * d);
      cards[kind].push(tint(g, col.clone().offsetHSL(rr(-0.02, 0.02), 0, rr(-0.05, 0.06))));
    }
  };


  // courtyard: palms in the west corners, a planted strip along the south wall
  palm(-4.2, 3.2, 5.2);
  palm(-4.3, -0.2, 4.4);
  for (let x = -4.6; x < 4.6; x += 0.55) {
    const k = rnd();
    shrub(x + rr(-0.15, 0.15), rr(3.25, 3.75), rr(0.35, 0.6), k < 0.4 ? 'broad' : k < 0.8 ? 'mid' : k < 0.9 ? 'fine' : 'red', k < 0.9 ? [70, 110] : [350, 360], [0.2, 0.32]);
  }
  for (let z = 0.3; z < 2.9; z += 0.5) shrub(rr(-4.75, -4.55), z, rr(0.3, 0.45), 'fine', [60, 90], [0.26, 0.36]);

  // outside: palms and trees on the lawn, clear of the neighbour's sightline and the sun paths
  palm(-7.6, -7.4, 6.2);
  palm(-7.8, 4.6, 5.6);
  for (const [x, z, rad] of [[-8, -2, 1.0], [-3, -7.8, 0.9], [6.5, -7.9, 1.0], [13.8, -7.6, 0.9], [2, 5.0, 0.7], [-8.2, 1.5, 0.8]] as const)
    shrub(x, z, rad, 'broad', [80, 115], [0.18, 0.28], 0.0);

  const leafMat = (map: CanvasTexture, sway = 0.018) => {
    map.colorSpace = SRGBColorSpace;
    return addWind(new MeshStandardMaterial({map, alphaTest: 0.45, side: DoubleSide, vertexColors: true, roughness: 0.7}), sway);
  };
  const T = M.T;
  addMerged(site, leafMat(T.frond, 0.03), cards.frond, true, false);
  addMerged(site, leafMat(T.broad), [...cards.broad, ...cards.red], true, false);
  addMerged(site, leafMat(T.mid), cards.mid, true, false);
  addMerged(site, leafMat(T.fine), cards.fine, true, false);
  addMerged(site, M.trunk, trunks, true, false);

}
