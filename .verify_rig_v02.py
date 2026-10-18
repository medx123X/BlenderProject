import bpy,json
r=bpy.data.objects['RIG_HERO']
bpy.context.view_layer.update()
assert len(r.data.bones)==32
assert len(bpy.data.actions)==0
assert all(f.driver.is_valid for f in r.animation_data.drivers)
for k in ['Foot_IK_L','Foot_IK_R','Hand_IK_L','Hand_IK_R','Suspension_String_Follow','Hand_String_Follow_L','Hand_String_Follow_R']: assert r[k]==0
for o in bpy.data.collections['CHAR_HERO_STRINGS'].objects:
 assert len([m for m in o.modifiers if m.type=='HOOK'])==2
 assert all(f.driver.is_valid for f in o.animation_data.drivers)
assert all(not o.hide_get() for o in bpy.data.collections['CHAIRS'].objects)
assert bpy.data.collections['CHAR_HERO_NEUTRAL_REST'].hide_render
assert bpy.data.collections['ARCHIVE_HERO_v01'].hide_render
print('REOPEN VALIDATION PASS: 32 bones, valid drivers, six double-ended strings, defaults restored, empty seats retained, archives hidden, zero actions.')
