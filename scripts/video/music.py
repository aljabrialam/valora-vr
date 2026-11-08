# Synthesized score for the showcase cut (68.5 s), all in code: no samples.
#   0-22 s trailer: warm pad building under sparse plucks, a chime and swell on the logo (18.6 s)
#   22-64.5 s features: light marimba groove in D major (I V vi IV), shaker, soft kick, bass
#   64.5-68.5 s end card: the tonic chord rings out
# python3 scripts/video/music.py video/music.wav
import sys, wave
import numpy as np

SR = 44100
DUR = 61.0
BPM = 96
BEAT = 60 / BPM
N = int(SR * DUR)
L = np.zeros(N)
Rr = np.zeros(N)
rng = np.random.default_rng(3)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def add(sig, t0, pan=0.0, gain=1.0):
    i = int(t0 * SR)
    if i >= N:
        return
    sig = sig[: N - i] * gain
    L[i:i + len(sig)] += sig * (1 - max(0, pan))
    Rr[i:i + len(sig)] += sig * (1 + min(0, pan))


def env(n, a, d, s, r, sustain_len):
    e = np.zeros(n)
    A, D, R = int(a * SR), int(d * SR), int(r * SR)
    S_ = max(0, int(sustain_len * SR) - A - D)
    seg = np.concatenate([np.linspace(0, 1, max(A, 1)), np.linspace(1, s, max(D, 1)), np.full(S_, s), np.linspace(s, 0, max(R, 1))])
    e[: min(n, len(seg))] = seg[:n]
    return e


def lowpass(x, cut):
    a = np.exp(-2 * np.pi * cut / SR)
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):  # one-pole; only used on short signals
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def pad(notes, t0, length, gain=0.06):
    n = int((length + 1.5) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for m in notes:
        for det in (-0.12, 0.0, 0.11):
            f = hz(m + det * 0.1)
            out += 2 * ((t * f) % 1) - 1
    out = np.convolve(out, np.ones(24) / 24, mode='same')  # soften the saws
    out *= env(n, 1.2, 0.5, 0.85, 1.5, length)
    add(out, t0, -0.15, gain / len(notes))
    add(out, t0 + 0.012, 0.15, gain / len(notes))


def marimba(m, t0, gain=0.22, pan=0.0):
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    f = hz(m)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 6) + 0.35 * np.sin(2 * np.pi * f * 3.93 * t) * np.exp(-t * 22) + 0.15 * np.sin(2 * np.pi * f * 9.2 * t) * np.exp(-t * 45)
    s *= np.minimum(1, t * 400)
    add(s, t0, pan, gain)


def pluck(m, t0, gain=0.14, pan=0.0):
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    f = hz(m)
    s = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(4 * np.pi * f * t) + 0.25 * np.sin(6 * np.pi * f * t)) * np.exp(-t * 3.5)
    s *= np.minimum(1, t * 300)
    add(s, t0, pan, gain)


def bell(m, t0, gain=0.16):
    n = int(4 * SR)
    t = np.arange(n) / SR
    f = hz(m)
    s = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d) for r, a, d in ((1, 1, 0.9), (2.76, 0.5, 1.6), (5.4, 0.25, 2.6), (8.9, 0.12, 4)))
    add(s, t0, -0.2, gain)
    add(s, t0 + 0.02, 0.2, gain * 0.8)


def kick(t0, gain=0.5):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 52 + 70 * np.exp(-t * 30)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11)
    add(s, t0, 0, gain)


def shaker(t0, gain=0.05, pan=0.3):
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    s = rng.standard_normal(n)
    s = s - np.convolve(s, np.ones(6) / 6, mode='same')  # bright
    s *= np.exp(-t * 55) * np.minimum(1, t * 900)
    add(s, t0, pan, gain)


def bass(m, t0, length, gain=0.2):
    n = int((length + 0.2) * SR)
    t = np.arange(n) / SR
    f = hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    s *= env(n, 0.01, 0.2, 0.7, 0.15, length)
    add(s, t0, 0, gain)


# D major: I (D) V (A) vi (Bm) IV (G)
CH = {'D': [62, 66, 69], 'A': [61, 64, 69], 'Bm': [62, 66, 71], 'G': [62, 67, 71], 'Em': [64, 67, 71]}
ROOT = {'D': 38, 'A': 33, 'Bm': 35, 'G': 31, 'Em': 40}

# ---------------- trailer: pads change on each title, plucks answer each country
prog_t = [(0.0, 'D', 4.9), (4.9, 'Bm', 4.2), (9.1, 'G', 5.0), (14.1, 'Em', 4.5)]
for t0, c, ln in prog_t:
    pad([n - 12 for n in CH[c]] + [ROOT[c] + 12], t0, ln, 0.11)
for t0, notes in ((1.7, [74, 78, 81]), (6.6, [71, 74, 78]), (9.1, [74, 79, 83]), (11.6, [71, 76, 79]), (15.8, [76, 79, 83])):
    for k, m in enumerate(notes):
        pluck(m, t0 + k * BEAT / 2, 0.12, pan=-0.3 + 0.3 * k)
# rising swell into the logo, then the chime
n = int(3.0 * SR)
t = np.arange(n) / SR
sw = rng.standard_normal(n)
sw = np.convolve(sw, np.ones(40) / 40, mode='same') * (t / 3.0) ** 2.5
add(sw, 15.6, 0, 0.5)
bell(81, 18.6, 0.2)
bell(74, 18.6, 0.14)
pad([50, 57, 62, 66, 69], 18.6, 3.2, 0.13)

# ---------------- features groove: 22.0 .. 64.5
start = 22.0
bars = int((57.0 - start) / (4 * BEAT))
prog = ['D', 'A', 'Bm', 'G']
arp = [0, 1, 2, 1, 2, 0, 1, 2]
for b in range(bars):
    c = prog[b % 4]
    t0 = start + b * 4 * BEAT
    pad(CH[c], t0, 4 * BEAT, 0.07)
    bass(ROOT[c], t0, 1.5 * BEAT, 0.2)
    bass(ROOT[c], t0 + 2.5 * BEAT, 1.0 * BEAT, 0.14)
    for k in range(8):
        tt = t0 + k * BEAT / 2
        note = CH[c][arp[k]] + (12 if k in (4, 5) else 0)
        marimba(note, tt, 0.17 if k % 2 == 0 else 0.12, pan=(-0.35 if k % 2 else 0.35))
        shaker(tt + BEAT / 4, 0.045 if k % 2 else 0.03)
    kick(t0, 0.45)
    kick(t0 + 2 * BEAT, 0.35)
# a little lift into the VR section (57.5)
bell(86, 51.0, 0.08)

# ---------------- end: tonic rings out
pad([50, 57, 62, 66, 69, 74], 57.0, 3.0, 0.12)
bell(74, 57.0, 0.12)
marimba(78, 57.0, 0.15)
marimba(81, 57.0 + BEAT / 2, 0.12)

# ---------------- master: gentle glue, fade out, loudness to about -16 LUFS (RMS proxy), peak -1 dB
st = np.stack([L, Rr], axis=1)
fade = np.ones(N)
fi = int(0.3 * SR)
fade[:fi] = np.linspace(0, 1, fi)
fo = int(2.2 * SR)
fade[-fo:] = np.linspace(1, 0, fo) ** 1.5
st *= fade[:, None]
rms = np.sqrt(np.mean(st ** 2))
st *= 10 ** (-17.5 / 20) / max(rms, 1e-9)
st = np.tanh(st * 1.2) / 1.2  # soft limit
peak = np.max(np.abs(st))
if peak > 10 ** (-1 / 20):
    st *= 10 ** (-1 / 20) / peak
pcm = (st * 32767).astype(np.int16)
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'music.wav', 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print('wrote', DUR, 's')
