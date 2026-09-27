import asyncio, marketing_ads

promo = {
    "title": "Dolo 650 — Bulk Deal",
    "sku": "dolo650",
    "badge_lines": ["BUY 50 BOXES", "GET 1 BOX FREE"],
    "offer_text": "Dolo 650mg · 10 strips × 10 tablets",
}
retailer = {"id": "RET001", "shop": "Sri Balaji Medicals",
            "owner": "Chitra", "telegram_id": 123456789}

png = marketing_ads.generate_marketing_ad(promo, retailer)
open("/tmp/sri_balaji_ad.png", "wb").write(png)
print("written /tmp/sri_balaji_ad.png")
