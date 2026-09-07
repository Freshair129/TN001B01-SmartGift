#!/usr/bin/env bash
# Robust resumable downloads for the Wan 2.2 5B weights (curl -C -). Idempotent.
M="C:/Users/pc/Documents/comfy/ComfyUI/models"
LOG="C:/Users/pc/workspace/business-01-smart-gift/comfy-hero-video/outputs/download2.log"
dl() { # dir name url
  local dir="$1" name="$2" url="$3" tgt="$M/$1/$2"
  if [ -f "$tgt" ] && [ "$(stat -c %s "$tgt")" -gt 1000000000 ]; then echo "skip   $name (exists)" >> "$LOG"; return 0; fi
  echo "start  $name (curl)" >> "$LOG"
  curl -L --fail --retry 10 --retry-all-errors --retry-delay 5 -C - -sS -o "$tgt.part" "$url" 2>> "$LOG"
  local rc=$?
  if [ $rc -eq 0 ]; then mv -f "$tgt.part" "$tgt"; echo "done   $name ($(stat -c %s "$tgt") bytes)" >> "$LOG"; else echo "Error: curl rc=$rc for $name" >> "$LOG"; fi
  return $rc
}
dl text_encoders umt5_xxl_fp8_e4m3fn_scaled.safetensors "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors" &
dl diffusion_models wan2.2_ti2v_5B_fp16.safetensors "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors" &
wait
rc=0; for f in "$M/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors" "$M/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors"; do [ -f "$f" ] || rc=1; done
[ $rc -eq 0 ] && echo "ALL DONE" >> "$LOG"
echo "download exit=$rc" >> "$LOG"
