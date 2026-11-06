// What Tiki says, level by level. Short lines, one idea each, and the player acts as soon as possible.
// `until` decides when a step ends: a pinch on Tiki, or the level being solved.

export type Look = 'window' | 'seat' | 'plant' | 'handle' | 'overhang' | 'sun' | null;

export type Step = {
  id: string;
  say: string;
  hint?: string;
  look?: Look;
  until: 'tap' | 'solved';
  celebrate?: boolean;
  hop?: 'home' | [number, number, number];
  then?: 'next-level';
};

export const SCRIPT: Step[][] = [
  // Level 1 · The Neighbour
  [
    {id: 'hello', say: "Hi, I'm Tiki. I live on these walls, so I know where every shadow falls.", look: null, until: 'tap'},
    {id: 'watchers', say: 'Two watchers look at this house. One is your neighbour, at that window.', look: 'window', until: 'tap'},
    {id: 'beam', say: 'The red line is what they can see. Right now, the reading chair.', look: 'seat', until: 'tap'},
    {id: 'swing', say: 'Pinch the bronze handle and swing the screen until the chair is private.', hint: 'Look at the handle, pinch, and move your hand', look: 'handle', until: 'solved'},
    {id: 'l1-done', say: 'Private! Block the right watcher and the house works for you.', hint: 'Pinch Tiki for the next level', look: null, until: 'tap', celebrate: true, then: 'next-level'},
  ],
  // Level 2 · Morning Garden
  [
    {id: 'sun', say: 'The second watcher is the sun. The gold line is its light at 8:30 in the morning.', look: 'sun', until: 'tap'},
    {id: 'plant', say: 'The plant needs that morning sun. Keep the chair private too.', look: 'plant', until: 'tap'},
    {id: 'trade', say: 'Careful: swing too far and the screen steals the light. Find the one angle that does both.', look: 'handle', until: 'solved'},
    {id: 'l2-done', say: 'Both watchers happy. That was the only angle that works.', hint: 'Pinch Tiki for the last level', look: null, until: 'tap', celebrate: true, then: 'next-level'},
  ],
  // Level 3 · The Whole Day
  [
    {id: 'pm', say: 'Now the whole day. At 3:30 in the afternoon the sun comes for the reading chair.', look: 'seat', until: 'tap'},
    {id: 'overhang', say: 'Pull the overhang out over the glass to shade it. Keep the plant and the privacy too.', hint: 'Pinch the second handle and pull it towards you', look: 'overhang', until: 'solved'},
    {id: 'l3-done', say: 'Private, a sunny garden and a cool chair. That is the whole day, solved.', hint: 'Pinch Tiki to play again', look: null, until: 'tap', celebrate: true, then: 'next-level'},
  ],
];
