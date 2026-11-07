# Model-maker's trees for VaLora: Two Watchers, built headless in Blender.
#   /home/claude/bpy-env/bin/python art/blender/trees.py
# Style: an architect's study model. Palms are a basswood dowel with a crown of thin bent card
# fronds; shrubs are clumps of sage foam. Every piece is unit size at the origin (palm height 1,
# shrub radius 1); the game places and scales them. Plants are scenery only: the watcher checks
# never see them. Output: public/models/valora-trees.glb with nodes palm-a, palm-b, shrub-a,
# shrub-b, shrub-c.

import math, os, random
import bpy, bmesh
from mathutils import Vector, Matrix

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'public', 'models', 'valora-trees.glb')
rnd = random.Random(5)

bpy.ops.wm.read_factory_settings(use_empty=True)


def material(name, colour, rough):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*colour, 1)
    b.inputs['Roughness'].default_value = rough
    m.use_backface_culling = False
    return m


# linear values (glTF base colour is linear): basswood #b89a74, sage card #7f8c6c, sage foam #8e9a7c
DOWEL = material('basswood-dowel', (0.48, 0.33, 0.18), 0.7)
CARD = material('sage-card', (0.21, 0.26, 0.15), 0.85)
FOAM = material('sage-foam', (0.27, 0.32, 0.20), 0.95)


def finish(bm, name, mat):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return ob


def palm(name, lean, fronds):
    """Blender z is up here; glTF export turns it to y-up. Height 1."""
    parts = []
    # trunk: a tapered dowel along a gentle curve, with faint growth rings
    bm = bmesh.new()
    seg, ring = 18, 10
    pts = []
    for i in range(seg + 1):
        t = i / seg
        x = lean[0] * (t ** 1.6)
        y = lean[1] * (t ** 1.6)
        pts.append(Vector((x, y, t * 0.94)))
    rings = []
    for i, p in enumerate(pts):
        t = i / seg
        r = 0.022 * (1 - 0.35 * t) * (0.94 if i % 3 == 1 else 1.0)
        nxt = pts[min(i + 1, seg)] - pts[max(i - 1, 0)]
        nxt.normalize()
        side = nxt.cross(Vector((0, 0, 1)) if abs(nxt.z) < 0.99 else Vector((1, 0, 0))).normalized() if abs(nxt.z) < 0.99 else Vector((1, 0, 0))
        up = nxt.cross(side).normalized()
        rings.append([bm.verts.new(p + (side * math.cos(a) + up * math.sin(a)) * r) for a in [k * 2 * math.pi / ring for k in range(ring)]])
    for a, b in zip(rings, rings[1:]):
        for k in range(ring):
            bm.faces.new((a[k], a[(k + 1) % ring], b[(k + 1) % ring], b[k]))
    bm.faces.new(rings[-1][::-1])
    parts.append(finish(bm, name + '-trunk', DOWEL))
    top = pts[-1]
    # crown: thin card fronds, each a tapered strip that rises then droops, slightly twisted
    bm = bmesh.new()
    for f in range(fronds):
        az = f / fronds * 2 * math.pi + rnd.uniform(-0.2, 0.2)
        length = rnd.uniform(0.34, 0.44)
        rise = rnd.uniform(0.05, 0.12)
        d = Vector((math.cos(az), math.sin(az), 0))
        side = Vector((-d.y, d.x, 0))
        n = 10
        left, right = [], []
        for i in range(n + 1):
            t = i / n
            w = 0.045 * math.sin(math.pi * min(1, t * 1.15)) + 0.004
            centre = top + d * (length * t) + Vector((0, 0, rise * math.sin(math.pi * t * 0.8) - 0.22 * t * t))
            twist = Vector((0, 0, 0.012 * t))
            left.append(bm.verts.new(centre + side * w + twist))
            right.append(bm.verts.new(centre - side * w - twist))
        for i in range(n):
            bm.faces.new((left[i], right[i], right[i + 1], left[i + 1]))
    parts.append(finish(bm, name + '-crown', CARD))
    # a small cluster of seed balls under the crown, as model makers add for scale
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=0.03, matrix=Matrix.Translation(top + Vector((0, 0, -0.03))))
    parts.append(finish(bm, name + '-seed', DOWEL))
    return join(parts, name)


def shrub(name, blobs, flat=0.75):
    """Sage foam clump: a metaball of overlapping balls, converted to a smooth mesh. Radius 1."""
    mb = bpy.data.metaballs.new(name + '-mb')
    mb.resolution = 0.12
    mb.threshold = 0.6
    for i in range(blobs):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(0, 0.55)
        el = mb.elements.new()
        el.co = (math.cos(a) * r, math.sin(a) * r, rnd.uniform(0.25, 0.55) * flat)
        el.radius = rnd.uniform(0.38, 0.55)
    ob = bpy.data.objects.new(name + '-mbo', mb)
    bpy.context.collection.objects.link(ob)
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(deps))
    bpy.data.objects.remove(ob)
    out = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(out)
    # foam texture: jitter the surface a little so it is not a perfect blob, then flatten the base
    for v in me.vertices:
        v.co += v.normal * rnd.uniform(-0.025, 0.025)
        if v.co.z < 0.02:
            v.co.z = 0.02
    dec = out.modifiers.new('dec', 'DECIMATE')
    dec.ratio = 0.35
    bpy.context.view_layer.objects.active = out
    out.select_set(True)
    bpy.ops.object.modifier_apply(modifier='dec')
    out.select_set(False)
    # normalise to radius 1
    xs = [abs(v.co.x) for v in me.vertices] + [abs(v.co.y) for v in me.vertices]
    k = 1 / max(xs)
    for v in me.vertices:
        v.co *= k
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(FOAM)
    return out


def join(objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active
    o.name = name
    o.data.name = name
    o.select_set(False)
    return o


made = [
    palm('palm-a', (0.10, 0.03), 11),
    palm('palm-b', (-0.06, 0.09), 9),
    shrub('shrub-a', 7),
    shrub('shrub-b', 5, 0.9),
    shrub('shrub-c', 9, 0.6),
]
for i, o in enumerate(made):
    o.location = (i * 3.0, 0, 0)  # spread out in the file; the game reads each node's geometry only
for o in made:
    print('[trees]', o.name, len(o.data.polygons), 'faces')

os.makedirs(os.path.dirname(OUT), exist_ok=True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_yup=True, export_apply=True, export_materials='EXPORT')
print('[trees] wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')
