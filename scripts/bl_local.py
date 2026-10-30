# Vertex-coloured raw mesh -> small UV-textured GLB (Y up).
# Usage: blender -b -P bl_local.py -- IN.ply OUT.glb FACES TEX
# Makes a clean low copy (voxel remesh -> decimate -> smooth -> UV) and bakes the colours from the full mesh onto it.
import bpy, sys, math
a = sys.argv[sys.argv.index("--") + 1:]; src, out, faces, tex = a[0], a[1], int(a[2]), int(a[3])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.ply_import(filepath=src)
hi = bpy.context.selected_objects[0]
lo = hi.copy(); lo.data = hi.data.copy(); lo.name = "lo"; bpy.context.collection.objects.link(lo)
def sel(o):
    bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
def mod(o, kind, **kw):
    sel(o); m = o.modifiers.new("m", kind)
    for k, v in kw.items(): setattr(m, k, v)
    bpy.ops.object.modifier_apply(modifier="m")
def cleanup(o):
    sel(o); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=0.0005); bpy.ops.mesh.fill_holes(sides=0)
    bpy.ops.mesh.dissolve_degenerate(threshold=0.0005); bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")
cleanup(lo)
# Voxel remesh gives the cleanest surface, but it collapses on open meshes (it keeps only a few percent of the faces).
# Then decimate the cleaned full mesh directly.
keep = lo.data.copy()
mod(lo, "REMESH", mode="VOXEL", voxel_size=0.004)
if len(lo.data.polygons) < faces * 0.5:
    print("remesh collapsed, decimating directly"); lo.data = keep; cleanup(lo)
mod(lo, "TRIANGULATE")
n = len(lo.data.polygons); print("remesh", n)
mod(lo, "DECIMATE", ratio=min(1.0, faces / n))
mod(lo, "SMOOTH", factor=0.5, iterations=4)
cleanup(lo)
print("faces", len(lo.data.polygons))
sel(lo); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(89), island_margin=0.02); bpy.ops.object.mode_set(mode="OBJECT")
img = bpy.data.images.new("bake", tex, tex)
# hi: emission from vertex colour; lo: image node active
mh = bpy.data.materials.new("h"); mh.use_nodes = True; nt = mh.node_tree; nt.nodes.clear()
ca = nt.nodes.new("ShaderNodeAttribute"); ca.attribute_name = hi.data.color_attributes[0].name
em = nt.nodes.new("ShaderNodeEmission"); on = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(ca.outputs["Color"], em.inputs["Color"]); nt.links.new(em.outputs[0], on.inputs[0])
hi.data.materials.clear(); hi.data.materials.append(mh)
ml = bpy.data.materials.new("l"); ml.use_nodes = True; nl = ml.node_tree; nl.nodes.clear()
tn = nl.nodes.new("ShaderNodeTexImage"); tn.image = img; nl.nodes.active = tn
lo.data.materials.clear(); lo.data.materials.append(ml)
sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.samples = 1; sc.cycles.device = "CPU"
sc.render.bake.margin = 16
sel(hi); lo.select_set(True); bpy.context.view_layer.objects.active = lo
bpy.ops.object.bake(type="EMIT", use_selected_to_active=True, cage_extrusion=0.03, max_ray_distance=0.12)
# final material: bake -> base colour
nl.nodes.clear()
pb = nl.nodes.new("ShaderNodeBsdfPrincipled"); pb.inputs["Metallic"].default_value = 0; pb.inputs["Roughness"].default_value = 0.8
tn = nl.nodes.new("ShaderNodeTexImage"); tn.image = img; on = nl.nodes.new("ShaderNodeOutputMaterial")
nl.links.new(tn.outputs["Color"], pb.inputs["Base Color"]); nl.links.new(pb.outputs[0], on.inputs[0])
img.pack()
bpy.data.objects.remove(hi, do_unlink=True)
sel(lo); bpy.ops.object.shade_smooth()
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG", export_jpeg_quality=85, use_selection=True)
