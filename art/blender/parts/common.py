# ================================================================ shared modelling helpers for country houses
# Stays inside what src/sim checks: the room footprint x -5..5, z -7..-3 has solid north, west and
# east sides to 3 m, a roof plane at 3 m, and an open courtyard face; the reader's eye is 1.05 m at
# (1.6, -3.5); the garden fence is 1.0 m; the neighbour's house fits its box below 4.6 m.
#   right of the footprint: the bahay kubo raised on tall bamboo stilts. The reader sits on a bench
#     in the silong, the shaded space under the house, whose north and east sides are slatted.
#   left of the footprint: the dirty kitchen annex, a low open shed with a clay stove.
# Every sun ray that reaches the reader passes the courtyard face below 2.0 m in Manila in November
# (noon altitude about 59 degrees), so the kubo floor at 2 m shades nothing the checks let through.
import math as _m
from mathutils import Matrix, Euler, noise as mnoise

FENCE_H = 1.0
KFLOOR = 2.0  # kubo floor
KX0, KX1 = -0.6, 5.0  # kubo on the right of the footprint; annex to the left


def P(x, y, z):
    """Site metres (y up, +z south) to Blender (z up, -y south)."""
    return Vector((x, -z, y))


def _thatch(nt, bsdf, coord):
    # nipa: coarse straw streaks down the slope, sun-bleached and weathered grey in patches
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (7, 7, 0.7)
    nt.links.new(coord.outputs['Object'], mp.inputs['Vector'])
    n = nt.nodes.new('ShaderNodeTexNoise')
    n.inputs['Scale'].default_value = 1.0
    n.inputs['Detail'].default_value = 6
    n.inputs['Roughness'].default_value = 0.7
    nt.links.new(mp.outputs['Vector'], n.inputs['Vector'])
    r = nt.nodes.new('ShaderNodeValToRGB')
    els = r.color_ramp.elements
    els[0].position = 0.3
    els[0].color = (*S('#5e3f22'), 1)
    els[1].position = 0.72
    els[1].color = (*S('#cfa767'), 1)
    mid = els.new(0.5)
    mid.color = (*S('#9a7443'), 1)
    nt.links.new(n.outputs['Fac'], r.inputs['Fac'])
    weather = mix(nt, noise(nt, coord, 0.6, 2, 0.5), r.outputs['Color'], rgb(nt, S('#a39577')))
    nt.links.new(tint(nt, weather), bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.96


def _sawali(nt, bsdf, coord):
    # woven bamboo strips: a diagonal over-under checker, two straw tones, a little fibre
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Rotation'].default_value = (0.785, 0.785, 0.0)
    nt.links.new(coord.outputs['Object'], mp.inputs['Vector'])
    ch = nt.nodes.new('ShaderNodeTexChecker')
    ch.inputs['Scale'].default_value = 6.0
    ch.inputs['Color1'].default_value = (*S('#dcc086'), 1)
    ch.inputs['Color2'].default_value = (*S('#a9844e'), 1)
    nt.links.new(mp.outputs['Vector'], ch.inputs['Vector'])
    c = mix(nt, noise(nt, coord, 30, 4, 0.6), ch.outputs['Color'], rgb(nt, S('#c4a066')))
    nt.links.new(tint(nt, c), bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.85


def _bamboo(nt, bsdf, coord):
    # bamboo: straw with green-gold variation and darker weathering; per-pole tint does the rest
    c = mix(nt, noise(nt, coord, 4, 3, 0.5), rgb(nt, S('#d8b468')), rgb(nt, S('#bf9a52')))
    nt.links.new(tint(nt, c), bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.5


def _weathered(nt, bsdf, coord):
    # old timber: dark brown with grain and grey sun-bleaching
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (2, 2, 40)
    nt.links.new(coord.outputs['Object'], mp.inputs['Vector'])
    n = nt.nodes.new('ShaderNodeTexNoise')
    n.inputs['Scale'].default_value = 1.0
    n.inputs['Detail'].default_value = 5
    nt.links.new(mp.outputs['Vector'], n.inputs['Vector'])
    c = mix(nt, n.outputs['Fac'], rgb(nt, S('#4a3020')), rgb(nt, S('#7a5638')))
    c = mix(nt, noise(nt, coord, 0.8, 2, 0.5), c, rgb(nt, S('#8a7d6c')))
    nt.links.new(tint(nt, c), bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.85


def _banig(nt, bsdf, coord):
    w = nt.nodes.new('ShaderNodeTexWave')
    w.wave_profile = 'SAW'
    w.bands_direction = 'X'
    w.inputs['Scale'].default_value = 1.2
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
    nt.links.new(r.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.8


def _gi(nt, bsdf, coord):
    # corrugated iron with rust: ridges as light and dark bands, rust in patches
    w = nt.nodes.new('ShaderNodeTexWave')
    w.bands_direction = 'X'
    w.inputs['Scale'].default_value = 7.0
    nt.links.new(coord.outputs['Object'], w.inputs['Vector'])
    c = mix(nt, w.outputs['Fac'], rgb(nt, S('#8d969c')), rgb(nt, S('#c3cacd')))
    n = noise(nt, coord, 1.6, 4, 0.6)
    r = nt.nodes.new('ShaderNodeValToRGB')
    r.color_ramp.elements[0].position = 0.52
    r.color_ramp.elements[1].position = 0.62
    nt.links.new(n, r.inputs['Fac'])
    c = mix(nt, r.outputs['Color'], c, rgb(nt, S('#9c5a32')))
    nt.links.new(c, bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.55
    bsdf.inputs['Metallic'].default_value = 0.3


def _awning(nt, bsdf, coord):
    # striped canvas: red and white
    w = nt.nodes.new('ShaderNodeTexWave')
    w.wave_profile = 'SAW'
    w.bands_direction = 'X'
    w.inputs['Scale'].default_value = 2.2
    w.inputs['Distortion'].default_value = 0.0
    nt.links.new(coord.outputs['Object'], w.inputs['Vector'])
    r = nt.nodes.new('ShaderNodeValToRGB')
    r.color_ramp.interpolation = 'CONSTANT'
    r.color_ramp.elements[0].color = (*S('#d6453a'), 1)
    r.color_ramp.elements[1].position = 0.5
    r.color_ramp.elements[1].color = (*S('#f7efe2'), 1)
    nt.links.new(w.outputs['Fac'], r.inputs['Fac'])
    nt.links.new(r.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.8


def _plaster(base):
    # painted hollow block: paint colour with soft grime toward the ground
    def build(nt, bsdf, coord):
        sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        nt.links.new(coord.outputs['Object'], sep.inputs['Vector'])
        r = nt.nodes.new('ShaderNodeMapRange')
        r.inputs['From Min'].default_value = 0.0
        r.inputs['From Max'].default_value = 0.9
        nt.links.new(sep.outputs['Z'], r.inputs['Value'])
        c = mix(nt, noise(nt, coord, 6, 4, 0.6), rgb(nt, base), rgb(nt, tuple(v * 0.92 for v in base)))
        grime = mix(nt, r.outputs['Result'], rgb(nt, tuple(v * 0.72 for v in base)), c)
        nt.links.new(tint(nt, grime), bsdf.inputs['Base Color'])
        bsdf.inputs['Roughness'].default_value = 0.9
    return build


MATS.update({
    'thatch': node_mat('thatch', _thatch),
    'sawali': node_mat('sawali', _sawali),
    'bamboo': node_mat('bamboo', _bamboo),
    'timber': node_mat('timber', _weathered),
    'banig': node_mat('banig', _banig),
    'earth': node_mat('earth', card(S('#c9a57a'), 0.08)),
    'footing': node_mat('footing', card(S('#9d968a'), 0.06)),
    'teal': node_mat('teal', _plaster(S('#5fb3a6'))),
    'coral': node_mat('coral', _plaster(S('#f0a07a'))),
    'trim': node_mat('trim', card(S('#f6efe0'), 0.03)),
    'gi': node_mat('gi', _gi),
    'awning': node_mat('awning', _awning),
    'steel': node_mat('steel', flat(S('#2c3135'), 0.5, 0.3)),
    'glass': node_mat('glass', flat(S('#9fc3cf'), 0.2)),
    'tank': node_mat('tank', flat(S('#2f6fb5'), 0.45)),
    'clay': node_mat('clay', card(S('#b45f38'), 0.06)),
    'leaf': node_mat('leaf', card(S('#4f9a3a'), 0.12)),
    'banana': node_mat('banana', card(S('#7fbf3f'), 0.1)),
    'trunk': node_mat('trunk', card(S('#8a8a52'), 0.1)),
    'red': node_mat('red', flat(S('#c8322e'), 0.6)),
    'flower': node_mat('flower', flat(S('#e0302b'), 0.6)),
    'stone': node_mat('stone', card(S('#a99d88'), 0.07)),
    'water-bed': node_mat('water-bed', flat(S('#2e6f6a'), 0.6)),
    'carabao': node_mat('carabao', card(S('#77737a'), 0.06)),
    'horn': node_mat('horn', flat(S('#2a2622'), 0.5)),
    'cloth': node_mat('cloth', flat((1, 1, 1), 0.85)),
    'sign': node_mat('sign', flat(S('#f3d23a'), 0.7)),
    'char': node_mat('char', flat(S('#2b2421'), 0.9)),
    'hen': node_mat('hen', card(S('#c8743a'), 0.1)),
})


def _finish(ob, me, mat, tint_c):
    bpy.context.collection.objects.link(ob)
    col = me.color_attributes.new('tint', 'FLOAT_COLOR', 'POINT')
    for d in col.data:
        d.color = (*tint_c, 1)
    parts.append((ob, mat))
    return ob


def pole(a, b, r, mat, tint_c=(1, 1, 1), seg=8, name='pole', r2=None):
    """A round (optionally tapered) pole between two site points."""
    A, B = P(*a), P(*b)
    d = B - A
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=max(d.length, 1e-3))
    rot = d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=Matrix.Translation((A + B) / 2) @ rot, verts=bm.verts)
    bm.to_mesh(me)
    bm.free()
    return _finish(bpy.data.objects.new(name, me), me, mat, tint_c)


def obox(c, size, rot, mat, tint_c=(1, 1, 1), bevel=0.0, name='obox', taper=None):
    """An oriented box: centre and size in site metres, rotation (rx, ry, rz) in degrees about the
    site axes (y is up). taper scales the +x end (used for leaves)."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        # (x, z, -y): a rotation, not a mirror, so faces stay outward
        x, y, z = v.co.x * size[0], v.co.z * size[1], -v.co.y * size[2]
        if taper is not None and v.co.x > 0:
            y *= taper
            z *= taper
        v.co = Vector((x, y, z))
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=min(bevel, min(size) * 0.45), segments=2, profile=0.6, affect='EDGES')
    R_ = Euler((_m.radians(rot[0]), _m.radians(rot[1]), _m.radians(rot[2])), 'YXZ').to_matrix().to_4x4()
    # build in site axes (x, y up, z south) then convert to Blender
    to_b = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    bmesh.ops.transform(bm, matrix=Matrix.Translation(P(*c)) @ to_b @ R_, verts=bm.verts)
    bm.to_mesh(me)
    bm.free()
    return _finish(bpy.data.objects.new(name, me), me, mat, tint_c)


def solid(rings, mat, tint_c=(1, 1, 1), name='solid', cap_top=True, cap_bottom=True):
    """A closed solid through rings of site points (each ring the same count), bottom to top."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    vs = [[bm.verts.new(P(*p)) for p in ring] for ring in rings]
    n = len(rings[0])
    for a, b in zip(vs, vs[1:]):
        for k in range(n):
            bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]))
    if cap_bottom:
        bm.faces.new(vs[0][::-1])
    if cap_top and len(set(id(v) for v in vs[-1])) == n:
        bm.faces.new(vs[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    return _finish(bpy.data.objects.new(name, me), me, mat, tint_c)


def rect(x0, x1, z0, z1, y):
    return [(x0, y, z1), (x1, y, z1), (x1, y, z0), (x0, y, z0)]


def bamboo_tone():
    return rnd.choice([(1, 1, 1), (0.95, 1.0, 0.82), (1.06, 1.0, 0.9), (0.9, 0.88, 0.8)])


def slats(a, b, y0, y1, step, r, mat='bamboo', name='slat'):
    """Vertical round slats from a to b (site x,z), y0..y1."""
    L = math.dist(a, b)
    n = max(1, int(L / step))
    for k in range(n + 1):
        t = k / n
        x = a[0] + (b[0] - a[0]) * t
        z = a[1] + (b[1] - a[1]) * t
        pole((x, y0, z), (x, y1 - rnd.uniform(0, 0.04), z), r, mat, seg=6, tint_c=bamboo_tone(), name=name)



# ---- shared props
PATH_Y = [0.022]


def path(pts, w=0.9):
    """A worn dirt path: one continuous ribbon with a slightly wavy edge (no overlapping tiles)."""
    dense = []
    for (p0, p1) in zip(pts, pts[1:]):
        n = max(1, int(math.dist(p0, p1) / 0.25))
        for k in range(n):
            t = k / n
            dense.append((p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t))
    dense.append(pts[-1])
    left, right = [], []
    PATH_Y[0] += 0.004  # each path a hair above the last, so crossings do not flicker
    py = PATH_Y[0]
    for i, (x, z) in enumerate(dense):
        a_ = dense[max(0, i - 1)]
        b_ = dense[min(len(dense) - 1, i + 1)]
        dx, dz = b_[0] - a_[0], b_[1] - a_[1]
        L = math.hypot(dx, dz) or 1
        nx_, nz_ = -dz / L, dx / L
        hw = w / 2 * rnd.uniform(0.85, 1.1)
        left.append((x + nx_ * hw, py, z + nz_ * hw))
        right.append((x - nx_ * hw, py, z - nz_ * hw))
    me = bpy.data.meshes.new('path')
    bm = bmesh.new()
    L_ = [bm.verts.new(P(*p)) for p in left]
    R_ = [bm.verts.new(P(*p)) for p in right]
    for i in range(len(dense) - 1):
        f = bm.faces.new((L_[i], R_[i], R_[i + 1], L_[i + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        if f.normal.z < 0:
            f.normal_flip()
    bm.to_mesh(me)
    bm.free()
    _finish(bpy.data.objects.new('path', me), me, 'earth', (1.2, 1.15, 1.1))



def blob(x, y, z, r, mat, tint_c, squash=0.85, seed=0, name='blob'):
    """A faceted, slightly lumpy ball: leaves, fruit, stones."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
    k = random.Random(seed)
    off = Vector((k.uniform(0, 50), k.uniform(0, 50), 0))
    for v in bm.verts:
        v.co *= 1 + 0.11 * mnoise.noise(v.co * 1.5 + off)
        v.co.x *= r
        v.co.y *= r
        v.co.z *= r * squash
    bmesh.ops.transform(bm, matrix=Matrix.Translation(P(x, y, z)), verts=bm.verts)
    bm.to_mesh(me)
    bm.free()
    return _finish(bpy.data.objects.new(name, me), me, mat, tint_c)


def shrub(x, z, r, flowers=True):
    s0 = rnd.randint(0, 999)
    blob(x, r * 0.75, z, r, 'leaf', jitter((1, 1, 1), 0.12), seed=s0, name='shrub')
    blob(x + r * 0.45, r * 0.55, z + r * 0.2, r * 0.7, 'leaf', jitter((1.08, 1.12, 1.0), 0.1), seed=s0 + 1, name='shrub')
    blob(x - r * 0.4, r * 0.5, z - r * 0.25, r * 0.65, 'leaf', jitter((0.92, 1.0, 0.9), 0.1), seed=s0 + 2, name='shrub')
    if flowers:
        for _ in range(int(6 * r / 0.3)):
            a = rnd.uniform(0, math.tau)
            fx, fz = x + math.cos(a) * r * 0.85, z + math.sin(a) * r * 0.85
            fy = rnd.uniform(r * 0.6, r * 1.8)
            blob(fx, fy, fz, 0.075, 'flower', jitter((1, 1, 1), 0.1), squash=0.6, seed=rnd.randint(0, 999), name='gumamela')



def banana(x, z, h=2.6, seed=0):
    k = random.Random(seed)
    pole((x, 0.0, z), (x, h * 0.65, z), 0.16, 'trunk', seg=9, r2=0.11, name='banana-trunk')
    for i in range(7):
        a = i / 7 * 360 + k.uniform(-20, 20)
        tilt = k.uniform(25, 55)
        L = k.uniform(1.0, 1.4)
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        cxl = x + ca * L * 0.45 * math.cos(math.radians(tilt))
        czl = z + sa * L * 0.45 * math.cos(math.radians(tilt))
        cy = h * 0.65 + L * 0.45 * math.sin(math.radians(tilt)) * 0.6
        obox((cxl, cy, czl), (L, 0.025, 0.38), (0, -a, tilt * 0.6), 'banana', tint_c=jitter((1, 1, 1), 0.12), name='banana-leaf', taper=0.55)
    obox((x + 0.15, h * 0.55, z), (0.18, 0.3, 0.18), (0, 0, 0), 'banana', tint_c=(0.9, 1.1, 0.6), bevel=0.06, name='banana-bunch')
    pole((x + 0.15, h * 0.45, z), (x + 0.15, h * 0.32, z), 0.08, 'red', seg=8, r2=0.03, tint_c=(0.6, 0.2, 0.35), name='banana-heart')


def papaya(x, z, h=3.2, seed=0):
    k = random.Random(seed)
    pole((x, 0.0, z), (x, h, z), 0.1, 'trunk', seg=8, r2=0.07, tint_c=(1.1, 1.0, 0.85), name='papaya-trunk')
    for i in range(8):
        a = i / 8 * 360 + k.uniform(-15, 15)
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        obox((x + ca * 0.55, h + 0.05, z + sa * 0.55), (0.9, 0.03, 0.5), (0, -a, -18), 'leaf', tint_c=jitter((1.05, 1.1, 0.95), 0.1), name='papaya-leaf', taper=1.2)
    for i in range(5):
        a = i / 5 * math.tau
        fx, fz = x + math.cos(a) * 0.14, z + math.sin(a) * 0.14
        fy = h - 0.25 - (i % 2) * 0.15
        box(fx - 0.08, fx + 0.08, fy - 0.13, fy + 0.13, fz - 0.08, fz + 0.08, 'banana', bevel=0.07, tint_c=(1.2, 0.9, 0.35) if i % 2 else (0.85, 1.05, 0.55), name='papaya-fruit')


def carabao(x, z, yaw=0):
    # a resting water buffalo: body, belly, head, swept horns, legs, tail
    def part(c, s, rot=(0, 0, 0), mat='carabao', b=0.08):
        ca, sa = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
        px, pz = c[0] * ca - c[2] * sa, c[0] * sa + c[2] * ca
        obox((x + px, c[1], z + pz), s, (rot[0], rot[1] - yaw, rot[2]), mat, bevel=b, name='carabao')
    part((0, 0.95, 0), (1.9, 0.75, 0.85))
    part((0.05, 0.62, 0), (1.5, 0.3, 0.7))
    part((1.15, 0.95, 0), (0.55, 0.45, 0.42), (0, 0, -18))
    part((1.42, 0.82, 0), (0.25, 0.25, 0.32), (0, 0, -18), b=0.06)
    for s in (-1, 1):
        part((1.05, 1.25, s * 0.38), (0.6, 0.09, 0.09), (s * -25, s * 30, 18), 'horn', 0.03)
    for (dx, dz) in ((0.7, -0.27), (0.7, 0.27), (-0.7, -0.27), (-0.7, 0.27)):
        part((dx, 0.3, dz), (0.17, 0.62, 0.17), b=0.04)
    part((-1.0, 0.75, 0), (0.06, 0.55, 0.06), (0, 0, 12), 'horn', 0.02)


def hen(x, z, yaw=0, white=False):
    tc = (1.6, 1.6, 1.6) if white else (1, 1, 1)
    obox((x, 0.18, z), (0.3, 0.2, 0.18), (0, -yaw, 0), 'hen', tint_c=tc, bevel=0.07, name='hen')
    ca, sa = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    obox((x + ca * 0.17, 0.33, z + sa * 0.17), (0.11, 0.12, 0.1), (0, -yaw, 0), 'hen', tint_c=tc, bevel=0.04, name='hen-head')
    obox((x + ca * 0.18, 0.41, z + sa * 0.18), (0.08, 0.05, 0.03), (0, -yaw, 0), 'red', name='hen-comb')
    obox((x - ca * 0.16, 0.3, z - sa * 0.16), (0.08, 0.2, 0.14), (0, -yaw, -25), 'hen', tint_c=(0.5, 0.35, 0.25) if not white else tc, bevel=0.03, name='hen-tail')


