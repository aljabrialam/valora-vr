# ================================================================ INDONESIA: Javanese joglo, Jakarta
# Inside what src/sim checks: room x -5..5, z -7..-3 with solid north, west and east sides to 3 m,
# a roof plane at 3 m, an open courtyard face; the reader's eye 1.05 m at (1.6, -3.5); garden walls
# 2.2 m; the neighbour inside its box below 4.6 m.
#   the dalem (inner house) of a joglo: carved teak gebyok walls on a low stone plinth, open to the
#   courtyard through a pendopo-like front of teak columns on umpak stone bases. The joglo roof
#   breaks pitch twice: a shallow skirt from 3 m, a steeper middle, and the tall brunjung on top,
#   in terracotta genteng tiles with mustaka finials. Its courtyard eave stops at z -2.9.
#   garden: exposed red-brick walls with plaster copings, andesite paving, a kolam fish pond.

PLINTH = 0.2


def _genteng(nt, bsdf, coord):
    # terracotta roof tiles: rows of courses down the slope and staggered tile joints
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (3.2, 3.2, 3.2)
    nt.links.new(coord.outputs['Object'], mp.inputs['Vector'])
    br = nt.nodes.new('ShaderNodeTexBrick')
    br.inputs['Color1'].default_value = (*S('#b9532c'), 1)
    br.inputs['Color2'].default_value = (*S('#9c4426'), 1)
    br.inputs['Mortar'].default_value = (*S('#5a2414'), 1)
    br.inputs['Scale'].default_value = 1.0
    br.inputs['Mortar Size'].default_value = 0.025
    br.inputs['Brick Width'].default_value = 0.32
    br.inputs['Row Height'].default_value = 0.3
    nt.links.new(mp.outputs['Vector'], br.inputs['Vector'])
    c = mix(nt, noise(nt, coord, 0.9, 2, 0.5), br.outputs['Color'], rgb(nt, S('#8a5a42')))
    nt.links.new(tint(nt, c), bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.75


def _brick(nt, bsdf, coord):
    # bata merah: red bricks in pale mortar
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (4.5, 4.5, 4.5)
    nt.links.new(coord.outputs['Object'], mp.inputs['Vector'])
    br = nt.nodes.new('ShaderNodeTexBrick')
    br.inputs['Color1'].default_value = (*S('#b2502f'), 1)
    br.inputs['Color2'].default_value = (*S('#97402a'), 1)
    br.inputs['Mortar'].default_value = (*S('#d9cbb4'), 1)
    br.inputs['Scale'].default_value = 1.0
    br.inputs['Mortar Size'].default_value = 0.03
    br.inputs['Brick Width'].default_value = 0.5
    br.inputs['Row Height'].default_value = 0.25
    nt.links.new(mp.outputs['Vector'], br.inputs['Vector'])
    nt.links.new(tint(nt, br.outputs['Color']), bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.85


def _gebyok(nt, bsdf, coord):
    # carved teak panels: warm dark teak with lighter carved bands and a fine floral grain
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (14, 14, 14)
    nt.links.new(coord.outputs['Object'], mp.inputs['Vector'])
    v = nt.nodes.new('ShaderNodeTexVoronoi')
    v.inputs['Scale'].default_value = 1.0
    nt.links.new(mp.outputs['Vector'], v.inputs['Vector'])
    w = nt.nodes.new('ShaderNodeTexWave')
    w.bands_direction = 'Z'
    w.inputs['Scale'].default_value = 1.4
    w.inputs['Distortion'].default_value = 0.0
    nt.links.new(coord.outputs['Object'], w.inputs['Vector'])
    carve = mix(nt, v.outputs['Distance'], rgb(nt, S('#4a2716')), rgb(nt, S('#9a5f33')))
    c = mix(nt, w.outputs['Fac'], carve, rgb(nt, S('#6e3c20')))
    nt.links.new(tint(nt, c), bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.55


MATS.update({
    'genteng': node_mat('genteng', _genteng),
    'brick': node_mat('brick', _brick),
    'gebyok': node_mat('gebyok', _gebyok),
    'teak': node_mat('teak', _weathered),
    'andesite': node_mat('andesite', card(S('#6f6c68'), 0.08)),
    'terracotta': node_mat('terracotta', card(S('#c46a43'), 0.05)),
    'plaster': node_mat('plaster', _plaster(S('#f1e8d6'))),
    'mint': node_mat('mint', _plaster(S('#9fd5c0'))),
    'yellow': node_mat('yellow', _plaster(S('#f2cf6b'))),
    'gold': node_mat('gold', flat(S('#c9a13b'), 0.35, 0.6)),
    'kamboja': node_mat('kamboja', flat(S('#fbf3df'), 0.6)),
    'scooter': node_mat('scooter', flat(S('#c23a35'), 0.4, 0.2)),
})

R = LAY['room']
C = LAY['court']
N = LAY['neighbour']
sx, _, sz = LAY['seat']
pool = {'x0': -4.3, 'x1': -1.6, 'z0': 0.3, 'z1': 2.9}

# ================================================================ courtyard
box(C['x0'], C['x1'], -0.04, 0.02, C['z0'], C['z1'], 'grass', bevel=0.0, name='lawn')
# andesite paving: a front terrace and a cross path, laid in large slabs with grass joints
def slabs(x0, x1, z0, z1, s=0.6):
    z = z0
    while z < z1 - 0.05:
        x = x0
        while x < x1 - 0.05:
            box(x + 0.03, min(x + s, x1) - 0.03, 0.0, 0.04, z + 0.03, min(z + s, z1) - 0.03, 'andesite', bevel=0.02, tint_c=jitter((1, 1, 1), 0.08), name='slab')
            x += s
        z += s


slabs(C['x0'] + 0.2, C['x1'] - 0.2, C['z0'], C['z0'] + 1.2)
slabs(0.9, 2.1, C['z0'] + 1.2, C['z1'] - 0.3)
slabs(-1.4, 0.9, 1.3, 1.9)
# kolam: a stone-edged fish pond with lotus
box(pool['x0'], pool['x1'], -0.45, -0.3, pool['z0'], pool['z1'], 'water-bed', bevel=0.0, name='pond-bed')
for (a, b, c, d) in ((pool['x0'] - 0.25, pool['x1'] + 0.25, pool['z0'] - 0.25, pool['z0']), (pool['x0'] - 0.25, pool['x1'] + 0.25, pool['z1'], pool['z1'] + 0.25), (pool['x0'] - 0.25, pool['x0'], pool['z0'], pool['z1']), (pool['x1'], pool['x1'] + 0.25, pool['z0'], pool['z1'])):
    box(a, b, -0.45, 0.12, c, d, 'andesite', bevel=0.03, tint_c=(1.1, 1.1, 1.1), name='pond-edge')
for (x, zz, r) in ((-3.6, 0.9, 0.3), (-2.3, 1.5, 0.24), (-3.1, 2.3, 0.28)):
    pole((x, 0.07, zz), (x, 0.085, zz), r, 'leaf', seg=12, name='lily')
pole((-2.8, 0.085, 2.0), (-2.8, 0.18, 2.0), 0.08, 'flower', seg=8, tint_c=(1.0, 0.7, 0.8), name='lotus')
# a carved teak table with two chairs at the table spot (top 0.75 m)
tx, tz = 2.6, 2.6
box(tx - 0.6, tx + 0.6, 0.7, 0.77, tz - 0.45, tz + 0.45, 'teak', bevel=0.02, name='table')
for dx in (-0.5, 0.5):
    for dz in (-0.35, 0.35):
        box(tx + dx - 0.04, tx + dx + 0.04, 0.0, 0.7, tz + dz - 0.04, tz + dz + 0.04, 'teak', bevel=0.01, name='table-leg')
for s_ in (-1, 1):
    cx = tx + s_ * 0.95
    box(cx - 0.22, cx + 0.22, 0.42, 0.48, tz - 0.22, tz + 0.22, 'teak', bevel=0.02, name='chair')
    box(cx + s_ * 0.18 - 0.03, cx + s_ * 0.18 + 0.03, 0.48, 1.0, tz - 0.22, tz + 0.22, 'gebyok', bevel=0.01, name='chair-back')
    for dz in (-0.18, 0.18):
        box(cx - 0.18, cx - 0.14, 0.0, 0.42, tz + dz - 0.02, tz + dz + 0.02, 'teak', bevel=0.0, name='chair-leg')
        box(cx + 0.14, cx + 0.18, 0.0, 0.42, tz + dz - 0.02, tz + dz + 0.02, 'teak', bevel=0.0, name='chair-leg')
# potted plants and a stone lantern
for (x, z) in ((-4.4, -2.5), (4.4, -2.5), (4.4, 3.5)):
    pole((x, 0.0, z), (x, 0.45, z), 0.26, 'terracotta', seg=12, r2=0.2, name='pot')
    blob(x, 0.75, z, 0.32, 'leaf', jitter((1, 1, 1), 0.1), seed=int(x * 7 + z * 3), name='pot-plant')
box(-4.5, -4.1, 0.0, 0.5, 3.4, 3.8, 'andesite', bevel=0.03, name='lantern-base')
box(-4.55, -4.05, 0.5, 0.85, 3.35, 3.85, 'andesite', bevel=0.05, tint_c=(1.15, 1.15, 1.15), name='lantern')
obox((-4.3, 0.95, 3.6), (0.62, 0.12, 0.62), (0, 45, 0), 'andesite', bevel=0.03, name='lantern-cap')

# ================================================================ the dalem: plinth, floor, walls, columns
box(R['x0'] - 0.3, R['x1'] + 0.3, -0.02, PLINTH, R['z0'] - 0.3, R['z1'] + 0.35, 'andesite', bevel=0.03, name='plinth')
box(R['x0'] - 0.1, R['x1'] + 0.1, PLINTH, PLINTH + 0.02, R['z0'] - 0.1, R['z1'] + 0.15, 'terracotta', bevel=0.0, name='floor')
# floor tiles: a grid of slightly varied terracotta squares
x = R['x0']
while x < R['x1'] - 0.05:
    z = R['z0']
    while z < R['z1'] + 0.1:
        box(x + 0.02, x + 0.38, PLINTH + 0.02, PLINTH + 0.03, z + 0.02, z + 0.38, 'terracotta', bevel=0.0, tint_c=jitter((1, 1, 1), 0.07), name='tile')
        z += 0.4
    x += 0.4
for (nm, a, b, c, d) in (('n', R['x0'], R['x1'], R['z0'] - 0.06, R['z0'] + 0.06), ('w', R['x0'] - 0.06, R['x0'] + 0.06, R['z0'], R['z1']), ('e', R['x1'] - 0.06, R['x1'] + 0.06, R['z0'], R['z1'])):
    box(a, b, PLINTH, 3.0, c, d, 'gebyok', bevel=0.0, name='gebyok-' + nm)
    # framed panels: rails and stiles proud of the carving
    for y in (PLINTH + 0.05, 1.1, 2.3, 2.92):
        box(a - 0.04, b + 0.04, y - 0.05, y + 0.05, c - 0.04, d + 0.04, 'teak', bevel=0.01, name='rail')
    L0, L1 = (a, b) if nm == 'n' else (c, d)
    t = L0
    while t <= L1 + 0.01:
        if nm == 'n':
            box(t - 0.06, t + 0.06, PLINTH, 3.0, c - 0.04, d + 0.04, 'teak', bevel=0.01, name='stile')
        else:
            box(a - 0.04, b + 0.04, PLINTH, 3.0, t - 0.06, t + 0.06, 'teak', bevel=0.01, name='stile')
        t += 1.25
# teak columns on umpak stone bases along the open front, and the four tall soko guru inside
for x in (R['x0'], -2.5, 0.0, 2.5, R['x1']):
    box(x - 0.22, x + 0.22, PLINTH, PLINTH + 0.3, R['z1'] - 0.22, R['z1'] + 0.22, 'andesite', bevel=0.06, tint_c=(1.15, 1.15, 1.15), name='umpak')
    box(x - 0.11, x + 0.11, PLINTH + 0.3, 3.0, R['z1'] - 0.11, R['z1'] + 0.11, 'teak', bevel=0.02, name='column')
    box(x - 0.16, x + 0.16, 2.85, 3.0, R['z1'] - 0.16, R['z1'] + 0.16, 'gold', bevel=0.01, name='capital')
SOKO = ((-1.6, -5.9), (1.6, -5.9), (-1.6, -4.1), (1.6, -4.1))
for (x, z) in SOKO:
    box(x - 0.24, x + 0.24, PLINTH, PLINTH + 0.32, z - 0.24, z + 0.24, 'andesite', bevel=0.07, tint_c=(1.15, 1.15, 1.15), name='umpak')
    box(x - 0.13, x + 0.13, PLINTH + 0.32, 4.95, z - 0.13, z + 0.13, 'teak', bevel=0.02, name='soko-guru')
box(R['x0'], R['x1'], 2.88, 3.0, R['z1'] - 0.12, R['z1'] + 0.12, 'teak', bevel=0.015, name='front-beam')
# the reading corner: a low rattan chair, a woven mat and a small carved stand
box(sx - 1.2, sx + 1.0, PLINTH + 0.03, PLINTH + 0.04, sz - 1.4, sz + 0.3, 'banig', bevel=0.0, tint_c=(0.9, 0.85, 0.75), name='mat')
box(sx - 0.35, sx + 0.35, 0.47, 0.55, sz - 0.35, sz + 0.25, 'bamboo', bevel=0.04, tint_c=(0.9, 0.75, 0.55), name='rattan-seat')
box(sx - 0.35, sx + 0.35, 0.55, 1.05, sz - 0.42, sz - 0.32, 'sawali', bevel=0.04, tint_c=(0.9, 0.75, 0.55), name='rattan-back')
for dx in (-0.3, 0.3):
    for dz in (-0.3, 0.2):
        pole((sx + dx, PLINTH, sz + dz), (sx + dx, 0.47, sz + dz), 0.025, 'bamboo', tint_c=(0.8, 0.65, 0.45), name='rattan-leg')
box(sx + 0.6, sx + 1.1, PLINTH, PLINTH + 0.45, sz - 0.6, sz - 0.1, 'teak', bevel=0.03, name='stand')
pole((sx + 0.85, PLINTH + 0.45, sz - 0.35), (sx + 0.85, PLINTH + 0.62, sz - 0.35), 0.06, 'terracotta', seg=10, name='teapot')
# a gamelan gong and a carved chest at the back, a batik hanging on the north wall
pole((-3.0, PLINTH + 0.6, -6.4), (-3.0, PLINTH + 0.6, -6.25), 0.42, 'gold', seg=18, name='gong')
for x in (-3.4, -2.6):
    box(x - 0.05, x + 0.05, PLINTH, PLINTH + 1.1, -6.38, -6.28, 'teak', bevel=0.01, name='gong-frame')
box(-3.5, -2.5, PLINTH + 1.05, PLINTH + 1.15, -6.38, -6.28, 'teak', bevel=0.01, name='gong-frame')
box(3.2, 4.4, PLINTH, PLINTH + 0.6, -6.8, -6.2, 'gebyok', bevel=0.03, name='chest')
box(-0.8, 0.8, 1.2, 2.5, R['z0'] + 0.07, R['z0'] + 0.09, 'banig', bevel=0.0, tint_c=(0.6, 0.45, 0.6), name='batik')

# ================================================================ the joglo roof
# eave rectangle at 3 m; break to a steeper middle at 4.3 m; brunjung from 5.4 m to the ridge
TH = 0.14
E = (R['x0'] - 1.0, R['x1'] + 1.0, R['z0'] - 0.9, R['z1'] + 0.1, 2.95)
M = (-3.4, 3.4, -6.5, -3.5, 4.2)
B = (-2.5, 2.5, -6.15, -3.85, 5.1)
RG = (-1.7, 1.7, -5.0, 7.1)


def band(lo, hi, mat, tone=(1, 1, 1), name='roof'):
    a = rect(lo[0], lo[1], lo[2], lo[3], lo[4])
    b = rect(hi[0], hi[1], hi[2], hi[3], hi[4])
    solid([a, [(p[0], p[1] + TH, p[2]) for p in a][::1]], mat, tone, name=name + '-edge', cap_top=False, cap_bottom=False)
    solid([[(p[0], p[1] + TH, p[2]) for p in a], [(p[0], p[1] + TH, p[2]) for p in b]], mat, tone, name=name, cap_top=False, cap_bottom=False)
    solid([a, b], 'teak', (0.8, 0.8, 0.8), name=name + '-under', cap_top=False, cap_bottom=False)


band(E, M, 'genteng', (1, 1, 1), 'skirt')
band(M, B, 'genteng', (0.95, 0.95, 0.95), 'middle')
solid([[(p[0], p[1] + TH, p[2]) for p in rect(B[0], B[1], B[2], B[3], B[4])], [(RG[1], RG[3], RG[2]), (RG[1], RG[3], RG[2]), (RG[0], RG[3], RG[2]), (RG[0], RG[3], RG[2])]], 'genteng', (0.9, 0.9, 0.9), name='brunjung', cap_top=False, cap_bottom=False)
# ridge and hip caps in darker tile, mustaka finials at the ridge ends
pole((RG[0] - 0.1, RG[3] + 0.06, RG[2]), (RG[1] + 0.1, RG[3] + 0.06, RG[2]), 0.12, 'genteng', seg=8, tint_c=(0.7, 0.65, 0.62), name='ridge')
for (cx, cz) in ((E[0], E[3]), (E[1], E[3]), (E[1], E[2]), (E[0], E[2])):
    pole((cx, E[4] + TH, cz), ((M[0] if cx < 0 else M[1]), M[4] + TH, (M[3] if cz > -5 else M[2])), 0.07, 'genteng', seg=6, tint_c=(0.7, 0.65, 0.62), name='hip')
for (cx, cz) in ((M[0], M[3]), (M[1], M[3]), (M[1], M[2]), (M[0], M[2])):
    pole((cx, M[4] + TH, cz), ((B[0] if cx < 0 else B[1]), B[4] + TH, (B[3] if cz > -5 else B[2])), 0.07, 'genteng', seg=6, tint_c=(0.7, 0.65, 0.62), name='hip')
for (cx, cz) in ((B[0], B[3]), (B[1], B[3]), (B[1], B[2]), (B[0], B[2])):
    pole((cx, B[4] + TH, cz), ((RG[0] if cx < 0 else RG[1]), RG[3], RG[2]), 0.07, 'genteng', seg=6, tint_c=(0.7, 0.65, 0.62), name='hip')
for x in (RG[0] - 0.1, RG[1] + 0.1):
    pole((x, RG[3] + 0.1, RG[2]), (x, RG[3] + 0.55, RG[2]), 0.12, 'terracotta', seg=8, r2=0.02, tint_c=(0.8, 0.7, 0.6), name='mustaka')
# fascia boards along the eave
for (a, b) in (((E[0], E[3]), (E[1], E[3])), ((E[1], E[3]), (E[1], E[2])), ((E[1], E[2]), (E[0], E[2])), ((E[0], E[2]), (E[0], E[3]))):
    pole((a[0], E[4] - 0.02, a[1]), (b[0], E[4] - 0.02, b[1]), 0.06, 'teak', seg=4, name='fascia')

# ================================================================ red-brick garden walls, 2.2 m
for key in ('east garden wall', 'south garden wall', 'west garden wall'):
    b = BOX[key]
    x0, x1 = b['c'][0] - b['h'][0], b['c'][0] + b['h'][0]
    z0, z1 = b['c'][2] - b['h'][2], b['c'][2] + b['h'][2]
    top = b['c'][1] + b['h'][1]
    box(x0, x1, 0.0, top - 0.12, z0, z1, 'brick', bevel=0.0, name='wall')
    box(x0 - 0.05, x1 + 0.05, top - 0.12, top + 0.02, z0 - 0.05, z1 + 0.05, 'plaster', bevel=0.02, name='coping')
    box(x0 - 0.04, x1 + 0.04, 0.0, 0.25, z0 - 0.04, z1 + 0.04, 'plaster', bevel=0.01, tint_c=(0.9, 0.88, 0.85), name='plinth')
    along_x = (x1 - x0) > (z1 - z0)
    L0, L1 = (x0, x1) if along_x else (z0, z1)
    t = L0
    while t <= L1 + 0.01:  # brick piers with plaster caps
        if along_x:
            box(t - 0.18, t + 0.18, 0.0, top + 0.12, z0 - 0.06, z1 + 0.06, 'brick', bevel=0.01, name='pier')
            box(t - 0.22, t + 0.22, top + 0.12, top + 0.24, z0 - 0.1, z1 + 0.1, 'plaster', bevel=0.03, name='pier-cap')
        else:
            box(x0 - 0.06, x1 + 0.06, 0.0, top + 0.12, t - 0.18, t + 0.18, 'brick', bevel=0.01, name='pier')
            box(x0 - 0.1, x1 + 0.1, top + 0.12, top + 0.24, t - 0.22, t + 0.22, 'plaster', bevel=0.03, name='pier-cap')
        t += 2.5

# ================================================================ the neighbour: Jakarta kampung house
nh = BOX['neighbour house']
nx0, nx1 = nh['c'][0] - nh['h'][0], nh['c'][0] + nh['h'][0]
nz0, nz1 = nh['c'][2] - nh['h'][2], nh['c'][2] + nh['h'][2]
ny1 = nh['c'][1] + nh['h'][1]
GF = 2.4
box(nx0, nx1, 0.0, GF, nz0, nz1, 'mint', bevel=0.05, name='n-ground')
box(nx0 - 0.05, nx1 + 0.05, GF, GF + 0.15, nz0 - 0.05, nz1 + 0.05, 'plaster', bevel=0.02, name='n-band')
box(nx0, nx1, GF + 0.15, 3.85, nz0, nz1, 'yellow', bevel=0.05, name='n-upper')
# hipped genteng roof inside the box: eave 3.85 m, ridge 4.6 m
solid([rect(nx0 - 0.35, nx1 + 0.35, nz0 - 0.35, nz1 + 0.35, 3.8), [(nx1 - 1.0, ny1, (nz0 + nz1) / 2), (nx1 - 1.0, ny1, (nz0 + nz1) / 2), (nx0 + 1.0, ny1, (nz0 + nz1) / 2), (nx0 + 1.0, ny1, (nz0 + nz1) / 2)]], 'genteng', name='n-roof', cap_top=False)
wy, wz = N['window'][1], N['window'][2]
box(nx0 - 0.06, nx0 + 0.02, wy - 0.6, wy + 0.6, wz - 0.7, wz + 0.7, 'char', bevel=0.0, name='n-win-dark')
for k in range(9):  # teralis: a steel window grille
    zz = wz - 0.65 + k * 0.16
    pole((nx0 - 0.1, wy - 0.6, zz), (nx0 - 0.1, wy + 0.6, zz), 0.012, 'steel', seg=4, name='teralis')
for y in (wy - 0.2, wy + 0.25):
    pole((nx0 - 0.1, y, wz - 0.7), (nx0 - 0.1, y, wz + 0.7), 0.012, 'steel', seg=4, name='teralis')
box(nx0 - 0.85, nx0, GF - 0.05, GF + 0.12, wz - 1.1, wz + 1.1, 'plaster', bevel=0.02, name='n-balcony')
for k in range(15):
    zz = wz - 1.05 + k * 0.15
    pole((nx0 - 0.82, GF + 0.12, zz), (nx0 - 0.82, GF + 0.95, zz), 0.016, 'steel', seg=4, name='rail')
pole((nx0 - 0.82, GF + 0.95, wz - 1.1), (nx0 - 0.82, GF + 0.95, wz + 1.1), 0.025, 'steel', seg=6, name='rail-top')
for zz in (wz - 0.8, wz + 0.85):
    pole((nx0 - 0.55, GF + 0.12, zz), (nx0 - 0.55, GF + 0.36, zz), 0.13, 'terracotta', seg=10, r2=0.1, name='pot')
    blob(nx0 - 0.55, GF + 0.55, zz, 0.24, 'leaf', jitter((1, 1, 1), 0.1), seed=int(zz * 10), name='pot-plant')
# south face: a shop window with a rolling shutter half up, a door, a sign; upper windows with grilles
box(nx0 + 0.5, nx0 + 2.6, 0.0, 2.1, nz1 - 0.03, nz1 + 0.02, 'char', bevel=0.0, name='shop-dark')
box(nx0 + 0.45, nx0 + 2.65, 1.3, 2.15, nz1, nz1 + 0.06, 'gi', bevel=0.0, name='shutter')
box(nx0 + 0.45, nx0 + 2.65, 2.2, 2.38, nz1, nz1 + 0.08, 'sign', bevel=0.01, tint_c=(0.4, 0.75, 1.0), name='shop-sign')
for k in range(5):
    box(nx0 + 0.7 + k * 0.38, nx0 + 0.95 + k * 0.38, 0.0, 0.9, nz1 - 0.25, nz1 - 0.05, 'cloth', bevel=0.01, tint_c=rnd.choice([(0.9, 0.3, 0.25), (0.2, 0.5, 0.8), (0.95, 0.8, 0.2)]), name='goods')
box(nx0 + 2.9, nx0 + 3.8, 0.0, 2.1, nz1 - 0.03, nz1 + 0.03, 'teak', bevel=0.01, name='n-door')
for x in (nx0 + 1.1, nx0 + 3.0):
    box(x - 0.5, x + 0.5, 2.8, 3.6, nz1 - 0.02, nz1 + 0.03, 'char', bevel=0.0, name='n-upwin')
    for k in range(6):
        pole((x - 0.45 + k * 0.18, 2.8, nz1 + 0.05), (x - 0.45 + k * 0.18, 3.6, nz1 + 0.05), 0.012, 'steel', seg=4, name='teralis')
# a scooter parked in front, and a satellite dish on the roof edge
sxs, szs = nx0 + 1.6, nz1 + 0.9
obox((sxs, 0.45, szs), (1.2, 0.28, 0.3), (0, 0, 0), 'scooter', bevel=0.1, name='scooter-body')
obox((sxs - 0.15, 0.68, szs), (0.6, 0.08, 0.26), (0, 0, 0), 'char', bevel=0.04, name='scooter-seat')
pole((sxs + 0.5, 0.45, szs), (sxs + 0.42, 1.0, szs), 0.03, 'steel', name='scooter-stem')
pole((sxs + 0.42, 1.0, szs - 0.3), (sxs + 0.42, 1.0, szs + 0.3), 0.02, 'steel', name='scooter-bar')
for x in (sxs - 0.45, sxs + 0.55):
    pole((x, 0.2, szs - 0.06), (x, 0.2, szs + 0.06), 0.2, 'char', seg=12, name='wheel')
pole((nx1 - 0.3, 3.8, nz1 - 0.5), (nx1 - 0.3, 4.3, nz1 - 0.5), 0.025, 'steel', seg=4, name='dish-arm')
obox((nx1 - 0.3, 4.35, nz1 - 0.5), (0.05, 0.55, 0.55), (0, 0, -25), 'trim', bevel=0.2, name='dish')

# ================================================================ around: frangipani, banana, rice terrace
def kamboja(x, z, h=2.6, seed=0):
    """Frangipani: a few crooked grey branches ending in leaf rosettes with cream flowers."""
    k = random.Random(seed)
    pole((x, 0.0, z), (x, h * 0.45, z), 0.11, 'trunk', seg=8, r2=0.09, tint_c=(0.75, 0.72, 0.7), name='kamboja')
    for i in range(5):
        a = i / 5 * math.tau + k.uniform(-0.3, 0.3)
        ex, ez = x + math.cos(a) * k.uniform(0.6, 1.0), z + math.sin(a) * k.uniform(0.6, 1.0)
        ey = h * k.uniform(0.75, 1.0)
        pole((x, h * 0.45, z), (ex, ey, ez), 0.06, 'trunk', seg=6, r2=0.04, tint_c=(0.75, 0.72, 0.7), name='kamboja')
        blob(ex, ey + 0.1, ez, 0.42, 'leaf', jitter((0.95, 1.05, 0.9), 0.1), squash=0.55, seed=seed * 10 + i, name='kamboja-leaf')
        for j in range(4):
            fa = k.uniform(0, math.tau)
            blob(ex + math.cos(fa) * 0.28, ey + 0.28, ez + math.sin(fa) * 0.28, 0.07, 'kamboja', (1, 1, 1), squash=0.5, seed=seed * 100 + i * 10 + j, name='kamboja-flower')


kamboja(-6.8, -6.4, seed=1)
kamboja(6.6, -7.6, 2.4, seed=2)
banana(-7.4, -7.8, seed=3)
banana(3.8, -8.4, 2.4, seed=4)
# low shrubs and a second frangipani on the west lawn (low enough to keep shadows off the yard)
for (x, z, r) in ((-6.4, 0.4, 0.45), (-7.2, 1.6, 0.35), (-6.0, 2.8, 0.4), (-7.6, -1.6, 0.4)):
    shrub(x, z, r, flowers=False)
kamboja(-7.6, 4.0, 1.6, seed=5)
