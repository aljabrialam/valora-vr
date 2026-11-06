// Authored art, loaded from public/ (no CDN at runtime):
// - Meta's IWSDK example "environment-desk": a room with baked lighting (MIT, @iwsdk/example-assets 0.4.2)
// - Meta's IWSDK example "plant-sansevieria": a modelled snake plant (MIT, same package)
// Baked materials are shown unlit, so the baked light is not lit a second time.

import {Group, Mesh, MeshBasicMaterial, MeshStandardMaterial, SRGBColorSpace, type Object3D} from '@iwsdk/core';
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
