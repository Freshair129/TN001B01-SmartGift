---
version: "0.1.0b"
created_at: "2026-09-07T22:06:35+07:00,RWANG,uncommitted"
last_update: "2026-09-07T22:06:35+07:00,RWANG"
status: beta
attributes:
  scope: comfy-hero-video
---

# Hero conform loses the final frame

## Symptom

Approved v3 source MP4s decode to 120 frames, duration 4.00 s. Existing `conform.py` produced 119 frames, duration 3.97 s, despite eight I-frames and passing first-frame parity.

## Evidence

`outputs/v3/verification_raw.json`, `conform.log`, `conformed_west_ffmpeg.log` and controlled `conform_filter_experiment.json`:

- Direct decode: 120 frames, final PTS 3.966667.
- scale alone or crop alone: 120 frames.
- `scale=1920:1080,fps=30`: 119 frames.
- `fps=30,scale=1920:1080,crop=1920:1080`: 120 frames.
- Setting `eof_action=pass` after scale does not restore the frame.
- Replacing `-t 4` with a frame limit, or removing the output limit, does not restore it (`conform_rca_experiment.json`).

## Root Cause

The final frame is lost in this installed imageio FFmpeg 7.1 filter chain when scale precedes fps. The failure is isolated to that ordering by controlled experiments; the underlying FFmpeg implementation mechanism has not been established. The original source renderer is complete and the output time limit is not the cause.

## Why the issue escaped detection

The existing conform script reports frame count but never asserts it. It copies both files even when required gates fail. Eight I-frames and first-frame parity alone do not establish 4.0 s duration.

## Proposed prevention

Normalize fps before spatial filters, preserving all 120 frames; assert 120 frames, eight I-frames and parity before either copy. Run the independent v3 artifact verifier afterward to validate actual decoded timestamps, duration, High profile, no audio and moov ordering. This is a LOW isolated correction necessary for the approved v3 delivery contract; no web behavior or product data changes.

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.1.0b | 2026-09-07 | beta | Isolate conform filter ordering and define narrow correction | uncommitted | RWANG |
