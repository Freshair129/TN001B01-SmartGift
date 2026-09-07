"""Reference-based volumetric product geometry; no photographic product plates."""
import math
import bpy
from mathutils import Vector


def build_products(root, cube, material, foam):
    groups = {}
    black = material('Tumbler powder coat', (.012, .017, .022), .31, .15, True)
    rubber = material('Moulded black handle', (.008, .010, .013), .38)
    steel = material('Brushed stainless rim', (.48, .53, .58), .24, .92)
    plastic = material('Translucent lid polymer', (.50, .57, .62), .18)
    plastic.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value = .55
    leather = material('Tan fine-grain leather', (.32, .137, .047), .48, grain=True)
    edge = material('Leather edge paint', (.12, .042, .012), .48)
    thread = material('Tan stitching', (.57, .34, .14), .76)
    fabric = material('Black woven canvas', (.013, .015, .018), .9, grain=True)
    nt = fabric.node_tree
    weave = nt.nodes.new('ShaderNodeTexWave')
    weave.wave_type = 'BANDS'
    weave.bands_direction = 'X'
    weave.inputs['Scale'].default_value = 220
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = .17
    bump.inputs['Distance'].default_value = .003
    nt.links.new(weave.outputs['Color'], bump.inputs['Height'])
    nt.links.new(nt.nodes['Bump'].outputs['Normal'], bump.inputs['Normal'])
    nt.links.new(bump.outputs['Normal'], nt.nodes['Principled BSDF'].inputs['Normal'])
    white = material('Fine white foam', (.82, .84, .85), .78, grain=True)
    clear = material('Clear light-stick handle', (.78, .82, .85), .14)
    clear.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value = 1

    def mesh(name, vertices, faces, mat, uvs=None):
        data = bpy.data.meshes.new(name)
        data.from_pydata(vertices, [], faces)
        data.update()
        obj = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(obj)
        data.materials.append(mat)
        for poly in data.polygons:
            poly.use_smooth = True
        if uvs:
            data.uv_layers.new()
            for poly in data.polygons:
                for li in poly.loop_indices:
                    data.uv_layers.active.data[li].uv = uvs[data.loops[li].vertex_index]
        return obj

    def tube(name, points, radius, mat, cyclic=False):
        curve = bpy.data.curves.new(name, 'CURVE')
        curve.dimensions = '3D'
        curve.resolution_u = 16
        curve.bevel_depth = radius
        curve.bevel_resolution = 4
        spline = curve.splines.new('BEZIER')
        spline.bezier_points.add(len(points)-1)
        for p, co in zip(spline.bezier_points, points):
            p.co = co
            p.handle_left_type = p.handle_right_type = 'AUTO'
        spline.use_cyclic_u = cyclic
        obj = bpy.data.objects.new(name, curve)
        bpy.context.collection.objects.link(obj)
        obj.data.materials.append(mat)
        return obj

    def lathe(name, x, z, profile, mat):
        n = 96
        vertices = [(x+r*math.sin(2*math.pi*j/n), y, z+r*math.cos(2*math.pi*j/n))
                    for y,r in profile for j in range(n)]
        faces = [(k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j)
                 for k in range(len(profile)-1) for j in range(n)]
        faces += [tuple(reversed(range(n))), tuple((len(profile)-1)*n+j for j in range(n))]
        obj = mesh(name, vertices, faces, mat)
        bevel = obj.modifiers.new('Turned edge radii', 'BEVEL')
        bevel.width = .012
        bevel.segments = 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
        return obj

    def cut(insert, cutter):
        bpy.context.view_layer.objects.active = insert
        mod = insert.modifiers.new('Fitted cavity', 'BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.solver = 'EXACT'
        mod.object = cutter
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(cutter, do_unlink=True)

    def artwork(name, source, crop, ink, base):
        # Reuse original artwork through UV sampling; exclude photographed lighting from shading.
        mat = base.copy()
        mat.name = name
        nt = mat.node_tree
        tex = nt.nodes.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(str(source), check_existing=True)
        mapping = nt.nodes.new('ShaderNodeVectorMath')
        mapping.operation = 'MULTIPLY_ADD'
        x0,y0,x1,y1 = crop
        mapping.inputs[1].default_value = (x1-x0,y1-y0,1)
        mapping.inputs[2].default_value = (x0,1-y1,0)
        uv = nt.nodes.new('ShaderNodeTexCoord')
        nt.links.new(uv.outputs['UV'], mapping.inputs[0])
        nt.links.new(mapping.outputs[0], tex.inputs['Vector'])
        mix = nt.nodes.new('ShaderNodeMixRGB')
        bs = nt.nodes['Principled BSDF']
        mix.inputs[1].default_value = bs.inputs['Base Color'].default_value
        mix.inputs[2].default_value = (*ink,1)
        nt.links.new(tex.outputs['Alpha'],mix.inputs[0])
        nt.links.new(mix.outputs[0],bs.inputs['Base Color'])
        return mat

    def label(name, cx, cy, z, w, h, mat, radius=None, rotate=False):
        # A shallow surface patch follows the actual curved product, not a camera-facing billboard.
        vertices,uvs,faces = [],[],[]
        nx,ny=32,8
        for row in range(ny+1):
            v=row/ny
            for col in range(nx+1):
                u=col/nx
                dx=(u-.5)*w
                vertices.append((cx+dx,cy+(v-.5)*h,z if radius is None else z+math.sqrt(radius*radius-dx*dx)+.0005))
                uvs.append((v,1-u) if rotate else (u,v))
        for row in range(ny):
            for col in range(nx):
                a=row*(nx+1)+col
                faces.append((a,a+1,a+nx+2,a+nx+1))
        return mesh(name,vertices,faces,mat,uvs)

    before = set(bpy.data.objects)
    insert = cube('A machined foam insert',(0,0,.72),(3.60,2.70,1.06),foam,.012)
    # Open recesses extend from top to the curved bed, with real vertical cavity walls.
    cut(insert, lathe('Tumbler cavity',-.78,.92,[(-1.13,.38),(-.63,.40),(-.45,.55),(1.35,.55)],foam))
    cut(insert,cube('Handle recess',(-.10,.45,1.16),(.55,1.53,.45),foam,.12))
    cut(insert,cube('Leather recess',(1.02,-.04,1.29),(.94,1.48,.30),foam,.095))
    cup_before=set(bpy.data.objects)
    lathe('UD Trucks tapered body',-.78,.92,[(-1.20,.28),(-1.18,.32),(-1.12,.33),(-.69,.35),(-.59,.40),(-.46,.475),(-.38,.49),(.94,.49),(.99,.475)],black)
    lathe('Tumbler base foot',-.78,.92,[(-1.21,.29),(-1.19,.32),(-1.12,.33)],rubber)
    lathe('Stainless collar',-.78,.92,[(.95,.48),(1.01,.49),(1.04,.49)],steel)
    lathe('Clear tumbler lid',-.78,.92,[(1.04,.49),(1.11,.49),(1.14,.47)],plastic)
    cube('Drinking slider',(-.78,1.142,1.24),(.24,.055,.13),rubber,.035)
    tube('Sculpted tumbler handle',[(-.32,.80,.98),(-.01,.78,.98),(.09,.60,.98),(.09,-.12,.98),(-.04,-.31,.98),(-.32,-.31,.98)],.092,rubber)
    ud = artwork('UD supplied print',root/'comfy-3d-products/assets/logos/udtrucks.png',(0,0,1,1),(.73,.75,.76),black)
    label('UD print on cylindrical wall',-.78,.31,.92,.59,.468,ud,.491)
    for obj in set(bpy.data.objects)-cup_before:
        obj.location.y+=.12
    cube('Leather edge layers',(1.02,-.04,1.19),(.82,1.34,.135),edge,.065)
    cube('Leather upper face',(1.02,-.04,1.26),(.79,1.31,.06),leather,.055)
    # Individually raised thread stitches, each resting on the rounded leather face.
    for side in [-1,1]:
        for j in range(23):
            y=-.61+j*.052
            tube('Leather side stitch',[(1.02+side*.354,y,1.292),(1.02+side*.354,y+.025,1.292)],.004,thread)
        for j in range(13):
            x=.71+j*.052
            tube('Leather end stitch',[(x,-.04+side*.607,1.292),(x+.025,-.04+side*.607,1.292)],.004,thread)
    true = artwork('True supplied print',root/'comfy-3d-products/assets/logos/truecorp.png',(0,0,1,1),(.68,.012,.012),leather)
    label('True print on leather',1.02,.23,1.2904,.37,.134,true)
    groups['A'] = list(set(bpy.data.objects)-before)

    before = set(bpy.data.objects)
    insert = cube('B machined foam insert',(0,0,.72),(3.60,2.70,1.06),foam,.012)
    cut(insert,cube('Folded tote cavity',(-.52,-.02,1.3),(2.14,2.10,.45),foam,.09))
    cut(insert,lathe('Foam stick cavity',1.13,1.20,[(-1.25,.17),(-1.07,.23),(.94,.23),(1.17,.13)],foam))

    # Layered folded cloth, with shaped edges and low-frequency wrinkles in actual geometry.
    def cloth_height(x,y,z):
        return z+.012*math.sin(8*x+2*y)+.007*math.sin(17*y-3*x)+.008*math.sin(21*x+7*y)
    def cloth(name,z,width,depth):
        vertices,faces=[],[]
        nx,ny=54,54
        for j in range(ny+1):
            y=-.02+(j/ny-.5)*depth
            for i in range(nx+1):
                x=-.52+(i/nx-.5)*width
                # Rounded corners and soft cloth borders.
                corner=max(0,abs(y+.02)-depth/2+.13)
                x=-.52+(x+.52)*(1-.055*(corner/.13)**2)
                vertices.append((x,y,cloth_height(x,y,z)+.015*math.cos((i/nx-.5)*math.pi)))
        for j in range(ny):
            for i in range(nx):
                a=j*(nx+1)+i
                faces.append((a,a+1,a+nx+2,a+nx+1))
        obj=mesh(name,vertices,faces,fabric)
        solid=obj.modifiers.new('Folded fabric thickness','SOLIDIFY')
        solid.thickness=.028
        bevel=obj.modifiers.new('Soft cloth edges','BEVEL')
        bevel.width=.01
        bevel.segments=2
        return obj
    for layer in range(4):
        cloth('Folded canvas layer',1.13+layer*.039,1.99-layer*.012,1.95-layer*.018)
    tote_front=cloth('Tote visible front panel',1.302,1.97,1.88)
    # Handles folded back into the package, with ribbon cross-section and seams.
    for k in range(2):
        points=[(-1.17+k*.60,.56,1.34),(-1.13+k*.60,.82,1.38),(-.92+k*.60,.90,1.39),(-.73+k*.60,.70,1.37),(-.70+k*.60,.54,1.34)]
        strap=tube('Folded woven tote handle',points,.034,fabric)
        # Thin flattened handle cross-section represented by bevel profile.
        profile=bpy.data.curves.new('Ribbon section','CURVE')
        profile.dimensions='2D'
        sp=profile.splines.new('POLY')
        sp.points.add(3)
        for p,co in zip(sp.points,[(-.052,-.009,0,1),(.052,-.009,0,1),(.052,.009,0,1),(-.052,.009,0,1)]):p.co=co
        sp.use_cyclic_u=True
        po=bpy.data.objects.new('Ribbon profile',profile)
        bpy.context.collection.objects.link(po)
        po.hide_render=True
        strap.data.bevel_mode='OBJECT'
        strap.data.bevel_object=po
    for y in [-.87,.52]:
        tube('Tote stitched seam',[(x,y,cloth_height(x,y,1.325)) for x in [-1.43,-1.1,-.7,-.3,.15,.39]],.004,material('Black thread',(.028,.03,.032),.85))
    one=artwork('ONE BANGKOK supplied print',root/'comfy-3d-products/assets/logos/onebangkok.png',(0,0,1,1),(.73,.75,.77),fabric)
    # The screen print is part of the cloth material itself, so folds cannot
    # intersect a separate logo mesh or create holes in the letters.
    nt=one.node_tree
    position=nt.nodes.new('ShaderNodeNewGeometry')
    subtract=nt.nodes.new('ShaderNodeVectorMath')
    subtract.operation='SUBTRACT'
    subtract.inputs[1].default_value=(-1.26,-.22,0)
    divide=nt.nodes.new('ShaderNodeVectorMath')
    divide.operation='DIVIDE'
    divide.inputs[1].default_value=(1.48,.18,1)
    nt.links.new(position.outputs['Position'],subtract.inputs[0])
    nt.links.new(subtract.outputs[0],divide.inputs[0])
    image_node=next(n for n in nt.nodes if n.type=='TEX_IMAGE')
    image_node.extension='CLIP'
    nt.links.new(divide.outputs[0],image_node.inputs['Vector'])
    tote_front.data.materials[0]=one
    lathe('ICONSIAM cylindrical foam',1.13,1.20,[(-1.08,.165),(-1.06,.192),(-1.02,.198),(.89,.198),(.94,.187),(.95,.16)],white)
    lathe('Clear event-stick grip',1.13,1.20,[(.945,.096),(1.14,.096),(1.16,.087)],clear)
    lathe('Grip end ring',1.13,1.20,[(1.12,.099),(1.145,.099)],clear)
    icon=artwork('ICONSIAM supplied print',root/'comfy-3d-products/assets/logos/iconsiam.png',(0,0,1,1),(.008,.009,.01),white)
    label('ICONSIAM print follows foam cylinder',1.13,-.03,1.20,.198,1.32,icon,.199,True)
    groups['B'] = list(set(bpy.data.objects)-before)
    for variant,objects in groups.items():
        for obj in objects:
            obj['variant']=variant
            obj.pass_index=1
    return groups
