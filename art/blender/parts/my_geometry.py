# ================================================================ MALAYSIA: a kampung house, Kampung Baru, Kuala Lumpur
# Inside what src/sim checks: room x -5..5, z -7..-3 with solid north, west and east sides to 3 m,
# a roof plane at 3 m, an open courtyard face (no posts for x 0..3.3); the reader's eye 1.05 m at
# (1.6, -3.5); garden walls 1.0 m; the neighbour inside its box below 4.6 m.
#   the house: rumah Melayu on short timber stilts with a lattice skirt, plank walls painted mint
#   with white trim, tall louvred windows under fretwork vents, an open serambi (veranda) to the
#   yard with turned balusters at its ends, front steps with Peranakan tiles and a tempayan jar.
#   The long gable roof (bumbung panjang) is red zinc, with carved gable boards (tebar layar) and
#   barge boards whose tips curl up. Its courtyard eave stops at z -2.9.
#   inside: tikar mats, a kerusi malas (planter's chair) for the reader, a glass-front almari.
#   the yard: swept sand, a tiled pool, hibiscus (bunga raya), white plastered walls with a relief band.
#   next door: a two-storey kampung house, concrete below and timber above.

FL = 0.45  # floor on short stilts
WALL_H = 1.0


def _zinc(nt, bsdf, coord):
    # painted corrugated zinc: deep red ribs, faded and streaked toward the eaves
    w = nt.nodes.new('ShaderNodeTexWave')
    w.bands_direction = 'X'
    w.inputs['Scale'].default_value = 9.0
    nt.links.new(coord.outputs['Object'], w.inputs['Vector'])
    c = mix(nt, w.outputs['Fac'], rgb(nt, S('#7e1f18')), rgb(nt, S('#a52b20')))
    c = mix(nt, noise(nt, coord, 1.2, 3, 0.55), c, rgb(nt, S('#9a4a3a')))
    nt.links.new(tint(nt, c), bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.5
    bsdf.inputs['Metallic'].default_value = 0.2


def _planks(base):
    # painted horizontal weatherboards: a dark line at each lap, a little brush variation
    def build(nt, bsdf, coord):
        sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        nt.links.new(coord.outputs['Object'], sep.inputs['Vector'])
        m = nt.nodes.new('ShaderNodeMath')
        m.operation = 'FRACT'
        sc = nt.nodes.new('ShaderNodeMath')
        sc.operation = 'MULTIPLY'
        sc.inputs[1].default_value = 5.0  # 20 cm boards
        nt.links.new(sep.outputs['Z'], sc.inputs[0])
        nt.links.new(sc.outputs['Value'], m.inputs[0])
        r = nt.nodes.new('ShaderNodeValToRGB')
        r.color_ramp.elements[0].position = 0.0
        r.color_ramp.elements[1].position = 0.12
        nt.links.new(m.outputs['Value'], r.inputs['Fac'])
        c = mix(nt, noise(nt, coord, 8, 3, 0.5), rgb(nt, base), rgb(nt, tuple(v * 0.93 for v in base)))
        c = mix(nt, r.outputs['Color'], rgb(nt, tuple(v * 0.6 for v in base)), c)
        nt.links.new(tint(nt, c), bsdf.inputs['Base Color'])
        bsdf.inputs['Roughness'].default_value = 0.7
    return build


def _tiles(nt, bsdf, coord):
    # Peranakan step tiles: a small checker of rose, teal and cream
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (7, 7, 7)
    nt.links.new(coord.outputs['Object'], mp.inputs['Vector'])
    ch = nt.nodes.new('ShaderNodeTexChecker')
    ch.inputs['Scale'].default_value = 1.0
    ch.inputs['Color1'].default_value = (*S('#d9707a'), 1)
    ch.inputs['Color2'].default_value = (*S('#2f8f8a'), 1)
    nt.links.new(mp.outputs['Vector'], ch.inputs['Vector'])
    v = nt.nodes.new('ShaderNodeTexVoronoi')
    v.inputs['Scale'].default_value = 14.0
    nt.links.new(coord.outputs['Object'], v.inputs['Vector'])
    c = mix(nt, v.outputs['Distance'], rgb(nt, S('#f3e9d2')), ch.outputs['Color'])
    nt.links.new(c, bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.25


def _pooltile(nt, bsdf, coord):
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (8, 8, 8)
    nt.links.new(coord.outputs['Object'], mp.inputs['Vector'])
    br = nt.nodes.new('ShaderNodeTexBrick')
    br.offset = 0.0
    br.inputs['Color1'].default_value = (*S('#3fb3c9'), 1)
    br.inputs['Color2'].default_value = (*S('#35a3bb'), 1)
    br.inputs['Mortar'].default_value = (*S('#e8f4f2'), 1)
    br.inputs['Scale'].default_value = 1.0
    br.inputs['Mortar Size'].default_value = 0.04
    br.inputs['Brick Width'].default_value = 1.0
    br.inputs['Row Height'].default_value = 1.0
    nt.links.new(mp.outputs['Vector'], br.inputs['Vector'])
    nt.links.new(br.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.2


MATS.update({
    'zinc': node_mat('zinc', _zinc),
    'mint-plank': node_mat('mint-plank', _planks(S('#8fd1c1'))),
    'blue-plank': node_mat('blue-plank', _planks(S('#9cc3e6'))),
    'white': node_mat('white', card(S('#f6f2e8'), 0.03)),
    'stilt': node_mat('stilt', _weathered),
    'chengal': node_mat('chengal', flat(S('#6e4026'), 0.5)),
    'steptile': node_mat('steptile', _tiles),
    'pooltile': node_mat('pooltile', _pooltile),
    'water': node_mat('water', flat(S('#5fd0de'), 0.08)),
    'sand': node_mat('sand', card(S('#e7d3a6'), 0.06)),
    'rattan': node_mat('rattan', card(S('#c99a5a'), 0.08)),
    'canvas': node_mat('canvas', flat(S('#f1e6cc'), 0.8)),
    'songket': node_mat('songket', flat(S('#7a1f3d'), 0.4, 0.2)),
    'gold': node_mat('gold', flat(S('#d4aa45'), 0.3, 0.7)),
    'tempayan': node_mat('tempayan', flat(S('#4a3226'), 0.3)),
    'yellow': node_mat('yellow', _plaster(S('#f1d98a'))),
    'hibiscus': node_mat('hibiscus', flat(S('#e0233a'), 0.5)),
    'motor': node_mat('motor', flat(S('#1f5fa8'), 0.35, 0.2)),
})

R = LAY['room']
C = LAY['court']
N = LAY['neighbour']
sx, _, sz = LAY['seat']
pool = {'x0': -4.3, 'x1': -1.6, 'z0': 0.3, 'z1': 2.9}

# ================================================================ the yard: swept sand, a tiled pool, hibiscus
box(C['x0'], C['x1'], -0.04, 0.02, C['z0'], C['z1'], 'sand', bevel=0.0, name='yard')
box(pool['x0'], pool['x1'], -0.6, -0.08, pool['z0'], pool['z1'], 'pooltile', bevel=0.0, name='pool-shell')
box(pool['x0'] + 0.02, pool['x1'] - 0.02, -0.12, -0.06, pool['z0'] + 0.02, pool['z1'] - 0.02, 'water', bevel=0.0, name='pool-water')
for (a, b, c, d) in ((pool['x0'] - 0.25, pool['x1'] + 0.25, pool['z0'] - 0.25, pool['z0']), (pool['x0'] - 0.25, pool['x1'] + 0.25, pool['z1'], pool['z1'] + 0.25), (pool['x0'] - 0.25, pool['x0'], pool['z0'], pool['z1']), (pool['x1'], pool['x1'] + 0.25, pool['z0'], pool['z1'])):
    box(a, b, -0.1, 0.06, c, d, 'white', bevel=0.02, name='pool-coping')
# a garden table under a white umbrella frame at the table spot (top 0.75 m); stools of chengal
tx, tz = 2.6, 2.6
pole((tx, 0.0, tz), (tx, 0.72, tz), 0.05, 'chengal', seg=8, name='table-post')
pole((tx, 0.72, tz), (tx, 0.77, tz), 0.6, 'chengal', seg=20, tint_c=(1.2, 1.15, 1.1), name='table-top')
for dx in (-0.95, 0.95):
    box(tx + dx - 0.2, tx + dx + 0.2, 0.0, 0.45, tz - 0.2, tz + 0.2, 'chengal', bevel=0.03, name='stool')
for dx in (-0.1, 0.12):  # teh tarik in tall glasses
    pole((tx + dx, 0.77, tz - 0.05), (tx + dx, 0.92, tz - 0.05), 0.035, 'canvas', seg=8, tint_c=(0.85, 0.65, 0.42), name='teh-tarik')
# hibiscus (bunga raya) and pandan along the walls, low
for (x, z, r) in ((-4.5, 3.4, 0.38), (0.4, 3.5, 0.34), (4.4, 0.6, 0.36), (4.5, -1.8, 0.3)):
    shrub(x, z, r, flowers=False)
    for i in range(7):
        a = i / 7 * math.tau
        blob(x + math.cos(a) * r * 0.85, r * 0.6 + (i % 3) * 0.15, z + math.sin(a) * r * 0.85, 0.09, 'hibiscus', jitter((1, 1, 1), 0.06), squash=0.6, seed=500 + i + int(x * 10), name='bunga-raya')
for (x, z) in ((-0.9, 3.55), (-2.6, 3.55)):
    for i in range(10):
        a = i / 10 * math.tau
        obox((x + math.cos(a) * 0.18, 0.35, z + math.sin(a) * 0.12), (0.5, 0.02, 0.07), (0, -math.degrees(a), 55), 'leaf', tint_c=(0.85, 1.15, 0.7), name='pandan', taper=0.4)

# ================================================================ the house: stilts, skirt, plank walls
box(R['x0'] - 0.25, R['x1'] + 0.25, FL - 0.08, FL, R['z0'] - 0.25, R['z1'] + 0.15, 'chengal', bevel=0.02, name='floor-edge')
box(R['x0'] - 0.1, R['x1'] + 0.1, FL, FL + 0.02, R['z0'] - 0.1, R['z1'] + 0.1, 'chengal', bevel=0.0, tint_c=(1.25, 1.18, 1.1), name='floor')
# stilts on concrete footings, all round and through the middle
for x in (-4.9, -3.3, -1.6, 0.0, 1.6, 3.4, 4.9):
    for z in (-6.9, -5.0, -3.1):
        if z == -3.1 and 0.0 <= x <= 3.3:
            continue  # nothing on the open face in front of the reader
        box(x - 0.16, x + 0.16, 0.0, 0.14, z - 0.16, z + 0.16, 'white', bevel=0.03, tint_c=(0.85, 0.85, 0.85), name='footing')
        box(x - 0.08, x + 0.08, 0.14, FL - 0.08, z - 0.08, z + 0.08, 'stilt', bevel=0.01, name='stilt')
# lattice skirt between the stilts on the closed sides
for (a, b, z0, z1) in ((R['x0'], R['x1'], R['z0'] - 0.02, R['z0'] + 0.02), (R['x0'] - 0.02, R['x0'] + 0.02, R['z0'], R['z1']), (R['x1'] - 0.02, R['x1'] + 0.02, R['z0'], R['z1'])):
    box(a, b, 0.05, FL - 0.1, z0, z1, 'chengal', bevel=0.0, tint_c=(0.6, 0.55, 0.5), name='skirt')
    L0, L1 = (a, b) if (b - a) > (z1 - z0) else (z0, z1)
    t = L0 + 0.1
    while t < L1:
        if (b - a) > (z1 - z0):
            obox((t, FL / 2, z0 - 0.03), (0.04, FL * 0.9, 0.02), (0, 0, 45), 'white', name='kisi')
            obox((t, FL / 2, z0 - 0.03), (0.04, FL * 0.9, 0.02), (0, 0, -45), 'white', name='kisi')
        else:
            xx = a - 0.03 if a < 0 else b + 0.03
            obox((xx, FL / 2, t), (0.02, FL * 0.9, 0.04), (45, 0, 0), 'white', name='kisi')
            obox((xx, FL / 2, t), (0.02, FL * 0.9, 0.04), (-45, 0, 0), 'white', name='kisi')
        t += 0.28
for (nm, a, b, c, d) in (('n', R['x0'], R['x1'], R['z0'] - 0.06, R['z0'] + 0.06), ('w', R['x0'] - 0.06, R['x0'] + 0.06, R['z0'], R['z1']), ('e', R['x1'] - 0.06, R['x1'] + 0.06, R['z0'], R['z1'])):
    box(a, b, FL, 3.0, c, d, 'mint-plank', bevel=0.0, name='wall-' + nm)
    # white corner boards and a white band under the eave
    box(a - 0.03, b + 0.03, 2.82, 3.0, c - 0.03, d + 0.03, 'white', bevel=0.01, name='wall-band')
    box(a - 0.03, b + 0.03, FL, FL + 0.12, c - 0.03, d + 0.03, 'white', bevel=0.01, name='wall-sill')
for (x, z) in ((R['x0'], R['z0']), (R['x1'], R['z0']), (R['x0'], R['z1']), (R['x1'], R['z1'])):
    box(x - 0.1, x + 0.1, FL, 3.0, z - 0.1, z + 0.1, 'white', bevel=0.02, name='corner-post')


def jendela(face, c, w=0.9):
    """A tall window: louvred leaves folded open, a fretwork vent panel above."""
    y0, y1 = FL + 0.35, FL + 1.85
    if face in ('w', 'e'):
        xw = R['x0'] - 0.07 if face == 'w' else R['x1'] + 0.07
        sgn = -1 if face == 'w' else 1
        box(xw - 0.02, xw + 0.02, y0, y1, c - w / 2, c + w / 2, 'char', bevel=0.0, name='win-dark')
        box(xw - 0.04, xw + 0.04, y0 - 0.06, y1 + 0.06, c - w / 2 - 0.06, c + w / 2 + 0.06, 'white', bevel=0.01, tint_c=(1, 1, 1), name='win-frame')
        for s_ in (-1, 1):  # leaves opened flat against the wall
            box(xw + sgn * 0.02, xw + sgn * 0.06, y0, y1, c + s_ * (w / 2 + 0.06) - (w / 2 if s_ < 0 else 0), c + s_ * (w / 2 + 0.06) + (w / 2 if s_ > 0 else 0), 'chengal', bevel=0.01, tint_c=(1.3, 1.25, 1.2), name='win-leaf')
        box(xw - 0.03, xw + 0.03, y1 + 0.12, y1 + 0.45, c - w / 2, c + w / 2, 'white', bevel=0.0, name='vent-panel')
        for k in range(5):
            zz = c - w / 2 + (k + 0.5) * w / 5
            pole((xw + sgn * 0.04, y1 + 0.28, zz - 0.06), (xw + sgn * 0.04, y1 + 0.28, zz + 0.06), 0.08, 'chengal', seg=6, name='ukiran')
    else:
        zw = R['z0'] - 0.07
        box(c - w / 2, c + w / 2, y0, y1, zw - 0.02, zw + 0.02, 'char', bevel=0.0, name='win-dark')
        box(c - w / 2 - 0.06, c + w / 2 + 0.06, y0 - 0.06, y1 + 0.06, zw - 0.04, zw + 0.04, 'white', bevel=0.01, name='win-frame')
        box(c - w / 2, c + w / 2, y1 + 0.12, y1 + 0.45, zw - 0.03, zw + 0.03, 'white', bevel=0.0, name='vent-panel')


for z in (-6.0, -4.1):
    jendela('w', z)
    jendela('e', z)
for x in (-3.0, 3.0):
    jendela('n', x)

# ---- the serambi: open to the yard; front posts and turned balusters only at the ends
for x in (R['x0'] + 0.1, -3.3, -1.6, 3.4, R['x1'] - 0.1):
    box(x - 0.08, x + 0.08, FL, 3.0, R['z1'] - 0.08, R['z1'] + 0.08, 'white', bevel=0.02, name='serambi-post')
box(R['x0'], R['x1'], 2.84, 3.0, R['z1'] - 0.08, R['z1'] + 0.1, 'white', bevel=0.015, name='front-beam')
for (x0, x1) in ((R['x0'] + 0.2, -1.7), (3.5, R['x1'] - 0.2)):
    box(x0, x1, FL + 0.62, FL + 0.7, R['z1'] - 0.05, R['z1'] + 0.05, 'white', bevel=0.01, name='rail')
    t = x0 + 0.1
    while t < x1:
        pole((t, FL, R['z1']), (t, FL + 0.62, R['z1']), 0.03, 'white', seg=8, r2=0.022, name='baluster')
        t += 0.17
# a fretwork valance under the front beam, between the end posts only
for (x0, x1) in ((R['x0'] + 0.2, -1.7), (3.5, R['x1'] - 0.2)):
    box(x0, x1, 2.6, 2.84, R['z1'] - 0.02, R['z1'] + 0.02, 'white', bevel=0.0, name='valance')
    t = x0 + 0.15
    while t < x1:
        pole((t, 2.72, R['z1'] - 0.04), (t, 2.72, R['z1'] + 0.04), 0.06, 'chengal', seg=6, name='valance-hole')
        t += 0.3
# front steps with Peranakan tiled risers, and a tempayan jar with a dipper at their foot
for i in range(2):
    y = FL - (i + 1) * FL / 3
    z = R['z1'] + 0.28 + i * 0.28
    box(-3.1, -2.0, 0.0, y + 0.03, z - 0.14, z + 0.14, 'white', bevel=0.02, name='step')
    box(-3.08, -2.02, 0.02, y, z + 0.14, z + 0.15, 'steptile', bevel=0.0, name='step-tile')
solid([[(-3.75 + math.cos(a) * rr, y, -2.3 + math.sin(a) * rr) for a in [i / 14 * math.tau for i in range(14)]] for (y, rr) in ((0.0, 0.18), (0.2, 0.3), (0.45, 0.32), (0.62, 0.24), (0.68, 0.2))], 'tempayan', (1, 1, 1), name='tempayan')
pole((-3.75, 0.68, -2.3), (-3.75, 0.7, -2.3), 0.19, 'water', seg=14, name='tempayan-water')
# inside: tikar mats, the kerusi malas for the reader, an almari, a framed songket, a low table
box(sx - 1.3, sx + 1.1, FL + 0.02, FL + 0.03, sz - 1.6, sz + 0.3, 'banig', bevel=0.0, tint_c=(0.95, 0.8, 0.7), name='tikar')
box(-3.8, -1.2, FL + 0.02, FL + 0.03, -6.3, -4.6, 'banig', bevel=0.0, tint_c=(0.75, 0.9, 0.8), name='tikar')
obox((sx, FL + 0.35, sz - 0.05), (0.62, 0.05, 0.9), (-22, 0, 0), 'rattan', bevel=0.03, name='malas-seat')
obox((sx, FL + 0.62, sz - 0.5), (0.62, 0.05, 0.6), (-58, 0, 0), 'canvas', bevel=0.02, name='malas-back')
for s_ in (-1, 1):
    obox((sx + s_ * 0.32, FL + 0.42, sz - 0.1), (0.05, 0.05, 1.3), (-10, 0, 0), 'chengal', bevel=0.01, name='malas-arm')
    pole((sx + s_ * 0.3, FL, sz + 0.45), (sx + s_ * 0.3, FL + 0.32, sz + 0.4), 0.025, 'chengal', name='malas-leg')
    pole((sx + s_ * 0.3, FL, sz - 0.65), (sx + s_ * 0.3, FL + 0.55, sz - 0.6), 0.025, 'chengal', name='malas-leg')
box(sx + 0.6, sx + 1.15, FL, FL + 0.3, sz - 0.6, sz - 0.1, 'chengal', bevel=0.02, name='low-table')
box(3.0, 4.5, FL, FL + 1.9, -6.85, -6.35, 'chengal', bevel=0.03, name='almari')
box(3.1, 4.4, FL + 0.9, FL + 1.8, -6.36, -6.33, 'glass', bevel=0.0, name='almari-glass')
box(-0.9, 0.9, 1.35, 2.35, R['z0'] + 0.07, R['z0'] + 0.1, 'gold', bevel=0.0, name='frame')
box(-0.82, 0.82, 1.42, 2.28, R['z0'] + 0.1, R['z0'] + 0.11, 'songket', bevel=0.0, name='songket')

# ================================================================ the roof: bumbung panjang in red zinc
TH = 0.08
EY = 3.0
EZ0, EZ1 = R['z0'] - 0.9, R['z1'] + 0.1  # eaves; z1 = -2.9
GX0, GX1 = R['x0'] - 0.55, R['x1'] + 0.55  # gable ends
RZ, RY = (EZ0 + EZ1) / 2, 5.6
for (za, sgn) in ((EZ1, 1), (EZ0, -1)):
    # each slope is a thin slab: a closed cross-section swept from the eave up to the ridge
    def sec(x, y0, th):
        return [(x, y0, 0), (x, y0 + th, 0)]
    a0, a1 = (GX0, EY, za), (GX1, EY, za)
    b0, b1 = (GX0, RY, RZ), (GX1, RY, RZ)
    solid([[(a0[0], a0[1], a0[2]), (a1[0], a1[1], a1[2]), (a1[0], a1[1] + TH, a1[2]), (a0[0], a0[1] + TH, a0[2])],
           [(b0[0], b0[1], b0[2]), (b1[0], b1[1], b1[2]), (b1[0], b1[1] + TH, b1[2]), (b0[0], b0[1] + TH, b0[2])]], 'zinc', (1, 1, 1), name='roof')
    solid([[(a0[0], a0[1] - 0.04, a0[2]), (a1[0], a1[1] - 0.04, a1[2]), (a1[0], a1[1], a1[2]), (a0[0], a0[1], a0[2])],
           [(b0[0], b0[1] - 0.04, b0[2]), (b1[0], b1[1] - 0.04, b1[2]), (b1[0], b1[1], b1[2]), (b0[0], b0[1], b0[2])]], 'chengal', (0.8, 0.8, 0.8), name='roof-under')
    pole((GX0, EY + 0.02, za), (GX1, EY + 0.02, za), 0.05, 'white', seg=4, name='fascia')
pole((GX0 - 0.05, RY + TH + 0.04, RZ), (GX1 + 0.05, RY + TH + 0.04, RZ), 0.09, 'zinc', seg=6, tint_c=(0.8, 0.8, 0.8), name='ridge')
# the gables: tebar layar boards with fretwork, sun-ray battens, and barge boards curling at the tips
for gx in (GX0 + 0.05, GX1 - 0.05):
    out = -1 if gx < 0 else 1
    tri = lambda x: [(x, EY, EZ1 - 0.4), (x, EY, EZ0 + 0.4), (x, RY - 0.05, RZ)]
    solid([tri(gx - out * 0.02), tri(gx + out * 0.03)], 'white', (1, 1, 1), name='tebar-layar')
    for k in range(9):  # sun-ray battens fanning from the base centre
        a = math.radians(25 + k * 16.25)
        L = 1.9
        p0 = (gx + out * 0.04, EY + 0.15, RZ)
        p1 = (gx + out * 0.04, EY + 0.15 + math.sin(a) * L * 0.95, RZ + math.cos(a) * L * 1.25)
        pole(p0, p1, 0.025, 'mint-plank', seg=4, name='sinar')
    for (za, sg) in ((EZ1, 1), (EZ0, -1)):
        pts = [(gx + out * 0.12, RY + 0.15, RZ)]
        for k in range(1, 7):
            t = k / 6
            pts.append((gx + out * 0.12, RY + 0.15 + (EY - RY) * t, RZ + (za - RZ) * t))
        for p, q in zip(pts, pts[1:]):
            pole(p, q, 0.06, 'white', seg=6, name='barge')
        pole(pts[-1], (gx + out * 0.12, EY + 0.3, za + sg * 0.25), 0.05, 'white', seg=6, r2=0.02, name='barge-curl')
    pole((gx + out * 0.12, RY + 0.12, RZ), (gx + out * 0.12, RY + 0.75, RZ), 0.05, 'white', seg=6, r2=0.015, name='silang-gunting')

# ================================================================ garden walls: white plaster, a relief band, green cap
for key in ('east garden wall', 'south garden wall', 'west garden wall'):
    b = BOX[key]
    x0, x1 = b['c'][0] - b['h'][0], b['c'][0] + b['h'][0]
    z0, z1 = b['c'][2] - b['h'][2], b['c'][2] + b['h'][2]
    box(x0, x1, 0.0, WALL_H - 0.08, z0, z1, 'white', bevel=0.01, name='garden-wall')
    box(x0 - 0.05, x1 + 0.05, WALL_H - 0.08, WALL_H, z0 - 0.05, z1 + 0.05, 'leaf', bevel=0.02, tint_c=(0.55, 0.85, 0.65), name='coping')
    along_x = (x1 - x0) > (z1 - z0)
    L0, L1 = (x0, x1) if along_x else (z0, z1)
    t = L0 + 0.2
    while t < L1 - 0.1:  # a band of square relief tiles echoing the breeze blocks
        if along_x:
            for zz in (z0 - 0.01, z1 + 0.01):
                obox((t, 0.62, zz), (0.22, 0.22, 0.02), (0, 0, 45), 'white', tint_c=(0.82, 0.88, 0.86), name='relief')
        else:
            for xx in (x0 - 0.01, x1 + 0.01):
                obox((xx, 0.62, t), (0.02, 0.22, 0.22), (45, 0, 0), 'white', tint_c=(0.82, 0.88, 0.86), name='relief')
        t += 0.42

# ================================================================ outside: a kapcai, banana, rambutan
mx, mz = 6.4, 4.8  # a little motorbike parked on the sand by the gatepost
obox((mx, 0.5, mz), (1.1, 0.26, 0.28), (0, 0, 0), 'motor', bevel=0.09, name='kapcai')
obox((mx - 0.15, 0.7, mz), (0.55, 0.08, 0.24), (0, 0, 0), 'char', bevel=0.03, name='kapcai-seat')
pole((mx + 0.48, 0.5, mz), (mx + 0.4, 1.0, mz), 0.03, 'steel', name='kapcai-stem')
pole((mx + 0.4, 1.0, mz - 0.28), (mx + 0.4, 1.0, mz + 0.28), 0.02, 'steel', name='kapcai-bar')
for x in (mx - 0.42, mx + 0.5):
    pole((x, 0.22, mz - 0.05), (x, 0.22, mz + 0.05), 0.22, 'char', seg=14, name='wheel')
banana(-7.2, -0.6, seed=12)
banana(6.4, -7.8, 2.4, seed=13)
for (x, z, r) in ((-6.4, 3.6, 0.42), (-7.4, 2.0, 0.36), (6.2, 3.4, 0.4), (13.4, 3.2, 0.42)):
    shrub(x, z, r, flowers=True)
# rambutan behind the house, north of everything the sun can see
pole((2.4, 0.0, -8.8), (2.4, 2.2, -8.8), 0.16, 'trunk', seg=8, r2=0.12, tint_c=(0.8, 0.7, 0.6), name='rambutan-trunk')
for (dx, dy, dz, r) in ((0, 3.0, 0, 1.1), (0.8, 2.6, 0.3, 0.8), (-0.8, 2.7, -0.2, 0.85)):
    blob(2.4 + dx, dy, -8.8 + dz, r, 'leaf', jitter((0.85, 1.0, 0.85), 0.08), squash=0.8, seed=600 + int(dx * 10), name='rambutan')
for i in range(14):
    a = i / 14 * math.tau
    blob(2.4 + math.cos(a) * 1.0, 2.7 + (i % 3) * 0.3, -8.8 + math.sin(a) * 0.9, 0.07, 'hibiscus', (1, 1, 1), squash=1.0, seed=700 + i, name='rambutan-fruit')

# ================================================================ the neighbour: a two-storey kampung house
nh = BOX['neighbour house']
nx0, nx1 = nh['c'][0] - nh['h'][0], nh['c'][0] + nh['h'][0]
nz0, nz1 = nh['c'][2] - nh['h'][2], nh['c'][2] + nh['h'][2]
ny1 = nh['c'][1] + nh['h'][1]
GF = 2.3
box(nx0, nx1, 0.0, GF, nz0, nz1, 'yellow', bevel=0.03, name='n-ground')
box(nx0 - 0.04, nx1 + 0.04, GF - 0.06, GF + 0.08, nz0 - 0.04, nz1 + 0.04, 'white', bevel=0.01, name='n-band')
box(nx0, nx1, GF + 0.08, 3.85, nz0, nz1, 'blue-plank', bevel=0.02, name='n-upper')
solid([rect(nx0 - 0.35, nx1 + 0.35, nz0 - 0.35, nz1 + 0.35, 3.8), [(nx1 - 1.0, ny1, (nz0 + nz1) / 2), (nx1 - 1.0, ny1, (nz0 + nz1) / 2), (nx0 + 1.0, ny1, (nz0 + nz1) / 2), (nx0 + 1.0, ny1, (nz0 + nz1) / 2)]], 'zinc', (0.85, 0.85, 0.85), name='n-roof', cap_top=False)
# ground floor: a grille door and louvred windows to the lane; upper: tall windows
box(nx0 + 0.5, nx0 + 1.5, 0.0, 2.05, nz1 - 0.02, nz1 + 0.03, 'chengal', bevel=0.01, name='n-door')
for k in range(6):
    pole((nx0 + 0.55 + k * 0.18, 0.05, nz1 + 0.06), (nx0 + 0.55 + k * 0.18, 2.0, nz1 + 0.06), 0.012, 'steel', seg=4, name='grille')
for x in (nx0 + 2.4, nx1 - 0.7):
    box(x - 0.4, x + 0.4, 0.9, 1.9, nz1 - 0.02, nz1 + 0.03, 'char', bevel=0.0, name='n-win')
    for k in range(7):
        box(x - 0.42, x + 0.42, 0.95 + k * 0.13, 1.0 + k * 0.13, nz1 + 0.03, nz1 + 0.07, 'white', bevel=0.0, name='louvre')
for x in (nx0 + 1.1, nx1 - 1.1):
    box(x - 0.45, x + 0.45, GF + 0.35, 3.6, nz1 - 0.02, nz1 + 0.03, 'char', bevel=0.0, name='n-upwin')
    box(x - 0.5, x + 0.5, GF + 0.3, GF + 0.36, nz1, nz1 + 0.08, 'white', bevel=0.0, name='n-sill')
# the side window the neighbour watches from, west face, with the ledge he stands on
wy, wz = N['window'][1], N['window'][2]
box(nx0 - 0.06, nx0 + 0.02, wy - 0.6, wy + 0.6, wz - 0.55, wz + 0.55, 'char', bevel=0.0, name='n-win-dark')
box(nx0 - 0.09, nx0 - 0.03, wy - 0.66, wy + 0.66, wz - 0.62, wz + 0.62, 'white', bevel=0.01, name='n-win-frame')
box(nx0 - 0.7, nx0, wy - 1.68, wy - 1.56, wz - 0.9, wz + 0.9, 'white', bevel=0.02, name='n-ledge')
for k in range(10):
    zz = wz - 0.85 + k * 0.19
    pole((nx0 - 0.66, wy - 1.56, zz), (nx0 - 0.66, wy - 0.9, zz), 0.014, 'steel', seg=4, name='ledge-rail')
pole((nx0 - 0.66, wy - 0.9, wz - 0.9), (nx0 - 0.66, wy - 0.9, wz + 0.9), 0.02, 'steel', seg=6, name='ledge-rail-top')
pole((nx1 - 0.6, 3.85, nz0 + 0.5), (nx1 - 0.6, 4.5, nz0 + 0.5), 0.02, 'steel', seg=4, name='aerial')
