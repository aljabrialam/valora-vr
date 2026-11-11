# Borrowed Quest test checklist

Use a Quest 3 or 3S with hand tracking on and controllers put away. Sit at a normal chair. Record results in [TESTING](TESTING.md) under *Headset*.

## Before you start
- [ ] Quest Browser updated; hand tracking enabled in Settings
- [ ] Open the judge URL over HTTPS; Enter VR appears
- [ ] Session starts without a controller ever being paired or picked up

## Comfort and reach (seated)
- [ ] The view sets itself up for a seated player: the island is in front, at desk height, not the sky
- [ ] Nothing needs standing or leaning; the raft, the courtyard, the sun and Tiki are all within a short point
- [ ] No arm fatigue after 5 minutes of play

## Hands
- [ ] Pinching Tiki works on the first try (10 attempts: __/10)
- [ ] A raft piece is picked up on the first try (10 attempts: __/10)
- [ ] A held piece follows the hand ray across the courtyard without jitter; the ring shows the socket
- [ ] Letting go lands the piece on the socket shown; letting go off the courtyard sends it back to the raft
- [ ] A short pinch on a placed piece turns it and does not move it
- [ ] The sun follows the hand along its arc; the shadows move
- [ ] The play button starts the day
- [ ] The overhang handle (levels that have it) slides with the hand

## Readability
- [ ] Labels SEEN / PRIVATE / SUN / SHADE / DRY / WET / SHELTERED / WINDY readable at arm's length
- [ ] Tiki's speech card readable without leaning in, beside the level card, and never covering the courtyard
- [ ] Level card readable without leaning in
- [ ] Meaning is clear without relying on colour

## Performance
- [ ] Stable frame rate (target 72 fps or higher; judging minimum 60)
- [ ] No hitches when beams update or labels redraw, or while the day plays
- [ ] Load time from link to Enter VR: ___ s; time to change country on the globe: ___ s
- [ ] Draw calls and frame time per country (Manila, Bangkok, Hanoi, Kuala Lumpur, Jakarta, Singapore): ___

## Full run
- [ ] Tutorial and all three levels of one country with hands only, in under 10 minutes
- [ ] One level with Touch controllers: the trigger carries, turns and drags like the pinch
- [ ] Kuala Lumpur: the condo towers fit in view from the seat without turning the head far
- [ ] Change country on the globe in the headset; each island loads with its house
- [ ] Pause and resume (take the headset off and on) restores the game
- [ ] No console errors (connect over USB and check, or use `metavr log`)
