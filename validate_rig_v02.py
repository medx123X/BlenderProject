import bpy, math, json
from mathutils import Vector, Quaternion
r=bpy.data.objects['RIG_HERO']
state=bpy.app.driver_namespace['rig_v02_validation']
neutral={p.name:p.matrix_basis.copy() for p in r.pose.bones}
state['neutral_all']=neutral
def update():
    r.update_tag();bpy.context.view_layer.update()
def reset():
    for p in r.pose.bones:p.matrix_basis=neutral[p.name]
    for k in ['Foot_IK_L','Foot_IK_R','Hand_IK_L','Hand_IK_R','Suspension_String_Follow','Hand_String_Follow_L','Hand_String_Follow_R']:r[k]=0.0
    update()
results={}
# Each main chain can move independently; the static scenery and controller rigs are untouched.
samples={'Head':'HERO2_Head_Anatomical','Torso':'HERO2_Torso_Core','Pelvis':'HERO2_Pelvis','UpperArm.L':'HERO2_L_UpperArm','Elbow.L':'HERO2_L_Forearm','Wrist.L':'HERO2_L_Hand_Palm','UpperLeg.L':'HERO2_L_UpperLeg','Knee.L':'HERO2_L_LowerLeg','Foot.L':'HERO2_L_Foot_Shoe','UpperArm.R':'HERO2_R_UpperArm','Elbow.R':'HERO2_R_Forearm','Wrist.R':'HERO2_R_Hand_Palm','UpperLeg.R':'HERO2_R_UpperLeg','Knee.R':'HERO2_R_LowerLeg','Foot.R':'HERO2_R_Foot_Shoe'}
for bn,on in samples.items():
    reset(); obj=bpy.data.objects[on]; old=obj.matrix_world.copy()
    p=r.pose.bones[bn];p.matrix_basis=neutral[bn]@Quaternion((1,0,0),math.radians(20)).to_matrix().to_4x4();update()
    change=max(abs(obj.matrix_world[i][j]-old[i][j]) for i in range(4) for j in range(4))
    assert change>.01,(bn,'did not move')
    results[bn]=round(change,6)
reset()
# Optional pull links: switch on at baseline, then move a fingertip target, restore it.
pulls=[]
for bn,tn,prop in [('CTRL_Suspension','STRING_TARGET_L_Index','Suspension_String_Follow'),('CTRL_Hand.L_IK','STRING_TARGET_L_Pinky','Hand_String_Follow_L'),('CTRL_Hand.R_IK','STRING_TARGET_R_Index','Hand_String_Follow_R')]:
    reset();p=r.pose.bones[bn];target=bpy.data.objects[tn]
    base=p.matrix.translation.copy();r[prop]=1.;update()
    pop=(p.matrix.translation-base).length
    old=target.matrix_world.copy();m=old.copy();m.translation+=Vector((0,0,.12));target.matrix_world=m;update()
    delta=p.matrix.translation-base
    pulls.append((bn,pop,list(delta)))
    target.matrix_world=old;reset()
    assert pop<1e-4,(bn,'follow switch pop',pop)
    assert abs(delta.z-.12)<1e-4,(bn,'pull mismatch',list(delta))
# IK reach under a moderate crouch and one raised foot.
reset()
r.pose.bones['Pelvis'].location.y=-.08
for side in ['L','R']:
    r['Foot_IK_'+side]=1.
m=r.pose.bones['CTRL_Foot.L_IK'].matrix.copy();m.translation+=Vector((0,-.16,.12));r.pose.bones['CTRL_Foot.L_IK'].matrix=m
update()
ikerr={s:(r.pose.bones['Ankle.'+s].head-r.pose.bones['CTRL_Foot.'+s+'_IK'].head).length for s in ['L','R']}
assert max(ikerr.values())<.003,ikerr
for side in ['L','R']:
    r['Hand_IK_'+side]=1.
    p=r.pose.bones['CTRL_Hand.'+side+'_IK'];m=p.matrix.copy();m.translation+=Vector((-.12 if side=='L' else .12,-.12,.20));p.matrix=m
update()
handerr={s:(r.pose.bones['Wrist.'+s].head-r.pose.bones['CTRL_Hand.'+s+'_IK'].head).length for s in ['L','R']}
assert max(handerr.values())<.003,handerr
r.pose.bones['Torso'].matrix_basis=Quaternion((0,0,1),math.radians(7)).to_matrix().to_4x4()
r.pose.bones['Head'].matrix_basis=neutral['Head']@Quaternion((0,1,0),math.radians(15)).to_matrix().to_4x4()
update()
# Verify rendered curve mesh really reaches each moving attachment (within string radius).
deps=bpy.context.evaluated_depsgraph_get();stringerr={}
for o in bpy.data.collections['CHAR_HERO_STRINGS'].objects:
    a=bpy.data.objects['HERO2_StringAnchor_'+o.name.removeprefix('HERO_String_')].matrix_world.translation
    ev=o.evaluated_get(deps);mesh=ev.to_mesh()
    stringerr[o.name]=min((ev.matrix_world@v.co-a).length for v in mesh.vertices)
    ev.to_mesh_clear()
assert max(stringerr.values())<.015,stringerr
state['validation_results']={'joint_motion':results,'pull_links':pulls,'foot_IK_errors':ikerr,'hand_IK_errors':handerr,'string_surface_distance':stringerr}
state['test_pose']={p.name:p.matrix_basis.copy() for p in r.pose.bones}
print(json.dumps(state['validation_results'],indent=2))
print('Temporary combined test pose active for visual inspection. No keys.')
