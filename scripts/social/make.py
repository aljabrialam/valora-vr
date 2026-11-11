# Writes the social graphics artboards (Design canvas .dc.html files) into scripts/social/project/.
# Image urls come from blobs.json (asset name -> the canvas's uploaded asset url); export.mjs swaps
# them for the local renders in docs/social/img when it makes the PNGs.
#   python3 scripts/social/make.py
import json, os, sys, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, 'project')
B = json.load(open(os.path.join(ROOT, 'blobs.json'))) if os.path.exists(os.path.join(ROOT, 'blobs.json')) else {}


def img(name):
    return B.get(name, f'__IMG_{name}__')


FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&amp;family=Inter:wght@400;500;600&amp;display=swap" rel="stylesheet">'
INK, PAPER, BRONZE, MUTED = '#1d1d1f', '#faf8f3', '#8a6a44', '#55534e'
SERIF = "'Cormorant Garamond', Georgia, serif"
SANS = "Inter, system-ui, sans-serif"
URL = 'valora-vr.vercel.app'


def page(title, w, h, body):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
{FONTS}
<style>
body{{margin:0}}
a{{color:{BRONZE}}}a:hover{{color:{INK}}}
</style>
</helmet>
<div style="width: {w}px; height: {h}px; box-sizing: border-box; position: relative; overflow: hidden; background: {PAPER}; color: {INK}; font-family: {SANS}">
{body}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{w},"height":{h}}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
'''


def kicker(t, size=20, color=BRONZE):
    return f'<div style="font-family: {SANS}; font-size: {size}px; font-weight: 600; letter-spacing: 0.16em; text-transform: uppercase; color: {color}">{t}</div>'


def logo(h=44):
    return f'<img src="{img("logo")}" alt="VaLora" style="height: {h}px; width: auto; display: block">'


def footer(pad=64, size=22):
    return f'''<div style="display: flex; align-items: center; justify-content: space-between; gap: 24px">
{logo(40)}
<div style="font-size: {size}px; font-weight: 500; color: {INK}">{URL}</div>
</div>'''


def photo(name, alt, style):
    return f'<img src="{img(name)}" alt="{alt}" style="display: block; object-fit: cover; {style}">'


COUNTRIES = [
    ('ph', '01', 'Philippines', 'Manila', 'A bahay kubo on bamboo stilts, the dirty kitchen and a banca on the beach.', 'Typhoon wind', 'comes in low over a one-metre bamboo fence.', ['Kapitbahay', 'Umaga', 'Bagyo']),
    ('th', '02', 'Thailand', 'Bangkok', 'A teak ruen thai on posts by the canal, with a spirit house and a water landing.', 'Long-tail boats', 'pass on the khlong and look over a low wall.', ['Long-tail Boats', 'Lunch by the Water', 'A Day on the Water']),
    ('id', '03', 'Indonesia', 'Jakarta', 'A Javanese joglo with its three-pitch roof, carved teak and red-brick walls.', 'Monsoon rain', 'slants in from the west every afternoon.', ['Hujan', 'Rain and Shine', 'Musim Hujan']),
    ('sg', '04', 'Singapore', 'Singapore', 'A black-and-white bungalow with a verandah, a pool and a Peranakan shophouse next door.', 'The high-rise', 'next door looks straight down into the garden.', ['High-rise', 'Morning Swim', 'The Whole Day']),
]

boards = {}

# 1. Square post: the hero
boards['Main.dc.html'] = (1080, 1080, 'Square post', page('Same sun, different skies', 1080, 1080, f'''
{photo('hero_th', 'The Bangkok island: a teak Thai stilt house by a canal, floating on turquoise water', 'position: absolute; left: 0; top: 0; width: 1080px; height: 590px')}
<div style="position: absolute; left: 0; top: 590px; width: 1080px; height: 490px; box-sizing: border-box; padding: 52px 64px 48px; display: flex; flex-direction: column; justify-content: space-between">
<div style="display: flex; flex-direction: column; gap: 14px">
{kicker('A seated VR puzzle · hands only')}
<h1 style="margin: 0; font-family: {SERIF}; font-weight: 600; font-size: 92px; line-height: 0.98; letter-spacing: -0.01em">Same sun.<br>Different skies.</h1>
<p style="margin: 0; font-size: 26px; line-height: 1.4; color: {MUTED}; max-width: 860px">Let the sun in, keep the watchers out: four South-east Asian capitals.</p>
</div>
{footer()}
</div>'''))

# 2. Portrait post: four islands
tiles = ''.join(f'''<div style="display: flex; flex-direction: column; gap: 14px">
{photo('hero_' + c, f'The {city} island', 'width: 100%; height: 330px; border-radius: 16px')}
<div style="display: flex; flex-direction: column; gap: 4px">
<div style="font-family: {SERIF}; font-size: 40px; font-weight: 600; line-height: 1">{city}</div>
<div style="font-size: 20px; color: {MUTED}">{twist}</div>
</div>
</div>''' for (c, n, country, city, house, twist, more, levels) in COUNTRIES)
boards['Islands.dc.html'] = (1080, 1350, 'Portrait post: four islands', page('Four capitals, four watchers', 1080, 1350, f'''
<div style="box-sizing: border-box; width: 1080px; height: 1350px; padding: 64px; display: flex; flex-direction: column; gap: 40px">
<div style="display: flex; flex-direction: column; gap: 14px">
{kicker('Four capitals · four watchers · twelve puzzles')}
<h1 style="margin: 0; font-family: {SERIF}; font-weight: 600; font-size: 84px; line-height: 0.98">Same sun. Different skies.</h1>
</div>
<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 40px 32px; flex-grow: 1">
{tiles}
</div>
{footer()}
</div>'''))

# 3. Story / Reel cover
boards['Story.dc.html'] = (1080, 1920, 'Story 9:16', page('Story: play VaLora', 1080, 1920, f'''
<div style="position: absolute; left: 0; top: 0; width: 1080px; height: 600px; box-sizing: border-box; padding: 110px 72px 0; display: flex; flex-direction: column; gap: 18px">
{kicker('VaLora: Two Watchers', 22)}
<h1 style="margin: 0; font-family: {SERIF}; font-weight: 600; font-size: 112px; line-height: 0.95">Same sun.<br>Different skies.</h1>
<p style="margin: 0; font-size: 30px; line-height: 1.4; color: {MUTED}">Point and pinch to place screens, hedges and trees. Drag the sun. Live the day.</p>
</div>
{photo('story_th', 'The Bangkok island seen from above, with the raft of pieces on the canal', 'position: absolute; left: 0; top: 600px; width: 1080px; height: 1320px; object-position: center 22%')}
<div style="position: absolute; left: 64px; bottom: 120px; right: 64px; box-sizing: border-box; padding: 40px 52px; background: {PAPER}; border-radius: 28px; display: flex; flex-direction: column; gap: 18px">
<div style="font-size: 26px; color: {MUTED}">Play free in Quest Browser, or on any computer</div>
<div style="font-family: {SERIF}; font-size: 64px; font-weight: 600; line-height: 1">{URL}</div>
<div style="height: 1px; background: #d9d3c7"></div>
<div style="display: flex; align-items: center; justify-content: space-between; gap: 20px">
{logo(40)}
<div style="font-size: 20px; color: {MUTED}">Entry · Meta VR Start Developer Competition 2026</div>
</div>
</div>'''))

# 4. Landscape post (LinkedIn, X)
boards['Landscape.dc.html'] = (1200, 675, 'Landscape post (LinkedIn, X)', page('Landscape post', 1200, 675, f'''
{photo('hero_ph', 'The Manila island: a bahay kubo on stilts', 'position: absolute; left: 500px; top: 0; width: 700px; height: 675px')}
<div style="position: absolute; left: 0; top: 0; width: 500px; height: 675px; box-sizing: border-box; padding: 56px 48px; display: flex; flex-direction: column; justify-content: space-between">
<div style="display: flex; flex-direction: column; gap: 18px">
{kicker('Seated VR puzzle', 17)}
<h1 style="margin: 0; font-family: {SERIF}; font-weight: 600; font-size: 72px; line-height: 0.98">Same sun.<br>Different skies.</h1>
<p style="margin: 0; font-size: 21px; line-height: 1.45; color: {MUTED}">Sun, shade and privacy in Manila, Bangkok, Hanoi, Kuala Lumpur, Jakarta and Singapore. Each capital with its own house, its own sun path and its own watchers. Hands or Touch controllers.</p>
</div>
<div style="display: flex; flex-direction: column; gap: 14px">
{logo(36)}
<div style="font-size: 20px; font-weight: 500">{URL}</div>
</div>
</div>'''))

# 5-8. Carousel: one card per country
for (c, n, country, city, house, twist, more, levels) in COUNTRIES:
    chips = ''.join(f'<div style="padding: 10px 18px; border: 1px solid #cfc7b8; border-radius: 999px; font-size: 20px; font-weight: 500">{lv}</div>' for lv in levels)
    boards[f'Country-{c}.dc.html'] = (1080, 1350, f'Carousel {n}: {city}', page(f'{city}', 1080, 1350, f'''
{photo('hero_' + c, f'The {city} island', 'position: absolute; left: 0; top: 0; width: 1080px; height: 760px')}
<div style="position: absolute; left: 0; top: 760px; width: 1080px; height: 590px; box-sizing: border-box; padding: 52px 64px 56px; display: flex; flex-direction: column; justify-content: space-between">
<div style="display: flex; flex-direction: column; gap: 16px">
<div style="display: flex; align-items: baseline; justify-content: space-between">
{kicker(country)}
<div style="font-size: 20px; font-weight: 600; color: {BRONZE}">{n} / 04</div>
</div>
<h1 style="margin: 0; font-family: {SERIF}; font-weight: 600; font-size: 96px; line-height: 0.95">{city}</h1>
<p style="margin: 0; font-size: 26px; line-height: 1.4; color: {MUTED}">{house}</p>
<p style="margin: 0; font-size: 26px; line-height: 1.4"><span style="font-weight: 600">The watcher: {twist.lower() if c != 'sg' else 'the high-rise'}</span> {more}</p>
</div>
<div style="display: flex; flex-direction: column; gap: 28px">
<div style="display: flex; flex-wrap: wrap; gap: 12px">{chips}</div>
{footer()}
</div>
</div>'''))

# 9. How it plays
steps = [
    ('globe', '1', 'Choose a place', 'Spin the globe to Manila, Bangkok, Jakarta or Singapore.'),
    ('raft', '2', 'Place pieces', 'Point and pinch a screen, hedge, tree or pergola from the raft.'),
    ('sun', '3', 'Drag the sun', 'Each capital follows its own real sun path. Watch the shadows move.'),
    ('day', '4', 'Live the day', 'Every watcher checked hour by hour. Fewer pieces, more stars.'),
]
rows = ''.join(f'''<div style="display: flex; gap: 32px; align-items: center">
{photo('how_' + k, t, 'width: 360px; height: 220px; border-radius: 16px; flex-shrink: 0')}
<div style="display: flex; flex-direction: column; gap: 8px">
<div style="font-size: 20px; font-weight: 600; color: {BRONZE}">Step {num}</div>
<div style="font-family: {SERIF}; font-size: 48px; font-weight: 600; line-height: 1">{t}</div>
<div style="font-size: 22px; line-height: 1.4; color: {MUTED}">{d}</div>
</div>
</div>''' for (k, num, t, d) in steps)
boards['HowItPlays.dc.html'] = (1080, 1350, 'Carousel: how it plays', page('How it plays', 1080, 1350, f'''
<div style="box-sizing: border-box; width: 1080px; height: 1350px; padding: 64px; display: flex; flex-direction: column; justify-content: space-between">
<div style="display: flex; flex-direction: column; gap: 14px">
{kicker('Seated · hands only · no controllers')}
<h1 style="margin: 0; font-family: {SERIF}; font-weight: 600; font-size: 88px; line-height: 0.98">How it plays</h1>
</div>
<div style="display: flex; flex-direction: column; gap: 36px">{rows}</div>
{footer()}
</div>'''))

# 10. Competition entry, landscape (X, LinkedIn, YouTube community, Devpost): the six islands as a mosaic
DEMO = 'youtu.be/BQlZkN5x4PU'
TILES = [('ph', 'Manila', 'typhoon wind'), ('th', 'Bangkok', 'long-tail boats'), ('vn', 'Hanoi', 'motorbikes in the lane'),
         ('my', 'Kuala Lumpur', 'condo towers'), ('id', 'Jakarta', 'monsoon rain'), ('sg', 'Singapore', 'the high-rise')]
tiles = ''.join(f'''<div style="position: relative; border-radius: 20px; overflow: hidden; background: #e9e2d4">
{photo('hero_' + c, f'The {city} island', 'position: absolute; left: 0; top: 0; width: 100%; height: 100%')}
<div style="position: absolute; left: 14px; bottom: 14px; display: flex; align-items: baseline; gap: 8px; padding: 9px 16px; border-radius: 999px; background: {PAPER}; font-size: 17px; line-height: 1"><span style="font-weight: 600">{city}</span><span style="color: {MUTED}">{twist}</span></div>
</div>''' for c, city, twist in TILES)
pill = lambda t: f'<div style="padding: 9px 16px; border: 1px solid #cfc7b8; border-radius: 999px; font-size: 17px; font-weight: 500; white-space: nowrap">{t}</div>'
ico_play = f'<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="{BRONZE}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polygon points="10,8 16,12 10,16"></polygon></svg>'
ico_link = f'<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="{BRONZE}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 17L17 7"></path><path d="M8 7h9v9"></path></svg>'
boards['Entry.dc.html'] = (1600, 900, 'Competition entry (landscape)', page('Competition entry', 1600, 900, f'''
<div style="position: absolute; left: 0; top: 0; width: 620px; height: 900px; box-sizing: border-box; padding: 60px 52px 56px 64px; display: flex; flex-direction: column; justify-content: space-between">
<div style="display: flex; flex-direction: column; gap: 22px">
<div style="display: flex; flex-direction: column; gap: 8px">
{kicker('Our entry', 16)}
<div style="font-size: 21px; font-weight: 600">Meta VR Start Developer Competition 2026</div>
</div>
<div style="display: flex">{logo(46)}</div>
<h1 style="margin: 0; font-family: {SERIF}; font-weight: 600; font-size: 74px; line-height: 0.96">Let the sun in.<br>Keep the<br>watchers out.</h1>
<p style="margin: 0; font-size: 20px; line-height: 1.5; color: {MUTED}">A seated VR puzzle for Meta Quest across six Southeast Asian capitals, each with its own house, its own sun path and its own watchers. One player. The two watchers are the sun, and whoever looks in.</p>
<div style="display: flex; flex-wrap: wrap; gap: 10px">{pill('18 levels')}{pill('6 capitals')}{pill('Hands or Touch controllers')}{pill('WebXR · Quest Browser')}</div>
</div>
<div style="display: flex; flex-direction: column; gap: 14px; padding-top: 22px; border-top: 1px solid #ddd5c6">
<div style="display: flex; align-items: center; gap: 12px">{ico_link}<span style="font-size: 15px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: {BRONZE}; width: 72px">Play</span><span style="font-size: 21px; font-weight: 500; font-feature-settings: 'calt' 0, 'liga' 0, 'cv05' 1">{URL}</span></div>
<div style="display: flex; align-items: center; gap: 12px">{ico_play}<span style="font-size: 15px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: {BRONZE}; width: 72px">Demo</span><span style="font-size: 21px; font-weight: 500; font-feature-settings: 'calt' 0, 'liga' 0, 'cv05' 1">{DEMO}</span></div>
</div>
</div>
<div style="position: absolute; left: 620px; top: 28px; width: 952px; height: 844px; display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr 1fr; gap: 16px">
{tiles}
</div>'''))

for path, (w, h, title, html) in boards.items():
    open(os.path.join(P, path), 'w').write(html)


# canvas.json: social sizes grouped in rows
layout = [
    ['Main.dc.html', 'Landscape.dc.html', 'Entry.dc.html'],
    ['Islands.dc.html', 'HowItPlays.dc.html', 'Story.dc.html'],
    ['Country-ph.dc.html', 'Country-th.dc.html', 'Country-id.dc.html', 'Country-sg.dc.html'],
]
bx = {}
y = 0
for row in layout:
    x = 0
    rh = 0
    for p in row:
        w, h, title, _ = boards[p]
        bx[p] = {'x': x, 'y': y, 'w': w, 'h': h, 'title': title}
        x += w + 80
        rh = max(rh, h)
    y += rh + 360
canvas = {
    'v': 3,
    'createdOnFiles': {'v': 1, 'at': '2026-11-08T10:23:51Z'},  # when the canvas was first made
    'title': 'VaLora social media graphics',
    'launch': {'view': 'canvas'},
    'pages': [],
    'boards': bx,
    'order': [p for row in layout for p in row],
    'notes': {
        'row1': {'x': 0, 'y': -260, 'text': 'Launch posts and the competition entry', 'kind': 'title1', 'maxW': 4040},
        'row2': {'x': 0, 'y': bx['Islands.dc.html']['y'] - 260, 'text': 'Four islands, how it plays, story', 'kind': 'title1', 'maxW': 3400},
        'row3': {'x': 0, 'y': bx['Country-ph.dc.html']['y'] - 260, 'text': 'Carousel: one slide per country', 'kind': 'title1', 'maxW': 4560},
    },
    'designSystems': [],
}
open(os.path.join(P, 'canvas.json'), 'w').write(json.dumps(canvas, indent=1))
print('wrote', len(boards), 'artboards')
