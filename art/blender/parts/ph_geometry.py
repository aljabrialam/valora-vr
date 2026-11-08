# ================================================================ PHILIPPINES v3: bahay kubo and bakuran
# (helpers and materials: parts/common.py)
R = LAY['room']
C = LAY['court']
N = LAY['neighbour']
sx, _, sz = LAY['seat']

# ================================================================ the bakuran (yard)
pool = {'x0': -4.3, 'x1': -1.6, 'z0': 0.3, 'z1': 2.9}
box(C['x0'], C['x1'], -0.04, 0.02, C['z0'], C['z1'], 'grass', bevel=0.0, name='yard')
# a worn dirt path: ladder -> table, with a spur to the pond and the kitchen
path([(2.0, -2.4), (1.6, -0.8), (2.2, 0.8), (2.6, 2.0)])
path([(1.6, -0.8), (-0.4, -0.3), (-1.2, 0.0)], 0.75)
path([(-0.4, -0.3), (-2.6, -1.6), (-3.2, -2.6)], 0.75)
# fish pond: dark basin, a rim of river stones, lily pads and a lotus
box(pool['x0'], pool['x1'], -0.45, -0.3, pool['z0'], pool['z1'], 'water-bed', bevel=0.0, name='pond-bed')
for (a, b, c, d) in ((pool['x0'] - 0.1, pool['x1'] + 0.1, pool['z0'] - 0.1, pool['z0']), (pool['x0'] - 0.1, pool['x1'] + 0.1, pool['z1'], pool['z1'] + 0.1), (pool['x0'] - 0.1, pool['x0'], pool['z0'], pool['z1']), (pool['x1'], pool['x1'] + 0.1, pool['z0'], pool['z1'])):
    box(a, b, -0.45, 0.0, c, d, 'earth', bevel=0.0, name='pond-wall')
cx_, cz_ = (pool['x0'] + pool['x1']) / 2, (pool['z0'] + pool['z1']) / 2
for k in range(34):
    a = k / 34 * math.tau
    x = cx_ + math.cos(a) * ((pool['x1'] - pool['x0']) / 2 + 0.12)
    z = cz_ + math.sin(a) * ((pool['z1'] - pool['z0']) / 2 + 0.12)
    x = min(max(x, pool['x0'] - 0.12), pool['x1'] + 0.12)
    z = min(max(z, pool['z0'] - 0.12), pool['z1'] + 0.12)
    r = rnd.uniform(0.13, 0.21)
    box(x - r, x + r, 0.0, rnd.uniform(0.1, 0.2), z - r, z + r, 'stone', bevel=r * 0.8, tint_c=jitter((1, 1, 1), 0.12), name='pond-stone')
for (x, zz, r) in ((-3.6, 0.9, 0.32), (-2.3, 1.5, 0.26), (-3.1, 2.3, 0.3), (-2.0, 0.7, 0.2), (-3.9, 2.6, 0.18)):
    pole((x, 0.07, zz), (x, 0.085, zz), r, 'leaf', seg=12, tint_c=(0.9, 1.05, 0.9), name='lily')
for (x, zz) in ((-3.0, 1.7), (-2.4, 2.4)):
    pole((x, 0.085, zz), (x, 0.17, zz), 0.07, 'flower', seg=8, tint_c=(1.0, 0.75, 0.8), name='lotus')
# bamboo table with two stools at the courtyard table spot (top 0.75 m)
tx, tz = 2.6, 2.6
for k in range(9):
    x = tx - 0.6 + k * 0.15
    pole((x, 0.75, tz - 0.45), (x, 0.75, tz + 0.45), 0.07, 'bamboo', seg=7, tint_c=bamboo_tone(), name='table-top')
for dx in (-0.5, 0.5):
    for dz in (-0.35, 0.35):
        pole((tx + dx, 0.0, tz + dz), (tx + dx, 0.7, tz + dz), 0.045, 'bamboo', name='table-leg')
for (x, z) in ((tx - 0.95, tz), (tx + 0.95, tz)):
    pole((x, 0.0, z), (x, 0.45, z), 0.19, 'bamboo', seg=10, tint_c=bamboo_tone(), name='stool')
# the papag: a bamboo daybed in front of the house (the deck spot the wind level checks, eye 0.8 m)
for k in range(10):
    x = 0.4 + k * 0.17
    pole((x, 0.45, -2.95), (x, 0.45, -2.05), 0.075, 'bamboo', seg=7, tint_c=bamboo_tone(), name='papag')
for x in (0.45, 1.95):
    for z in (-2.9, -2.1):
        pole((x, 0.0, z), (x, 0.42, z), 0.05, 'bamboo', name='papag-leg')
# gumamela (hibiscus) and low shrubs in the yard corners, all below 0.9 m
for (x, z, r) in ((-4.5, 3.6, 0.42), (-3.7, 3.7, 0.3), (4.5, 3.55, 0.45), (3.75, 3.7, 0.32), (4.55, -0.6, 0.36)):
    shrub(x, z, r)

# ================================================================ the bahay kubo
posts_x = [KX0, 1.3, 3.1, KX1]
posts_z = [R['z0'], -5.0, R['z1']]
for x in posts_x:
    for z in posts_z:
        box(x - 0.17, x + 0.17, -0.02, 0.15, z - 0.17, z + 0.17, 'footing', bevel=0.03, name='footing')
        corner = (x in (KX0, KX1)) and (z in (R['z0'], R['z1']))
        top = 4.0 if (corner or z in (R['z0'], R['z1']) or x in (KX0, KX1)) else KFLOOR
        pole((x, 0.15, z), (x, top, z), 0.1, 'bamboo', seg=10, tint_c=bamboo_tone(), name='stilt')
# floor: joists and bamboo slats; the underside reads as the silong ceiling
for z in (R['z0'] + 0.1, -5.0, R['z1'] - 0.1):
    pole((KX0, KFLOOR - 0.12, z), (KX1, KFLOOR - 0.12, z), 0.09, 'bamboo', seg=8, tint_c=(0.85, 0.82, 0.75), name='joist')
x = KX0 + 0.06
while x < KX1 - 0.04:
    pole((x, KFLOOR - 0.02, R['z0'] - 0.05), (x, KFLOOR - 0.02, R['z1'] + 0.05), 0.045, 'bamboo', seg=6, tint_c=bamboo_tone(), name='floor')
    x += 0.09
# silong: slatted on the north and east (solid to the checks), open to the yard and the kitchen
slats((KX0, R['z0']), (KX1, R['z0']), 0.15, KFLOOR - 0.16, 0.1, 0.035, name='silong-n')
slats((KX1, R['z0']), (KX1, R['z1']), 0.15, KFLOOR - 0.16, 0.1, 0.035, name='silong-e')
for y in (0.6, 1.4):
    pole((KX0, y, R['z0'] - 0.05), (KX1, y, R['z0'] - 0.05), 0.03, 'timber', name='silong-rail')
    pole((KX1 + 0.05, y, R['z0']), (KX1 + 0.05, y, R['z1']), 0.03, 'timber', name='silong-rail')
# the reader's bench (bangko) under the house, seat 0.45 m: eye 1.05 m at the checked spot
for k in range(6):
    zz = sz - 0.42 + k * 0.08
    pole((sx - 0.8, 0.45, zz), (sx + 0.8, 0.45, zz), 0.04, 'bamboo', seg=6, tint_c=bamboo_tone(), name='bangko')
for x in (sx - 0.7, sx + 0.7):
    for zz in (sz - 0.38, sz):
        pole((x, 0.0, zz), (x, 0.42, zz), 0.035, 'bamboo', name='bangko-leg')
box(sx - 0.25, sx + 0.25, 0.47, 0.6, sz - 0.4, sz - 0.1, 'banig', bevel=0.04, name='cushion')
# silong life: a clay jar, a rolled mat, hanging baskets, a stack of coconuts
pole((4.3, 0.0, -6.4), (4.3, 0.75, -6.4), 0.3, 'clay', seg=12, r2=0.18, name='tapayan')
pole((3.4, 0.12, -6.6), (2.2, 0.12, -6.6), 0.12, 'banig', seg=10, name='rolled-banig')
for (x, z) in ((2.2, -4.6), (3.7, -4.4)):
    pole((x, KFLOOR - 0.15, z), (x, 1.45, z), 0.008, 'char', seg=4, name='cord')
    pole((x, 1.45, z), (x, 1.2, z), 0.22, 'sawali', seg=10, r2=0.16, name='basket')
for (x, z) in ((0.5, -6.3), (0.8, -6.5), (0.6, -6.0), (0.65, -6.25)):
    box(x - 0.13, x + 0.13, 0.0 if z != -6.25 else 0.22, 0.24 if z != -6.25 else 0.46, z - 0.13, z + 0.13, 'trunk', bevel=0.1, tint_c=(0.75, 0.6, 0.45), name='coconut')

# upper room: sawali walls on all four sides, timber sill and plate, bamboo corner battens
EYV = 4.0
for (a, b, c, d, nm) in ((KX0, KX1, R['z0'] - 0.05, R['z0'] + 0.05, 'n'), (KX0, KX1, R['z1'] - 0.05, R['z1'] + 0.05, 's'), (KX0 - 0.05, KX0 + 0.05, R['z0'], R['z1'], 'w'), (KX1 - 0.05, KX1 + 0.05, R['z0'], R['z1'], 'e')):
    box(a, b, KFLOOR, EYV - 0.1, c, d, 'sawali', bevel=0.0, name='wall-' + nm)
    box(a - 0.05, b + 0.05, KFLOOR - 0.05, KFLOOR + 0.08, c - 0.05, d + 0.05, 'timber', bevel=0.01, name='sill')
    box(a - 0.06, b + 0.06, EYV - 0.14, EYV, c - 0.06, d + 0.06, 'timber', bevel=0.01, name='plate')
    box(a - 0.03, b + 0.03, 2.95, 3.02, c - 0.03, d + 0.03, 'bamboo', bevel=0.01, name='mid-rail')
# windows with propped awnings (tukod) and a dark room behind
def window(cx, cz, face, w=1.1):
    # face: 's' or 'e' or 'w' or 'n' — outward direction
    o = {'s': (0, 1), 'n': (0, -1), 'e': (1, 0), 'w': (-1, 0)}[face]
    along_x = face in ('s', 'n')
    hw = w / 2
    if along_x:
        box(cx - hw, cx + hw, 2.45, 3.45, cz - 0.06, cz + 0.06, 'char', bevel=0.0, name='win-dark')
        box(cx - hw - 0.08, cx + hw + 0.08, 2.37, 2.45, cz - 0.08 + o[1] * 0.04, cz + 0.08 + o[1] * 0.04, 'timber', bevel=0.01, name='win-sill')
        obox((cx, 3.45 + 0.28, cz + o[1] * 0.42), (w + 0.2, 0.06, 0.95), (o[1] * -58, 0, 0), 'sawali', bevel=0.0, name='awning')
        pole((cx - hw, 2.45, cz + o[1] * 0.08), (cx - hw, 3.5, cz + o[1] * 0.8), 0.02, 'bamboo', name='tukod')
    else:
        box(cx - 0.06, cx + 0.06, 2.45, 3.45, cz - hw, cz + hw, 'char', bevel=0.0, name='win-dark')
        box(cx - 0.08 + o[0] * 0.04, cx + 0.08 + o[0] * 0.04, 2.37, 2.45, cz - hw - 0.08, cz + hw + 0.08, 'timber', bevel=0.01, name='win-sill')
        obox((cx + o[0] * 0.42, 3.45 + 0.28, cz), (0.95, 0.06, w + 0.2), (0, 0, o[0] * 58), 'sawali', bevel=0.0, name='awning')
        pole((cx + o[0] * 0.08, 2.45, cz - hw), (cx + o[0] * 0.8, 3.5, cz - hw), 0.02, 'bamboo', name='tukod')


window(3.9, R['z1'], 's')
window(KX1, -5.0, 'e')
window(KX0, -5.6, 'w', 0.9)
window(2.0, R['z0'], 'n')
# door on the yard side, a small landing and a bamboo ladder down to the path
box(1.6, 2.5, KFLOOR + 0.08, 3.65, R['z1'] - 0.07, R['z1'] + 0.07, 'char', bevel=0.0, name='door-dark')
box(1.5, 2.6, 3.65, 3.75, R['z1'] - 0.09, R['z1'] + 0.09, 'timber', bevel=0.01, name='door-head')
box(1.45, 2.65, KFLOOR - 0.06, KFLOOR + 0.02, R['z1'], R['z1'] + 0.45, 'bamboo', bevel=0.02, name='landing')
lz0, lz1 = R['z1'] + 0.45, R['z1'] + 1.55
for x in (1.65, 2.45):
    pole((x, 0.0, lz1), (x, KFLOOR + 0.6, lz0 - 0.15), 0.045, 'bamboo', seg=8, name='ladder-rail')
for k in range(1, 6):
    t = k / 6
    y = KFLOOR * t
    z = lz1 + (lz0 - lz1) * t
    pole((1.65, y, z), (2.45, y, z), 0.03, 'bamboo', seg=6, tint_c=bamboo_tone(), name='rung')

# the nipa roof: one steep hip, eaves 4.0 m, ridge 7.6 m; thin course lines read as layered thatch;
# a shaggy fringe; a bundled ridge with crossed sticks
ex0, ex1, ez0, ez1 = KX0 - 0.9, KX1 + 0.9, R['z0'] - 0.9, R['z1'] + 0.1
rx0, rx1, rzr = 1.7, 2.7, (ez0 + ez1) / 2
EY, RY, TH = EYV - 0.05, 7.6, 0.4


def roof_ring(t, out=0.0):
    """Outline of the roof surface at fraction t from eave (0) to ridge (1), pushed out by `out`."""
    a0 = ex0 + (rx0 - ex0) * t - out
    a1 = ex1 + (rx1 - ex1) * t + out
    b0 = ez0 + (rzr - ez0) * t - out
    b1 = ez1 + (rzr - ez1) * t + out
    return rect(a0, a1, b0, b1, EY + (RY - EY) * t)


solid([rect(ex0 + 0.05, ex1 - 0.05, ez0 + 0.05, ez1 - 0.05, EY), roof_ring(0.0, 0.0), [(rx1, RY + TH, rzr), (rx1, RY + TH, rzr), (rx0, RY + TH, rzr), (rx0, RY + TH, rzr)]], 'thatch', name='thatch-skin', cap_top=False)
# lift the outer surface by the thatch thickness at the eave
solid([roof_ring(0.0, 0.0), [(p[0], p[1] + TH, p[2]) for p in roof_ring(0.0, 0.06)]], 'thatch', tint_c=(0.82, 0.8, 0.76), name='thatch-edge', cap_top=False, cap_bottom=False)
for k, t in enumerate((0.16, 0.32, 0.48, 0.64, 0.8)):
    lo = [(p[0], p[1] + TH - 0.02, p[2]) for p in roof_ring(t, 0.02)]
    hi = [(p[0], p[1] + TH + 0.07, p[2]) for p in roof_ring(t - 0.035, 0.1)]
    solid([lo, hi], 'thatch', tint_c=(0.72, 0.68, 0.62), name=f'course-{k}', cap_top=False, cap_bottom=False)
# fringe: ragged bundles hanging below the eave
ring = roof_ring(0.0, 0.03)
for i in range(4):
    p0, p1 = ring[i], ring[(i + 1) % 4]
    L = math.dist((p0[0], p0[2]), (p1[0], p1[2]))
    t = 0.0
    while t < L:
        w = rnd.uniform(0.16, 0.34)
        k0, k1 = t / L, min(1, (t + w) / L)
        a = (p0[0] + (p1[0] - p0[0]) * k0, p0[2] + (p1[2] - p0[2]) * k0)
        b = (p0[0] + (p1[0] - p0[0]) * k1, p0[2] + (p1[2] - p0[2]) * k1)
        drop = rnd.uniform(0.06, 0.2)
        box(min(a[0], b[0]) - 0.02, max(a[0], b[0]) + 0.02, EY - drop, EY + TH * 0.6, min(a[1], b[1]) - 0.05, max(a[1], b[1]) + 0.05, 'thatch', bevel=0.04, tint_c=jitter((0.9, 0.88, 0.84), 0.12), name='tuft')
        t += w * rnd.uniform(0.75, 0.95)
pole((rx0 - 0.45, RY + TH + 0.08, rzr), (rx1 + 0.45, RY + TH + 0.08, rzr), 0.2, 'thatch', seg=10, tint_c=(0.62, 0.55, 0.47), name='ridge')
for x in (rx0 - 0.4, rx1 + 0.4):
    pole((x - 0.3, RY + TH - 0.1, rzr), (x + 0.3, RY + TH + 0.7, rzr), 0.045, 'timber', name='ridge-horn')
    pole((x + 0.3, RY + TH - 0.1, rzr), (x - 0.3, RY + TH + 0.7, rzr), 0.045, 'timber', name='ridge-horn')

# ================================================================ the dirty kitchen annex
AX0, AX1 = R['x0'], KX0 - 0.05
for x in (AX0, (AX0 + AX1) / 2, AX1):
    for z in (R['z0'], R['z1']):
        pole((x, 0.0, z), (x, 3.0 if z == R['z1'] else 3.9, z), 0.08, 'bamboo', seg=8, tint_c=bamboo_tone(), name='annex-post')
# solid north and west walls (to the checks), woven panels with a bamboo rail
box(AX0, AX1, 0.0, 3.0, R['z0'] - 0.05, R['z0'] + 0.05, 'sawali', bevel=0.0, tint_c=(0.92, 0.9, 0.86), name='annex-n')
box(AX0 - 0.05, AX0 + 0.05, 0.0, 3.0, R['z0'], R['z1'], 'sawali', bevel=0.0, tint_c=(0.92, 0.9, 0.86), name='annex-w')
for y in (0.9, 2.0):
    pole((AX0 - 0.08, y, R['z0']), (AX0 - 0.08, y, R['z1']), 0.035, 'bamboo', name='annex-rail')
# low nipa lean-to roof: 3.0 m at the yard edge rising to 3.9 m at the back; west overhang
az0, az1 = R['z0'] - 0.7, R['z1'] + 0.1
ax0, ax1 = AX0 - 0.7, AX1
solid([[(ax0, 2.95, az1), (ax1, 2.95, az1), (ax1, 3.85, az0), (ax0, 3.85, az0)], [(ax0, 3.25, az1), (ax1, 3.25, az1), (ax1, 4.15, az0), (ax0, 4.15, az0)]], 'thatch', tint_c=(0.95, 0.93, 0.88), name='annex-roof')
for k, f in enumerate((0.25, 0.5, 0.75)):
    zz = az1 + (az0 - az1) * f
    yy = 3.25 + (4.15 - 3.25) * f
    box(ax0 - 0.03, ax1, yy - 0.02, yy + 0.07, zz - 0.06, zz + 0.06, 'thatch', bevel=0.03, tint_c=(0.72, 0.68, 0.62), name='annex-course')
t = ax0
while t < ax1:
    w = rnd.uniform(0.16, 0.32)
    box(t, min(t + w, ax1), 2.95 - rnd.uniform(0.05, 0.16), 3.15, az1 - 0.06, az1 + 0.06, 'thatch', bevel=0.04, tint_c=jitter((0.9, 0.88, 0.84), 0.12), name='tuft')
    t += w * 0.85
# kitchen: a clay stove on a raised hearth, two palayok pots, firewood, a water jar, a shelf of plates
box(-4.7, -3.0, 0.0, 0.8, -6.85, -6.0, 'clay', bevel=0.06, tint_c=(0.9, 0.85, 0.8), name='hearth')
for x in (-4.25, -3.45):
    box(x - 0.28, x + 0.28, 0.8, 0.98, -6.7, -6.15, 'char', bevel=0.05, name='stove')
    pole((x, 0.98, -6.42), (x, 1.22, -6.42), 0.22, 'char', seg=12, r2=0.17, name='palayok')
for k in range(7):
    y = 0.08 + (k % 3) * 0.14
    z = -4.2 + (k // 3) * 0.02
    pole((-4.75, y, z - 0.6), (-4.75, y, z + 0.6), 0.065, 'timber', seg=6, tint_c=jitter((1.1, 1.0, 0.9), 0.1), name='firewood')
pole((-1.5, 0.0, -6.4), (-1.5, 0.7, -6.4), 0.3, 'clay', seg=12, r2=0.2, name='banga')
box(-2.8, -1.2, 1.5, 1.56, -6.95, -6.65, 'timber', bevel=0.01, name='shelf')
for k in range(5):
    x = -2.65 + k * 0.3
    pole((x, 1.56, -6.8), (x, 1.82, -6.82), 0.12, 'trim', seg=10, name='plate')
for x in (-2.2, -1.9):
    pole((x, 3.0, -4.5), (x, 2.2, -4.5), 0.008, 'char', seg=4, name='cord')
    box(x - 0.08, x + 0.08, 2.0, 2.25, -4.58, -4.42, 'trim', bevel=0.06, tint_c=(1.0, 0.95, 0.85), name='garlic')

# ================================================================ bamboo fence, 1.0 m
for key in ('east garden wall', 'south garden wall', 'west garden wall'):
    b = BOX[key]
    x0, x1 = b['c'][0] - b['h'][0], b['c'][0] + b['h'][0]
    z0, z1 = b['c'][2] - b['h'][2], b['c'][2] + b['h'][2]
    along_x = (x1 - x0) > (z1 - z0)
    mid = (z0 + z1) / 2 if along_x else (x0 + x1) / 2
    L0, L1 = (x0, x1) if along_x else (z0, z1)
    t = L0 + 0.05
    i = 0
    while t < L1 - 0.02:
        top = FENCE_H - (0.07 if i % 3 == 1 else 0.0 if i % 3 == 0 else 0.03)
        p0 = (t, 0.0, mid) if along_x else (mid, 0.0, t)
        p1 = (t, top, mid) if along_x else (mid, top, t)
        pole(p0, p1, 0.048, 'bamboo', seg=7, tint_c=bamboo_tone(), name='fence-pole')
        t += 0.1
        i += 1
    out = 0.08 if key != 'west garden wall' else -0.08
    for y in (0.3, 0.75):
        p0 = (L0, y, mid + out) if along_x else (mid + out, y, L0)
        p1 = (L1, y, mid + out) if along_x else (mid + out, y, L1)
        pole(p0, p1, 0.035, 'timber', seg=6, name='fence-rail')

# ================================================================ the neighbour's house, Manila
nh = BOX['neighbour house']
nx0, nx1 = nh['c'][0] - nh['h'][0], nh['c'][0] + nh['h'][0]
nz0, nz1 = nh['c'][2] - nh['h'][2], nh['c'][2] + nh['h'][2]
ny1 = nh['c'][1] + nh['h'][1]
GF = 2.5
box(nx0, nx1, 0.0, GF, nz0, nz1, 'teal', bevel=0.05, name='n-ground')
box(nx0 - 0.05, nx1 + 0.05, GF, GF + 0.14, nz0 - 0.05, nz1 + 0.05, 'trim', bevel=0.02, name='n-band')
box(nx0, nx1, GF + 0.14, ny1 - 0.32, nz0, nz1, 'coral', bevel=0.05, name='n-upper')
# corrugated shed roof inside the box: 4.6 m at the west, 4.3 m at the east, with fascia
solid([[(nx0 - 0.25, ny1 - 0.32, nz1 + 0.3), (nx1 + 0.2, ny1 - 0.62, nz1 + 0.3), (nx1 + 0.2, ny1 - 0.62, nz0 - 0.3), (nx0 - 0.25, ny1 - 0.32, nz0 - 0.3)],
       [(nx0 - 0.25, ny1 - 0.26, nz1 + 0.3), (nx1 + 0.2, ny1 - 0.56, nz1 + 0.3), (nx1 + 0.2, ny1 - 0.56, nz0 - 0.3), (nx0 - 0.25, ny1 - 0.26, nz0 - 0.3)]], 'gi', name='n-roof')
box(nx0 - 0.3, nx0 - 0.22, ny1 - 0.45, ny1 - 0.2, nz0 - 0.3, nz1 + 0.3, 'trim', bevel=0.01, name='n-fascia')
# west face: the watching window, a jalousie, the balcony with a decorative grille
wy, wz = N['window'][1], N['window'][2]
box(nx0 - 0.06, nx0 + 0.02, wy - 0.62, wy + 0.62, wz - 0.72, wz + 0.72, 'char', bevel=0.0, name='n-win-dark')
for k in range(7):
    y = wy - 0.5 + k * 0.17
    obox((nx0 - 0.08, y, wz - 0.38), (0.02, 0.13, 0.62), (0, 0, 35), 'glass', name='jalousie')
box(nx0 - 0.1, nx0 + 0.02, wy - 0.7, wy + 0.7, wz - 0.8, wz - 0.72, 'trim', bevel=0.005, name='n-win-frame')
box(nx0 - 0.1, nx0 + 0.02, wy - 0.7, wy + 0.7, wz + 0.72, wz + 0.8, 'trim', bevel=0.005, name='n-win-frame')
box(nx0 - 0.1, nx0 + 0.02, wy + 0.62, wy + 0.7, wz - 0.8, wz + 0.8, 'trim', bevel=0.005, name='n-win-frame')
box(nx0 - 0.85, nx0, GF - 0.05, GF + 0.12, wz - 1.15, wz + 1.15, 'trim', bevel=0.02, name='n-balcony')
for k in range(16):
    zz = wz - 1.1 + k * 0.147
    pole((nx0 - 0.82, GF + 0.12, zz), (nx0 - 0.82, GF + 0.95, zz), 0.016, 'steel', seg=4, name='grille')
for y in (GF + 0.45, GF + 0.95):
    pole((nx0 - 0.82, y, wz - 1.15), (nx0 - 0.82, y, wz + 1.15), 0.025, 'steel', seg=6, name='grille-rail')
for k in range(5):  # a row of grille hoops: the decorative band
    zz = wz - 0.88 + k * 0.44
    pole((nx0 - 0.82, GF + 0.62, zz - 0.18), (nx0 - 0.82, GF + 0.8, zz), 0.012, 'steel', seg=4, name='grille-loop')
    pole((nx0 - 0.82, GF + 0.8, zz), (nx0 - 0.82, GF + 0.62, zz + 0.18), 0.012, 'steel', seg=4, name='grille-loop')
for zz in (wz - 0.85, wz + 0.9):
    pole((nx0 - 0.55, GF + 0.12, zz), (nx0 - 0.55, GF + 0.36, zz), 0.13, 'clay', seg=10, r2=0.1, name='pot')
    box(nx0 - 0.78, nx0 - 0.32, GF + 0.32, GF + 0.62, zz - 0.22, zz + 0.22, 'leaf', bevel=0.12, name='pot-plant')
# laundry on the balcony rail
for k, c in enumerate(((0.9, 0.3, 0.3), (0.3, 0.55, 0.85), (0.95, 0.85, 0.35))):
    zz = wz - 0.6 + k * 0.5
    box(nx0 - 0.86, nx0 - 0.8, GF + 0.55, GF + 0.95, zz - 0.18, zz + 0.18, 'cloth', bevel=0.0, tint_c=c, name='laundry')
# south face (toward the player): the sari-sari store with grille, counter, goods, striped awning, sign
sx0, sx1 = nx0 + 0.5, nx0 + 2.6
box(sx0, sx1, 0.8, 2.0, nz1 - 0.04, nz1 + 0.02, 'char', bevel=0.0, name='store-dark')
for k in range(8):
    y = 0.95 + (k % 2) * 0.5
    for j in range(7):
        x = sx0 + 0.15 + j * 0.28
        box(x - 0.07, x + 0.07, y, y + rnd.uniform(0.14, 0.28), nz1 - 0.2, nz1 - 0.06, 'cloth', bevel=0.01, tint_c=rnd.choice([(0.9, 0.3, 0.25), (0.2, 0.5, 0.8), (0.95, 0.8, 0.2), (0.3, 0.7, 0.4), (0.95, 0.95, 0.95)]), name='goods')
    if k > 1:
        break
for k in range(15):
    x = sx0 + k * (sx1 - sx0) / 14
    pole((x, 0.8, nz1 + 0.05), (x, 2.0, nz1 + 0.05), 0.012, 'steel', seg=4, name='store-grille')
box(sx0 - 0.1, sx1 + 0.1, 0.78, 0.86, nz1, nz1 + 0.35, 'timber', bevel=0.01, name='counter')
obox(((sx0 + sx1) / 2, 2.22, nz1 + 0.45), (sx1 - sx0 + 0.5, 0.04, 1.0), (24, 0, 0), 'awning', name='store-awning')
box(sx0, sx1, 2.38, 2.55, nz1 + 0.02, nz1 + 0.08, 'sign', bevel=0.01, name='store-sign')
for k in range(9):  # painted letters suggested by dark blocks
    x = sx0 + 0.15 + k * 0.22
    box(x, x + 0.13, 2.41, 2.52, nz1 + 0.08, nz1 + 0.09, 'red', bevel=0.0, name='sign-letter')
box(sx1 + 0.4, sx1 + 1.3, 0.0, 2.1, nz1 - 0.03, nz1 + 0.03, 'timber', bevel=0.01, name='n-door')
# upper windows on the south: jalousies with trim
for x in (nx0 + 1.1, nx0 + 3.0):
    box(x - 0.5, x + 0.5, 3.0, 3.9, nz1 - 0.02, nz1 + 0.03, 'char', bevel=0.0, name='n-upwin')
    for k in range(5):
        obox((x, 3.1 + k * 0.18, nz1 + 0.05), (0.95, 0.13, 0.02), (35, 0, 0), 'glass', name='jalousie')
    box(x - 0.58, x + 0.58, 2.92, 3.0, nz1, nz1 + 0.1, 'trim', bevel=0.01, name='n-upsill')
# east face: an aircon box under a window
box(nx1 - 0.02, nx1 + 0.04, 3.1, 3.9, -1.2, -0.2, 'char', bevel=0.0, name='n-ewin')
box(nx1, nx1 + 0.45, 2.75, 3.0, -1.1, -0.3, 'trim', bevel=0.03, name='aircon')
# roof top: a blue water tank on a stand and a TV antenna (both small, at the east side)
for (dx, dz) in ((-0.3, -0.3), (0.3, -0.3), (-0.3, 0.3), (0.3, 0.3)):
    pole((nx1 - 0.9 + dx, ny1 - 0.55, nz0 + 1.0 + dz), (nx1 - 0.9 + dx, ny1 - 0.15, nz0 + 1.0 + dz), 0.03, 'steel', seg=4, name='tank-stand')
pole((nx1 - 0.9, ny1 - 0.15, nz0 + 1.0), (nx1 - 0.9, ny1 + 0.75, nz0 + 1.0), 0.42, 'tank', seg=14, name='tank')
pole((nx1 - 0.4, ny1 - 0.6, nz1 - 0.6), (nx1 - 0.4, ny1 + 1.2, nz1 - 0.6), 0.02, 'steel', seg=4, name='antenna')
for k in range(4):
    y = ny1 + 0.6 + k * 0.17
    pole((nx1 - 0.4, y, nz1 - 0.95 + k * 0.05), (nx1 - 0.4, y, nz1 - 0.25 - k * 0.05), 0.012, 'steel', seg=4, name='antenna-bar')

# ================================================================ around the yard: life
# tall plants only where their shadows cannot reach the yard in the levels' hours: behind the house
# (north), or far out at the island's sides
banana(6.8, -7.6, seed=1)
banana(7.8, -8.2, 2.3, seed=2)
banana(-6.6, -6.2, 2.4, seed=3)
papaya(3.6, -8.3, seed=4)
papaya(-2.8, -8.4, 3.0, seed=5)
carabao(-7.4, -3.8, yaw=-70)
for (x, z, yaw, w) in ((-6.2, 0.6, 30, False), (-6.7, 1.3, 160, True), (6.4, 3.5, 250, False), (-5.9, 1.8, 90, True)):
    hen(x, z, yaw, w)
# a laundry line on the west lawn
for z in (0.4, 3.0):
    pole((-7.8, 0.0, z), (-7.8, 1.75, z), 0.04, 'bamboo', name='line-pole')
pole((-7.8, 1.7, 0.4), (-7.8, 1.7, 3.0), 0.008, 'char', seg=4, name='line')
for k, c in enumerate(((0.95, 0.35, 0.3), (0.95, 0.95, 0.95), (0.3, 0.55, 0.9), (0.98, 0.8, 0.25), (0.45, 0.75, 0.45))):
    zz = 0.7 + k * 0.48
    box(-7.83, -7.77, 1.15 + (k % 2) * 0.12, 1.7, zz - 0.18, zz + 0.18, 'cloth', bevel=0.0, tint_c=c, name='laundry')
# gumamela hedge along the front of the fence, outside, low
for (x, z, r) in ((-4.0, 4.7, 0.42), (-3.3, 4.95, 0.28), (-0.6, 4.75, 0.34), (2.4, 4.8, 0.44), (3.1, 5.0, 0.26)):
    shrub(x, z, r, flowers=r > 0.3)
