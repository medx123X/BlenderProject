import bpy,json
from collections import Counter
print('AUDIT_FILE',bpy.data.filepath)
print('ARMATURES',[(o.name,len(o.data.bones)) for o in bpy.data.objects if o.type=='ARMATURE'])
c=bpy.data.collections.get('CHAR_HERO_PUPPET')
print('CHARACTER',len(c.objects),Counter(o.parent_type for o in c.objects))
print('PIVOTS',[(o.name,o.parent.name if o.parent else None,tuple(round(x,3) for x in o.matrix_world.translation)) for o in c.objects if o.type=='EMPTY'])
print('CONSTRAINTS',[(o.name,[(x.type,x.name) for x in o.constraints]) for o in c.objects if o.constraints])
print('STRINGS',[(o.name,[(m.type,m.name) for m in o.modifiers]) for o in bpy.data.collections['CHAR_HERO_STRINGS'].objects])
print('MATERIALS',len(bpy.data.materials),'ACTIONS',len(bpy.data.actions))
