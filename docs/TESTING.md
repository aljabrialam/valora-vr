# Testing and results

Emulator results and headset results are reported separately. Emulation cannot establish real hand-tracking reliability, seated reach, fatigue, stereo readability, comfort or Quest performance.

## Summary (8 November 2026)

| Check | Environment | Result | How to run |
|---|---|---|---|
| Every level solvable, none starts solved, par is the fewest pieces | Node | 18/18 (6 countries x 3) | `npm run prove` |
| Type check | Node | clean | `npm run typecheck` |
| Production build | Node | builds | `npm run build` |
| Hands-only playthrough: seated recentre, headset wording, Tiki pinch, carry a raft piece onto a socket by pointing, tutorial moves on by itself, turn the piece, solve Manila level 1, drag the sun, tutorial moves on, play button starts the day, no console errors | IWER emulator, Meta Quest 3 profile, hand input | 11/11 checks pass, re-run after the smooth-art pass | `npm run e2e:play` |
| Mouse playthrough: Manila level 1 solved with 3 stars, the day completes | Desktop Chrome, software WebGL | pass | browser test |
| All six islands load with their own house, island and neighbour | Desktop Chrome, software WebGL | pass | screenshots in `docs/screens/*-v3.jpg` |
| Hand tracking on a real Quest 3 or 3S | Headset | not yet tested | [QUEST-TEST-CHECKLIST](QUEST-TEST-CHECKLIST.md) |
| Frame rate on Quest 3 | Headset | not yet measured | [PERFORMANCE](PERFORMANCE.md) |

`npm run e2e:play` output on 8 November:

```text
PASS  Seated recentre on entering VR
PASS  Words switch to the headset view
PASS  Pinching Tiki starts the tutorial
PASS  Hand grab places a raft piece on a socket
PASS  Placing a piece moves the tutorial on by itself
PASS  Short pinch turns the placed piece
PASS  Level ph-1 solved with hands only
PASS  Sun handle follows the hand ray  hour 10 -> 8.5
PASS  Moving the sun moves the tutorial on  [VR] step ph-1-done
PASS  Play button press starts the day
PASS  No console errors
ALL PASS (emulator, hands)
```

The sections below keep the history of earlier test rounds, including bugs the tests found.

## 1. Solvability proof

*History: this section describes the first prototype's proof. The current proof is `scripts/prove2.ts` (`npm run prove`), which tries every layout of each level's raft pieces over every socket and turn, for all 12 levels, and also checks that par equals the fewest pieces.*

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

## 2. Emulator hand test (prototype, 6 November)

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

## 5. Hands-only playthrough after the raft and the countries (8 November 2026)

The game moved from one swinging screen to pieces carried from a raft, four countries and a draggable sun. The playthrough was rewritten (`scripts/e2e-play.mjs`): it enters the emulated session, reads the seated rig offset from the `[VR] recentre` log, and drives the right hand in rig space through `IWER_DEVICE`.

| Symptom | Cause | Fix |
| --- | --- | --- |
| Pieces needed a 0.85 m reach | `MoveAtSource` grabbing moved the piece with the hand, not the ray | Held pieces follow where the hand ray meets the desk plane |
| Rays slipped between raft slats and hedge leaves | Thin geometry | Invisible hit boxes on every piece, the sun, Tiki and the play button |
| A pinch to turn a piece was read as a move | The emulator runs about 20 times slower than real time, so a time limit failed | A tap is judged on movement only (under 2 cm) |
| The headset view started looking at the sky | The rig was not placed for a seated player | Recentre 30 frames into the session from `world.player.head` |
| The page map covered the headset view | The overlay stayed visible | The overlay hides while presenting |

## 6. Vietnam, Malaysia, controllers and Tiki's words (9 to 11 November 2026)

| Check | Result |
| --- | --- |
| `npm run prove`: 18 levels, each solvable, none solved at the start, par equals the fewest pieces | 18/18 |
| `npm run e2e:play` (hands, Manila level 1) after moving Tiki's words beside the level card | 11/11 |
| Touch controllers in the emulator (`INPUT=controller`): Hanoi level 1 carried and solved with the trigger | pass |
| Scoring in the headset view: Hanoi level 2, both rules from NOT YET to DONE, three stars, "2 pieces · par 2" on the card | pass |

| Symptom | Cause | Fix |
| --- | --- | --- |
| Tiki's speech bubble covered the house and courtyard in the headset | It floated at eye height over the middle of the desk | It now sits beside the level card at the back of the desk; both were raised above every roofline |
| The level card did not show the score in the headset | Stars were only in the page overlay | The card draws three stars and "pieces · par" |
| The Kuala Lumpur towers stood in the sea | They sat west of the island | The island is wider on the west, with a paved plaza under the towers |

## 7. Art changes and the checks

The houses and islands are scenery: they do not take rays and the checks never read them. After each art change the proof and the playthrough are re-run, and the screenshots are compared against the rules in [ART](ART.md) (no post on the open face where the reader's sun crosses it, eaves stop at z −2.9, tall things only where their shadows cannot reach the yard).

## 8. Not tested yet

- Real hand tracking: pinch reliability on raft pieces and the sun, drift, jitter.
- Seated reach and arm fatigue at the desk height and distance.
- Text legibility in stereo at the label and card sizes, including Tiki's words beside the card.
- Touch controllers on a real Quest (only the emulator so far).
- Frame rate, draw calls and shadow cost on Quest 3.
- Audio balance in the headset.

All are on the [Quest test checklist](QUEST-TEST-CHECKLIST.md).
