"""Calibrated shared hinged gift-box scene; reference-composited inserts.
Run with Blender --background --python this.py -- --mode proof|render.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs' / 'v4'
OUT.mkdir(parents=True, exist_ok=True)
args = argparse.ArgumentParser()
args.add_argument('--mode', choices=['proof', 'render'], default='proof')
args.add_argument('--start', type=int, default=0)
args.add_argument('--end', type=int, default=119)
args.add_argument('--variant', choices=['A', 'B', 'both'], default='both')
opt = args.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 48
scene.cycles.use_denoising = True
scene.cycles.seed = 41
scene.cycles.use_animated_seed = False
scene.cycles.max_bounces = 4
scene.cycles.diffuse_bounces = 2
scene.cycles.glossy_bounces = 2
prefs = bpy.context.preferences.addons['cycles'].preferences
try:
    prefs.compute_device_type = 'OPTIX'
    prefs.get_devices()
    for dev in prefs.devices:
        dev.use = dev.type != 'CPU'
        print('RENDER_DEVICE', dev.name, dev.type, dev.use, flush=True)
    scene.cycles.device = 'GPU'
except Exception as exc:
    print('GPU unavailable:', exc, flush=True)
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 50 if opt.mode == 'proof' else 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.fps = 30
scene.render.use_persistent_data = True
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.render.film_transparent = True
scene.use_nodes = True
comp = scene.node_tree
comp.nodes.clear()
layers = comp.nodes.new('CompositorNodeRLayers')
over = comp.nodes.new('CompositorNodeAlphaOver')
over.inputs[1].default_value = (1, 1, 1, 1)
comp.links.new(layers.outputs['Image'], over.inputs[2])
comp.links.new(over.outputs[0], comp.nodes.new('CompositorNodeComposite').inputs[0])
scene.world = bpy.data.worlds.new('White studio')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (1, 1, 1, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = .6


def material(name, color, rough=.55, metal=0, grain=False):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bs = nt.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = rough
    bs.inputs['Metallic'].default_value = metal
    bs.inputs['Specular IOR Level'].default_value = .16
    if grain:
        noise = nt.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 240
        noise.inputs['Detail'].default_value = 2
        bump = nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .08
        bump.inputs['Distance'].default_value = .008
        nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
        nt.links.new(bump.outputs['Normal'], bs.inputs['Normal'])
    return mat


navy = material('Matte navy paper', (.004, .007, .014), .66, grain=True)
ivory = material('Warm ivory lining', (.69, .60, .45), .85, grain=True)
foam = material('Charcoal fitted insert', (.012, .013, .015), .85, grain=True)
ground = material('Neutral studio ground', (.92, .92, .92), .7)


def cube(name, loc, scale, mat, bevel=.015, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new('Manufactured soft edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted surface normals', 'WEIGHTED_NORMAL')
    obj.data.materials.append(mat)
    if parent:
        obj.parent = parent
    return obj


def plane(name, width, depth, z, mat, center_y=0, parent=None, flip=False):
    vertices = [(-width/2, center_y-depth/2, z), (width/2, center_y-depth/2, z),
                (width/2, center_y+depth/2, z), (-width/2, center_y+depth/2, z)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], [(0, 1, 2, 3)])
    mesh.uv_layers.new()
    for loop, uv in zip(mesh.uv_layers.active.data, [(0, 0), (1, 0), (1, 1), (0, 1)]):
        loop.uv = (uv[0], 1-uv[1]) if flip else uv
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    obj.parent = parent
    return obj


# Outer box 38 x 29 x 16cm; all geometry is shared between variants.
W, D, Z, T = 3.8, 2.9, 1.6, .095
floor = cube('Ground', (0, 0, -.065), (200, 200, .1), ground, 0)
floor.is_shadow_catcher = True
cube('Base bottom', (0, 0, .065), (W, D, .13), navy)
cube('Front wall', (0, -D/2+T/2, Z/2), (W, T, Z), navy)
cube('Rear wall', (0, D/2-T/2, Z/2), (W, T, Z), navy)
cube('Left wall', (-W/2+T/2, 0, Z/2), (T, D-T*2, Z), navy)
cube('Right wall', (W/2-T/2, 0, Z/2), (T, D-T*2, Z), navy)
cube('Deep insert support', (0, 0, .69), (W-T*2, D-T*2, 1.1), foam)

bpy.ops.object.empty_add(location=(0, D/2, Z+.014))
hinge = bpy.context.object
hinge.name = 'Rear hinge — linear 0 to105 degrees'
cube('Rigid lid shell', (0, -D/2, .065), (W+.018, D+.018, .13), navy, parent=hinge)
cube('Ivory inset lining', (0, -D/2, -.004), (W-.18, D-.18, .016), ivory, .009, hinge)


def logo_surface(name, gold, bottom=False):
    # The logo mask changes the lid's own surface material, with zero decal geometry offset.
    mat = material(name, (.004, .007, .014) if gold else (.69, .60, .45), .66, grain=True)
    nt = mat.node_tree
    n, links = nt.nodes, nt.links
    bs = n.get('Principled BSDF')
    uv = n.new('ShaderNodeTexCoord')
    mapping = n.new('ShaderNodeVectorMath')
    mapping.operation = 'MULTIPLY_ADD'
    # Logo texture includes white margins and tagline; crop to original emblem/wordmark.
    mapping.inputs[1].default_value = (.88, .56, 1)
    mapping.inputs[2].default_value = (.065, .27, 0)
    links.new(uv.outputs['UV'], mapping.inputs[0])
    tex = n.new('ShaderNodeTexImage')
    tex.image = bpy.data.images.load(str(ROOT.parents[1] / 'web-ui-smg/public/logo-smg.jpg'), check_existing=True)
    links.new(mapping.outputs['Vector'], tex.inputs['Vector'])
    bw = n.new('ShaderNodeRGBToBW')
    links.new(tex.outputs['Color'], bw.inputs[0])
    mask = n.new('ShaderNodeMapRange')
    mask.clamp = True
    mask.inputs['From Min'].default_value = .75
    mask.inputs['From Max'].default_value = .92
    mask.inputs['To Min'].default_value = 1
    mask.inputs['To Max'].default_value = 0
    links.new(bw.outputs[0], mask.inputs[0])
    mix = n.new('ShaderNodeMixRGB')
    mix.inputs[1].default_value = (.004, .007, .014, 1) if gold else (.69, .60, .45, 1)
    mix.inputs[2].default_value = (.83, .51, .14, 1)
    if not gold:
        links.new(tex.outputs['Color'], mix.inputs[2])
    links.new(mask.outputs[0], mix.inputs[0])
    links.new(mix.outputs[0], bs.inputs['Base Color'])
    if gold:
        links.new(mask.outputs[0], bs.inputs['Metallic'])
        rough = n.new('ShaderNodeMapRange')
        rough.inputs['To Min'].default_value = .66
        rough.inputs['To Max'].default_value = .25
        links.new(mask.outputs[0], rough.inputs[0])
        links.new(rough.outputs[0], bs.inputs['Roughness'])
        deboss = n.new('ShaderNodeBump')
        deboss.invert = True
        deboss.inputs['Strength'].default_value = .22
        deboss.inputs['Distance'].default_value = .0015
        links.new(mask.outputs[0], deboss.inputs['Height'])
        links.new(n.get('Bump').outputs['Normal'], deboss.inputs['Normal'])
        links.new(deboss.outputs['Normal'], bs.inputs['Normal'])
    # Tiny coplanar material patch uses exactly the paper shader outside the mask.
    return plane(name, 1.80, .83, -.013 if bottom else .1303, mat, -D/2, hinge, flip=bottom)


logo_surface('Exterior paper-integrated gold foil', True)
logo_surface('Inner printed SmartGift', False, True)

insert_mat = material('Reference product surface', (.012, .013, .015), .85, grain=True)
nt = insert_mat.node_tree
tex = nt.nodes.new('ShaderNodeTexImage')
images = {v: bpy.data.images.load(str(ROOT / 'assets/v4' / f'insert_{v}.png')) for v in ['A', 'B']}
tex.image = images['A']
uv = nt.nodes.new('ShaderNodeTexCoord')
split = nt.nodes.new('ShaderNodeSeparateXYZ')
nt.links.new(uv.outputs['UV'], split.inputs[0])
edges = []
for axis in ['X', 'Y']:
    invert = nt.nodes.new('ShaderNodeMath')
    invert.operation = 'SUBTRACT'
    invert.inputs[0].default_value = 1
    nt.links.new(split.outputs[axis], invert.inputs[1])
    nearest = nt.nodes.new('ShaderNodeMath')
    nearest.operation = 'MINIMUM'
    nt.links.new(split.outputs[axis], nearest.inputs[0])
    nt.links.new(invert.outputs[0], nearest.inputs[1])
    edges.append(nearest.outputs[0])
nearest = nt.nodes.new('ShaderNodeMath')
nearest.operation = 'MINIMUM'
for i, edge in enumerate(edges):
    nt.links.new(edge, nearest.inputs[i])
feather = nt.nodes.new('ShaderNodeMapRange')
feather.interpolation_type = 'SMOOTHSTEP'
feather.inputs['From Max'].default_value = .075
nt.links.new(nearest.outputs[0], feather.inputs[0])
blend = nt.nodes.new('ShaderNodeMixRGB')
blend.inputs[1].default_value = (.012, .013, .015, 1)
nt.links.new(feather.outputs[0], blend.inputs[0])
nt.links.new(tex.outputs['Color'], blend.inputs[2])
nt.links.new(blend.outputs[0], nt.nodes['Principled BSDF'].inputs['Base Color'])
insert = plane('Recessed product photographic insert', 3.15, 2.4, 1.2403, insert_mat, center_y=.1)
insert.pass_index = 1
scene.view_layers[0].use_pass_object_index = True
cube('Common front foam margin', (0, -1.125, 1.241), (W-.2, .45, .014), foam, .002)
mask_node = comp.nodes.new('CompositorNodeMath')
mask_node.operation = 'GREATER_THAN'
mask_node.inputs[1].default_value = .5
comp.links.new(layers.outputs['IndexOB'], mask_node.inputs[0])
mask_output = comp.nodes.new('CompositorNodeOutputFile')
mask_output.format.file_format = 'PNG'
mask_output.format.color_mode = 'BW'
mask_output.file_slots[0].path = ''
comp.links.new(mask_node.outputs[0], mask_output.inputs[0])
# Prevent variant colors from tinting the shared shell/ground via indirect rays.
insert.visible_diffuse = False
insert.visible_glossy = False


def area(name, location, energy, size, color=(1, 1, 1)):
    bpy.ops.object.light_add(type='AREA', location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.energy = energy
    obj.data.shape = 'DISK'
    obj.data.size = size
    obj.data.color = color
    obj.rotation_euler = (Vector((0, 0, 1))-obj.location).to_track_quat('-Z', 'Y').to_euler()


area('Broad upper-left softbox', (-4, -4, 8), 120, 7)
area('Soft right fill', (4, -1, 6), 120, 6)
area('Rear foil reflection source', (0, 5, 7), 80, 7)
bpy.ops.object.camera_add()
camera = bpy.context.object
scene.camera = camera
camera.data.type = 'ORTHO'
camera.data.lens = 65


def pose(i):
    p = i/119
    elevation = 80-30*p
    hinge.rotation_euler.x = -math.radians(105*p)
    target = Vector((0, .9*p, 1.05+.75*p))
    azimuth = math.radians(3)
    el = math.radians(elevation)
    direction = Vector((math.cos(el)*math.sin(azimuth), -math.cos(el)*math.cos(azimuth), math.sin(el)))
    camera.location = target+direction*20
    camera.rotation_euler = (-direction).to_track_quat('-Z', 'Y').to_euler()
    camera.data.ortho_scale = 7.2+5*p
    scene.frame_set(i)
    return {'frame':i,'progress':p,'lid_degrees':105*p,'camera_elevation':elevation,
            'ortho_width':camera.data.ortho_scale,'camera_location':list(camera.location),
            'hinge_location':list(hinge.location),'base_location':[0,0,0]}


poses = [pose(i) for i in range(120)]
(OUT / 'scene_contract.json').write_text(json.dumps({'frames':poses,'products':'reference-composited insert plates; not full volumetric product twins','renderer':bpy.app.version_string,'samples':scene.cycles.samples}, indent=2), encoding='utf-8')
pose(0)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'smartgift_hinged_v4.blend'))
variants = ['A', 'B'] if opt.variant == 'both' else [opt.variant]
frames = [0, 18, 60, 119] if opt.mode == 'proof' else range(opt.start, opt.end+1)
for v in variants:
    tex.image = images[v]
    dest = OUT / ('proof' if opt.mode == 'proof' else 'frames') / v
    dest.mkdir(parents=True, exist_ok=True)
    mask_output.base_path = str(OUT / ('proof_masks' if opt.mode == 'proof' else 'masks') / v)
    for i in frames:
        pose(i)
        scene.render.filepath = str(dest / f'{i:04}.png')
        bpy.ops.render.render(write_still=True)
        print('FRAME_DONE', v, i, flush=True)
