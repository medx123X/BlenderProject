import bpy, json, math
from mathutils import Vector
s=bpy.context.scene;r=bpy.data.objects['RIG_HERO']
required=[1,48,96,120,144,168,192,216,240]
strings=list(bpy.data.collections['CHAR_HERO_STRINGS'].objects)
lengths={o.name:[] for o in strings}
max_ik=0.;max_seam=0.;max_endpoint=0.;max_step=0.;min_foot_z=1e9
previous=None;records=[]
pairs=[('UpperArm.L','Elbow.L'),('UpperArm.R','Elbow.R'),('Elbow.L','Wrist.L'),('Elbow.R','Wrist.R'),('UpperLeg.L','Knee.L'),('UpperLeg.R','Knee.R'),('Knee.L','Ankle.L'),('Knee.R','Ankle.R')]
for f in range(1,241):
    s.frame_set(f);dg=bpy.context.evaluated_depsgraph_get()
    ik=(r.pose.bones['Wrist.R'].head-r.pose.bones['CTRL_Hand.R_IK'].head).length
    max_ik=max(max_ik,ik)
    seam=max((r.pose.bones[a].tail-r.pose.bones[b].head).length for a,b in pairs)
    max_seam=max(max_seam,seam)
    wrist=bpy.data.objects['HERO2_StringAnchor_Right_Wrist'].matrix_world.translation.copy()
    if previous is not None:max_step=max(max_step,(wrist-previous).length)
    previous=wrist
    for side in ['L','R']:
        o=bpy.data.objects['HERO2_'+side+'_Shoe_Sole']
        min_foot_z=min(min_foot_z,min((o.matrix_world@Vector(c)).z for c in o.bound_box))
    for o in strings:
        lower=bpy.data.objects['HERO2_StringAnchor_'+o.name.removeprefix('HERO_String_')].matrix_world.translation
        upper=o.modifiers['Follow fingertip'].object.matrix_world.translation
        lengths[o.name].append((upper-lower).length)
        if f in required:
            ev=o.evaluated_get(dg);m=ev.to_mesh();verts=[ev.matrix_world@v.co for v in m.vertices]
            # Tube surface should lie one radius from both endpoint centers.
            max_endpoint=max(max_endpoint,min((v-lower).length for v in verts),min((v-upper).length for v in verts))
            ev.to_mesh_clear()
    if f in required:records.append({'frame':f,'wrist_world':list(wrist),'IK_error':ik,'joint_seam_error':seam})
report={'frames_checked':240,'visual_checkpoint_frames':required,'max_right_wrist_IK_error':max_ik,'max_joint_seam_error':max_seam,'max_string_endpoint_surface_distance':max_endpoint,'max_wrist_travel_per_frame':max_step,'minimum_sole_world_z':min_foot_z,'string_lengths':{n:{'min':min(v),'max':max(v),'max_deviation_percent':100*max(abs(x-v[0]) for x in v)/v[0]} for n,v in lengths.items()},'checkpoints':records}
assert max_ik<.002,report
assert max_seam<.002,report
assert max_endpoint<.005,report
assert max_step<.06,report
t=bpy.data.texts.new('AWAKENING_VALIDATION.json');t.write(json.dumps(report,indent=2))
bpy.app.driver_namespace['awakening_report']=report
s.frame_set(1)
print(json.dumps(report,indent=2))
