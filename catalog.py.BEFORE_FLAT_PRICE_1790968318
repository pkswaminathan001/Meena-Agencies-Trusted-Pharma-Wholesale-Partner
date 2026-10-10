"""
catalog.py — Aggregates 10,000+ inventory rows into categories + unique medicines.
Solves: duplicate batches, performance, browsing UX.
"""
import pandas as pd
from collections import defaultdict


CATEGORIES = {
    "Antibiotic":   {"emoji": "💊", "color": "#ff8c42", "order": 1},
    "Pain Relief":  {"emoji": "💊", "color": "#00d4ff", "order": 2},
    "Cardiac":      {"emoji": "❤️", "color": "#e91e63", "order": 3},
    "Diabetes":     {"emoji": "🩸", "color": "#ff4d6d", "order": 4},
    "Gastro":       {"emoji": "🫃", "color": "#00d47a", "order": 5},
    "Allergy":      {"emoji": "🤧", "color": "#7b61ff", "order": 6},
    "Injection":    {"emoji": "💉", "color": "#ff4d6d", "order": 7},
    "Syrup":        {"emoji": "🧴", "color": "#00d4ff", "order": 8},
    "Inhaler":      {"emoji": "🌬️", "color": "#7b61ff", "order": 9},
    "Topical":      {"emoji": "🧴", "color": "#00d47a", "order": 10},
    "Powder":       {"emoji": "🥤", "color": "#ffb547", "order": 11},
    "Vitamin":      {"emoji": "🍊", "color": "#ffb547", "order": 12},
    "Other":        {"emoji": "💊", "color": "#8892b0", "order": 99},
}


def categorize(name: str) -> str:
    """Return category name for a medicine."""
    n = str(name).lower()

    if any(k in n for k in ["insulin", "injection", "vaccine", "glargine"]):
        return "Injection"
    if any(k in n for k in ["inhaler", "salbutamol", "asthalin", "ventorlin"]):
        return "Inhaler"
    if any(k in n for k in ["syrup", "suspension", "drops", "tonic"]):
        return "Syrup"
    if any(k in n for k in ["ors", "powder", "sachet", "electral"]):
        return "Powder"
    if any(k in n for k in ["cream", "ointment", "gel", "lotion"]):
        return "Topical"
    if any(k in n for k in ["vitamin", "multivitamin", "vit c", "b-complex", "b complex"]):
        return "Vitamin"
    if any(k in n for k in ["amoxicillin", "azithromycin", "ciprofloxacin", "cefixime",
                             "augmentin", "penicillin", "doxycycline", "metronidazole",
                             "cephalexin", "ceftriaxone", "levofloxacin"]):
        return "Antibiotic"
    if any(k in n for k in ["metformin", "glimepiride", "glycomet", "glibenclamide"]):
        return "Diabetes"
    if any(k in n for k in ["atorvastatin", "amlodipine", "telmisartan", "statin",
                             "metoprolol", "clopidogrel", "aspirin", "ecosprin",
                             "losartan", "ramipril"]):
        return "Cardiac"
    if any(k in n for k in ["paracetamol", "ibuprofen", "aspirin", "diclofenac",
                             "aceclofenac", "naproxen", "dolo", "crocin"]):
        return "Pain Relief"
    if any(k in n for k in ["cetirizine", "loratadine", "antihistamine",
                             "fexofenadine", "levocetirizine"]):
        return "Allergy"
    if any(k in n for k in ["omeprazole", "pantoprazole", "ranitidine",
                             "antacid", "domperidone", "ondansetron"]):
        return "Gastro"
    return "Other"


def build_catalog(df: pd.DataFrame) -> dict:
    """
    Aggregate inventory by medicine_name.
    Returns:
    {
      "categories": {category_name: [medicine_dict, ...]},
      "by_medicine": {medicine_name: {aggregated info + batches}},
      "total_unique_medicines": int,
      "total_batches": int,
    }
    """
    if df is None or len(df) == 0:
        return {"categories": {}, "by_medicine": {}, "total_unique_medicines": 0, "total_batches": 0}

    # Ensure numeric
    df = df.copy()
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
    df["cost_price"] = pd.to_numeric(df["cost_price"], errors="coerce").fillna(0.0)
    if "selling_price" not in df.columns:
        df["selling_price"] = (df["cost_price"] * 1.25).round(2)

    by_med = {}
    for name, group in df.groupby("medicine_name"):
        # Pick earliest expiry among in-stock batches
        in_stock = group[group["quantity"] > 0]
        if len(in_stock) > 0:
            earliest = in_stock.sort_values("expiry_date").iloc[0]
            next_expiry = earliest["expiry_date"]
        else:
            next_expiry = group["expiry_date"].min()

        # Aggregate
        total_qty = int(group["quantity"].sum())
        avg_price = float(group["selling_price"].mean())
        batches = []
        for _, row in group.iterrows():
            batches.append({
                "batch": str(row.get("batch_number", "")),
                "qty": int(row.get("quantity", 0)),
                "price": float(row.get("selling_price", 0)),
                "expiry": row.get("expiry_date"),
                "supplier": str(row.get("supplier", "")),
                "item_id": str(row.get("item_id", "")),
            })
        batches.sort(key=lambda b: (b["expiry"] if hasattr(b["expiry"], "year") else 9999, -b["qty"]))

        by_med[name] = {
            "name": name,
            "category": categorize(name),
            "total_qty": total_qty,
            "avg_price": round(avg_price, 2),
            "next_expiry": next_expiry,
            "batches": batches,
            "batch_count": len(batches),
        }

    # Group by category
    categories = defaultdict(list)
    for med in by_med.values():
        categories[med["category"]].append(med)

    # Sort categories by predefined order
    ordered_cats = {}
    for cat_name, meds in categories.items():
        meds.sort(key=lambda m: (-m["total_qty"], m["name"]))
        ordered_cats[cat_name] = meds

    return {
        "categories": dict(ordered_cats),
        "by_medicine": by_med,
        "total_unique_medicines": len(by_med),
        "total_batches": len(df),
    }


def search_catalog(catalog: dict, query: str, limit: int = 50) -> list:
    """Search unique medicines by name."""
    q = query.lower().strip()
    if not q:
        return []
    results = []
    for med in catalog["by_medicine"].values():
        if q in med["name"].lower():
            results.append(med)
            if len(results) >= limit:
                break
    results.sort(key=lambda m: (-m["total_qty"], m["name"]))
    return results


def category_summary(catalog: dict) -> list:
    """Return list of {name, emoji, color, count, total_qty}."""
    out = []
    for cat_name, meds in catalog["categories"].items():
        info = CATEGORIES.get(cat_name, CATEGORIES["Other"])
        out.append({
            "name": cat_name,
            "emoji": info["emoji"],
            "color": info["color"],
            "order": info["order"],
            "count": len(meds),
            "total_qty": sum(m["total_qty"] for m in meds),
        })
    out.sort(key=lambda c: c["order"])
    return out
