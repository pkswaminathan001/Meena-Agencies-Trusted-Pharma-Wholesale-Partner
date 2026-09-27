import marketing_ads

promo = {
    "badge_lines": ["BUY 50 BOXES", "GET 1 BOX FREE"],
    "offer_text":  "Dolo 650mg · 10 strips × 10 tablets",
    "product":     {"mrp": 30.0, "wholesale_price": 22.0,
                    "special_price": 20.5, "stock": 3, "sku": "Dolo 650"},
}

retailers = [
    {"id": "RET001", "shop": "Sri Balaji Medicals", "owner": "Chitra"},
    {"id": "RET002", "shop": "Annai Pharmacy",       "owner": "Ramesh"},
    {"id": "RET003", "shop": "Vetri Medicals",       "owner": "Kumar"},
]

for r in retailers:
    png = marketing_ads.generate_marketing_ad(promo, r)
    out = f"/tmp/ad_{r['id']}.png"
    open(out, "wb").write(png)
    print(f"{r['shop']:<25} -> {out}  ({len(png):,} bytes)")
