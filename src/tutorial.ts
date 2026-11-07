// What Tiki says, level by level. Short lines, one idea each; the player acts as soon as possible.
// `until` decides when a step ends: a pinch on Tiki, or the level being solved.

export type Look = 'window' | 'terrace' | 'seat' | 'plant' | 'pool' | 'table' | 'tray' | 'sun' | 'overhang' | 'play' | null;

export type Step = {
  id: string;
  say: string;
  hint?: string;
  look?: Look;
  until: 'tap' | 'solved';
  celebrate?: boolean;
  then?: 'next-level';
};

const done = (id: string, say: string): Step => ({id, say, hint: 'Pinch Tiki for the next level', look: 'play', until: 'tap', celebrate: true, then: 'next-level'});

export const SCRIPT: Step[][] = [
  // 1 · The Neighbour: learn to place a piece
  [
    {id: 'hello', say: "Hi, I'm Tiki. I live on these walls, so I know where every shadow falls.", until: 'tap'},
    {id: 'watcher', say: 'See the man at that window? He is waving because he can see right into your reading chair.', look: 'window', until: 'tap'},
    {id: 'place', say: 'Pinch and drag the screen from the tray into the courtyard, so it blocks the red line.', hint: 'Pinch a piece on the tray, move it over the courtyard, let go', look: 'tray', until: 'solved'},
    done('l1-done', 'He stopped waving. Pinch a placed piece to turn it, or play the day with the bronze button.'),
  ],
  // 2 · Morning Light: the sun is a watcher too
  [
    {id: 'sun', say: 'The second watcher is the sun. Drag it across the sky and watch the shadows move.', hint: 'Pinch and drag the sun', look: 'sun', until: 'tap'},
    {id: 'plant', say: 'The plant needs the 8:30 sun from the east. Stay private, but do not steal its light.', look: 'plant', until: 'solved'},
    done('l2-done', 'Both watchers happy. One piece was enough: that is three stars.'),
  ],
  // 3 · Lunch Outside: high sun, different tools
  [
    {id: 'lunch', say: 'At lunch the sun is almost overhead. A screen will not help; something above the table will.', look: 'table', until: 'solved'},
    done('l3-done', 'Shade and privacy from one piece. Height matters.'),
  ],
  // 4 · Morning Swim: a watcher from above
  [
    {id: 'terrace', say: 'Now the neighbour is up on his roof terrace, looking down at the pool.', look: 'terrace', until: 'tap'},
    {id: 'swim', say: 'Hide the pool from above, but leave it in the 11 o’clock sun.', look: 'pool', until: 'solved'},
    done('l4-done', 'A private swim in the sun. Trees see things screens cannot.'),
  ],
  // 5 · Afternoon Read: the overhang
  [
    {id: 'pm', say: 'At 3:30 the sun comes low from the west, right onto your chair.', look: 'seat', until: 'tap'},
    {id: 'overhang', say: 'Try pulling the roof overhang out over the glass, then fix the privacy.', hint: 'Pinch and drag the bronze handle on the roof', look: 'overhang', until: 'solved'},
    done('l5-done', 'Cool, private and the plant still gets its morning. Nicely done.'),
  ],
  // 6 · The Whole Day
  [
    {id: 'whole', say: 'Last one: the whole day. Six moments, two watchers. Two pieces is possible.', look: 'tray', until: 'solved'},
    done('l6-done', 'The house works from morning to night. Come back tomorrow for a new day.'),
  ],
];
