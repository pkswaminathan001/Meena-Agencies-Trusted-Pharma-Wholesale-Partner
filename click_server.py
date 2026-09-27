"""click_server.py — Receives browser click events into audit_pro.jsonl on port 8766."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
import json, threading

try:
    from audit_pro import log_event
except Exception:
    def log_event(user, action, page="", details=""): pass

PORT = 8766
LOCK = threading.Lock()

class ClickHandler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200); self._cors(); self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8", errors="ignore")
            data = json.loads(body) if body else {}
            with LOCK:
                log_event(
                    user=data.get("user", "GUEST"),
                    action="CLICK",
                    page=data.get("page", "")[:30],
                    details=f'label="{data.get("label","")}" xy=({data.get("x",0)},{data.get("y",0)})',
                )
            self.send_response(200); self._cors(); self.end_headers()
            self.wfile.write(b"ok")
        except Exception as e:
            self.send_response(500); self._cors(); self.end_headers()
            self.wfile.write(str(e).encode())

    def log_message(self, *args): pass

if __name__ == "__main__":
    print(f"🖱 Click server running on http://localhost:{PORT}")
    HTTPServer(("0.0.0.0", PORT), ClickHandler).serve_forever()
