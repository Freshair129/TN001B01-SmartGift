"""Local-only video review server with byte-range support for native scrubbing."""
import functools
import http.server
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'outputs/v4'


class RangeHandler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        self.remaining = None
        requested = self.headers.get('Range')
        path = Path(self.translate_path(self.path))
        if not requested or not path.is_file():
            return super().send_head()
        size = path.stat().st_size
        match = re.fullmatch(r'bytes=(\d*)-(\d*)', requested.strip())
        if not match or not any(match.groups()):
            self.send_error(416)
            return None
        low, high = match.groups()
        start = int(low) if low else max(0, size-int(high))
        end = min(size-1, int(high)) if low and high else size-1
        if start > end or start >= size:
            self.send_response(416)
            self.send_header('Content-Range', f'bytes */{size}')
            self.end_headers()
            return None
        stream = path.open('rb')
        stream.seek(start)
        self.remaining = end-start+1
        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(str(path)))
        self.send_header('Content-Length', str(self.remaining))
        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.end_headers()
        return stream

    def end_headers(self):
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def copyfile(self, source, target):
        if self.remaining is None:
            return super().copyfile(source,target)
        while self.remaining:
            data = source.read(min(65536,self.remaining))
            if not data:
                break
            target.write(data)
            self.remaining -= len(data)


http.server.ThreadingHTTPServer(('127.0.0.1',8777),functools.partial(RangeHandler,directory=str(ROOT))).serve_forever()
