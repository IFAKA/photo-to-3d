"""Batch voxel dump for trellis-mac: load TRELLIS once, then for each line of LIST ("photo prefix")
write prefix_vox.npz (renamed into place when complete). Usage: python batch_vox.py LIST [--steps 6] [--seed 42]
Copy next to trellis-mac/generate.py (it reuses its backend setup)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate  # noqa: F401  (sets backends and paths; main() is not run)
import torch, numpy as np
from PIL import Image
lst = sys.argv[1]; steps = int(sys.argv[sys.argv.index("--steps") + 1]) if "--steps" in sys.argv else 6
seed = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 42
from trellis2.pipelines.trellis2_image_to_3d import Trellis2ImageTo3DPipeline
p = Trellis2ImageTo3DPipeline.from_pretrained("microsoft/TRELLIS.2-4B"); p.to(torch.device("mps"))
ov = {"steps": steps}
for line in open(lst):
    if not line.strip(): continue
    photo, prefix = line.split()
    t = time.time()
    try:
        o = p.run(Image.open(photo), seed=seed, pipeline_type="512", sparse_structure_sampler_params=ov, shape_slat_sampler_params=ov, tex_slat_sampler_params=ov)
        m = o[0] if isinstance(o, list) else o
        np.savez(prefix + "_tmp.npz", verts=np.asarray(m.vertices.cpu().numpy(), dtype=np.float32), faces=np.asarray(m.faces.cpu().numpy(), dtype=np.int32),
                 coords=m.coords.cpu().float().numpy(), attrs=m.attrs.cpu().float().numpy(), origin=m.origin.cpu().float().numpy(), vs=float(m.voxel_size))
        os.replace(prefix + "_tmp.npz", prefix + "_vox.npz")
    except Exception as e:
        print("FAILED", photo, repr(e), flush=True); open(prefix + "_failed", "w").write(repr(e))
    print(f"gen {photo} {time.time()-t:.0f}s", flush=True)
