# Colour the raw local-TRELLIS mesh from its voxels. Usage: local_color.py VOX.npz OUT.ply
import sys, numpy as np, trimesh
from scipy.spatial import cKDTree
d = np.load(sys.argv[1])
verts, faces, coords, attrs, origin, vs = d["verts"], d["faces"][:, ::-1], d["coords"], d["attrs"], d["origin"], float(d["vs"])
tree = cKDTree(coords.astype(np.float32) * vs + origin + vs * 0.5)
dist, idx = tree.query(verts, k=8, workers=-1)
w = 1.0 / (dist + vs * 0.1); w[dist > vs * 2] = 0
w /= np.maximum(w.sum(1, keepdims=True), 1e-9)
col = np.clip((attrs[idx][..., :3] * w[..., None]).sum(1), 0, 1)
rgba = np.c_[(col * 255).astype(np.uint8), np.full(len(col), 255, np.uint8)]
trimesh.Trimesh(verts, faces, vertex_colors=rgba, process=False).export(sys.argv[2])
print("coloured", len(verts), "verts")
