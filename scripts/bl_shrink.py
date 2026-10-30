"""Shrink a GLB to a viewing budget. usage (blender -b -P): bl_shrink.py -- IN.glb OUT.glb FACES TEX_PX [JPEG_QUALITY]"""
import bpy, sys
a = sys.argv[sys.argv.index("--")+1:]
src, out, faces, tex = a[0], a[1], int(a[2]), int(a[3])
quality = int(a[4]) if len(a) > 4 else 85
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for o in bpy.context.scene.objects:
    if o.type == 'MESH' and len(o.data.polygons) > max(faces, 1000):
        m = o.modifiers.new("d", 'DECIMATE'); m.ratio = faces / len(o.data.polygons)
        bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier="d")
    if o.type == 'MESH':
        print("faces", o.name, len(o.data.polygons))
    for s in (o.material_slots if o.type == 'MESH' else []):
        if s.material and s.material.use_nodes:
            for n in s.material.node_tree.nodes:
                if n.type == 'BSDF_PRINCIPLED':
                    for l in list(n.inputs['Metallic'].links): s.material.node_tree.links.remove(l)
                    n.inputs['Metallic'].default_value = 0.0
for img in bpy.data.images:
    if max(img.size) > tex:
        img.scale(tex, tex)
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_image_format='JPEG', export_jpeg_quality=quality)
