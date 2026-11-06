# VaLora house for VaLora: Two Watchers, modelled and baked headless in Blender.
#   /home/claude/bpy-env/bin/python art/blender/house.py   (or: blender -b -P art/blender/house.py)
# Reads art/layout.json (exported from src/sim/world.ts) so every wall matches the boxes the
# watchers test against. Bakes two atlases with Cycles:
#   - colour: the procedural materials flattened to an albedo texture
#   - occlusion: ambient occlusion (soft contact darkening in corners and under things)
# The sun is NOT baked: it moves between levels and the screen and overhang move with the
# player's hands, so the game lights the house with a real-time sun and shadows.
# Output: public/models/valora-house.glb (one mesh, two textures; the roof is its own material
# so the game can ghost it).

import json, math, os, random, sys
import bpy, bmesh
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
L = json.load(open(os.path.join(ROOT, 'art', 'layout.json')))
LAY = L['layout']
BOX = {b['id']: b for b in L['boxes']}
OUT = os.path.join(ROOT, 'public', 'models', 'valora-house.glb')
TEX = int(os.environ.get('VALORA_TEX', '2048'))
SAMPLES = int(os.environ.get('VALORA_SAMPLES', '24'))
rnd = random.Random(11)

# ---------------------------------------------------------------- scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = SAMPLES
scene.unit_settings.scale_length = 1.0


def S(x, y, z):
    """Site coordinates (y up, +z south) to Blender (z up, -y south)."""
    return Vector((x, -z, y))


# ---------------------------------------------------------------- materials (procedural, baked later)
def node_mat(name, build):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    coord = nt.nodes.new('ShaderNodeTexCoord')
    build(nt, bsdf, coord)
    return m


def rgb(nt, c):
    n = nt.nodes.new('ShaderNodeRGB')
    n.outputs[0].default_value = (*c, 1)
    return n.outputs[0]


def mix(nt, fac, a, b):
    n = nt.nodes.new('ShaderNodeMix')
    n.data_type = 'RGBA'
    nt.links.new(fac, n.inputs['Factor'])
    nt.links.new(a, n.inputs['A'])
    nt.links.new(b, n.inputs['B'])
    return n.outputs['Result']


def noise(nt, coord, scale, detail=6.0, rough=0.55):
    n = nt.nodes.new('ShaderNodeTexNoise')
    n.inputs['Scale'].default_value = scale
    n.inputs['Detail'].default_value = detail
    n.inputs['Roughness'].default_value = rough
    nt.links.new(coord.outputs['Object'], n.inputs['Vector'])
    return n.outputs['Fac']


def tint(nt, colour_out):
    """Multiply by the per-part 'tint' colour attribute (random variation per board, slab, book)."""
    a = nt.nodes.new('ShaderNodeVertexColor')
    a.layer_name = 'tint'
    m = nt.nodes.new('ShaderNodeMix')
    m.data_type = 'RGBA'
    m.blend_type = 'MULTIPLY'
    m.inputs['Factor'].default_value = 1.0
    nt.links.new(colour_out, m.inputs['A'])
    nt.links.new(a.outputs['Color'], m.inputs['B'])
    return m.outputs['Result']


def concrete(nt, bsdf, coord):
    # board-formed: 300 mm horizontal boards with darker joints, cloudy tone, fine grain
    w = nt.nodes.new('ShaderNodeTexWave')
    w.wave_type = 'BANDS'
    w.bands_direction = 'Z'
    w.inputs['Scale'].default_value = 1 / 0.3 / 1.0 * 0.5
    w.inputs['Distortion'].default_value = 0.6
    w.inputs['Detail'].default_value = 2
    nt.links.new(coord.outputs['Object'], w.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.30, 0.29, 0.27, 1)
    ramp.color_ramp.elements[1].position = 0.12
    ramp.color_ramp.elements[1].color = (0.47, 0.455, 0.43, 1)
    nt.links.new(w.outputs['Fac'], ramp.inputs['Fac'])
    cloud = mix(nt, noise(nt, coord, 0.6, 4, 0.5), rgb(nt, (0.40, 0.39, 0.37)), rgb(nt, (0.52, 0.51, 0.49)))
    grain = noise(nt, coord, 28, 8, 0.7)
    base = mix(nt, w.outputs['Fac'], ramp.outputs['Color'], cloud)
    fine = mix(nt, grain, base, rgb(nt, (0.36, 0.35, 0.33)))
    nt.links.new(fine, bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.92


def oak(nt, bsdf, coord):
    w = nt.nodes.new('ShaderNodeTexWave')
    w.bands_direction = 'X'
    w.inputs['Scale'].default_value = 3.0
    w.inputs['Distortion'].default_value = 8
    w.inputs['Detail'].default_value = 3
    nt.links.new(coord.outputs['Object'], w.inputs['Vector'])
    c = mix(nt, w.outputs['Fac'], rgb(nt, (0.42, 0.27, 0.15)), rgb(nt, (0.58, 0.40, 0.24)))
    nt.links.new(tint(nt, c), bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.55


def deck(nt, bsdf, coord):
    w = nt.nodes.new('ShaderNodeTexWave')
    w.bands_direction = 'X'
    w.inputs['Scale'].default_value = 5.0
    w.inputs['Distortion'].default_value = 10
    nt.links.new(coord.outputs['Object'], w.inputs['Vector'])
    c = mix(nt, w.outputs['Fac'], rgb(nt, (0.33, 0.20, 0.11)), rgb(nt, (0.50, 0.32, 0.18)))
    nt.links.new(tint(nt, c), bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.7


def stone(nt, bsdf, coord):
    c = mix(nt, noise(nt, coord, 6, 6, 0.6), rgb(nt, (0.40, 0.385, 0.35)), rgb(nt, (0.50, 0.48, 0.44)))
    nt.links.new(tint(nt, c), bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.8


def plaster(nt, bsdf, coord):
    c = mix(nt, noise(nt, coord, 3, 5, 0.5), rgb(nt, (0.60, 0.565, 0.51)), rgb(nt, (0.67, 0.63, 0.57)))
    nt.links.new(c, bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.95


def flat(colour, rough=0.6, metal=0.0):
    def f(nt, bsdf, coord):
        nt.links.new(tint(nt, rgb(nt, colour)), bsdf.inputs['Base Color'])
        bsdf.inputs['Roughness'].default_value = rough
        bsdf.inputs['Metallic'].default_value = metal
    return f


def grass(nt, bsdf, coord):
    c = mix(nt, noise(nt, coord, 2.5, 8, 0.6), rgb(nt, (0.13, 0.22, 0.07)), rgb(nt, (0.24, 0.35, 0.12)))
    c = mix(nt, noise(nt, coord, 40, 4, 0.7), c, rgb(nt, (0.18, 0.28, 0.09)))
    nt.links.new(c, bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 1.0


def soil(nt, bsdf, coord):
    c = mix(nt, noise(nt, coord, 12, 6, 0.6), rgb(nt, (0.12, 0.08, 0.05)), rgb(nt, (0.21, 0.15, 0.10)))
    nt.links.new(c, bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 1.0


MATS = {
    'concrete': node_mat('concrete', concrete),
    'roof': node_mat('roof', concrete),
    'oak': node_mat('oak', oak),
    'deck': node_mat('deck', deck),
    'stone': node_mat('stone', stone),
    'plaster': node_mat('plaster', plaster),
    'frame': node_mat('frame', flat((0.05, 0.05, 0.05), 0.45, 0.6)),
    'linen': node_mat('linen', flat((0.78, 0.74, 0.66), 0.95)),
    'teak': node_mat('teak', flat((0.36, 0.20, 0.10), 0.5)),
    'grass': node_mat('grass', grass),
    'soil': node_mat('soil', soil),
    'pool': node_mat('pool', flat((0.10, 0.20, 0.21), 0.4)),
    'book': node_mat('book', flat((1, 1, 1), 0.7)),
    'brass': node_mat('brass', flat((0.62, 0.47, 0.26), 0.35, 0.8)),
}

# ---------------------------------------------------------------- geometry helpers
parts = []  # (object, material key)


def box(x0, x1, y0, y1, z0, z1, mat, bevel=0.015, tint_c=(1, 1, 1), name='part'):
    """Axis-aligned box in site metres with bevelled edges."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = (x0 + x1) / 2 + v.co.x * (x1 - x0)
        sy = (y0 + y1) / 2 + v.co.z * (y1 - y0)
        sz = (z0 + z1) / 2 + v.co.y * -(z1 - z0)
        v.co.y = -sz
        v.co.z = sy
    if bevel > 0:
        lim = min(x1 - x0, y1 - y0, z1 - z0) * 0.45
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=min(bevel, lim), segments=2, profile=0.6, affect='EDGES')
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    col = me.color_attributes.new('tint', 'FLOAT_COLOR', 'POINT')
    for d in col.data:
        d.color = (*tint_c, 1)
    parts.append((ob, mat))
    return ob


def jitter(c, amt):
    k = 1 + rnd.uniform(-amt, amt)
    return tuple(min(1, max(0, v * k)) for v in c)


R = LAY['room']
C = LAY['court']
N = LAY['neighbour']

# ---------------------------------------------------------------- ground and lawn
box(-9.0, 15.4, -0.08, 0.0, -8.6, 5.8, 'grass', bevel=0.0, name='lawn')

# ---------------------------------------------------------------- the room
box(R['x0'], R['x1'], 0.0, 0.05, R['z0'], R['z1'], 'oak', bevel=0.0, name='room-floor')
# oak boards: thin strips just proud of the floor, each a slightly different tone
x = R['x0'] + 0.1
while x < R['x1'] - 0.1:
    box(x, min(x + 0.19, R['x1'] - 0.1), 0.05, 0.055, R['z0'] + 0.15, R['z1'] - 0.05, 'oak', bevel=0.004, tint_c=jitter((1, 1, 1), 0.12), name='board')
    x += 0.2
for key in ('north wall', 'west wall', 'east wall'):
    b = BOX[key]
    box(b['c'][0] - b['h'][0], b['c'][0] + b['h'][0], 0.0, b['c'][1] + b['h'][1], b['c'][2] - b['h'][2], b['c'][2] + b['h'][2], 'concrete', bevel=0.03, name=key)
rf = BOX['roof']
box(rf['c'][0] - rf['h'][0], rf['c'][0] + rf['h'][0], rf['c'][1] - rf['h'][1], rf['c'][1] + rf['h'][1], rf['c'][2] - rf['h'][2], rf['c'][2] + rf['h'][2], 'roof', bevel=0.04, name='roof')

# glazing frames on the courtyard face: sill, head, mullions every 2.45 m, a sliding-door track
gz = R['z1']
box(R['x0'] + 0.15, R['x1'] - 0.15, 0.05, 0.11, gz - 0.06, gz + 0.06, 'frame', bevel=0.006, name='sill')
box(R['x0'] + 0.15, R['x1'] - 0.15, R['h'] - 0.1, R['h'], gz - 0.06, gz + 0.06, 'frame', bevel=0.006, name='head')
mx = R['x0'] + 0.15
while mx <= R['x1'] - 0.1:
    box(mx - 0.045, mx + 0.045, 0.05, R['h'], gz - 0.06, gz + 0.06, 'frame', bevel=0.006, name='mullion')
    mx += 2.45

# ---------------------------------------------------------------- the reading corner
sx, _, sz = LAY['seat']
cz = sz - 0.2
# armchair: low teak frame, deep linen seat and back cushions, rounded arms
box(sx - 0.46, sx + 0.46, 0.05, 0.3, cz - 0.44, cz + 0.42, 'teak', bevel=0.03, name='chair-base')
box(sx - 0.46, sx - 0.32, 0.05, 0.66, cz - 0.44, cz + 0.42, 'linen', bevel=0.06, name='chair-arm')
box(sx + 0.32, sx + 0.46, 0.05, 0.66, cz - 0.44, cz + 0.42, 'linen', bevel=0.06, name='chair-arm')
box(sx - 0.33, sx + 0.33, 0.3, 0.48, cz - 0.3, cz + 0.4, 'linen', bevel=0.07, name='chair-seat')
box(sx - 0.33, sx + 0.33, 0.3, 1.02, cz - 0.44, cz - 0.24, 'linen', bevel=0.08, name='chair-back')
# rug, side table with a brass lamp, a book stack
box(sx - 1.3, sx + 1.3, 0.055, 0.07, sz - 1.7, sz + 0.65, 'linen', bevel=0.004, tint_c=(0.86, 0.80, 0.72), name='rug')
box(sx + 0.7, sx + 1.15, 0.05, 0.56, cz - 0.45, cz - 0.0, 'teak', bevel=0.02, name='side-table')
box(sx + 0.9, sx + 0.95, 0.56, 1.25, cz - 0.25, cz - 0.2, 'brass', bevel=0.0, name='lamp-stem')
box(sx + 0.78, sx + 1.07, 1.2, 1.42, cz - 0.37, cz - 0.08, 'linen', bevel=0.04, tint_c=(1.1, 1.05, 0.95), name='lamp-shade')
# bookshelf along the west wall with books of varied colour and height
bx0 = R['x0'] + 0.15
box(bx0, bx0 + 0.38, 0.05, 2.2, R['z0'] + 0.6, R['z0'] + 2.6, 'teak', bevel=0.015, name='shelf')
for shelf_y in (0.45, 0.95, 1.45, 1.95):
    z = R['z0'] + 0.68
    while z < R['z0'] + 2.5:
        w = rnd.uniform(0.04, 0.08)
        h = rnd.uniform(0.22, 0.34)
        col = rnd.choice([(0.45, 0.20, 0.15), (0.20, 0.30, 0.35), (0.75, 0.68, 0.55), (0.30, 0.35, 0.22), (0.15, 0.15, 0.17), (0.62, 0.48, 0.30)])
        box(bx0 + 0.04, bx0 + 0.34, shelf_y, shelf_y + h, z, z + w, 'book', bevel=0.004, tint_c=col, name='book')
        z += w + 0.005

# ---------------------------------------------------------------- the courtyard
deck_z1 = C['z0'] + 1.5
# deck boards running east-west, 140 mm wide with 6 mm gaps
z = C['z0'] + 0.02
while z < deck_z1:
    box(C['x0'], C['x1'], 0.0, 0.06, z, min(z + 0.14, deck_z1), 'deck', bevel=0.006, tint_c=jitter((1, 1, 1), 0.14), name='deck-board')
    z += 0.146
pool = {'x0': -4.3, 'x1': -1.6, 'z0': 0.3, 'z1': 2.9}
# stone paving: 600 x 600 slabs with 10 mm joints over a mortar bed, skipping the pool
box(C['x0'], C['x1'], -0.02, 0.02, deck_z1, C['z1'] - 1.0, 'soil', bevel=0.0, tint_c=(0.7, 0.7, 0.7), name='bed')
z = deck_z1 + 0.005
while z < C['z1'] - 1.0 - 0.1:
    x = C['x0'] + 0.005
    while x < C['x1'] - 0.1:
        x1 = min(x + 0.59, C['x1'] - 0.005)
        z1 = min(z + 0.59, C['z1'] - 1.0 - 0.005)
        inside_pool = x1 > pool['x0'] - 0.25 and x < pool['x1'] + 0.25 and z1 > pool['z0'] - 0.25 and z < pool['z1'] + 0.25
        if not inside_pool:
            box(x, x1, 0.0, 0.05, z, z1, 'stone', bevel=0.008, tint_c=jitter((1, 1, 1), 0.08), name='slab')
        x += 0.6
    z += 0.6
# pool: basin, coping, a step
box(pool['x0'], pool['x1'], -0.45, -0.3, pool['z0'], pool['z1'], 'pool', bevel=0.0, name='pool-floor')
for (a, b, c, d) in ((pool['x0'] - 0.25, pool['x1'] + 0.25, pool['z0'] - 0.25, pool['z0']), (pool['x0'] - 0.25, pool['x1'] + 0.25, pool['z1'], pool['z1'] + 0.25), (pool['x0'] - 0.25, pool['x0'], pool['z0'], pool['z1']), (pool['x1'], pool['x1'] + 0.25, pool['z0'], pool['z1'])):
    box(a, b, -0.45, 0.09, c, d, 'stone', bevel=0.015, tint_c=(1.08, 1.06, 1.02), name='coping')
# planted bed along the south wall with a concrete kerb
box(C['x0'], C['x1'], 0.0, 0.18, C['z1'] - 1.0, C['z1'] - 0.92, 'concrete', bevel=0.012, name='kerb')
box(C['x0'], C['x1'], 0.0, 0.14, C['z1'] - 0.92, C['z1'], 'soil', bevel=0.0, name='bed-south')
# garden walls with a wider coping cap, and small brass wall lights
for key in ('east garden wall', 'south garden wall', 'west garden wall'):
    b = BOX[key]
    x0, x1 = b['c'][0] - b['h'][0], b['c'][0] + b['h'][0]
    z0, z1 = b['c'][2] - b['h'][2], b['c'][2] + b['h'][2]
    top = b['c'][1] + b['h'][1]
    box(x0, x1, 0.0, top - 0.06, z0, z1, 'concrete', bevel=0.02, name=key)
    box(x0 - 0.03, x1 + 0.03, top - 0.06, top, z0 - 0.03, z1 + 0.03, 'stone', bevel=0.012, name='cap')
for lx in (-3.0, 0.0, 3.0):
    box(lx - 0.07, lx + 0.07, 1.6, 1.72, C['z1'] - 0.06, C['z1'], 'brass', bevel=0.01, name='wall-light')
# a teak bench on the west side of the pool
box(-4.75, -4.35, 0.0, 0.45, -0.6, 0.15, 'teak', bevel=0.02, name='bench')

# ---------------------------------------------------------------- the neighbour's house
nh = BOX['neighbour house']
nx0, nx1 = nh['c'][0] - nh['h'][0], nh['c'][0] + nh['h'][0]
nz0, nz1 = nh['c'][2] - nh['h'][2], nh['c'][2] + nh['h'][2]
ny1 = nh['c'][1] + nh['h'][1]
box(nx0, nx1, 0.0, ny1, nz0, nz1, 'plaster', bevel=0.03, name='neighbour')
box(nx0 - 0.06, nx1 + 0.06, ny1, ny1 + 0.35, nz0 - 0.06, nz1 + 0.06, 'plaster', bevel=0.03, tint_c=(0.95, 0.95, 0.95), name='parapet')
box(nx0 + 0.15, nx1 - 0.15, ny1 + 0.02, ny1 + 0.36, nz0 + 0.15, nz1 - 0.15, 'concrete', bevel=0.0, name='roof-inner')
wy, wz = N['window'][1], N['window'][2]
# the watching window: dark frame and a stone sill (the glow is added by the game)
for (a, b, c, d) in ((wy - 0.66, wy - 0.6, wz - 0.76, wz + 0.76), (wy + 0.6, wy + 0.66, wz - 0.76, wz + 0.76), (wy - 0.66, wy + 0.66, wz - 0.76, wz - 0.7), (wy - 0.66, wy + 0.66, wz + 0.7, wz + 0.76)):
    box(nx0 - 0.06, nx0 + 0.02, a, b, c, d, 'frame', bevel=0.005, name='win-frame')
box(nx0 - 0.16, nx0 + 0.02, wy - 0.74, wy - 0.66, wz - 0.86, wz + 0.86, 'stone', bevel=0.01, name='win-sill')
# a second, ground-floor window and a door so the house reads as lived in
box(nx0 - 0.04, nx0 + 0.01, 0.9, 2.1, nz0 + 1.0, nz0 + 2.2, 'frame', bevel=0.005, name='win2')
box(nx0 - 0.04, nx0 + 0.01, 0.0, 2.2, nz1 - 1.6, nz1 - 0.6, 'teak', bevel=0.01, name='door')

# ---------------------------------------------------------------- stepping stones on the lawn
for i, (x, z) in enumerate(((6.2, 2.2), (6.9, 3.0), (7.4, 3.9), (5.6, 1.4))):
    box(x - 0.32, x + 0.32, -0.02, 0.03, z - 0.24, z + 0.24, 'stone', bevel=0.02, tint_c=jitter((1, 1, 1), 0.06), name='step')

# ---------------------------------------------------------------- join, unwrap, bake
# The lawn and the roof stay out of the baked mesh: the game draws the lawn with a tiled texture
# and the roof as a ghost the player sees through, so the roof must not darken the room either.
for ob, key in parts:
    ob.data.materials.append(MATS[key])
lawn = next(ob for ob, _ in parts if ob.name.startswith('lawn'))
roof = next(ob for ob, _ in parts if ob.name.startswith('roof'))
roof.hide_render = True
baked = [ob for ob, _ in parts if ob not in (lawn, roof)]
bpy.ops.object.select_all(action='DESELECT')
for ob in baked:
    ob.select_set(True)
bpy.context.view_layer.objects.active = baked[0]
bpy.ops.object.join()
house = bpy.context.view_layer.objects.active
house.name = 'valora-house'

# drop faces nobody sees: undersides resting on the ground or on another part
bm = bmesh.new()
bm.from_mesh(house.data)
bm.normal_update()
gone = [f for f in bm.faces if f.normal.z < -0.9 and f.calc_center_median().z < 0.12]
bmesh.ops.delete(bm, geom=gone, context='FACES')
bm.to_mesh(house.data)
bm.free()
print('[house] polygons', len(house.data.polygons), 'removed', len(gone))

bpy.ops.object.select_all(action='DESELECT')
house.select_set(True)
bpy.context.view_layer.objects.active = house
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.002, area_weight=0.0, scale_to_bounds=False)
bpy.ops.uv.pack_islands(rotate=True, margin=0.002)
bpy.ops.object.mode_set(mode='OBJECT')

colour_img = bpy.data.images.new('valora-colour', TEX, TEX, alpha=False)
ao_img = bpy.data.images.new('valora-ao', TEX, TEX, alpha=False, float_buffer=False)


def set_target(img):
    for m in house.data.materials:
        nt = m.node_tree
        n = nt.nodes.get('bake-target') or nt.nodes.new('ShaderNodeTexImage')
        n.name = 'bake-target'
        n.image = img
        for o in nt.nodes:
            o.select = False
        n.select = True
        nt.nodes.active = n


set_target(colour_img)
scene.cycles.samples = 4
bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, margin=6)
print('[house] colour baked')

# a sky-only world for the occlusion bake
world = bpy.data.worlds.new('sky')
scene.world = world
world.use_nodes = True
scene.cycles.samples = SAMPLES
set_target(ao_img)
scene.world.light_settings.distance = 1.2
bpy.ops.object.bake(type='AO', margin=6)
print('[house] occlusion baked')

# Three.js applies the occlusion map to ambient light only, so under a strong sun corners would
# float. Fold part of it into the albedo so contact darkening survives at every hour.
import numpy as np
c = np.array(colour_img.pixels[:]).reshape(-1, 4)
a = np.array(ao_img.pixels[:]).reshape(-1, 4)[:, :1]
c[:, :3] *= 1.0 - 0.55 * (1.0 - a)
colour_img.pixels[:] = c.ravel()

for img, name in ((colour_img, 'valora-colour.png'), (ao_img, 'valora-ao.png')):
    img.filepath_raw = os.path.join(ROOT, 'art', 'build', name)
    os.makedirs(os.path.dirname(img.filepath_raw), exist_ok=True)
    img.file_format = 'PNG'
    img.save()

# ---------------------------------------------------------------- export materials: baked colour + occlusion
def gltf_settings_group():
    g = bpy.data.node_groups.get('glTF Material Output')
    if g:
        return g
    g = bpy.data.node_groups.new('glTF Material Output', 'ShaderNodeTree')
    g.interface.new_socket('Occlusion', in_out='INPUT', socket_type='NodeSocketFloat')
    return g


for m in house.data.materials:
    nt = m.node_tree
    keep_rough = [n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'][0].inputs['Roughness'].default_value
    keep_metal = [n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'][0].inputs['Metallic'].default_value
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = keep_rough
    bsdf.inputs['Metallic'].default_value = keep_metal
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    cimg = nt.nodes.new('ShaderNodeTexImage')
    cimg.image = colour_img
    nt.links.new(cimg.outputs['Color'], bsdf.inputs['Base Color'])
    aimg = nt.nodes.new('ShaderNodeTexImage')
    aimg.image = ao_img
    aimg.image.colorspace_settings.name = 'Non-Color'
    sep = nt.nodes.new('ShaderNodeSeparateColor')
    nt.links.new(aimg.outputs['Color'], sep.inputs['Color'])
    grp = nt.nodes.new('ShaderNodeGroup')
    grp.node_tree = gltf_settings_group()
    m.use_backface_culling = True
    nt.links.new(sep.outputs['Red'], grp.inputs['Occlusion'])

house.data.color_attributes.remove(house.data.color_attributes['tint'])
bpy.ops.object.select_all(action='DESELECT')
house.select_set(True)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_yup=True, export_apply=True,
                          export_image_format='JPEG', export_jpeg_quality=88, export_materials='EXPORT')
print('[house] wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')
