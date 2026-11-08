# Controls

## In the headset (hands or Touch controllers)

Open [valora-vr.vercel.app](https://valora-vr.vercel.app) in Quest Browser, choose a place on the globe, select **Enter VR** and put the controllers down, or keep them in hand. The view sets itself up once for a seated player at the desk; there is no walking or turning.

Every action is a ray pinch: point your hand so its ray touches the thing, pinch thumb and index finger, move, and open your fingers to let go.

| To | Do this |
|---|---|
| Start, continue, next level | Pinch Tiki the gecko on the garden wall |
| Place a piece | Pinch a piece on the bamboo raft, point at the courtyard, let go. A ring shows the socket it will land on |
| Move a placed piece | Pinch it and point somewhere else |
| Turn a placed piece | Pinch it and let go without moving |
| Put a piece back | Let go away from the courtyard; it floats back to the raft |
| Move the sun | Pinch the sun and drag it along its arc |
| Slide the overhang (some levels) | Pinch its handle and pull |
| Live the day | Pinch the bronze play button beside the raft |

Touch controllers work the same way: aim the controller's ray and pull the trigger where the table says pinch. The demo video shows both (filmed in Meta's IWER emulator).

## On a computer or phone, no headset

Open the page and play straight away; no need to select Enter VR. The page shows Tiki's words and the level card at reading size.

| To | Do this |
|---|---|
| Choose a country | Click a place on the globe or its card |
| Continue, next level | Click **Continue** (or click Tiki) |
| Place or move a piece | Drag it from the raft to the courtyard |
| Turn a placed piece | Click it |
| Move the sun | Drag the sun |
| Live the day | Click **Live the day** on the level card, or the play button |
| Start over, change country | **Reset** or **Map** on the level card |

Tiki's words switch between "pinch" in a headset and "click" or "drag" on a screen.

## In the emulator (IWER)

IWER is IWSDK's browser-based XR emulator: it pretends to be a Quest so you can test the immersive mode on a computer. Open the dev URL (`npm run dev`), select **Enter XR**, then in the IWER toolbar choose **Select input mode → Gaze + Hands**.

| Emulated action | Mouse and keys |
|---|---|
| Aim | Move the pointer |
| Pinch | Hold the left mouse button |
| Move the pinching hand | Drag while holding the left button |
| Move the hand nearer or further | Mouse wheel while pinching |
| Turn your head | Drag with the right mouse button |
| Reset the hand | Space |

Source: [IWSDK testing guide](https://iwsdk.dev/guides/02-testing-experience.html).
