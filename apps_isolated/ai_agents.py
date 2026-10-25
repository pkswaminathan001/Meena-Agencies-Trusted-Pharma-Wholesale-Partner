import sqlite3, datetime, json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB = BASE_DIR / "meena_enterprise.db"


def run_inventory_agent() -> dict:
    """Scans products, flags low stock, suggests reorder quantities."""
    conn = sqlite3.connect(DB)
    low = conn.execute("SELECT sku, qty FROM products WHERE qty < 15 ORDER BY qty ASC").fetchall()
    total = conn.execute("SELECT COUNT(*), SUM(price*qty) FROM products").fetchone()
    conn.close()
    findings = []
    for sku, qty in low:
        reorder = 50 - qty
        findings.append(f"⚠️ {sku}: only {qty} left → reorder {reorder}")
    if not findings:
        findings.append("✅ All stock levels healthy (>=15 units)")
    return {
        "agent": "Inventory",
        "findings": findings,
        "summary": f"{len(low)} low-stock items, {total[0]} SKUs total, ₹{(total[1] or 0):,.0f} inventory value",
    }


def run_credit_agent() -> dict:
    """Checks each retailer's outstanding vs their limit, flags over-limit."""
    retailers = json.loads((BASE_DIR / "retailers.json").read_text())
    findings = []
    checked = 0
    for r in retailers:
        if r.get("role") != "retailer":
            continue
        checked += 1
        outstanding = r.get("outstanding", 0)
        limit = r.get("credit_limit", 50000)
        pct = (outstanding / limit * 100) if limit else 0
        if pct > 80:
            findings.append(f"🚨 {r['id']} ({r.get('shop')}): ₹{outstanding:,} / ₹{limit:,} ({pct:.0f}%) — OVER LIMIT")
        elif pct > 50:
            findings.append(f"⚠️ {r['id']} ({r.get('shop')}): ₹{outstanding:,} / ₹{limit:,} ({pct:.0f}%)")
        else:
            findings.append(f"✅ {r['id']} ({r.get('shop')}): ₹{outstanding:,} / ₹{limit:,} ({pct:.0f}%)")
    return {"agent": "Credit", "findings": findings, "summary": f"{checked} retailers checked"}


def run_fraud_agent() -> dict:
    """Flags unusual order patterns: high value, same-day repeats."""
    conn = sqlite3.connect(DB)
    orders = conn.execute("SELECT order_id, user_id, total, date FROM orders ORDER BY date DESC LIMIT 50").fetchall()
    conn.close()
    findings = []
    seen_users = {}
    for oid, uid, total, date in orders:
        seen_users.setdefault(uid, []).append((oid, total, date))
        if total > 10000:
            findings.append(f"🚨 {oid} ({uid}): ₹{total:,.0f} — high value (>₹10,000)")
    for uid, os in seen_users.items():
        if len(os) >= 3:
            findings.append(f"⚠️ {uid}: {len(os)} orders in last 50 — check for duplicate ordering")
    if not findings:
        findings.append("✅ No fraud patterns detected")
    return {"agent": "Fraud", "findings": findings, "summary": f"{len(orders)} orders scanned"}


def run_forecast_agent() -> dict:
    """Simple 7-day sales forecast based on last 30 days of orders."""
    conn = sqlite3.connect(DB)
    row = conn.execute("""
        SELECT COUNT(*) as order_count, COALESCE(SUM(total), 0) as revenue
        FROM orders
        WHERE date >= date('now', '-30 days') AND status IN ('Paid', 'Approved')
    """).fetchone()
    conn.close()
    count, revenue = row
    daily_avg = revenue / 30
    weekly = daily_avg * 7
    findings = [
        f"📊 Last 30 days: {count} orders, ₹{revenue:,.2f} revenue",
        f"📈 Daily avg: ₹{daily_avg:,.2f}",
        f"🔮 7-day forecast: ₹{weekly:,.2f}",
    ]
    if count == 0:
        findings.append("ℹ️ Not enough history yet — need at least 1 paid order")
    return {"agent": "Forecast", "findings": findings, "summary": f"₹{weekly:,.0f} projected this week"}


def _boss_critique(result: dict) -> dict:
    """Rule-based critic: flags vague phrases, missing numbers."""
    issues = []
    vague = ["being set up", "check back", "coming soon", "TBD", "N/A"]
    text = " ".join(result.get("findings", [])) + " " + result.get("summary", "")
    for phrase in vague:
        if phrase.lower() in text.lower():
            issues.append(f"Vague phrase '{phrase}' — needs specific numbers")
    if not any(c.isdigit() for c in result.get("summary", "")):
        issues.append("Summary has no numbers — must include a concrete metric")
    return {"verdict": "PASS" if not issues else "REJECT", "issues": issues}


def run_with_boss(agent_fn, max_rounds=3) -> dict:
    """Boss Loop: builder produces, boss critiques, repeat until PASS or max rounds."""
    history = []
    for round_num in range(1, max_rounds + 1):
        result = agent_fn()
        critique = _boss_critique(result)
        history.append({"round": round_num, "critique": critique, "result": result})
        if critique["verdict"] == "PASS":
            return {"status": "passed", "rounds": round_num, "final": result, "history": history}
    return {"status": "max_rounds", "rounds": max_rounds, "final": history[-1]["result"], "history": history}


def run_all_agents(user_id: str) -> list:
    """Runs all 4 agents with boss loop, logs each run to agent_activity."""
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS agent_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT, agent TEXT, verdict TEXT,
            summary TEXT, findings TEXT, rounds INTEGER, timestamp TEXT
        )
    """)
    results = []
    for fn in [run_inventory_agent, run_credit_agent, run_fraud_agent, run_forecast_agent]:
        r = run_with_boss(fn)
        final = r["final"]
        conn.execute(
            "INSERT INTO agent_activity (user_id, agent, verdict, summary, findings, rounds, timestamp) VALUES (?,?,?,?,?,?,?)",
            (user_id, final["agent"], r["status"], final["summary"],
             json.dumps(final["findings"]), r["rounds"], str(datetime.datetime.now()))
        )
        results.append(r)
    conn.commit()
    conn.close()
    return results