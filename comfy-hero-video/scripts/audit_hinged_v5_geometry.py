"""Inspect evaluated Blender geometry, including curve bevels and cloth thickness."""
import json
from pathlib import Path
import bpy
from mathutils import Vector

scene=bpy.context.scene
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
names=['UD Trucks tapered body','Sculpted tumbler handle','Leather edge layers',
       'Tote visible front panel','ICONSIAM cylindrical foam','Clear event-stick grip']
report={}
for name in names:
    obj=bpy.data.objects[name].evaluated_get(deps)
    mesh=obj.to_mesh()
    positions=[obj.matrix_world@v.co for v in mesh.vertices]
    lo=[min(p[i] for p in positions) for i in range(3)]
    hi=[max(p[i] for p in positions) for i in range(3)]
    assert hi[2]-lo[2]>.025,(name,'flat geometry')
    assert hi[2]<1.60,(name,'intersects closed lid')
    assert lo[2]>.13,(name,'below box floor')
    assert lo[0]>-1.805 and hi[0]<1.805,(name,'intersects side walls')
    assert lo[1]>-1.355 and hi[1]<1.355,(name,'intersects front/rear wall')
    report[name]={'vertices':len(positions),'bounds_min':lo,'bounds_max':hi,'physical_depth':hi[2]-lo[2]}
    obj.to_mesh_clear()
assert 'Recessed product photographic insert' not in bpy.data.objects
out=Path(bpy.data.filepath).parent/'geometry-audit.json'
out.write_text(json.dumps({'status':'PASS','products':report,'closed_lid_clearance':True,'no_product_planes':True},indent=2))
print('GEOMETRY_AUDIT_PASS',len(report),'volumetric components')
