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
if COUNTRY == 'vn':  # a lakeside lane runs along the front, outside the garden wall
    PZ1 = 7.7
if COUNTRY == 'my':  # room on the west for the condo towers
    PX0 = -15.6
BUILT_FRONT = COUNTRY in ('th', 'vn')  # a straight stone embankment instead of a beach
LANE = (5.0, 7.25)  # Hanoi lane, site z


def hexc(h):
    h = h.lstrip('#')
    return tuple(((int(h[i:i + 2], 16) / 255) ** 2.2) for i in (0, 2, 4))


PAL = {
    'grass': hexc('#7cbf4f'), 'grass2': hexc('#69ad43'), 'soil': hexc('#8a5a34'),
    'sand': hexc('#f1d7a2'), 'wet': hexc('#d9b67c'), 'bed': hexc('#c9a978'),
    'rock': hexc('#c9a26a'), 'rock2': hexc('#a9824f'), 'rockwet': hexc('#7e6446'), 'rocktop': hexc('#dfc08a'), 'moss': hexc('#86bf45'), 'moss2': hexc('#6fa83a'), 'lipdark': hexc('#7a5a3a'), 'foam': (1.0, 1.0, 1.0),
    'asphalt': hexc('#6d6f72'), 'kerb': hexc('#c9c3b6'), 'paint': hexc('#f1e3a8'),
    'paving': hexc('#c9c1b3'), 'paving2': hexc('#bdb4a5'),
    'wall': hexc('#9b7d60'), 'wall2': hexc('#86684e'), 'green': hexc('#4f8f3a'),
}


def sd_plateau(x, z):
    """Signed distance to the plateau outline (negative inside), with a wobbly coast."""
    cx, cz = (PX0 + PX1) / 2, (PZ0 + PZ1) / 2
    hx, hz = (PX1 - PX0) / 2 - PR, (PZ1 - PZ0) / 2 - PR
    qx, qz = abs(x - cx) - hx, abs(z - cz) - hz
    out = math.hypot(max(qx, 0), max(qz, 0)) + min(max(qx, qz), 0) - PR
    # wobble only outward so nothing built ends up over the edge
    wob = max(0.0, noise.noise(Vector((x * 0.16, z * 0.16, 3.0)))) * 0.9
    if BUILT_FRONT:  # a straight, built canal front: no wobble towards the water
        wob *= max(0.0, min(1.0, (2.5 - z) / 2.0))
    return out - wob


def canal_front(x, z):
    """Thailand: the front is a vertical laterite embankment on the khlong instead of a beach."""
    return BUILT_FRONT and z > (PZ0 + PZ1) / 2 + 2.0


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
        far = max(0.0, min(1.0, (-d - 0.0) / 2.5)) * (1.0 if ((x < -6.5 and COUNTRY != 'my') or x > 13.2 or z < -8.2) else 0.0)
        return far * (0.25 + 0.25 * noise.noise(Vector((x * 0.3, z * 0.3, 1.0))))
    if canal_front(x, z):
        return 0.0 if d < 0.04 else -2.3
    w = beach_width(x, z)
    if d < 0.35:  # soil lip
        return -0.32 * (d / 0.35)
    if w < 1.0:  # back: cliff straight down
        return -0.32 - min(1.0, (d - 0.35) / 0.6) * 2.6
    t = (d - 0.35) / w
    if t <= 1.0:  # beach: gentle, slightly convex, crossing the sea about two thirds out
        return -0.36 - 0.9 * t ** 1.15
    return -1.26 - min(3.0, (t - 1.0) * 4.0)


def colour(x, z, y, d):
    j = noise.noise(Vector((x * 0.9, z * 0.9, 5.0))) * 0.05
    if d > 0 and canal_front(x, z) and y > SEA - 0.5:
        band = int((y + 3.0) / 0.22) % 2
        c = PAL['wall'] if band else PAL['wall2']
        if y > -0.12:
            c = PAL['wall2']
    elif d <= 0 and COUNTRY == 'vn' and LANE[0] < z < LANE[1]:
        # asphalt with a worn centre, a kerb line either side
        edge = min(z - LANE[0], LANE[1] - z)
        c = PAL['kerb'] if edge < 0.18 else PAL['asphalt'] if abs(z - (LANE[0] + LANE[1]) / 2) > 0.06 else PAL['paint']
    elif d <= 0 and COUNTRY == 'my' and x < -8.9:
        c = PAL['paving'] if (int((x + 40) / 1.2) + int((z + 40) / 1.2)) % 2 else PAL['paving2']
    elif d <= 0:
        c = PAL['grass'] if noise.noise(Vector((x * 0.25, z * 0.25, 2.0))) > -0.1 else PAL['grass2']
    elif y > -0.33:
        c = PAL['rock2']
    elif y > SEA + 0.12:
        c = PAL['sand']
    elif y > SEA - 0.25:
        c = PAL['wet']
    else:
        c = PAL['bed']
    return tuple(max(0, min(1, v * (1 + j))) for v in c)


# ---------------------------------------------------------------- terrain grid
GX0, GX1, GZ0, GZ1, STEP = (-22.0 if COUNTRY == 'my' else -15.0), 21.0, -14.0, 12.5, 0.32
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
vcol = {}
for j in range(nz - 1):
    for i in range(nx - 1):
        a, b, c, e = verts[j][i], verts[j][i + 1], verts[j + 1][i + 1], verts[j + 1][i]
        # skip deep seabed cells nobody sees
        if max(a.co.z, b.co.z, c.co.z, e.co.z) < -2.6:
            continue
        for tri in ((a, b, c), (a, c, e)) if (i + j) % 2 else ((a, b, e), (b, c, e)):
            f = bm.faces.new(tri[::-1])
            for loop in f.loops:  # colour per corner: soft gradients, no sawtooth bands
                v = loop.vert
                key = v.index if v.index >= 0 else id(v)
                if v not in vcol:
                    vcol[v] = colour(v.co.x, -v.co.y, v.co.z, sd_plateau(v.co.x, -v.co.y))
                loop[col_layer] = (*vcol[v], 1.0)
me = bpy.data.meshes.new('terrain')
bm.to_mesh(me)
bm.free()
terrain = bpy.data.objects.new('terrain', me)
bpy.context.collection.objects.link(terrain)

# ---------------------------------------------------------------- boulders
parts = [terrain]


def rock(x, z, y0, y1, sx, sz, yaw, seed=0, mossy=True, seg=4):
    """A chunky stylised rock: a bevelled block with softened, hand-cut faces. Warm sandstone sides,
    darker and wet at the waterline, a cap of moss on top."""
    import mathutils
    m = bpy.data.meshes.new('rock')
    b = bmesh.new()
    bmesh.ops.create_cube(b, size=1.0)
    k = random.Random(seed)
    h = max(0.2, y1 - y0)
    for v in b.verts:
        v.co = Vector((v.co.x * sx, v.co.y * sz, v.co.z * h))
    bmesh.ops.bevel(b, geom=list(b.edges), offset=min(sx, sz, h) * k.uniform(0.26, 0.4), segments=seg, profile=0.5, affect='EDGES')
    off = Vector((k.uniform(0, 40), k.uniform(0, 40), 0))
    for v in b.verts:
        n = noise.noise(v.co * 0.7 + off)
        v.co += Vector((n * 0.08 * sx, noise.noise(v.co * 0.7 + off + Vector((7, 0, 0))) * 0.08 * sz, 0))
        if v.co.z > 0:  # tops slump a little, so rows do not read as bricks
            v.co.z += noise.noise(v.co * 0.5 + off) * 0.14 * h
    bmesh.ops.rotate(b, verts=b.verts, cent=Vector(), matrix=mathutils.Matrix.Rotation(yaw, 3, 'Z'))
    bmesh.ops.translate(b, verts=b.verts, vec=Vector((x, -z, (y0 + y1) / 2)))
    b.normal_update()
    cl = b.loops.layers.float_color.new('Col')
    tone = k.uniform(0.92, 1.06)
    top_y = max(v.co.z for v in b.verts)
    def mixc(c0, c1, t):
        t = max(0.0, min(1.0, t))
        return tuple(a_ + (b_ - a_) * t for a_, b_ in zip(c0, c1))
    for f in b.faces:
        for loop in f.loops:
            v = loop.vert
            yv, nz = v.co.z, v.normal.z
            c = mixc(PAL['rock2'], PAL['rock'], (yv - y0) / h)              # darker toward the foot
            c = mixc(c, PAL['rocktop'], (nz - 0.3) * 1.6)                  # sunlit upper faces
            c = mixc(PAL['rockwet'], c, (yv - (SEA - 0.05)) / 0.3)          # wet band at the waterline
            if mossy:
                c = mixc(c, PAL['moss'], (nz - 0.55) * 4.0 * (1.0 if yv > top_y - h * 0.35 else 0.0))
            c = tuple(min(1, ch * tone) for ch in c)
            loop[cl] = (*c, 1.0)
    b.to_mesh(m)
    b.free()
    o = bpy.data.objects.new('rock', m)
    bpy.context.collection.objects.link(o)
    parts.append(o)
    return o


def boulder(x, z, y, r, squash=0.7, seed=0, mossy=True):
    k = random.Random(seed + 500)
    return rock(x, z, y - r * squash, y + r * squash, r * k.uniform(1.4, 1.9), r * k.uniform(1.3, 1.8), k.uniform(0, 6.28), seed, mossy)


# the plinth: a ring of chunky rocks all round the plateau (two rows, the outer one lower and wet),
# except where the beach runs into the water and, in Thailand, along the built canal front
cxp, czp = (PX0 + PX1) / 2, (PZ0 + PZ1) / 2
s = 0
def edge_at(a):
    dx, dz = math.cos(a), math.sin(a)
    r = 2.0
    while sd_plateau(cxp + dx * r, czp + dz * r) < 0:
        r += 0.02
    return r, dx, dz
a = 0.0
while a < math.tau:
    r, dx, dz = edge_at(a)
    x, z = cxp + dx * r, czp + dz * r
    beachy = beach_width(x, z) > 1.7
    if not (canal_front(x, z) or beachy):
        w = rnd.choice((rnd.uniform(0.8, 1.2), rnd.uniform(1.3, 2.2)))
        back = z < czp - 3
        top = rnd.uniform(-0.2, 0.1) + (rnd.uniform(0.2, 0.8) if back and rnd.random() > 0.5 else 0.0) + (0.25 if w > 1.6 else 0.0)
        rock(x + dx * 0.25, z + dz * 0.25, SEA - 0.9, top, w, w * rnd.uniform(0.55, 0.85), math.atan2(dx, dz) + rnd.uniform(-0.4, 0.4), seed=s)
        if rnd.random() > 0.6:  # a pebble or two tucked in front
            pr = rnd.uniform(0.18, 0.32)
            rock(x + dx * 1.2 + rnd.uniform(-0.4, 0.4), z + dz * 1.2 + rnd.uniform(-0.4, 0.4), SEA - 0.3, SEA + pr, pr * 2, pr * 1.7, rnd.uniform(0, 6.28), seed=s + 7000, mossy=False)
        s += 1
        if rnd.random() > 0.25:
            w2 = rnd.uniform(0.6, 1.1)
            rock(x + dx * (1.05 + rnd.uniform(0, 0.3)), z + dz * (1.05 + rnd.uniform(0, 0.3)), SEA - 0.8, SEA + rnd.uniform(0.15, 0.6), w2, w2 * rnd.uniform(0.8, 1.1), rnd.uniform(0, 6.28), seed=s, mossy=rnd.random() > 0.5)
            s += 1
    elif beachy and rnd.random() > 0.8:
        rr = rnd.uniform(0.25, 0.45)
        boulder(x + dx * 1.6, z + dz * 1.6, height(x + dx * 1.6, z + dz * 1.6) + rr * 0.3, rr, 0.7, seed=s, mossy=False)
        s += 1
    a += (0.75 + w * 0.45) / max(r, 4.0) * rnd.uniform(0.85, 1.05) if not (canal_front(x, z) or beachy) else 1.0 / max(r, 4.0)
# the outcrop: a stack of boulders behind the house at the back left, the island's landmark
for (x, z, y, r) in ((-7.2, -8.4, 0.2, 1.7), (-5.6, -8.9, 0.0, 1.4), (-6.6, -9.4, 1.4, 1.2), (-8.4, -9.0, 0.9, 1.1), (-6.1, -8.1, 1.9, 0.8), (-3.9, -9.2, -0.2, 1.1)):
    if COUNTRY == 'my' and x < -6.0:
        continue  # the tower plaza takes this corner
    boulder(x, z, y, r * 0.8, 0.85, seed=s)
    s += 1
# shore rocks on the beach and in the shallows, a few, in clusters, never in the boats' lane
for (x, z, r) in ((-9.6, 4.6, 0.55), (-9.1, 5.3, 0.35), (-10.2, 3.6, 0.42), (15.8, 3.9, 0.6), (16.4, 3.0, 0.4), (15.2, 4.8, 0.32), (-4.0, 8.4, 0.3), (12.6, 7.8, 0.36)):
    if COUNTRY == 'my' and x < -8:
        continue
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

# ---------------------------------------------------------------- Thailand: the canal embankment
if BUILT_FRONT:
    # one mesh for the embankment strip
    fb = bmesh.new()
    fcl_ = fb.loops.layers.float_color.new('Col')
    def fbox(x0, x1, y0, y1, z0, z1, col):
        made = bmesh.ops.create_cube(fb, size=1.0)['verts']
        for v in made:
            v.co = Vector(((x0 + x1) / 2 + v.co.x * (x1 - x0), -((z0 + z1) / 2 + v.co.y * (z1 - z0)), (y0 + y1) / 2 + v.co.z * (y1 - y0)))
        for f in {f for v in made for f in v.link_faces}:
            for loop in f.loops:
                loop[fcl_] = (*col, 1.0)
    # the embankment on our side: a coping strip and a battered laterite face along the canal front
    cx_, cz_ = (PX0 + PX1) / 2, (PZ0 + PZ1) / 2
    edge = []
    for k in range(400):
        a = math.pi * (0.03 + 0.94 * k / 399)  # south half, sweeping east to west
        dx, dz = math.cos(a), math.sin(a)
        r = 2.0
        while height(cx_ + dx * r, cz_ + dz * r) > -0.01:
            r += 0.01
        x, z = cx_ + dx * r, cz_ + dz * r
        if canal_front(x, z):
            edge.append((x, z, dx, dz))
    ring = []
    for (x, z, dx, dz) in edge:
        ring.append([fb.verts.new(Vector((x - dx * 0.4, -(z - dz * 0.4), 0.06))), fb.verts.new(Vector((x + dx * 0.4, -(z + dz * 0.4), 0.06))), fb.verts.new(Vector((x + dx * 0.5, -(z + dz * 0.5), SEA - 1.4)))])
    for i_, (x, z, dx, dz) in enumerate(edge[::5]):
        for (y0_, y1_) in ((SEA - 0.7, -0.5), (-0.52, -0.02)):
            rock(x + dx * 0.55, z + dz * 0.55, y0_, y1_, 0.62, 0.42, math.atan2(dx, dz) + random.Random(i_).uniform(-0.05, 0.05), seed=9000 + i_ * 2 + (y0_ > -1), mossy=False, seg=2)
    for A, B in zip(ring, ring[1:]):
        for (i, col) in ((0, PAL['wall2']), (1, PAL['wall'])):
            f = fb.faces.new((A[i], A[i + 1], B[i + 1], B[i]))
            for loop in f.loops:
                loop[fcl_] = (*col, 1.0)
    bmesh.ops.recalc_face_normals(fb, faces=fb.faces)
    fm_ = bpy.data.meshes.new('farbank')
    fb.to_mesh(fm_)
    fb.free()
    o = bpy.data.objects.new('farbank', fm_)
    bpy.context.collection.objects.link(o)
    parts.append(o)

# ---------------------------------------------------------------- the grass lip
# a smooth, rounded edge where the lawn rolls over onto the sand or the rocks (hides the grid's
# sawtooth), grass on top shading to warm earth underneath
lb = bmesh.new()
lcl = lb.loops.layers.float_color.new('Col')
prof = [(-0.35, 0.012, 'grass'), (-0.05, 0.03, 'grass'), (0.08, 0.0, 'grass2'), (0.14, -0.1, 'grass2'), (0.12, -0.2, 'lipdark'), (0.2, -0.34, 'rock2'), (0.42, -0.42, 'rock2')]
cxl, czl = (PX0 + PX1) / 2, (PZ0 + PZ1) / 2
rows = []
N_ = 520
for k in range(N_):
    a = k / N_ * math.tau
    dx, dz = math.cos(a), math.sin(a)
    r = 2.0
    while sd_plateau(cxl + dx * r, czl + dz * r) < 0:
        r += 0.01
    x, z = cxl + dx * r, czl + dz * r
    rows.append(None if canal_front(x, z) else [lb.verts.new(Vector((x + dx * o, -(z + dz * o), y))) for (o, y, _) in prof])
for k in range(N_):
    A, B = rows[k], rows[(k + 1) % N_]
    if A is None or B is None:
        continue
    for i in range(len(prof) - 1):
        f = lb.faces.new((A[i], A[i + 1], B[i + 1], B[i]))
        for loop in f.loops:
            j = A.index(loop.vert) if loop.vert in A else B.index(loop.vert)
            loop[lcl] = (*PAL[prof[j][2]], 1.0)
bmesh.ops.recalc_face_normals(lb, faces=lb.faces)
for f in lb.faces:
    if f.normal.z < -0.2 and f.calc_center_median().z > -0.05:
        f.normal_flip()
lme = bpy.data.meshes.new('lip')
lb.to_mesh(lme)
lb.free()
lip = bpy.data.objects.new('lip', lme)
bpy.context.collection.objects.link(lip)
parts.append(lip)

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
    bm_ = bmesh.new()
    bm_.from_mesh(o.data)
    for f in bm_.faces:
        f.smooth = True
    for e in bm_.edges:  # soft everywhere, crisp only at real corners
        e.smooth = not (len(e.link_faces) == 2 and e.calc_face_angle(0) > math.radians(55))
    bm_.to_mesh(o.data)
    bm_.free()
print('[island2]', COUNTRY, 'faces', len(island.data.polygons), 'foam', len(foam.data.polygons))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_yup=True, export_apply=True, export_materials='EXPORT')
print('[island2] wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')
