# ================================================================ PHILIPPINES: bahay kubo
# Matches src/sim: room x -5..5, z -7..-3 with solid north/west/east walls to 3 m and a roof slab
# from 3 m; the courtyard face is open. The floor is raised 0.45 m on posts (the silong), so the
# reader sitting on a banig mat has the 1.05 m eye height the checks use. The steep nipa roof rises
# above 3 m; its courtyard eave stops at the checks' roof edge (z -2.9), so it shades nothing the
# checks do not know about. Garden fence: 1.0 m bamboo, as in the Philippines levels.
import math as _m
from mathutils import Matrix

FLOOR = 0.45


def P(x, y, z):
    """Site metres (y up, +z south) to Blender (z up, -y south)."""
    return Vector((x, -z, y))
FENCE_H = 1.0


def S2(hexs):
    return S(hexs)


MATS.update({
    'thatch': node_mat('thatch', None.__class__ and (lambda nt, bsdf, coord: _thatch(nt, bsdf, coord))),
    'sawali': node_mat('sawali', lambda nt, bsdf, coord: _sawali(nt, bsdf, coord)),
    'bamboo': node_mat('bamboo', flat(S('#d8b468'), 0.55)),
    'timber': node_mat('timber', basswood(S('#6b4428'))),
    'capiz': node_mat('capiz', lambda nt, bsdf, coord: _capiz(nt, bsdf, coord)),
    'banig': node_mat('banig', lambda nt, bsdf, coord: _banig(nt, bsdf, coord)),
    'earth': node_mat('earth', card(S('#c49a6c'), 0.08)),
    'footing': node_mat('footing', card(S('#bdb5a6'), 0.05)),
    'mint': node_mat('mint', card(S('#a9d9c0'), 0.03)),
    'cream': node_mat('cream', card(S('#f4e7cc'), 0.03)),
    'gi': node_mat('gi', lambda nt, bsdf, coord: _gi(nt, bsdf, coord)),
    'steel': node_mat('steel', flat(S('#2f3438'), 0.5, 0.3)),
    'clay': node_mat('clay', card(S('#b9643d'), 0.05)),
    'leaf': node_mat('leaf', flat(S('#4f9a3a'), 0.7)),
    'water-bed': node_mat('water-bed', flat(S('#2e7f7a'), 0.6)),
    'red': node_mat('red', flat(S('#c0443a'), 0.6)),
    'stone': node_mat('stone', card(S('#b8ab95'), 0.06)),  # river stone, warmer and darker than paving
})


def _thatch(nt, bsdf, coord):
    # nipa shingles: long straw streaks down the slope (Blender z), banded courses, sun-bleached tips
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (11, 11, 0.9)
    nt.links.new(coord.outputs['Object'], mp.inputs['Vector'])
    n = nt.nodes.new('ShaderNodeTexNoise')
    n.inputs['Scale'].default_value = 1.0
    n.inputs['Detail'].default_value = 4
    nt.links.new(mp.outputs['Vector'], n.inputs['Vector'])
    w = nt.nodes.new('ShaderNodeTexWave')
    w.bands_direction = 'Z'
    w.inputs['Scale'].default_value = 1.6
    w.inputs['Distortion'].default_value = 1.5
    nt.links.new(coord.outputs['Object'], w.inputs['Vector'])
    straw = mix(nt, n.outputs['Fac'], rgb(nt, S('#6e4622')), rgb(nt, S('#d2a660')))
    c = mix(nt, w.outputs['Fac'], straw, rgb(nt, S('#a8793f')))
    nt.links.new(tint(nt, c), bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.95


def _sawali(nt, bsdf, coord):
    # woven bamboo strips: a diagonal over-under checker, two straw tones, a little fibre
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Rotation'].default_value = (0.785, 0.785, 0.0)
    nt.links.new(coord.outputs['Object'], mp.inputs['Vector'])
    ch = nt.nodes.new('ShaderNodeTexChecker')
    ch.inputs['Scale'].default_value = 7.0
    ch.inputs['Color1'].default_value = (*S('#d9bb7d'), 1)
    ch.inputs['Color2'].default_value = (*S('#b38f57'), 1)
    nt.links.new(mp.outputs['Vector'], ch.inputs['Vector'])
    c = mix(nt, noise(nt, coord, 30, 4, 0.6), ch.outputs['Color'], rgb(nt, S('#c7a56a')))
    nt.links.new(tint(nt, c), bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.85


def _capiz(nt, bsdf, coord):
    # capiz shell panes: pearly squares in a dark timber grid
    out = None
    grid = []
    for axis in ('X', 'Z'):
        w = nt.nodes.new('ShaderNodeTexWave')
        w.wave_profile = 'SAW'
        w.bands_direction = axis
        w.inputs['Scale'].default_value = 2.2
        w.inputs['Distortion'].default_value = 0.0
        nt.links.new(coord.outputs['Object'], w.inputs['Vector'])
        r = nt.nodes.new('ShaderNodeValToRGB')
        r.color_ramp.interpolation = 'CONSTANT'
        r.color_ramp.elements[0].color = (*S('#4a2f1c'), 1)
        r.color_ramp.elements[1].position = 0.12
        r.color_ramp.elements[1].color = (1, 1, 1, 1)
        nt.links.new(w.outputs['Fac'], r.inputs['Fac'])
        grid.append(r.outputs['Color'])
    m = nt.nodes.new('ShaderNodeMix')
    m.data_type = 'RGBA'
    m.blend_type = 'MULTIPLY'
    m.inputs['Factor'].default_value = 1.0
    nt.links.new(grid[0], m.inputs['A'])
    nt.links.new(grid[1], m.inputs['B'])
    pearl = mix(nt, noise(nt, coord, 14, 3, 0.5), rgb(nt, S('#efe6d2')), rgb(nt, S('#f8f2e6')))
    m2 = nt.nodes.new('ShaderNodeMix')
    m2.data_type = 'RGBA'
    m2.blend_type = 'MULTIPLY'
    m2.inputs['Factor'].default_value = 1.0
    nt.links.new(pearl, m2.inputs['A'])
    nt.links.new(m.outputs['Result'], m2.inputs['B'])
    nt.links.new(m2.outputs['Result'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.35


def _banig(nt, bsdf, coord):
    # woven sleeping mat: bright stripes on straw
    w = nt.nodes.new('ShaderNodeTexWave')
    w.wave_profile = 'SAW'
    w.bands_direction = 'X'
    w.inputs['Scale'].default_value = 0.9
    w.inputs['Distortion'].default_value = 0.0
    nt.links.new(coord.outputs['Object'], w.inputs['Vector'])
    r = nt.nodes.new('ShaderNodeValToRGB')
    r.color_ramp.interpolation = 'CONSTANT'
    cols = ['#e6c98e', '#c0443a', '#e6c98e', '#2f7f6d', '#e6c98e', '#e3a12f', '#e6c98e', '#7a3f8f']
    els = r.color_ramp.elements
    els[0].color = (*S(cols[0]), 1)
    els[1].position = 1 / len(cols)
    els[1].color = (*S(cols[1]), 1)
    for i in range(2, len(cols)):
        e = els.new(i / len(cols))
        e.color = (*S(cols[i]), 1)
    nt.links.new(w.outputs['Fac'], r.inputs['Fac'])
    c = mix(nt, noise(nt, coord, 60, 2, 0.5), r.outputs['Color'], rgb(nt, S('#d7b97c')))
    nt.links.new(c, bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.8


def _gi(nt, bsdf, coord):
    # corrugated iron, painted blue: fine ridges baked as light and dark bands
    w = nt.nodes.new('ShaderNodeTexWave')
    w.bands_direction = 'X'
    w.inputs['Scale'].default_value = 6.0
    nt.links.new(coord.outputs['Object'], w.inputs['Vector'])
    c = mix(nt, w.outputs['Fac'], rgb(nt, S('#3d6f9e')), rgb(nt, S('#5b8fc0')))
    nt.links.new(c, bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.5


def pole(a, b, r, mat, tint_c=(1, 1, 1), seg=8, name='pole'):
    """A round pole between two site points (bamboo, posts, rails)."""
    A, B = P(*a), P(*b)
    d = B - A
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r, depth=d.length)
    rot = d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=Matrix.Translation((A + B) / 2) @ rot, verts=bm.verts)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    col = me.color_attributes.new('tint', 'FLOAT_COLOR', 'POINT')
    for dd in col.data:
        dd.color = (*tint_c, 1)
    parts.append((ob, mat))
    return ob


def poly_solid(top_pts, bottom_pts, mat, name='solid', tint_c=(1, 1, 1)):
    """A closed solid between two rings of site points (same count): used for the thatch roof."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    t = [bm.verts.new(P(*p)) for p in top_pts]
    b = [bm.verts.new(P(*p)) for p in bottom_pts]
    return bm, t, b, me


def bamboo_tone():
    return rnd.choice([(1, 1, 1), (0.92, 0.95, 0.8), (1.05, 1.0, 0.92), (0.88, 0.86, 0.8)])


R = LAY['room']
C = LAY['court']
N = LAY['neighbour']

# ---------------------------------------------------------------- courtyard ground
pool = {'x0': -4.3, 'x1': -1.6, 'z0': 0.3, 'z1': 2.9}
box(C['x0'], C['x1'], -0.04, 0.02, C['z0'], C['z1'], 'earth', bevel=0.0, name='court-earth')
# a bamboo terrace (batalan) in front of the house, slats running east-west
z = C['z0'] + 0.02
while z < C['z0'] + 1.5:
    box(C['x0'] + 0.1, C['x1'] - 0.1, 0.02, 0.1, z, min(z + 0.11, C['z0'] + 1.5), 'bamboo', bevel=0.02, tint_c=bamboo_tone(), name='batalan')
    z += 0.125
for x in (C['x0'] + 0.1, 0.0, C['x1'] - 0.1):
    box(x - 0.08, x + 0.08, -0.02, 0.06, C['z0'], C['z0'] + 1.5, 'timber', bevel=0.01, name='bearer')
# stepping stones: one deliberate path from the ladder to the table, a spur to the pond
def stones(pts, size=0.5):
    for (x, zz) in pts:
        w = size * rnd.uniform(0.85, 1.15)
        d = size * rnd.uniform(0.7, 0.95)
        box(x - w / 2, x + w / 2, -0.01, 0.035, zz - d / 2, zz + d / 2, 'stone', bevel=0.05, tint_c=jitter((0.72, 0.68, 0.62), 0.08), name='flag')


stones([(-3.7, -1.2), (-3.2, -0.45), (-2.4, 0.0), (-1.4, 0.1), (-0.4, 0.45), (0.5, 0.95), (1.3, 1.55), (1.9, 2.0)])
stones([(-1.0, 0.9), (-1.2, 1.7)], 0.42)
# fish pond: dark basin, a rim of rounded stones, lily pads
box(pool['x0'], pool['x1'], -0.45, -0.3, pool['z0'], pool['z1'], 'water-bed', bevel=0.0, name='pond-bed')
for (a, b, c, d) in ((pool['x0'] - 0.25, pool['x1'] + 0.25, pool['z0'] - 0.25, pool['z0']), (pool['x0'] - 0.25, pool['x1'] + 0.25, pool['z1'], pool['z1'] + 0.25), (pool['x0'] - 0.25, pool['x0'], pool['z0'], pool['z1']), (pool['x1'], pool['x1'] + 0.25, pool['z0'], pool['z1'])):
    box(a, b, -0.45, 0.02, c, d, 'stone', bevel=0.01, tint_c=(0.85, 0.83, 0.8), name='pond-wall')
k = 0.0
per = 2 * ((pool['x1'] - pool['x0']) + (pool['z1'] - pool['z0']))
while k < per:
    t = k
    if t < pool['x1'] - pool['x0']:
        x, zz = pool['x0'] + t, pool['z0'] - 0.12
    elif t < (pool['x1'] - pool['x0']) + (pool['z1'] - pool['z0']):
        x, zz = pool['x1'] + 0.12, pool['z0'] + t - (pool['x1'] - pool['x0'])
    elif t < 2 * (pool['x1'] - pool['x0']) + (pool['z1'] - pool['z0']):
        x, zz = pool['x1'] - (t - (pool['x1'] - pool['x0']) - (pool['z1'] - pool['z0'])), pool['z1'] + 0.12
    else:
        x, zz = pool['x0'] - 0.12, pool['z1'] - (t - 2 * (pool['x1'] - pool['x0']) - (pool['z1'] - pool['z0']))
    r = rnd.uniform(0.13, 0.2)
    box(x - r, x + r, 0.0, rnd.uniform(0.12, 0.2), zz - r, zz + r, 'stone', bevel=r * 0.8, tint_c=jitter((0.7, 0.68, 0.64), 0.1), name='pond-stone')
    k += r * 1.7
for (x, zz, r) in ((-3.6, 0.9, 0.32), (-2.3, 1.5, 0.26), (-3.1, 2.3, 0.3), (-2.0, 0.7, 0.2)):
    pole((x, 0.07, zz), (x, 0.085, zz), r, 'leaf', seg=12, name='lily')
pole((-3.0, 0.085, 1.7), (-3.0, 0.16, 1.7), 0.07, 'red', seg=8, name='lotus')

# a green verge inside the fence, with low shrubs in the corners
for (a, b, c, d) in ((C['x0'], C['x1'], C['z1'] - 0.55, C['z1']), (C['x0'], C['x0'] + 0.5, C['z0'] + 1.5, C['z1']), (C['x1'] - 0.5, C['x1'], C['z0'] + 1.5, C['z1'])):
    box(a, b, -0.02, 0.035, c, d, 'grass', bevel=0.0, name='verge')
for (x, zz, r) in ((-4.55, 3.55, 0.42), (-3.9, 3.65, 0.3), (4.5, 3.5, 0.45), (3.85, 3.65, 0.32), (4.55, -0.9, 0.36), (-4.55, -0.6, 0.3)):
    box(x - r, x + r, 0.0, r * 1.5, zz - r, zz + r, 'leaf', bevel=r * 0.7, tint_c=jitter((1, 1, 1), 0.12), name='shrub')

# bamboo table and stools at the courtyard table spot (top at 0.75 m)
tx, tz = 2.6, 2.6
box(tx - 0.6, tx + 0.6, 0.72, 0.78, tz - 0.45, tz + 0.45, 'bamboo', bevel=0.02, name='table-top')
for dx in (-0.5, 0.5):
    for dz in (-0.35, 0.35):
        pole((tx + dx, 0.0, tz + dz), (tx + dx, 0.72, tz + dz), 0.045, 'bamboo', name='table-leg')
for (sx_, sz_) in ((tx - 0.95, tz), (tx + 0.95, tz)):
    pole((sx_, 0.0, sz_), (sx_, 0.45, sz_), 0.2, 'bamboo', seg=10, tint_c=bamboo_tone(), name='stool')

# ---------------------------------------------------------------- the bahay kubo
xs = [R['x0'], -2.5, 0.0, 2.5, R['x1']]
zs = [R['z0'], -5.0, R['z1']]
for x in xs:
    for zz in zs:
        box(x - 0.2, x + 0.2, -0.02, 0.18, zz - 0.2, zz + 0.2, 'footing', bevel=0.03, name='footing')
        top = R['h'] if (zz in (R['z0'], R['z1']) or x in (R['x0'], R['x1'])) else FLOOR
        box(x - 0.09, x + 0.09, 0.18, top, zz - 0.09, zz + 0.09, 'timber', bevel=0.02, name='post')
# floor: bamboo slats on joists
for zz in (R['z0'] + 0.1, -5.0, R['z1'] - 0.1):
    box(R['x0'], R['x1'], FLOOR - 0.16, FLOOR - 0.06, zz - 0.08, zz + 0.08, 'timber', bevel=0.01, name='joist')
x = R['x0'] + 0.05
while x < R['x1'] - 0.05:
    box(x, min(x + 0.075, R['x1'] - 0.05), FLOOR - 0.06, FLOOR, R['z0'] + 0.05, R['z1'] - 0.02, 'bamboo', bevel=0.012, tint_c=bamboo_tone(), name='slat')
    x += 0.09
# silong: bamboo lattice skirt on the three closed sides
for (a, b, c, d) in ((R['x0'], R['x1'], R['z0'] - 0.04, R['z0'] + 0.04), (R['x0'] - 0.04, R['x0'] + 0.04, R['z0'], R['z1']), (R['x1'] - 0.04, R['x1'] + 0.04, R['z0'], R['z1'])):
    along_x = (b - a) > (d - c)
    L0, L1 = (a, b) if along_x else (c, d)
    t = L0 + 0.12
    while t < L1 - 0.1:
        p0 = (t, 0.18, (c + d) / 2) if along_x else ((a + b) / 2, 0.18, t)
        p1 = (t, FLOOR - 0.06, (c + d) / 2) if along_x else ((a + b) / 2, FLOOR - 0.06, t)
        pole(p0, p1, 0.03, 'bamboo', seg=6, tint_c=bamboo_tone(), name='lattice')
        t += 0.11
# walls: woven sawali panels between timber posts, a sill and a top plate
WALLS = [('north', R['x0'], R['x1'], R['z0'] - 0.05, R['z0'] + 0.05), ('west', R['x0'] - 0.05, R['x0'] + 0.05, R['z0'], R['z1']), ('east', R['x1'] - 0.05, R['x1'] + 0.05, R['z0'], R['z1'])]
for (nm, a, b, c, d) in WALLS:
    box(a, b, FLOOR, R['h'] - 0.12, c, d, 'sawali', bevel=0.0, name='sawali-' + nm)
    box(a - 0.04, b + 0.04, FLOOR, FLOOR + 0.1, c - 0.04, d + 0.04, 'timber', bevel=0.01, name='sill')
    box(a - 0.05, b + 0.05, R['h'] - 0.14, R['h'], c - 0.05, d + 0.05, 'timber', bevel=0.01, name='plate')
    box(a - 0.03, b + 0.03, 1.55, 1.62, c - 0.03, d + 0.03, 'bamboo', bevel=0.01, name='mid-rail')
# capiz windows, closed (the checks treat these walls as solid): north two, west and east one
def capiz_window(cx, cz, along_x, outward):
    w = 1.3
    if along_x:
        a, b, c, d = cx - w / 2, cx + w / 2, cz + outward * 0.06, cz + outward * 0.1
    else:
        a, b, c, d = cx + outward * 0.06, cx + outward * 0.1, cz - w / 2, cz + w / 2
    box(a, b, 1.25, 2.45, min(c, d), max(c, d), 'capiz', bevel=0.0, name='capiz')
    # frame, and a propped awning shutter (tukod) over it
    if along_x:
        box(a - 0.08, b + 0.08, 2.45, 2.55, min(c, d) - 0.02, max(c, d) + 0.02, 'timber', bevel=0.01, name='win-head')
        box(a - 0.08, b + 0.08, 1.15, 1.25, min(c, d) - 0.04, max(c, d) + 0.06, 'timber', bevel=0.01, name='win-sill')
        box(a - 0.05, b + 0.05, 2.55, 2.62, cz + outward * 0.1, cz + outward * 0.75, 'sawali', bevel=0.0, name='awning')
    else:
        box(min(a, b) - 0.02, max(a, b) + 0.02, 2.45, 2.55, c - 0.08, d + 0.08, 'timber', bevel=0.01, name='win-head')
        box(min(a, b) - 0.04, max(a, b) + 0.06, 1.15, 1.25, c - 0.08, d + 0.08, 'timber', bevel=0.01, name='win-sill')
        lo, hi = sorted((cx + outward * 0.1, cx + outward * 0.75))
        box(lo, hi, 2.55, 2.62, c - 0.05, d + 0.05, 'sawali', bevel=0.0, name='awning')


capiz_window(-2.5, R['z0'], True, -1)
capiz_window(2.5, R['z0'], True, -1)
capiz_window(R['x0'], -5.0, False, -1)
capiz_window(R['x1'], -5.0, False, 1)
# courtyard face: open veranda with a low bamboo rail (top 0.85 m, below every sight line to the
# reader), an eave beam, and a gap for the ladder
box(R['x0'], R['x1'], R['h'] - 0.16, R['h'], R['z1'] - 0.08, R['z1'] + 0.08, 'timber', bevel=0.015, name='eave-beam')
gap = (-4.3, -3.2)
for (a, b) in ((R['x0'], gap[0]), (gap[1], R['x1'])):
    pole((a, 0.85, R['z1'] + 0.02), (b, 0.85, R['z1'] + 0.02), 0.04, 'bamboo', name='rail')
    pole((a, 0.66, R['z1'] + 0.02), (b, 0.66, R['z1'] + 0.02), 0.03, 'bamboo', name='rail')
    t = a + 0.15
    while t < b - 0.05:
        pole((t, FLOOR, R['z1'] + 0.02), (t, 0.85, R['z1'] + 0.02), 0.022, 'bamboo', seg=6, tint_c=bamboo_tone(), name='baluster')
        t += 0.18
# steps: three solid bamboo-faced treads up to the floor
lx0, lx1 = gap
for i, y in enumerate((0.15, 0.3, 0.45)):
    box(lx0 + 0.04, lx1 - 0.04, 0.0, y, R['z1'], R['z1'] + 0.75 - i * 0.25, 'bamboo', bevel=0.03, tint_c=jitter((0.95, 0.92, 0.85), 0.05), name='step')

# ---------------------------------------------------------------- the nipa roof
# hip roof: eaves at 3.0 m, ridge at 6.0 m; thick thatch with a ragged fringe; dark ridge cap
EY, RY, TH = R['h'] - 0.05, 6.0, 0.38
ex0, ex1, ez0, ez1 = R['x0'] - 0.9, R['x1'] + 0.9, R['z0'] - 0.9, R['z1'] + 0.1
rx0, rx1, rz = -2.4, 2.4, (ez0 + ez1) / 2
def hip_layer(inset, lift, thick, tone, name):
    """One course of thatch: a closed hip-roof shell whose eave is inset and lifted."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()

    def V(x, y, zz):
        return bm.verts.new(P(x, y, zz))
    a0, a1, b0, b1 = ex0 + inset, ex1 - inset, ez0 + inset, ez1 - inset * 0.25
    y0 = EY + lift
    o = [V(a0, y0 + thick, b1), V(a1, y0 + thick, b1), V(a1, y0 + thick, b0), V(a0, y0 + thick, b0)]
    ro = [V(rx0, RY + thick, rz), V(rx1, RY + thick, rz)]
    i_ = [V(a0 + 0.06, y0, b1 - 0.06), V(a1 - 0.06, y0, b1 - 0.06), V(a1 - 0.06, y0, b0 + 0.06), V(a0 + 0.06, y0, b0 + 0.06)]
    ri = [V(rx0 + 0.3, RY - 0.12, rz), V(rx1 - 0.3, RY - 0.12, rz)]
    for f in ((o[0], o[1], ro[1], ro[0]), (o[2], o[3], ro[0], ro[1]), (o[1], o[2], ro[1]), (o[3], o[0], ro[0])):
        bm.faces.new(f)
    for f in ((i_[1], i_[0], ri[0], ri[1]), (i_[3], i_[2], ri[1], ri[0]), (i_[2], i_[1], ri[1]), (i_[0], i_[3], ri[0])):
        bm.faces.new(f)
    for k in range(4):
        bm.faces.new((i_[k], i_[(k + 1) % 4], o[(k + 1) % 4], o[k]))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    col = me.color_attributes.new('tint', 'FLOAT_COLOR', 'POINT')
    for dd in col.data:
        dd.color = (*tone, 1)
    parts.append((ob, 'thatch'))
    return (a0, a1, b0, b1, y0)


def fringe(p0, p1, y0, tone):
    """A ragged hanging edge: overlapping straw bundles of uneven width and drop."""
    L = math.dist((p0[0], p0[1]), (p1[0], p1[1]))
    t = 0.0
    while t < L:
        w = rnd.uniform(0.18, 0.42)
        k0, k1 = t / L, min(1.0, (t + w) / L)
        a = (p0[0] + (p1[0] - p0[0]) * k0, p0[1] + (p1[1] - p0[1]) * k0)
        b = (p0[0] + (p1[0] - p0[0]) * k1, p0[1] + (p1[1] - p0[1]) * k1)
        drop = rnd.uniform(0.05, 0.17)
        box(min(a[0], b[0]) - 0.02, max(a[0], b[0]) + 0.02, y0 - drop, y0 + 0.1, min(a[1], b[1]) - 0.05, max(a[1], b[1]) + 0.05, 'thatch', bevel=0.05, tint_c=jitter(tone, 0.12), name='tuft')
        t += w * rnd.uniform(0.7, 0.95)


# three courses, each lifted and drawn in, so the roof shows the stepped layers of nipa thatch
for k, (inset, lift, tone) in enumerate(((0.0, 0.0, (0.9, 0.88, 0.84)), (0.42, 0.55, (1.0, 0.98, 0.96)), (0.84, 1.1, (1.06, 1.04, 1.0)))):
    a0, a1, b0, b1, y0 = hip_layer(inset, lift, TH, tone, f'thatch-{k}')
    for (p0, p1) in (((a0, b1), (a1, b1)), ((a1, b1), (a1, b0)), ((a1, b0), (a0, b0)), ((a0, b0), (a0, b1))):
        fringe(p0, p1, y0, tone)
pole((rx0 - 0.35, RY + TH + 0.05, rz), (rx1 + 0.35, RY + TH + 0.05, rz), 0.2, 'timber', seg=10, tint_c=(0.8, 0.75, 0.7), name='ridge')
for x in (rx0 - 0.3, rx1 + 0.3):
    pole((x - 0.25, RY + TH - 0.1, rz), (x + 0.25, RY + TH + 0.55, rz), 0.05, 'timber', name='ridge-horn')
# rafters showing under the eave on the courtyard side
x = ex0 + 0.4
while x < ex1 - 0.3:
    pole((x, EY - 0.02, ez1 - 0.05), (x * 0.6, RY - 0.4, rz), 0.035, 'bamboo', seg=6, name='rafter')
    x += 0.8

# ---------------------------------------------------------------- inside: the reading corner
sx, _, sz = LAY['seat']
box(sx - 1.3, sx + 1.2, FLOOR, FLOOR + 0.012, sz - 1.4, sz + 0.3, 'banig', bevel=0.0, name='banig')
box(sx - 0.35, sx + 0.35, FLOOR + 0.01, FLOOR + 0.16, sz - 1.05, sz - 0.6, 'red', bevel=0.06, name='pillow')
box(sx + 0.55, sx + 1.15, FLOOR, FLOOR + 0.32, sz - 0.9, sz - 0.3, 'timber', bevel=0.02, name='dulang')
for i in range(4):
    h = 0.04 + i * 0.0
    box(sx + 0.65 + rnd.uniform(-0.03, 0.03), sx + 0.95, FLOOR + 0.32 + i * 0.045, FLOOR + 0.36 + i * 0.045, sz - 0.75, sz - 0.5, 'book', bevel=0.004, tint_c=rnd.choice([(0.85, 0.3, 0.25), (0.25, 0.45, 0.6), (0.9, 0.8, 0.5), (0.3, 0.5, 0.35)]), name='book')
# baul chest and a clay jar at the back
box(R['x0'] + 0.3, R['x0'] + 1.4, FLOOR, FLOOR + 0.55, R['z0'] + 0.25, R['z0'] + 0.85, 'timber', bevel=0.03, tint_c=(1.1, 1.0, 0.9), name='baul')
pole((R['x1'] - 0.6, FLOOR, R['z0'] + 0.6), (R['x1'] - 0.6, FLOOR + 0.55, R['z0'] + 0.6), 0.22, 'clay', seg=12, name='banga')
# a hanging capiz lamp
pole((0.0, R['h'], -5.0), (0.0, 2.45, -5.0), 0.01, 'steel', seg=4, name='lamp-cord')
box(-0.22, 0.22, 2.1, 2.45, -5.22, -4.78, 'capiz', bevel=0.08, name='lamp')

# ---------------------------------------------------------------- bamboo fence, 1.0 m
for key in ('east garden wall', 'south garden wall', 'west garden wall'):
    b = BOX[key]
    x0, x1 = b['c'][0] - b['h'][0], b['c'][0] + b['h'][0]
    z0, z1 = b['c'][2] - b['h'][2], b['c'][2] + b['h'][2]
    along_x = (x1 - x0) > (z1 - z0)
    L0, L1 = (x0, x1) if along_x else (z0, z1)
    mid = (z0 + z1) / 2 if along_x else (x0 + x1) / 2
    t = L0 + 0.05
    i = 0
    while t < L1 - 0.02:
        top = FENCE_H - (0.06 if i % 2 else 0.0)
        p0 = (t, 0.0, mid) if along_x else (mid, 0.0, t)
        p1 = (t, top, mid) if along_x else (mid, top, t)
        pole(p0, p1, 0.048, 'bamboo', seg=7, tint_c=bamboo_tone(), name='fence-pole')
        t += 0.1
        i += 1
    for y in (0.3, 0.78):
        off = 0.08
        p0 = (L0, y, mid + off) if along_x else (mid - off if key == 'west garden wall' else mid + off, y, L0)
        p1 = (L1, y, mid + off) if along_x else (mid - off if key == 'west garden wall' else mid + off, y, L1)
        pole(p0, p1, 0.035, 'timber', seg=6, name='fence-rail')

# ---------------------------------------------------------------- the neighbour's house, Manila
nh = BOX['neighbour house']
nx0, nx1 = nh['c'][0] - nh['h'][0], nh['c'][0] + nh['h'][0]
nz0, nz1 = nh['c'][2] - nh['h'][2], nh['c'][2] + nh['h'][2]
ny1 = nh['c'][1] + nh['h'][1]
box(nx0, nx1, 0.0, 2.45, nz0, nz1, 'mint', bevel=0.06, name='n-ground')
box(nx0 - 0.04, nx1 + 0.04, 2.45, 2.6, nz0 - 0.04, nz1 + 0.04, 'cream', bevel=0.02, name='n-band')
box(nx0, nx1, 2.6, ny1, nz0, nz1, 'cream', bevel=0.06, name='n-upper')
box(nx0 - 0.06, nx1 + 0.06, ny1 - 0.1, ny1 + 0.05, nz0 - 0.06, nz1 + 0.06, 'mint', bevel=0.02, name='n-parapet')
wy, wz = N['window'][1], N['window'][2]
# the watching window on the west face: timber frame, dark opening (the game adds the warm glow)
for (a, b, c, d) in ((wy - 0.66, wy - 0.6, wz - 0.76, wz + 0.76), (wy + 0.6, wy + 0.66, wz - 0.76, wz + 0.76), (wy - 0.66, wy + 0.66, wz - 0.76, wz - 0.7), (wy - 0.66, wy + 0.66, wz + 0.7, wz + 0.76)):
    box(nx0 - 0.06, nx0 + 0.02, a, b, c, d, 'timber', bevel=0.005, name='n-win-frame')
# balcony: slab, steel grille, a blue corrugated canopy, potted plants
box(nx0 - 0.85, nx0, 2.45, 2.6, wz - 1.1, wz + 1.1, 'cream', bevel=0.02, name='n-balcony')
for zz in [wz - 1.05 + k * 0.15 for k in range(15)]:
    pole((nx0 - 0.82, 2.6, zz), (nx0 - 0.82, 3.35, zz), 0.015, 'steel', seg=4, name='grille')
pole((nx0 - 0.82, 3.35, wz - 1.1), (nx0 - 0.82, 3.35, wz + 1.1), 0.03, 'steel', seg=6, name='grille-top')
for (z_a, z_b) in ((wz - 1.1, wz - 1.1), (wz + 1.1, wz + 1.1)):
    pole((nx0 - 0.82, 2.6, z_a), (nx0, 3.35, z_b), 0.0, 'steel', seg=3, name='nop') if False else None
box(nx0 - 1.0, nx0 + 0.02, 4.32, 4.4, wz - 1.25, wz + 1.25, 'gi', bevel=0.0, name='n-canopy')
for zz in (wz - 0.8, wz + 0.85):
    pole((nx0 - 0.6, 2.6, zz), (nx0 - 0.6, 2.85, zz), 0.13, 'clay', seg=10, name='pot')
    pole((nx0 - 0.6, 2.85, zz), (nx0 - 0.6, 3.15, zz), 0.2, 'leaf', seg=8, name='pot-plant')
# ground floor: sari-sari store window on the south face, a door on the west
box(nx0 + 0.6, nx0 + 2.4, 0.9, 2.0, nz1 - 0.02, nz1 + 0.06, 'steel', bevel=0.0, name='n-store-grille')
box(nx0 + 0.5, nx0 + 2.5, 0.85, 0.95, nz1, nz1 + 0.3, 'timber', bevel=0.01, name='n-store-counter')
box(nx0 + 0.4, nx0 + 2.6, 2.05, 2.15, nz1, nz1 + 0.5, 'red', bevel=0.01, name='n-store-sign')
box(nx0 - 0.04, nx0 + 0.01, 0.0, 2.15, nz0 + 1.2, nz0 + 2.2, 'timber', bevel=0.01, name='n-door')
box(nx0 - 0.04, nx0 + 0.01, 0.9, 1.9, nz0 + 2.8, nz0 + 3.9, 'capiz', bevel=0.0, name='n-win2')
# a water tank on the roof, at the far east side
pole((nx1 - 0.8, ny1, nz0 + 0.8), (nx1 - 0.8, ny1 + 0.9, nz0 + 0.8), 0.45, 'steel', seg=14, tint_c=(2.2, 2.2, 2.3), name='tank')

# ---------------------------------------------------------------- stepping stones on the lawn
for (x, zz) in ((6.2, 2.2), (6.9, 3.0), (7.4, 3.9), (5.6, 1.4)):
    box(x - 0.32, x + 0.32, -0.02, 0.03, zz - 0.24, zz + 0.24, 'stone', bevel=0.02, tint_c=jitter((1, 1, 1), 0.06), name='step')
