from pathlib import Path
import py_compile

APP = Path("app.py")
src = APP.read_text()
original = src

# ── 1. Extract the theme block ──
start_marker = "# ═════════════════════════════════════════════════════════════════\n# PEACOCK_THEME_V1"
end_marker   = "# ═════════════════════════════════════════════════════════════════\n"

if start_marker not in src:
    print("❌ Theme block not found")
    raise SystemExit(1)

start_idx = src.index(start_marker)
# Find the closing marker AFTER the opening one
end_idx = src.index(end_marker, start_idx + len(start_marker)) + len(end_marker)
theme_block = src[start_idx:end_idx]

print(f"Theme block spans {start_idx}..{end_idx} ({len(theme_block)} bytes)")

# ── 2. Remove it ──
src_without = src[:start_idx] + src[end_idx:]

# ── 3. Find the set_page_config line ──
spc_marker = "st.set_page_config("
if spc_marker not in src_without:
    print("❌ set_page_config not found")
    raise SystemExit(1)

spc_i = src_without.index(spc_marker)
spc_line_end = src_without.index("\n", spc_i) + 1

# ── 4. Re-insert theme block AFTER set_page_config ──
new_src = src_without[:spc_line_end] + "\n" + theme_block + "\n" + src_without[spc_line_end:]

APP.write_text(new_src)
try:
    py_compile.compile("app.py", doraise=True)
    print("✅ app.py compiles")
    print("✅ Theme block moved after set_page_config")
except Exception as e:
    APP.write_text(original)
    print(f"❌ compile failed: {e}")
    print("⚠️  reverted")
