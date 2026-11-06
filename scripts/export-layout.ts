// Writes art/layout.json from the game's own layout, so the Blender model is built from the
// exact numbers the watchers test against. Run: node scripts/export-layout.ts
import {writeFileSync} from 'node:fs';
import {fixedBoxes, LAYOUT} from '../src/sim/world.ts';

const out = {note: 'Generated from src/sim/world.ts. Site metres: +x east, -z north, +y up.', layout: LAYOUT, boxes: fixedBoxes()};
writeFileSync(new URL('../art/layout.json', import.meta.url), JSON.stringify(out, null, 2));
console.log('art/layout.json:', out.boxes.length, 'boxes');
