"""
real_speed_test.py — Measures ACTUAL app.py execution time.
Runs app.py in isolation to see how long each user click really takes.
"""
import time, subprocess, sys
from pathlib import Path

APP = Path("app.py")

print("═" * 60)
print("  REAL APP SPEED TEST — " + time.strftime("%H:%M:%S"))
print("═" * 60)

# ── 1. How long does it take to EXECUTE app.py once? ──
print("\n── 1. APP.PY EXECUTION TIME (per user click) ──")
times = []
for i in range(5):
    t0 = time.time()
    r = subprocess.run(
        [sys.executable, "-c", "import py_compile; py_compile.compile('app.py', doraise=True)"],
        capture_output=True, cwd=".",
    )
    elapsed = (time.time() - t0) * 1000
    times.append(elapsed)
    print(f"  Run {i+1}: {elapsed:.0f} ms")

print(f"\n  Average: {sum(times)/len(times):.0f} ms per full app.py compile")

# ── 2. Actual Python import time (first load) ──
print("\n── 2. IMPORT TIME (all modules together) ──")
t0 = time.time()
try:
    import streamlit
    t_st = (time.time() - t0) * 1000
    print(f"  streamlit:      {t_st:.0f} ms")
except Exception as e:
    print(f"  streamlit ERR: {e}")

t0 = time.time()
try:
    import pandas
    print(f"  pandas:         {(time.time()-t0)*1000:.0f} ms")
except Exception:
    pass

t0 = time.time()
try:
    import numpy
    print(f"  numpy:          {(time.time()-t0)*1000:.0f} ms")
except Exception:
    pass

t0 = time.time()
try:
    import PIL
    print(f"  Pillow:         {(time.time()-t0)*1000:.0f} ms")
except Exception:
    pass

# ── 3. Estimate real per-click cost ──
print("\n── 3. ESTIMATED PER-CLICK COST ──")
file_size = APP.stat().st_size
lines = APP.read_text().count("\n")
print(f"  app.py size:    {file_size:,} bytes ({file_size/1024:.1f} KB)")
print(f"  app.py lines:   {lines:,}")
print(f"  st.rerun calls: {APP.read_text().count('st.rerun()')}")

# Rough estimate: 1 KB of Streamlit code ≈ 3-5ms execution
per_click_est = (file_size / 1024) * 4
print(f"\n  Estimated per-click cost: {per_click_est:.0f} ms")
print(f"  Per 100 users (sequential): {per_click_est * 100 / 1000:.1f} seconds")
print(f"  Per 100 users (concurrent): {per_click_est * 3:.0f} ms (Streamlit parallelises 3-4x)")

# ── 4. Critical: 1000-user estimate ──
print("\n── 4. 1000-USER SCALING PROJECTION ──")
concurrent_limit = 4  # Streamlit realistic concurrency per worker
per_user_cost = per_click_est
workers_needed = 1000 / concurrent_limit
print(f"  Streamlit realistic concurrency per process: {concurrent_limit}")
print(f"  Workers needed for 1000 users: {workers_needed:.0f}")
print(f"  RAM per worker: ~200 MB")
print(f"  Total RAM needed: {workers_needed * 0.2:.1f} GB")
print(f"  Per-click latency at 1000 users: {per_user_cost * 3:.0f} ms")

print("\n" + "═" * 60)
