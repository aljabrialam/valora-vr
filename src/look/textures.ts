// @ts-nocheck
// Ported unchanged from the VaLora website (aljabrialam/valora, site/src/textures.js) so the VR model shares its materials.
// Procedural material textures drawn on canvas at load: no image files, so the page stays one small offline file.
// Every texture tiles; `metres` is how much world one tile covers, used with world-space UVs.
import * as THREE from '@iwsdk/core';

let seed = 11;
const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
const rr = (a, b) => a + (b - a) * rnd();

function tex(size, metres, draw, {srgb = true, aniso = 8} = {}) {
  const c = document.createElement('canvas');
  c.width = c.height = size;
  const g = c.getContext('2d');
  draw(g, size);
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
  t.anisotropy = aniso;
  t.repeat.set(1 / metres, 1 / metres);
  return t;
}
const speckle = (g, s, n, cols, rmax = 1.5) => {
  for (let i = 0; i < n; i++) {
    g.fillStyle = cols[(rnd() * cols.length) | 0];
    const r = rr(0.3, rmax);
    g.fillRect(rnd() * s, rnd() * s, r, r);
  }
};
const hsl = (h, s, l, a = 1) => `hsla(${h},${s}%,${l}%,${a})`;

// board-formed concrete: 300 mm boards, staggered butt joints, tie holes at 600 mm, grain streaks, tonal drift
export function concrete() {
  const M = 2.4;
  return tex(1024, M, (g, s) => {
    const px = s / M;
    g.fillStyle = '#b3afa8';
    g.fillRect(0, 0, s, s);
    // large-scale cloudy tone
    for (let i = 0; i < 60; i++) {
      const x = rnd() * s;
      const y = rnd() * s;
      const r = rr(60, 260);
      const gr = g.createRadialGradient(x, y, 0, x, y, r);
      const l = rr(62, 76);
      gr.addColorStop(0, hsl(36, 6, l, 0.18));
      gr.addColorStop(1, hsl(36, 6, l, 0));
      g.fillStyle = gr;
      g.fillRect(x - r, y - r, r * 2, r * 2);
    }
    const bh = 0.3 * px;
    for (let b = 0; b < s / bh; b++) {
      const y = b * bh;
      g.fillStyle = hsl(36, rr(2, 6), rr(58, 72), 0.45);
      g.fillRect(0, y, s, bh);
      // grain
      for (let k = 0; k < 40; k++) {
        g.strokeStyle = hsl(30, 8, rr(55, 80), rr(0.05, 0.16));
        g.lineWidth = rr(0.6, 2);
        const yy = y + rnd() * bh;
        g.beginPath();
        g.moveTo(0, yy);
        for (let x = 0; x <= s; x += 64) g.lineTo(x, yy + Math.sin(x * 0.01 + k) * rr(0.5, 2.5));
        g.stroke();
      }
      // board seam (a lip of slurry with a shadow under it)
      g.fillStyle = 'rgba(55,50,44,.55)';
      g.fillRect(0, y, s, 3);
      g.fillStyle = 'rgba(255,255,255,.12)';
      g.fillRect(0, y + 2, s, 1.5);
      // butt joints, staggered per board
      const off = (b % 2) * 0.6 * px;
      for (let x = off; x < s; x += 1.2 * px) {
        g.fillStyle = 'rgba(70,64,56,.28)';
        g.fillRect(x, y, 2, bh);
      }
    }
    // tie holes
    for (let y = 0.15 * px; y < s; y += 0.6 * px)
      for (let x = 0.3 * px; x < s; x += 0.6 * px) {
        g.fillStyle = 'rgba(60,55,50,.55)';
        g.beginPath();
        g.arc(x, y, 4, 0, Math.PI * 2);
        g.fill();
        g.fillStyle = 'rgba(255,255,255,.18)';
        g.beginPath();
        g.arc(x + 1, y + 1.5, 3, 0, Math.PI * 2);
        g.fill();
      }
    // weathering streaks running down from the top
    for (let i = 0; i < 30; i++) {
      const x = rnd() * s;
      const gr = g.createLinearGradient(0, 0, 0, rr(100, 500));
      gr.addColorStop(0, 'rgba(80,74,64,.12)');
      gr.addColorStop(1, 'rgba(80,74,64,0)');
      g.fillStyle = gr;
      g.fillRect(x, 0, rr(4, 18), s);
    }
    speckle(g, s, 26000, ['rgba(60,55,48,.25)', 'rgba(255,255,255,.18)', 'rgba(120,110,95,.2)']);
  });
}

// charcoal roof pavers on pedestals, 600 mm square
export function roof() {
  const M = 2.4;
  return tex(512, M, (g, s) => {
    const p = s / M;
    g.fillStyle = '#26282a';
    g.fillRect(0, 0, s, s);
    for (let y = 0; y < s; y += 0.6 * p)
      for (let x = 0; x < s; x += 0.6 * p) {
        g.fillStyle = hsl(210, 3, rr(19, 25));
        g.fillRect(x + 1.5, y + 1.5, 0.6 * p - 3, 0.6 * p - 3);
      }
    speckle(g, s, 9000, ['rgba(255,255,255,.06)', 'rgba(0,0,0,.2)'], 1.2);
  });
}

// dark slate pavers, 600 x 300 running bond
export function slate() {
  const M = 2.4;
  return tex(512, M, (g, s) => {
    const p = s / M;
    g.fillStyle = '#1f2021';
    g.fillRect(0, 0, s, s);
    let row = 0;
    for (let y = 0; y < s; y += 0.3 * p, row++)
      for (let x = (row % 2) * -0.3 * p; x < s; x += 0.6 * p) {
        g.fillStyle = hsl(200, rr(2, 6), rr(25, 33));
        g.fillRect(x + 1.5, y + 1.5, 0.6 * p - 3, 0.3 * p - 3);
      }
    speckle(g, s, 8000, ['rgba(255,255,255,.07)', 'rgba(0,0,0,.18)'], 1.4);
  });
}

// teak deck: 140 mm boards with grain and staggered ends; boards run along u
export function deck() {
  const M = 2.8;
  return tex(1024, M, (g, s) => {
    const p = s / M;
    g.fillStyle = '#2a1a10';
    g.fillRect(0, 0, s, s);
    const bw = 0.14 * p;
    for (let b = 0; b < s / bw; b++) {
      const y = b * bw;
      const h = rr(22, 30);
      const l = rr(30, 40);
      g.fillStyle = hsl(h, 45, l);
      g.fillRect(0, y + 1.5, s, bw - 3);
      for (let k = 0; k < 14; k++) {
        g.strokeStyle = hsl(h, 50, l + rr(-10, 8), rr(0.15, 0.4));
        g.lineWidth = rr(0.6, 1.8);
        const yy = y + 2 + rnd() * (bw - 4);
        g.beginPath();
        g.moveTo(0, yy);
        for (let x = 0; x <= s; x += 40) g.lineTo(x, yy + Math.sin(x * 0.02 + k * 3) * rr(0.3, 1.6));
        g.stroke();
      }
      const off = rnd() * s;
      g.fillStyle = 'rgba(20,12,6,.7)';
      g.fillRect(off, y, 2, bw);
    }
    speckle(g, s, 6000, ['rgba(0,0,0,.15)', 'rgba(255,220,180,.08)'], 1.2);
  });
}

// pale travertine for stepping stones and copings
export function stone() {
  const M = 1.2;
  return tex(512, M, (g, s) => {
    g.fillStyle = '#c9c0b0';
    g.fillRect(0, 0, s, s);
    for (let i = 0; i < 160; i++) {
      g.strokeStyle = hsl(38, 18, rr(62, 82), rr(0.1, 0.3));
      g.lineWidth = rr(1, 4);
      const y = rnd() * s;
      g.beginPath();
      g.moveTo(0, y);
      g.bezierCurveTo(s * 0.3, y + rr(-8, 8), s * 0.6, y + rr(-8, 8), s, y + rr(-4, 4));
      g.stroke();
    }
    for (let i = 0; i < 260; i++) {
      g.fillStyle = 'rgba(120,105,85,.35)';
      g.beginPath();
      g.ellipse(rnd() * s, rnd() * s, rr(1, 4), rr(0.5, 1.5), 0, 0, Math.PI * 2);
      g.fill();
    }
    speckle(g, s, 9000, ['rgba(0,0,0,.08)', 'rgba(255,255,255,.12)'], 1.3);
  });
}

// lawn and forest floor
export function grass() {
  const M = 3;
  return tex(512, M, (g, s) => {
    g.fillStyle = '#56663a';
    g.fillRect(0, 0, s, s);
    for (let i = 0; i < 26000; i++) {
      g.strokeStyle = hsl(rr(70, 92), rr(30, 45), rr(22, 42), 0.6);
      g.lineWidth = 1;
      const x = rnd() * s;
      const y = rnd() * s;
      g.beginPath();
      g.moveTo(x, y);
      g.lineTo(x + rr(-1.5, 1.5), y - rr(2, 6));
      g.stroke();
    }
  });
}

// interior oak floor
export function oak() {
  const M = 2.4;
  return tex(512, M, (g, s) => {
    const p = s / M;
    const bw = 0.19 * p;
    for (let b = 0; b < s / bw; b++) {
      const l = rr(62, 70);
      g.fillStyle = hsl(32, 34, l);
      g.fillRect(0, b * bw, s, bw);
      for (let k = 0; k < 6; k++) {
        g.strokeStyle = hsl(30, 30, l - rr(4, 10), 0.25);
        g.beginPath();
        const yy = b * bw + rnd() * bw;
        g.moveTo(0, yy);
        g.lineTo(s, yy + rr(-2, 2));
        g.stroke();
      }
      g.fillStyle = 'rgba(80,60,40,.25)';
      g.fillRect(0, b * bw, s, 1);
      g.fillRect(rnd() * s, b * bw, 1, bw);
    }
  });
}

// vertical timber battens (interior feature walls next to the glass)
export function battens() {
  const M = 1.2;
  return tex(256, M, (g, s) => {
    const p = s / M;
    g.fillStyle = '#2b1b10';
    g.fillRect(0, 0, s, s);
    for (let x = 0; x < s; x += 0.06 * p) {
      g.fillStyle = hsl(24, 42, rr(28, 36));
      g.fillRect(x + 1, 0, 0.045 * p, s);
    }
  });
}

// leaf cards: alpha textures for fronds and foliage. White-ish greens so vertex colour can tint them per plant.
export function frond() {
  const c = document.createElement('canvas');
  c.width = 128;
  c.height = 512;
  const g = c.getContext('2d');
  g.clearRect(0, 0, 128, 512);
  g.strokeStyle = '#a7b07a';
  g.lineWidth = 4;
  g.beginPath();
  g.moveTo(64, 0);
  g.lineTo(64, 512);
  g.stroke();
  for (let y = 10; y < 500; y += 6) {
    const t = y / 512;
    const len = 60 * Math.sin(Math.PI * Math.min(1, t * 1.15)) + 4;
    for (const side of [-1, 1]) {
      g.strokeStyle = hsl(90, 40, rr(48, 66));
      g.lineWidth = rr(5, 7.5);
      g.beginPath();
      g.moveTo(64, y);
      g.quadraticCurveTo(64 + side * len * 0.5, y + 8, 64 + side * len, y + 22 + rr(-3, 3));
      g.stroke();
    }
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  return t;
}

export function foliage(kind = 'broad') {
  const c = document.createElement('canvas');
  c.width = c.height = 256;
  const g = c.getContext('2d');
  g.clearRect(0, 0, 256, 256);
  const n = kind === 'broad' ? 34 : kind === 'fine' ? 300 : 90;
  for (let i = 0; i < n; i++) {
    const a = rnd() * Math.PI * 2;
    const r = Math.sqrt(rnd()) * (kind === 'broad' ? 70 : 100);
    const x = 128 + Math.cos(a) * r;
    const y = 128 + Math.sin(a) * r;
    g.save();
    g.translate(x, y);
    g.rotate(rr(0, Math.PI * 2));
    const L = kind === 'broad' ? rr(40, 64) : kind === 'fine' ? rr(8, 16) : rr(22, 36);
    const Wd = kind === 'broad' ? L * rr(0.45, 0.6) : kind === 'fine' ? L * 0.45 : L * 0.28;
    g.fillStyle = hsl(90, 38, rr(46, 70));
    g.beginPath();
    g.ellipse(0, 0, L / 2, Wd / 2, 0, 0, Math.PI * 2);
    g.fill();
    g.strokeStyle = 'rgba(80,90,60,.5)';
    g.lineWidth = 1;
    g.beginPath();
    g.moveTo(-L / 2, 0);
    g.lineTo(L / 2, 0);
    g.stroke();
    g.restore();
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  return t;
}
