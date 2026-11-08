// The country picker's globe: a small orthographic Earth drawn in SVG. Choosing a place turns the
// globe to it before the island loads. ASEAN members are tinted; playable ones carry a marker.
import {animate} from 'motion';
import {geoGraticule10, geoOrthographic, geoPath, type GeoPermissibleObjects} from 'd3-geo';
import {feature} from 'topojson-client';
import type {GeometryCollection, Topology} from 'topojson-specification';
import world from 'world-atlas/countries-110m.json';

export type Place = {name: string; place: string; lon: number; lat: number; id?: string};

// ISO 3166 numeric codes used by world-atlas (Singapore is too small for the 1:110m map; its marker
// stands in for it)
const ASEAN = new Set(['608', '764', '360', '702', '458', '704', '418', '116', '104', '096', '626']);
const PLAYABLE_CODE: Record<string, string> = {ph: '608', th: '764', id: '360', sg: '702'};

const SIZE = 440;
const R = SIZE / 2 - 10;
const NS = 'http://www.w3.org/2000/svg';
const reduced = () => matchMedia('(prefers-reduced-motion: reduce)').matches;

export class Globe {
  readonly svg = document.createElementNS(NS, 'svg');
  private proj = geoOrthographic().scale(R).translate([SIZE / 2, SIZE / 2]).clipAngle(90).precision(0.4);
  private path = geoPath(this.proj);
  private rot: [number, number] = [-112, -4];
  private zoom = 1;
  private sea: SVGCircleElement[] = [];
  private land: {id: string; d: GeoPermissibleObjects}[];
  private layer = {grid: el('path'), countries: el('g'), markers: el('g')};
  private focus = '';
  private spin: {stop: () => void} | null = null;
  onPick: (id: string) => void = () => {};

  constructor(private places: Place[]) {
    const topo = world as unknown as Topology<{countries: GeometryCollection}>;
    const fc = feature(topo, topo.objects.countries) as unknown as {features: {id: string}[]};
    this.land = fc.features.map((f) => ({id: String(f.id), d: f as unknown as GeoPermissibleObjects}));
    this.svg.setAttribute('viewBox', `0 0 ${SIZE} ${SIZE}`);
    this.svg.setAttribute('class', 'vh-globe');
    this.svg.setAttribute('role', 'img');
    this.svg.setAttribute('aria-label', 'Globe showing South-east Asia');
    this.svg.innerHTML = `<defs>
      <radialGradient id="vh-sea" cx="38%" cy="32%" r="75%"><stop offset="0" stop-color="#d9f1f8"/><stop offset=".55" stop-color="#8fd0e4"/><stop offset="1" stop-color="#4c9fbd"/></radialGradient>
      <radialGradient id="vh-shine" cx="34%" cy="28%" r="60%"><stop offset="0" stop-color="#fff" stop-opacity=".45"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
    </defs>
    <circle cx="${SIZE / 2}" cy="${SIZE / 2 + 6}" r="${R}" fill="#12344a" opacity=".12"/>
    <circle cx="${SIZE / 2}" cy="${SIZE / 2}" r="${R}" fill="url(#vh-sea)"/>`;
    this.sea = [...this.svg.querySelectorAll('circle')] as SVGCircleElement[];
    this.layer.grid.setAttribute('fill', 'none');
    this.layer.grid.setAttribute('stroke', '#ffffff');
    this.layer.grid.setAttribute('stroke-opacity', '.25');
    this.layer.grid.setAttribute('stroke-width', '.6');
    this.svg.append(this.layer.grid, this.layer.countries, this.layer.markers);
    const shine = el('circle');
    for (const [k, v] of Object.entries({cx: SIZE / 2, cy: SIZE / 2, r: R, fill: 'url(#vh-shine)', 'pointer-events': 'none'})) shine.setAttribute(k, String(v));
    this.svg.append(shine);
    this.sea.push(shine as SVGCircleElement);
    this.listen();
    this.draw();
    // a slow drift until the player points at a place
    if (!reduced()) this.spin = animate(this.rot[0], this.rot[0] - 24, {duration: 40, ease: 'linear', onUpdate: (v) => this.set([v, this.rot[1]])});
  }

  /** Turn to a place; resolves when the turn is done. */
  turnTo(lon: number, lat: number, duration = 1.1, zoomTo = this.zoom): Promise<void> {
    this.spin?.stop();
    this.spin = null;
    const from = [...this.rot] as [number, number];
    const to: [number, number] = [-lon, -lat];
    // the short way round
    let dl = to[0] - from[0];
    dl = ((dl + 540) % 360) - 180;
    const z0 = this.zoom;
    if (reduced()) {
      this.zoom = zoomTo;
      this.set([from[0] + dl, to[1]]);
      return Promise.resolve();
    }
    return new Promise((done) => {
      animate(0, 1, {
        duration,
        ease: [0.32, 0.72, 0, 1],
        onUpdate: (k) => {
          // turn first, then lean in: the zoom trails the turn so the place is centred before it grows
          const kz = Math.max(0, (k - 0.35) / 0.65);
          this.zoom = z0 + (zoomTo - z0) * kz * kz;
          this.set([from[0] + dl * k, from[1] + (to[1] - from[1]) * k]);
        },
        onComplete: () => done(),
      });
    });
  }

  /** Highlight one playable place (hover or keyboard focus). */
  highlight(id: string) {
    this.focus = id;
    this.draw();
  }

  private set(r: [number, number]) {
    this.rot = r;
    this.draw();
  }

  private draw() {
    this.proj.rotate(this.rot).scale(R * this.zoom);
    for (const c of this.sea) c.setAttribute('r', String(R * this.zoom));
    this.layer.grid.setAttribute('d', this.path(geoGraticule10()) ?? '');
    const focusCode = PLAYABLE_CODE[this.focus];
    const playable = new Set(Object.values(PLAYABLE_CODE));
    this.layer.countries.innerHTML = this.land
      .map(({id, d}) => {
        const p = this.path(d);
        if (!p) return '';
        const fill = id === focusCode ? '#c8643c' : playable.has(id) ? '#e8a77f' : ASEAN.has(id) ? '#f3dcc0' : '#f4efe4';
        return `<path d="${p}" fill="${fill}" stroke="#ffffff" stroke-width=".6"/>`;
      })
      .join('');
    // markers on the near side only
    const [cl, cp] = [-this.rot[0], -this.rot[1]];
    this.layer.markers.innerHTML = this.places
      .map((p) => {
        if (angle(cl, cp, p.lon, p.lat) > 82) return '';
        const xy = this.proj([p.lon, p.lat]);
        if (!xy) return '';
        const on = !!p.id;
        const hot = p.id === this.focus;
        const left = p.lon < 102; // mainland west: label to the left; elsewhere the sea to the east has room
        const r = on ? (hot ? 9 : 7) : 3.5;
        return `<g ${on ? `data-country="${p.id}" tabindex="0" role="button" aria-label="${p.name}" style="cursor:pointer"` : ''}>
          ${on ? `<circle cx="${xy[0]}" cy="${xy[1]}" r="${r + 9}" fill="transparent"/>` : ''}
          <circle cx="${xy[0]}" cy="${xy[1]}" r="${r}" fill="${on ? '#c8643c' : '#ffffff'}" stroke="${on ? '#ffffff' : '#7aa9bb'}" stroke-width="${on ? 2.5 : 1.5}"/>
          ${on || hot ? `<text x="${xy[0] + (left ? -12 : 12)}" y="${xy[1] + 5}" text-anchor="${left ? 'end' : 'start'}" font-size="${hot ? 16 : 14}" font-weight="600" fill="#1d1d1f" stroke="#ffffff" stroke-width="3" paint-order="stroke" font-family="-apple-system,Inter,system-ui,sans-serif">${p.name}</text>` : ''}
        </g>`;
      })
      .join('');
  }

  /** One set of listeners on the marker layer: the markers are redrawn every frame while turning. */
  private listen() {
    // hold still under the pointer so a marker can be clicked
    this.svg.addEventListener('pointerenter', () => {
      this.spin?.stop();
      this.spin = null;
    });
    const idOf = (e: Event) => (e.target as Element).closest<SVGGElement>('[data-country]')?.dataset.country;
    const m = this.layer.markers;
    m.addEventListener('click', (e) => {
      const id = idOf(e);
      if (id) this.onPick(id);
    });
    m.addEventListener('keydown', (e) => {
      const id = idOf(e);
      if (id && (e.key === 'Enter' || e.key === ' ')) this.onPick(id);
    });
    m.addEventListener('pointerover', (e) => {
      const id = idOf(e);
      if (id && id !== this.focus) this.highlight(id);
    });
  }
}

function el(tag: string) {
  return document.createElementNS(NS, tag);
}
/** Great-circle angle in degrees between two lon/lat points. */
function angle(l1: number, p1: number, l2: number, p2: number) {
  const D = Math.PI / 180;
  const c = Math.sin(p1 * D) * Math.sin(p2 * D) + Math.cos(p1 * D) * Math.cos(p2 * D) * Math.cos((l2 - l1) * D);
  return Math.acos(Math.max(-1, Math.min(1, c))) / D;
}
