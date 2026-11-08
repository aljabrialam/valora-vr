# Voice-over for the VR demo cut (CUT=demo in edit.py, 159.55 s).
#   pip install kokoro-onnx soundfile
#   KOKORO_DIR=/path/to/models python3 scripts/video/vo.py   -> video/vo-demo.wav
# Models: kokoro-v1.0.onnx and voices-v1.0.bin from
#   https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0
# Each line starts at a fixed second, timed to the segment it describes. The script fails if a line
# runs into the next one, so a wording change cannot drift the narration off the picture.
import os, sys
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

VOICE = os.environ.get('VO_VOICE', 'af_heart')
SPEED = float(os.environ.get('VO_SPEED', '1.0'))
DUR = 159.55
SR = 24000

# (start seconds, line). Segment times come from the demo timeline in docs/VIDEO.md.
LINES = [
    # trailer 0.0 - 27.0
    (0.4, 'Six homes across Southeast Asia, all under the same sun.'),
    (4.9, 'Manila. Bangkok. Hanoi. Kuala Lumpur. Jakarta. Singapore.'),
    (19.1, 'But someone is always watching.'),
    (21.1, 'Your goal: let the sun in, and keep the watchers out.'),
    (24.1, 'This is Valora: Two Watchers.'),
    # entry 27.0 - 31.2, goal 31.2 - 35.8
    (27.1, 'Our entry for the Meta VR Start Developer Competition.'),
    (31.4, "It's a single-player puzzle. The two watchers are the sun, and whoever looks in."),
    # globe 35.8 - 45.2
    (36.1, 'Start on the globe. Pick a country, then enter VR.'),
    (40.0, 'Each one has its own house, its own sun path, and its own watchers.'),
    # "Now, in the headset" 45.2 - 47.8
    (45.3, 'In the headset, stay seated. Use hands or controllers.'),
    # Tiki 47.8 - 52.1, place 52.1 - 58.0, private 58.0 - 59.8, turn 59.8 - 63.55
    (49.0, 'Point at Tiki the gecko, and pinch to start.'),
    (52.4, 'Pinch a screen on the bamboo raft. Point it at the courtyard, and let go.'),
    (58.1, "Now the neighbour can't see your chair."),
    (60.0, 'A short pinch turns a piece.'),
    # look 63.55 - 70.95
    (63.8, 'Look around. Every watcher has a line of sight: the neighbour, the boats on the canal, and the sun.'),
    # sun 70.95 - 81.05
    (71.2, "Pinch the sun and drag it across the sky. The shadows follow each city's own sun path."),
    (76.9, 'A spot is sunny when the sun can see it, and private when no one else can.'),
    # score 81.05 - 107.65
    (81.3, "Here's how you score. Each level has a few rules, and they start as not yet."),
    (86.2, 'This one has two watchers at once: the neighbour, and the riders in the lane.'),
    (91.0, 'A screen blocks the neighbour. A hedge blocks the riders.'),
    (95.4, 'Every rule is done. Use the fewest pieces, and you earn three stars.'),
    (100.9, 'Then press play to live the day. Every hour is checked.'),
    # controllers, Hanoi 107.65 - 115.55
    (107.9, 'Prefer controllers? Point, and pull the trigger. In Hanoi, a hedge hides the table from the motorbikes.'),
    # Bangkok 115.55 - 123.45, Kuala Lumpur 123.45 - 131.35, Jakarta 131.35 - 139.25, Singapore 139.25 - 147.15
    (115.8, 'In Bangkok, a hedge hides the table from the long-tail boats.'),
    (123.7, "In Kuala Lumpur, condo towers look down. A tree's canopy hides the table."),
    (131.6, 'In Jakarta, a pergola keeps the table dry in the monsoon rain.'),
    (139.5, "In Singapore, a tree's canopy hides the pool from the high-rise next door."),
    # proof 147.15 - 150.55, profile 150.55 - 155.55, end 155.55 - 159.55
    (147.25, 'Eighteen levels, six capitals, all proven solvable.'),
    (151.0, 'Made by Aljabri Alam, in Singapore.'),
    (155.8, 'Valora. Let the sun in. Keep the watchers out.'),
]
GAP = 0.15  # least silence between two lines


def main():
    d = os.environ.get('KOKORO_DIR', '/home/claude/tts')
    k = Kokoro(os.path.join(d, 'kokoro-v1.0.onnx'), os.path.join(d, 'voices-v1.0.bin'))
    out = np.zeros(int(DUR * SR) + SR, dtype=np.float32)
    bad = []
    for i, (t, text) in enumerate(LINES):
        s, sr = k.create(text, voice=VOICE, speed=SPEED, lang='en-us')
        assert sr == SR
        s = np.asarray(s, dtype=np.float32)
        # trim the model's leading and trailing silence so the start time is the first syllable
        nz = np.nonzero(np.abs(s) > 0.01)[0]
        if len(nz):
            s = s[max(0, nz[0] - int(0.02 * SR)): nz[-1] + int(0.08 * SR)]
        end = t + len(s) / SR
        nxt = LINES[i + 1][0] if i + 1 < len(LINES) else DUR - 0.3
        flag = '' if end + GAP <= nxt else f'  OVERRUNS next by {end + GAP - nxt:.2f}s'
        if flag:
            bad.append(i)
        print(f'{t:6.2f} -> {end:6.2f}  {text}{flag}')
        a = int(t * SR)
        out[a:a + len(s)] += s
    out = out[:int(DUR * SR)]
    peak = np.max(np.abs(out))
    out = out / peak * 0.89
    os.makedirs('video', exist_ok=True)
    sf.write('video/vo-demo.wav', out, SR)
    print('wrote video/vo-demo.wav', VOICE, SPEED)
    if bad:
        sys.exit(f'{len(bad)} line(s) overrun; shorten them or move their start')


if __name__ == '__main__':
    main()
