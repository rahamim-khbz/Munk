#!/usr/bin/env python3
"""
Local HTTP review and redline persistence server for the dual-scan Redline Reader.
Serves static scans/assets and handles /api/page/<id> and /api/feedback endpoints.
"""

import http.server
import json
import os
import urllib.parse

FEEDBACK_FILE = "data/faur_review_feedback.json"
PAGES_DIR = "data/faur_pages"
QUEUE_FILE = "data/faur_queue_state.json"


class ReviewServerHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.startswith("/api/page/"):
            page_id = parsed.path.replace("/api/page/", "").strip()
            page_path = os.path.join(PAGES_DIR, f"page_{page_id}.json")
            if os.path.exists(page_path):
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                with open(page_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'{"error": "Page not found"}')
            return

        if parsed.path == "/api/queue":
            if os.path.exists(QUEUE_FILE):
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                with open(QUEUE_FILE, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(b'{"pages": {}}')
            return

        if parsed.path == "/api/feedback":
            if os.path.exists(FEEDBACK_FILE):
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                with open(FEEDBACK_FILE, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(b'{}')
            return

        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/feedback":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                payload = json.loads(body.decode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

            page_id = payload.get("page_id")
            if not page_id:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Missing page_id"}')
                return

            current_feedback = {}
            if os.path.exists(FEEDBACK_FILE):
                try:
                    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                        current_feedback = json.load(f)
                except Exception:
                    current_feedback = {}

            current_feedback[page_id] = payload
            os.makedirs(os.path.dirname(FEEDBACK_FILE), exist_ok=True)
            with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
                json.dump(current_feedback, f, indent=2)

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(b'{"status": "saved"}')
            return

        self.send_response(404)
        self.end_headers()


def run_server(port: int = 8765):
    server_address = ("", port)
    httpd = http.server.HTTPServer(server_address, ReviewServerHandler)
    print(f"Serving Faur Redline Review Server at http://localhost:{port}/faur_review_reader.html")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
