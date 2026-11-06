// The level card that stands at the back of the desk: title, brief and one line per rule
// with a pass or fail symbol. Drawn to a canvas so it stays sharp and cheap to render.

import {CanvasTexture, Mesh, MeshBasicMaterial, PlaneGeometry, SRGBColorSpace} from 'three';
import {BRONZE, drawIcon, FAIL, INK, PASS, roundRect} from './feedback.ts';
import type {Level, RuleResult} from './sim/levels.ts';

const W = 1024;
const H = 600;

export class LevelCard {
  mesh: Mesh;
  private canvas = document.createElement('canvas');
  private tex: CanvasTexture;

  constructor(widthM = 0.46) {
    this.canvas.width = W;
    this.canvas.height = H;
    this.tex = new CanvasTexture(this.canvas);
    this.tex.colorSpace = SRGBColorSpace;
    this.tex.anisotropy = 8;
    this.mesh = new Mesh(
      new PlaneGeometry(widthM, (widthM * H) / W),
      new MeshBasicMaterial({map: this.tex, transparent: true, toneMapped: false}),
    );
  }

  draw(index: number, level: Level, results: RuleResult[], solved: boolean) {
    const g = this.canvas.getContext('2d')!;
    g.clearRect(0, 0, W, H);
    roundRect(g, 8, 8, W - 16, H - 16, 44);
    g.fillStyle = 'rgba(250,248,243,0.92)';
    g.fill();
    g.lineWidth = 3;
    g.strokeStyle = 'rgba(29,29,31,0.12)';
    g.stroke();

    g.textBaseline = 'alphabetic';
    g.fillStyle = BRONZE;
    g.font = '600 26px Inter, -apple-system, sans-serif';
    g.fillText(`LEVEL ${index + 1} OF 3`, 56, 78);
    g.fillStyle = INK;
    g.font = '500 60px "Cormorant Garamond", Georgia, serif';
    g.fillText(level.title, 56, 146);

    g.font = '400 27px Inter, -apple-system, sans-serif';
    g.fillStyle = '#4a4945';
    wrap(g, level.brief, 56, 196, W - 112, 38);

    let y = 318;
    for (const r of results) {
      drawIcon(g, r.pass ? 'check' : 'cross', 52, y - 34, 50, r.pass ? PASS : FAIL);
      g.fillStyle = INK;
      g.font = '500 30px Inter, -apple-system, sans-serif';
      g.fillText(r.rule.text, 120, y);
      g.fillStyle = r.pass ? PASS : FAIL;
      g.font = '600 22px Inter, -apple-system, sans-serif';
      g.fillText(r.pass ? 'DONE' : 'NOT YET', W - 56 - g.measureText(r.pass ? 'DONE' : 'NOT YET').width, y);
      y += 70;
    }

    g.fillStyle = solved ? PASS : '#6b6a66';
    g.font = '500 24px Inter, -apple-system, sans-serif';
    g.fillText(solved ? 'Solved. Pinch Next to sit in the chair.' : 'Illustrative sunlight and visibility checks.', 56, H - 48);
    this.tex.needsUpdate = true;
  }
}

function wrap(g: CanvasRenderingContext2D, text: string, x: number, y: number, max: number, lh: number) {
  let line = '';
  for (const word of text.split(' ')) {
    const t = line ? `${line} ${word}` : word;
    if (g.measureText(t).width > max && line) {
      g.fillText(line, x, y);
      line = word;
      y += lh;
    } else line = t;
  }
  if (line) g.fillText(line, x, y);
}
