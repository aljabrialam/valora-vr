# Game design

## 1. The idea in one line

> Two watchers look at your house: the Sun and the Neighbour. Let one see in. Keep the other out.

A spot is in direct sun when the sun can see it. A seat is private when the neighbour cannot see it. Both are the same question, *can this watcher see that target?*, so the whole game runs on one rule. The player learns it with their own hand in the first 30 seconds and then applies it to architecture.

## 2. Pillars

1. **Hands are the controller.** Every action is a pinch on a large handle, a drag or a look. Nothing needs fine finger poses, throwing or speed.
2. **Cause and effect you can see.** Each rule has a beam along the watcher's line of sight and a label in words and a symbol. Moving anything updates them immediately.
3. **Consequences from both sides.** You can look through the neighbour's eyes and through the sun's, and at the end you sit in the chair yourself.
4. **Short and complete.** About five minutes from link to seat view, with pause and resume at any point.

## 3. The session

| Beat | Time | What happens |
|---|---|---|
| Arrival | 0:00 | The desk, the model in late-afternoon light, soft courtyard ambience |
| Tutorial: your hand is the first shade | 0:15 | A sunbeam falls on the reading chair. "Hold your hand in the light." Your hand blocks the beam, the label turns to SHADED. "The house has to do this for you." |
| Lift the roof | 0:45 | Pinch the roof and lift it off to see the reading chair, the plant and the neighbour's window. Put it back or leave it ghosted |
| Level 1 · The Neighbour | 1:00 | Swing the screen to block the neighbour's view |
| Level 2 · Morning Garden | 2:00 | Keep the seat private and give the plant its 8:30 a.m. sun. Swing too far and you steal its light |
| Level 3 · The Whole Day | 3:00 | Add the overhang: privacy, morning sun on the plant, and shade on the chair at 3:30 p.m. |
| Results | 4:15 | The floor shows a sun-hours map; stars for a neat solution |
| The seat view | 4:30 | Fade into the reading chair at full size. Sunlight falls through your screen and overhang; the neighbour's window is hidden. Ten quiet seconds, then back to the model |

## 4. Tiki, the guide

Tiki is an original house gecko (the name comes from *butiki*, Filipino for gecko). Geckos live on courtyard walls in Singapore and the Philippines and spend their day moving between sun and shade, so Tiki knows where every shadow falls. Tiki sits on the front left of the desk, inside the narrow Meta VR Glasses view, and:

- speaks one short line at a time on a card above its head, never a wall of text;
- turns to look at whatever it is talking about (the neighbour's window, the chair, the plant, the handle);
- blinks, breathes, sways its tail and waves a foot when you solve a level;
- is pinched to continue, so the tutorial itself teaches the pinch.

The script is in [`src/tutorial.ts`](../src/tutorial.ts): hello, meet the neighbour, the red line, swing the screen (ends when solved), then one or two lines per later level. Tiki is built from simple shapes in code, with no imported art.

## 5. Levels

Defined in [`src/sim/levels.ts`](../src/sim/levels.ts) and proven by [`scripts/prove.ts`](../scripts/prove.ts).

| Level | Rules | Start | Solutions |
|---|---|---|---|
| The Neighbour | Neighbour cannot see the seat | Screen at −90° (open to the south) | 30°, 45°, 60° |
| Morning Garden | + Sun reaches the plant at 8:30 a.m. | Screen at 60° (private, but shading the plant) | 30° only |
| The Whole Day | + Seat in shade at 3:30 p.m. | Screen at 60°, no overhang | 30° with a 0.6, 1.2 or 1.8 m overhang |

The screen cannot swing through the courtyard glass or the garden wall, so some angles are physically unreachable (0° and ±15°, 75° to 105°). That is intentional: it makes the screen behave like a real object.

**Tuning note.** The levels were tuned with a layout search: the hinge, screen length and plant position were chosen so that Level 2 has a single solution and its starting position already looks right (the seat is private) while failing the plant. That "looks right but isn't" opening is the puzzle.

## 6. Interactions

| Action | Gesture | Notes |
|---|---|---|
| Swing the screen | Pinch the bronze handle and drag around the hinge | Snaps every 15°, a click per detent, the screen follows on a spring |
| Slide the overhang | Pinch the second bronze handle and pull it towards you | Snaps every 0.6 m, Level 3 only |
| Move the sun | Pinch the sun and drag it along its arc | Snaps to the hours each rule names, free in between (*planned*) |
| Look through a watcher's eyes | Pinch the neighbour's window or the sun and hold | Fixed viewpoint, fade in and out (*planned*) |
| Lift the roof | Pinch and lift | (*planned*) |
| Continue the tutorial, next level | Pinch Tiki | |
| Undo, reset, pause | Palm-up wrist menu | (*planned*) |

All grab targets accept a ray pinch (aim and pinch), so the same build works with Quest hand tracking and with look-and-pinch on Meta VR Glasses.

## 7. Feedback

- **Neighbour beam:** a rust-red rod from the neighbour's window. It ends in a stop marker on whatever blocks it, or runs all the way to the seat.
- **Sun beam:** a warm gold rod from the sun's direction to each sun target, stopped the same way.
- **Labels** over each target: SEEN / PRIVATE with an eye or crossed-out eye; IN SUN / SHADED with a sun or half-shaded disc. The outline colour helps but is never the only cue.
- **Level card:** one line per rule with a check or cross symbol and DONE / NOT YET, plus the line "Illustrative sunlight and visibility checks."

## 8. Simulation boundaries

The checks are explicit geometry: an unobstructed segment from the watcher to the target. For the sun, the segment points along the sun's direction at the hour the rule names, for Singapore (latitude 1.35°) on 6 November. They are separate from the rendered lighting. We describe them only as *illustrative sunlight and visibility checks*: not certified daylight analysis, thermal comfort, legal privacy compliance or structural validation, and direct sun alone does not determine a plant's health or a room's comfort.

## 9. Out of scope

General CAD editing, floor-plan generation, BIM import, multiplayer, AI assistants, accounts, payments, a backend, continuous locomotion, physics, weather simulation, and passthrough as decoration.

## 10. Stretch goals (only if the core is finished and smooth by 15 November)

- **Daily sun:** a daily challenge using that day's real Singapore sun path. `sunAt()` already takes the declination, so the puzzle changes with the date.
- **Dusk level:** the house as a lantern; the neighbour now sees *lit* rooms.
