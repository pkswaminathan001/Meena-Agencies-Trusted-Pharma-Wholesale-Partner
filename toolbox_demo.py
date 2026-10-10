"""toolbox_demo.py - Shows all 5 toolboxes in action.
New file - does not modify existing screens."""
import streamlit as st
import theme
import ui_helpers
import ux_flow
import retailer_journey
import hx_personas


def render():
    """Render the toolbox demo page."""
    theme.title("🎨 Toolbox Showcase", icon="🎨",
                subtitle="Live demo of GUI · UI · UX · CX · HX toolboxes")

    # ═══ 1. GUI FOUNDATION (theme.py) ═══
    with st.expander("1️⃣ GUI Foundation (theme.py) - LIVE", expanded=True):
        st.caption("Colors, fonts, spacing, all consistent from one file.")
        theme.card("""
            <b>Theme tokens:</b><br>
            Primary: <span style="color:#00d4ff;">#00d4ff</span> ·
            Secondary: <span style="color:#7b61ff;">#7b61ff</span> ·
            Success: <span style="color:#00d47a;">#00d47a</span> ·
            Danger: <span style="color:#ff4d6d;">#ff4d6d</span>
        """, accent="primary")

    # ═══ 2. UI HELPERS ═══
    with st.expander("2️⃣ UI Helpers - Empty States + Toasts", expanded=True):
        st.markdown("**Empty state (used when no data):**")
        ui_helpers.empty_orders("Try This Button")

        st.markdown("---")
        st.markdown("**Success toast:**")
        ui_helpers.toast_success("Order saved", "ORD-1234 · Rs 5,400")

        st.markdown("**Error toast:**")
        ui_helpers.toast_error("Couldn't save", "Network timeout", action_label="Retry")

        st.markdown("**Warning toast:**")
        ui_helpers.toast_warning("Low stock", "Paracetamol below 50 units")

    # ═══ 3. UX FLOW ═══
    with st.expander("3️⃣ UX Flow - Welcome + Undo", expanded=True):
        st.markdown("**Welcome card:**")
        ux_flow.welcome_card("Swaminathan", role="demo_owner")

        st.markdown("**Keyboard shortcuts active:**")
        st.info("⌨️ Press Ctrl+K anywhere to focus search. Press Esc to blur.")

    # ═══ 4. CX RETAILER JOURNEY ═══
    with st.expander("4️⃣ CX Retailer Journey - Order Progress", expanded=True):
        st.markdown("**Order progress bar (Pending → Delivered):**")
        sample_order = {
            "order_id": "ORD-DEMO-001",
            "status": "Approved",
            "total": 5400,
            "placed_at": "10-Oct-2026 09:00",
        }
        retailer_journey.render_order_progress(sample_order)

        st.markdown("**Delivery estimate:**")
        st.info(retailer_journey.estimate_delivery(sample_order))

        st.markdown("---")
        st.markdown("**Feedback prompt (appears after delivery):**")
        # Just show, don't save
        st.markdown("### ⭐ How was this order?")
        st.radio("Rate:", [1, 2, 3, 4, 5], format_func=lambda x: "⭐" * x, horizontal=True, key="demo_feedback")

    # ═══ 5. HX PERSONAS ═══
    with st.expander("5️⃣ HX Personas - Rep Leaderboard + Scorecards", expanded=True):
        st.markdown("**Rep leaderboard:**")
        hx_personas.render_leaderboard([
            {"name": "Ravi", "score": 85, "visits": 12},
            {"name": "Kumar", "score": 62, "visits": 8},
            {"name": "Senthil", "score": 45, "visits": 5},
        ])

        st.markdown("**Rep scorecard:**")
        hx_personas.render_rep_scorecard("Ravi", {"score": 85, "tier": "🏆 Champion"})

        st.markdown("---")
        st.markdown("**High contrast mode:**")
        hx_personas.high_contrast_mode()

    # ═══ SUMMARY ═══
    st.markdown("---")
    st.success("✅ All 5 toolboxes are working. See the code in each `.py` file.")
