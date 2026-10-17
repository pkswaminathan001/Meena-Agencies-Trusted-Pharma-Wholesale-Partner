"""Lightweight tracker — listens for visibility/idle events from browsers"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import json, os, threading

PORT = 8765  # separate from Streamlit
BASE = os.path.dirname(os.path.abspath(__file__))
BREAK_FILE = os.path.join(BASE, "breaks.json")
LOCK = threading.Lock()

def load_breaks():
    if os.path.exists(BREAK_FILE):
        with open(BREAK_FILE) as f: return json.load(f)
    return []

def save_breaks(data):
    with open(BREAK_FILE, "w") as f: json.dump(data, f, indent=2)

def record_event(worker, event):
    with LOCK:
        data = load_breaks()
        now = datetime.now()
        if event == "hidden" or event == "idle":
            # start break if no active one
            active = [b for b in data if b["worker"]==worker and b.get("end") is None]
            if not active:
                data.append({"worker": worker, "start": now.isoformat(), "end": None,
                             "duration_min": 0, "source": event})
                print(f"[AUTO-BREAK START] {worker} ({event}) at {now.strftime('%H:%M:%S')}")
        elif event == "visible":
            for b in data:
                if b["worker"]==worker and b.get("end") is None:
                    b["end"] = now.isoformat()
                    start = datetime.fromisoformat(b["start"])
                    b["duration_min"] = int((now - start).total_seconds() / 60)
                    print(f"[AUTO-BREAK END] {worker} duration {b['duration_min']} min")
        save_breaks(data)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            q = parse_qs(urlparse(self.path).query)
            worker = q.get("worker", [None])[0]
            event = q.get("event", [None])[0]
            if worker and event:
                record_event(worker, event)
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok")
        except Exception as e:
            self.send_response(500); self.end_headers()
            self.wfile.write(str(e).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def log_message(self, *args): pass  # silence


if __name__ == "__main__":
    print(f"Tracker running on http://localhost:{PORT}")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
