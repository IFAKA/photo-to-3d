"""Scale a GLB so its width (X) is WIDTH_CM, keep textures as JPEG. usage: set_width.py IN.glb OUT.glb WIDTH_CM"""
import sys, io, trimesh
from PIL import Image
s = trimesh.load(sys.argv[1])
s.apply_scale((float(sys.argv[3]) / 100) / (s.bounds[1][0] - s.bounds[0][0]))
for g in s.geometry.values():
    m = getattr(g.visual, "material", None)
    t = getattr(m, "baseColorTexture", None)
    if t is not None and t.format != "JPEG":
        b = io.BytesIO(); t.convert("RGB").save(b, "JPEG", quality=85); b.seek(0); m.baseColorTexture = Image.open(b)
s.export(sys.argv[2])
