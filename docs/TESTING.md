# Testing and results

Emulator results and headset results are reported separately. Emulation cannot establish real hand-tracking reliability, seated reach, fatigue, stereo readability, comfort or Quest performance.

## Summary (6 November 2026)

| Check | Environment | Result | How to run |
|---|---|---|---|
| Every level solvable, none starts solved | Node | 3/3 | `npm run prove` |
| Type check | Node | clean | `npm run typecheck` |
| Production build | Node | builds | `npm run build` |
| Rules match the picture (start and solved states of Level 2) | Desktop Chrome, software WebGL | match | screenshots in `docs/screens/` |
| Simulated right hand pinches the handle and swings the screen to a solution | IWER emulator, Meta Quest 3 profile, hand input | pass | `npm run e2e:hand` |
| Hand tracking on a real Quest 3 or 3S | Headset | not yet tested | [QUEST-TEST-CHECKLIST](QUEST-TEST-CHECKLIST.md) |
| Frame rate on Quest 3 | Headset | not yet measured | [PERFORMANCE](PERFORMANCE.md) |

## 1. Solvability proof

`scripts/prove.ts` enumerates every snap position the player can reach with the tools each level gives them and evaluates the level's rules with the same code the game uses. It fails if a level has no solution or starts solved.

```text
PASS  The Neighbour      3 of  18 snap positions solve it
      solutions: 30°/0 m, 45°/0 m, 60°/0 m
PASS  Morning Garden     1 of  18 snap positions solve it
      solutions: 30°/0 m
PASS  The Whole Day      3 of  90 snap positions solve it
      solutions: 30°/0.6 m, 30°/1.2 m, 30°/1.8 m
```

The proof already earned its place: moving the screen's hinge so it could not swing into the room made every level unsolvable, and the proof failed before any of it reached the headset. The layout was then re-tuned with a search over hinge position, screen length and plant position.

## 2. Emulator hand test

`scripts/e2e-hand.sh` drives the IWSDK dev server's managed browser through the `iwsdk` CLI:

1. reload, enter the emulated immersive session (Meta Quest 3 profile), switch input to hands;
2. run `scripts/e2e-hand-swing.json`: aim the right hand's ray at the handle, pinch, swing towards 30°, release;
3. read the app's `[VR] design` log lines.

Result:

```text
selectstart → select → selectend
screenDeg -90 → -75 → -60 → -30 → 30   solved true
```

## 3. Not tested yet

- Real hand tracking: pinch reliability on the handle, drift, jitter at detents.
- Seated reach and arm fatigue at the desk height and distance.
- Text legibility in stereo at the label and card sizes.
- Frame rate, draw calls and shadow cost on Quest 3.
- Audio balance in the headset.

All are on the [Quest test checklist](QUEST-TEST-CHECKLIST.md).
