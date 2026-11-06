# Performance

**Target:** a stable 72 fps or higher in Quest Browser on Quest 3 and 3S (judging minimum: 60 fps). Quest Browser starts WebXR sessions at 72 Hz; we will request 90 Hz only if measurements leave headroom.

| Budget | Target | Now (prototype) |
|---|---|---|
| Draw calls per eye | < 100 | about 40 (estimate from scene contents) |
| Shadow-casting lights | 1 | 1 |
| Shadow map | 2048², fitted to the model | 2048² |
| Post-processing | none in XR | none |
| Texture memory | < 64 MB | canvas labels and card only |
| JS bundle | < 3 MB | 2.4 MB (IWSDK and three.js), to be split |

Rules we follow:
- No per-frame allocation in systems; canvas labels redraw only when their text changes.
- Merge static model geometry into a few meshes before the final build.
- No bloom, ambient occlusion passes or soft-shadow passes in XR.
- Measure on device with Quest Browser's performance overlay and `metavr` before submission (see the checklist).

Measured headset numbers go in [TESTING](TESTING.md).
