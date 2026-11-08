# ================================================================ THAILAND: ruen thai by the khlong
# (helpers and materials: parts/common.py)
# Inside what src/sim checks: room x -5..5, z -7..-3 with solid north, west and east sides to 3 m,
# a roof plane at 3 m and an open courtyard face; the reader's eye 1.05 m at (1.6, -3.5); the garden
# wall 0.9 m; the neighbour inside its box below 4.6 m.
#   a traditional central Thai house: two teak pavilions (the main ruen and the kitchen) raised on
#   round posts with an open terrace (chan) between them and a tree growing through it; steep gable
#   roofs of small clay tiles with a kicked lower eave, pan lom bargeboards with hooked ends and
#   crossed kalae tips, sunburst gables, fa pakon panel walls, tall windows with open shutters.
#   The reader sits on a teak daybed (tang) in the shaded space under the house (tai thun), which is
#   slatted on the north, west and east.
# In Bangkok in November the noon sun stands about 60 degrees high, so every ray that reaches the
# reader crosses the open face below 2.0 m: the floors at 1.7 and 2.0 m shade nothing the checks
# let through. No post stands on the open face where the reader's rays or the neighbour's sight
# line cross it (x 0..3.3). Courtyard gables stop at z -2.9.
#   garden: a whitewashed wall with terracotta coping, brick paving, a lotus pond, glazed lotus jars,
#   a teak table with a food carrier; outside: the spirit house, plumerias, a power pole and its
#   wires, a canal embankment with a water landing (tha nam) and a moored rowing boat.
#   neighbour: a Bangkok shophouse (tuek thaew) with a folding steel shutter and a burglar grille.


def _teak(nt, bsdf, coord):
    # oiled teak: warm brown with long grain streaks
    w = nt.nodes.new('ShaderNodeTexWave')
    w.bands_direction = 'Z'
    w.inputs['Scale'].default_value = 3.0
    w.inputs['Distortion'].default_value = 6.0
    w.inputs['Detail'].default_value = 3.0
    nt.links.new(coord.outputs['Object'], w.inputs['Vector'])
    c = mix(nt, w.outputs['Fac'], rgb(nt, S('#6b3a1c')), rgb(nt, S('#9a5a2c')))
    c = mix(nt, noise(nt, coord, 2.0, 3, 0.4), c, rgb(nt, S('#7d4522')))
    nt.links.new(tint(nt, c), bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.55


def _thtile(nt, bsdf, coord):
    # small flat clay tiles, staggered, with darker weathering
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (4.0, 4.0, 4.0)
    nt.links.new(coord.outputs['Object'], mp.inputs['Vector'])
    br = nt.nodes.new('ShaderNodeTexBrick')
    br.inputs['Color1'].default_value = (*S('#d9763f'), 1)
    br.inputs['Color2'].default_value = (*S('#c4612f'), 1)
    br.inputs['Mortar'].default_value = (*S('#5a2a17'), 1)
    br.inputs['Mortar Size'].default_value = 0.025
    br.inputs['Brick Width'].default_value = 0.32
    br.inputs['Row Height'].default_value = 0.22
    nt.links.new(mp.outputs['Vector'], br.inputs['Vector'])
    c = mix(nt, noise(nt, coord, 0.9, 3, 0.55), br.outputs['Color'], rgb(nt, S('#9a5a3a')))
    nt.links.new(tint(nt, c), bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.75


def _brick(nt, bsdf, coord):
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (4.5, 4.5, 4.5)
    nt.links.new(coord.outputs['Object'], mp.inputs['Vector'])
    br = nt.nodes.new('ShaderNodeTexBrick')
    br.inputs['Color1'].default_value = (*S('#b5583a'), 1)
    br.inputs['Color2'].default_value = (*S('#9c4a31'), 1)
    br.inputs['Mortar'].default_value = (*S('#d8c7a8'), 1)
    br.inputs['Mortar Size'].default_value = 0.03
    br.inputs['Brick Width'].default_value = 0.5
    br.inputs['Row Height'].default_value = 0.25
    nt.links.new(mp.outputs['Vector'], br.inputs['Vector'])
    c = mix(nt, noise(nt, coord, 1.5, 3, 0.4), br.outputs['Color'], rgb(nt, S('#8a5a44')))
    nt.links.new(tint(nt, c), bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.85


def _glaze(base, rough=0.22):
    def build(nt, bsdf, coord):
        c = mix(nt, noise(nt, coord, 5.0, 3, 0.5), rgb(nt, base), rgb(nt, tuple(v * 0.7 for v in base)))
        nt.links.new(tint(nt, c), bsdf.inputs['Base Color'])
        bsdf.inputs['Roughness'].default_value = rough
    return build


MATS.update({
    'teak': node_mat('teak', _teak),
    'thtile': node_mat('thtile', _thtile),
    'brick': node_mat('brick', _brick),
    'lime': node_mat('lime', _plaster(S('#f4f0e6'))),
    'terracotta': node_mat('terracotta', card(S('#b9572f'), 0.05)),
    'laterite': node_mat('laterite', card(S('#9b7a5c'), 0.07)),
    'gold': node_mat('gold', flat(S('#d9a52c'), 0.35)),
    'lacquer': node_mat('lacquer', flat(S('#a3221c'), 0.4)),
    'glaze': node_mat('glaze', _glaze(S('#6a3d1e'))),
    'celadon': node_mat('celadon', _glaze(S('#8db59c'))),
    'lotus': node_mat('lotus', flat(S('#f28cb1'), 0.6)),
    'marigold': node_mat('marigold', flat(S('#f39a1b'), 0.7)),
    'cream': node_mat('cream', _plaster(S('#ece1c6'))),
    'mint': node_mat('mint', _plaster(S('#bfe0cf'))),
    'enamel': node_mat('enamel', flat(S('#2f8f6b'), 0.3)),
    'silk': node_mat('silk', flat(S('#b3262a'), 0.55)),
    'frangi': node_mat('frangi', flat(S('#fbf6e8'), 0.6)),
    'concrete': node_mat('concrete', card(S('#bdb7ab'), 0.05)),
    'wire': node_mat('wire', flat(S('#17181a'), 0.6)),
})

R = LAY['room']
C = LAY['court']
N = LAY['neighbour']
sx, _, sz = LAY['seat']
pool = {'x0': -4.3, 'x1': -1.6, 'z0': 0.3, 'z1': 2.9}
GW = 0.9      # garden wall
F = 2.0       # pavilion floors
FT = 1.7      # terrace floor
WT = 4.0      # wall plate
MX0, MX1 = -0.1, 5.0   # main ruen
KX0, KX1 = -4.9, -2.0  # kitchen ruen
SZ, NZ = R['z1'], R['z0']  # -3 and -7


def plank(a, b, w, t, mat, tint_c=(1, 1, 1), name='plank', bevel=0.0):
    """A board from a to b in one z plane (a, b are site (x, y, z) with the same z)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    c = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, a[2])
    return obox(c, (L, w, t), (0, 0, math.degrees(math.atan2(dy, dx))), mat, tint_c=tint_c, bevel=bevel, name=name)


def slab(quad, T, mat, tint_c=(1, 1, 1), name='slab'):
    return solid([quad, [(p[0], p[1] + T, p[2]) for p in quad]], mat, tint_c=tint_c, name=name)


def lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(len(a)))


# ================================================================ garden
box(C['x0'], C['x1'], -0.04, 0.02, C['z0'], C['z1'], 'grass', bevel=0.0, name='yard')
# brick apron along the house and a brick path: apron -> table -> gate
box(C['x0'] + 0.1, C['x1'] - 0.1, 0.0, 0.035, SZ, SZ + 1.05, 'brick', bevel=0.0, name='apron')
box(C['x0'] + 0.08, C['x1'] - 0.08, 0.0, 0.05, SZ + 1.05, SZ + 1.15, 'laterite', bevel=0.01, name='apron-edge')
for (x0_, x1_, z0_, z1_) in ((0.0, 1.2, SZ + 1.15, 2.0), (0.0, 3.5, 2.0, 3.2), (0.0, 1.2, 3.2, C['z1'])):
    box(x0_, x1_, 0.0, 0.032, z0_, z1_, 'brick', bevel=0.0, name='brick-path')
# a lotus pond: a laterite rim, dark water, floating pads to the south, standing leaves to the north
box(pool['x0'], pool['x1'], -0.45, -0.3, pool['z0'], pool['z1'], 'water-bed', bevel=0.0, name='pond-bed')
for (a, b, c, d) in ((pool['x0'] - 0.18, pool['x1'] + 0.18, pool['z0'] - 0.18, pool['z0']), (pool['x0'] - 0.18, pool['x1'] + 0.18, pool['z1'], pool['z1'] + 0.18), (pool['x0'] - 0.18, pool['x0'], pool['z0'], pool['z1']), (pool['x1'], pool['x1'] + 0.18, pool['z0'], pool['z1'])):
    box(a, b, -0.45, 0.12, c, d, 'laterite', bevel=0.02, name='pond-rim')
for (x, zz, r) in ((-3.7, 2.4, 0.26), (-2.3, 2.5, 0.22), (-3.3, 1.9, 0.2), (-2.0, 1.4, 0.18), (-3.9, 1.3, 0.2), (-2.7, 2.7, 0.16)):
    pole((x, 0.06, zz), (x, 0.075, zz), r, 'leaf', seg=12, tint_c=(0.85, 1.05, 0.85), name='lotus-pad')
for (x, zz, h) in ((-3.9, 0.55, 0.45), (-3.4, 0.6, 0.6), (-2.2, 0.5, 0.5), (-1.85, 0.75, 0.35), (-2.8, 0.45, 0.55)):
    pole((x, 0.0, zz), (x, h, zz), 0.012, 'leaf', seg=4, tint_c=(0.9, 1.1, 0.7), name='lotus-stalk')
    obox((x, h, zz), (0.42, 0.02, 0.42), (rnd.uniform(-15, 15), rnd.uniform(0, 90), rnd.uniform(-15, 15)), 'leaf', tint_c=(0.8, 1.08, 0.82), bevel=0.0, name='lotus-leaf')
for (x, zz, h) in ((-3.1, 0.5, 0.7), (-2.5, 0.65, 0.62)):
    pole((x, 0.0, zz), (x, h, zz), 0.01, 'leaf', seg=4, name='lotus-stalk')
    for k in range(5):
        a = k / 5 * 360
        obox((x, h + 0.06, zz), (0.05, 0.16, 0.09), (12, a, 0), 'lotus', bevel=0.02, name='lotus-petal')
# the teak table at the table spot (top 0.75 m): round top, four stools, a pinto food carrier
tx, tz = 2.6, 2.6
pole((tx, 0.71, tz), (tx, 0.76, tz), 0.62, 'teak', seg=24, name='table-top')
pole((tx, 0.0, tz), (tx, 0.71, tz), 0.08, 'teak', seg=10, name='table-stem')
for a in (0, 90, 180, 270):
    ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
    obox((tx + ca * 0.22, 0.05, tz + sa * 0.22), (0.5, 0.08, 0.08), (0, -a, 0), 'teak', bevel=0.02, name='table-foot')
for a in (20, 110, 200, 290):
    ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
    cx_, cz_ = tx + ca * 0.95, tz + sa * 0.95
    pole((cx_, 0.0, cz_), (cx_, 0.44, cz_), 0.2, 'teak', seg=12, r2=0.17, tint_c=(0.9, 0.9, 0.9), name='stool')
for k in range(3):
    pole((tx + 0.1, 0.76 + k * 0.11, tz - 0.05), (tx + 0.1, 0.86 + k * 0.11, tz - 0.05), 0.1, 'enamel', seg=14, tint_c=((1, 1, 1), (1.2, 0.5, 0.35), (1, 1, 1))[k], name='pinto')
pole((tx + 0.1, 1.09, tz - 0.05), (tx + 0.1, 1.11, tz - 0.05), 0.1, 'steel', seg=14, tint_c=(2.5, 2.5, 2.5), name='pinto-lid')
for dx in (-0.09, 0.09):
    pole((tx + 0.1 + dx, 0.8, tz - 0.05), (tx + 0.1 + dx, 1.24, tz - 0.05), 0.008, 'steel', seg=4, tint_c=(2.5, 2.5, 2.5), name='pinto-rail')
pole((tx + 0.01, 1.24, tz - 0.05), (tx + 0.19, 1.24, tz - 0.05), 0.012, 'steel', seg=4, tint_c=(2.5, 2.5, 2.5), name='pinto-handle')
pole((tx - 0.25, 0.76, tz + 0.15), (tx - 0.25, 0.94, tz + 0.15), 0.07, 'celadon', seg=12, r2=0.05, name='jug')
for (x, z) in ((tx - 0.1, tz + 0.35), (tx + 0.3, tz + 0.25)):
    pole((x, 0.76, z), (x, 0.8, z), 0.09, 'celadon', seg=12, r2=0.11, name='bowl')
# a teak bench at the deck spot (eye 0.8 m)
box(0.45, 1.95, 0.4, 0.46, -2.85, -2.15, 'teak', bevel=0.02, name='bench')
for x in (0.55, 1.85):
    for z in (-2.75, -2.25):
        box(x - 0.04, x + 0.04, 0.0, 0.4, z - 0.04, z + 0.04, 'teak', bevel=0.0, tint_c=(0.85, 0.85, 0.85), name='bench-leg')
# glazed lotus jars (ong bua) along the south wall, and two beside the house steps
for (x, z, r, h, m) in ((-4.4, 3.55, 0.3, 0.5, 'glaze'), (-0.6, 3.6, 0.26, 0.45, 'celadon'), (2.1, 3.6, 0.3, 0.5, 'glaze'), (4.4, 3.55, 0.28, 0.48, 'celadon')):
    pole((x, 0.0, z), (x, h * 0.6, z), r * 0.7, m, seg=16, r2=r, name='jar')
    pole((x, h * 0.6, z), (x, h, z), r, m, seg=16, r2=r * 0.85, name='jar')
    pole((x, h - 0.03, z), (x, h - 0.02, z), r * 0.8, 'water-bed', seg=16, name='jar-water')
    for k in range(3):
        a = rnd.uniform(0, math.tau)
        pole((x + math.cos(a) * r * 0.4, h - 0.015, z + math.sin(a) * r * 0.4), (x + math.cos(a) * r * 0.4, h - 0.005, z + math.sin(a) * r * 0.4), 0.09, 'leaf', seg=10, name='jar-pad')
    obox((x, h + 0.04, z), (0.07, 0.08, 0.07), (0, 0, 0), 'lotus', bevel=0.03, name='jar-bud')
# clipped low hedges (khoi) inside the east and west walls, under 0.6 m
for (x, z0_, z1_) in ((4.65, -1.4, 3.1), (-4.65, -1.6, -0.2)):
    z = z0_
    while z < z1_:
        blob(x, 0.32, z + 0.25, 0.3, 'leaf', jitter((0.85, 1.0, 0.8), 0.06), squash=0.95, seed=int(z * 10 + x * 3) + 300, name='khoi')
        z += 0.5

# ================================================================ the house: posts, floors, tai thun
def post(x, z, top):
    box(x - 0.17, x + 0.17, -0.02, 0.12, z - 0.17, z + 0.17, 'footing', bevel=0.03, name='footing')
    pole((x, 0.12, z), (x, top, z), 0.13, 'teak', seg=12, r2=0.105, name='post')


for x in (MX0, 1.6, 3.5, MX1):
    for z in (NZ, -5.0, SZ):
        if z == SZ and 0.0 < x < 3.3:
            continue  # keep the open face clear where the reader's rays and the window's line cross it
        outer = z in (NZ, SZ) or x in (MX0, MX1)
        post(x, z, WT if outer else F)
for x in (KX0, -3.45, KX1):
    for z in (NZ, -5.0, SZ):
        outer = z in (NZ, SZ) or x in (KX0, KX1)
        post(x, z, WT if outer else F)
# floor beams under each pavilion, the floor boards and their fascia
for (x0_, x1_, fy) in ((MX0, MX1, F), (KX0, KX1, F)):
    for z in (NZ, -5.0, SZ):
        box(x0_ - 0.15, x1_ + 0.15, fy - 0.32, fy - 0.12, z - 0.09, z + 0.09, 'teak', bevel=0.01, tint_c=(0.8, 0.8, 0.8), name='beam')
    box(x0_ - 0.12, x1_ + 0.12, fy - 0.12, fy, NZ - 0.12, SZ + 0.08, 'teak', bevel=0.0, tint_c=(0.9, 0.9, 0.9), name='floor')
    box(x0_ - 0.14, x1_ + 0.14, fy - 0.2, fy + 0.02, SZ + 0.06, SZ + 0.1, 'teak', bevel=0.005, tint_c=(0.7, 0.7, 0.7), name='fascia')
# the chan: a terrace a step lower between the pavilions, with an opening for the stair
box(KX1 + 0.12, MX0 - 0.12, FT - 0.3, FT - 0.14, NZ - 0.05, SZ + 0.05, 'teak', bevel=0.0, tint_c=(0.8, 0.8, 0.8), name='chan-beam')
for (z0_, z1_, xa_, xb_) in ((NZ - 0.1, -4.95, KX1 + 0.12, MX0 - 0.12), (-4.95, SZ + 0.08, KX1 + 0.12, -1.6), (-4.95, SZ + 0.08, -0.55, MX0 - 0.12)):
    box(xa_, xb_, FT - 0.12, FT, z0_, z1_, 'teak', bevel=0.0, tint_c=(1.05, 1.0, 0.95), name='chan')
    x = xa_ + 0.15
    while x < xb_:
        box(x, x + 0.012, FT, FT + 0.003, z0_, z1_, 'char', bevel=0.0, name='chan-joint')
        x += 0.17
# a low panelled balustrade round the chan (top 0.6 m above it) and round the stair head
def balustrade(a, b, y0):
    plank((a[0], y0 + 0.6, a[1]), (b[0], y0 + 0.6, b[1]), 0.07, 0.12, 'teak', name='bal-rail') if a[1] == b[1] else None
    L = math.dist(a, b)
    n = max(1, int(L / 0.16))
    for k in range(n + 1):
        p = lerp(a, b, k / n)
        box(p[0] - 0.025, p[0] + 0.025, y0, y0 + 0.57, p[1] - 0.025, p[1] + 0.025, 'teak', bevel=0.0, tint_c=(0.85, 0.85, 0.85), name='baluster')
    if a[1] != b[1]:
        box(a[0] - 0.05, a[0] + 0.05, y0 + 0.57, y0 + 0.64, min(a[1], b[1]), max(a[1], b[1]), 'teak', bevel=0.01, name='bal-rail')


balustrade((KX1 + 0.15, SZ + 0.02), (-1.62, SZ + 0.02), FT)
balustrade((-0.53, SZ + 0.02), (MX0 - 0.15, SZ + 0.02), FT)
balustrade((-1.62, SZ + 0.02), (-1.62, -4.9), FT)
balustrade((-0.53, SZ + 0.02), (-0.53, -4.9), FT)
# north edge of the chan: a teak lattice screen to 3 m (the checks treat the north side as solid)
box(KX1 + 0.1, MX0 - 0.1, FT, 3.0, NZ - 0.04, NZ + 0.04, 'char', bevel=0.0, name='chan-screen-back')
x = KX1 + 0.15
while x < MX0 - 0.1:
    box(x - 0.03, x + 0.03, FT, 3.0, NZ + 0.04, NZ + 0.08, 'teak', bevel=0.0, name='chan-lattice')
    x += 0.2
for y in (FT + 0.4, 2.35, 2.95):
    box(KX1 + 0.1, MX0 - 0.1, y - 0.04, y + 0.04, NZ + 0.08, NZ + 0.12, 'teak', bevel=0.0, tint_c=(0.8, 0.8, 0.8), name='chan-lattice-rail')
# the stair: from the brick apron north up to the chan, inside the footprint
n_st = 9
for k in range(n_st):
    y = (k + 1) * FT / (n_st + 1)
    z = SZ - 0.15 - k * (1.85 / n_st)
    box(-1.55, -0.6, y - 0.05, y, z - 0.24, z, 'teak', bevel=0.01, tint_c=(1.05, 1.0, 0.95), name='tread')
for x in (-1.58, -0.57):
    plank((x, 0.0, -3.15), (x, FT, -5.0), 0.2, 0.06, 'teak', tint_c=(0.75, 0.75, 0.75), name='stringer')
    obox((x, FT / 2 + 0.65, -4.05), (0.05, 0.05, 2.15), (math.degrees(math.atan2(FT, 1.85)), 0, 0), 'teak', name='stair-rail')
    box(x - 0.04, x + 0.04, 0.0, 0.95, -3.22, -3.14, 'teak', bevel=0.01, name='newel')
# the tai thun: teak slat screens on the north, west and east (solid to the checks), open to the yard
def slat_screen(a, b, y0, y1, step=0.13):
    L = math.dist(a, b)
    n = max(1, int(L / step))
    along_x = abs(b[0] - a[0]) > abs(b[1] - a[1])
    for k in range(n + 1):
        p = lerp(a, b, k / n)
        if along_x:
            box(p[0] - 0.035, p[0] + 0.035, y0, y1, p[1] - 0.02, p[1] + 0.02, 'teak', bevel=0.0, tint_c=jitter((0.95, 0.95, 0.95), 0.06), name='slat')
        else:
            box(p[0] - 0.02, p[0] + 0.02, y0, y1, p[1] - 0.035, p[1] + 0.035, 'teak', bevel=0.0, tint_c=jitter((0.95, 0.95, 0.95), 0.06), name='slat')
    for y in (y0 + 0.25, (y0 + y1) / 2, y1 - 0.1):
        if along_x:
            box(min(a[0], b[0]), max(a[0], b[0]), y - 0.04, y + 0.04, a[1] + 0.02, a[1] + 0.07, 'teak', bevel=0.0, tint_c=(0.75, 0.75, 0.75), name='slat-rail')
        else:
            box(a[0] + (0.02 if a[0] < 0 else -0.07), a[0] + (0.07 if a[0] < 0 else -0.02), y - 0.04, y + 0.04, min(a[1], b[1]), max(a[1], b[1]), 'teak', bevel=0.0, tint_c=(0.75, 0.75, 0.75), name='slat-rail')


slat_screen((MX0, NZ), (MX1, NZ), 0.1, F - 0.3)
slat_screen((KX0, NZ), (KX1, NZ), 0.1, F - 0.3)
slat_screen((KX1, NZ), (MX0, NZ), 0.1, FT - 0.3)
slat_screen((MX1, NZ), (MX1, SZ), 0.1, F - 0.3)
slat_screen((KX0, NZ), (KX0, SZ), 0.1, F - 0.3)
box(C['x0'] - 0.05, C['x1'] + 0.05, -0.02, 0.03, NZ, SZ, 'earth', bevel=0.0, tint_c=(1.1, 1.05, 1.0), name='tai-thun-floor')
# the reader's tang (teak daybed), seat 0.45 m: eye 1.05 m at the checked spot, with a mon khwan
box(sx - 0.8, sx + 0.8, 0.38, 0.45, sz - 0.55, sz + 0.3, 'teak', bevel=0.02, name='tang')
for x in (sx - 0.72, sx + 0.72):
    for z in (sz - 0.47, sz + 0.22):
        box(x - 0.05, x + 0.05, 0.0, 0.38, z - 0.05, z + 0.05, 'teak', bevel=0.0, tint_c=(0.8, 0.8, 0.8), name='tang-leg')
box(sx - 0.75, sx + 0.75, 0.45, 0.47, sz - 0.5, sz + 0.25, 'banig', bevel=0.0, tint_c=(1.0, 0.95, 0.85), name='sua-mat')
mk = sz - 0.3
solid([[(sx - 0.45, 0.47, mk + 0.12), (sx - 0.45, 0.47, mk - 0.22), (sx - 0.45, 0.85, mk - 0.22)], [(sx + 0.15, 0.47, mk + 0.12), (sx + 0.15, 0.47, mk - 0.22), (sx + 0.15, 0.85, mk - 0.22)]], 'silk', name='mon-khwan')
for x in (sx - 0.46, sx + 0.16):
    solid([[(x, 0.5, mk + 0.06), (x, 0.5, mk - 0.18), (x, 0.79, mk - 0.18)], [(x + 0.02, 0.5, mk + 0.06), (x + 0.02, 0.5, mk - 0.18), (x + 0.02, 0.79, mk - 0.18)]], 'gold', name='mon-khwan-end')
for k in range(3):
    x = sx - 0.35 + k * 0.2
    box(x, x + 0.03, 0.472, 0.476, mk - 0.22, mk + 0.12, 'gold', bevel=0.0, name='mon-khwan-stripe')
box(sx + 0.3, sx + 0.7, 0.47, 0.52, sz - 0.35, sz + 0.05, 'teak', bevel=0.01, tint_c=(0.75, 0.75, 0.75), name='tea-tray')
pole((sx + 0.45, 0.52, sz - 0.2), (sx + 0.45, 0.66, sz - 0.2), 0.07, 'celadon', seg=12, r2=0.05, name='teapot')
for (x, z) in ((sx + 0.6, sz - 0.05), (sx + 0.38, sz - 0.02)):
    pole((x, 0.52, z), (x, 0.57, z), 0.035, 'celadon', seg=10, name='cup')
# under the kitchen: dragon jars, a hammock, a hanging dove cage, a basket stack
for (x, z, r) in ((-4.4, -6.5, 0.36), (-3.7, -6.55, 0.3)):
    pole((x, 0.0, z), (x, r * 1.4, z), r * 0.75, 'glaze', seg=16, r2=r, name='ong')
    pole((x, r * 1.4, z), (x, r * 2.1, z), r, 'glaze', seg=16, r2=r * 0.55, name='ong')
    pole((x, r * 1.35, z), (x, r * 1.5, z), r * 1.01, 'gold', seg=16, tint_c=(0.9, 0.8, 0.6), name='ong-band')
pts = []
for k in range(9):
    t = k / 8
    x = -4.75 + (-2.15 + 4.75) * t
    y = 1.35 - 0.55 * math.sin(math.pi * t)
    pts.append((x, y, -5.0))
for a, b in zip(pts, pts[1:]):
    plank(a, b, 0.01, 0.55, 'cloth', tint_c=(0.35, 0.55, 0.85), name='hammock')
for (x, z) in ((-3.0, -3.75),):
    pole((x, F - 0.32, z), (x, 1.55, z), 0.006, 'char', seg=4, name='cage-cord')
    pole((x, 1.08, z), (x, 1.12, z), 0.17, 'teak', seg=14, name='cage-base')
    for k in range(14):
        a = k / 14 * math.tau
        pole((x + math.cos(a) * 0.16, 1.12, z + math.sin(a) * 0.16), (x + math.cos(a) * 0.05, 1.52, z + math.sin(a) * 0.05), 0.006, 'bamboo', seg=4, name='cage-bar')
    pole((x, 1.52, z), (x, 1.58, z), 0.06, 'gold', seg=8, r2=0.01, name='cage-hook')
for k in range(3):
    pole((-2.6, k * 0.22, -6.5), (-2.6, k * 0.22 + 0.2, -6.5), 0.22 - k * 0.03, 'sawali', seg=12, r2=0.2 - k * 0.03, name='basket')

# ================================================================ pavilion walls, windows, doors
def panel_wall(a, b, y0, y1, face, mat='teak'):
    """A fa pakon wall from a to b (site x, z): a teak skin with a framed panel grid on the outside."""
    o = {'n': (0, -1), 's': (0, 1), 'e': (1, 0), 'w': (-1, 0)}[face]
    along_x = face in ('n', 's')
    if along_x:
        z = a[1]
        box(min(a[0], b[0]), max(a[0], b[0]), y0, y1, z - 0.05, z + 0.05, mat, bevel=0.0, tint_c=(0.92, 0.92, 0.92), name='wall-' + face)
    else:
        x = a[0]
        box(x - 0.05, x + 0.05, y0, y1, min(a[1], b[1]), max(a[1], b[1]), mat, bevel=0.0, tint_c=(0.92, 0.92, 0.92), name='wall-' + face)
    L = math.dist(a, b)
    n = max(1, round(L / 0.62))
    for k in range(n + 1):
        p = lerp(a, b, k / n)
        if along_x:
            box(p[0] - 0.035, p[0] + 0.035, y0, y1, z + o[1] * 0.05 - 0.02, z + o[1] * 0.05 + 0.02, 'teak', bevel=0.005, tint_c=(0.72, 0.7, 0.7), name='stile')
        else:
            box(x + o[0] * 0.05 - 0.02, x + o[0] * 0.05 + 0.02, y0, y1, p[1] - 0.035, p[1] + 0.035, 'teak', bevel=0.005, tint_c=(0.72, 0.7, 0.7), name='stile')
    for y in (y0 + 0.06, y0 + 0.45, y1 - 0.08):
        if along_x:
            box(min(a[0], b[0]), max(a[0], b[0]), y - 0.035, y + 0.035, z + o[1] * 0.05 - 0.02, z + o[1] * 0.05 + 0.02, 'teak', bevel=0.005, tint_c=(0.72, 0.7, 0.7), name='rail')
        else:
            box(x + o[0] * 0.05 - 0.02, x + o[0] * 0.05 + 0.02, y - 0.035, y + 0.035, min(a[1], b[1]), max(a[1], b[1]), 'teak', bevel=0.005, tint_c=(0.72, 0.7, 0.7), name='rail')


def window(cx, cz, face, w=0.78, y0=F + 0.45, y1=F + 1.7):
    """A tall Thai window: dark opening, carved apron below, two shutters swung flat to the wall."""
    o = {'n': (0, -1), 's': (0, 1), 'e': (1, 0), 'w': (-1, 0)}[face]
    hw = w / 2
    if face in ('n', 's'):
        z = cz + o[1] * 0.06
        box(cx - hw, cx + hw, y0, y1, z - 0.02, z + 0.02, 'char', bevel=0.0, name='win-dark')
        box(cx - hw - 0.07, cx + hw + 0.07, y0 - 0.06, y0, z - 0.04, z + 0.04, 'teak', bevel=0.01, tint_c=(0.7, 0.7, 0.7), name='win-sill')
        box(cx - hw - 0.1, cx + hw + 0.1, y1, y1 + 0.1, z - 0.05, z + 0.05, 'teak', bevel=0.01, tint_c=(0.7, 0.7, 0.7), name='win-head')
        box(cx - hw, cx + hw, F + 0.08, y0 - 0.06, z, z + o[1] * 0.025, 'teak', bevel=0.0, tint_c=(1.15, 1.1, 1.0), name='win-apron')
        for k in range(5):
            xx = cx - hw + 0.1 + k * (w - 0.2) / 4
            box(xx - 0.025, xx + 0.025, F + 0.12, y0 - 0.1, z + o[1] * 0.025, z + o[1] * 0.045, 'teak', bevel=0.0, tint_c=(0.7, 0.7, 0.7), name='win-baluster')
        for s_ in (-1, 1):
            x0_ = cx + s_ * hw
            box(min(x0_, x0_ + s_ * hw), max(x0_, x0_ + s_ * hw), y0, y1, z + o[1] * 0.03, z + o[1] * 0.07, 'teak', bevel=0.005, tint_c=(1.05, 1.0, 0.95), name='shutter')
            for y in (y0 + 0.3, y1 - 0.3):
                box(min(x0_, x0_ + s_ * hw) + 0.05, max(x0_, x0_ + s_ * hw) - 0.05, y - 0.2, y + 0.2, z + o[1] * 0.07, z + o[1] * 0.085, 'teak', bevel=0.0, tint_c=(0.78, 0.75, 0.72), name='shutter-panel')
    else:
        x = cx + o[0] * 0.06
        box(x - 0.02, x + 0.02, y0, y1, cz - hw, cz + hw, 'char', bevel=0.0, name='win-dark')
        box(x - 0.04, x + 0.04, y0 - 0.06, y0, cz - hw - 0.07, cz + hw + 0.07, 'teak', bevel=0.01, tint_c=(0.7, 0.7, 0.7), name='win-sill')
        box(x - 0.05, x + 0.05, y1, y1 + 0.1, cz - hw - 0.1, cz + hw + 0.1, 'teak', bevel=0.01, tint_c=(0.7, 0.7, 0.7), name='win-head')
        box(min(x, x + o[0] * 0.025), max(x, x + o[0] * 0.025), F + 0.08, y0 - 0.06, cz - hw, cz + hw, 'teak', bevel=0.0, tint_c=(1.15, 1.1, 1.0), name='win-apron')
        for s_ in (-1, 1):
            z0_ = cz + s_ * hw
            box(min(x + o[0] * 0.03, x + o[0] * 0.07), max(x + o[0] * 0.03, x + o[0] * 0.07), y0, y1, min(z0_, z0_ + s_ * hw), max(z0_, z0_ + s_ * hw), 'teak', bevel=0.005, tint_c=(1.05, 1.0, 0.95), name='shutter')
            for y in (y0 + 0.3, y1 - 0.3):
                box(min(x + o[0] * 0.07, x + o[0] * 0.085), max(x + o[0] * 0.07, x + o[0] * 0.085), y - 0.2, y + 0.2, min(z0_, z0_ + s_ * hw) + 0.05, max(z0_, z0_ + s_ * hw) - 0.05, 'teak', bevel=0.0, tint_c=(0.78, 0.75, 0.72), name='shutter-panel')


for (x0_, x1_) in ((MX0, MX1), (KX0, KX1)):
    panel_wall((x0_, SZ), (x1_, SZ), F, WT, 's')
    panel_wall((x0_, NZ), (x1_, NZ), F, WT, 'n')
    panel_wall((x0_, NZ), (x0_, SZ), F, WT, 'w')
    panel_wall((x1_, NZ), (x1_, SZ), F, WT, 'e')
    box(x0_ - 0.1, x1_ + 0.1, WT - 0.12, WT + 0.02, NZ - 0.1, SZ + 0.1, 'teak', bevel=0.01, tint_c=(0.65, 0.62, 0.6), name='wall-plate')
window(0.85, SZ, 's')
window(4.15, SZ, 's')
window(2.5, SZ, 's', 0.6, F + 0.75, F + 1.55)  # a small centre window between them
window(MX1, -6.0, 'e')
window(MX1, -4.1, 'e')
window(1.3, NZ, 'n')
window(3.8, NZ, 'n')
window(-3.45, SZ, 's', 0.9)
window(KX0, -5.0, 'w')
# doors from the chan into each pavilion, a step up, with carved lintels
for (x, face) in ((MX0, 'w'), (KX1, 'e')):
    o = -1 if face == 'w' else 1
    xx = x + o * 0.06
    box(xx - 0.02, xx + 0.02, F, F + 1.85, -5.4, -4.5, 'char', bevel=0.0, name='door-dark')
    box(xx - 0.05, xx + 0.05, F + 1.85, F + 2.0, -5.5, -4.4, 'teak', bevel=0.01, tint_c=(0.65, 0.62, 0.6), name='door-head')
    box(min(xx, xx + o * 0.04), max(xx, xx + o * 0.04), F, F + 1.85, -4.5, -4.05, 'teak', bevel=0.005, tint_c=(1.05, 1.0, 0.95), name='door-leaf')
    box(min(xx, xx + o * 0.04), max(xx, xx + o * 0.04), F, F + 1.85, -5.85, -5.4, 'teak', bevel=0.005, tint_c=(1.05, 1.0, 0.95), name='door-leaf')
    box(x + o * 0.05 - 0.15, x + o * 0.05 + 0.15, FT, F, -5.45, -4.45, 'teak', bevel=0.01, tint_c=(0.85, 0.85, 0.85), name='door-step')

# ================================================================ the roofs
def thai_roof(x0, x1, ry, kick_w=True, kick_e=True, z0=NZ - 0.45, z1=SZ + 0.1):
    """A steep gable along z with a kicked lower eave, tiles over teak boarding, bargeboards with
    hooked ends and crossed kalae tips, a sunburst gable at the courtyard end."""
    xm = (x0 + x1) / 2
    EK = WT + 0.25  # knee: steep upper slope meets the shallower lower eave
    EY = WT - 0.12
    xa0, xa1 = x0 - 0.35, x1 + 0.35
    xb0 = x0 - 0.95 if kick_w else xa0
    xb1 = x1 + 0.95 if kick_e else xa1
    T = 0.1
    # tiles
    for (xa, xb, kick) in ((xa0, xb0, kick_w), (xa1, xb1, kick_e)):
        slab([(xm, ry, z1), (xa, EK, z1), (xa, EK, z0), (xm, ry, z0)], T, 'thtile', name='roof-tile')
        slab([(xm, ry - 0.04, z1), (xa, EK - 0.04, z1), (xa, EK - 0.04, z0), (xm, ry - 0.04, z0)], 0.04, 'teak', tint_c=(0.7, 0.68, 0.66), name='roof-board')
        if kick:
            slab([(xa, EK, z1), (xb, EY, z1), (xb, EY, z0), (xa, EK, z0)], T, 'thtile', name='roof-tile')
            slab([(xa, EK - 0.04, z1), (xb, EY - 0.04, z1), (xb, EY - 0.04, z0), (xa, EK - 0.04, z0)], 0.04, 'teak', tint_c=(0.7, 0.68, 0.66), name='roof-board')
        # tile courses: thin raised ribs across the slope
        for k in range(1, 9):
            p = lerp((xm, ry), (xa, EK), k / 9)
            box(p[0] - 0.03, p[0] + 0.03, p[1] + T - 0.01, p[1] + T + 0.035, z0, z1, 'thtile', bevel=0.0, tint_c=(0.78, 0.74, 0.72), name='tile-course')
        if kick:
            for k in range(1, 3):
                p = lerp((xa, EK), (xb, EY), k / 3)
                box(p[0] - 0.03, p[0] + 0.03, p[1] + T - 0.01, p[1] + T + 0.03, z0, z1, 'thtile', bevel=0.0, tint_c=(0.78, 0.74, 0.72), name='tile-course')
        # the eave edge board
        xe, ye = (xb, EY) if kick else (xa, EK)
        box(xe - 0.04, xe + 0.04, ye - 0.12, ye + T, z0, z1, 'teak', bevel=0.005, tint_c=(0.62, 0.6, 0.58), name='eave-board')
    box(xm - 0.13, xm + 0.13, ry + T - 0.05, ry + T + 0.1, z0 - 0.02, z1 + 0.02, 'thtile', bevel=0.03, tint_c=(0.7, 0.62, 0.6), name='ridge')
    # gables: a teak pediment on each end, a sunburst on the courtyard end
    def roof_y(x):
        if x <= xm:
            return EK + (ry - EK) * (x - xa0) / (xm - xa0)
        return EK + (ry - EK) * (xa1 - x) / (xa1 - xm)
    for (z, sun) in ((SZ, True), (NZ, False)):
        zz = z + (0.02 if sun else -0.02)
        ring = [(x0, WT, zz), (x1, WT, zz), (x1, roof_y(x1) - 0.06, zz), (xm, ry - 0.08, zz), (x0, roof_y(x0) - 0.06, zz)]
        solid([ring, [(p[0], p[1], p[2] + (-0.08 if sun else 0.08)) for p in ring]], 'teak', tint_c=(0.95, 0.92, 0.9), name='pediment')
        out = 1 if sun else -1
        box(x0, x1, WT, WT + 0.12, zz + out * 0.0, zz + out * 0.04, 'teak', bevel=0.005, tint_c=(0.62, 0.6, 0.58), name='pediment-sill')
        if sun:
            cx_, cy_ = xm, WT + 0.12
            for k in range(13):
                th = math.radians(12 + k * (156 / 12))
                d = (math.cos(th), math.sin(th))
                # distance from the hub to the roof line along d
                lo, hi = 0.0, 6.0
                for _ in range(30):
                    m = (lo + hi) / 2
                    x, y = cx_ + d[0] * m, cy_ + d[1] * m
                    if x0 < x < x1 and y < roof_y(x) - 0.12:
                        lo = m
                    else:
                        hi = m
                L = lo
                if L < 0.25:
                    continue
                plank((cx_ + d[0] * 0.18, cy_ + d[1] * 0.18, zz + 0.025), (cx_ + d[0] * L, cy_ + d[1] * L, zz + 0.025), 0.06, 0.03, 'teak', tint_c=(0.68, 0.65, 0.62), name='sunray')
            solid([[(cx_ + math.cos(math.radians(a)) * 0.2, cy_ + math.sin(math.radians(a)) * 0.2, zz + 0.01) for a in range(0, 181, 20)], [(cx_ + math.cos(math.radians(a)) * 0.2, cy_ + math.sin(math.radians(a)) * 0.2, zz + 0.06) for a in range(0, 181, 20)]], 'gold', name='sun-hub')
    # pan lom bargeboards along both gable ends, hooked at the eaves, crossed above the ridge (kalae)
    for z in (z1 + 0.035, z0 - 0.035):
        for (xa, xb, kick, sgn) in ((xa0, xb0, kick_w, -1), (xa1, xb1, kick_e, 1)):
            lift = 0.1
            plank((xm, ry + lift, z), (xa, EK + lift, z), 0.2, 0.06, 'teak', tint_c=(0.62, 0.58, 0.55), name='pan-lom')
            end = (xa, EK + lift)
            if kick:
                plank((xa, EK + lift, z), (xb, EY + lift, z), 0.2, 0.06, 'teak', tint_c=(0.62, 0.58, 0.55), name='pan-lom')
                end = (xb, EY + lift)
            # ngao: an upturned hook at the eave end
            plank((end[0], end[1] - 0.05, z), (end[0] + sgn * 0.16, end[1] + 0.32, z), 0.12, 0.06, 'gold', name='ngao')
            # kalae: the board carried on past the ridge, then tipped up
            d = ((xm - xa), (ry - EK))
            Ld = math.hypot(*d)
            d = (d[0] / Ld, d[1] / Ld)
            tip = (xm + d[0] * 0.55, ry + lift + d[1] * 0.55)
            plank((xm - d[0] * 0.08, ry + lift - d[1] * 0.08, z), (tip[0], tip[1], z), 0.16, 0.06, 'teak', tint_c=(0.62, 0.58, 0.55), name='kalae')
            plank((tip[0], tip[1], z), (tip[0] - sgn * 0.12, tip[1] + 0.32, z), 0.1, 0.06, 'gold', name='kalae-tip')


thai_roof(MX0, MX1, 7.7, kick_w=False, kick_e=True)
thai_roof(KX0, KX1, 6.5, kick_w=True, kick_e=False)
# hanging orchids under the main east eave and the kitchen west eave
for (x, z) in ((MX1 + 0.55, -6.3), (MX1 + 0.55, -4.8), (MX1 + 0.55, -3.4), (KX0 - 0.55, -6.0), (KX0 - 0.55, -3.6)):
    pole((x, WT, z), (x, 3.0, z), 0.005, 'char', seg=4, name='orchid-wire')
    box(x - 0.13, x + 0.13, 2.86, 3.0, z - 0.13, z + 0.13, 'teak', bevel=0.02, tint_c=(0.8, 0.8, 0.8), name='orchid-basket')
    for k in range(5):
        a = k / 5 * 360
        obox((x, 3.02, z), (0.32, 0.02, 0.09), (0, a, -20), 'leaf', tint_c=(0.9, 1.1, 0.8), name='orchid-leaf', taper=0.5)
    for k in range(6):
        ang = rnd.uniform(0, math.tau)
        blob(x + math.cos(ang) * 0.16, 2.95 - k * 0.07, z + math.sin(ang) * 0.16, 0.04, 'lotus', (0.85, 0.6, 1.25), squash=0.6, seed=k + int(z * 7), name='orchid-flower')
# potted jasmine and a bonsai on the chan
for (x, z) in ((-1.9, -6.6), (-0.3, -6.6), (-1.85, -5.3)):
    pole((x, FT, z), (x, FT + 0.3, z), 0.13, 'celadon', seg=12, r2=0.17, name='pot')
    blob(x, FT + 0.48, z, 0.22, 'leaf', jitter((0.95, 1.05, 0.9), 0.08), seed=int(x * 9 - z), name='jasmine')
    for k in range(5):
        a = rnd.uniform(0, math.tau)
        blob(x + math.cos(a) * 0.17, FT + rnd.uniform(0.45, 0.62), z + math.sin(a) * 0.17, 0.03, 'frangi', (1, 1, 1), squash=0.7, seed=k, name='jasmine-flower')
# the tree through the chan: a trunk rising through a hole in the deck, crown above the roofs
TX, TZ = -1.05, -6.0
pole((TX, 0.0, TZ), (TX, 3.6, TZ), 0.16, 'trunk', seg=10, r2=0.11, tint_c=(0.75, 0.68, 0.6), name='chan-tree')
for (dx, dz, y, r) in ((0.0, 0.0, 4.9, 1.0), (0.6, 0.4, 4.4, 0.7), (-0.6, -0.3, 4.6, 0.75), (0.2, -0.6, 5.4, 0.7), (-0.3, 0.5, 5.3, 0.65)):
    blob(TX + dx, y, TZ + dz, r, 'leaf', jitter((0.92, 1.05, 0.88), 0.08), squash=0.75, seed=int(y * 13 + dx * 7) + 50, name='chan-crown')
pole((TX, 3.4, TZ), (TX + 0.6, 4.3, TZ + 0.4), 0.06, 'trunk', seg=6, tint_c=(0.75, 0.68, 0.6), name='chan-branch')
pole((TX, 3.3, TZ), (TX - 0.6, 4.4, TZ - 0.3), 0.06, 'trunk', seg=6, tint_c=(0.75, 0.68, 0.6), name='chan-branch')

# ================================================================ whitewashed garden wall, 0.9 m, terracotta coping
for key in ('east garden wall', 'south garden wall', 'west garden wall'):
    b = BOX[key]
    x0, x1 = b['c'][0] - b['h'][0], b['c'][0] + b['h'][0]
    z0, z1 = b['c'][2] - b['h'][2], b['c'][2] + b['h'][2]
    along_x = (x1 - x0) > (z1 - z0)
    gate = key == 'south garden wall'
    spans = [(x0, 0.0), (1.2, x1)] if gate else [((x0, x1) if along_x else (z0, z1))]
    for (u0, u1) in spans:
        if along_x:
            box(u0, u1, 0.0, GW - 0.08, z0, z1, 'lime', bevel=0.0, name='gwall')
            box(u0 - 0.04, u1 + 0.04, GW - 0.08, GW, z0 - 0.05, z1 + 0.05, 'terracotta', bevel=0.015, name='gwall-coping')
            box(u0, u1, 0.0, 0.12, z0 - 0.02, z1 + 0.02, 'laterite', bevel=0.0, name='gwall-plinth')
        else:
            box(x0, x1, 0.0, GW - 0.08, u0, u1, 'lime', bevel=0.0, name='gwall')
            box(x0 - 0.05, x1 + 0.05, GW - 0.08, GW, u0 - 0.04, u1 + 0.04, 'terracotta', bevel=0.015, name='gwall-coping')
            box(x0 - 0.02, x1 + 0.02, 0.0, 0.12, u0, u1, 'laterite', bevel=0.0, name='gwall-plinth')
    L0, L1 = (x0, x1) if along_x else (z0, z1)
    t = L0
    while t <= L1 + 0.01:
        if along_x:
            box(t - 0.13, t + 0.13, 0.0, GW + 0.1, z0 - 0.04, z1 + 0.04, 'lime', bevel=0.01, name='gpier')
            pole((t, GW + 0.1, (z0 + z1) / 2), (t, GW + 0.24, (z0 + z1) / 2), 0.14, 'terracotta', seg=4, r2=0.02, name='gpier-cap')
        else:
            box(x0 - 0.04, x1 + 0.04, 0.0, GW + 0.1, t - 0.13, t + 0.13, 'lime', bevel=0.01, name='gpier')
            pole(((x0 + x1) / 2, GW + 0.1, t), ((x0 + x1) / 2, GW + 0.24, t), 0.14, 'terracotta', seg=4, r2=0.02, name='gpier-cap')
        t += 2.5
# the canal gate: two teak leaves (closed, the wall's height) between brick piers
b = BOX['south garden wall']
gz0, gz1 = b['c'][2] - b['h'][2], b['c'][2] + b['h'][2]
for x in (0.0, 1.2):
    box(x - 0.14, x + 0.14, 0.0, GW + 0.2, gz0 - 0.05, gz1 + 0.05, 'lime', bevel=0.01, name='gate-pier')
    pole((x, GW + 0.2, (gz0 + gz1) / 2), (x, GW + 0.36, (gz0 + gz1) / 2), 0.15, 'terracotta', seg=4, r2=0.02, name='gpier-cap')
for (a, b_) in ((0.14, 0.59), (0.61, 1.06)):
    box(a, b_, 0.05, GW - 0.05, gz0 + 0.06, gz1 - 0.06, 'teak', bevel=0.01, name='gate-leaf')
    x = a + 0.06
    while x < b_ - 0.03:
        box(x - 0.02, x + 0.02, 0.1, GW - 0.1, gz1 - 0.06, gz1 - 0.03, 'teak', bevel=0.0, tint_c=(0.7, 0.7, 0.7), name='gate-board')
        x += 0.09

# ================================================================ outside: canal walk, tha nam, spirit house, plumerias, pole
EDGE = 5.4  # the island's straight canal front (art/blender/island2.py, country th)
box(-5.2, 5.2, 0.0, 0.03, gz1, EDGE - 0.4, 'brick', bevel=0.0, name='canal-walk')
for x in (-5.3, 5.2):
    box(x, x + 0.1, 0.0, 0.06, gz1, EDGE - 0.4, 'laterite', bevel=0.01, name='canal-walk-edge')
# the water landing: three steps down to a teak deck on posts, two mooring posts, a lantern post
PX0_, PX1_ = -0.1, 1.3
for k, (y, z0_, z1_) in enumerate(((-0.15, EDGE + 0.06, EDGE + 0.36), (-0.32, EDGE + 0.36, EDGE + 0.66))):
    box(PX0_, PX1_, y - 0.06, y, z0_, z1_, 'teak', bevel=0.01, tint_c=(0.9, 0.88, 0.85), name='pier-step')
box(PX0_ - 0.1, PX1_ + 0.1, -0.56, -0.5, EDGE + 0.66, 6.6, 'teak', bevel=0.01, tint_c=(0.85, 0.82, 0.78), name='pier-deck')
x = PX0_ - 0.05
while x < PX1_ + 0.1:
    box(x, x + 0.01, -0.5, -0.497, EDGE + 0.66, 6.6, 'char', bevel=0.0, name='pier-joint')
    x += 0.14
for x in (PX0_ - 0.05, PX1_ + 0.05):
    for z in (EDGE + 0.7, 6.55):
        pole((x, -1.6, z), (x, -0.5, z), 0.07, 'teak', seg=8, tint_c=(0.6, 0.55, 0.5), name='pier-pile')
    pole((x, -0.5, 6.55), (x, 0.5, 6.55), 0.07, 'teak', seg=8, tint_c=(0.75, 0.7, 0.65), name='mooring-post')
    pole((x, 0.5, 6.55), (x, 0.6, 6.55), 0.075, 'gold', seg=8, r2=0.02, name='mooring-cap')
# the rua: a slim teak rowing boat tied alongside, an oar and a woven hat on the thwart
def rua(x0, z0, L=2.6):
    rings = []
    for i in range(11):
        t = i / 10
        u = 2 * t - 1
        w = 0.3 * (1 - u ** 4) ** 0.7 + 0.015
        lift = 0.12 * u ** 6
        xs = x0 + L * t
        y0 = -0.92
        rings.append([(xs, y0 + 0.28 + lift, z0 - w), (xs, y0 + 0.05 + lift * 0.5, z0 - w * 0.6), (xs, y0 + lift * 0.4, z0), (xs, y0 + 0.05 + lift * 0.5, z0 + w * 0.6), (xs, y0 + 0.28 + lift, z0 + w)])
    me = bpy.data.meshes.new('rua')
    bm = bmesh.new()
    vs = [[bm.verts.new(P(*p)) for p in r] for r in rings]
    for a, c in zip(vs, vs[1:]):
        for k in range(4):
            bm.faces.new((a[k], a[k + 1], c[k + 1], c[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    _finish(bpy.data.objects.new('rua', me), me, 'teak', (0.75, 0.7, 0.65))
    for t in (0.35, 0.65):
        xs = x0 + L * t
        box(xs - 0.06, xs + 0.06, -0.7, -0.66, z0 - 0.26, z0 + 0.26, 'teak', bevel=0.005, name='rua-thwart')
    pole((x0 + L * 0.65, -0.62, z0), (x0 + L * 0.65, -0.6, z0), 0.24, 'sawali', seg=14, r2=0.03, name='ngob-hat')
    pole((x0 + L * 0.65, -0.6, z0), (x0 + L * 0.65, -0.52, z0), 0.03, 'sawali', seg=8, r2=0.0, name='ngob-hat')
    plank((x0 + 0.4, -0.64, z0 + 0.15), (x0 + 1.9, -0.66, z0 + 0.2), 0.04, 0.03, 'teak', name='oar')


rua(PX1_ + 0.25, 6.15)
# the spirit house (san phra phum) on its pillar outside the east wall, facing west, with offerings
SX, SZ_ = 6.25, -2.35
box(SX - 0.32, SX + 0.32, 0.0, 0.12, SZ_ - 0.32, SZ_ + 0.32, 'lime', bevel=0.02, name='sp-base')
pole((SX, 0.12, SZ_), (SX, 1.25, SZ_), 0.1, 'lime', seg=10, r2=0.085, name='sp-pillar')
box(SX - 0.36, SX + 0.36, 1.25, 1.32, SZ_ - 0.36, SZ_ + 0.36, 'lacquer', bevel=0.01, name='sp-platform')
box(SX - 0.4, SX + 0.4, 1.32, 1.35, SZ_ - 0.4, SZ_ + 0.4, 'gold', bevel=0.005, name='sp-platform-trim')
box(SX - 0.2, SX + 0.2, 1.35, 1.75, SZ_ - 0.18, SZ_ + 0.18, 'lime', bevel=0.01, name='sp-body')
for (dz) in (-0.18, 0.18):
    for dx in (-0.2, 0.2):
        box(SX + dx - 0.025, SX + dx + 0.025, 1.35, 1.75, SZ_ + dz - 0.025, SZ_ + dz + 0.025, 'gold', bevel=0.0, name='sp-column')
box(SX - 0.21, SX - 0.205, 1.4, 1.65, SZ_ - 0.07, SZ_ + 0.07, 'char', bevel=0.0, name='sp-door')
def mini_gable(xa, xb, half, y0, h, mat):
    """A steep little gable roof, ridge along x, gable ends facing west and east."""
    tri = lambda x: [(x, y0, SZ_ - half), (x, y0, SZ_ + half), (x, y0 + h, SZ_)]
    solid([tri(xa), tri(xb)], mat, name='sp-roof')
    return tri(xa)


for (xa, xb, half, y0_, h, m) in ((SX - 0.3, SX + 0.3, 0.3, 1.75, 0.3, 'lacquer'), (SX - 0.22, SX + 0.22, 0.2, 1.93, 0.3, 'enamel')):
    mini_gable(xa, xb, half, y0_, h, m)
    for xe in (xa - 0.012, xb + 0.012):
        for z_s in (-1, 1):
            a_ = (xe, y0_ + h + 0.015, SZ_)
            b_ = (xe, y0_ - 0.01, SZ_ + z_s * (half + 0.02))
            pole(a_, b_, 0.016, 'gold', seg=4, name='sp-board')
            pole(b_, (xe, y0_ + 0.1, SZ_ + z_s * (half + 0.09)), 0.012, 'gold', seg=4, name='sp-hook')
        pole((xe, y0_ + h, SZ_), (xe, y0_ + h + 0.13, SZ_), 0.014, 'gold', seg=4, r2=0.003, name='sp-chofa')
pole((SX, 2.23, SZ_), (SX, 2.5, SZ_), 0.025, 'gold', seg=8, r2=0.004, name='sp-spire')
for k in range(8):  # marigold garland round the pillar and offerings on the platform
    a = k / 8 * math.tau
    blob(SX + math.cos(a) * 0.12, 1.12 - abs(math.sin(a)) * 0.08, SZ_ + math.sin(a) * 0.12, 0.035, 'marigold', (1, 1, 1), squash=0.9, seed=k, name='malai')
for (dx, dz) in ((-0.28, -0.12), (-0.28, 0.0), (-0.28, 0.12)):
    pole((SX + dx, 1.35, SZ_ + dz), (SX + dx, 1.47, SZ_ + dz), 0.022, 'red', seg=8, name='offering-bottle')
pole((SX - 0.28, 1.35, SZ_ + 0.26), (SX - 0.28, 1.38, SZ_ + 0.26), 0.06, 'celadon', seg=10, name='offering-dish')
for (dx, dz) in ((-0.33, -0.25), (-0.33, 0.25)):
    blob(SX + dx, 1.4, SZ_ + dz, 0.05, 'cloth', (0.95, 0.35, 0.7), squash=0.8, seed=int(dz * 10) + 9, name='garland')
# plumeria (lantom) trees outside the west wall, white and yellow flowers at the branch tips
def plumeria(x, z, h=2.6, seed=0):
    k = random.Random(seed)
    pole((x, 0.0, z), (x, h * 0.5, z), 0.1, 'trunk', seg=8, r2=0.08, tint_c=(0.85, 0.82, 0.78), name='pl-trunk')
    for i in range(5):
        a = i / 5 * math.tau + k.uniform(-0.3, 0.3)
        r = k.uniform(0.6, 0.95)
        tip = (x + math.cos(a) * r, h + k.uniform(-0.2, 0.25), z + math.sin(a) * r)
        pole((x, h * 0.5, z), tip, 0.06, 'trunk', seg=6, r2=0.045, tint_c=(0.85, 0.82, 0.78), name='pl-branch')
        blob(tip[0], tip[1] + 0.08, tip[2], 0.42, 'leaf', jitter((0.95, 1.08, 0.88), 0.08), squash=0.55, seed=seed * 20 + i, name='pl-crown')
        for j in range(4):
            fx, fz = tip[0] + k.uniform(-0.1, 0.1), tip[2] + k.uniform(-0.1, 0.1)
            blob(fx, tip[1] + 0.27 + k.uniform(0, 0.04), fz, 0.07, 'frangi', (1.0, 1.0, 0.75) if j % 2 else (1, 1, 1), squash=0.5, seed=seed * 50 + i * 5 + j, name='pl-flower')


plumeria(-6.4, -3.4, seed=3)
plumeria(-6.7, -1.0, 2.3, seed=4)
for (x, z, s) in ((-3.0, -8.0, 21), (2.6, -8.1, 22), (4.4, -7.9, 23)):
    banana(x, z, 2.4, seed=s)
# a concrete power pole outside the north-east corner, wires running north and east (never over the yard)
PPX, PPZ = 7.0, -3.9
box(PPX - 0.25, PPX + 0.25, 0.0, 0.1, PPZ - 0.25, PPZ + 0.25, 'concrete', bevel=0.02, name='pp-foot')
pole((PPX, 0.1, PPZ), (PPX, 6.6, PPZ), 0.12, 'concrete', seg=8, r2=0.08, name='pp')
for (y, L) in ((6.1, 1.0), (5.5, 0.8)):
    box(PPX - L / 2, PPX + L / 2, y - 0.05, y + 0.05, PPZ - 0.05, PPZ + 0.05, 'steel', bevel=0.0, name='pp-arm')
pole((PPX + 0.15, 4.9, PPZ - 0.15), (PPX + 0.15, 5.25, PPZ - 0.15), 0.18, 'steel', seg=10, tint_c=(2.2, 2.2, 2.2), name='pp-transformer')
nh = BOX['neighbour house']
nx0, nx1 = nh['c'][0] - nh['h'][0], nh['c'][0] + nh['h'][0]
nz0, nz1 = nh['c'][2] - nh['h'][2], nh['c'][2] + nh['h'][2]
ny1 = nh['c'][1] + nh['h'][1]


def wire(a, b, sag=0.35, r=0.012):
    pts = []
    for k in range(9):
        t = k / 8
        p = lerp(a, b, t)
        pts.append((p[0], p[1] - sag * math.sin(math.pi * t), p[2]))
    for p, q in zip(pts, pts[1:]):
        pole(p, q, r, 'wire', seg=4, name='wire')


for (dx, y) in ((-0.45, 6.1), (-0.15, 6.1), (0.15, 6.1), (0.45, 6.1), (-0.35, 5.5), (0.35, 5.5)):
    wire((PPX + dx, y, PPZ), (PPX + dx * 0.8, y - 0.2, -9.4), 0.4 + abs(dx) * 0.3)
for (dy, s) in ((0.0, 0.3), (-0.12, 0.42), (-0.2, 0.5)):
    wire((PPX + 0.4, 5.5 + dy, PPZ), (nx0 + 0.6, ny1 - 0.25 + dy, nz0 + 0.3), s, 0.01)
for k in range(5):  # a coil of spare cable and a tangle low on the pole
    a0 = k / 5 * math.tau
    pole((PPX + math.cos(a0) * 0.16, 3.6 + k * 0.03, PPZ + math.sin(a0) * 0.16), (PPX + math.cos(a0 + 1.26) * 0.16, 3.6 + k * 0.03, PPZ + math.sin(a0 + 1.26) * 0.16), 0.015, 'wire', seg=4, name='cable-coil')

# ================================================================ neighbour: a Bangkok shophouse (tuek thaew)
GF = 2.4
box(nx0, nx1, 0.0, GF, nz0, nz1 - 0.6, 'cream', bevel=0.03, name='th-ground')
box(nx0, nx1, GF, 4.15, nz0, nz1, 'mint', bevel=0.03, name='th-upper')
box(nx0 - 0.05, nx1 + 0.05, GF - 0.12, GF + 0.04, nz0 - 0.05, nz1 + 0.05, 'cream', bevel=0.01, tint_c=(0.85, 0.85, 0.85), name='th-floor-band')
box(nx0 - 0.04, nx1 + 0.04, 4.15, 4.5, nz0 - 0.04, nz1 + 0.04, 'cream', bevel=0.02, name='th-parapet')
box(nx0 + 0.08, nx1 - 0.08, 4.38, 4.42, nz0 + 0.08, nz1 - 0.08, 'concrete', bevel=0.0, name='th-roof')
pole((nx1 - 0.7, 4.4, nz0 + 0.8), (nx1 - 0.7, 4.6, nz0 + 0.8), 0.35, 'tank', seg=16, tint_c=(1.6, 1.6, 1.6), name='th-tank')
for x in (nx0 + 0.05, (nx0 + nx1) / 2, nx1 - 0.05):  # party-wall piers on the street front
    box(x - 0.12, x + 0.12, 0.0, 4.15, nz1 - 0.6, nz1 + 0.04, 'cream', bevel=0.02, name='th-pier')
# ground floor: two bays with folding steel shutters, one half open onto a dark shop
for (xa_, xb_, open_) in ((nx0 + 0.17, (nx0 + nx1) / 2 - 0.12, True), ((nx0 + nx1) / 2 + 0.12, nx1 - 0.17, False)):
    box(xa_, xb_, 0.0, 2.15, nz1 - 0.66, nz1 - 0.6, 'char', bevel=0.0, name='th-shop-dark')
    top = 2.15
    bot = 1.1 if open_ else 0.0
    x = xa_
    while x < xb_ - 0.01:
        box(x, x + 0.05, bot, top, nz1 - 0.58, nz1 - 0.54, 'steel', bevel=0.0, tint_c=(1.8, 1.8, 1.9), name='th-shutter-slat')
        x += 0.09
    for y in (bot + 0.02, top - 0.05):
        box(xa_, xb_, y, y + 0.04, nz1 - 0.6, nz1 - 0.52, 'steel', bevel=0.0, name='th-shutter-rail')
    if open_:
        for k in range(3):  # a shelf of goods glimpsed under the shutter
            y = 0.2 + k * 0.32
            box(xa_ + 0.1, xb_ - 0.1, y, y + 0.03, nz1 - 1.1, nz1 - 0.8, 'timber', bevel=0.0, name='th-shelf')
            for j in range(6):
                xx = xa_ + 0.2 + j * (xb_ - xa_ - 0.4) / 5
                box(xx - 0.07, xx + 0.07, y + 0.03, y + 0.03 + rnd.uniform(0.12, 0.22), nz1 - 1.0, nz1 - 0.86, 'cloth', bevel=0.01, tint_c=rnd.choice([(0.9, 0.3, 0.25), (0.2, 0.5, 0.8), (0.95, 0.8, 0.2), (0.3, 0.7, 0.4)]), name='th-goods')
box(nx0 + 0.1, nx1 - 0.1, 2.15, 2.38, nz1 - 0.02, nz1 + 0.04, 'sign', bevel=0.01, name='th-signboard')
box(nx0 + 0.1, nx1 - 0.1, 2.15, 2.2, nz1 + 0.04, nz1 + 0.05, 'red', bevel=0.0, name='th-sign-band')
for k in range(10):  # lettering suggested by blocks, no words
    x = nx0 + 0.4 + k * 0.33
    box(x, x + 0.2, 2.23, 2.33, nz1 + 0.04, nz1 + 0.05, 'red', bevel=0.0, name='th-sign-letter')
# a canvas awning over the open bay
obox((nx0 + 1.1, 2.05, nz1 + 0.4), (1.9, 0.03, 0.85), (22, 0, 0), 'awning', name='th-awning')
# upper floor: aluminium windows with sun hoods, a balcony with a steel grille and pots
for xc in (nx0 + 1.05, nx1 - 1.05):
    box(xc - 0.75, xc + 0.75, GF + 0.55, 3.75, nz1 - 0.02, nz1 + 0.02, 'glass', bevel=0.0, name='th-win')
    for k in range(4):
        xx = xc - 0.75 + k * 0.5
        box(xx - 0.025, xx + 0.025, GF + 0.55, 3.75, nz1 + 0.02, nz1 + 0.05, 'steel', bevel=0.0, tint_c=(2.2, 2.2, 2.3), name='th-mullion')
    obox((xc, 3.9, nz1 + 0.3), (1.7, 0.05, 0.62), (28, 0, 0), 'concrete', name='th-hood')
box(nx0 + 0.15, nx1 - 0.15, GF, GF + 0.08, nz1, nz1 + 0.5, 'cream', bevel=0.01, name='th-balcony')
x = nx0 + 0.2
while x < nx1 - 0.15:
    pole((x, GF + 0.08, nz1 + 0.47), (x, GF + 0.95, nz1 + 0.47), 0.012, 'steel', seg=4, name='th-grille')
    x += 0.12
pole((nx0 + 0.15, GF + 0.95, nz1 + 0.47), (nx1 - 0.15, GF + 0.95, nz1 + 0.47), 0.022, 'steel', seg=6, name='th-grille-top')
for xx in (nx0 + 0.6, nx0 + 1.6, nx1 - 0.9):
    pole((xx, GF + 0.08, nz1 + 0.25), (xx, GF + 0.32, nz1 + 0.25), 0.13, 'clay', seg=10, r2=0.1, name='th-pot')
    blob(xx, GF + 0.5, nz1 + 0.25, 0.22, 'leaf', jitter((1, 1, 1), 0.1), seed=int(xx * 10), name='th-pot-plant')
# west face (toward the garden): the watching window behind a burglar grille, an air conditioner below
wy, wz = N['window'][1], N['window'][2]
BY = wy - 1.62 + 0.06  # balcony floor: the neighbour figure stands here (src/index.ts)
box(nx0 - 0.04, nx0 + 0.02, BY, wy + 0.55, wz - 0.6, wz + 0.6, 'char', bevel=0.0, name='th-wwin')
box(nx0 - 0.85, nx0, BY - 0.12, BY, wz - 1.05, wz + 1.05, 'cream', bevel=0.02, name='th-wbalcony')
for k in range(15):
    zz = wz - 1.0 + k * (2.0 / 14)
    pole((nx0 - 0.8, BY, zz), (nx0 - 0.8, BY + 0.92, zz), 0.012, 'steel', seg=4, name='th-wbal-grille')
for zz in (wz - 1.0, wz + 1.0):
    for k in range(5):
        xx = nx0 - 0.8 + k * 0.18
        pole((xx, BY, zz), (xx, BY + 0.92, zz), 0.012, 'steel', seg=4, name='th-wbal-grille')
pole((nx0 - 0.8, BY + 0.92, wz - 1.0), (nx0 - 0.8, BY + 0.92, wz + 1.0), 0.022, 'steel', seg=6, name='th-wbal-top')
for zz in (wz - 0.85, wz + 0.85):
    pole((nx0 - 0.55, BY, zz), (nx0 - 0.55, BY + 0.24, zz), 0.12, 'clay', seg=10, r2=0.09, name='th-pot')
    blob(nx0 - 0.55, BY + 0.42, zz, 0.2, 'leaf', jitter((1, 1, 1), 0.1), seed=int(zz * 10) + 3, name='th-pot-plant')
for k in range(9):
    zz = wz - 0.6 + k * 0.15
    pole((nx0 - 0.12, BY, zz), (nx0 - 0.12, wy + 0.6, zz), 0.01, 'steel', seg=4, name='th-burglar')
for y in (BY + 0.05, wy - 0.6, wy, wy + 0.6):
    pole((nx0 - 0.12, y, wz - 0.65), (nx0 - 0.12, y, wz + 0.65), 0.014, 'steel', seg=4, name='th-burglar')
for zz in (wz - 0.65, wz + 0.65):
    for y in (BY + 0.05, wy + 0.6):
        pole((nx0, y, zz), (nx0 - 0.12, y, zz), 0.014, 'steel', seg=4, name='th-burglar')
box(nx0 - 0.3, nx0, 1.4, 1.95, -2.9, -2.0, 'trim', bevel=0.03, name='th-aircon')
for k in range(6):
    zz = -2.85 + k * 0.15
    box(nx0 - 0.31, nx0 - 0.3, 1.45, 1.9, zz, zz + 0.08, 'char', bevel=0.0, name='th-aircon-grille')
pole((nx0 - 0.15, 1.95, -2.4), (nx0 - 0.15, 3.0, -2.4), 0.02, 'trim', seg=6, name='th-aircon-pipe')
box(nx0 - 0.05, nx0, 0.0, 0.25, nz0, nz1 - 0.6, 'cream', bevel=0.0, tint_c=(0.75, 0.75, 0.72), name='th-plinth')
