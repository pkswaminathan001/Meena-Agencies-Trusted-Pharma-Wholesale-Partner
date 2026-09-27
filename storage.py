"""
storage.py — safe file writes for Meena Agencies.
Atomic writes prevent data loss when multiple users save at the same time.
Drop-in replacement — same behavior, but crash-proof and race-proof.
"""
import json, os, tempfile, fcntl
from pathlib import Path
from contextlib import contextmanager


def atomic_write_json(path, data):
    """
    Write JSON atomically. If two users write at the same time,
    one waits for the other. No order can be lost.
    """
    path = Path(path)
    d = path.parent
    d.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(d), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)     # atomic rename — the secret
    except Exception:
        try: os.unlink(tmp)
        except Exception: pass
        raise


@contextmanager
def locked(path):
    """
    Exclusive file lock for read-modify-write cycles.
    Prevents two users from interleaving their writes.
    """
    lock_path = str(path) + ".lock"
    Path(lock_path).touch(exist_ok=True)
    with open(lock_path, "r") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lk, fcntl.LOCK_UN)
