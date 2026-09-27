"""
speed_test.py — Measures real performance under load.
Simulates concurrent users hitting the Streamlit app.
"""
import time, subprocess, json, statistics
from pathlib import Path
import concurrent.futures
import urllib.request

BASE = "http://localhost:8501"

def hit_app(_):
    t0 = time.time()
    try:
        with urllib.request.urlopen(BASE, timeout=10) as r:
            r.read()
        return (time.time() - t0) * 1000, r.status
    except Exception as e:
        return (time.time() - t0) * 1000, 0

def bench(label, n=100):
    print(f"\n── {label}: {n} requests ──")
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as ex:
        results = list(ex.map(hit_app, range(n)))
    times = [t for t, s in results if s == 200]
    errs = sum(1 for _, s in results if s != 200)
    if not times:
        print("  ❌ ALL FAILED")
        return
    times.sort()
    p50 = statistics.median(times)
    p95 = times[int(len(times) * 0.95)]
    p99 = times[int(len(times) * 0.99)] if len(times) > 10 else max(times)
    print(f"  Requests OK:  {len(times)}/{n}")
    print(f"  Errors:       {errs}")
    print(f"  Avg:          {statistics.mean(times):.0f} ms")
    print(f"  Median (p50): {p50:.0f} ms")
    print(f"  p95:          {p95:.0f} ms")
    print(f"  p99:          {p99:.0f} ms")
    print(f"  Max:          {max(times):.0f} ms")

# ── 1. Cold start (single user) ──
print("═" * 60)
print("  SPEED TEST — " + time.strftime("%H:%M:%S"))
print("═" * 60)
bench("Warm-up (10 sequential)", 10)

# ── 2. Concurrent load ──
bench("Concurrent: 50 users", 50)
bench("Concurrent: 100 users", 100)
bench("Concurrent: 200 users", 200)

# ── 3. Memory ──
print("\n── PROCESS MEMORY ──")
out = subprocess.check_output(["ps", "aux"], text=True)
for line in out.split("\n"):
    if "streamlit run" in line and "grep" not in line:
        p = line.split()
        print(f"  PID {p[1]}  CPU {p[2]}%  MEM {p[3]}%  RSS {p[5]} KB")

# ── 4. Data file read cost ──
print("\n── FILE READ COST ──")
for f in ["orders.json", "retailers.json", "inventory.csv", "promotions.json"]:
    p = Path(f)
    if not p.exists(): continue
    t0 = time.time()
    for _ in range(100):
        _ = p.read_text()
    ms = (time.time() - t0) * 10
    print(f"  {f:<22} {p.stat().st_size:>8} bytes  →  {ms:.2f} ms per read")

print("\n" + "═" * 60)
print("  DONE")
print("═" * 60)
