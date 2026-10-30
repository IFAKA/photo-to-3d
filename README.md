# photo-to-3d

Turn one product photo into a small, real-size 3D file (GLB) for the shop's "Ver en mi mesa" AR feature.
The shop only needs the finished file: put it in the shop's `public/models/` and add one line in `lib/models3d.ts`.

```
./photo3d examples/cheesecake-input.jpg cheesecake.glb 24 --plug -0.012,0.44
#          photo                        output         width cm   hide holes under the cake top
```

Steps (about 2 to 4 minutes with the cloud model, 5 seconds without it):
1. **Photo to raw 3D** (`scripts/cloud.py`): free TRELLIS.2 on Hugging Face (MIT license). It has a daily free GPU
   quota (about 2 minutes of GPU per run, resets in about 24 h). `--raw FILE.glb` skips this step.
2. **Plug** (`scripts/plug.py`, optional): generated models are hollow and show dark gaps at cracks. A hidden disc
   under the top surface, in the colour of the top, hides them. Cakes: Y=-0.012, R=0.44 (metres, model units).
3. **Real size** (`scripts/set_width.py`): scale so the width equals the real width in cm. AR shows this size.
4. **Shrink** (`scripts/bl_shrink.py`, Blender): keep 25% of the faces, JPEG textures, metallic set to 0
   (the model came out about 44% metal, which looked wrong). 11 MB becomes about 4 MB with the same colours.

Needs `python3` and `blender` on the PATH. The first run makes `.venv` by itself.

## Facts learned
- Only the width is real. The height is the AI's guess from the photo. For other sizes the shop scales the model.
- Do not decimate with trimesh: it scrambles the UVs and the colours. Use Blender.
- AR on Android: WebXR in Chrome over https works. Scene Viewer (the Google app) crashed on a Galaxy S10.
  ngrok free adds a warning page that blocks the model file; a Cloudflare quick tunnel does not.
- Hands in front of the model (occlusion) needs a phone with real depth. The S10 depth map never sees a hand.
- A client's shop must never be used in marketing: use a made-up shop.

## Local on a Mac (not run yet)
`trellis-mac` (PyTorch on Apple GPU, needs 24 GB or more) can replace step 1. Notes from the setup attempt:
- Install: clone https://github.com/shivampkumar/trellis-mac, `SKIP_METAL=1 bash setup.sh` (about 16 GB of weights).
- The background remover in its pipeline is RMBG-2.0 (non-commercial license). Use BiRefNet (MIT) instead:
  in `TRELLIS.2/trellis2/pipelines/trellis2_image_to_3d.py` replace the `getattr(rembg, ...)` line with
  `rembg.BiRefNet(model_name='ZhengPeng7/BiRefNet')`.
- It needs the gated model `facebook/dinov3-vitl16-pretrain-lvd1689m` (Meta license form on Hugging Face).
  Weights load took about 4 minutes and 10 GB of memory before it stopped on that gate.
- Run: `python generate.py photo.jpg --output out --texture-size 2048`

## How much detail

More detail than the eye can see only costs download time and size. Measured on the cheesecake (24 cm):

| faces / texture | file | look |
|---|---|---|
| 73k / 2048 | 4.0 MB | clean, even very close |
| **50k / 1024 (default)** | 2.4 MB | clean at AR distance, small shards only if you zoom to 30 cm |
| 30k / 1024 | 1.7 MB | shards on the fruit when close |
| 20k / 1024, 15k / 512 | 1.2 MB / 0.9 MB | too rough for AR |

Why: the drawer shows the model about 420 px wide. In AR on a 1440 px phone the cake is about 600 px (50 cm away) to 1000 px (30 cm). A 1024 px texture already matches that, so 2048 px is wasted. Faces matter more than texture here, because decimation makes the visible shards. Use `--faces` and `--tex` to change it (a flat product like a box can use fewer faces).

## Local run (no cloud quota)

`photo3d-local PHOTO OUT.glb WIDTH_CM` does everything on the Mac. Cheesecake: about 4–7 min for the AI step, then 6 s to finish. Result: 50k faces, 1024 px, 1.7 MB, with no plug needed. It looks smoother than the cloud one.

Setup (once): clone `shivampkumar/trellis-mac`, run `SKIP_METAL=1 bash setup.sh`, `uv pip install -p .venv/bin/python einops`, apply `local/trellis-mac.patch` to `generate.py` and make `.float()` in `TRELLIS.2/trellis2/pipelines/rembg/BiRefNet.py` `to()`. Also use `ZhengPeng7/BiRefNet` instead of RMBG-2.0 (licence). Then `export TRELLIS_MAC=/path/to/trellis-mac`.

Three bugs found on the way (all fixed in the patch / scripts):
1. The mesh from trellis-mac is wound inside-out. It looks like shards until you flip the faces.
2. Its own UV unwrap (xatlas) breaks the mesh into thousands of tiny pieces. So we skip it: colour the vertices from the voxels (`local_color.py`), then Blender makes a clean low copy and bakes the colour onto it (`bl_local.py`).
3. Blender's voxel remesh makes quads, so "55k faces" was really 110k triangles. Triangulate first. Use smooth shading, or every triangle gets its own 3 vertices and the file is 3x bigger.

Do not run `bl_shrink.py` on this result: it breaks the texture. `photo3d-local` does not.
