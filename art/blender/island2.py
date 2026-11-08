# Island v2 for VaLora: Two Watchers: a low-poly diorama island that meets the sea.
#   VALORA_COUNTRY=ph /home/claude/bpy-env/bin/python art/blender/island2.py
# Built as a heightfield in site metres (y up, +z south towards the player):
#   - a flat grass plateau where the house, courtyard and neighbour stand (height 0)
#   - a short soil lip, then a sand beach that runs under the water (sea level -0.9)
#   - rock cliffs instead of beach along the back, with a boulder outcrop as the backdrop landmark
#   - faceted boulders on the shore, and a foam strip where sand meets water
# Vertex colours only (flat shaded); the game adds the moving sea.
# Output: public/models/valora-island-<country>.glb

import math, os, random
import bpy, bmesh
from mathutils import Vector, noise

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
COUNTRY = os.environ.get('VALORA_COUNTRY', 'ph')
OUT = os.path.join(ROOT, 'public', 'models', f'valora-island-{COUNTRY}.glb')
rnd = random.Random(7)
bpy.ops.wm.read_factory_settings(use_empty=True)

SEA = -0.9
# the plateau: everything built stands inside this rounded rectangle
PX0, PX1, PZ0, PZ1, PR = -8.8, 14.8, -9.0, 5.4, 3.2


def hexc(h):
    h = h.lstrip('#')
    return tuple(((int(h[i:i + 2], 16) / 255) ** 2.2) for i in (0, 2, 4))


PAL = {
    'grass': hexc('#7cbf4f'), 'grass2': hexc('#69ad43'), 'soil': hexc('#8a5a34'),
    'sand': hexc('#f1d7a2'), 'wet': hexc('#d9b67c'), 'bed': hexc('#c9a978'),
    'rock': hexc('#9a8f84'), 'rock2': hexc('#7f756c'), 'moss': hexc('#7aa64a'), 'foam': (1.0, 1.0, 1.0),
}


def sd_plateau(x, z):
    """Signed distance to the plateau outline (negative inside), with a wobbly coast."""
    cx, cz = (PX0 + PX1) / 2, (PZ0 + PZ1) / 2
    hx, hz = (PX1 - PX0) / 2 - PR, (PZ1 - PZ0) / 2 - PR
    qx, qz = abs(x - cx) - hx, abs(z - cz) - hz
    out = math.hypot(max(qx, 0), max(qz, 0)) + min(max(qx, qz), 0) - PR
    # wobble only outward so nothing built ends up over the edge
    return out - max(0.0, noise.noise(Vector((x * 0.16, z * 0.16, 3.0)))) * 0.9


def beach_width(x, z):
    """Wide sandy beach at the front (towards the player), cliffs along the back."""
    cz = (PZ0 + PZ1) / 2
    front = max(0.0, min(1.0, (z - cz) / ((PZ1 - PZ0) / 2)))  # 0 back .. 1 front
    w = 0.6 + 3.4 * front ** 1.4
    return w * (0.85 + 0.3 * (noise.noise(Vector((x * 0.11, z * 0.11, 9.0))) + 0.5))


def height(x, z):
    d = sd_plateau(x, z)
    if d <= 0:
        # flat where people live; soft mounds only far from the built area
        far = max(0.0, min(1.0, (-d - 0.0) / 2.5)) * (1.0 if (x < -6.5 or x > 13.2 or z < -8.2) else 0.0)
        return far * (0.25 + 0.25 * noise.noise(Vector((x * 0.3, z * 0.3, 1.0))))
    w = beach_width(x, z)
    if d < 0.35:  # soil lip
        return -0.32 * (d / 0.35)
    if w < 1.0:  # back: cliff straight down
        return -0.32 - min(1.0, (d - 0.35) / 0.6) * 2.6
    t = (d - 0.35) / w
    if t <= 1.0:  # beach: gentle, slightly convex, crossing the sea about two thirds out
        return -0.36 - 0.9 * t ** 1.15
    return -1.26 - min(2.0, (t - 1.0) * 1.6)


def colour(x, z, y, d):
    j = noise.noise(Vector((x * 0.9, z * 0.9, 5.0))) * 0.05
    if d <= 0:
        c = PAL['grass'] if noise.noise(Vector((x * 0.25, z * 0.25, 2.0))) > -0.1 else PAL['grass2']
    elif y > -0.33:
        c = PAL['soil']
    elif y > SEA + 0.12:
        c = PAL['sand']
    elif y > SEA - 0.25:
        c = PAL['wet']
    else:
        c = PAL['bed']
    return tuple(max(0, min(1, v * (1 + j))) for v in c)


# ---------------------------------------------------------------- terrain grid
GX0, GX1, GZ0, GZ1, STEP = -15.0, 21.0, -14.0, 12.5, 0.32
nx, nz = int((GX1 - GX0) / STEP) + 1, int((GZ1 - GZ0) / STEP) + 1
bm = bmesh.new()
verts = []
for j in range(nz):
    row = []
    for i in range(nx):
        x = GX0 + i * STEP
        z = GZ0 + j * STEP
        d = sd_plateau(x, z)
        # jitter the grid off the plateau so facets read as hand-cut, not as a mesh grid
        if d > 0.05:
            x += rnd.uniform(-0.11, 0.11)
            z += rnd.uniform(-0.11, 0.11)
        y = height(x, z)
        row.append(bm.verts.new(Vector((x, -z, y))))
    verts.append(row)
col_layer = bm.loops.layers.float_color.new('Col')
for j in range(nz - 1):
    for i in range(nx - 1):
        a, b, c, e = verts[j][i], verts[j][i + 1], verts[j + 1][i + 1], verts[j + 1][i]
        # skip deep seabed cells nobody sees
        if max(a.co.z, b.co.z, c.co.z, e.co.z) < -2.6:
            continue
        for tri in ((a, b, c), (a, c, e)) if (i + j) % 2 else ((a, b, e), (b, c, e)):
            f = bm.faces.new(tri[::-1])
            cen = f.calc_center_median()
            x, z, y = cen.x, -cen.y, cen.z
            col = colour(x, z, y, sd_plateau(x, z))
            for loop in f.loops:
                loop[col_layer] = (*col, 1.0)
me = bpy.data.meshes.new('terrain')
bm.to_mesh(me)
bm.free()
terrain = bpy.data.objects.new('terrain', me)
bpy.context.collection.objects.link(terrain)

# ---------------------------------------------------------------- boulders
parts = [terrain]


def boulder(x, z, y, r, squash=0.7, seed=0, mossy=True):
    m = bpy.data.meshes.new('rock')
    b = bmesh.new()
    bmesh.ops.create_icosphere(b, subdivisions=1, radius=1.0)
    k = random.Random(seed)
    sx, sz = k.uniform(0.8, 1.3), k.uniform(0.8, 1.3)
    for v in b.verts:
        n = noise.noise(v.co * 1.7 + Vector((seed, 0, 0)))
        v.co *= 1 + 0.22 * n
        v.co.x *= r * sx
        v.co.y *= r * sz
        v.co.z *= r * squash
    bmesh.ops.rotate(b, verts=b.verts, cent=Vector(), matrix=__import__('mathutils').Matrix.Rotation(k.uniform(0, 6.28), 3, 'Z'))
    cl = b.loops.layers.float_color.new('Col')
    base = PAL['rock'] if k.random() > 0.4 else PAL['rock2']
    for f in b.faces:
        f.normal_update()
        top = mossy and f.normal.z > 0.75 and f.calc_center_median().z > r * squash * 0.4
        c = PAL['moss'] if top else tuple(v * k.uniform(0.9, 1.08) for v in base)
        for loop in f.loops:
            loop[cl] = (*c, 1.0)
    b.to_mesh(m)
    b.free()
    o = bpy.data.objects.new('rock', m)
    o.location = (x, -z, y)
    bpy.context.collection.objects.link(o)
    parts.append(o)
    return o


# back cliff line: big boulders shouldering the cliff, mossy on top
s = 0
for i in range(26):
    t = i / 25
    x = PX0 - 0.4 + t * (PX1 - PX0 + 0.8)
    z = PZ0 - 0.7 + rnd.uniform(-0.3, 0.4)
    r = rnd.uniform(0.9, 1.6)
    boulder(x, z, -0.9 + rnd.uniform(-0.2, 0.5), r, rnd.uniform(0.75, 1.0), seed=s)
    s += 1
# side cliffs where the beach is narrow
for side in (-1, 1):
    for i in range(7):
        z = PZ0 + 0.5 + i * 1.6 + rnd.uniform(-0.3, 0.3)
        x = (PX0 - 0.7) if side < 0 else (PX1 + 0.7)
        boulder(x + rnd.uniform(-0.3, 0.3), z, -1.0 + rnd.uniform(-0.2, 0.3), rnd.uniform(0.7, 1.3), 0.8, seed=s)
        s += 1
# the outcrop: a stack of boulders behind the house at the back left, the island's landmark
for (x, z, y, r) in ((-7.2, -8.4, 0.2, 1.7), (-5.6, -8.9, 0.0, 1.4), (-6.6, -9.4, 1.4, 1.2), (-8.4, -9.0, 0.9, 1.1), (-6.1, -8.1, 1.9, 0.8), (-3.9, -9.2, -0.2, 1.1)):
    boulder(x, z, y, r, 0.95, seed=s)
    s += 1
# shore rocks on the beach and in the shallows, a few, in clusters, never in the boats' lane
for (x, z, r) in ((-9.6, 4.6, 0.55), (-9.1, 5.3, 0.35), (-10.2, 3.6, 0.42), (15.8, 3.9, 0.6), (16.4, 3.0, 0.4), (15.2, 4.8, 0.32), (-4.0, 8.4, 0.3), (12.6, 7.8, 0.36)):
    boulder(x, z, height(x, z) - 0.05, r, 0.7, seed=s, mossy=False)
    s += 1


# ---------------------------------------------------------------- Philippines: a banca on the beach
def banca(x0, z0, yaw_deg=8):
    """An outrigger boat pulled up on the sand: white hull with a blue stripe, raised bow and
    stern, bamboo outriggers on two cross booms."""
    import mathutils
    b = bmesh.new()
    cl = b.loops.layers.float_color.new('Col')
    L, W, D = 4.4, 0.55, 0.42
    n = 14
    rings = []
    for i in range(n + 1):
        t = i / n
        u = 2 * t - 1
        w = W * (1 - u ** 4) ** 0.6 + 0.02
        lift = 0.28 * u ** 6
        xs = -L / 2 + L * t
        ring = [(xs, -w, D + lift), (xs, -w * 0.93, 0.29 + lift * 0.8), (xs, -w * 0.75, 0.12 + lift * 0.4), (xs, 0.0, 0.0 + lift * 0.5), (xs, w * 0.75, 0.12 + lift * 0.4), (xs, w * 0.93, 0.29 + lift * 0.8), (xs, w, D + lift)]
        rings.append([b.verts.new(Vector(p)) for p in ring])
    for a, c in zip(rings, rings[1:]):
        for k in range(6):
            b.faces.new((a[k], a[k + 1], c[k + 1], c[k]))
    for f in b.faces:
        k_ = [v.co.z for v in f.verts]
        zc = sum(k_) / len(k_)
        lo = min(k_)
        col = (0.95, 0.95, 0.93) if lo > 0.28 else (0.12, 0.33, 0.72) if lo > 0.11 else (0.72, 0.2, 0.16)
        for loop in f.loops:
            loop[cl] = (*col, 1.0)
    # seats/thwarts and the outriggers (katig) on two booms
    def bar(c, size, col):
        made = bmesh.ops.create_cube(b, size=1.0)['verts']
        for v in made:
            v.co = Vector((c[0] + v.co.x * size[0], c[1] + v.co.y * size[1], c[2] + v.co.z * size[2]))
        fs = {f for v in made for f in v.link_faces}
        for f in fs:
            for loop in f.loops:
                loop[cl] = (*col, 1.0)
    for xb in (-0.9, 0.9):
        bar((xb, 0, D - 0.02), (0.1, 3.1, 0.07), (0.55, 0.38, 0.22))
    for yb in (-1.5, 1.5):
        bar((0, yb, 0.12), (3.8, 0.12, 0.12), (0.85, 0.72, 0.42))
    bar((0, 0, D - 0.06), (0.25, W * 1.6, 0.04), (0.6, 0.42, 0.25))
    me = bpy.data.meshes.new('banca')
    b.to_mesh(me)
    b.free()
    o = bpy.data.objects.new('banca', me)
    gy = max(height(x0, z0), SEA + 0.05)
    o.location = (x0, -z0, gy - 0.02)
    o.rotation_euler = (0.04, 0.0, math.radians(yaw_deg))
    bpy.context.collection.objects.link(o)
    parts.append(o)


if COUNTRY == 'ph':
    banca(12.4, 6.2, -14)
    # a few coconuts and a log on the sand by the boat
    for (x, z, r) in ((10.6, 6.0, 0.16), (10.8, 6.3, 0.15), (10.45, 6.35, 0.14)):
        boulder(x, z, height(x, z) + 0.08, r, 0.95, seed=900 + int(x * 10), mossy=False)

# ---------------------------------------------------------------- foam: a strip along the waterline
fbm = bmesh.new()
fcl = fbm.loops.layers.float_color.new('Col')
cx, cz = (PX0 + PX1) / 2, (PZ0 + PZ1) / 2
N = 260
inner, outer = [], []
for k in range(N):
    a = k / N * math.tau
    dx, dz = math.cos(a), math.sin(a)
    # march out from the centre until the ground drops below the sea
    r = 4.0
    while r < 30 and height(cx + dx * r, cz + dz * r) > SEA:
        r += 0.05
    w = 0.22 + 0.12 * (noise.noise(Vector((dx * 3, dz * 3, 4.0))) + 0.5)
    inner.append(fbm.verts.new(Vector((cx + dx * (r - 0.12), -(cz + dz * (r - 0.12)), SEA + 0.025))))
    outer.append(fbm.verts.new(Vector((cx + dx * (r + w), -(cz + dz * (r + w)), SEA + 0.02))))
for k in range(N):
    f = fbm.faces.new((inner[k], outer[k], outer[(k + 1) % N], inner[(k + 1) % N])[::-1])
    for loop, alpha in zip(f.loops, (0.95, 0.0, 0.0, 0.95)[::-1]):
        loop[fcl] = (1.0, 1.0, 1.0, alpha)
fm = bpy.data.meshes.new('foam')
fbm.to_mesh(fm)
fbm.free()
foam = bpy.data.objects.new('foam', fm)
bpy.context.collection.objects.link(foam)

# ---------------------------------------------------------------- materials and export
def vc_material(name, alpha=False):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes['Principled BSDF']
    a = nt.nodes.new('ShaderNodeVertexColor')
    a.layer_name = 'Col'
    nt.links.new(a.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.92
    if alpha:
        nt.links.new(a.outputs['Alpha'], bsdf.inputs['Alpha'])
        m.blend_method = 'BLEND' if hasattr(m, 'blend_method') else None
    return m


land = vc_material('island-land')
foam_m = vc_material('island-foam', alpha=True)
bpy.ops.object.select_all(action='DESELECT')
for o in parts:
    o.select_set(True)
bpy.context.view_layer.objects.active = terrain
bpy.ops.object.join()
island = bpy.context.view_layer.objects.active
island.name = 'island'
island.data.materials.append(land)
foam.data.materials.append(foam_m)
for o in (island, foam):
    for p in o.data.polygons:
        p.use_smooth = False
print('[island2]', COUNTRY, 'faces', len(island.data.polygons), 'foam', len(foam.data.polygons))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_yup=True, export_apply=True, export_materials='EXPORT')
print('[island2] wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')
