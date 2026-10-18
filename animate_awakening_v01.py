import bpy, math, json, os
from mathutils import Vector, Quaternion

s=bpy.context.scene
r=bpy.data.objects['RIG_HERO']; hand=bpy.data.objects['RIG_Controller_R']
assert not r.animation_data.action if r.animation_data else True
assert not os.path.exists(os.path.join(os.path.dirname(bpy.data.filepath),'StringsOfFreedom_AnimationTest_v01.blend'))
baseline={o.name:{p.name:p.matrix_basis.copy() for p in o.pose.bones} for o in [r,hand]}
bpy.app.driver_namespace['awakening_baseline']=baseline
s.frame_start=1;s.frame_end=240;s.render.fps=24;s.render.fps_base=1
s.tool_settings.use_keyframe_insert_auto=False
for prop,val in {'Foot_IK_L':0.,'Foot_IK_R':0.,'Hand_IK_L':0.,'Hand_IK_R':1.,'Suspension_String_Follow':0.,'Hand_String_Follow_L':0.,'Hand_String_Follow_R':1.,'Strings_Visible':True}.items():
    r[prop]=val
    r.keyframe_insert(data_path='["'+prop+'"]',frame=1,group='Rig modes - held constant')
    r.keyframe_insert(data_path='["'+prop+'"]',frame=240,group='Rig modes - held constant')

def qkey(obj,bn,f,world_angles):
    p=obj.pose.bones[bn];p.rotation_mode='QUATERNION'
    q=baseline[obj.name][bn].to_quaternion()
    axes=p.bone.matrix_local.to_3x3().inverted()
    for axis,angle in zip([(1,0,0),(0,1,0),(0,0,1)],world_angles):
        if angle:q=q@Quaternion(axes@Vector(axis),math.radians(angle))
    p.rotation_quaternion=q
    p.keyframe_insert('rotation_quaternion',frame=f,group=bn)

def lkey(obj,bn,f,delta):
    p=obj.pose.bones[bn]
    p.location=baseline[obj.name][bn].translation+p.bone.matrix_local.to_3x3().inverted()@Vector(delta)
    p.keyframe_insert('location',frame=f,group=bn)

# A near-still, long-period swing; the feet hover just clear of the stage.
for f,x,y,z in [(1,.15,-.28,0),(24,-.12,.30,0),(48,.10,-.22,0),(72,-.08,.18,0),(96,.08,-.16,0),(120,-.07,.22,0),(144,.06,.32,0),(168,-.09,.18,0),(192,.05,.24,0),(216,-.04,-.10,0),(240,.02,.07,0)]:
    qkey(r,'CTRL_Suspension',f,(x,y,z))
    lkey(r,'CTRL_Suspension',f,(0,0,.075))

# Head leads awareness; torso follows after a short delay. Final glance goes to the wrist string.
for f,pitch,turn in [(1,3,0),(32,3.4,0),(48,3,0),(58,2,0),(68,-2,0),(75,-1.5,0),(88,-10,0),(96,-12,0),(108,-12,0),(128,-10,2),(144,-8,4),(160,-6,5),(178,-5,6),(192,-4,8),(208,-1,14),(224,2,20),(240,2.5,22)]:
    qkey(r,'Head',f,(pitch,0,turn))
for f,pitch,lean in [(1,0,0),(48,0,0),(64,0,0),(80,-.7,0),(96,-1.3,0),(108,-1.3,0),(120,-.8,.5),(136,-.4,1.4),(144,-.2,1.7),(154,.15,1.1),(162,-.05,1.6),(170,.2,1.25),(181,-.1,1.5),(192,.1,1.0),(208,.2,.35),(220,-.2,-.25),(232,.05,.1),(240,0,.05)]:
    qkey(r,'Torso',f,(pitch,lean,0))
for f,angle in [(1,0),(104,0),(118,.3),(132,1.3),(144,2),(154,1.1),(162,1.7),(168,1.3),(176,1.8),(184,1.2),(192,1.4),(208,.5),(220,-.25),(232,.08),(240,0)]:
    qkey(r,'Shoulder.R',f,(0,angle,0))

# Right index curls first. Small whole-hand lift makes the external cause legible.
# Each tuple is frame, index-base flexion, index-middle flexion, overall pull amount.
pull=[(1,0,0,0),(48,0,0,0),(96,0,0,0),(100,1,.3,.05),(108,5,1.5,.28),(120,12,4,.75),(132,16,6,1),(144,16.5,6.2,1),(150,15.8,5.8,.98),(156,16.8,6.3,1.02),(162,16.2,6,1),(168,17,6.5,1.03),(174,16.3,6.1,1.0),(181,16.8,6.4,1.02),(187,16.1,6.0,.99),(192,15,5.5,.95),(200,12,4.4,.77),(208,7,2.4,.45),(216,2,.7,.13),(223,-.6,-.2,-.035),(231,.25,.08,.015),(240,0,0,0)]
for f,base,middle,amount in pull:
    for bn,angle in [('Index_Base.R',base),('Index_Middle.R',middle),('Index_Tip.R',middle*.2)]:
        p=hand.pose.bones[bn]
        p.rotation_quaternion=baseline[hand.name][bn].to_quaternion()@Quaternion((1,0,0),math.radians(angle))
        p.keyframe_insert('rotation_quaternion',frame=f,group=bn)
    lkey(hand,'Wrist.R',f,(.045*amount,.16*amount,.075*amount))

# Local effort against the externally driven target: millimetres, never a competing FK arm pose.
for f,resist in [(1,0),(48,0),(96,0),(144,0),(150,-.010),(156,-.022),(162,-.014),(168,-.026),(174,-.017),(181,-.024),(187,-.015),(192,-.018),(204,-.008),(216,0),(223,-.004),(232,.001),(240,0)]:
    lkey(r,'CTRL_Hand.R_IK',f,(0,0,.075+resist))
for f,angle in [(1,0),(96,0),(108,1),(132,7),(144,9),(156,7),(168,8.2),(181,7.3),(192,6),(208,2),(223,-1.5),(232,.6),(240,.3)]:
    qkey(r,'CTRL_Hand.R_IK',f,(angle,0,0))

# Tiny lower-body overlap, kept in FK to hang instead of planting the feet.
for bn,phase in [('UpperLeg.L',1),('UpperLeg.R',-.7)]:
    for f,a in [(1,0),(32,.18),(60,-.15),(88,.10),(112,-.08),(144,.15),(176,-.12),(204,.08),(228,-.04),(240,0)]:
        qkey(r,bn,f,(a*phase,0,0))

def curves(action):
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                yield from bag.fcurves
for obj,name in [(r,'AWAKENING | Puppet | 001-240'),(hand,'AWAKENING | Puppeteer right pull | 001-240')]:
    a=obj.animation_data.action;a.name=name
    for fc in curves(a):
        for k in fc.keyframe_points:
            k.interpolation='CONSTANT' if fc.data_path.startswith('["') else 'BEZIER'
            k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
for name,f in [('01 Suspended Silence',1),('02 First Awareness',49),('03 Forced Movement',97),('04 Resistance',145),('05 Realization',193)]:
    s.timeline_markers.new(name,frame=f)

# Static review camera includes the boy, strings, and visible cause above him.
data=bpy.data.cameras.new('CAM_Awakening_Test');cam=bpy.data.objects.new('CAM_Awakening_Test',data)
bpy.data.collections['CAMERAS'].objects.link(cam)
cam.location=(.8,-20.5,6.2)
cam.rotation_euler=(Vector((.53,-.25,6.05))-cam.location).to_track_quat('-Z','Y').to_euler()
data.lens=43;data.clip_end=200;s.camera=cam
s.frame_set(1);bpy.context.view_layer.update()
print('KEYED',[(o.name,o.animation_data.action.name,len(list(curves(o.animation_data.action)))) for o in [r,hand]])
print('Frame range:',s.frame_start,s.frame_end,'FPS',s.render.fps)
