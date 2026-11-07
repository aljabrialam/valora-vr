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


TRUNK = material('trunk', '#9b6a3f', 0.85)
LEAF = material('leaf', '#3fa34d', 0.45)
LEAF2 = material('leaf-light', '#6cc04a', 0.5)
BLOOM = material('bougainvillea', '#e8458f', 0.6)
SHRUB = material('shrub', '#4f9a3a', 0.8)


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
    parts = []
    # trunk: a curve of slightly bulging rings, like a real palm, thicker at the base
    bm = bmesh.new()
    seg, ring = 22, 12
    rings = []
    for i in range(seg + 1):
        t = i / seg
        c = Vector((lean[0] * t ** 1.8, lean[1] * t ** 1.8, t * 0.9))
        r = 0.032 * (1 - 0.4 * t) * (1.08 if i % 2 == 0 else 0.95)
        if i == 0:
            r *= 1.5
        rings.append([bm.verts.new(c + Vector((math.cos(a) * r, math.sin(a) * r, 0))) for a in [k * 2 * math.pi / ring for k in range(ring)]])
    for a, b in zip(rings, rings[1:]):
        for k in range(ring):
            bm.faces.new((a[k], a[(k + 1) % ring], b[(k + 1) % ring], b[k]))
    parts.append(obj(name + '-trunk', bm, TRUNK))
    top = Vector((lean[0], lean[1], 0.9))
    # fronds: a midrib that rises and arches down, with leaflets either side (one mesh per frond)
    bm = bmesh.new()
    for f in range(fronds):
        az = f / fronds * 2 * math.pi + rnd.uniform(-0.15, 0.15)
        length = rnd.uniform(0.42, 0.55)
        lift = rnd.uniform(0.08, 0.2)
        d = Vector((math.cos(az), math.sin(az), 0))
        side = Vector((-d.y, d.x, 0))
        n = 14
        spine = [top + d * (length * t) + Vector((0, 0, lift * math.sin(math.pi * t * 0.7) - 0.3 * t * t)) for t in [i / n for i in range(n + 1)]]
        for i in range(1, n):
            t = i / n
            w = 0.13 * math.sin(math.pi * t) + 0.02
            for s in (-1, 1):
                a = bm.verts.new(spine[i])
                b = bm.verts.new(spine[i + 1])
                tip = spine[i] + side * s * w + d * 0.04 + Vector((0, 0, -0.05 * t - 0.02))
                c = bm.verts.new(tip)
                bm.faces.new((a, b, c) if s > 0 else (b, a, c))
    parts.append(obj(name + '-fronds', bm, LEAF))
    # coconuts
    bm = bmesh.new()
    for k in range(3):
        a = k * 2.1
        bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=7, radius=0.028, matrix=Matrix.Translation(top + Vector((math.cos(a) * 0.035, math.sin(a) * 0.035, -0.04))))
    parts.append(obj(name + '-nuts', bm, TRUNK))
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
        v.co += v.normal * noise.noise(v.co * 4 + Vector((seed, 0, 0))) * 0.06
        v.co.z = max(v.co.z, 0.02)
    dec = out.modifiers.new('dec', 'DECIMATE')
    dec.ratio = 0.3
    bpy.context.view_layer.objects.active = out
    out.select_set(True)
    bpy.ops.object.modifier_apply(modifier='dec')
    out.select_set(False)
    k = 1 / max(max(abs(v.co.x), abs(v.co.y)) for v in me.vertices)
    for v in me.vertices:
        v.co *= k
    for p in me.polygons:
        p.use_smooth = False  # faceted leaves catch the light
    me.materials.append(mat)
    parts = [out]
    if flowers:
        # flower clusters sitting on the surface
        bm = bmesh.new()
        surf = [v.co.copy() for v in me.vertices if v.co.z > 0.25]
        for i in range(flowers):
            p = rnd.choice(surf)
            bmesh.ops.create_icosphere(bm, subdivisions=1, radius=rnd.uniform(0.07, 0.12), matrix=Matrix.Translation(p * 1.02))
        parts.append(obj(name + '-flowers', bm, BLOOM, smooth=False))
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
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_yup=True, export_apply=True, export_materials='EXPORT')
print('[trees] wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')
