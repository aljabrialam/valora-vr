# Submission form and YouTube (final drafts, 11 November 2026)

Copy each block into the Devpost form or YouTube as it is. Media files are in [`docs/submission/`](submission/) (made by `node scripts/submission/media.mjs`). Items in [square brackets] are for the team to fill in.

Before submitting: redeploy valora-vr.vercel.app so the live build matches the video (six capitals, Tiki's words beside the level card), and update the Quest line under *How we built it* after the headset test.

## Elevator pitch (162 characters)

```
The sun and the neighbour both look at your house. Let one in, keep the other out. A seated VR puzzle across six Southeast Asian capitals, played with your hands.
```

## Project story (Markdown, with LaTeX)

```markdown
## Inspiration
Every tropical house fights two battles at once: let the light in, keep the eyes out. Architects juggle sun paths and sightlines with diagrams and software, but you only really *feel* the trade-off when you sit in the room. While designing VaLora, a courtyard house in Singapore, we noticed something simple: **sunlight and privacy are the same question.** A spot is in direct sun when the sun can see it. A chair is private when the neighbour can't see it. The sun is just a watcher very far away. That one rule became the game, and then we took it around Southeast Asia, where every city has its own sun, its own houses and its own watchers.

## What it does
**VaLora: Two Watchers** is a seated, single-player VR puzzle about designing for sun and privacy. A small island sits on the desk in front of you with a house, its courtyard and the neighbours. The two watchers are the **sun** and **whoever looks in**.

- **Choose a place** on a globe: Manila, Bangkok, Hanoi, Kuala Lumpur, Jakarta or Singapore. Each has its own vernacular house (a bahay kubo, a teak ruen thai, a northern village house, a Malay kampung house on stilts, a joglo, a black-and-white bungalow), its own sun path, and its own twist: typhoon wind over a bamboo fence, long-tail boats on the canal, motorbikes in the lane, condo towers looking down, monsoon rain, the high-rise next door.
- **Play with your hands.** Pinch a screen, hedge, tree or pergola on the bamboo raft, point it at the courtyard and let go; pinch it again to turn it. Pinch the sun and drag it across the sky. Touch controllers work too: the trigger does the pinch.
- **See every line of sight.** Each watcher's beam stops on whatever blocks it. Labels say SEEN or PRIVATE, SUN or SHADE, DRY or WET, in words and symbols, never colour alone.
- **Score.** Each level has a few rules on the level card, each NOT YET until it holds. When every rule is DONE the level is solved, and using the fewest pieces (par) earns three stars. Then press play to **live the day**: the sun crosses the sky and every rule is checked hour by hour.
- **Tiki**, a house gecko on the garden wall, teaches by doing: the tutorial moves on when you place a piece or move the sun.

18 levels across 6 capitals, about two minutes each. No walking, no time pressure, pause any time.

## How we built it
- **Meta Immersive Web SDK (IWSDK) and WebXR**, running in Quest Browser from a link. IWSDK's entity-component system and input: `RayInteractable` on every target, `DistanceGrabbable` on the raft pieces and the sun, `Pressed` for the play button. Hand tracking and Touch controllers share the same rays.
- **One small geometry engine for every watcher.** A target is visible to a watcher when the straight segment between them crosses no box (walls, roofs, the neighbour's house, every placed piece):

$$\text{sees}(W,T) \iff [W,T] \cap B = \varnothing \quad \text{for every box } B$$

  For the sun, the segment runs from the target towards the sun at the hour each rule names, using each capital's latitude $\varphi$, the declination $\delta$ for 8 November and the hour angle $h$:

$$\sin a = \sin\varphi\,\sin\delta + \cos\varphi\,\cos\delta\,\cos h$$

- **A proof that every level is solvable.** The same engine runs in Node and tries every layout of each level's raft pieces over every socket and turn. It fails the build if any level is unsolvable or starts solved, and it sets par to the fewest pieces that work: 18 of 18 levels pass.
- **Houses and islands generated in Blender by script**, one per country, with baked colour and occlusion. They are built inside the boxes the engine checks, so what you see is what is checked: eaves stop where the checked roof stops, and no post stands where a watcher's line crosses the open face of the house.
- **Testing without a headset.** We drive Meta's IWER emulator (Quest 3 profile) with simulated hands: an automated playthrough enters VR, pinches Tiki, carries a piece from the raft, turns it, solves a level, drags the sun and presses play (11 of 11 checks pass). The same rig filmed the demo with hands and with Touch controllers. [After the Quest test: what a real Quest 3 showed about tracking, comfort, readability and frame rate.]

## Challenges we ran into
- **Making each level a real trade-off.** Some of our first levels started solved: a low wall already hid the pond from the lane. The solvability proof caught every one, and we reworked them until each rule costs something, like Hanoi's *Hàng Xóm*, where the neighbour and the riders watch at once and no single piece blocks both.
- **Thin things are hard to point at.** Rays slipped between raft slats and hedge leaves, so every piece, the sun, Tiki and the play button carry a larger invisible hit box, and scenery never takes rays.
- **Taps versus moves.** The emulator runs far slower than real time, so a time limit for "a short pinch turns the piece" failed. A tap is now judged on movement alone (under 2 cm), which also forgives slow and shaky pinches.
- **Keeping the view clear.** Tiki's speech bubble floated at eye height and covered the courtyard. It now sits beside the level card at the back of the desk, above every roofline.
- **Designing for hands we couldn't hold.** Without our own headset, every target is designed for forgiveness: large hit areas, snapping to sockets, a ghost preview, and a click for every place and turn, since hands have no vibration.

## Accomplishments that we're proud of
- Sunlight, privacy, wind and rain answered by **one rule**: can this watcher reach that spot in a straight line?
- **18 levels proven solvable** by code, each with a par that is provably the fewest pieces.
- **Six vernacular houses and islands** generated from code, each honest to the checks.
- Hands and Touch controllers verified end to end in Meta's emulator, from pinch to solved.
- Seated from the start: no locomotion, everything within a short point of a resting hand.

## What we learned
A puzzle is only as good as the tension between its rules, and an automated proof of solvability is worth more than a day of guessing. Hands-first design is mostly about forgiveness: large targets, snaps and sound. Tropical houses across the region answer the same question in very different ways, and those answers make good puzzles. An emulator can prove logic and flow, but only a real headset can prove comfort.

## What's next for VaLora: Two Watchers
- A **daily sun challenge** using that day's real sun path, so the puzzle changes every day.
- **More of ASEAN**: Myanmar, Laos, Cambodia, Brunei and Timor-Leste are already on the globe.
- **Look through each watcher's eyes**, and lift the roof off with your hand.
- A **dusk level** where the house becomes a lantern and the neighbour can see the lit rooms.
- Lighter models (compressed geometry and textures) for a steady frame rate on Quest.

*Illustrative sunlight and visibility checks, not certified daylight, comfort, weather or privacy analysis.*
```

## Image gallery (3:2, 1500×1000 JPG, all under 0.3 MB)

Upload in this order; the first is the cover.

| File | Shows |
|---|---|
| `gallery-01-cover.jpg` | Title over the Hanoi island |
| `gallery-02-play-hands.jpg` | Headset view: carrying a piece from the raft |
| `gallery-03-score.jpg` | Headset view: every rule DONE, three stars at par |
| `gallery-04-controllers.jpg` | Headset view with Touch controllers |
| `gallery-05-sun.jpg` | Dragging the sun |
| `gallery-06-globe.jpg` | Choosing a place (browser view) |
| `gallery-07-manila.jpg` to `gallery-12-singapore.jpg` | The six islands, each with its twist |
| `gallery-13-watching.jpg` | The neighbour's line of sight on the reading chair |

## Demonstration video

```
https://youtu.be/BQlZkN5x4PU
```

2:40, under the 3-minute limit. Upload `video/valora-demo-16x9.mp4`.

## What Meta VR capability(ies) did you use in your project?

```
- Meta Immersive Web SDK (IWSDK): the entity-component system and World, the XR session, and its input system: RayInteractable on every target, DistanceGrabbable on the raft pieces and the sun, Pressed for the play button, and the grabbing feature.
- WebXR in Meta Quest Browser: an immersive-vr session opened from a link, with no install.
- Hand tracking through WebXR Hand Input: every action is a ray pinch.
- Meta Quest Touch controllers through the same rays, with the trigger for the pinch.
- Meta's Immersive Web Emulation Runtime (IWER) with the Meta Quest 3 profile, driven from the IWSDK CLI: development, automated hand tests (11 of 11 checks pass) and the headset-view footage in the demo video.
- A seated experience: the view is recentred once for a seated player and locomotion is off.
```

## Describe how Hand Interactions are implemented into your experience.

```
Every action in VaLora is a ray pinch, built on IWSDK's input system: aim, pinch, move, let go. Nothing needs fine finger poses, throwing or speed, and nothing is out of reach of a resting hand.

- Start and continue: pinch Tiki, the gecko on the garden wall (RayInteractable).
- Carry a piece: pinch a screen, hedge, tree or pergola on the bamboo raft (DistanceGrabbable). While you hold it, the piece follows the point where your hand's ray meets the desk, snaps to the nearest courtyard socket and shows a ghost preview; let go to place it. You never reach into the model.
- Turn a piece: a short pinch on a placed piece turns it 90 degrees. A tap is judged on movement (under 2 cm), not time, so slow or shaky pinches still work.
- Move the sun: pinch the sun and move your hand; the sun follows its real arc for that city, and shadows, beams and labels update live.
- Live the day: pinch the bronze play button (Pressed).

Built for forgiveness: thin objects (raft slats, hedge leaves, the sun) carry larger invisible hit boxes; scenery and labels never take the ray, so nothing gets between your hand and a target; every place and turn makes a click, and solving a level plays a sound, since hands have no vibration. Tiki's tutorial moves on when you act, not only when you pinch Tiki.

The view is set up once for a seated player, with no locomotion. Hand tracking is optional in the session, so the same rays work with Touch controllers, where the trigger does the pinch.

We verified the hand flow in Meta's IWER emulator with simulated hands (11 of 11 automated checks: recentre, Tiki pinch, carry a piece, turn it, solve a level, drag the sun, press play, no console errors). [After the Quest test: real hand-tracking notes.]
```

## What makes you excited about the future of VR? (about 120 words)

```
VR lets you understand space by being in it. Architects read sun paths and sightlines off diagrams; in a headset you can sit in the chair, drag the sun and see the neighbour's line of sight land on you. That turns expert knowledge into something anyone can feel in two minutes.

We're excited that this now runs from a link. WebXR and Meta's Immersive Web SDK mean a game like VaLora opens in Quest Browser with no install, and hand tracking means no controller to learn. That lowers the door for players and for builders in places like Southeast Asia, where we can tell our own stories about our own houses, climates and neighbours, and share them with the world.
```

## What is the target launch date for your app, if not already published?

```
[Pick one]
Already published as a web app: playable now in Quest Browser at https://valora-vr.vercel.app (no install).
or
[Month Year], as a web app in Quest Browser, followed by a Meta Horizon Store listing as a progressive web app.
```

## YouTube

**File:** `video/valora-demo-16x9.mp4`. **Thumbnail:** `docs/submission/youtube-thumbnail-1280x720.jpg`. **Captions:** `docs/submission/valora-demo-captions.en.srt` (English).

**Title (88 characters):**

```
VaLora: Two Watchers | VR Puzzle for Meta Quest | Meta VR Start Developer Competition 2026
```

**Description:**

```
The sun and the neighbour both look at your house. Let one in, keep the other out.

VaLora: Two Watchers is a seated, single-player VR puzzle for Meta Quest, built with Meta's Immersive Web SDK and WebXR. Choose a place in Southeast Asia (Manila, Bangkok, Hanoi, Kuala Lumpur, Jakarta or Singapore), then pinch screens, hedges, trees and pergolas from a bamboo raft to let the sun in and keep the watchers out: the neighbour, long-tail boats, motorbikes in the lane, condo towers, typhoon wind and monsoon rain. Drag the sun across the sky, solve every rule, then live the day hour by hour. Play with your hands or Touch controllers.

Our entry for the Meta VR Start Developer Competition 2026.

Play in Quest Browser: https://valora-vr.vercel.app
Source: https://github.com/aljabrialam/valora-vr

Chapters
0:00 Trailer
0:27 Our entry, the goal, choosing a place
0:45 How to play (hands)
1:21 How to score
1:48 Touch controllers and six capitals
2:27 Proof and maker

Notes
- Headset footage is captured in Meta's Immersive Web Emulation Runtime (IWER) with the Meta Quest 3 profile and is labelled on screen. The globe shot is the browser view before entering VR.
- Narration is a synthetic voice generated locally with Kokoro (open weights). Music and sound are synthesised in code.
- Illustrative sunlight and visibility checks, not certified daylight, comfort, weather or privacy analysis.

Made by Aljabri Alam, Singapore.

#VR #MetaQuest #WebXR
```

**Tags:**

```
VaLora, Two Watchers, VR puzzle, Meta Quest, Meta Quest 3, WebXR, Immersive Web SDK, IWSDK, hand tracking, VR game, Southeast Asia, ASEAN, architecture, sun path, privacy, Manila, Bangkok, Hanoi, Kuala Lumpur, Jakarta, Singapore, Meta VR Start Developer Competition 2026
```

**Settings:**

| Setting | Choose |
|---|---|
| Visibility | Unlisted or Public (the rules allow either; no password) |
| Audience | No, it's not made for kids |
| Category | Gaming |
| Altered or synthetic content | YouTube asks this for realistic content that viewers could mistake for real people, places or events. The narrator is a synthetic voice that does not imitate anyone, and the game is clearly animated, so No is the likely answer; the description discloses the synthetic voice either way. Check YouTube's current help page if unsure. |
| Allow embedding | On (Devpost embeds the video) |
| Subtitles | Upload the SRT file (English) |
| Video language | English |
| License | Standard YouTube License |

Optional: `video/valora-demo-9x16.mp4` can go up separately as a Short.

## Team

**Team:** [names, emails and roles; the Team Representative]. See [COMPETITION](COMPETITION.md) for eligibility questions.
