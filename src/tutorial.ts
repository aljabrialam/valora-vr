// What Tiki says. Short lines, one idea each; the player acts as soon as possible.
// The first level anywhere teaches placing; each country's first level introduces its twist.

import type {Country, CountryLevel} from './sim/countries.ts';

export type Look = 'window' | 'tower' | 'boat' | 'moto' | 'seat' | 'plant' | 'pool' | 'table' | 'deck' | 'tray' | 'sun' | 'overhang' | 'play' | 'tiki' | null;

export type Step = {
  id: string;
  say: string;
  hint?: string;
  look?: Look;
  until: 'tap' | 'solved' | 'placed' | 'sun';
  celebrate?: boolean;
  then?: 'next-level';
};

const TWIST: Record<Country['id'], {say: string; look: Look}> = {
  ph: {say: 'Here the neighbour watches from his balcony, and in typhoon season the wind comes in low over the bamboo fence.', look: 'window'},
  th: {say: 'Long-tail boats pass on the water all day, and the railing is low. Passengers can see a lot.', look: 'boat'},
  vn: {say: 'Motorbikes stream down the lane all day, and the wall is only waist high. Riders glance in as they pass.', look: 'moto'},
  my: {say: 'Condo towers rise over the kampung and look straight down. Screens will not help much; think about what covers from above.', look: 'tower'},
  id: {say: 'In the wet season the afternoon rain slants in from the west. Cover from above keeps things dry.', look: 'table'},
  sg: {say: 'A high-rise block next door looks straight down. Screens will not help much; think about what covers from above.', look: 'tower'},
};

export function scriptFor(country: Country, index: number, level: CountryLevel, first: boolean): Step[] {
  const steps: Step[] = [];
  if (first) {
    steps.push({id: 'hello', say: "Hi, I'm Tiki. I know where every shadow falls on this island. Pinch me to start.", hint: 'Point at Tiki and pinch', look: 'tiki', until: 'tap'});
    steps.push({id: 'place', say: 'Pinch a piece on the raft, point it at the courtyard and let go. Pinch a placed piece to turn it.', hint: 'Follow the arrow to the raft', look: 'tray', until: 'placed'});
  }
  if (index === 0) steps.push({id: `${country.id}-twist`, say: `Welcome to ${country.place}: ${country.house}. ${TWIST[country.id].say}`, look: TWIST[country.id].look, until: 'tap'});
  if (index === 0 && first) steps.push({id: 'sun', say: 'Now pinch the sun and drag it across the sky. Watch the shadows move.', hint: 'Follow the arrow to the sun', look: 'sun', until: 'sun'});
  steps.push({id: `${level.id}-goal`, say: level.brief, look: lookFor(level), until: 'solved'});
  const last = index === country.levels.length - 1;
  steps.push({
    id: `${level.id}-done`,
    say: last ? `The ${country.name} house works all day. Try another country on the map.` : 'It works. Play the day with the bronze button, or try for fewer pieces.',
    hint: last ? 'Pinch Tiki for the next country' : 'Pinch Tiki for the next level',
    look: 'play',
    until: 'tap',
    celebrate: true,
    then: 'next-level',
  });
  return steps;
}

function lookFor(level: CountryLevel): Look {
  const r = level.rules[level.rules.length - 1];
  if (r.who === 'tower' || r.who === 'boat' || r.who === 'moto') return r.who;
  if (r.who === 'window') return 'window';
  return r.target;
}
