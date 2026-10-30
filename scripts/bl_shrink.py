import bpy, sys
a = sys.argv[sys.argv.index("--")+1:]; src, out, ratio = a[0], a[1], float(a[2])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for o in bpy.context.scene.objects:
    if o.type == 'MESH' and len(o.data.polygons) > 1000:
        m = o.modifiers.new("d", 'DECIMATE'); m.ratio = ratio
        bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier="d")
        print("faces", o.name, len(o.data.polygons))
    for s in (o.material_slots if o.type=='MESH' else []):
        if s.material and s.material.use_nodes:
            for n in s.material.node_tree.nodes:
                if n.type == 'BSDF_PRINCIPLED':
                    for l in list(n.inputs['Metallic'].links): s.material.node_tree.links.remove(l)
                    n.inputs['Metallic'].default_value = 0.0
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_image_format='JPEG', export_jpeg_quality=88)
