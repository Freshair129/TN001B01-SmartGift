"""
SmartGift Catalog UI HTTP Server & API Service
Serves the static web application and provides JSON endpoints for catalog data and audit logs.
"""

import os
import sys
import json
import mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

sys.stdout.reconfigure(encoding='utf-8')

PORT = 5180
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
CATALOG_PATH = os.path.join(BASE_DIR, "data-pipeline", "02_prepared", "smartgift_catalog_master.json")
AUDIT_LOG_PATH = os.path.join(BASE_DIR, "data-pipeline", "04_review_reports", "provenance_audit_log.jsonl")
FORMULA_PATH = os.path.join(BASE_DIR, "config", "pricing_rules_formula.yaml")
DIFF_REPORT_PATH = os.path.join(BASE_DIR, "data-pipeline", "04_review_reports", "catalog_version_diff_report.json")

class SmartGiftHTTPHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/catalog":
            self.serve_json_file(CATALOG_PATH)
        elif path == "/api/audit-logs":
            self.serve_audit_logs()
        elif path == "/api/diff-report":
            self.serve_json_file(DIFF_REPORT_PATH)
        elif path == "/api/formula":
            self.serve_formula()
        elif path == "/" or path == "/index.html":
            self.path = "/index.html"
            super().do_GET()
        else:
            super().do_GET()

    def serve_json_file(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        else:
            self.send_error(404, "File Not Found")

    def serve_audit_logs(self):
        entries = []
        if os.path.exists(AUDIT_LOG_PATH):
            with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entries.append(json.loads(line))
                        except Exception:
                            pass
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(entries, ensure_ascii=False).encode("utf-8"))

    def serve_formula(self):
        if os.path.exists(FORMULA_PATH):
            with open(FORMULA_PATH, "r", encoding="utf-8") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/yaml; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        else:
            self.send_error(404, "Formula Not Found")

def run():
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, SmartGiftHTTPHandler)
    print("=" * 70)
    print(f" 🚀 SmartGift Catalog UI Server running on http://localhost:{PORT}")
    print(f" 🏢 Enterprise Scope: Wannapa Workspace > Org-EtohGroup > SmartGift")
    print("=" * 70)
    httpd.serve_forever()

if __name__ == "__main__":
    run()
