import bpy, os, sys
from mathutils import Vector
s=bpy.context.scene
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
kind=args[0] if args else 'full'
single='single' in args
base=os.path.dirname(bpy.data.filepath)
folder=os.path.join(base,'Awakening_Preview_Frames',kind)
os.makedirs(folder,exist_ok=True)
# Preview settings are confined to this background Blender process. Never save them into the project.
try:s.render.engine='BLENDER_WORKBENCH'
except TypeError as exc:raise RuntimeError('Workbench preview unavailable: '+str(exc))
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'
sh=s.display.shading
sh.light='STUDIO';sh.color_type='MATERIAL';sh.show_shadows=True;sh.show_cavity=True
sh.cavity_type='BOTH';sh.show_specular_highlight=True
sh.background_type='WORLD'
s.display.render_aa='8'
if kind=='close':
    s.render.resolution_x=540;s.render.resolution_y=540
    data=bpy.data.cameras.new('Preview close camera');cam=bpy.data.objects.new('Preview close camera',data);s.collection.objects.link(cam)
    cam.location=(1.1,-7.7,3.7);cam.rotation_euler=(Vector((.53,-.25,3.65))-cam.location).to_track_quat('-Z','Y').to_euler();data.lens=63;s.camera=cam
for f in ([144] if single else range(1,241)):
    s.frame_set(f);s.render.filepath=os.path.join(folder,f'{f:04d}.png')
    bpy.ops.render.render(write_still=True)
    if f%24==0:print('PREVIEW_PROGRESS',kind,f,flush=True)
print('PREVIEW_DONE',kind,flush=True)
