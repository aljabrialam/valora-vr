# Stylised tropical planting for VaLora: Two Watchers (sunny floating-island art direction).
#   /home/claude/bpy-env/bin/python art/blender/trees.py
# Palms with a ringed, curving trunk and glossy arching fronds cut into leaflets; a banana plant
# with big paddle leaves; bougainvillea bushes in magenta; round shrubs. Unit size at the origin
# (palm height 1, shrub radius 1); the game places and scales them. Scenery only.
# Output: public/models/valora-trees.glb with nodes palm-a, palm-b, shrub-a, shrub-b, shrub-c.

import math, os, random
import bpy, bmesh
from mathutils import Vector, Matrix, noise

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'public', 'models', 'valora-trees.glb')
rnd = random.Random(5)
bpy.ops.wm.read_factory_settings(use_empty=True)


def S(h):
    h = h.lstrip('#')
    return tuple(((int(h[i:i + 2], 16) / 255) ** 2.2) for i in (0, 2, 4))


def material(name, hexcol, rough, flat=False):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*S(hexcol), 1)
    b.inputs['Roughness'].default_value = rough
    return m


TRUNK = material('trunk', '#b08456', 0.85)
LEAF = material('leaf', '#4caf4a', 0.55)
LEAF2 = material('leaf-light', '#6cc04a', 0.5)
BLOOM = material('bougainvillea', '#e8458f', 0.6)
SHRUB = material('shrub', '#4f9a3a', 0.8)
NUT = material('nut', '#7a5a2a', 0.6)


def obj(name, bm, mat, smooth=True):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    for p in me.polygons:
        p.use_smooth = smooth
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    return o


def join(objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active
    o.name = o.data.name = name
    o.select_set(False)
    return o


def palm(name, lean, fronds):
    """A storybook palm: a curving trunk of stacked, flared rings and broad, drooping fronds with
    a folded midrib and notched edges, shaded dark at the heart to light at the tips."""
    parts = []
    bm = bmesh.new()
    cl = bm.loops.layers.color.new('Col')
    seg, sides = 11, 14
    def centre(t):
        return Vector((lean[0] * t ** 1.7, lean[1] * t ** 1.7, t * 0.9))
    for i in range(seg):
        t0, t1 = i / seg, (i + 1) / seg
        r = 0.05 * (1 - 0.45 * t0) * (1.25 if i == 0 else 1.0)
        lo = [bm.verts.new(centre(t0) + Vector((math.cos(a) * r * 0.86, math.sin(a) * r * 0.86, 0))) for a in [k * 2 * math.pi / sides for k in range(sides)]]
        mid = [bm.verts.new(centre(t0 + (t1 - t0) * 0.8) + Vector((math.cos(a) * r * 1.08, math.sin(a) * r * 1.08, 0))) for a in [k * 2 * math.pi / sides for k in range(sides)]]
        hi = [bm.verts.new(centre(t1) + Vector((math.cos(a) * r * 0.9, math.sin(a) * r * 0.9, 0))) for a in [k * 2 * math.pi / sides for k in range(sides)]]
        for (A, B, ca, cb) in ((lo, mid, 0.72, 0.95), (mid, hi, 0.95, 0.7)):
            for k in range(sides):
                f = bm.faces.new((A[k], A[(k + 1) % sides], B[(k + 1) % sides], B[k]))
                for loop in f.loops:
                    c = ca if loop.vert in A else cb
                    loop[cl] = (c, c, c, 1)
    parts.append(obj(name + '-trunk', bm, TRUNK))
    top = centre(1.0) + Vector((0, 0, 0.01))
    bm = bmesh.new()
    cl = bm.loops.layers.color.new('Col')
    for f in range(fronds):
        az = f / fronds * 2 * math.pi + rnd.uniform(-0.2, 0.2)
        length = rnd.uniform(0.5, 0.64)
        lift = rnd.uniform(0.1, 0.2)
        droop = rnd.uniform(0.3, 0.42)
        d = Vector((math.cos(az), math.sin(az), 0))
        side = Vector((-d.y, d.x, 0))
        n = 16
        rows = []
        for i in range(n + 1):
            t = i / n
            p = top + d * (length * t) + Vector((0, 0, lift * math.sin(math.pi * t * 0.75) - droop * t * t))
            w = 0.16 * math.sin(math.pi * min(1, t * 1.08) ** 0.85) + 0.012
            if i % 2 == 1 and 0.15 < t < 0.95:
                w *= 0.72  # notches: the leaflets split at the edge
            fold = Vector((0, 0, 0.035 * math.sin(math.pi * t)))
            rows.append((bm.verts.new(p + side * w - fold * 0.6 + Vector((0, 0, -0.03 * t))), bm.verts.new(p + fold), bm.verts.new(p - side * w - fold * 0.6 + Vector((0, 0, -0.03 * t))), t))
        for (A, B) in zip(rows, rows[1:]):
            for (u, v) in ((0, 1), (1, 2)):
                face = bm.faces.new((A[u], A[v], B[v], B[u]))
                for loop in face.loops:
                    t = A[3] if loop.vert in A[:3] else B[3]
                    edge = loop.vert in (A[0], A[2], B[0], B[2])
                    c = (0.55 + 0.6 * t, 0.75 + 0.35 * t, 0.55 + 0.25 * t)
                    if edge:
                        c = tuple(min(1.25, ch * 1.08) for ch in c)
                    loop[cl] = (*c, 1)
    parts.append(obj(name + '-fronds', bm, LEAF))
    bm = bmesh.new()
    for k in range(4):
        a = k * 1.6
        bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=0.032, matrix=Matrix.Translation(top + Vector((math.cos(a) * 0.045, math.sin(a) * 0.045, -0.05))))
    parts.append(obj(name + '-nuts', bm, NUT))
    return join(parts, name)


def blob(name, blobs, flat, mat, flowers=None, seed=0):
    """A soft clump: a metaball of overlapping balls converted to a mesh, radius 1."""
    mb = bpy.data.metaballs.new(name + '-mb')
    mb.resolution = 0.1
    mb.threshold = 0.6
    pts = []
    for i in range(blobs):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(0, 0.5)
        el = mb.elements.new()
        el.co = (math.cos(a) * r, math.sin(a) * r, rnd.uniform(0.3, 0.6) * flat)
        el.radius = rnd.uniform(0.38, 0.52)
        pts.append(el.co.copy())
    ob = bpy.data.objects.new(name + '-mbo', mb)
    bpy.context.collection.objects.link(ob)
    bpy.context.view_layer.update()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(ob)
    out = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(out)
    for v in me.vertices:
        v.co += v.normal * noise.noise(v.co * 2.5 + Vector((seed, 0, 0))) * 0.04
        v.co.z = max(v.co.z, 0.02)
    dec = out.modifiers.new('dec', 'DECIMATE')
    dec.ratio = 0.6
    bpy.context.view_layer.objects.active = out
    out.select_set(True)
    bpy.ops.object.modifier_apply(modifier='dec')
    out.select_set(False)
    k = 1 / max(max(abs(v.co.x), abs(v.co.y)) for v in me.vertices)
    for v in me.vertices:
        v.co *= k
    for p in me.polygons:
        p.use_smooth = True  # soft, rounded clumps
    me.materials.append(mat)
    parts = [out]
    if flowers:
        # flower clusters sitting on the surface
        bm = bmesh.new()
        surf = [v.co.copy() for v in me.vertices if v.co.z > 0.25]
        for i in range(flowers):
            p = rnd.choice(surf)
            bmesh.ops.create_icosphere(bm, subdivisions=2, radius=rnd.uniform(0.07, 0.12), matrix=Matrix.Translation(p * 1.02))
        parts.append(obj(name + '-flowers', bm, BLOOM, smooth=True))
        return join(parts, name)
    return out


made = [
    palm('palm-a', (0.12, 0.03), 9),
    palm('palm-b', (-0.08, 0.1), 8),
    blob('shrub-a', 7, 0.8, SHRUB, flowers=0),
    blob('shrub-b', 5, 1.0, LEAF2, flowers=0),
    blob('shrub-c', 9, 0.7, SHRUB, flowers=22, seed=3),
]
for i, o in enumerate(made):
    o.location = (i * 3.0, 0, 0)
for o in made:
    print('[trees]', o.name, len(o.data.polygons), 'faces')
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_yup=True, export_apply=True, export_materials='EXPORT', export_vertex_color='ACTIVE')
print('[trees] wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')
