import bpy,os,time
s=bpy.context.scene;a=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D');sp=a.spaces.active
folder=r'C:\Users\Asus\Desktop\StringsOfFreedom\Awakening_Viewport_Frames'
os.makedirs(folder,exist_ok=True)
old=(s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.render.filepath,s.render.image_settings.file_format,sp.shading.type,sp.overlay.show_overlays,sp.region_3d.view_perspective,s.frame_current)
try:
    s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
    sp.shading.type='MATERIAL';sp.overlay.show_overlays=False;sp.region_3d.view_perspective='CAMERA'
    start=time.time()
    with bpy.context.temp_override(area=a,region=next(r for r in a.regions if r.type=='WINDOW')):
        for f in range(first_frame,last_frame+1):
            s.frame_set(f);s.render.filepath=os.path.join(folder,f'{f:04d}.png')
            bpy.ops.render.opengl(write_still=True,view_context=True)
    print('Captured',first_frame,'through',last_frame,'in',round(time.time()-start,2),'seconds')
finally:
    s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.render.filepath,s.render.image_settings.file_format,sp.shading.type,sp.overlay.show_overlays,sp.region_3d.view_perspective,frame=old
    s.frame_set(frame)
