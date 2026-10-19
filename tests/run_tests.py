#!/usr/bin/env python3
"""
Meena Agencies — Local Auth & Data Hardening Tests
Rebuilt from a corrupted original (heredoc splice damage).
Each check prints PASS/FAIL; exits non-zero if any HIGH/MEDIUM check fails.

Usage:
    ../.venv/bin/python tests/run_tests.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PARENT = Path(__file__).resolve().parent.parent

PASS = 0
FAIL_HIGH = 0
FAIL_MEDIUM = 0
FAIL_LOW = 0


def check(area: str, label: str, ok: bool, detail: str = "", severity: str = "info") -> None:
    """Print one PASS/FAIL line and record the tally."""
    global PASS, FAIL_HIGH, FAIL_MEDIUM, FAIL_LOW
    mark = "✅" if ok else "❌"
    print(f"  {mark} [{area}] {label}" + (f"   ({detail})" if detail else ""))
    if ok:
        PASS += 1
    else:
        if severity == "high":
            FAIL_HIGH += 1
        elif severity == "medium":
            FAIL_MEDIUM += 1
        else:
            FAIL_LOW += 1


def load_json(path: Path):
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        check("io", f"{path.name} parses as JSON", False, str(exc), "high")
        return None


def main() -> int:
    print("═══ Meena Agencies — local hardening tests ═══")

    # ── 1. Sensitive files exist ─────────────────────────────────
    print("\n── File presence ──")
    sensitive = ["orders.json", "audit.jsonl"]
    for name in sensitive:
        path = PARENT / name
        check("file", f"{name} exists", path.exists(),
              f"{path.stat().st_size} bytes" if path.exists() else "missing",
              "high")

    # ── 2. .gitignore hides sensitive files ──────────────────────
    print("\n── .gitignore coverage ──")
    gi = PARENT / ".gitignore"
    if gi.exists():
        gi_text = gi.read_text()
        for name in sensitive:
            check("ignore", f".gitignore mentions {name}", name in gi_text, "", "medium")
    else:
        check("ignore", ".gitignore exists", False, "missing", "medium")

    # ── 3. Users & PIN-hash quality ──────────────────────────────
    print("\n── User / hash quality ──")
    users_file = PARENT / "users.json"
    if users_file.exists():
        users = load_json(users_file)
        if isinstance(users, list):
            check("auth", "users.json is a list", True)
            for u in users:
                uid = u.get("id", "?")
                ph = u.get("pin_hash", "")
                check("auth", f"{uid} has pin_hash", bool(ph), f"len={len(ph)}", "high")
                check("auth", f"{uid} hash is not plaintext",
                      ph not in ("owner2026", "staff123", "1234", ""), "", "high")
                check("auth", f"{uid} hash length ≥ 40",
                      len(ph) >= 40, f"len={len(ph)}",
                      "medium" if len(ph) < 40 else "info")
        elif users is not None:
            check("auth", "users.json is a list", False, type(users).__name__, "high")
    else:
        check("auth", "users.json exists", False, "missing", "medium")

    # ── 4. Session tokens ────────────────────────────────────────
    print("\n── Session tokens ──")
    sess_file = PARENT / "sessions.json"
    if sess_file.exists():
        sess = load_json(sess_file)
        if isinstance(sess, dict):
            check("session", "sessions.json is a dict", True)
            for tok in sess.keys():
                check("session", f"session token length ≥ 16 (got {len(tok)})",
                      len(tok) >= 16, "", "medium")
        elif sess is not None:
            check("session", "sessions.json is a dict", False, type(sess).__name__, "high")
    else:
        check("session", "sessions.json exists (OK if no active sessions)",
              True, "not present — no active sessions", "info")

    # ── 5. Rate limit file ───────────────────────────────────────
    print("\n── Rate limiting ──")
    rl = PARENT / "rate_limit.json"
    check("rate", "rate_limit.json exists (tracks failed attempts)",
          rl.exists(), "", "info")

    # ── Summary ──────────────────────────────────────────────────
    print("\n═══ Summary ═══")
    print(f"  passed: {PASS}")
    print(f"  failed high: {FAIL_HIGH}   medium: {FAIL_MEDIUM}   low: {FAIL_LOW}")
    if FAIL_HIGH == 0 and FAIL_MEDIUM == 0:
        print("  🟢 ALL CRITICAL CHECKS PASS")
        return 0
    print("  🔴 at least one HIGH/MEDIUM check failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
