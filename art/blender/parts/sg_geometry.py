# ================================================================ SINGAPORE: black-and-white bungalow
# Inside what src/sim checks: room x -5..5, z -7..-3 with solid north, west and east sides to 3 m,
# a roof plane at 3 m, an open courtyard face; the reader's eye 1.05 m at (1.6, -3.5); garden walls
# 2.2 m; the neighbour inside its box below 4.6 m; the tower (code-built) in its own box.
#   a two-storey colonial black-and-white house: white plaster below, black half-timber framing on
#   white above, tall casements with bamboo chick blinds, a verandah open to the garden, a deep
#   hipped clay-tile roof with black fascia and white soffit. In Singapore in November the noon sun
#   stands about 72 degrees high, so rays to the reader cross the open front below 2.6 m; the upper
#   storey (above 3 m) shades nothing the checks let through. Courtyard eave stops at z -2.9.
#   garden: lawn, a tiled swimming pool, loungers, a wrought-iron table; white walls, black copings.
#   neighbour: a Peranakan shophouse with a five-foot way, louvred shutters and a tile band.

FL = 0.3      # verandah floor on brick piers
UP = 3.0      # upper storey floor
EAVE = 5.9    # main eave


def _tiles_sg(nt, bsdf, coord):
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (3.0, 3.0, 3.0)
    nt.links.new(coord.outputs['Object'], mp.inputs['Vector'])
    br = nt.nodes.new('ShaderNodeTexBrick')
    br.inputs['Color1'].default_value = (*S('#c9612f'), 1)
    br.inputs['Color2'].default_value = (*S('#b2532a'), 1)
    br.inputs['Mortar'].default_value = (*S('#6b2c16'), 1)
    br.inputs['Mortar Size'].default_value = 0.02
    br.inputs['Brick Width'].default_value = 0.4
    br.inputs['Row Height'].default_value = 0.28
    nt.links.new(mp.outputs['Vector'], br.inputs['Vector'])
    c = mix(nt, noise(nt, coord, 0.8, 2, 0.5), br.outputs['Color'], rgb(nt, S('#9c6a4c')))
    nt.links.new(tint(nt, c), bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.7


def _chick(nt, bsdf, coord):
    # bamboo chick blind: fine horizontal slats
    w = nt.nodes.new('ShaderNodeTexWave')
    w.bands_direction = 'Z'
    w.inputs['Scale'].default_value = 40.0
    w.inputs['Distortion'].default_value = 0.0
    nt.links.new(coord.outputs['Object'], w.inputs['Vector'])
    c = mix(nt, w.outputs['Fac'], rgb(nt, S('#8a6a3c')), rgb(nt, S('#d1b07a')))
    nt.links.new(c, bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.7


def _pooltile(nt, bsdf, coord):
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (6, 6, 6)
    nt.links.new(coord.outputs['Object'], mp.inputs['Vector'])
    ch = nt.nodes.new('ShaderNodeTexChecker')
    ch.inputs['Scale'].default_value = 1.0
    ch.inputs['Color1'].default_value = (*S('#3fb6c9'), 1)
    ch.inputs['Color2'].default_value = (*S('#2fa0b6'), 1)
    nt.links.new(mp.outputs['Vector'], ch.inputs['Vector'])
    nt.links.new(ch.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.3


def _peranakan(nt, bsdf, coord):
    # a band of glazed tiles: small coloured squares
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (8, 8, 8)
    nt.links.new(coord.outputs['Object'], mp.inputs['Vector'])
    v = nt.nodes.new('ShaderNodeTexVoronoi')
    v.feature = 'F1'
    v.distance = 'CHEBYCHEV'
    v.inputs['Scale'].default_value = 1.0
    nt.links.new(mp.outputs['Vector'], v.inputs['Vector'])
    r = nt.nodes.new('ShaderNodeValToRGB')
    r.color_ramp.interpolation = 'CONSTANT'
    cols = ['#2f6f8f', '#e9c46a', '#d1495b', '#3d9970', '#f4f1de']
    els = r.color_ramp.elements
    els[0].color = (*S(cols[0]), 1)
    els[1].position = 0.2
    els[1].color = (*S(cols[1]), 1)
    for i in range(2, len(cols)):
        e = els.new(i / len(cols))
        e.color = (*S(cols[i]), 1)
    nt.links.new(v.outputs['Color'], r.inputs['Fac'])
    nt.links.new(r.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.35


MATS.update({
    'white': node_mat('white', _plaster(S('#f6f3ec'))),
    'black': node_mat('black', flat(S('#1e1e1f'), 0.55)),
    'tiles': node_mat('tiles', _tiles_sg),
    'chick': node_mat('chick', _chick),
    'pooltile': node_mat('pooltile', _pooltile),
    'coping': node_mat('coping', card(S('#ece6da'), 0.03)),
    'deck': node_mat('deck', _weathered),
    'mintsh': node_mat('mintsh', _plaster(S('#a8d8c8'))),
    'pinksh': node_mat('pinksh', _plaster(S('#f2b8b0'))),
    'shutter': node_mat('shutter', flat(S('#2f7a5b'), 0.6)),
    'peranakan': node_mat('peranakan', _peranakan),
    'ironwork': node_mat('ironwork', flat(S('#222326'), 0.4, 0.4)),
    'cushion': node_mat('cushion', flat(S('#f1ece0'), 0.85)),
    'bougain': node_mat('bougain', flat(S('#d63384'), 0.6)),
    'brickpier': node_mat('brickpier', card(S('#8e3b2a'), 0.05)),
})

R = LAY['room']
C = LAY['court']
N = LAY['neighbour']
sx, _, sz = LAY['seat']
pool = {'x0': -4.3, 'x1': -1.6, 'z0': 0.3, 'z1': 2.9}

# ================================================================ garden
box(C['x0'], C['x1'], -0.04, 0.02, C['z0'], C['z1'], 'grass', bevel=0.0, name='lawn')
# the pool: tiled basin, white coping all round, steps at one end
box(pool['x0'], pool['x1'], -0.6, -0.5, pool['z0'], pool['z1'], 'pooltile', bevel=0.0, name='pool-floor')
for (a, b, c, d) in ((pool['x0'] - 0.05, pool['x1'] + 0.05, pool['z0'] - 0.05, pool['z0']), (pool['x0'] - 0.05, pool['x1'] + 0.05, pool['z1'], pool['z1'] + 0.05), (pool['x0'] - 0.05, pool['x0'], pool['z0'], pool['z1']), (pool['x1'], pool['x1'] + 0.05, pool['z0'], pool['z1'])):
    box(a, b, -0.6, 0.0, c, d, 'pooltile', bevel=0.0, name='pool-wall')
for (a, b, c, d) in ((pool['x0'] - 0.4, pool['x1'] + 0.4, pool['z0'] - 0.4, pool['z0'] - 0.05), (pool['x0'] - 0.4, pool['x1'] + 0.4, pool['z1'] + 0.05, pool['z1'] + 0.4), (pool['x0'] - 0.4, pool['x0'] - 0.05, pool['z0'] - 0.05, pool['z1'] + 0.05), (pool['x1'] + 0.05, pool['x1'] + 0.4, pool['z0'] - 0.05, pool['z1'] + 0.05)):
    box(a, b, 0.0, 0.07, c, d, 'coping', bevel=0.02, name='pool-coping')
for k in range(3):
    box(pool['x1'] - 0.7, pool['x1'] - 0.05, -0.15 - k * 0.15, -0.1 - k * 0.15, pool['z0'] + k * 0.25, pool['z0'] + 0.25 + k * 0.25, 'coping', bevel=0.01, name='pool-step')
# a timber deck between the verandah and the lawn, loungers by the pool
box(C['x0'] + 0.1, C['x1'] - 0.1, 0.0, 0.08, C['z0'], C['z0'] + 1.3, 'deck', bevel=0.01, name='deck')
x = C['x0'] + 0.1
while x < C['x1'] - 0.1:
    box(x, x + 0.015, 0.08, 0.085, C['z0'], C['z0'] + 1.3, 'black', bevel=0.0, name='deck-joint')
    x += 0.16
for (x, z) in ((-0.9, 0.6), (-0.9, 1.6)):
    obox((x, 0.32, z), (0.6, 0.08, 1.7), (0, 0, 0), 'deck', bevel=0.02, name='lounger')
    obox((x, 0.42, z - 0.65), (0.58, 0.07, 0.55), (-35, 0, 0), 'cushion', bevel=0.03, name='lounger-back')
    obox((x, 0.38, z + 0.15), (0.56, 0.05, 1.05), (0, 0, 0), 'cushion', bevel=0.02, name='lounger-pad')
    for dz in (-0.7, 0.7):
        box(x - 0.25, x + 0.25, 0.0, 0.28, z + dz - 0.03, z + dz + 0.03, 'deck', bevel=0.0, name='lounger-leg')
# wrought-iron table and chairs at the table spot (top 0.75 m), a parasol
tx, tz = 2.6, 2.6
pole((tx, 0.72, tz), (tx, 0.76, tz), 0.6, 'coping', seg=20, name='table-top')
pole((tx, 0.0, tz), (tx, 0.72, tz), 0.04, 'ironwork', seg=8, name='table-stem')
pole((tx, 0.0, tz), (tx, 0.03, tz), 0.3, 'ironwork', seg=12, name='table-foot')
for s_ in (-1, 1):
    cx = tx + s_ * 0.95
    pole((cx, 0.42, tz), (cx, 0.47, tz), 0.24, 'ironwork', seg=14, name='chair-seat')
    obox((cx + s_ * 0.22, 0.75, tz), (0.04, 0.55, 0.44), (0, 0, s_ * -8), 'ironwork', bevel=0.01, name='chair-back')
    for dz in (-0.16, 0.16):
        pole((cx - 0.14, 0.0, tz + dz), (cx - 0.14, 0.42, tz + dz), 0.015, 'ironwork', seg=4, name='chair-leg')
        pole((cx + 0.14, 0.0, tz + dz), (cx + 0.14, 0.42, tz + dz), 0.015, 'ironwork', seg=4, name='chair-leg')
# low planting: bird-of-paradise clumps and bougainvillea along the walls (all under 1.2 m)
for (x, z, r) in ((-4.5, 3.6, 0.45), (4.5, 3.6, 0.45), (4.55, -0.5, 0.4), (-4.55, -0.4, 0.35), (0.0, 3.7, 0.4)):
    shrub(x, z, r, flowers=False)
    for _ in range(5):
        a = rnd.uniform(0, math.tau)
        blob(x + math.cos(a) * r * 0.8, rnd.uniform(r * 0.8, r * 1.6), z + math.sin(a) * r * 0.8, 0.08, 'bougain', jitter((1, 1, 1), 0.1), squash=0.6, seed=rnd.randint(0, 999), name='bougainvillea')

# ================================================================ the house: piers, verandah, lower walls
box(R['x0'] - 0.2, R['x1'] + 0.2, -0.02, FL - 0.04, R['z0'] - 0.2, R['z1'] + 0.25, 'brickpier', bevel=0.02, name='base')
box(R['x0'] - 0.2, R['x1'] + 0.2, FL - 0.04, FL, R['z0'] - 0.2, R['z1'] + 0.25, 'deck', bevel=0.01, name='floor')
x = R['x0'] - 0.2
while x < R['x1'] + 0.2:
    box(x, x + 0.012, FL, FL + 0.004, R['z0'] - 0.2, R['z1'] + 0.25, 'black', bevel=0.0, name='floor-joint')
    x += 0.18
for (nm, a, b, c, d) in (('n', R['x0'], R['x1'], R['z0'] - 0.08, R['z0'] + 0.08), ('w', R['x0'] - 0.08, R['x0'] + 0.08, R['z0'], R['z1']), ('e', R['x1'] - 0.08, R['x1'] + 0.08, R['z0'], R['z1'])):
    box(a, b, FL, UP, c, d, 'white', bevel=0.0, name='wall-' + nm)
    box(a - 0.03, b + 0.03, FL, FL + 0.18, c - 0.03, d + 0.03, 'black', bevel=0.0, name='skirting')
    box(a - 0.04, b + 0.04, UP - 0.1, UP + 0.05, c - 0.04, d + 0.04, 'black', bevel=0.0, name='floor-band')
# tall casements with chick blinds half down, black frames (closed: the checks treat these walls as solid)
def casement(cx, cz, face, y0, y1, w=0.9):
    o = {'n': (0, -1), 'e': (1, 0), 'w': (-1, 0), 's': (0, 1)}[face]
    along_x = face in ('n', 's')
    hw = w / 2
    if along_x:
        z = cz + o[1] * 0.09
        box(cx - hw, cx + hw, y0, y1, z - 0.015, z + 0.015, 'glass', bevel=0.0, name='casement')
        for (a, b, c, d) in ((cx - hw - 0.06, cx - hw, y0, y1), (cx + hw, cx + hw + 0.06, y0, y1), (cx - hw - 0.06, cx + hw + 0.06, y0 - 0.06, y0), (cx - hw - 0.06, cx + hw + 0.06, y1, y1 + 0.06), (cx - 0.02, cx + 0.02, y0, y1)):
            box(a, b, c, d, z - 0.03, z + 0.03, 'black', bevel=0.0, name='frame')
        box(cx - hw - 0.08, cx + hw + 0.08, y0 + (y1 - y0) * 0.45, y1 + 0.08, z + o[1] * 0.03 - 0.012, z + o[1] * 0.03 + 0.012, 'chick', bevel=0.0, name='chick-blind')
    else:
        x = cx + o[0] * 0.09
        box(x - 0.015, x + 0.015, y0, y1, cz - hw, cz + hw, 'glass', bevel=0.0, name='casement')
        for (a, b, c, d) in ((cz - hw - 0.06, cz - hw, y0, y1), (cz + hw, cz + hw + 0.06, y0, y1), (cz - hw - 0.06, cz + hw + 0.06, y0 - 0.06, y0), (cz - hw - 0.06, cz + hw + 0.06, y1, y1 + 0.06), (cz - 0.02, cz + 0.02, y0, y1)):
            box(x - 0.03, x + 0.03, c, d, a, b, 'black', bevel=0.0, name='frame')
        box(x + o[0] * 0.03 - 0.012, x + o[0] * 0.03 + 0.012, y0 + (y1 - y0) * 0.45, y1 + 0.08, cz - hw - 0.08, cz + hw + 0.08, 'chick', bevel=0.0, name='chick-blind')


for x in (-3.0, 0.0, 3.0):
    casement(x, R['z0'], 'n', 0.9, 2.4)
for z in (-6.0, -4.0):
    casement(R['x0'], z, 'w', 0.9, 2.4)
    casement(R['x1'], z, 'e', 0.9, 2.4)
# verandah: square black columns, a white balustrade with a black rail (top 0.9 m)
for x in (R['x0'], -2.5, 0.0, 2.5, R['x1']):
    box(x - 0.12, x + 0.12, FL, UP, R['z1'] - 0.12, R['z1'] + 0.12, 'black', bevel=0.01, name='column')
    box(x - 0.18, x + 0.18, FL, FL + 0.25, R['z1'] - 0.18, R['z1'] + 0.18, 'white', bevel=0.02, name='column-base')
for (a, b) in ((R['x0'] + 0.12, -0.6), (0.6, R['x1'] - 0.12)):
    box(a, b, FL, FL + 0.08, R['z1'] - 0.05, R['z1'] + 0.05, 'white', bevel=0.0, name='bal-base')
    box(a, b, 0.84, 0.9, R['z1'] - 0.07, R['z1'] + 0.07, 'black', bevel=0.01, name='bal-rail')
    t = a + 0.1
    while t < b:
        box(t - 0.03, t + 0.03, FL + 0.08, 0.84, R['z1'] - 0.03, R['z1'] + 0.03, 'white', bevel=0.01, name='baluster')
        t += 0.14
for k in range(3):  # steps down to the deck in the gap
    box(-0.6, 0.6, 0.0, FL - k * 0.1, R['z1'] + 0.25 + k * 0.0, R['z1'] + 0.25 + (k + 1) * 0.22, 'white', bevel=0.01, name='step')
# the reading corner on the verandah: a planter's chair, a side table, a fern
box(sx - 0.35, sx + 0.35, 0.45, 0.5, sz - 0.4, sz + 0.35, 'deck', bevel=0.02, name='planter-seat')
obox((sx, 0.72, sz - 0.42), (0.7, 0.05, 0.6), (-55, 0, 0), 'chick', bevel=0.01, name='planter-back')
for dx in (-0.36, 0.36):
    obox((sx + dx, 0.6, sz - 0.02), (0.05, 0.04, 1.1), (0, 0, 0), 'deck', bevel=0.01, name='planter-arm')
    for dz in (-0.35, 0.3):
        box(sx + dx - 0.025, sx + dx + 0.025, FL, 0.6, sz + dz - 0.025, sz + dz + 0.025, 'deck', bevel=0.0, name='planter-leg')
box(sx + 0.65, sx + 1.05, FL, 0.85, sz - 0.25, sz + 0.15, 'black', bevel=0.02, name='side-table')
pole((sx - 1.0, FL, sz - 0.1), (sx - 1.0, FL + 0.35, sz - 0.1), 0.18, 'terracotta' if 'terracotta' in MATS else 'clay', seg=12, r2=0.14, name='pot')
blob(sx - 1.0, FL + 0.55, sz - 0.1, 0.3, 'leaf', (1.05, 1.15, 0.95), squash=0.7, seed=31, name='fern')
# ceiling fan under the verandah
box(R['x0'], R['x1'], UP - 0.12, UP - 0.1, R['z0'], R['z1'], 'white', bevel=0.0, name='ceiling')
pole((0.0, UP - 0.12, -4.0), (0.0, UP - 0.45, -4.0), 0.02, 'black', seg=6, name='fan-rod')
for a in (0, 120, 240):
    obox((0.0, UP - 0.47, -4.0), (1.1, 0.02, 0.14), (0, a, 0), 'deck', name='fan-blade')

# ================================================================ upper storey: half-timbered black and white
for (nm, a, b, c, d) in (('n', R['x0'], R['x1'], R['z0'] - 0.08, R['z0'] + 0.08), ('s', R['x0'], R['x1'], R['z1'] - 0.08, R['z1'] + 0.08), ('w', R['x0'] - 0.08, R['x0'] + 0.08, R['z0'], R['z1']), ('e', R['x1'] - 0.08, R['x1'] + 0.08, R['z0'], R['z1'])):
    box(a, b, UP + 0.05, EAVE - 0.1, c, d, 'white', bevel=0.0, name='upper-' + nm)
    along_x = nm in ('n', 's')
    L0, L1 = (a, b) if along_x else (c, d)
    out = {'n': -1, 's': 1, 'w': -1, 'e': 1}[nm]
    t = L0
    while t <= L1 + 0.01:  # studs
        if along_x:
            box(t - 0.06, t + 0.06, UP + 0.05, EAVE - 0.1, (c + d) / 2 + out * 0.09 - 0.03, (c + d) / 2 + out * 0.09 + 0.03, 'black', bevel=0.0, name='stud')
        else:
            box((a + b) / 2 + out * 0.09 - 0.03, (a + b) / 2 + out * 0.09 + 0.03, UP + 0.05, EAVE - 0.1, t - 0.06, t + 0.06, 'black', bevel=0.0, name='stud')
        t += 1.0 if along_x else 1.0
    for y in (UP + 0.95, EAVE - 0.18):  # rails
        if along_x:
            box(a, b, y - 0.05, y + 0.05, (c + d) / 2 + out * 0.09 - 0.03, (c + d) / 2 + out * 0.09 + 0.03, 'black', bevel=0.0, name='rail')
        else:
            box((a + b) / 2 + out * 0.09 - 0.03, (a + b) / 2 + out * 0.09 + 0.03, y - 0.05, y + 0.05, c, d, 'black', bevel=0.0, name='rail')
for x in (-3.0, 0.0, 3.0):
    casement(x, R['z1'], 's', UP + 1.15, EAVE - 0.45, 0.85)
    casement(x, R['z0'], 'n', UP + 1.15, EAVE - 0.45, 0.85)
for z in (-6.0, -4.0):
    casement(R['x0'], z, 'w', UP + 1.15, EAVE - 0.45, 0.85)
    casement(R['x1'], z, 'e', UP + 1.15, EAVE - 0.45, 0.85)

# ================================================================ the roof: deep hipped clay tiles
ex0, ex1, ez0, ez1 = R['x0'] - 1.1, R['x1'] + 1.1, R['z0'] - 1.1, R['z1'] + 0.1
RY = EAVE + 2.6
rx0, rx1, rzr = -2.6, 2.6, (ez0 + ez1) / 2
T = 0.16
under = rect(ex0, ex1, ez0, ez1, EAVE)
top = rect(ex0, ex1, ez0, ez1, EAVE + T)
ridge = [(rx1, RY + T, rzr), (rx1, RY + T, rzr), (rx0, RY + T, rzr), (rx0, RY + T, rzr)]
solid([top, ridge], 'tiles', name='roof', cap_top=False, cap_bottom=False)
solid([under, top], 'black', name='fascia', cap_top=False, cap_bottom=False)
box(ex0, ex1, EAVE - 0.02, EAVE, ez0, ez1, 'white', bevel=0.0, name='soffit')
pole((rx0 - 0.05, RY + T + 0.06, rzr), (rx1 + 0.05, RY + T + 0.06, rzr), 0.1, 'tiles', seg=8, tint_c=(0.8, 0.75, 0.72), name='ridge')
for (cx, cz) in ((ex0, ez1), (ex1, ez1), (ex1, ez0), (ex0, ez0)):
    pole((cx, EAVE + T + 0.03, cz), ((rx0 if cx < 0 else rx1), RY + T + 0.03, rzr), 0.07, 'tiles', seg=6, tint_c=(0.8, 0.75, 0.72), name='hip')
# brackets under the eave on the garden side
x = ex0 + 0.4
while x < ex1:
    obox((x, EAVE - 0.25, R['z1'] + 0.02), (0.08, 0.5, 0.08), (-35, 0, 0), 'black', name='bracket')
    x += 1.25
# chimney-like vent and a flagpole would be clutter; keep the roofline clean

# ================================================================ white garden walls, 2.2 m, black copings
for key in ('east garden wall', 'south garden wall', 'west garden wall'):
    b = BOX[key]
    x0, x1 = b['c'][0] - b['h'][0], b['c'][0] + b['h'][0]
    z0, z1 = b['c'][2] - b['h'][2], b['c'][2] + b['h'][2]
    top_ = b['c'][1] + b['h'][1]
    box(x0, x1, 0.0, top_ - 0.08, z0, z1, 'white', bevel=0.0, name='gwall')
    box(x0 - 0.05, x1 + 0.05, top_ - 0.08, top_ + 0.02, z0 - 0.05, z1 + 0.05, 'black', bevel=0.01, name='gwall-coping')
    box(x0 - 0.03, x1 + 0.03, 0.0, 0.2, z0 - 0.03, z1 + 0.03, 'black', bevel=0.0, name='gwall-plinth')
    along_x = (x1 - x0) > (z1 - z0)
    L0, L1 = (x0, x1) if along_x else (z0, z1)
    t = L0
    while t <= L1 + 0.01:
        if along_x:
            box(t - 0.15, t + 0.15, 0.0, top_ + 0.1, z0 - 0.05, z1 + 0.05, 'white', bevel=0.01, name='gpier')
            box(t - 0.19, t + 0.19, top_ + 0.1, top_ + 0.18, z0 - 0.09, z1 + 0.09, 'black', bevel=0.02, name='gpier-cap')
        else:
            box(x0 - 0.05, x1 + 0.05, 0.0, top_ + 0.1, t - 0.15, t + 0.15, 'white', bevel=0.01, name='gpier')
            box(x0 - 0.09, x1 + 0.09, top_ + 0.1, top_ + 0.18, t - 0.19, t + 0.19, 'black', bevel=0.02, name='gpier-cap')
        t += 2.5

# ================================================================ neighbour: a Peranakan shophouse
nh = BOX['neighbour house']
nx0, nx1 = nh['c'][0] - nh['h'][0], nh['c'][0] + nh['h'][0]
nz0, nz1 = nh['c'][2] - nh['h'][2], nh['c'][2] + nh['h'][2]
ny1 = nh['c'][1] + nh['h'][1]
GF = 2.3
box(nx0, nx1, 0.0, GF, nz0, nz1 - 1.2, 'mintsh', bevel=0.04, name='sh-ground')  # set back: the five-foot way
box(nx0, nx1, GF, 3.95, nz0, nz1, 'pinksh', bevel=0.04, name='sh-upper')
box(nx0 - 0.06, nx1 + 0.06, GF - 0.18, GF + 0.02, nz0 - 0.06, nz1 + 0.06, 'peranakan', bevel=0.0, name='sh-tileband')
box(nx0 - 0.08, nx1 + 0.08, 3.85, 4.0, nz0 - 0.08, nz1 + 0.08, 'white', bevel=0.02, name='sh-cornice')
# pitched clay roof inside the box (to 4.6 m)
solid([rect(nx0 - 0.2, nx1 + 0.2, nz0 - 0.2, nz1 + 0.2, 4.0), [(nx1 + 0.2, ny1, (nz0 + nz1) / 2), (nx1 + 0.2, ny1, (nz0 + nz1) / 2), (nx0 - 0.2, ny1, (nz0 + nz1) / 2), (nx0 - 0.2, ny1, (nz0 + nz1) / 2)]], 'tiles', name='sh-roof', cap_top=False)
# five-foot way: columns, the shop front behind, a tiled floor
for x in (nx0 + 0.2, nx0 + 2.1, nx1 - 0.2):
    box(x - 0.15, x + 0.15, 0.0, GF - 0.18, nz1 - 0.3, nz1, 'white', bevel=0.02, name='sh-column')
box(nx0, nx1, 0.0, 0.05, nz1 - 1.2, nz1, 'peranakan', bevel=0.0, name='sh-floor')
for x in (nx0 + 1.15, nx1 - 1.15):
    box(x - 0.6, x + 0.6, 0.0, 2.0, nz1 - 1.24, nz1 - 1.18, 'teak' if 'teak' in MATS else 'timber', bevel=0.01, name='sh-door')
    box(x - 0.6, x + 0.6, 1.95, 2.05, nz1 - 1.24, nz1 - 1.16, 'black', bevel=0.0, name='sh-door-head')
# upper floor: three tall windows with green louvred shutters, pilasters
for x in (nx0 + 0.75, (nx0 + nx1) / 2, nx1 - 0.75):
    box(x - 0.42, x + 0.42, GF + 0.35, 3.6, nz1 - 0.02, nz1 + 0.02, 'char', bevel=0.0, name='sh-win')
    for s_ in (-1, 1):
        box(x + s_ * 0.42 - 0.2, x + s_ * 0.42 + 0.2, GF + 0.35, 3.6, nz1 + 0.02, nz1 + 0.06, 'shutter', bevel=0.0, name='sh-shutter')
        for k in range(8):
            y = GF + 0.45 + k * 0.15
            box(x + s_ * 0.42 - 0.18, x + s_ * 0.42 + 0.18, y, y + 0.03, nz1 + 0.06, nz1 + 0.08, 'black', bevel=0.0, tint_c=(1.6, 1.6, 1.6), name='louvre')
    box(x - 0.5, x + 0.5, 3.6, 3.72, nz1, nz1 + 0.1, 'white', bevel=0.02, name='sh-head')
for x in (nx0 + 0.05, nx0 + 1.4, nx1 - 1.4, nx1 - 0.05):
    box(x - 0.08, x + 0.08, GF, 3.85, nz1, nz1 + 0.08, 'white', bevel=0.01, name='pilaster')
# west face: the watching window with shutters and a small balcony
wy, wz = N['window'][1], N['window'][2]
box(nx0 - 0.06, nx0 + 0.02, wy - 0.62, wy + 0.62, wz - 0.6, wz + 0.6, 'char', bevel=0.0, name='sh-wwin')
for s_ in (-1, 1):
    box(nx0 - 0.1, nx0 - 0.06, wy - 0.62, wy + 0.62, wz + s_ * 0.6 + (0.25 if s_ > 0 else -0.25) - 0.2, wz + s_ * 0.6 + (0.25 if s_ > 0 else -0.25) + 0.2, 'shutter', bevel=0.0, name='sh-wshutter')
box(nx0 - 0.85, nx0, GF - 0.05, GF + 0.1, wz - 1.1, wz + 1.1, 'white', bevel=0.02, name='sh-balcony')
for k in range(15):
    zz = wz - 1.05 + k * 0.15
    pole((nx0 - 0.82, GF + 0.1, zz), (nx0 - 0.82, GF + 0.95, zz), 0.016, 'ironwork', seg=4, name='sh-rail')
pole((nx0 - 0.82, GF + 0.95, wz - 1.1), (nx0 - 0.82, GF + 0.95, wz + 1.1), 0.025, 'ironwork', seg=6, name='sh-rail-top')
for zz in (wz - 0.8, wz + 0.85):
    pole((nx0 - 0.55, GF + 0.1, zz), (nx0 - 0.55, GF + 0.34, zz), 0.13, 'clay', seg=10, r2=0.1, name='pot')
    blob(nx0 - 0.55, GF + 0.55, zz, 0.24, 'leaf', jitter((1, 1, 1), 0.1), seed=int(zz * 10) + 7, name='pot-plant')

# ================================================================ around: a rain tree, frangipani, a park bench
def raintree(x, z, h=3.6, seed=0):
    """Singapore's rain tree, kept small: a short trunk and a broad, flat umbrella crown."""
    k = random.Random(seed)
    pole((x, 0.0, z), (x, h * 0.6, z), 0.18, 'trunk', seg=9, r2=0.13, tint_c=(0.7, 0.62, 0.55), name='rt-trunk')
    for i in range(7):
        a = i / 7 * math.tau + k.uniform(-0.3, 0.3)
        r = k.uniform(0.8, 1.5)
        blob(x + math.cos(a) * r, h + k.uniform(-0.15, 0.2), z + math.sin(a) * r, k.uniform(0.7, 1.0), 'leaf', jitter((0.95, 1.05, 0.9), 0.1), squash=0.5, seed=seed * 10 + i, name='rt-crown')
    blob(x, h + 0.25, z, 1.1, 'leaf', (1.0, 1.08, 0.95), squash=0.45, seed=seed * 10 + 9, name='rt-crown')


raintree(-6.9, -7.2, seed=1)
raintree(6.8, -7.9, 3.2, seed=2)
for (x, z, r) in ((-6.4, 0.4, 0.45), (-7.2, 1.8, 0.4), (-6.2, 3.0, 0.35), (6.2, 3.4, 0.4)):
    shrub(x, z, r, flowers=False)
# a green park bench on the west lawn, facing the sea
box(-8.2, -6.8, 0.42, 0.47, 2.4, 2.8, 'shutter', bevel=0.01, name='bench')
box(-8.2, -6.8, 0.47, 0.85, 2.38, 2.44, 'shutter', bevel=0.01, name='bench-back')
for x in (-8.1, -6.9):
    box(x - 0.03, x + 0.03, 0.0, 0.42, 2.45, 2.75, 'ironwork', bevel=0.0, name='bench-leg')
