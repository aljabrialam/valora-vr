# Assembles the showcase cut from rendered frames, overlays and the synthesized score.
#   python3 scripts/video/edit.py            -> video/valora-showcase-16x9.mp4 and -9x16.mp4
# Each segment: frames dir, seconds, optional overlay dir (transparent PNG frames), fade flags.
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

V = 'video'
FPS = 24
SEG = [
    # trailer
    ('titles/same', 1.7, None, 'in-out'),
    ('frames/t_ph', 3.2, 'titles/p_ph', ''),
    ('titles/skies', 1.7, None, 'in-out'),
    ('frames/t_th', 2.5, 'titles/p_th', ''),
    ('frames/t_id', 2.5, 'titles/p_id', ''),
    ('frames/t_sg', 2.5, 'titles/p_sg', ''),
    ('titles/watch', 1.7, None, 'in-out'),
    ('frames/t_watch', 2.8, None, ''),
    ('titles/logo', 3.4, None, 'in-out'),
    # features
    ('frames/w_globe', 6.0, 'titles/o_globe', 'in'),
    ('frames/w_tiki', 2.5, 'titles/o_tiki', ''),
    ('frames/w_place', 5.0, 'titles/o_place', ''),
    ('frames/w_sun', 3.5, 'titles/o_sun', ''),
    ('frames/w_day', 4.0, 'titles/o_day', ''),
    ('frames/w_ph3', 2.0, 'titles/o_ph3', ''),
    ('frames/w_th1', 2.0, 'titles/o_th1', ''),
    ('frames/w_id1', 2.0, 'titles/o_id1', ''),
    ('frames/w_sg1', 2.0, 'titles/o_sg1', ''),
    ('frames/w_vr', 6.0, 'titles/o_vr', ''),
    ('titles/end', 4.0, None, 'in'),
]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-2000:])
        sys.exit(1)


def frames_pattern(d):
    ext = 'png' if any(f.endswith('.png') for f in os.listdir(d)) else 'jpg'
    return os.path.join(d, f'f%05d.{ext}')


# CUT=trailer: the trailer shots, the logo and the end card only
NAME = 'showcase'
if os.environ.get('CUT') == 'trailer':
    SEG = SEG[:9] + [SEG[-1]]
    NAME = 'trailer'
# CUT=demo: the VR demo for the submission: the trailer, then the headset view (emulator), a proof card
if os.environ.get('CUT') == 'demo':
    SEG = SEG[:9] + [
        ('titles/vr', 2.6, None, 'in-out'),
        ('frames/v_ph', 4.3, 'titles/d_tiki', 'in', 0.0),
        ('frames/v_ph', 5.9, 'titles/d_place', '', 4.3),
        ('frames/v_ph', 1.8, 'titles/d_private', '', 10.2),
        ('frames/v_ph', 3.75, 'titles/d_turn', '', 12.0),
        ('frames/v_look', 7.4, 'titles/d_look', ''),
        ('frames/v_sun', 10.1, 'titles/d_sun', '', 1.8),
        ('frames/v_day', 11.0, 'titles/d_day', ''),
        ('frames/v_th', 7.9, 'titles/d_th', '', 1.9),
        ('frames/v_id', 7.9, 'titles/d_id', '', 1.9),
        ('frames/v_sg', 7.9, 'titles/d_sg', '', 1.9),
        ('titles/proof', 3.4, None, 'in-out'),
        SEG[-1],
    ]
    NAME = 'demo'
# LIMIT=n assembles only the first n segments (a quick check while shots are still rendering)
if os.environ.get('LIMIT'):
    SEG = SEG[: int(os.environ['LIMIT'])]
os.makedirs(f'{V}/seg', exist_ok=True)
parts = []
for i, seg in enumerate(SEG):
    src, secs, ov, fade = seg[:4]
    start = seg[4] if len(seg) > 4 else 0.0  # seconds into the shot's frames
    d = f'{V}/{src}'
    if not os.path.isdir(d) or not os.listdir(d):
        print('missing', d)
        sys.exit(1)
    out = f'{V}/seg/{i:02d}.mp4'
    n = int(round(secs * FPS))
    inputs = ['-framerate', str(FPS), '-start_number', str(int(round(start * FPS))), '-i', frames_pattern(d)]
    # hold the last frame if a shot is a little short, then trim to the exact length
    fil = f'[0:v]scale=1280:720,tpad=stop_mode=clone:stop=120,trim=end_frame={n},setpts=PTS-STARTPTS[v0]'
    last = 'v0'
    if ov:
        inputs += ['-framerate', str(FPS), '-i', frames_pattern(f'{V}/{ov}')]
        fil += f';[1:v]tpad=stop_mode=clone:stop=200,trim=end_frame={n},setpts=PTS-STARTPTS[o];[v0][o]overlay=0:0:format=auto[v1]'
        last = 'v1'
    if 'in' in fade:
        fil += f';[{last}]fade=t=in:st=0:d=0.25[f1]'
        last = 'f1'
    if 'out' in fade:
        fil += f';[{last}]fade=t=out:st={secs - 0.25:.3f}:d=0.25[f2]'
        last = 'f2'
    run(['ffmpeg', '-y', '-hide_banner', *inputs, '-filter_complex', fil, '-map', f'[{last}]', '-frames:v', str(n), '-r', str(FPS), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', out])
    parts.append(out)
    print('segment', i, src, secs)

with open(f'{V}/seg/list.txt', 'w') as f:
    for p in parts:
        f.write(f"file '{os.path.abspath(p)}'\n")
run(['ffmpeg', '-y', '-hide_banner', '-f', 'concat', '-safe', '0', '-i', f'{V}/seg/list.txt', '-c', 'copy', f'{V}/seg/picture.mp4'])
total = sum(s[1] for s in SEG)
MUSIC = os.environ.get('MUSIC', f'{V}/music.wav')
master = f'{V}/valora-{NAME}-16x9.mp4'
# VO=path adds a voice-over (scripts/video/vo.py): the music ducks under the voice, then the mix is normalised
VO = os.environ.get('VO')
fade = f'afade=t=out:st={total - 2.5:.2f}:d=2.5,loudnorm=I=-14:TP=-1:LRA=11'
if VO:
    duck = float(os.environ.get('MUSIC_LEVEL', '0.36'))
    graph = (f'[1:a]atrim=0:{total:.2f},aresample=48000,volume={duck}[m];'
             f'[2:a]aresample=48000,highpass=f=80,acompressor=threshold=0.1:ratio=3:attack=5:release=120,asplit=2[v1][v2];'
             f'[m][v1]sidechaincompress=threshold=0.015:ratio=14:attack=25:release=450[md];'
             f'[md][v2]amix=inputs=2:normalize=0,{fade}[a]')
    ins = ['-i', MUSIC, '-i', VO]
else:
    graph = f'[1:a]atrim=0:{total:.2f},{fade}[a]'
    ins = ['-i', MUSIC]
run(['ffmpeg', '-y', '-hide_banner', '-i', f'{V}/seg/picture.mp4', *ins, '-filter_complex', graph, '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', f'{total:.2f}', '-movflags', '+faststart', master])
print('master', master, total, 's')

# ---------------- 9:16 social cut: blurred fill, the 16:9 picture centred, a header and a footer
font = '/usr/share/fonts/truetype/inter/Inter-Bold.ttf'
for cand in ('/usr/share/fonts/truetype/inter/Inter-Bold.ttf', '/usr/share/fonts/opentype/inter/Inter-Bold.otf'):
    if os.path.exists(cand):
        font = cand
if not os.path.exists(font):
    out = subprocess.run(['fc-match', '-f', '%{file}', 'Inter:bold'], capture_output=True, text=True).stdout
    font = out.strip()
frame = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
g = ImageDraw.Draw(frame)
fb = ImageFont.truetype(font, 76)
fm = ImageFont.truetype(font, 38)
fs = ImageFont.truetype(font, 30)


def ctext(y, text, f, fill):
    w = g.textlength(text, font=f)
    g.text(((1080 - w) / 2, y), text, font=f, fill=fill)


g.rounded_rectangle((60, 250, 1020, 560), 44, fill=(10, 28, 41, 170))
ctext(300, 'VaLora: Two Watchers', fb, (255, 255, 255, 255))
ctext(400, 'A seated VR puzzle about sun,', fm, (233, 230, 222, 255))
ctext(450, 'shade and privacy', fm, (233, 230, 222, 255))
g.rounded_rectangle((60, 1420, 1020, 1660), 44, fill=(10, 28, 41, 170))
ctext(1460, 'Play free in your browser or Quest', fm, (233, 230, 222, 255))
ctext(1530, 'valora-vr.vercel.app', ImageFont.truetype(font, 58), (233, 178, 122, 255))
ctext(1720, 'Illustrative sunlight and visibility checks', fs, (255, 255, 255, 200))
frame.save(f'{V}/seg/vertical-frame.png')
vertical = f'{V}/valora-{NAME}-9x16.mp4'
run(['ffmpeg', '-y', '-hide_banner', '-i', master, '-i', f'{V}/seg/vertical-frame.png', '-filter_complex',
     '[0:v]split[a][b];[a]scale=-2:1920,crop=1080:1920,boxblur=24:2,eq=brightness=-0.06[bg];[b]scale=1080:-2[fg];[bg][fg]overlay=0:(H-h)/2[m];[m][1:v]overlay=0:0[v]',
     '-map', '[v]', '-map', '0:a', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-movflags', '+faststart', vertical])
print('vertical', vertical)
