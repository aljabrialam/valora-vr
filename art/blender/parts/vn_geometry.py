# ================================================================ VIETNAM: a northern village house, Hanoi
# Inside what src/sim checks: room x -5..5, z -7..-3 with solid north, west and east sides to 3 m,
# a roof plane at 3 m, an open courtyard face (no posts for x 0..3.3); the reader's eye 1.05 m at
# (1.6, -3.5); garden walls 1.1 m; the neighbour inside its box below 4.6 m.
#   the house: nha ba gian, three bays and two wings, like the old houses of Duong Lam. Laterite
#   (da ong) walls, dark lim-wood columns on stone bases along the open front, folding panel doors
#   (cua bức bàn) pushed back, an ancestral altar with a lacquered board, a curved fish-scale tiled
#   hip roof with lifted corners and a moulded ridge. Its courtyard eave stops at z -2.9.
#   the yard: san gach, Bat Trang terracotta tiles; a lotus pond on the pool spot; chum water jars.
#   outside: a lakeside lane where the motorbikes run, a flower seller's bicycle, a street tea stall
#   with plastic stools, a power pole with its tangle, and a Hanoi tube house next door.

PLINTH = 0.3
WALL_H = 1.1


def _laterite(nt, bsdf, coord):
    # da ong: porous ochre-brown blocks, pitted, in thin pale joints
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (2.6, 2.6, 2.6)
    nt.links.new(coord.outputs['Object'], mp.inputs['Vector'])
    br = nt.nodes.new('ShaderNodeTexBrick')
    br.inputs['Color1'].default_value = (*S('#a8673a'), 1)
    br.inputs['Color2'].default_value = (*S('#8f5530'), 1)
    br.inputs['Mortar'].default_value = (*S('#cbb79a'), 1)
    br.inputs['Scale'].default_value = 1.0
    br.inputs['Mortar Size'].default_value = 0.02
    br.inputs['Brick Width'].default_value = 0.42
    br.inputs['Row Height'].default_value = 0.2
    nt.links.new(mp.outputs['Vector'], br.inputs['Vector'])
    v = nt.nodes.new('ShaderNodeTexVoronoi')
    v.inputs['Scale'].default_value = 38.0
    nt.links.new(coord.outputs['Object'], v.inputs['Vector'])
    r = nt.nodes.new('ShaderNodeValToRGB')
    r.color_ramp.elements[0].position = 0.0
    r.color_ramp.elements[1].position = 0.18
    nt.links.new(v.outputs['Distance'], r.inputs['Fac'])
    c = mix(nt, r.outputs['Color'], rgb(nt, S('#5c3520')), br.outputs['Color'])
    c = mix(nt, noise(nt, coord, 0.9, 2, 0.5), c, rgb(nt, S('#9a7a5a')))
    nt.links.new(tint(nt, c), bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.95


def _ngoi(nt, bsdf, coord):
    # ngoi vay ca: small fish-scale tiles, aged red-brown with grey lichen in patches
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (5.0, 5.0, 5.0)
    nt.links.new(coord.outputs['Object'], mp.inputs['Vector'])
    br = nt.nodes.new('ShaderNodeTexBrick')
    br.inputs['Color1'].default_value = (*S('#a24a2a'), 1)
    br.inputs['Color2'].default_value = (*S('#8a3d24'), 1)
    br.inputs['Mortar'].default_value = (*S('#4a2014'), 1)
    br.inputs['Scale'].default_value = 1.0
    br.inputs['Mortar Size'].default_value = 0.03
    br.inputs['Brick Width'].default_value = 0.22
    br.inputs['Row Height'].default_value = 0.16
    nt.links.new(mp.outputs['Vector'], br.inputs['Vector'])
    n = noise(nt, coord, 0.7, 3, 0.6)
    r = nt.nodes.new('ShaderNodeValToRGB')
    r.color_ramp.elements[0].position = 0.64
    r.color_ramp.elements[1].position = 0.78
    nt.links.new(n, r.inputs['Fac'])
    c = mix(nt, noise(nt, coord, 3.0, 2, 0.5), br.outputs['Color'], rgb(nt, S('#b45a34')))
    c = mix(nt, r.outputs['Color'], c, rgb(nt, S('#8a8470')))
    nt.links.new(tint(nt, c), bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.8


def _battrang(nt, bsdf, coord):
    # Bat Trang yard tiles: 30 cm terracotta squares in thin dark joints, sun-faded unevenly
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (2.2, 2.2, 2.2)
    nt.links.new(coord.outputs['Object'], mp.inputs['Vector'])
    br = nt.nodes.new('ShaderNodeTexBrick')
    br.offset = 0.0
    br.inputs['Color1'].default_value = (*S('#c8714a'), 1)
    br.inputs['Color2'].default_value = (*S('#b9603c'), 1)
    br.inputs['Mortar'].default_value = (*S('#7a4a34'), 1)
    br.inputs['Scale'].default_value = 1.0
    br.inputs['Mortar Size'].default_value = 0.02
    br.inputs['Brick Width'].default_value = 1.0
    br.inputs['Row Height'].default_value = 1.0
    nt.links.new(mp.outputs['Vector'], br.inputs['Vector'])
    c = mix(nt, noise(nt, coord, 1.2, 3, 0.5), br.outputs['Color'], rgb(nt, S('#d8a07a')))
    nt.links.new(tint(nt, c), bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.85


def _lim(nt, bsdf, coord):
    # lim wood: near-black brown with a satin sheen and long grain
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (3, 3, 30)
    nt.links.new(coord.outputs['Object'], mp.inputs['Vector'])
    n = nt.nodes.new('ShaderNodeTexNoise')
    n.inputs['Scale'].default_value = 1.0
    n.inputs['Detail'].default_value = 5
    nt.links.new(mp.outputs['Vector'], n.inputs['Vector'])
    c = mix(nt, n.outputs['Fac'], rgb(nt, S('#2e1c12')), rgb(nt, S('#5a3a24')))
    nt.links.new(tint(nt, c), bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.45


MATS.update({
    'laterite': node_mat('laterite', _laterite),
    'ngoi': node_mat('ngoi', _ngoi),
    'battrang': node_mat('battrang', _battrang),
    'lim': node_mat('lim', _lim),
    'lacquer': node_mat('lacquer', flat(S('#9b1d1a'), 0.25)),
    'gold': node_mat('gold', flat(S('#d0a540'), 0.3, 0.7)),
    'lime': node_mat('lime', card(S('#efe6d2'), 0.04)),
    'bluestone': node_mat('bluestone', card(S('#6f7470'), 0.07)),
    'glaze': node_mat('glaze', flat(S('#5b3b2a'), 0.25)),
    'lotus': node_mat('lotus', flat(S('#f19bb5'), 0.5)),
    'lotusleaf': node_mat('lotusleaf', card(S('#4f8f45'), 0.08)),
    'water-bed': node_mat('water-bed', flat(S('#355f52'), 0.5)),
    'plastic-red': node_mat('plastic-red', flat(S('#d8332d'), 0.35)),
    'plastic-blue': node_mat('plastic-blue', flat(S('#2f6fc4'), 0.35)),
    'tube-yellow': node_mat('tube-yellow', _plaster(S('#f1cf6e'))),
    'shutter': node_mat('shutter', flat(S('#2f7a57'), 0.55)),
    'pole-concrete': node_mat('pole-concrete', card(S('#bdb8ad'), 0.05)),
    'wire': node_mat('wire', flat(S('#1d1d1f'), 0.6)),
    'bike': node_mat('bike', flat(S('#2b4a6b'), 0.4, 0.4)),
    'basket': node_mat('basket', card(S('#b98a4e'), 0.08)),
    'bougain': node_mat('bougain', flat(S('#d0388a'), 0.6)),
})

R = LAY['room']
C = LAY['court']
N = LAY['neighbour']
sx, _, sz = LAY['seat']
pool = {'x0': -4.3, 'x1': -1.6, 'z0': 0.3, 'z1': 2.9}

# ================================================================ the yard: Bat Trang tiles, lotus pond, jars
box(C['x0'], C['x1'], -0.04, 0.03, C['z0'], C['z1'], 'battrang', bevel=0.0, name='yard')
# a lotus pond on the pool spot: a bluestone kerb, dark water, round leaves and pink flowers
box(pool['x0'], pool['x1'], -0.45, -0.25, pool['z0'], pool['z1'], 'water-bed', bevel=0.0, name='pond-bed')
for (a, b, c, d) in ((pool['x0'] - 0.22, pool['x1'] + 0.22, pool['z0'] - 0.22, pool['z0']), (pool['x0'] - 0.22, pool['x1'] + 0.22, pool['z1'], pool['z1'] + 0.22), (pool['x0'] - 0.22, pool['x0'], pool['z0'], pool['z1']), (pool['x1'], pool['x1'] + 0.22, pool['z0'], pool['z1'])):
    box(a, b, -0.45, 0.14, c, d, 'bluestone', bevel=0.03, tint_c=jitter((1, 1, 1), 0.06), name='pond-kerb')
k_ = random.Random(21)
for i in range(9):
    lx, lz = k_.uniform(pool['x0'] + 0.35, pool['x1'] - 0.35), k_.uniform(pool['z0'] + 0.35, pool['z1'] - 0.35)
    r = k_.uniform(0.18, 0.32)
    pole((lx, 0.06, lz), (lx, 0.075, lz), r, 'lotusleaf', seg=14, tint_c=jitter((1, 1, 1), 0.12), name='lotus-leaf')
for (lx, lz, h) in ((-3.5, 1.0, 0.45), (-2.4, 2.1, 0.38), (-3.1, 2.5, 0.3)):
    pole((lx, 0.07, lz), (lx, h, lz), 0.012, 'lotusleaf', seg=5, name='lotus-stem')
    blob(lx, h + 0.06, lz, 0.1, 'lotus', jitter((1, 1, 1), 0.06), squash=1.1, seed=int(lx * 30), name='lotus-bud')
# chum jars: big glazed clay rain jars with wooden lids, by the east wall
for (x, z, r) in ((4.45, -2.3, 0.36), (4.5, -1.35, 0.3), (4.4, 3.4, 0.33)):
    solid([[(x + math.cos(a) * rr, y, z + math.sin(a) * rr) for a in [i / 14 * math.tau for i in range(14)]] for (y, rr) in ((0.0, r * 0.62), (0.18, r * 0.92), (0.42, r), (0.68, r * 0.86), (0.82, r * 0.6), (0.86, r * 0.62))], 'glaze', jitter((1, 1, 1), 0.08), name='chum')
    pole((x, 0.86, z), (x, 0.9, z), r * 0.68, 'lim', seg=14, tint_c=(1.5, 1.4, 1.3), name='chum-lid')
# a stone table with two stools on the tile, at the table spot (top 0.75 m), a tea tray on it
tx, tz = 2.6, 2.6
pole((tx, 0.0, tz), (tx, 0.7, tz), 0.16, 'bluestone', seg=12, r2=0.12, name='table-foot')
pole((tx, 0.7, tz), (tx, 0.77, tz), 0.62, 'bluestone', seg=20, tint_c=(1.12, 1.12, 1.12), name='table-top')
for dx in (-0.95, 0.95):
    pole((tx + dx, 0.0, tz), (tx + dx, 0.44, tz), 0.2, 'bluestone', seg=12, r2=0.17, name='stool')
box(tx - 0.2, tx + 0.2, 0.77, 0.79, tz - 0.14, tz + 0.14, 'lim', bevel=0.01, name='tea-tray')
pole((tx, 0.79, tz), (tx, 0.9, tz), 0.06, 'lime', seg=10, tint_c=(0.85, 0.9, 1.0), name='teapot')
for dx in (-0.12, 0.12):
    pole((tx + dx, 0.79, tz + 0.08), (tx + dx, 0.83, tz + 0.08), 0.025, 'lime', seg=8, name='cup')
# bonsai in glazed pots along the front of the house, low enough to stay under every sight line
for (x, z) in ((-4.3, -2.55), (-0.6, -2.55), (4.1, -2.55)):
    box(x - 0.28, x + 0.28, 0.0, 0.3, z - 0.18, z + 0.18, 'glaze', bevel=0.04, tint_c=(0.55, 0.75, 0.95), name='bonsai-pot')
    pole((x, 0.3, z), (x + 0.1, 0.55, z), 0.04, 'lim', seg=6, name='bonsai-trunk')
    blob(x + 0.12, 0.6, z, 0.2, 'leaf', jitter((0.9, 1.0, 0.9), 0.08), squash=0.55, seed=int(x * 11), name='bonsai')

# ================================================================ the house: plinth, laterite walls, lim columns
box(R['x0'] - 0.35, R['x1'] + 0.35, -0.02, PLINTH, R['z0'] - 0.35, R['z1'] + 0.3, 'bluestone', bevel=0.03, name='plinth')
box(R['x0'] - 0.1, R['x1'] + 0.1, PLINTH, PLINTH + 0.02, R['z0'] - 0.1, R['z1'] + 0.1, 'battrang', bevel=0.0, tint_c=(0.92, 0.88, 0.85), name='floor')
for (nm, a, b, c, d) in (('n', R['x0'], R['x1'], R['z0'] - 0.12, R['z0'] + 0.12), ('w', R['x0'] - 0.12, R['x0'] + 0.12, R['z0'], R['z1']), ('e', R['x1'] - 0.12, R['x1'] + 0.12, R['z0'], R['z1'])):
    box(a, b, PLINTH, 3.0, c, d, 'laterite', bevel=0.02, name='wall-' + nm)
    box(a - 0.02, b + 0.02, 2.82, 3.0, c - 0.02, d + 0.02, 'lime', bevel=0.01, name='wall-band')
# round vents high in the side walls, a carved window in each wing
for z in (-6.0, -4.0):
    for xw in (R['x0'] - 0.13, R['x1'] + 0.13):
        pole((xw - 0.02, 2.3, z), (xw + 0.02, 2.3, z), 0.2, 'lim', seg=16, name='vent')
# lim columns on bluestone bases along the open front, and two inner rows that carry the roof
FRONT = (R['x0'] + 0.15, -3.3, -1.6, 3.4, R['x1'] - 0.15)
for x in FRONT:
    pole((x, PLINTH, R['z1'] + 0.05), (x, PLINTH + 0.22, R['z1'] + 0.05), 0.2, 'bluestone', seg=12, r2=0.17, tint_c=(1.1, 1.1, 1.1), name='chan-tang')
    pole((x, PLINTH + 0.22, R['z1'] + 0.05), (x, 3.0, R['z1'] + 0.05), 0.11, 'lim', seg=12, r2=0.1, name='column')
for x in (-3.3, -1.6, 1.6, 3.4):
    for z in (-6.3, -4.5):
        pole((x, PLINTH, z), (x, PLINTH + 0.22, z), 0.22, 'bluestone', seg=12, r2=0.18, tint_c=(1.1, 1.1, 1.1), name='chan-tang')
        pole((x, PLINTH + 0.22, z), (x, 3.7 if z > -5 else 4.3, z), 0.13, 'lim', seg=12, r2=0.12, name='cot-cai')
box(R['x0'], R['x1'], 2.86, 3.0, R['z1'] - 0.08, R['z1'] + 0.12, 'lim', bevel=0.015, name='front-beam')
for x in (-3.3, -1.6, 1.6, 3.4):  # tie beams across, with a carved bracket under each end
    box(x - 0.07, x + 0.07, 2.8, 2.98, R['z0'] + 0.1, R['z1'], 'lim', bevel=0.01, name='tie-beam')
    obox((x, 2.62, R['z1'] - 0.25), (0.08, 0.35, 0.45), (0, 0, 0), 'lim', bevel=0.03, name='bracket')
# folding panel doors pushed back against the wing columns (none on the open face for x 0..3.3)
for (x0, x1) in ((R['x0'] + 0.25, -3.4), (-3.2, -1.7), (3.5, R['x1'] - 0.25)):
    n = 4
    w = (x1 - x0) / n
    for i in range(n):
        xa = x0 + i * w
        z = R['z1'] - 0.35 - (i % 2) * 0.12
        box(xa + 0.02, xa + w - 0.02, PLINTH + 0.05, 2.75, z - 0.03, z + 0.03, 'lim', bevel=0.01, tint_c=(1.2, 1.15, 1.1), name='door-leaf')
        for y in (0.9, 1.8):
            box(xa + 0.08, xa + w - 0.08, y, y + 0.55, z + 0.03, z + 0.05, 'lim', bevel=0.005, tint_c=(1.5, 1.4, 1.3), name='door-panel')

# ---- the ancestral altar on the north wall: a tall red-and-gold altar table, a lacquered board above
ax = 0.0
box(ax - 1.1, ax + 1.1, PLINTH, PLINTH + 1.05, R['z0'] + 0.15, R['z0'] + 0.75, 'lacquer', bevel=0.03, name='altar')
box(ax - 1.15, ax + 1.15, PLINTH + 1.05, PLINTH + 1.12, R['z0'] + 0.12, R['z0'] + 0.8, 'gold', bevel=0.02, name='altar-top')
box(ax - 0.9, ax + 0.9, PLINTH + 0.25, PLINTH + 0.85, R['z0'] + 0.76, R['z0'] + 0.78, 'gold', bevel=0.0, tint_c=(0.8, 0.75, 0.7), name='altar-carving')
pole((ax, PLINTH + 1.12, R['z0'] + 0.45), (ax, PLINTH + 1.32, R['z0'] + 0.45), 0.13, 'gold', seg=12, r2=0.1, name='censer')
for dx in (-0.6, 0.6):
    pole((ax + dx, PLINTH + 1.12, R['z0'] + 0.45), (ax + dx, PLINTH + 1.55, R['z0'] + 0.45), 0.035, 'gold', seg=8, name='candlestick')
    blob(ax + dx * 1.3, PLINTH + 1.3, R['z0'] + 0.4, 0.13, 'flower', (1.0, 0.75, 0.2), squash=0.8, seed=int(dx * 10 + 50), name='marigold')
box(ax - 1.2, ax + 1.2, 2.2, 2.65, R['z0'] + 0.13, R['z0'] + 0.18, 'lacquer', bevel=0.02, name='hoanh-phi')
box(ax - 1.05, ax + 1.05, 2.3, 2.55, R['z0'] + 0.18, R['z0'] + 0.2, 'gold', bevel=0.0, name='hoanh-phi-script')
for dx in (-1.45, 1.45):
    box(ax + dx - 0.12, ax + dx + 0.12, 0.8, 2.55, R['z0'] + 0.13, R['z0'] + 0.17, 'lacquer', bevel=0.01, name='cau-doi')
    box(ax + dx - 0.07, ax + dx + 0.07, 0.9, 2.45, R['z0'] + 0.17, R['z0'] + 0.19, 'gold', bevel=0.0, name='cau-doi-script')
# the reader's corner: a lim chair and a small tea table on a rush mat, a sap go platform behind
box(sx - 1.1, sx + 1.1, PLINTH + 0.02, PLINTH + 0.03, sz - 1.3, sz + 0.25, 'banig', bevel=0.0, tint_c=(0.85, 0.8, 0.6), name='mat')
box(sx - 0.28, sx + 0.28, 0.5, 0.56, sz - 0.3, sz + 0.22, 'lim', bevel=0.02, name='chair-seat')
box(sx - 0.28, sx + 0.28, 0.56, 1.1, sz - 0.34, sz - 0.27, 'lim', bevel=0.02, name='chair-back')
for dx in (-0.24, 0.24):
    for dz in (-0.28, 0.18):
        box(sx + dx - 0.03, sx + dx + 0.03, PLINTH, 0.5, sz + dz - 0.03, sz + dz + 0.03, 'lim', bevel=0.005, name='chair-leg')
box(sx + 0.55, sx + 1.05, PLINTH, PLINTH + 0.4, sz - 0.5, sz, 'lim', bevel=0.02, name='side-table')
pole((sx + 0.8, PLINTH + 0.4, sz - 0.25), (sx + 0.8, PLINTH + 0.52, sz - 0.25), 0.055, 'lime', seg=10, tint_c=(0.85, 0.9, 1.0), name='teapot')
box(-4.4, -2.3, PLINTH, PLINTH + 0.5, -6.6, -5.2, 'lim', bevel=0.04, name='sap-go')
box(-4.45, -2.25, PLINTH + 0.5, PLINTH + 0.56, -6.65, -5.15, 'lim', bevel=0.02, tint_c=(1.25, 1.2, 1.1), name='sap-top')
box(3.0, 4.4, PLINTH, PLINTH + 0.9, -6.75, -6.25, 'lim', bevel=0.03, name='chest')
box(3.05, 4.35, PLINTH + 0.25, PLINTH + 0.75, -6.25, -6.23, 'gold', bevel=0.0, tint_c=(0.7, 0.6, 0.5), name='chest-inlay')

# ================================================================ the roof: a curved hip roof in fish-scale tile
TH = 0.12
E = (R['x0'] - 1.0, R['x1'] + 1.0, R['z0'] - 0.85, R['z1'] + 0.1)  # eave, z1 = -2.9
EY = 3.0
RG = (-2.8, 2.8, -5.0, 5.7)  # ridge x0, x1, z, y
LIFT = 0.4  # corners turn up


def roof_ring(t, n=10):
    """One ring of the roof surface: t 0 at the eave, 1 at the ridge. A concave profile (steeper
    near the ridge), each side's corners lifted, the lift fading towards the ridge."""
    x0 = E[0] + (RG[0] - E[0]) * t
    x1 = E[1] + (RG[1] - E[1]) * t
    z0 = E[2] + (RG[2] - E[2]) * t
    z1 = E[3] + (RG[2] - E[3]) * t
    y = EY + (RG[3] - EY) * (t ** 1.45)
    out = []
    sides = (((x0, z1), (x1, z1)), ((x1, z1), (x1, z0)), ((x1, z0), (x0, z0)), ((x0, z0), (x0, z1)))
    for (a, b) in sides:
        for i in range(n):
            u = i / n
            px, pz = a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u
            corner = abs(2 * u - 1) if i else 1.0
            out.append((px, y + LIFT * (1 - t) ** 1.5 * corner ** 4, pz))
    return out


rings = [roof_ring(t) for t in (0.0, 0.18, 0.36, 0.54, 0.72, 0.88, 1.0)]
solid([[(p[0], p[1] + TH, p[2]) for p in r_] for r_ in rings], 'ngoi', (1, 1, 1), name='roof', cap_top=False, cap_bottom=False)
solid([rings[0], [(p[0], p[1] + TH, p[2]) for p in rings[0]]], 'lim', (1, 1, 1), name='roof-edge', cap_top=False, cap_bottom=False)
solid(rings, 'lim', (0.8, 0.8, 0.8), name='roof-under', cap_top=False, cap_bottom=False)
# the moulded ridge (bo noc) in lime plaster with curled ends, and hip ridges down to the lifted corners
box(RG[0] - 0.2, RG[1] + 0.2, RG[3] + TH - 0.02, RG[3] + TH + 0.26, RG[2] - 0.14, RG[2] + 0.14, 'lime', bevel=0.04, name='ridge')
box(RG[0] + 0.2, RG[1] - 0.2, RG[3] + TH + 0.26, RG[3] + TH + 0.34, RG[2] - 0.06, RG[2] + 0.06, 'ngoi', bevel=0.02, tint_c=(0.7, 0.7, 0.7), name='ridge-cap')
for s_ in (-1, 1):
    xe = RG[1] + 0.2 if s_ > 0 else RG[0] - 0.2
    for k in range(6):  # a curl rising out of each ridge end
        a0, a1 = k / 6 * 2.2, (k + 1) / 6 * 2.2
        p0 = (xe + s_ * 0.35 * math.sin(a0), RG[3] + TH + 0.2 + 0.35 * (1 - math.cos(a0)), RG[2])
        p1 = (xe + s_ * 0.35 * math.sin(a1), RG[3] + TH + 0.2 + 0.35 * (1 - math.cos(a1)), RG[2])
        pole(p0, p1, 0.09 - k * 0.008, 'lime', seg=8, name='ridge-curl')
for (cx, cz, rx) in ((E[0], E[3], RG[0]), (E[1], E[3], RG[1]), (E[1], E[2], RG[1]), (E[0], E[2], RG[0])):
    pts = []
    for k in range(7):
        t = k / 6
        x = cx + (rx - cx) * t
        z = cz + (RG[2] - cz) * t
        y = EY + (RG[3] - EY) * (t ** 1.45) + LIFT * (1 - t) ** 1.5 + TH + 0.05
        pts.append((x, y, z))
    for p, q in zip(pts, pts[1:]):
        pole(p, q, 0.07, 'lime', seg=6, name='hip')
    pole(pts[0], (pts[0][0] + (0.25 if cx > 0 else -0.25), pts[0][1] + 0.28, pts[0][2] + (0.25 if cz > -5 else -0.25)), 0.06, 'lime', seg=6, r2=0.02, name='dau-dao')

# ================================================================ laterite garden walls, 1.1 m, tiled coping
for key in ('east garden wall', 'south garden wall', 'west garden wall'):
    b = BOX[key]
    x0, x1 = b['c'][0] - b['h'][0], b['c'][0] + b['h'][0]
    z0, z1 = b['c'][2] - b['h'][2], b['c'][2] + b['h'][2]
    box(x0, x1, 0.0, WALL_H - 0.1, z0, z1, 'laterite', bevel=0.01, name='garden-wall')
    box(x0 - 0.06, x1 + 0.06, WALL_H - 0.1, WALL_H, z0 - 0.06, z1 + 0.06, 'ngoi', bevel=0.02, tint_c=(0.85, 0.85, 0.85), name='coping')

# ================================================================ outside: the lane, stall, flower bike, power pole
# kerbside: a row of young sau trees would shade the lane; keep it open, with low shrubs at the corners
for (x, z, r) in ((-6.6, 4.4, 0.4), (6.0, 4.5, 0.35), (-7.8, 3.2, 0.45), (13.2, 3.4, 0.4)):
    shrub(x, z, r, flowers=True)
# a street tea stall (tra da) west of the house: a low table and little plastic stools
box(-8.0, -7.3, 0.0, 0.35, 2.3, 2.8, 'plastic-blue', bevel=0.03, name='stall-table')
for (x, z, m) in ((-8.4, 2.1, 'plastic-red'), (-6.9, 2.3, 'plastic-blue'), (-8.3, 3.0, 'plastic-blue'), (-7.0, 3.05, 'plastic-red')):
    box(x - 0.16, x + 0.16, 0.0, 0.26, z - 0.16, z + 0.16, m, bevel=0.04, name='stool')
for dx in (-0.15, 0.1):
    pole((-7.65 + dx, 0.35, 2.55), (-7.65 + dx, 0.45, 2.55), 0.04, 'glass', seg=8, name='tea-glass')
# the flower seller's bicycle by the kerb, baskets full of flowers
bx, bz = 6.9, 4.65
for x in (bx - 0.55, bx + 0.55):
    pole((x, 0.33, bz - 0.03), (x, 0.33, bz + 0.03), 0.33, 'wire', seg=18, name='bike-wheel')
pole((bx - 0.55, 0.33, bz), (bx + 0.1, 0.75, bz), 0.025, 'bike', name='bike-frame')
pole((bx + 0.1, 0.75, bz), (bx + 0.55, 0.33, bz), 0.025, 'bike', name='bike-frame')
pole((bx + 0.45, 0.95, bz - 0.25), (bx + 0.45, 0.95, bz + 0.25), 0.02, 'bike', name='bike-bar')
for (x, w) in ((bx - 0.75, 0.55), (bx + 0.75, 0.4)):
    box(x - w / 2, x + w / 2, 0.55, 0.85, bz - 0.28, bz + 0.28, 'basket', bevel=0.05, name='basket')
    for i in range(9):
        a = i / 9 * math.tau
        blob(x + math.cos(a) * w * 0.32, 0.9 + (i % 3) * 0.05, bz + math.sin(a) * 0.2, 0.08, 'flower', rnd.choice([(1.0, 1.0, 1.0), (1.0, 0.75, 0.2), (1.0, 0.55, 0.9), (1.4, 1.4, 1.4)]), squash=0.8, seed=200 + i, name='bike-flower')
# a concrete power pole on the corner and its famous tangle, running east along the lane
PPX, PPZ = 5.9, 4.9
pole((PPX, 0.0, PPZ), (PPX, 6.4, PPZ), 0.14, 'pole-concrete', seg=8, r2=0.1, name='power-pole')
box(PPX - 0.55, PPX + 0.55, 5.9, 6.0, PPZ - 0.06, PPZ + 0.06, 'pole-concrete', bevel=0.01, name='cross-arm')


def wire(a, b, sag=0.35, r=0.012):
    pts = []
    for k in range(9):
        t = k / 8
        pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t - sag * math.sin(math.pi * t), a[2] + (b[2] - a[2]) * t))
    for p, q in zip(pts, pts[1:]):
        pole(p, q, r, 'wire', seg=4, name='wire')


for (dx, y) in ((-0.45, 6.0), (-0.15, 6.0), (0.15, 6.0), (0.45, 6.0)):
    wire((PPX + dx, y, PPZ), (16.0, y - 0.3, PPZ + dx * 0.4), 0.5 + abs(dx))
for (dy, s_) in ((0.0, 0.3), (-0.15, 0.45), (-0.3, 0.6)):
    wire((PPX + 0.3, 5.6 + dy, PPZ), (PPX + 2.4, 4.3 + dy, 2.2), s_, 0.01)
for k in range(9):  # the tangle: loops of spare cable at mid height
    a0 = k / 9 * math.tau * 2
    pole((PPX + math.cos(a0) * 0.2, 4.4 + k * 0.04, PPZ + math.sin(a0) * 0.2), (PPX + math.cos(a0 + 0.9) * 0.2, 4.4 + k * 0.04, PPZ + math.sin(a0 + 0.9) * 0.2), 0.016, 'wire', seg=4, name='tangle')
# behind the house: areca palms and a bamboo clump, north of everything the sun can see
for (x, z, h) in ((-6.8, -7.6, 5.2), (-6.0, -8.6, 4.6), (6.2, -8.2, 5.0)):
    pole((x, 0.0, z), (x, h, z), 0.09, 'trunk', seg=8, r2=0.07, tint_c=(1.1, 1.05, 0.9), name='cau-trunk')
    for i in range(7):
        a = i / 7 * 360
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        obox((x + ca * 0.5, h + 0.05, z + sa * 0.5), (1.0, 0.025, 0.28), (0, -a, -25), 'leaf', tint_c=jitter((1.05, 1.1, 0.95), 0.1), name='cau-frond', taper=0.5)
for i in range(9):
    a = i / 9 * math.tau
    x, z = 3.0 + math.cos(a) * 0.5, -8.6 + math.sin(a) * 0.4
    pole((x, 0.0, z), (x + math.cos(a) * 0.5, 3.6 + (i % 3) * 0.4, z + math.sin(a) * 0.3), 0.04, 'bamboo', seg=6, tint_c=(0.75, 1.0, 0.6), name='tre')
    blob(x + math.cos(a) * 0.55, 3.5 + (i % 3) * 0.4, z + math.sin(a) * 0.35, 0.4, 'leaf', jitter((0.9, 1.05, 0.8), 0.1), squash=0.6, seed=300 + i, name='tre-leaf')
banana(-7.4, -5.6, seed=8)

# ================================================================ the neighbour: a Hanoi tube house (nha ong)
nh = BOX['neighbour house']
nx0, nx1 = nh['c'][0] - nh['h'][0], nh['c'][0] + nh['h'][0]
nz0, nz1 = nh['c'][2] - nh['h'][2], nh['c'][2] + nh['h'][2]
ny1 = nh['c'][1] + nh['h'][1]
GF = 2.3
box(nx0, nx1, 0.0, GF, nz0, nz1 - 0.5, 'lime', bevel=0.03, tint_c=(0.95, 0.93, 0.88), name='tube-ground')
box(nx0, nx1, GF, 4.2, nz0, nz1, 'tube-yellow', bevel=0.03, name='tube-upper')
box(nx0 - 0.05, nx1 + 0.05, 4.2, 4.45, nz0 - 0.05, nz1 + 0.05, 'lime', bevel=0.02, name='tube-parapet')
box(nx0 + 0.3, nx1 - 0.3, 4.45, ny1 - 0.02, nz0 + 0.4, nz0 + 1.6, 'ngoi', bevel=0.02, name='stair-roof')
# street front (south): a shop with a rolling shutter, French shutters and a balcony above
box(nx0 + 0.3, nx1 - 0.3, 0.0, 2.05, nz1 - 0.55, nz1 - 0.5, 'char', bevel=0.0, name='shop-dark')
box(nx0 + 0.25, nx1 - 0.25, 1.4, 2.1, nz1 - 0.5, nz1 - 0.44, 'gi', bevel=0.0, name='shutter-roll')
box(nx0 + 0.2, nx1 - 0.2, GF - 0.1, GF + 0.06, nz1, nz1 + 0.75, 'lime', bevel=0.02, name='balcony')
for k in range(16):
    xx = nx0 + 0.25 + k * (nx1 - nx0 - 0.5) / 15
    pole((xx, GF + 0.06, nz1 + 0.72), (xx, GF + 0.95, nz1 + 0.72), 0.014, 'wire', seg=4, name='balcony-rail')
pole((nx0 + 0.2, GF + 0.95, nz1 + 0.72), (nx1 - 0.2, GF + 0.95, nz1 + 0.72), 0.025, 'wire', seg=6, name='rail-top')
for x in (nx0 + 1.1, nx1 - 1.1):
    box(x - 0.45, x + 0.45, GF + 0.2, 3.95, nz1 + 0.01, nz1 + 0.04, 'char', bevel=0.0, name='tube-door')
    for s_ in (-1, 1):
        box(x + s_ * 0.45 - 0.2, x + s_ * 0.45 + 0.2, GF + 0.2, 3.95, nz1 + 0.04, nz1 + 0.08, 'shutter', bevel=0.01, name='french-shutter')
box(nx0 + 0.4, nx1 - 0.4, 2.0, 2.25, nz1 + 0.76, nz1 + 0.8, 'sign', bevel=0.01, tint_c=(1.0, 0.35, 0.3), name='shop-sign')
# bougainvillea spilling over the balcony, an air-conditioner and a water tank on the roof
for i in range(6):
    blob(nx0 + 0.6 + i * 0.6, GF + 0.85 + (i % 2) * 0.2, nz1 + 0.8, 0.28, 'bougain', jitter((1, 1, 1), 0.1), squash=0.7, seed=400 + i, name='bougainvillea')
box(nx0 - 0.4, nx0, 3.0, 3.45, -2.6, -1.8, 'trim', bevel=0.03, name='aircon')
pole((nx1 - 0.8, 4.45, nz0 + 2.6), (nx1 - 0.8, 4.55, nz0 + 2.6), 0.32, 'steel', seg=12, tint_c=(2.2, 2.2, 2.2), name='inox-tank')
# the side window the neighbour watches from, west face
wy, wz = N['window'][1], N['window'][2]
box(nx0 - 0.06, nx0 + 0.02, wy - 0.6, wy + 0.6, wz - 0.6, wz + 0.6, 'char', bevel=0.0, name='n-win-dark')
for s_ in (-1, 1):
    box(nx0 - 0.1, nx0 - 0.04, wy - 0.62, wy + 0.62, wz + s_ * 0.6 - (0.32 if s_ < 0 else 0), wz + s_ * 0.6 + (0.32 if s_ > 0 else 0), 'shutter', bevel=0.01, name='n-shutter')
box(nx0 - 0.7, nx0, wy - 1.68, wy - 1.56, wz - 0.9, wz + 0.9, 'lime', bevel=0.02, name='n-ledge')
