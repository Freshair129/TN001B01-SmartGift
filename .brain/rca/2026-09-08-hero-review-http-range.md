# Hero review seek failure

- Symptom: review slider changed to119 but both decoded videos returned to currentTime0.
- Evidence: Chromium reported duration4, readyState4, buffered[0,4] but seekable[0,0] for both files. A request with `Range: bytes=0-99` received HTTP200 from Python SimpleHTTP/0.6 rather than206. Offline FFmpeg verification passed for all120 frames and shared decoded prefix0–22.
- Root cause: the temporary Python3.12 static server does not implement byte ranges, which this browser requires for MP4 seeking. The video files themselves contain faststart metadata and valid frequent keyframes.
- Why it escaped detection: file/decoder validation cannot prove the HTTP transport contract; the integration test was the first browser seek attempt.
- Prevention: serve the isolated local review directory with a single-range HTTP handler; check206/Content-Range and then repeat native playback, reverse seeking and browser pixel comparison. Production Nginx is not modified.
