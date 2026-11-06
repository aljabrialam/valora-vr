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
| Hands-only playthrough: pinch Tiki three times through the tutorial, swing the screen, solve Level 1, Tiki celebrates | IWER emulator, Meta Quest 3 profile, hand input | pass | `npm run e2e:play` |
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

## 3. Bug found by the playthrough

The labels and Tiki's speech card are three.js sprites. IWSDK's hand ray pointer raycasts every object, and a sprite throws ("Raycaster.camera needs to be set") without a camera, which stopped input processing and blanked the XR view. Sprites are display only, so their `raycast` is now a no-op; Tiki's pinch goes to an invisible hit sphere. The playthrough passed after the fix.

## 4. Full hands-only playthrough after the Blender house (7 November 2026)

`npm run e2e:play` (scripts/e2e-play.mjs) pinches Tiki through the Level 1 tutorial, then grabs the bronze handle and carries the hand along the arc to 30°.

```text
[VR] step hello → watchers → beam → swing
[VR] design screenDeg -90 → -75 → -60 → -45 → -30 → 30   solved true
[VR] step l1-done
PASS: Tiki tutorial and screen swing solved Level 1 with hands only
```

Three things the heavier scene exposed, all fixed:

| Symptom | Cause | Fix |
| --- | --- | --- |
| Only the first Tiki pinch counted | The baked house mesh sat between the hand ray and Tiki (Tiki stands at the south-west wall corner), so presses after it loaded went to scenery | The house is scenery: its meshes do not take rays (`raycast` no-op in `src/look/assets.ts`). Watcher checks never used it: they use `src/sim` geometry |
| Tiki kept the `Pressed` tag | A `pinch: 0` sequence step did not release the emulated hand under software GL | The script releases with `xr set-select-value` |
| The swing stopped near -30° | Software GL runs the emulator well below real time, and each emulator command must finish within the dev server's 27 s limit | Short pose commands, waits in wall-clock time |

These are emulator and test-script limits. Frame rate on a real Quest 3 still needs the headset test. Desktop budget from `VR.stats()`: 142 draw calls, about 128,000 triangles, 26 textures.

## 5. Not tested yet

- Real hand tracking: pinch reliability on the handle, drift, jitter at detents.
- Seated reach and arm fatigue at the desk height and distance.
- Text legibility in stereo at the label and card sizes.
- Frame rate, draw calls and shadow cost on Quest 3.
- Audio balance in the headset.

All are on the [Quest test checklist](QUEST-TEST-CHECKLIST.md).
