"""db_schema.py — Auto-discover SQLite schemas to give LLM context."""
import sqlite3
from pathlib import Path


def discover_schema(db_path: str) -> str:
    """Return a human-readable schema description."""
    if not Path(db_path).exists():
        return f"Database {db_path} not found"

    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in c.fetchall()]

        lines = [f"Database: {db_path}"]
        for t in tables:
            c.execute(f"PRAGMA table_info({t})")
            cols = c.fetchall()
            # Count rows
            try:
                c.execute(f"SELECT COUNT(*) FROM {t}")
                count = c.fetchone()[0]
            except Exception:
                count = "?"

            lines.append(f"\nTable: {t} ({count} rows)")
            for col in cols:
                cid, name, col_type, notnull, default, pk = col
                lines.append(f"  - {name} ({col_type})" + (" PRIMARY KEY" if pk else ""))

        conn.close()
        return "\n".join(lines)
    except Exception as e:
        return f"Error reading {db_path}: {e}"


def all_schemas() -> str:
    """Get schemas for all databases."""
    parts = []
    for db in ["queryable.db", "accounting.db", "inventory.db"]:
        if Path(db).exists():
            parts.append(discover_schema(db))
    return "\n\n" + ("=" * 60 + "\n").join(parts) if parts else "No databases found"


def describe_json(path: str, max_keys: int = 20) -> str:
    """Describe a JSON file structure (keys only)."""
    import json
    p = Path(path)
    if not p.exists():
        return f"{path} not found"
    try:
        data = json.loads(p.read_text())
        if isinstance(data, list):
            if not data:
                return f"{path}: empty list"
            sample = data[0]
            return f"{path}: list of {len(data)} items. Each item keys: {list(sample.keys())[:max_keys]}"
        elif isinstance(data, dict):
            return f"{path}: dict with keys {list(data.keys())[:max_keys]}"
        return f"{path}: {type(data).__name__}"
    except Exception as e:
        return f"{path}: error {e}"


def all_json_schemas() -> str:
    parts = []
    for f in ["retailers.json", "orders.json", "products.json"]:
        if Path(f).exists():
            parts.append(describe_json(f))
    return "\n".join(parts)
