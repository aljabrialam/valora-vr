// Readable text for players on a computer or phone. In the headset the level card and Tiki's speech
// bubble live in the room; on a flat screen they are too small to read, so this page overlay
// carries the same words at normal reading size. Hidden while an immersive session is running.
// Styling follows Apple's HIG: system font, 17 px body, translucent material, quiet colour.

import {animate} from 'motion';
import type {Level, RuleResult} from './sim/play.ts';

const CSS = `
.vh{position:fixed;inset:0;pointer-events:none;font:17px/1.4 -apple-system,BlinkMacSystemFont,"SF Pro Text",Inter,system-ui,sans-serif;color:#1d1d1f;-webkit-font-smoothing:antialiased;z-index:5}
.vh[hidden]{display:none}
.vh-glass{background:rgba(250,249,246,.86);-webkit-backdrop-filter:blur(24px) saturate(160%);backdrop-filter:blur(24px) saturate(160%);border:1px solid rgba(0,0,0,.08);border-radius:18px;box-shadow:0 10px 30px rgba(0,0,0,.18)}
.vh-card{position:absolute;top:16px;left:16px;width:min(340px,calc(100vw - 32px));padding:16px 18px}
.vh-over{font-size:12px;font-weight:600;letter-spacing:.06em;color:#8a6a43;text-transform:uppercase}
.vh-title{font:600 22px/1.2 -apple-system,BlinkMacSystemFont,"SF Pro Display",Inter,system-ui,sans-serif;margin:2px 0 6px}
.vh-brief{font-size:15px;color:#4a4945;margin:0 0 10px}
.vh-rules{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.vh-rule{display:grid;grid-template-columns:22px 1fr auto;gap:8px;align-items:center;font-size:15px}
.vh-rule svg{width:22px;height:22px}
.vh-state{font-size:12px;font-weight:600;letter-spacing:.04em}
.vh-pass{color:#2f6f4f}.vh-fail{color:#a2452e}
.vh-note{font-size:12px;color:#6b6a66;margin-top:10px}
.vh-meta{display:flex;justify-content:space-between;align-items:center;margin-top:12px;font-size:13px;color:#4a4945}
.vh-stars{font-size:18px;letter-spacing:2px;color:#a8835a}
.vh-actions{display:flex;gap:8px;margin-top:12px;pointer-events:auto}
.vh-btn{font:600 15px/1 -apple-system,BlinkMacSystemFont,"SF Pro Text",Inter,system-ui,sans-serif;border:0;border-radius:12px;padding:11px 16px;min-height:44px;cursor:pointer}
.vh-primary{background:#1d1d1f;color:#fff;flex:1}
.vh-secondary{background:rgba(0,0,0,.06);color:#1d1d1f}
.vh-btn:focus-visible{outline:3px solid #a8835a;outline-offset:2px}
.vh-levels{display:flex;gap:6px;margin-top:10px;pointer-events:auto}
.vh-dot{width:28px;height:28px;border-radius:8px;border:0;background:rgba(0,0,0,.06);font:600 12px/28px Inter,system-ui,sans-serif;color:#4a4945;cursor:pointer;padding:0}
.vh-dot[aria-current=true]{background:#1d1d1f;color:#fff}
.vh-map{font:17px/1.4 -apple-system,BlinkMacSystemFont,"SF Pro Text",Inter,system-ui,sans-serif;color:#1d1d1f;position:fixed;inset:0;display:grid;place-items:center;background:rgba(18,52,74,.35);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px);pointer-events:auto;z-index:6}
.vh-map[hidden]{display:none}
.vh-mapcard{width:min(880px,calc(100vw - 32px));max-height:calc(100vh - 32px);overflow:auto;padding:24px 26px}
.vh-maptitle{font:600 28px/1.15 -apple-system,BlinkMacSystemFont,"SF Pro Display",Inter,system-ui,sans-serif;margin:2px 0 4px}
.vh-mapsub{font-size:15px;color:#4a4945;margin:0 0 14px}
.vh-mapgrid{display:grid;grid-template-columns:1.25fr 1fr;gap:18px;align-items:start}
.vh-mapsvg{width:100%;height:auto;background:linear-gradient(180deg,#bfe6f2,#8fd0e4);border-radius:14px}
.vh-places{display:grid;gap:8px}
.vh-place{display:grid;grid-template-columns:1fr auto;gap:2px 10px;text-align:left;border:0;border-radius:12px;padding:12px 14px;background:rgba(0,0,0,.05);cursor:pointer;font:inherit;color:inherit;min-height:44px}
.vh-place:hover,.vh-place:focus-visible{background:rgba(0,0,0,.09);outline:none}
.vh-place b{font-weight:600}
.vh-place small{grid-column:1/-1;color:#4a4945;font-size:13px}
.vh-place[disabled]{opacity:.5;cursor:default}
.vh-soon{font-size:12px;color:#6b6a66}
.vh-mapbtn{pointer-events:auto;margin-top:10px}
@media (max-width:700px){.vh-mapgrid{grid-template-columns:1fr}}
.vh-tiki{position:absolute;left:0;right:0;margin:0 auto;bottom:20px;width:min(560px,calc(100vw - 32px));padding:14px 18px}
.vh-name{font-size:12px;font-weight:600;letter-spacing:.06em;color:#8a6a43;text-transform:uppercase}
.vh-say{font-size:17px;margin:2px 0 0}
.vh-hint{font-size:15px;font-weight:600;color:#8a6a43;margin-top:6px}
.vh-hint:empty{display:none}
@media (max-width:600px){.vh-card{top:8px;left:8px;width:calc(100vw - 16px);padding:12px 14px}.vh-brief{display:none}.vh-tiki{bottom:10px}}
@media (prefers-reduced-transparency:reduce){.vh-glass{background:#faf9f6;-webkit-backdrop-filter:none;backdrop-filter:none}}
`;

const ICON = {
  pass: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10" fill="#2f6f4f"/><path d="M7.5 12.4l3 3 6-6.6" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  fail: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10" fill="none" stroke="#a2452e" stroke-width="2"/><path d="M9 9l6 6M15 9l-6 6" stroke="#a2452e" stroke-width="2" stroke-linecap="round"/></svg>',
};

const esc = (s: string) => s.replace(/[&<>"]/g, (c) => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'})[c]!);
const reduced = () => matchMedia('(prefers-reduced-motion: reduce)').matches;

export class Hud {
  private root = document.createElement('div');
  private card = document.createElement('section');
  private tiki = document.createElement('section');
  private lastSay = '';
  private lastSolved = false;

  constructor() {
    const style = document.createElement('style');
    style.textContent = CSS;
    document.head.append(style);
    this.root.className = 'vh';
    this.card.className = 'vh-glass vh-card';
    this.card.setAttribute('aria-label', 'Level');
    this.tiki.className = 'vh-glass vh-tiki';
    this.tiki.setAttribute('role', 'status');
    this.tiki.setAttribute('aria-live', 'polite');
    this.root.append(this.card, this.tiki);
    document.body.append(this.root);
  }

  /** Show or hide the overlay (hidden in the headset). */
  set visible(v: boolean) {
    this.root.hidden = !v;
  }

  onPlay: () => void = () => {};
  onCountry: (id: string) => void = () => {};
  onMap: () => void = () => {};
  private countryName = '';
  private map = document.createElement('div');

  /** The country being played, shown above the level title. */
  country(name: string) {
    this.countryName = name;
  }

  /** The ASEAN map: four playable places, the others coming soon. Capitals plotted by longitude
   *  and latitude so the map is honest without needing coastlines. */
  showMap(playable: {id: string; name: string; place: string; house: string}[]) {
    const all: {name: string; place: string; lon: number; lat: number; id?: string}[] = [
      {name: 'Myanmar', place: 'Naypyidaw', lon: 96.1, lat: 19.7},
      {name: 'Thailand', place: 'Bangkok', lon: 100.5, lat: 13.75, id: 'th'},
      {name: 'Laos', place: 'Vientiane', lon: 102.6, lat: 18.0},
      {name: 'Vietnam', place: 'Hanoi', lon: 105.8, lat: 21.0},
      {name: 'Cambodia', place: 'Phnom Penh', lon: 104.9, lat: 11.6},
      {name: 'Malaysia', place: 'Kuala Lumpur', lon: 101.7, lat: 3.1},
      {name: 'Singapore', place: 'Singapore', lon: 103.8, lat: 1.35, id: 'sg'},
      {name: 'Brunei', place: 'Bandar Seri Begawan', lon: 114.9, lat: 4.9},
      {name: 'Philippines', place: 'Manila', lon: 121.0, lat: 14.6, id: 'ph'},
      {name: 'Indonesia', place: 'Jakarta', lon: 106.8, lat: -6.2, id: 'id'},
      {name: 'Timor-Leste', place: 'Dili', lon: 125.6, lat: -8.6},
    ];
    const X = (lon: number) => ((lon - 92) / 38) * 520 + 20;
    const Y = (lat: number) => ((24 - lat) / 36) * 400 + 20;
    const dots = all
      .map((p) => {
        const on = !!p.id;
        return `<g ${on ? `data-country="${p.id}" style="cursor:pointer"` : ''}><circle cx="${X(p.lon)}" cy="${Y(p.lat)}" r="${on ? 11 : 6}" fill="${on ? '#c8643c' : '#ffffff'}" stroke="${on ? '#fff' : '#7aa9bb'}" stroke-width="3"/><text x="${X(p.lon) + (p.lon > 118 ? -14 : 14)}" y="${Y(p.lat) + 5}" text-anchor="${p.lon > 118 ? 'end' : 'start'}" font-size="${on ? 17 : 13}" font-weight="${on ? 600 : 400}" fill="${on ? '#1d1d1f' : '#47707f'}" font-family="-apple-system,Inter,system-ui,sans-serif">${p.name}</text></g>`;
      })
      .join('');
    const cards = playable
      .map((c) => `<button class="vh-place" data-country="${c.id}"><b>${esc(c.name)}</b><span class="vh-soon">${esc(c.place)}</span><small>${esc(c.house)}</small></button>`)
      .join('');
    const soon = all.filter((p) => !p.id).map((p) => p.name).join(', ');
    this.map.className = 'vh-map';
    this.map.innerHTML = `<section class="vh-glass vh-mapcard" role="dialog" aria-label="Choose a place"><div class="vh-over">VaLora: Two Watchers</div><h1 class="vh-maptitle">Choose a place</h1><p class="vh-mapsub">Same sun, different skies. Each country has its own house, its own sun path for today, and its own watchers.</p>
      <div class="vh-mapgrid"><svg class="vh-mapsvg" viewBox="0 0 560 440" role="img" aria-label="Map of South-east Asia">${dots}</svg><div class="vh-places">${cards}<p class="vh-soon">Coming soon: ${esc(soon)}.</p></div></div></section>`;
    this.map.hidden = false;
    if (!this.map.isConnected) document.body.append(this.map);
    this.map.querySelectorAll<HTMLElement>('[data-country]').forEach((el) =>
      el.addEventListener('click', () => {
        this.map.hidden = true;
        this.onCountry(el.dataset.country!);
      }),
    );
    if (!reduced()) animate(this.map.firstElementChild as HTMLElement, {opacity: [0, 1], y: [12, 0]}, {duration: 0.35, ease: 'easeOut'});
  }
  onReset: () => void = () => {};
  onLevel: (i: number) => void = () => {};

  level(index: number, total: number, level: Level, results: RuleResult[], solved: boolean, info: {used: number; par: number; stars: number; best: number}) {
    const rules = results
      .map((r) => `<li class="vh-rule">${r.pass ? ICON.pass : ICON.fail}<span>${esc(r.rule.text)}</span><span class="vh-state ${r.pass ? 'vh-pass' : 'vh-fail'}">${r.pass ? 'DONE' : 'NOT YET'}</span></li>`)
      .join('');
    const starStr = (n: number) => '\u2605'.repeat(n) + '\u2606'.repeat(3 - n);
    const dots = Array.from({length: total}, (_, i) => `<button class="vh-dot" data-level="${i}" aria-label="Level ${i + 1}" aria-current="${i === index}">${i + 1}</button>`).join('');
    this.card.innerHTML = `<div class="vh-over">${esc(this.countryName)} \u00b7 Level ${index + 1} of ${total}</div><h1 class="vh-title">${esc(level.title)}</h1><p class="vh-brief">${esc(level.brief)}</p><ul class="vh-rules">${rules}</ul>
      <div class="vh-meta"><span>Pieces used ${info.used} \u00b7 three stars with ${info.par}</span><span class="vh-stars" aria-label="${solved ? info.stars : info.best} stars">${starStr(solved ? info.stars : info.best)}</span></div>
      <div class="vh-actions"><button class="vh-btn vh-primary" data-act="play">Live the day</button><button class="vh-btn vh-secondary" data-act="reset">Reset</button></div>
      <div class="vh-levels">${dots}<button class="vh-dot" style="width:auto;padding:0 10px" data-act="map" aria-label="Choose a country">Map</button></div>
      <div class="vh-note">${solved ? '<span class="vh-pass">Solved.</span> Live the day, or click Tiki for the next level.' : 'Illustrative sunlight and visibility checks.'}</div>`;
    this.card.querySelector('[data-act=play]')!.addEventListener('click', () => this.onPlay());
    this.card.querySelector('[data-act=reset]')!.addEventListener('click', () => this.onReset());
    this.card.querySelector('[data-act=map]')!.addEventListener('click', () => this.onMap());
    this.card.querySelectorAll<HTMLButtonElement>('.vh-dot[data-level]').forEach((b) => b.addEventListener('click', () => this.onLevel(Number(b.dataset.level))));
    if (solved && !this.lastSolved && !reduced()) animate(this.card, {scale: [1, 1.03, 1]}, {duration: 0.45, ease: 'easeOut'});
    this.lastSolved = solved;
  }

  say(text: string, hint: string) {
    if (!text) {
      this.tiki.hidden = true;
      this.lastSay = '';
      return;
    }
    this.tiki.hidden = false;
    if (text === this.lastSay) return;
    this.lastSay = text;
    const extra = hint && !text.includes(hint) ? hint : ''; // skip a hint the sentence already says
    this.tiki.innerHTML = `<div class="vh-name">Tiki</div><p class="vh-say">${esc(text)}</p><div class="vh-hint">${esc(extra)}</div>`;
    if (!reduced()) animate(this.tiki, {opacity: [0, 1], y: [8, 0]}, {duration: 0.3, ease: 'easeOut'});
  }
}
