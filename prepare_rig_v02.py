import bpy, math, json
from mathutils import Vector, Matrix

r = bpy.data.objects['RIG_HERO']
assert 'CTRL_Suspension' not in r.data.bones, 'Rig v02 controls already exist; do not run twice.'
char = list(bpy.data.collections['CHAR_HERO_PUPPET'].objects)
state = {'basis': {b.name:b.matrix_basis.copy() for b in r.pose.bones},
         'world': {o.name:o.matrix_world.copy() for o in char},
         'data': {o.name:(o.data.name if o.data else None, tuple(m.name if m else '' for m in o.data.materials) if hasattr(o.data,'materials') else ()) for o in char}}
bpy.app.driver_namespace['rig_v02_validation'] = state
if bpy.context.object and bpy.context.object.mode != 'OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
r.hide_set(False)
r.hide_viewport=False
r.show_in_front=True
bpy.ops.object.select_all(action='DESELECT')
r.select_set(True)
bpy.context.view_layer.objects.active=r
targets={}
for side in ['L','R']:
    for kind, joint, end in [('Foot','Knee','Foot'),('Hand','Elbow','Wrist')]:
        a=r.pose.bones[('UpperLeg.' if kind=='Foot' else 'UpperArm.')+side].head.copy()
        b=r.pose.bones[joint+'.'+side].head.copy()
        c=r.pose.bones[('Ankle.' if kind=='Foot' else 'Wrist.')+side].head.copy()
        line=c-a
        bend=b-(a+line*((b-a).dot(line)/line.length_squared))
        if bend.length < .001: bend=Vector((0,-1,0))
        pole=b+bend.normalized()*.65
        targets[kind+'.'+side]=(r.pose.bones[end+'.'+side].matrix.copy(),pole)
bpy.ops.object.mode_set(mode='EDIT')
hang=r.data.edit_bones.new('CTRL_Suspension')
hang.head=(0,0,2.2); hang.tail=(0,0,2.5)
hang.parent=r.data.edit_bones['Root']; hang.use_deform=False
r.data.edit_bones['Pelvis'].parent=hang
for key,(mat,pole) in targets.items():
    b=r.data.edit_bones.new('CTRL_'+key+'_IK')
    b.head=mat.translation; b.tail=mat.translation+mat.to_3x3().col[1]*.22
    b.align_roll(mat.to_3x3().col[2]); b.use_deform=False
    p=r.data.edit_bones.new('CTRL_'+key+'_Pole')
    p.head=pole; p.tail=pole+Vector((0,0,.15)); p.use_deform=False
bpy.ops.object.mode_set(mode='OBJECT')
fk=r.data.collections.new('01 Body and FK joints')
ikc=r.data.collections.new('02 Hand and Foot IK')
polec=r.data.collections.new('03 IK bend directions')
for b in r.data.bones:
    (polec if b.name.endswith('_Pole') else ikc if b.name.endswith('_IK') else fk).assign(b)
    pb=r.pose.bones[b.name]
    pb.lock_scale=(True,True,True)
    if not b.name.startswith('CTRL_') and b.name not in ['Root','Pelvis']:
        pb.lock_location=(True,True,True)
    if b.name.startswith('CTRL_'):
        pb.rotation_mode='XYZ'
    b.color.palette='THEME04' if b.name.endswith('_IK') else 'THEME03' if b.name.endswith('_Pole') else 'THEME02'

def driven_influence(constraint,prop):
    fc=constraint.driver_add('influence')
    d=fc.driver; d.type='AVERAGE'
    v=d.variables.new(); v.name='blend'; v.type='SINGLE_PROP'
    v.targets[0].id=r; v.targets[0].data_path='["'+prop+'"]'

for key in targets:
    kind,side=key.split('.')
    prop=kind+'_IK_'+side
    r[prop]=0.0
    r.id_properties_ui(prop).update(min=0.0,max=1.0,description='0: direct FK joints; 1: IK target. Match target to current limb before switching.')
    pb=r.pose.bones[('Knee.' if kind=='Foot' else 'Elbow.')+side]
    c=pb.constraints.new('IK'); c.name='Animator '+kind+' IK'
    c.target=r; c.subtarget='CTRL_'+key+'_IK'
    c.pole_target=r; c.pole_subtarget='CTRL_'+key+'_Pole'
    c.chain_count=2; c.use_stretch=False; c.iterations=128
    driven_influence(c,prop)
    for n in [('UpperLeg.' if kind=='Foot' else 'UpperArm.')+side,pb.name]:
        r.pose.bones[n].ik_stretch=0
    rot=r.pose.bones[('Foot.' if kind=='Foot' else 'Wrist.')+side].constraints.new('COPY_ROTATION')
    rot.name='Animator '+kind+' orientation'
    rot.target=r; rot.subtarget='CTRL_'+key+'_IK'
    rot.target_space='POSE'; rot.owner_space='POSE'
    driven_influence(rot,prop)

# Both ends use Blender native hooks: no runtime Python handlers are needed.
for o in bpy.data.collections['CHAR_HERO_STRINGS'].objects:
    suffix=o.name.removeprefix('HERO_String_')
    anchor=bpy.data.objects['HERO2_StringAnchor_'+suffix]
    p=o.data.splines[0].points[1]
    p.co=(*(o.matrix_world.inverted()@anchor.matrix_world.translation),1)
    h=o.modifiers.new('Follow puppet attachment','HOOK')
    h.object=anchor; h.vertex_indices_set([1]); h.strength=1.0
    h.matrix_inverse=anchor.matrix_world.inverted()@o.matrix_world
    h.falloff_type='NONE'
r['Strings_Visible']=True
r.id_properties_ui('Strings_Visible').update(description='Visibility only; does not simulate broken strings. Body remains independently animatable.')
for o in bpy.data.collections['CHAR_HERO_STRINGS'].objects:
    for path in ['hide_render','hide_viewport']:
        d=o.driver_add(path).driver; d.type='SCRIPTED'; d.expression='1-visible'
        v=d.variables.new();v.name='visible';v.type='SINGLE_PROP'
        v.targets[0].id=r;v.targets[0].data_path='["Strings_Visible"]'

bpy.context.view_layer.update()
# Calibrate pole angles to the pre-existing bend plane with IK enabled temporarily.
calibration={}
for key in targets:
    kind,side=key.split('.')
    mid=r.pose.bones[('Knee.' if kind=='Foot' else 'Elbow.')+side]
    c=mid.constraints['Animator '+kind+' IK']
    expected=mid.head.copy()
    prop=kind+'_IK_'+side
    r[prop]=1.0; r.update_tag()
    best=(float('inf'),0)
    for i in range(73):
        angle=-math.pi+i*math.tau/72
        c.pole_angle=angle
        bpy.context.view_layer.update()
        err=(mid.head-expected).length
        if err<best[0]: best=(err,angle)
    c.pole_angle=best[1]
    calibration[key]={'joint_error':best[0],'angle':best[1]}
    r[prop]=0.0; r.update_tag(); bpy.context.view_layer.update()
state['calibration']=calibration
print('POLE CALIBRATION',calibration)
print('NEUTRAL MATRIX ERROR',max(max(abs(o.matrix_world[i][j]-state['world'][o.name][i][j]) for i in range(4) for j in range(4)) for o in char))
print('Rig prepared:',len(r.data.bones),'bones. No keyframes created.')
