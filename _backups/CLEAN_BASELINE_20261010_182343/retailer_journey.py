"""retailer_journey.py - CX (Customer Experience) helpers for Meena Agencies.
Order tracking, delivery ETA, 1-tap reorder, feedback.
Nothing replaced - only new helpers."""
import streamlit as st
import json
from datetime import datetime, timedelta
from pathlib import Path


# ═══════════════════════════════════════════════
# ORDER TRACKING
# ═══════════════════════════════════════════════

ORDER_STAGES = [
    ("Pending",    "⏳", "Awaiting owner approval"),
    ("Approved",   "✅", "Approved — preparing for dispatch"),
    ("Dispatched", "🚚", "On the way"),
    ("Delivered",  "📬", "Delivered to your shop"),
]

STAGE_INDEX = {name: i for i, (name, _, _) in enumerate(ORDER_STAGES)}


def render_order_progress(order: dict):
    """Render a visual progress bar for an order."""
    status = order.get("status", "Pending")
    current = STAGE_INDEX.get(status, 0)

    # Calculate total width per stage
    cols = st.columns(len(ORDER_STAGES))

    for i, (stage_name, icon, description) in enumerate(ORDER_STAGES):
        with cols[i]:
            if i <= current:
                color = "#00d47a"  # green = done
            else:
                color = "#8892b0"  # grey = pending

            # Circle
            st.markdown(f"""
            <div style="text-align:center;">
                <div style="width:50px;height:50px;border-radius:50%;
                            background:{color};color:#0a0e27;
                            display:inline-flex;align-items:center;justify-content:center;
                            font-size:1.5rem;font-weight:800;
                            box-shadow:0 4px 12px rgba(0,0,0,0.3);">
                    {icon}
                </div>
                <div style="color:{color};font-weight:600;margin-top:0.5rem;font-size:0.85rem;">
                    {stage_name}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Current status message
    if current < len(ORDER_STAGES):
        _, _, desc = ORDER_STAGES[current]
        st.caption(f"📍 {desc}")


def estimate_delivery(order: dict) -> str:
    """Estimate delivery time based on status."""
    status = order.get("status", "Pending")
    placed = order.get("placed_at", "")
    today = datetime.now()

    try:
        placed_dt = datetime.strptime(placed[:11], "%d-%b-%Y")
    except Exception:
        placed_dt = today

    if status == "Pending":
        return "Awaiting owner approval (usually within 24 hours)"
    elif status == "Approved":
        eta = placed_dt + timedelta(days=2)
        return f"Expected delivery: {eta.strftime('%d-%b-%Y')}"
    elif status == "Dispatched":
        eta = placed_dt + timedelta(days=1)
        return f"Arriving today or tomorrow ({eta.strftime('%d-%b-%Y')})"
    elif status == "Delivered":
        return "✅ Delivered"
    else:
        return "Status unknown"


# ═══════════════════════════════════════════════
# 1-TAP REORDER
# ═══════════════════════════════════════════════

def render_reorder_button(last_order: dict, retailer_id: str):
    """Show a button to reorder the previous order."""
    if not last_order:
        return None

    item_count = len(last_order.get("items", []))
    total = last_order.get("total", 0)

    st.markdown(f"""
    <div style="background:rgba(0,212,255,0.08);border-left:3px solid #00d4ff;
                padding:1rem;border-radius:10px;margin:0.5rem 0;">
        <div style="font-weight:600;color:#00d4ff;">🔁 Reorder Previous</div>
        <div style="color:#8892b0;font-size:0.85rem;margin-top:0.3rem;">
            {item_count} items · Rs {total:,.0f} · Placed {last_order.get('placed_at','')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    return st.button("🔁 Reorder Now", type="primary", use_container_width=True)


def build_reorder_cart(last_order: dict) -> list:
    """Convert last order into a fresh cart."""
    cart = []
    for item in last_order.get("items", []):
        cart.append({
            "item_id": item.get("item_id", ""),
            "medicine": item.get("medicine", ""),
            "batch": item.get("batch", ""),
            "qty": item.get("qty", 10),
            "price": item.get("price", 0),
        })
    return cart


# ═══════════════════════════════════════════════
# POST-DELIVERY FEEDBACK
# ═══════════════════════════════════════════════

def render_feedback_prompt(order: dict):
    """Show 1-5 star rating after delivery."""
    order_id = order.get("order_id", "")

    # Skip if already rated
    feedback_file = Path("feedback.json")
    feedbacks = {}
    if feedback_file.exists():
        try:
            feedbacks = json.loads(feedback_file.read_text())
        except Exception:
            feedbacks = {}

    if order_id in feedbacks:
        return None

    st.markdown("### ⭐ How was this order?")
    st.caption("Your feedback helps us improve.")

    rating = st.radio(
        "Rate your experience:",
        options=[1, 2, 3, 4, 5],
        format_func=lambda x: "⭐" * x,
        horizontal=True,
        key=f"feedback_{order_id}"
    )

    comment = st.text_input("Any comments? (optional)", key=f"comment_{order_id}")

    if st.button("Submit Feedback", key=f"submit_{order_id}", type="primary"):
        feedbacks[order_id] = {
            "rating": rating,
            "comment": comment,
            "submitted_at": datetime.now().isoformat(),
            "retailer_id": order.get("retailer_id", ""),
        }
        feedback_file.write_text(json.dumps(feedbacks, indent=2))
        st.success(f"✅ Thanks! You rated {rating} stars.")
        st.balloons()
        st.rerun()

    return True


# ═══════════════════════════════════════════════
# SELF-SIGNUP
# ═══════════════════════════════════════════════

def render_signup_link():
    """Show signup link for new retailers."""
    st.markdown("""
    <div style="background:rgba(123,97,255,0.10);border-left:3px solid #7b61ff;
                padding:1rem;border-radius:10px;margin-top:1rem;">
        <div style="font-weight:600;color:#7b61ff;">🏪 New here?</div>
        <div style="color:#8892b0;font-size:0.85rem;margin-top:0.3rem;">
            Register your pharmacy in 2 minutes. Contact owner for the signup link.
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_signup_form():
    """Full signup form for new retailers."""
    st.markdown("### 🏪 Retailer Registration")
    st.caption("Fill in your details. Owner will approve within 24 hours.")

    with st.form("retailer_signup"):
        shop = st.text_input("Shop Name *", placeholder="Sri Balaji Medicals")
        owner = st.text_input("Owner Name *", placeholder="Chitra")
        phone = st.text_input("Phone Number *", max_chars=10, placeholder="9876543210")
        address = st.text_area("Shop Address *", placeholder="Full address with PIN")
        gstin = st.text_input("GSTIN (optional)", max_chars=15)
        license_num = st.text_input("Drug License Number *", placeholder="DL-XXXXXX")

        st.caption("Upload your drug license (PDF or image)")
        license_file = st.file_uploader("Drug License", type=["pdf", "jpg", "png"], key="license_upload")

        submitted = st.form_submit_button("🚀 Submit for Approval", type="primary", use_container_width=True)

        if submitted:
            if not all([shop, owner, phone, address, license_num]):
                st.error("Please fill all required fields.")
            elif len(phone) != 10 or not phone.isdigit():
                st.error("Phone must be 10 digits.")
            else:
                # Save pending application
                pending_file = Path("pending_signups.json")
                pending = []
                if pending_file.exists():
                    try:
                        pending = json.loads(pending_file.read_text())
                    except Exception:
                        pending = []

                pending.append({
                    "shop": shop,
                    "owner": owner,
                    "phone": phone,
                    "address": address,
                    "gstin": gstin,
                    "license_num": license_num,
                    "submitted_at": datetime.now().isoformat(),
                    "status": "pending",
                })
                pending_file.write_text(json.dumps(pending, indent=2))

                st.success("✅ Application submitted! Owner will review shortly.")
                st.info("You'll receive a call from Meena Agencies within 24 hours.")

    return True
