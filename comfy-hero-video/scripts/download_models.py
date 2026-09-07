"""Download the Wan 2.2 5B TI2V weights the template needs into the local ComfyUI models folders.

Idempotent: skips files that already exist. Run: python scripts/download_models.py
"""
import os
import shutil
import sys
import time

from huggingface_hub import hf_hub_download

sys.stdout.reconfigure(encoding='utf-8')
MODELS_ROOT = r'C:\Users\pc\Documents\comfy\ComfyUI\models'
STAGING = os.path.join(MODELS_ROOT, '_hf_staging')

FILES = [
    ('Comfy-Org/Wan_2.2_ComfyUI_Repackaged', 'split_files/vae/wan2.2_vae.safetensors', 'vae'),
    ('Comfy-Org/Wan_2.1_ComfyUI_repackaged', 'split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors', 'text_encoders'),
    ('Comfy-Org/Wan_2.2_ComfyUI_Repackaged', 'split_files/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors', 'diffusion_models'),
]

os.makedirs(STAGING, exist_ok=True)
for repo, filename, folder in FILES:
    name = os.path.basename(filename)
    target = os.path.join(MODELS_ROOT, folder, name)
    if os.path.exists(target) and os.path.getsize(target) > 1_000_000:
        print(f'skip   {name} (exists, {os.path.getsize(target)/1e9:.2f} GB)', flush=True)
        continue
    t0 = time.time()
    print(f'start  {name} from {repo}', flush=True)
    path = hf_hub_download(repo_id=repo, filename=filename, local_dir=STAGING)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    shutil.move(path, target)
    print(f'done   {name} -> {target} ({os.path.getsize(target)/1e9:.2f} GB, {time.time()-t0:.0f}s)', flush=True)

shutil.rmtree(STAGING, ignore_errors=True)
print('ALL DONE', flush=True)
