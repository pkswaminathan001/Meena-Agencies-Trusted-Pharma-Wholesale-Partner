"""
owner_staff_report.py — Owner view: staff activity, audit, alerts.
"""
import streamlit as st
from pathlib import Path
import json
import csv
import io

import staff_monitor
import staff_messages


def render():
    st.markdown("### 📊 Staff Monitoring & Audit")
    st.caption("Private owner view. Staff cannot see this. Every action logged silently.")

    # ── Cleanup old logs on load ──
    try:
        staff_monitor.cleanup_old()
    except Exception:
        pass

    tabs = st.tabs(["📊 Today", "📅 Weekly", "🚨 Alerts",
                    "💬 Messages", "🔍 Full Log", "📥 Export"])

    # ── Today ──
    with tabs[0]:
        s = staff_monitor.today_summary()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Actions", s["total_actions"])
        c2.metric("Active Staff", s["active_staff"])
        c3.metric("High-Risk", len(s["high_risk"]))
        c4.metric("Date", s["date"])

        if not s["by_staff"]:
            st.info("No activity today")
        else:
            for sid, data in s["by_staff"].items():
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"#### 👤 {data['name']}  `{sid}`")
                    with c2:
                        st.metric("Total Actions", data["actions"])
                    c1, c2, c3 = st.columns(3)
                    c1.caption(f"First: {data['first']}")
                    c2.caption(f"Last: {data['last']}")
                    c3.caption(f"🚨 High-risk: {data['high_risk_count']}")
                    st.markdown("**Action breakdown:**")
                    cols = st.columns(min(4, len(data["breakdown"]) or 1))
                    for i, (act, n) in enumerate(data["breakdown"].items()):
                        cols[i % len(cols)].caption(f"• {act}: **{n}**")

    # ── Weekly ──
    with tabs[1]:
        st.markdown("#### Last 7 Days")
        for d in staff_monitor.weekly_summary():
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            c1.markdown(f"**{d['date']}**")
            c2.metric("Actions", d["actions"], label_visibility="collapsed")
            c3.metric("Staff", d["staff_count"], label_visibility="collapsed")
            c4.metric("🚨", d["high_risk"], label_visibility="collapsed")

    # ── Alerts ──
    with tabs[2]:
        st.markdown("#### 🚨 Suspicious Activity (Last 24h)")
        alerts = staff_monitor.suspicious_activity()
        if not alerts:
            st.success("✅ No suspicious activity detected")
        else:
            for a in alerts:
                sev = a.get("severity", "low")
                icon = {"high": "🚨", "medium": "⚠️", "low": "ℹ️"}.get(sev, "ℹ️")
                if sev == "high":
                    st.error(f"{icon} **{a['title']}**\n\n{a['detail']}")
                elif sev == "medium":
                    st.warning(f"{icon} **{a['title']}**\n\n{a['detail']}")
                else:
                    st.info(f"{icon} **{a['title']}**\n\n{a['detail']}")

        st.markdown("---")
        st.markdown("#### Recent High-Risk Actions")
        today = staff_monitor.today_summary()
        if today["high_risk"]:
            for e in reversed(today["high_risk"][-10:]):
                st.error(f"**{e['time']}** · {e['staff_name']} · `{e['action']}` · {e.get('details','')}")
        else:
            st.caption("None today")

    # ── Messages ──
    with tabs[3]:
        unread = staff_messages.get_unread_for_owner()
        if unread:
            st.warning(f"🚨 {len(unread)} unread message(s)")
        all_msgs = staff_messages.get_all_for_owner()
        if not all_msgs:
            st.info("No messages yet")
        else:
            for m in all_msgs[:20]:
                with st.container(border=True):
                    icon = "🚨" if m.get("priority") == "urgent" else "💬"
                    tag = "🆕 " if not m.get("read") else ""
                    st.markdown(f"{tag}{icon} **{m['subject']}**")
                    st.caption(f"From: {m['from_name']} · {m['sent_at']}")
                    st.markdown(m["body"])
                    if m.get("replied"):
                        st.success(f"Your reply: {m['reply']}")
                    else:
                        reply_text = st.text_input("Reply", key=f"rep_{m['id']}")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("📤 Send Reply", key=f"sendrep_{m['id']}", use_container_width=True):
                                if reply_text.strip():
                                    staff_messages.reply(m["id"], reply_text)
                                    st.success("Sent"); st.rerun()
                        with col2:
                            if st.button("✓ Mark Read", key=f"mread_{m['id']}", use_container_width=True):
                                staff_messages.mark_read(m["id"]); st.rerun()

    # ── Full Log ──
    with tabs[4]:
        c1, c2, c3 = st.columns(3)
        flt_staff = c1.text_input("Staff ID filter", key="flt_staff")
        flt_action = c2.text_input("Action filter", key="flt_action")
        flt_risk = c3.selectbox("Risk", ["all", "high", "normal"], key="flt_risk")

        entries = staff_monitor.recent_actions(limit=500)
        if flt_staff:
            entries = [e for e in entries if flt_staff.lower() in e.get("staff_id", "").lower()]
        if flt_action:
            entries = [e for e in entries if flt_action.lower() in e.get("action", "").lower()]
        if flt_risk != "all":
            entries = [e for e in entries if e.get("risk", "normal") == flt_risk]

        st.caption(f"Showing {len(entries)} entries")

        for e in entries[:100]:
            risk_icon = "🚨" if e.get("risk") == "high" else "·"
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 2, 3])
                c1.markdown(f"{risk_icon} **{e.get('time','')}** · {e.get('date','')}")
                c2.markdown(f"**{e.get('staff_name','')}** `{e.get('staff_id','')}`")
                c3.markdown(f"`{e.get('action','')}`")
                if e.get("details"):
                    st.caption(f"↳ {e['details']}")

    # ── Export ──
    with tabs[5]:
        st.markdown("#### 📥 Export Activity Log")
        entries = staff_monitor.recent_actions(limit=1000)

        if not entries:
            st.info("No data to export")
        else:
            # CSV download
            buf = io.StringIO()
            writer = csv.writer(buf)
            writer.writerow(["Date", "Time", "Staff ID", "Staff Name", "Action", "Details", "Risk"])
            for e in entries:
                writer.writerow([
                    e.get("date",""), e.get("time",""),
                    e.get("staff_id",""), e.get("staff_name",""),
                    e.get("action",""), e.get("details",""),
                    e.get("risk",""),
                ])
            csv_data = buf.getvalue()

            st.download_button(
                "⬇️ Download CSV",
                data=csv_data,
                file_name=f"staff_audit_{staff_monitor.datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

            st.caption(f"{len(entries)} entries ready for download")
