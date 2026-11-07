// The four playable places. Same courtyard puzzle, local house and a local twist:
//   Philippines: typhoon wind across a low bamboo fence
//   Thailand:    long-tail boats passing on the water, looking over the railing
//   Indonesia:   monsoon rain slanting in from the west
//   Singapore:   a high-rise next door looking down
// Sun: real positions for 8 November at each city (latitude, and local clock time of solar noon
// from longitude, time zone and the equation of time, about +16 minutes that day).

import type {V3} from './geom.ts';

export type WatcherId = 'sun' | 'window' | 'terrace' | 'tower' | 'boat' | 'wind' | 'rain';
export type TargetId = 'seat' | 'plant' | 'pool' | 'table' | 'deck';
export type KindId = 'screen' | 'tree' | 'pergola' | 'hedge';

export type CountryRule = {
  id: string;
  who: WatcherId;
  target: TargetId;
  want: 'sees' | 'blind';
  hour: number; // when this moment of the day happens (the sun's hour for sun rules)
  text: string;
};

export type CountryLevel = {
  id: string;
  title: string;
  brief: string;
  tray: Partial<Record<KindId, number>>;
  overhang: boolean;
  par: number;
  rules: CountryRule[];
};

export type Country = {
  id: 'ph' | 'th' | 'id' | 'sg';
  name: string;
  place: string; // city the sun is computed for
  house: string; // the local house, in words
  lat: number;
  solarNoon: number; // local clock time
  wallH: number; // courtyard wall height: low fences let wind and boats in
  eyes: Partial<Record<'window' | 'terrace' | 'tower' | 'boat', V3[]>>; // a boat has several positions
  wind?: V3; // unit vector towards where the wind comes from
  rain?: V3; // unit vector towards where the rain comes from
  extra?: {id: string; c: V3; h: V3}[]; // extra fixed buildings (the Singapore tower)
  levels: CountryLevel[];
};

export const DECL_NOV_8 = -16.6;

const dir = (azDeg: number, elDeg: number): V3 => {
  const a = (azDeg * Math.PI) / 180;
  const e = (elDeg * Math.PI) / 180;
  return [Math.cos(e) * Math.sin(a), Math.sin(e), -Math.cos(e) * Math.cos(a)];
};

const WINDOW: V3 = [7.75, 3.6, 1.5];
const BOATS: V3[] = [-6, -2.5, 1, 4.5, 8].map((x) => [x, 1.9, 7.2] as V3);

const r = {
  private: (hour = 9.5): CountryRule => ({id: 'private', who: 'window', target: 'seat', want: 'blind', hour, text: 'The neighbour cannot see you reading'}),
  plantAm: (hour = 8.5): CountryRule => ({id: 'plant-am', who: 'sun', target: 'plant', want: 'sees', hour, text: 'Morning sun on the plant at 8:30'}),
  seatPm: (hour = 15.5): CountryRule => ({id: 'seat-pm', who: 'sun', target: 'seat', want: 'blind', hour, text: 'Shade on the reading chair at 3:30'}),
  lunch: (hour = 12.5): CountryRule => ({id: 'lunch', who: 'sun', target: 'table', want: 'blind', hour, text: 'Shade on the garden table at lunch'}),
  swimSun: (hour = 11): CountryRule => ({id: 'swim-sun', who: 'sun', target: 'pool', want: 'sees', hour, text: 'Sun on the pool for an 11:00 swim'}),
};

export const COUNTRIES: Country[] = [
  {
    id: 'ph',
    name: 'Philippines',
    place: 'Manila',
    house: 'a bahay kubo on stilts, with a nipa roof and a bamboo fence',
    lat: 14.6,
    solarNoon: 11.66,
    wallH: 1.0,
    eyes: {window: [WINDOW]},
    wind: dir(135, 6), // the typhoon blows in from the south-east, low and hard
    levels: [
      {id: 'ph-1', title: 'Kapitbahay', brief: 'Your neighbour can see into your reading chair. Place a screen to block his view.', tray: {screen: 1}, overhang: false, par: 1, rules: [r.private()]},
      {id: 'ph-2', title: 'Umaga', brief: 'Stay private, but the plant needs the 8:30 sun from the east.', tray: {screen: 2, hedge: 1}, overhang: false, par: 1, rules: [r.private(), r.plantAm()]},
      {
        id: 'ph-3',
        title: 'Bagyo',
        brief: 'A typhoon is coming from the south-east. Shelter the deck from the wind, and keep the plant in its morning sun.',
        tray: {screen: 2, hedge: 2, tree: 1},
        overhang: false,
        par: 1,
        rules: [r.plantAm(), {id: 'wind', who: 'wind', target: 'deck', want: 'blind', hour: 16, text: 'The deck is sheltered from the typhoon'}],
      },
    ],
  },
  {
    id: 'th',
    name: 'Thailand',
    place: 'Bangkok',
    house: 'a Thai stilt house with a steep layered roof, by a canal',
    lat: 13.75,
    solarNoon: 12.03,
    wallH: 0.9,
    eyes: {window: [WINDOW], boat: BOATS},
    levels: [
      {id: 'th-1', title: 'Long-tail Boats', brief: 'Boats pass all day on the water. Keep the garden table out of their sight.', tray: {hedge: 2, screen: 1}, overhang: false, par: 1, rules: [{id: 'boats', who: 'boat', target: 'table', want: 'blind', hour: 10, text: 'Boat passengers cannot see the table'}]},
      {
        id: 'th-2',
        title: 'Lunch by the Water',
        brief: 'Lunch in the shade, and out of sight of the boats.',
        tray: {screen: 2, hedge: 1, tree: 1, pergola: 1},
        overhang: false,
        par: 2,
        rules: [r.lunch(), {id: 'boats', who: 'boat', target: 'table', want: 'blind', hour: 12.5, text: 'Boat passengers cannot see lunch'}],
      },
      {
        id: 'th-3',
        title: 'A Day on the Water',
        brief: 'A sunny swim the boats cannot see, a private chair, a shaded afternoon.',
        tray: {screen: 2, hedge: 2, tree: 2},
        overhang: true,
        par: 1,
        rules: [r.swimSun(), {id: 'boats-pool', who: 'boat', target: 'pool', want: 'blind', hour: 11, text: 'Swim unseen from the boats'}, r.private(), r.seatPm()],
      },
    ],
  },
  {
    id: 'id',
    name: 'Indonesia',
    place: 'Jakarta',
    house: 'a joglo with a tall stepped roof',
    lat: -6.2,
    solarNoon: 11.61,
    wallH: 2.2,
    eyes: {window: [WINDOW]},
    rain: dir(250, 70), // monsoon rain slanting in from the west
    levels: [
      {id: 'id-1', title: 'Hujan', brief: 'The afternoon monsoon rain slants in from the west. Keep the garden table dry.', tray: {pergola: 1, tree: 1}, overhang: false, par: 1, rules: [{id: 'rain', who: 'rain', target: 'table', want: 'blind', hour: 15, text: 'The table stays dry in the 3:00 rain'}]},
      {
        id: 'id-2',
        title: 'Rain and Shine',
        brief: 'A dry table in the rain, and the plant still gets its morning sun.',
        tray: {pergola: 1, tree: 2, screen: 1},
        overhang: false,
        par: 1,
        rules: [r.plantAm(), {id: 'rain', who: 'rain', target: 'table', want: 'blind', hour: 15, text: 'The table stays dry in the 3:00 rain'}],
      },
      {
        id: 'id-3',
        title: 'Musim Hujan',
        brief: 'Wet season: a dry deck, a private chair, and shade in the afternoon.',
        tray: {pergola: 1, tree: 2, screen: 2},
        overhang: true,
        par: 1,
        rules: [r.private(), r.seatPm(), {id: 'rain-deck', who: 'rain', target: 'deck', want: 'blind', hour: 16, text: 'The deck stays dry in the 4:00 rain'}],
      },
    ],
  },
  {
    id: 'sg',
    name: 'Singapore',
    place: 'Singapore',
    house: 'a black-and-white bungalow under a high-rise',
    lat: 1.35,
    solarNoon: 12.81,
    wallH: 2.2,
    eyes: {window: [WINDOW], tower: [[10.6, 9.5, -6.4]]},
    extra: [{id: 'tower', c: [12.8, 6, -6.6], h: [2.0, 6, 1.8]}],
    levels: [
      {id: 'sg-1', title: 'High-rise', brief: 'The new block next door looks right down into the pool. Hide it from above.', tray: {tree: 1, pergola: 1}, overhang: false, par: 1, rules: [{id: 'tower', who: 'tower', target: 'pool', want: 'blind', hour: 11, text: 'Swim unseen from the high-rise'}]},
      {
        id: 'sg-2',
        title: 'Morning Swim',
        brief: 'Hidden from the block, but the pool still needs the 11:00 sun.',
        tray: {tree: 2, pergola: 1, hedge: 1},
        overhang: false,
        par: 1,
        rules: [{id: 'tower', who: 'tower', target: 'pool', want: 'blind', hour: 11, text: 'Swim unseen from the high-rise'}, r.swimSun()],
      },
      {
        id: 'sg-3',
        title: 'The Whole Day',
        brief: 'Morning plant, a private swim, shaded lunch, an afternoon read. Plan the whole day.',
        tray: {screen: 2, tree: 2, pergola: 1, hedge: 1},
        overhang: true,
        par: 3,
        rules: [r.plantAm(), r.swimSun(), {id: 'tower', who: 'tower', target: 'pool', want: 'blind', hour: 11, text: 'Swim unseen from the high-rise'}, r.lunch(), r.private(), r.seatPm()],
      },
    ],
  },
];
