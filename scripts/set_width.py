"""Scale a GLB so its width (X) is WIDTH_CM. usage: set_width.py IN.glb OUT.glb WIDTH_CM"""
import sys, trimesh
s = trimesh.load(sys.argv[1])
s.apply_scale((float(sys.argv[3]) / 100) / (s.bounds[1][0] - s.bounds[0][0]))
s.export(sys.argv[2])
