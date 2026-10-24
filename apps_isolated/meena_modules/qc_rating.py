import streamlit as st
import pandas as pd

def calculate_employee_qc_score(employee_id, load_activity, load_orders):
    try:
        activity = load_activity()
        orders = load_orders()
    except:
        return {"employee_id": employee_id, "total_score": 0, "grade": "N/A"}

    emp_activity = [a for a in activity if a.get("worker") == employee_id]
    emp_orders = [o for o in orders if o.get("processed_by") == employee_id]
    
    login_days = len(set(a.get("ts", "")[:10] for a in emp_activity if "LOGIN" in a.get("action", "")))
    attendance_score = min(20, login_days * 0.67)
    total_actions = len(emp_activity)
    activity_score = min(20, total_actions / 50)
    completed = len([o for o in emp_orders if o.get("status") in ("Approved", "Delivered")])
    total = len(emp_orders)
    completion_rate = (completed / total * 100) if total > 0 else 0
    task_score = (completion_rate / 100) * 20
    
    total_score = attendance_score + activity_score + task_score + 40
    
    if total_score >= 85: grade = "A+"
    elif total_score >= 70: grade = "A"
    elif total_score >= 55: grade = "B"
    elif total_score >= 40: grade = "C"
    else: grade = "D"
    return {"employee_id": employee_id, "total_score": round(total_score, 1), "grade": grade}

def render_qc_dashboard(load_activity, load_orders):
    st.markdown("### 🎯 QC Auto-Rating System")
    try:
        activity = load_activity()
    except:
        st.info("Could not load activity data.")
        return
        
    workers = list(set(a.get("worker", "") for a in activity if a.get("worker") and a.get("worker") != "OWNER"))
    
    if not workers:
        st.info("No employee data yet.")
        return
        
    results = [calculate_employee_qc_score(w, load_activity, load_orders) for w in workers]
    results.sort(key=lambda x: x["total_score"], reverse=True)
    
    for r in results:
        score_color = "#00d47a" if r["total_score"] >= 70 else ("#ffb547" if r["total_score"] >= 55 else "#ff4d6d")
        st.markdown(f"""
        <div style="background:rgba(26,31,58,0.7);border-left:4px solid {score_color};border-radius:12px;padding:1.2rem;margin:0.8rem 0;">
            <span style="font-size:1.3rem;font-weight:700;">👤 {r['employee_id']}</span> | 
            <span style="color:{score_color};font-weight:600;">{r['grade']}</span> | 
            <span style="font-size:1.5rem;font-weight:900;color:{score_color};">{r['total_score']}/100</span>
        </div>
        """, unsafe_allow_html=True)
