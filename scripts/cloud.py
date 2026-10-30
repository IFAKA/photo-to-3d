"""Photo -> raw 3D (GLB) with the free TRELLIS.2 Hugging Face Space. usage: cloud.py PHOTO OUT.glb [seed] [resolution] [decimation] [texture]"""
import shutil, sys, time
from gradio_client import Client, handle_file

img, out = sys.argv[1], sys.argv[2]
seed, res, dec, tex = (int(sys.argv[3]) if len(sys.argv) > 3 else 7), (sys.argv[4] if len(sys.argv) > 4 else "1024"), \
    (int(sys.argv[5]) if len(sys.argv) > 5 else 300000), (int(sys.argv[6]) if len(sys.argv) > 6 else 2048)
t = time.time()
c = Client("microsoft/TRELLIS.2", verbose=False)
c.predict(api_name="/start_session")
pre = c.predict(handle_file(img), api_name="/preprocess_image")
c.predict(handle_file(pre if isinstance(pre, str) else pre["path"]), seed, res, api_name="/image_to_3d")
glb, _ = c.predict(dec, tex, api_name="/extract_glb")
shutil.copy(glb, out)
print(f"raw model {out} ({time.time() - t:.0f} s)")
