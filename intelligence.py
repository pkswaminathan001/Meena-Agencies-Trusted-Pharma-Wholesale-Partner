"""Owner Intelligence — AI business analyst for Meena Agencies"""
import os, json
from datetime import datetime, timedelta
from collections import defaultdict
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def load_activity():
    """Read worker activity log (from activity.json)."""
    if os.path.exists("activity.json"):
        with open("activity.json") as f: return json.load(f)
    return []


def log_activity(worker_id, action, details=""):
    """Record a worker action with timestamp."""
    acts = load_activity()
    acts.append({
        "ts": datetime.now().isoformat(),
        "worker": worker_id,
        "action": action,
        "details": details
    })
    with open("activity.json", "w") as f: json.dump(acts, f, indent=2)


def calculate_worker_metrics(activity, orders, days=7):
    """Return per-worker productivity metrics for last N days."""
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    recent = [a for a in activity if a["ts"] > cutoff]
    
    metrics = defaultdict(lambda: {
        "logins": 0, "logouts": 0, "orders_placed": 0,
        "session_minutes": 0, "breaks": 0,
        "first_login": None, "last_active": None,
        "actions": defaultdict(int)
    })
    
    for a in recent:
        w = a["worker"]
        m = metrics[w]
        m["actions"][a["action"]] += 1
        if a["action"] == "LOGIN_SUCCESS": m["logins"] += 1
        if a["action"] == "LOGOUT": m["logouts"] += 1
        if a["action"] == "ORDER_PLACED": m["orders_placed"] += 1
        if not m["first_login"] or a["ts"] < m["first_login"]:
            m["first_login"] = a["ts"]
        if not m["last_active"] or a["ts"] > m["last_active"]:
            m["last_active"] = a["ts"]
    
    # Calculate session duration
    for w, m in metrics.items():
        if m["first_login"] and m["last_active"]:
            start = datetime.fromisoformat(m["first_login"])
            end = datetime.fromisoformat(m["last_active"])
            m["session_minutes"] = int((end - start).total_seconds() / 60)
    
    return dict(metrics)


def detect_breaks(activity, min_break_minutes=15):
    """Detect gaps in activity (15+ min) = breaks."""
    if not activity: return []
    
    sorted_acts = sorted(activity, key=lambda x: x["ts"])
    breaks = []
    for i in range(1, len(sorted_acts)):
        prev = datetime.fromisoformat(sorted_acts[i-1]["ts"])
        curr = datetime.fromisoformat(sorted_acts[i]["ts"])
        gap = (curr - prev).total_seconds() / 60
        if gap >= min_break_minutes:
            breaks.append({
                "worker": sorted_acts[i]["worker"],
                "break_start": sorted_acts[i-1]["ts"],
                "break_end": sorted_acts[i]["ts"],
                "duration_min": int(gap),
                "before": sorted_acts[i-1]["action"],
                "after": sorted_acts[i]["action"]
            })
    return breaks


def analyze_workload_balance(worker_metrics):
    """Classify each worker: overloaded, balanced, underused."""
    if not worker_metrics: return {}
    counts = [m["orders_placed"] for m in worker_metrics.values()]
    if not counts: return {}
    avg = sum(counts) / len(counts)
    
    result = {}
    for w, m in worker_metrics.items():
        c = m["orders_placed"]
        if c > avg * 1.3:
            status = "🔴 Overloaded"
            advice = f"Processing {c} orders ({c/avg*100:.0f}% of average). Consider offloading."
        elif c < avg * 0.7:
            status = "🟡 Underused"
            advice = f"Only {c} orders ({c/avg*100:.0f}% of average). Has capacity."
        else:
            status = "🟢 Balanced"
            advice = f"{c} orders — consistent with peers."
        result[w] = {"status": status, "advice": advice, "orders": c, "avg": avg}
    return result


def generate_daily_report(worker_metrics, orders, retailers, breaks):
    """AI-generated narrative daily report."""
    today = datetime.now().strftime("%d-%b-%Y").upper()
    total_orders = len(orders)
    total_value = sum(o.get("total", 0) for o in orders)
    
    summary = f"""Meena Agencies Daily Report — {today}

Orders today: {total_orders}
Total order value: ₹{total_value:,.0f}
Active workers: {len(worker_metrics)}

Worker breakdown:"""
    for w, m in worker_metrics.items():
        summary += f"\n- {w}: {m['orders_placed']} orders, session {m['session_minutes']}min, logins {m['logins']}"
    
    if breaks:
        summary += f"\n\nBreaks detected: {len(breaks)}"
        for b in breaks[:5]:
            summary += f"\n- {b['worker']}: {b['duration_min']}min break"
    
    prompt = f"""You are a business intelligence analyst writing a daily report for a pharma wholesale owner.

DATA:
{summary}

Write a professional 5-6 sentence narrative report that:
1. Summarizes the day's performance
2. Highlights standout workers (positive or negative)
3. Notes any concerns (breaks, inactivity)
4. Gives 1-2 actionable recommendations

Be direct, specific, and use the numbers.

━━━ FORMATTING RULES (MANDATORY) ━━━
Do NOT write paragraphs. Return ONLY structured bullet points.
Use EXACTLY this shape:

📊 HEADLINE
   <one-line summary, max 20 words>

🚨 CRITICAL RISKS
   ├─ <risk 1>
   ├─ <risk 2>
   └─ <risk 3 if any>

📈 TRENDS
   ├─ <trend 1>
   └─ <trend 2>

👥 WORKER SIGNALS
   ├─ <worker>: <signal>
   └─ <worker>: <signal>

💡 ACTIONS (numbered, most urgent first)
   1️⃣  <action>
   2️⃣  <action>
   3️⃣  <action>

Rules:
- No paragraphs, no long sentences.
- Each bullet under 15 words.
- If a section has nothing, write "— none —".
- Use the emojis exactly as shown.
"""
    
    try:
        r = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role":"user","content":prompt}],
            temperature=0.3, max_tokens=250
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"Report generation failed: {e}"


def generate_weekly_insights(worker_metrics, orders, retailers, breaks):
    """AI weekly trend analysis."""
    total_orders = len(orders)
    total_value = sum(o.get("total", 0) for o in orders)
    avg_order = total_value / total_orders if total_orders else 0
    blocked = [r for r in retailers if r["status"] == "Blocked"]
    high_util = [r for r in retailers if r["outstanding"] / max(r["credit_limit"],1) > 0.85]
    
    data_summary = f"""Weekly Data:
Total orders: {total_orders}
Total value: ₹{total_value:,.0f}
Average order: ₹{avg_order:,.0f}
Active retailers: {len([r for r in retailers if r['status']=='Active'])}
Blocked retailers: {len(blocked)}
High credit utilization: {len(high_util)}
Total breaks detected: {len(breaks)}

Worker metrics:
{json.dumps({w: {"orders": m['orders_placed'], "session_min": m['session_minutes']} for w,m in worker_metrics.items()}, indent=2)}
"""
    
    prompt = f"""You are a senior business consultant analyzing a week of pharma wholesale data.

{data_summary}

Provide a strategic analysis in 8-10 sentences covering:
1. Overall business health
2. Trend identification (growing, stable, declining)
3. Risk areas (credit, worker, retailer concentration)
4. Opportunities (upsell, reactivation, efficiency)
5. Specific recommendations (3-5 action items)

Be analytical, not generic. Reference the data.

━━━ FORMATTING RULES (MANDATORY) ━━━
Do NOT write paragraphs. Return ONLY structured bullet points.
Use EXACTLY this shape:

📊 HEADLINE
   <one-line summary, max 20 words>

🚨 CRITICAL RISKS
   ├─ <risk 1>
   ├─ <risk 2>
   └─ <risk 3 if any>

📈 TRENDS
   ├─ <trend 1>
   └─ <trend 2>

👥 WORKER SIGNALS
   ├─ <worker>: <signal>
   └─ <worker>: <signal>

💡 ACTIONS (numbered, most urgent first)
   1️⃣  <action>
   2️⃣  <action>
   3️⃣  <action>

Rules:
- No paragraphs, no long sentences.
- Each bullet under 15 words.
- If a section has nothing, write "— none —".
- Use the emojis exactly as shown.
"""
    
    try:
        r = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role":"user","content":prompt}],
            temperature=0.4, max_tokens=300
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"Analysis failed: {e}"


def psychological_profile(worker_metrics, breaks):
    """AI analyzes behavior patterns for stress/burnout indicators."""
    if not worker_metrics:
        return "Not enough data yet. Need at least 1 week of activity."
    
    patterns = []
    for w, m in worker_metrics.items():
        worker_breaks = [b for b in breaks if b["worker"] == w]
        total_break_min = sum(b["duration_min"] for b in worker_breaks)
        pattern = f"{w}: {m['orders_placed']} orders, {m['session_minutes']}min session, {len(worker_breaks)} breaks ({total_break_min}min total)"
        patterns.append(pattern)
    
    prompt = f"""You are an organizational psychologist analyzing worker patterns in a small business.

Worker behavioral data (past week):
{chr(10).join(patterns)}

Provide a subtle, professional psychological analysis covering:
1. Engagement levels (based on session length, order output)
2. Potential stress/burnout indicators (long sessions, few breaks)
3. Disengagement signs (short sessions, low output)
4. Team dynamics (spread of work)
5. Wellbeing recommendations for the owner

Focus on workplace behavior patterns.

━━━ FORMATTING RULES (MANDATORY) ━━━
Do NOT write paragraphs. Return ONLY structured bullet points.
Use EXACTLY this shape:

📊 HEADLINE
   <one-line summary, max 20 words>

🚨 CRITICAL RISKS
   ├─ <risk 1>
   ├─ <risk 2>
   └─ <risk 3 if any>

📈 TRENDS
   ├─ <trend 1>
   └─ <trend 2>

👥 WORKER SIGNALS
   ├─ <worker>: <signal>
   └─ <worker>: <signal>

💡 ACTIONS (numbered, most urgent first)
   1️⃣  <action>
   2️⃣  <action>
   3️⃣  <action>

Rules:
- No paragraphs, no long sentences.
- Each bullet under 15 words.
- If a section has nothing, write "— none —".
- Use the emojis exactly as shown.
"""
    
    try:
        r = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role":"user","content":prompt}],
            temperature=0.5, max_tokens=250
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"Profile failed: {e}"


def strategic_recommendations(worker_metrics, orders, retailers, breaks):
    """AI gives owner 5+ strategic improvement ideas."""
    context = f"""Business snapshot:
- {len(retailers)} retailers ({len([r for r in retailers if r['status']=='Active'])} active, {len([r for r in retailers if r['status']=='Blocked'])} blocked)
- {len(orders)} total orders
- {len(worker_metrics)} staff
- {len(breaks)} breaks detected this period
- Total outstanding: ₹{sum(r['outstanding'] for r in retailers):,.0f}
- Total credit extended: ₹{sum(r['credit_limit'] for r in retailers):,.0f}
"""
    
    prompt = f"""You are a strategic advisor to a small pharma wholesale business owner in India.

{context}

Give the owner 5-7 specific, actionable recommendations to:
1. Improve profitability
2. Reduce credit risk
3. Increase staff efficiency
4. Grow retailer base
5. Improve operations

Each recommendation must be:
- Specific (not generic advice)
- Actionable within 30 days
- Measurable

Format each as RECOMMENDATION with IMPACT and EFFORT.

━━━ FORMATTING RULES (MANDATORY) ━━━
Do NOT write paragraphs. Return ONLY structured bullet points.
Use EXACTLY this shape:

📊 HEADLINE
   <one-line summary, max 20 words>

🚨 CRITICAL RISKS
   ├─ <risk 1>
   ├─ <risk 2>
   └─ <risk 3 if any>

📈 TRENDS
   ├─ <trend 1>
   └─ <trend 2>

👥 WORKER SIGNALS
   ├─ <worker>: <signal>
   └─ <worker>: <signal>

💡 ACTIONS (numbered, most urgent first)
   1️⃣  <action>
   2️⃣  <action>
   3️⃣  <action>

Rules:
- No paragraphs, no long sentences.
- Each bullet under 15 words.
- If a section has nothing, write "— none —".
- Use the emojis exactly as shown.
"""
    
    try:
        r = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role":"user","content":prompt}],
            temperature=0.5, max_tokens=300
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"Recommendations failed: {e}"


# ========== MONTHLY / YEARLY REPORTS ==========

def generate_monthly_report(worker_metrics, orders, retailers, breaks):
    """AI monthly business review."""
    total_orders = len(orders)
    total_value = sum(o.get("total", 0) for o in orders)
    avg_order = total_value / total_orders if total_orders else 0
    top_retailers = sorted(retailers, key=lambda r: r["outstanding"], reverse=True)[:3]
    top_ret_list = ", ".join([f"{r['shop']} (₹{r['outstanding']:,})" for r in top_retailers])
    
    context = f"""Month-to-date business review:
- Total orders: {total_orders}
- Total revenue: ₹{total_value:,.0f}
- Average order: ₹{avg_order:,.0f}
- Staff count: {len(worker_metrics)}
- Top 3 by outstanding: {top_ret_list}
- Total outstanding: ₹{sum(r['outstanding'] for r in retailers):,.0f}
- Credit extended: ₹{sum(r['credit_limit'] for r in retailers):,.0f}
- Breaks: {len(breaks)}"""
    
    prompt = f"""You are a monthly business reviewer for a pharma wholesale owner.

{context}

Write an executive monthly report (10-12 sentences) covering:
1. Overall month performance (good/bad/stable)
2. Revenue trajectory
3. Risk concentration (top retailers, blocked accounts)
4. Staff productivity trend
5. Three specific goals for next month

Use numbers. Be direct. No fluff.

━━━ FORMATTING RULES (MANDATORY) ━━━
Do NOT write paragraphs. Return ONLY structured bullet points.
Use EXACTLY this shape:

📊 HEADLINE
   <one-line summary, max 20 words>

🚨 CRITICAL RISKS
   ├─ <risk 1>
   ├─ <risk 2>
   └─ <risk 3 if any>

📈 TRENDS
   ├─ <trend 1>
   └─ <trend 2>

👥 WORKER SIGNALS
   ├─ <worker>: <signal>
   └─ <worker>: <signal>

💡 ACTIONS (numbered, most urgent first)
   1️⃣  <action>
   2️⃣  <action>
   3️⃣  <action>

Rules:
- No paragraphs, no long sentences.
- Each bullet under 15 words.
- If a section has nothing, write "— none —".
- Use the emojis exactly as shown.
"""
    try:
        r = client.chat.completions.create(model="qwen/qwen3.8-27b", messages=[{"role":"user","content":prompt}], temperature=0.4, max_tokens=300)
        return r.choices[0].message.content
    except Exception as e:
        return f"Report failed: {e}"


def generate_yearly_report(worker_metrics, orders, retailers, breaks):
    """AI yearly strategy review."""
    context = f"""Year-to-date snapshot:
- Orders: {len(orders)}
- Revenue: ₹{sum(o.get('total',0) for o in orders):,.0f}
- Retailers: {len(retailers)} total, {len([r for r in retailers if r['status']=='Active'])} active
- Staff: {len(worker_metrics)}
- Breaks logged: {len(breaks)}"""
    
    prompt = f"""You are writing a YEARLY STRATEGIC REVIEW for a pharma wholesale owner.

{context}

Write a 12-15 sentence annual review covering:
1. Year in numbers
2. Business growth analysis
3. Customer base health
4. Staff efficiency
5. Market positioning (vs typical Indian pharma wholesalers)
6. 5 strategic priorities for next year

Be specific and strategic.

━━━ FORMATTING RULES (MANDATORY) ━━━
Do NOT write paragraphs. Return ONLY structured bullet points.
Use EXACTLY this shape:

📊 HEADLINE
   <one-line summary, max 20 words>

🚨 CRITICAL RISKS
   ├─ <risk 1>
   ├─ <risk 2>
   └─ <risk 3 if any>

📈 TRENDS
   ├─ <trend 1>
   └─ <trend 2>

👥 WORKER SIGNALS
   ├─ <worker>: <signal>
   └─ <worker>: <signal>

💡 ACTIONS (numbered, most urgent first)
   1️⃣  <action>
   2️⃣  <action>
   3️⃣  <action>

Rules:
- No paragraphs, no long sentences.
- Each bullet under 15 words.
- If a section has nothing, write "— none —".
- Use the emojis exactly as shown.
"""
    try:
        r = client.chat.completions.create(model="qwen/qwen3.8-27b", messages=[{"role":"user","content":prompt}], temperature=0.4, max_tokens=300)
        return r.choices[0].message.content
    except Exception as e:
        return f"Report failed: {e}"


# ========== WORKER PROBLEM ANALYSIS ==========

def analyze_worker_problems(activity, orders):
    """Detect worker difficulties from activity patterns."""
    problems = []
    
    # Problem 1: Frequent re-logins (session issues)
    worker_logins = {}
    for a in activity:
        if a["action"] == "LOGIN_SUCCESS":
            worker_logins[a["worker"]] = worker_logins.get(a["worker"], 0) + 1
    for w, count in worker_logins.items():
        if count > 5:
            problems.append({
                "worker": w, "type": "Frequent re-logins", "severity": "medium",
                "detail": f"{count} logins — possibly session drops or forgot PIN",
                "fix": "Check if session timeout is too short, or PIN reset needed"
            })
    
    # Problem 2: Failed login attempts
    for a in activity:
        if a["action"] == "LOGIN_FAILED":
            problems.append({
                "worker": a["worker"], "type": "Failed login", "severity": "low",
                "detail": "Wrong PIN entered", "fix": "Reset PIN or retrain"
            })
    
    # Problem 3: OTP requests without order completion
    otp_requests = {}
    orders_placed = {}
    for a in activity:
        if a["action"] == "OTP_REQUESTED":
            otp_requests[a["worker"]] = otp_requests.get(a["worker"], 0) + 1
        if a["action"] == "ORDER_PLACED":
            orders_placed[a["worker"]] = orders_placed.get(a["worker"], 0) + 1
    for w, otps in otp_requests.items():
        placed = orders_placed.get(w, 0)
        if otps > placed * 1.5 and otps >= 3:
            problems.append({
                "worker": w, "type": "OTP abandonment", "severity": "medium",
                "detail": f"{otps} OTPs requested, only {placed} orders placed",
                "fix": "May be struggling with order form, or abandoning mid-way"
            })
    
    # Problem 4: Long gaps between order steps
    return problems


# ========== INDUSTRY BENCHMARKS ==========

INDUSTRY_BENCHMARKS = {
    "credit_utilization_pct": {"industry": 60, "unit": "%", "better": "lower"},
    "days_sales_outstanding": {"industry": 75, "unit": "days", "better": "lower"},
    "retailer_retention_pct": {"industry": 75, "unit": "%/year", "better": "higher"},
    "stock_turnover_x": {"industry": 8, "unit": "times/year", "better": "higher"},
    "order_processing_min": {"industry": 8, "unit": "minutes", "better": "lower"},
    "gross_margin_pct": {"industry": 15, "unit": "%", "better": "higher"},
    "monthly_growth_pct": {"industry": 3, "unit": "%", "better": "higher"},
}


def compare_to_industry(retailers, orders):
    """Calculate your metrics and compare to industry."""
    your = {}
    
    total_limit = sum(r["credit_limit"] for r in retailers)
    total_out = sum(r["outstanding"] for r in retailers)
    your["credit_utilization_pct"] = (total_out / total_limit * 100) if total_limit else 0
    your["days_sales_outstanding"] = 90  # placeholder — needs payment data
    
    results = []
    for key, bench in INDUSTRY_BENCHMARKS.items():
        your_val = your.get(key, "—")
        if your_val == "—":
            status = "no_data"
        elif bench["better"] == "lower":
            status = "good" if your_val <= bench["industry"] else "bad"
        else:
            status = "good" if your_val >= bench["industry"] else "bad"
        
        results.append({
            "metric": key.replace("_", " ").title(),
            "industry": f"{bench['industry']} {bench['unit']}",
            "yours": f"{your_val:.1f} {bench['unit']}" if your_val != "—" else "—",
            "status": status
        })
    return results
