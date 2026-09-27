"""
github_push.py — Pushes your project to GitHub via API.
No git required. Handles empty repos. Skips secrets + backups.
"""
import os, base64, json, sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ requests not installed. Run: pip install requests")
    sys.exit(1)

# ── Config ──
OWNER  = "pkswaminathan001"
REPO   = "Meena-Agencies-Trusted-Pharma-Wholesale-Partner"
BRANCH = "main"
API    = f"https://api.github.com/repos/{OWNER}/{REPO}"

# ── Ignore rules ──
IGNORE_DIRS = {".git", "venv", ".venv", "__pycache__", "_archive_old",
               ".vscode", ".idea", ".streamlit", ".pytest_cache"}
IGNORE_SUFFIXES = (".log", ".backup", ".bak", ".broken", ".db", ".sqlite",
                   ".swp", ".pyc", ".pyo", ".tmp")
IGNORE_EXACT = {".env", ".env.local", ".salt", "audit_pro.jsonl",
                "audit_pro.jsonl.before_archive", "pharma_intel_cache.json",
                "pharma_intel_seen.json", "rate_limit.json",
                "pending_replies.json", "owner_state.json",
                "flash_offers.json", "service_log.json", "broadcast_log.json"}
IGNORE_NAME_PARTS = (".before_", ".backup_", ".broken", ".v1_backup",
                     ".v2_backup", ".v3_broken", "audit_archive_", "audit_pro_archive_")


def should_include(path: Path) -> bool:
    parts = path.parts
    if any(p in IGNORE_DIRS for p in parts):
        return False
    if path.name in IGNORE_EXACT:
        return False
    name = str(path)
    if any(s in name for s in IGNORE_SUFFIXES):
        return False
    if any(s in name for s in IGNORE_NAME_PARTS):
        return False
    if path.name.startswith(".") and path.name not in (".gitignore", ".gitkeep"):
        return False
    return True


def collect_files() -> list:
    files = []
    for p in Path(".").rglob("*"):
        if p.is_file() and should_include(p):
            rel = str(p.relative_to("."))
            # GitHub API path uses forward slashes
            rel = rel.replace(os.sep, "/")
            size = p.stat().st_size
            if size > 50 * 1024 * 1024:
                print(f"  ⚠️  Skipping (too big): {rel} ({size/1024/1024:.1f} MB)")
                continue
            files.append((rel, p, size))
    return files


def main():
    print("═" * 60)
    print("  GITHUB PUSH — Meena Agencies")
    print("═" * 60)

    token = os.getenv("GITHUB_TOKEN") or input("\n🔑 Paste GitHub token: ").strip()
    if not token:
        print("❌ No token. Aborted.")
        return

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    # ── Verify token ──
    print("\n[1/6] Verifying token…")
    r = requests.get("https://api.github.com/user", headers=headers)
    if r.status_code != 200:
        print(f"❌ Bad token: {r.status_code} {r.text[:200]}")
        return
    user = r.json()
    print(f"   ✅ Logged in as {user['login']}")

    # ── Check repo access ──
    print("\n[2/6] Checking repo access…")
    r = requests.get(API, headers=headers)
    if r.status_code == 404:
        print(f"❌ Repo not found: {OWNER}/{REPO}")
        print("   Make sure the repo exists on GitHub (create empty repo first)")
        return
    if r.status_code != 200:
        print(f"❌ Error: {r.status_code} {r.text[:200]}")
        return
    print(f"   ✅ Repo accessible: {OWNER}/{REPO}")

    # ── Get base commit/tree ──
    print("\n[3/6] Getting base state…")
    r = requests.get(f"{API}/git/ref/heads/{BRANCH}", headers=headers)
    if r.status_code == 200:
        base_sha = r.json()["object"]["sha"]
        r2 = requests.get(f"{API}/git/commits/{base_sha}", headers=headers)
        base_tree = r2.json()["tree"]["sha"]
        print(f"   ✅ Existing branch '{BRANCH}' at {base_sha[:8]}")
        parents = [base_sha]
    else:
        base_tree = None
        parents = []
        print(f"   ℹ️  Fresh repo — creating initial commit")

    # ── Collect files ──
    print("\n[4/6] Collecting files…")
    files = collect_files()
    total = sum(s for _, _, s in files)
    print(f"   ✅ {len(files)} files, {total/1024:.1f} KB total")
    print(f"\n   🚨 Verifying secrets are excluded:")
    for name, _, _ in files:
        if name == ".env" or ".env." in name:
            print(f"   ❌ DANGER: {name} is included! Aborting.")
            return
    print(f"   ✅ .env not in list")

    # ── Create blobs ──
    print(f"\n[5/6] Uploading {len(files)} files…")
    tree_items = []
    for i, (rel, path, size) in enumerate(files, 1):
        with open(path, "rb") as f:
            content = f.read()
        b64 = base64.b64encode(content).decode()
        r = requests.post(
            f"{API}/git/blobs",
            headers=headers,
            json={"content": b64, "encoding": "base64"},
            timeout=60,
        )
        if r.status_code != 201:
            print(f"   ❌ Failed: {rel} — {r.status_code}")
            return
        sha = r.json()["sha"]
        tree_items.append({"path": rel, "mode": "100644", "type": "blob", "sha": sha})
        if i % 10 == 0 or i == len(files):
            print(f"   [{i}/{len(files)}] uploaded")

    # ── Create tree ──
    print("\n[6/6] Creating tree + commit + branch…")
    tree_payload = {"tree": tree_items}
    if base_tree:
        tree_payload["base_tree"] = base_tree
    r = requests.post(f"{API}/git/trees", headers=headers, json=tree_payload)
    if r.status_code != 201:
        print(f"   ❌ Tree failed: {r.text[:200]}")
        return
    tree_sha = r.json()["sha"]

    # ── Create commit ──
    commit_payload = {
        "message": "Initial commit — Meena Agencies AI Pharma Platform",
        "tree": tree_sha,
    }
    if parents:
        commit_payload["parents"] = parents
    r = requests.post(f"{API}/git/commits", headers=headers, json=commit_payload)
    if r.status_code != 201:
        print(f"   ❌ Commit failed: {r.text[:200]}")
        return
    commit_sha = r.json()["sha"]

    # ── Create or update branch ──
    if parents:
        # Update existing
        r = requests.patch(
            f"{API}/git/refs/heads/{BRANCH}",
            headers=headers,
            json={"sha": commit_sha, "force": False},
        )
    else:
        # Create new
        r = requests.post(
            f"{API}/git/refs",
            headers=headers,
            json={"ref": f"refs/heads/{BRANCH}", "sha": commit_sha},
        )
    if r.status_code not in (200, 201):
        print(f"   ❌ Ref failed: {r.status_code} {r.text[:200]}")
        return

    print()
    print("═" * 60)
    print(f"  ✅ PUSHED SUCCESSFULLY")
    print(f"  Commit:  {commit_sha[:12]}")
    print(f"  URL:     https://github.com/{OWNER}/{REPO}")
    print(f"  Files:   {len(files)}")
    print(f"  Size:    {total/1024:.1f} KB")
    print("═" * 60)


if __name__ == "__main__":
    main()
