# Roadmap to 18 November 2026, 12:00 p.m. PST (19 Nov, 4:00 a.m. SGT)

```mermaid
gantt
  dateFormat YYYY-MM-DD
  axisFormat %d %b
  section Build
  Prototype: one screen, one neighbour, one sun (done)  :done, p, 2026-11-06, 1d
  Style frame and larger model scale                     :s, 2026-11-07, 1d
  Overhang, sun drag, watcher views, roof lift           :m1, 2026-11-08, 3d
  Tutorial, menu, undo/reset/pause, seat view, saving    :m2, 2026-11-11, 2d
  Sound, polish, performance pass                        :m3, 2026-11-13, 2d
  section Validate
  Borrowed Quest test and fixes                          :m4, 2026-11-12, 4d
  section Submit
  Video, write-up, screenshots, freeze                   :m5, 2026-11-16, 3d
```

Freeze the submitted build on the evening of 18 November (Singapore time).

**Changes after reading the full rules (6 Nov)**
- Daily-sun challenge moves from stretch goal to core (judges reward repeat usage and habit).
- FoV-aware layout: everything essential inside the narrow Meta VR Glasses view; add a `metaVRGlasses` emulator test.
- Resolve the "identifiable person" rule for the VaLora name story before any entry material mentions it.

**Known follow-ups from the prototype**
- Scale up the model (about 1:16) and put the handle on a longer lever: at 1:25 the 15° detents are only about 2 cm apart, too fine for real hands.
- Tighten Level 1 (3 solutions) once the other tools exist.
- Desktop mouse dragging does not drive IWSDK grabbing outside XR; use the emulator for interaction tests.
