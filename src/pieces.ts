// The pieces the player places, built in code in the architect's-model style: basswood battens,
// a dowel tree with a sage foam crown, a slatted pergola, a foam hedge. Built in site metres around
// the socket centre, with the same footprints and heights the checks use (src/sim/play.ts).
// Also: the tiny scale figures (the resident and the neighbour) model makers put in for scale.

import {
  BoxGeometry,
  type BufferGeometry,
  CylinderGeometry,
  Group,
  IcosahedronGeometry,
  Mesh,
  MeshStandardMaterial,
  SphereGeometry,
  CapsuleGeometry,
  type Material,
} from '@iwsdk/core';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import type {Kind} from './sim/play.ts';

export const MAT = {
  basswood: new MeshStandardMaterial({color: '#c98a4b', roughness: 0.7}),
  dowel: new MeshStandardMaterial({color: '#8a5a33', roughness: 0.8}),
  foam: new MeshStandardMaterial({color: '#4f9a3a', roughness: 0.85, flatShading: true}),
  foamDark: new MeshStandardMaterial({color: '#3d7f2e', roughness: 0.85, flatShading: true}),
  flowerPink: new MeshStandardMaterial({color: '#e8458f', roughness: 0.6}),
  flowerWhite: new MeshStandardMaterial({color: '#fff4dc', roughness: 0.5, emissive: '#3a2a00', emissiveIntensity: 0.15}),
  card: new MeshStandardMaterial({color: '#f4ece0', roughness: 0.9}),
  figure: new MeshStandardMaterial({color: '#f2b37a', roughness: 0.6}),
  figureDark: new MeshStandardMaterial({color: '#8d5a3b', roughness: 0.6}),
  shirt: new MeshStandardMaterial({color: '#2f8fd6', roughness: 0.7}),
  shirtDark: new MeshStandardMaterial({color: '#e2553a', roughness: 0.7}),
  ghostOk: new MeshStandardMaterial({color: '#ffffff', roughness: 0.6, transparent: true, opacity: 0.55, depthWrite: false}),
};

function at(g: BufferGeometry, x: number, y: number, z: number, ry = 0): BufferGeometry {
  if (ry) g.rotateY(ry);
  g.translate(x, y, z);
  return g;
}

function mesh(geos: BufferGeometry[], mat: Material): Mesh {
  const m = new Mesh(mergeGeometries(geos.map((g) => g.toNonIndexed()), false)!, mat);
  m.castShadow = true;
  m.receiveShadow = true;
  return m;
}

/** Seeded so every copy of a piece looks the same. */
function rng(seed: number) {
  return () => (seed = (seed * 16807) % 2147483647) / 2147483647;
}

/** A piece model in site metres, centred on its socket, unrotated (the game rotates the group). */
export function pieceModel(kind: Kind): Group {
  const g = new Group();
  g.name = `piece-${kind}`;
  switch (kind) {
    case 'screen': {
      // 2.0 m x 2.6 m: two posts, top and bottom rails, vertical battens with gaps
      const parts: BufferGeometry[] = [at(new BoxGeometry(0.1, 2.6, 0.1), -1.0, 1.3, 0), at(new BoxGeometry(0.1, 2.6, 0.1), 1.0, 1.3, 0), at(new BoxGeometry(2.1, 0.08, 0.08), 0, 2.56, 0), at(new BoxGeometry(2.1, 0.08, 0.08), 0, 0.12, 0)];
      for (let x = -0.9; x <= 0.91; x += 0.12) parts.push(at(new BoxGeometry(0.075, 2.4, 0.05), x, 1.32, 0));
      g.add(mesh(parts, MAT.basswood));
      break;
    }
    case 'hedge': {
      // 2.4 m x 1.2 m x 0.7 m clipped hedge of foam lumps
      const r = rng(3);
      const lumps: BufferGeometry[] = [at(new BoxGeometry(2.3, 1.0, 0.6), 0, 0.5, 0)];
      for (let i = 0; i < 14; i++) lumps.push(at(new IcosahedronGeometry(0.28 + r() * 0.1, 1), -1.05 + (i % 7) * 0.35, 0.95 + r() * 0.12, i < 7 ? -0.12 : 0.12));
      g.add(mesh(lumps, MAT.foam));
      const fl: BufferGeometry[] = [];
      for (let i = 0; i < 26; i++) fl.push(at(new IcosahedronGeometry(0.08, 0), -1.1 + r() * 2.2, 0.75 + r() * 0.5, (r() < 0.5 ? -1 : 1) * (0.3 + r() * 0.1)));
      g.add(mesh(fl, MAT.flowerPink));
      break;
    }
    case 'tree': {
      // a dowel trunk and a broad foam crown between 2.2 m and 4.2 m
      const r = rng(9);
      g.add(mesh([at(new CylinderGeometry(0.07, 0.11, 2.6, 10), 0, 1.3, 0), at(new CylinderGeometry(0.03, 0.04, 0.9, 6).rotateZ(0.8), 0.3, 2.5, 0), at(new CylinderGeometry(0.03, 0.04, 0.9, 6).rotateZ(-0.8), -0.3, 2.45, 0.1)], MAT.dowel));
      const crown: BufferGeometry[] = [];
      for (let i = 0; i < 9; i++) {
        const a = (i / 9) * Math.PI * 2 + r();
        const d = i === 0 ? 0 : 0.55 + r() * 0.35;
        crown.push(at(new IcosahedronGeometry(0.55 + r() * 0.25, 1).scale(1, 0.75, 1), Math.cos(a) * d, 3.1 + (r() - 0.5) * 0.6, Math.sin(a) * d));
      }
      g.add(mesh(crown, MAT.foam));
      const fl: BufferGeometry[] = [];
      for (let i = 0; i < 30; i++) {
        const a = r() * Math.PI * 2;
        const d = r() * 1.1;
        fl.push(at(new IcosahedronGeometry(0.1, 0), Math.cos(a) * d, 3.55 + r() * 0.35, Math.sin(a) * d));
      }
      g.add(mesh(fl, MAT.flowerWhite));
      break;
    }
    case 'pergola': {
      // four posts and a slatted roof 2.6 m square at 2.55 m
      const posts: BufferGeometry[] = [];
      for (const x of [-1.2, 1.2]) for (const z of [-1.2, 1.2]) posts.push(at(new BoxGeometry(0.1, 2.5, 0.1), x, 1.25, z));
      posts.push(at(new BoxGeometry(2.6, 0.1, 0.1), 0, 2.5, -1.2), at(new BoxGeometry(2.6, 0.1, 0.1), 0, 2.5, 1.2));
      for (let z = -1.25; z <= 1.26; z += 0.16) posts.push(at(new BoxGeometry(0.06, 0.1, 2.7), 0, 0, 0, Math.PI / 2).translate(0, 2.6, z));
      g.add(mesh(posts, MAT.basswood));
      // a vine along the beams and over part of the roof
      const r = rng(5);
      const vine: BufferGeometry[] = [];
      for (let i = 0; i < 22; i++) vine.push(at(new IcosahedronGeometry(0.16 + r() * 0.08, 0), -1.2 + r() * 2.4, 2.68 + r() * 0.1, (r() < 0.5 ? -1.15 : 1.15) + (r() - 0.5) * 0.4));
      for (let i = 0; i < 6; i++) vine.push(at(new IcosahedronGeometry(0.14, 0), (r() < 0.5 ? -1.2 : 1.2), 0.4 + r() * 2.0, (r() < 0.5 ? -1.2 : 1.2)));
      g.add(mesh(vine, MAT.foamDark));
      break;
    }
  }
  return g;
}

/** A 1:18 scale figure (about 1.75 m tall in site metres), white card like a model maker's. */
export function scaleFigure(dark = false): Group {
  const g = new Group();
  const m = dark ? MAT.figureDark : MAT.figure;
  const body = new Mesh(new CapsuleGeometry(0.24, 0.62, 4, 12), dark ? MAT.shirtDark : MAT.shirt);
  body.position.y = 0.85;
  const head = new Mesh(new SphereGeometry(0.21, 20, 14), m);
  head.position.y = 1.55;
  const arm = new Group(); // right arm, pivots at the shoulder so it can wave
  arm.name = 'arm';
  arm.position.set(0.24, 1.28, 0);
  const a = new Mesh(new CapsuleGeometry(0.075, 0.5, 4, 8), dark ? MAT.shirtDark : MAT.shirt);
  a.position.y = -0.3;
  arm.add(a);
  for (const o of [body, head, a]) o.castShadow = true;
  g.add(body, head, arm);
  return g;
}
