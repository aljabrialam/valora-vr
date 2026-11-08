# Performance

**Target:** a stable 72 fps or higher in Quest Browser on Quest 3 and 3S (judging minimum: 60 fps). Quest Browser starts WebXR sessions at 72 Hz; we request 90 Hz only if measurements leave headroom.

**Status (8 November):** not yet measured on a headset. The desktop numbers below are over budget after the smooth-art pass, so the reductions in the plan come before the Quest test.

| Budget | Target | Measured (desktop, flat view, `VR.stats()`, 8 Nov) |
|---|---|---|
| Draw calls per frame (includes the shadow pass) | < 150 | Manila 253, Bangkok 292 |
| Triangles per frame (includes the shadow pass) | < 200,000 | Manila 244,000, Bangkok 271,000 |
| Textures | < 20 | 15 |
| Shadow-casting lights | 1 | 1, 2048² map fitted to the island |
| Post-processing in XR | none | none |
| Download per country (house + island) | < 4 MB | 5 to 7 MB uncompressed |
| JS (gzip) | < 1.5 MB | about 1.4 MB, most of it IWSDK and three.js |

## Plan before the Quest test

1. **Compress the models:** Draco or meshopt geometry and KTX2 textures for the house atlases. Expected: downloads under 2 MB per country.
2. **Fewer triangles on the islands:** rock bevels at 3 segments instead of 4, the canal wall at 2 (already), a coarser seabed. The rock ring is about half of each island's triangles.
3. **Fewer draw calls:** merge the code-built scenery (clouds, mooring posts, raft poles) into one mesh each; instance the placed pieces.
4. **Shadows:** islands receive but do not cast; only the house, pieces and trees cast.
5. **Measure on the headset** with Quest Browser's performance overlay and record the numbers in [TESTING](TESTING.md).

## Rules we follow

- No per-frame allocation in systems; canvas labels redraw only when their text changes.
- Scenery never takes rays, so the hand rays test only a few hit boxes.
- No bloom, ambient-occlusion pass or soft-shadow pass in XR; occlusion is baked into the house textures.
- A player downloads only the country they are playing.
