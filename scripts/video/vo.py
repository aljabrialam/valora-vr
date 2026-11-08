# Voice-over for the VR demo cut (CUT=demo in edit.py, 99.95 s).
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
DUR = 99.95
SR = 24000

# (start seconds, line). Segment times come from the demo timeline in docs/VIDEO.md.
LINES = [
    # trailer 0.0 - 22.0
    (0.5, 'Four homes in Southeast Asia, all under the same sun.'),
    (5.0, 'Manila. Bangkok. Jakarta. Singapore.'),
    (14.2, 'But someone is always watching.'),
    (16.6, 'Your goal: let the sun in, and keep the watchers out.'),
    (19.6, 'This is Valora: Two Watchers.'),
    # "Now, in the headset" card 22.0 - 24.6
    (22.15, "Here's how to play: seated, hands only."),
    # Tiki 24.6 - 28.9
    (25.0, 'Point at Tiki the gecko, and pinch to start.'),
    # place 28.9 - 34.8
    (29.2, 'Pinch a screen on the bamboo raft. Point it at the courtyard, and let go.'),
    # private 34.8 - 36.6, turn 36.6 - 40.35
    (34.9, "Now the neighbour can't see your chair."),
    (37.2, 'A short pinch turns a piece.'),
    # look 40.35 - 47.75
    (40.6, 'Look around. Every watcher has a line of sight: the neighbour, the boats on the canal, and the sun.'),
    # sun 47.75 - 57.85
    (48.1, 'Pinch the sun and drag it across the sky. The shadows follow each city\'s own sun path.'),
    (53.6, 'A spot is sunny when the sun can see it, and private when no one else can.'),
    # day 57.85 - 68.85
    (58.2, 'When every rule passes, press play to live the day.'),
    (61.8, 'The sun crosses the sky, and every watcher is checked, hour by hour.'),
    # Bangkok 68.85 - 76.75
    (69.1, 'Each city adds a twist. In Bangkok, a hedge hides the garden table from the long-tail boats.'),
    # Jakarta 76.75 - 84.65
    (77.1, 'In Jakarta, a pergola keeps the table dry in the monsoon rain.'),
    # Singapore 84.65 - 92.55
    (85.0, "In Singapore, a tree's canopy hides the pool from the high-rise next door."),
    # proof 92.55 - 95.95
    (92.75, 'Twelve levels, four capitals, every one proven solvable.'),
    # end 95.95 - 99.95
    (96.45, 'Valora. Let the sun in. Keep the watchers out.'),
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
