// Authored art, loaded from public/ (no CDN at runtime):
// - Meta's IWSDK example "environment-desk": a room with baked lighting (MIT, @iwsdk/example-assets 0.4.2)
// - Meta's IWSDK example "plant-sansevieria": a modelled snake plant (MIT, same package)
// Baked materials are shown unlit, so the baked light is not lit a second time.

import {Group, InstancedMesh, Matrix4, Mesh, MeshBasicMaterial, MeshStandardMaterial, Quaternion, SRGBColorSpace, Vector3, type Object3D} from '@iwsdk/core';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';

const base = import.meta.env.BASE_URL;
const loader = new GLTFLoader();

/** The room's table top is 0.856 m high as authored; scale the room so it lands at seated desk height. */
export const ROOM = {authoredTop: 0.856, top: 0.75, depthCentre: 2.185};
export const ROOM_SCALE = ROOM.top / ROOM.authoredTop;

function unlitBake(root: Object3D) {
  root.traverse((o) => {
    const m = o as Mesh;
    if (!m.isMesh) return;
    const src = m.material as MeshStandardMaterial;
    if (src.map) src.map.colorSpace = SRGBColorSpace;
    m.material = new MeshBasicMaterial({map: src.map ?? null, side: src.side, toneMapped: true});
    m.receiveShadow = false;
    m.castShadow = false;
  });
}

/** The baked room, placed so its table's middle sits at (0, ROOM.top, deskZ) in front of the player. */
export async function loadRoom(deskZ: number): Promise<Group> {
  const gltf = await loader.loadAsync(`${base}models/environment-desk/environmentDesk.gltf`);
  unlitBake(gltf.scene);
  const g = new Group();
  g.name = 'room';
  g.add(gltf.scene);
  g.scale.setScalar(ROOM_SCALE);
  g.rotation.y = Math.PI; // the table is authored behind the origin; turn the room to face the player
  g.position.set(0, 0, deskZ + ROOM.depthCentre * ROOM_SCALE);
  return g;
}

/** The snake plant, about `height` metres tall, origin at the base of its pot. */
export async function loadPlant(height: number): Promise<Group> {
  const gltf = await loader.loadAsync(`${base}models/plant-sansevieria/plantSansevieria.gltf`);
  gltf.scene.traverse((o) => {
    const m = o as Mesh;
    if (m.isMesh) {
      m.castShadow = true;
      m.receiveShadow = true;
      const mat = m.material as MeshStandardMaterial;
      if (mat.map) mat.map.colorSpace = SRGBColorSpace;
    }
  });
  const g = new Group();
  g.add(gltf.scene);
  g.scale.setScalar(height / 0.48);
  return g;
}

/**
 * The VaLora house, modelled and baked in Blender (art/blender/house.py). Site metres, so it goes
 * straight into the site group. Colour and ambient occlusion are baked; the sun stays real-time
 * because it moves between levels and the screen and overhang move with the player's hands.
 */
export async function loadHouse(): Promise<Group> {
  const gltf = await loader.loadAsync(`${base}models/valora-house.glb`);
  gltf.scene.traverse((o) => {
    const m = o as Mesh;
    if (!m.isMesh) return;
    m.castShadow = true;
    m.receiveShadow = true;
    // Scenery only: the watcher checks use src/sim geometry, and the house must never catch a
    // pinch ray meant for Tiki or a handle (Tiki sits right by the south-west wall).
    m.raycast = () => {};
    const mat = m.material as MeshStandardMaterial;
    if (mat.map) mat.map.colorSpace = SRGBColorSpace;
    mat.aoMapIntensity = 1.0;
    mat.envMapIntensity = 0.9;
  });
  const g = new Group();
  g.name = 'house';
  g.add(gltf.scene);
  return g;
}

/**
 * Model-maker's trees (art/blender/trees.py), one instanced mesh per variant, placed in site
 * metres from `placements` ([variant, x, z, size]). Scenery only: they never take rays.
 */
export async function loadTrees(placements: [string, number, number, number][]): Promise<Group> {
  const gltf = await loader.loadAsync(`${base}models/valora-trees.glb`);
  const g = new Group();
  g.name = 'trees';
  const m = new Matrix4();
  const q = new Quaternion();
  const up = new Vector3(0, 1, 0);
  let seed = 3;
  const rand = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  gltf.scene.traverse((o) => {
    const src = o as Mesh;
    if (!src.isMesh) return;
    const name = (src.parent && src.parent !== gltf.scene ? src.parent.name : src.name).replace(/_\d+$/, '');
    const mine = placements.filter((p) => p[0] === name);
    if (!mine.length) return;
    const inst = new InstancedMesh(src.geometry, src.material, mine.length);
    mine.forEach(([, x, z, size], i) => {
      q.setFromAxisAngle(up, rand() * Math.PI * 2);
      const flat = name.startsWith('shrub') ? 0.85 : 1;
      m.compose(new Vector3(x, 0, z), q, new Vector3(size, size * flat, size));
      inst.setMatrixAt(i, m);
    });
    inst.castShadow = true;
    inst.receiveShadow = true;
    inst.raycast = () => {};
    g.add(inst);
  });
  return g;
}
