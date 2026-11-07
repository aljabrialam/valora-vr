# The floating island for VaLora: Two Watchers (sunny floating-island art direction).
#   /home/claude/bpy-env/bin/python art/blender/island.py
# A rounded grass top the size of the old site board (site metres, x -9..15.4, z -8.6..5.8),
# a grass lip, then strata of earth and rock tapering to a craggy point with a few hanging roots
# and stalactites. Flat-shaded rock facets, soft grass. Exported with vertex colours.
# Output: public/models/valora-island.glb

import math, os, random
import bpy, bmesh
from mathutils import Vector, noise

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'public', 'models', 'valora-island.glb')
rnd = random.Random(4)
bpy.ops.wm.read_factory_settings(use_empty=True)

X0, X1, Z0, Z1 = -9.0, 15.4, -8.6, 5.8
CX, CZ = (X0 + X1) / 2, (Z0 + Z1) / 2
HW, HD = (X1 - X0) / 2, (Z1 - Z0) / 2
N = 160


def rounded_rect(hw, hd, r, n):
    """Points around a rounded rectangle, counter-clockwise, as (x, z, outward normal)."""
    pts = []
    straight_x, straight_z = 2 * (hw - r), 2 * (hd - r)
    per = 2 * straight_x + 2 * straight_z + 2 * math.pi * r
    for i in range(n):
        s = i / n * per
        segs = [
            (straight_x, lambda t: (-hw + r + t, -hd, 0, -1)),
            (math.pi * r / 2, lambda t: (hw - r + r * math.sin(t / r), -hd + r - r * math.cos(t / r), math.sin(t / r), -math.cos(t / r))),
            (straight_z, lambda t: (hw, -hd + r + t, 1, 0)),
            (math.pi * r / 2, lambda t: (hw - r + r * math.cos(t / r), hd - r + r * math.sin(t / r), math.cos(t / r), math.sin(t / r))),
            (straight_x, lambda t: (hw - r - t, hd, 0, 1)),
            (math.pi * r / 2, lambda t: (-hw + r - r * math.sin(t / r), hd - r + r * math.cos(t / r), -math.sin(t / r), math.cos(t / r))),
            (straight_z, lambda t: (-hw, hd - r - t, -1, 0)),
            (math.pi * r / 2, lambda t: (-hw + r - r * math.cos(t / r), -hd + r - r * math.sin(t / r), -math.cos(t / r), -math.sin(t / r))),
        ]
        for length, f in segs:
            if s <= length:
                x, z, nx, nz = f(s)
                pts.append((x + CX, z + CZ, nx, nz))
                break
            s -= length
    return pts


BASE = rounded_rect(HW, HD, 2.6, N)

# strata: (inset from the edge, height, noise amplitude, colour) from the top down
STRATA = [
    (-0.15, 0.0, 0.05, (0.38, 0.66, 0.24)),   # grass top edge, slightly proud
    (-0.25, -0.35, 0.12, (0.33, 0.58, 0.20)),  # grass lip
    (0.05, -0.75, 0.25, (0.55, 0.36, 0.21)),   # topsoil
    (0.6, -2.0, 0.55, (0.47, 0.30, 0.18)),     # earth
    (1.6, -3.6, 0.9, (0.55, 0.52, 0.49)),      # rock
    (3.4, -5.4, 1.1, (0.47, 0.45, 0.43)),      # rock
    (6.0, -7.4, 1.0, (0.40, 0.38, 0.37)),      # rock
]


def ring(inset, y, amp, seed):
    out = []
    for i, (x, z, nx, nz) in enumerate(BASE):
        # pull towards the centre by `inset`, then wobble the edge with noise
        n = noise.noise(Vector((x * 0.18, z * 0.18, seed))) * amp
        k = inset + n
        px, pz = x - nx * k, z - nz * k
        # shrink the deeper rings towards the middle as well as inwards
        if inset > 1:
            f = min(0.75, inset / 10)
            px = px + (CX - px) * f * 0.6
            pz = pz + (CZ - pz) * f * 0.6
        py = y + noise.noise(Vector((x * 0.3, z * 0.3, seed + 7))) * amp * 0.6
        out.append(Vector((px, -pz, py)))  # site (x, z, y) -> Blender (x, -z, y)
    return out


me = bpy.data.meshes.new('island')
bm = bmesh.new()
col = bm.loops.layers.color.new('Col')
rings = [[bm.verts.new(v) for v in ring(inset, y, amp, i * 3.1)] for i, (inset, y, amp, _) in enumerate(STRATA)]


def paint(face, c, jitter=0.05):
    j = 1 + rnd.uniform(-jitter, jitter)
    for loop in face.loops:
        loop[col] = (min(1, c[0] * j), min(1, c[1] * j), min(1, c[2] * j), 1)


# the grass top: a cap over the first ring
top = bm.faces.new(rings[0])
paint(top, STRATA[0][3], 0)
# the sides between strata
for r in range(len(rings) - 1):
    a, b = rings[r], rings[r + 1]
    for i in range(N):
        f = bm.faces.new((a[i], a[(i + 1) % N], b[(i + 1) % N], b[i]))
        paint(f, STRATA[r + 1][3] if r > 0 else STRATA[1][3])
# the craggy underside: a fan to a few points rather than one cone
tip = bm.verts.new(Vector((CX + 1.5, -CZ, -10.5)))
last = rings[-1]
for i in range(N):
    f = bm.faces.new((last[i], last[(i + 1) % N], tip))
    paint(f, (0.36, 0.34, 0.33))
bmesh.ops.triangulate(bm, faces=[top])
bm.normal_update()
bm.to_mesh(me)
bm.free()
island = bpy.data.objects.new('island', me)
bpy.context.collection.objects.link(island)

# stalactites and hanging rocks under the island
def cone(name, x, z, y, r, h, c):
    m = bpy.data.meshes.new(name)
    b = bmesh.new()
    cl = b.loops.layers.color.new('Col')
    bmesh.ops.create_cone(b, cap_ends=True, segments=7, radius1=r, radius2=0.05, depth=h)
    for v in b.verts:
        v.co.z = -v.co.z  # point down
        v.co += Vector((rnd.uniform(-0.1, 0.1), rnd.uniform(-0.1, 0.1), 0)) * r
    for f in b.faces:
        j = 1 + rnd.uniform(-0.06, 0.06)
        for l in f.loops:
            l[cl] = (c[0] * j, c[1] * j, c[2] * j, 1)
    b.to_mesh(m)
    b.free()
    o = bpy.data.objects.new(name, m)
    o.location = (x, -z, y - h / 2)
    bpy.context.collection.objects.link(o)
    return o


parts = [island]
for i in range(9):
    a = rnd.uniform(0, 2 * math.pi)
    d = rnd.uniform(2, 7)
    parts.append(cone(f'stal{i}', CX + math.cos(a) * d * 1.4, CZ + math.sin(a) * d * 0.8, rnd.uniform(-6.5, -4.5), rnd.uniform(0.5, 1.2), rnd.uniform(1.5, 3.5), (0.42, 0.40, 0.38)))
# roots: thin dark tubes hanging from the earth layer
for i in range(10):
    x, z, nx, nz = BASE[rnd.randrange(N)]
    parts.append(cone(f'root{i}', x - nx * 0.6, z - nz * 0.6, -1.2, 0.08, rnd.uniform(1.0, 2.6), (0.33, 0.22, 0.13)))

bpy.ops.object.select_all(action='DESELECT')
for p in parts:
    p.select_set(True)
bpy.context.view_layer.objects.active = island
bpy.ops.object.join()
island = bpy.context.view_layer.objects.active

mat = bpy.data.materials.new('island')
mat.use_nodes = True
nt = mat.node_tree
bsdf = nt.nodes['Principled BSDF']
vc = nt.nodes.new('ShaderNodeVertexColor')
vc.layer_name = 'Col'
nt.links.new(vc.outputs['Color'], bsdf.inputs['Base Color'])
bsdf.inputs['Roughness'].default_value = 0.95
island.data.materials.append(mat)
for p in island.data.polygons:
    p.use_smooth = False  # faceted, stylised rock
print('[island] faces', len(island.data.polygons))
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=False, export_yup=True, export_apply=True, export_materials='EXPORT')
print('[island] wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')
