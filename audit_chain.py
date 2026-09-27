"""Tamper-proof hash-chained audit log. Every entry references prior hash."""
import os, json, hashlib
from datetime import datetime

CHAIN_FILE = "audit_chain.json"


def _genesis_hash():
    return "0" * 64


def load_chain():
    if os.path.exists(CHAIN_FILE):
        with open(CHAIN_FILE) as f: return json.load(f)
    return []


def save_chain(chain):
    with open(CHAIN_FILE, "w") as f: json.dump(chain, f, indent=2)


def _compute_hash(entry):
    s = f"{entry['idx']}|{entry['timestamp']}|{entry['user']}|{entry['action']}|{entry['details']}|{entry['prev_hash']}"
    return hashlib.sha256(s.encode()).hexdigest()


def record(user, action, details=""):
    """Append a tamper-proof entry to the chain."""
    chain = load_chain()
    idx = len(chain)
    prev_hash = chain[-1]["hash"] if chain else _genesis_hash()
    entry = {
        "idx": idx,
        "timestamp": datetime.now().strftime("%d-%b-%Y %H:%M:%S").upper(),
        "iso": datetime.now().isoformat(),
        "user": user,
        "action": action,
        "details": details,
        "prev_hash": prev_hash
    }
    entry["hash"] = _compute_hash(entry)
    chain.append(entry)
    save_chain(chain)
    return entry


def verify_chain():
    """Verify the entire chain hasn't been tampered with."""
    chain = load_chain()
    if not chain:
        return {"valid": True, "entries": 0, "issues": []}
    issues = []
    for i, entry in enumerate(chain):
        # Check hash matches
        expected = _compute_hash(entry)
        if entry["hash"] != expected:
            issues.append(f"Entry #{i} hash mismatch — tampered")
        # Check prev_hash linkage
        if i == 0:
            if entry["prev_hash"] != _genesis_hash():
                issues.append(f"Entry #0 prev_hash wrong")
        else:
            if entry["prev_hash"] != chain[i-1]["hash"]:
                issues.append(f"Entry #{i} prev_hash broken — chain severed")
        # Check index
        if entry["idx"] != i:
            issues.append(f"Entry at position {i} has idx={entry['idx']} — reordered")
    return {"valid": len(issues) == 0, "entries": len(chain), "issues": issues}


def get_user_history(user, last_n=50):
    chain = load_chain()
    return [e for e in chain if e["user"] == user][-last_n:]


def get_action_counts(days=7):
    from datetime import timedelta
    cutoff = datetime.now() - timedelta(days=days)
    chain = load_chain()
    counts = {}
    for e in chain:
        if datetime.fromisoformat(e["iso"]) >= cutoff:
            counts[e["action"]] = counts.get(e["action"], 0) + 1
    return counts
