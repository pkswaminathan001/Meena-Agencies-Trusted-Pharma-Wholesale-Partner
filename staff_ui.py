"""staff_ui.py — Owner-only staff management UI."""
import streamlit as st
import rbac
import pandas as pd
from datetime import datetime


def render_staff_tab():
    """Full staff management — add, view, toggle, reset PIN."""
    st.markdown("### 👨‍💼 Staff Management")
    st.caption("Add, deactivate, and manage staff accounts")

    users = rbac.load_users()
    staff = users.get("staff", [])

    # ─── KPI Row ───
    c1, c2, c3 = st.columns(3)
    active = sum(1 for s in staff if s.get("active", True))
    inactive = len(staff) - active
    c1.metric("Total Staff", len(staff))
    c2.metric("Active", active)
    c3.metric("Deactivated", inactive)

    st.markdown("---")

    # ─── Add New Staff ───
    with st.expander("➕ Add New Staff", expanded=(len(staff) == 0)):
        with st.form("add_staff_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name *", placeholder="Rajesh Kumar")
            with col2:
                pin = st.text_input("Initial PIN (6 digits) *",
                                     type="password", max_chars=6)
            if st.form_submit_button("Add Staff Member", use_container_width=True,
                                     type="primary"):
                if not name.strip():
                    st.error("Name is required")
                elif not pin or len(pin) < 6:
                    st.error("PIN must be exactly 6 digits")
                else:
                    ok, msg, sid = rbac.add_staff(name.strip(), pin)
                    if ok:
                        st.success(msg)
                        st.info(f"📌 Share this ID with the staff: **{sid}**")
                        st.rerun()
                    else:
                        st.error(msg)

    # ─── Staff List ───
    if staff:
        st.markdown("#### Current Staff")
        for s in staff:
            active_flag = s.get("active", True)
            _badge_color = "#00d47a" if active_flag else "#ff4d6d"
            _badge_text = "Active" if active_flag else "Inactive"
            with st.container():
                st.markdown(f"""
                <div style="background:rgba(26,31,58,0.7);border-left:4px solid {_badge_color};
                            border-radius:10px;padding:12px 16px;margin:6px 0;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <div style="font-weight:700;color:#e8eaf6;font-size:1.05rem;">
                                👤 {s['name']}
                            </div>
                            <div style="font-size:0.75rem;color:#8892b0;margin-top:2px;">
                                ID: <b>{s['id']}</b> · Joined {s.get('created_at', '—')}
                            </div>
                        </div>
                        <div>
                            <span style="background:rgba(255,255,255,0.05);color:{_badge_color};
                                        padding:3px 10px;border-radius:10px;font-size:0.7rem;
                                        font-weight:700;">{_badge_text}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                _sc1, _sc2, _sc3 = st.columns([1, 1, 3])
                with _sc1:
                    _lbl = "🔒 Deactivate" if active_flag else "✅ Reactivate"
                    if st.button(_lbl, key=f"toggle_{s['id']}", use_container_width=True):
                        rbac.toggle_staff(s["id"], not active_flag)
                        st.success(f"{s['name']} {'deactivated' if active_flag else 'reactivated'}")
                        st.rerun()
                with _sc2:
                    with st.popover("🔑 Reset PIN"):
                        new_pin = st.text_input("New PIN (6 digits)",
                                                 type="password", max_chars=6,
                                                 key=f"reset_{s['id']}")
                        if st.button("Confirm Reset", key=f"confirm_{s['id']}"):
                            if new_pin and len(new_pin) == 6:
                                rbac.reset_staff_pin(s["id"], new_pin)
                                st.success("PIN reset ✅")
                                st.rerun()
                            else:
                                st.error("PIN must be 6 digits")
                st.markdown("")
    else:
        st.info("👋 No staff added yet. Use the form above to add your first staff member.")
