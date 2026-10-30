import sys, trimesh, numpy as np
src, out, y, R = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
s = trimesh.load(src); g = list(s.geometry.values())[0]
a = np.asarray(g.visual.material.baseColorTexture.convert('RGB')).astype(int)
uv = g.visual.uv; h, w = a.shape[:2]; v = g.vertices
px = a[((1-uv[:,1])*(h-1)).astype(int), (uv[:,0]*(w-1)).astype(int)]
r = np.hypot(v[:,0], v[:,2]); sel = (r < 0.4) & (v[:,1] > -0.01) & (v[:,1] < 0.05)
col = np.median(px[sel], axis=0).astype(np.uint8); print("plug color", col)
disk = trimesh.creation.cylinder(radius=R, height=0.004, sections=96)
disk.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1,0,0]))
disk.apply_translation([0, y, 0])
disk.visual = trimesh.visual.ColorVisuals(disk, face_colors=np.r_[col, 255])
s.add_geometry(disk, geom_name="plug")
s.export(out); print("wrote", out)
