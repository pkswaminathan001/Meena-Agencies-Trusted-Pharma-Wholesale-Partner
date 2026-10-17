"""
medicine_cards.py — Beautiful 3D medicine cards with emoji pictures.
Click a card → quantity slides in → add to cart with animation.
"""
import streamlit as st

# ────────────────────────────────────────────────
# MEDICINE EMOJI + COLOR MAP
# ────────────────────────────────────────────────
def classify_medicine(name: str) -> dict:
    """Return emoji, color, and category for a medicine name."""
    n = name.lower()

    # Injections
    if "insulin" in n or "injection" in n or "vaccine" in n:
        return {"emoji": "💉", "color": "#ff4d6d", "category": "Injection"}

    # Inhalers
    if "inhaler" in n or "salbutamol" in n or "asthma" in n:
        return {"emoji": "🌬️", "color": "#7b61ff", "category": "Inhaler"}

    # Syrups / Liquids
    if "syrup" in n or "suspension" in n or "drops" in n or "tonic" in n:
        return {"emoji": "🧴", "color": "#00d4ff", "category": "Syrup"}

    # Powders
    if "ors" in n or "powder" in n or "sachet" in n:
        return {"emoji": "🥤", "color": "#ffb547", "category": "Powder"}

    # Ointments / Creams
    if "cream" in n or "ointment" in n or "gel" in n or "lotion" in n:
        return {"emoji": "🧴", "color": "#00d47a", "category": "Topical"}

    # Antibiotics (by name)
    antibiotics = ["amoxicillin", "azithromycin", "ciprofloxacin", "cefixime",
                   "augmentin", "penicillin", "doxycycline", "metronidazole"]
    if any(a in n for a in antibiotics):
        return {"emoji": "💊", "color": "#ff8c42", "category": "Antibiotic"}

    # Diabetes
    if "metformin" in n or "glimepiride" in n or "glargine" in n:
        return {"emoji": "🩸", "color": "#ff4d6d", "category": "Diabetes"}

    # Cardiac
    if "atorvastatin" in n or "amlodipine" in n or "telmisartan" in n or "statin" in n:
        return {"emoji": "❤️", "color": "#e91e63", "category": "Cardiac"}

    # Pain / Fever
    if "paracetamol" in n or "ibuprofen" in n or "aspirin" in n or "diclofenac" in n:
        return {"emoji": "💊", "color": "#00d4ff", "category": "Pain Relief"}

    # Allergy
    if "cetirizine" in n or "loratadine" in n or "antihistamine" in n:
        return {"emoji": "🤧", "color": "#7b61ff", "category": "Allergy"}

    # Stomach
    if "omeprazole" in n or "pantoprazole" in n or "ranitidine" in n or "antacid" in n:
        return {"emoji": "🫃", "color": "#00d47a", "category": "Gastro"}

    # Default
    return {"emoji": "💊", "color": "#00d4ff", "category": "Medicine"}


# ────────────────────────────────────────────────
# INJECT CARD CSS (once per app)
# ────────────────────────────────────────────────
def inject_card_styles():
    st.markdown("""
    <style>
    /* ─── 3D medicine card ─── */
    .med-card {
        background: linear-gradient(145deg, rgba(26,31,58,0.95), rgba(15,20,40,0.95));
        border: 1px solid rgba(123,97,255,0.3);
        border-radius: 16px;
        padding: 1.2rem 1rem;
        text-align: center;
        cursor: pointer;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        transform-style: preserve-3d;
        transform: perspective(1000px) rotateX(0deg) translateY(0);
    }
    .med-card::before {
        content: '';
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(0,212,255,0.15) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.4s;
        pointer-events: none;
    }
    .med-card:hover {
        transform: perspective(1000px) rotateX(-6deg) translateY(-8px) scale(1.03);
        border-color: var(--card-color, #00d4ff);
        box-shadow: 0 20px 45px rgba(0,212,255,0.3),
                    0 0 0 2px var(--card-color, #00d4ff);
    }
    .med-card:hover::before {
        opacity: 1;
    }
    .med-card:active {
        transform: perspective(1000px) rotateX(-2deg) translateY(-2px) scale(0.99);
    }

    /* ─── Selected card pulse ─── */
    .med-card.selected {
        border: 2px solid #00d47a;
        box-shadow: 0 0 30px rgba(0,212,122,0.6),
                    inset 0 0 30px rgba(0,212,122,0.1);
        animation: card-pulse 1.5s ease-in-out infinite;
    }
    @keyframes card-pulse {
        0%, 100% { box-shadow: 0 0 30px rgba(0,212,122,0.5); }
        50%      { box-shadow: 0 0 50px rgba(0,212,122,0.8), inset 0 0 30px rgba(0,212,122,0.15); }
    }

    /* ─── Emoji float animation ─── */
    .med-emoji {
        font-size: 3rem;
        display: inline-block;
        animation: emoji-float 3s ease-in-out infinite;
        filter: drop-shadow(0 6px 12px rgba(0,0,0,0.4));
    }
    @keyframes emoji-float {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50%      { transform: translateY(-6px) rotate(3deg); }
    }

    /* ─── Category pill ─── */
    .med-cat {
        display: inline-block;
        font-size: 0.65rem;
        padding: 2px 8px;
        border-radius: 10px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        font-weight: 600;
        margin-top: 4px;
    }

    /* ─── Quantity reveal slide-in ─── */
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-10px); max-height: 0; }
        to   { opacity: 1; transform: translateY(0); max-height: 400px; }
    }
    .qty-reveal {
        animation: slideDown 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        overflow: hidden;
    }

    /* ─── Cart item pop ─── */
    @keyframes pop {
        0%   { transform: scale(0.8); opacity: 0; }
        50%  { transform: scale(1.08); }
        100% { transform: scale(1); opacity: 1; }
    }
    .cart-pop { animation: pop 0.4s ease-out; }

    /* ─── Success flash on add ─── */
    @keyframes flash-green {
        0%, 100% { background: transparent; }
        50%      { background: rgba(0,212,122,0.25); }
    }
    .flash-green { animation: flash-green 0.6s ease-out; }

    /* ─── Ripple effect on button press ─── */
    @keyframes ripple {
        to { transform: scale(4); opacity: 0; }
    }
    .stButton > button:active::after {
        content: '';
        position: absolute;
        border-radius: 50%;
        background: rgba(0,212,255,0.4);
        width: 20px; height: 20px;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%) scale(0);
        animation: ripple 0.6s ease-out;
    }
    </style>
    """, unsafe_allow_html=True)


# ────────────────────────────────────────────────
# RENDER ONE CARD (HTML only — click handled by wrapper)
# ────────────────────────────────────────────────
def medicine_card_html(row, selected=False):
    """Return the HTML for one medicine card."""
    name = row.get("medicine_name", "")
    info = classify_medicine(name)
    selected_cls = "selected" if selected else ""
    stock = int(row.get("quantity", 0))
    expiry = row.get("expiry_date", "")
    if hasattr(expiry, "strftime"):
        expiry = expiry.strftime("%b-%Y")
    price = float(row.get("selling_price", 0))

    # Stock health
    if stock < 20:
        stock_color = "#ff4d6d"
        stock_txt = f"⚠️ Only {stock} left"
    elif stock < 100:
        stock_color = "#ffb547"
        stock_txt = f"{stock} in stock"
    else:
        stock_color = "#00d47a"
        stock_txt = f"{stock} in stock"

    return f"""
    <div class="med-card {selected_cls}" style="--card-color: {info['color']};">
        <div class="med-emoji">{info['emoji']}</div>
        <div style="font-weight: 700; margin-top: 0.5rem; font-size: 0.85rem; color: #e8eaf6; min-height: 2.2rem; line-height: 1.2;">
            {name[:32]}
        </div>
        <div class="med-cat" style="background: {info['color']}22; color: {info['color']}; border: 1px solid {info['color']}55;">
            {info['category']}
        </div>
        <div style="margin-top: 0.6rem; color: #8892b0; font-size: 0.7rem;">
            Exp: {expiry}
        </div>
        <div style="margin-top: 0.4rem; font-size: 0.95rem; font-weight: 700; color: {info['color']};">
            ₹{price:,.2f}
        </div>
        <div style="margin-top: 0.3rem; font-size: 0.7rem; color: {stock_color};">
            {stock_txt}
        </div>
    </div>
    """
