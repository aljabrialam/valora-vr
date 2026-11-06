// Sun position for VaLora's site in Singapore. Ported from the VaLora website's spec.js
// (same formula, same conventions): +x is east, -z is north, +y is up, angles in degrees.

const D = Math.PI / 180;

export const SITE = {
  lat: 1.35, // Singapore
  // Solar declination and solar-noon clock time for 6 November, the date the VaLora site uses.
  decl: -16.1,
  solarNoon: 12.82,
};

export type Sun = {
  hour: number;
  el: number; // elevation above the horizon, degrees
  az: number; // azimuth clockwise from north, degrees
  dir: [number, number, number]; // unit vector from the ground towards the sun
};

/** Day of year (1..366) to solar declination in degrees (Cooper's approximation). */
export function declination(dayOfYear: number): number {
  return 23.44 * Math.sin(((360 / 365) * (284 + dayOfYear)) * D);
}

export function sunAt(hour: number, decl = SITE.decl, solarNoon = SITE.solarNoon, lat = SITE.lat): Sun {
  const H = (hour - solarNoon) * 15 * D;
  const phi = lat * D;
  const dec = decl * D;
  const sinEl = Math.sin(phi) * Math.sin(dec) + Math.cos(phi) * Math.cos(dec) * Math.cos(H);
  const el = Math.asin(sinEl);
  let cosAz = (Math.sin(dec) - sinEl * Math.sin(phi)) / (Math.cos(el) * Math.cos(phi));
  cosAz = Math.min(1, Math.max(-1, cosAz));
  let az = Math.acos(cosAz);
  if (H > 0) az = 2 * Math.PI - az;
  return {
    hour,
    el: el / D,
    az: az / D,
    dir: [Math.cos(el) * Math.sin(az), Math.sin(el), -Math.cos(el) * Math.cos(az)],
  };
}

export function clock(hour: number): string {
  const h = Math.floor(hour);
  const m = Math.round((hour - h) * 60);
  const hh = ((h + 11) % 12) + 1;
  return `${hh}:${String(m).padStart(2, '0')} ${h < 12 ? 'a.m.' : 'p.m.'}`;
}
