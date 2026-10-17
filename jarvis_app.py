"""
jarvis_app.py — Standalone Jarvis app. Runs on port 8502.
Open http://localhost:8502 to use Jarvis.
"""
import streamlit as st
import os
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="JARVIS",
    page_icon="🤖",
    layout="centered",
)

# ═══════════════════════════════════════════════════
# STYLING
# ═══════════════════════════════════════════════════
st.markdown("""
<style>
    .stApp { background: radial-gradient(ellipse at top, #0a1535 0%, #050818 70%); }
    .jarvis-header { text-align: center; padding: 2rem 0 1rem 0; }
    .jarvis-icon { font-size: 4rem; animation: pulse 3s ease-in-out infinite; }
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.05); opacity: 0.85; }
    }
    .jarvis-title {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00d4ff, #7b61ff, #00d47a);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 4s linear infinite;
        letter-spacing: 3px;
    }
    @keyframes gradientShift {
        0% { background-position: 0% center; }
        100% { background-position: 200% center; }
    }
    .jarvis-sub {
        color: #8892b0;
        font-size: 0.85rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 0.5rem;
    }
    .online-badge {
        display: inline-block;
        padding: 0.35rem 1rem;
        background: rgba(0,212,122,0.15);
        border: 1px solid #00d47a;
        border-radius: 20px;
        color: #00d47a;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1px;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════
st.markdown("""
<div class="jarvis-header">
    <div class="jarvis-icon">🤖</div>
    <div class="jarvis-title">JARVIS</div>
    <div class="jarvis-sub">Meena Agencies · AI Assistant</div>
    <div class="online-badge">● ONLINE 24/7</div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
# BRAIN
# ═══════════════════════════════════════════════════
def get_brain():
    try:
        import ai_brain
        return ai_brain.ask
    except ImportError:
        return None


def fallback_ask(question: str) -> str:
    try:
        from groq import Groq
        key = os.getenv("GROQ_API_KEY", "").strip()
        if not key:
            for line in Path(".env").read_text().splitlines():
                if line.startswith("GROQ_API_KEY="):
                    key = line.split("=", 1)[1].strip()
        client = Groq(api_key=key)
        r = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "You are JARVIS, AI assistant for Meena Agencies pharmaceutical wholesale business. Be concise, professional, helpful. Use Rs/₹ for currency."},
                {"role": "user", "content": question},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        return r.choices[0].message.content or "No response"
    except Exception as e:
        return f"⚠️ JARVIS brain error: {e}"


def ask_jarvis(q):
    brain = get_brain()
    if brain:
        try:
            r = brain(q)
            if isinstance(r, dict):
                return r
            return {"answer": str(r), "source": "ai_brain"}
        except Exception:
            return {"answer": fallback_ask(q), "source": "fallback"}
    return {"answer": fallback_ask(q), "source": "fallback"}


# ═══════════════════════════════════════════════════
# CHAT
# ═══════════════════════════════════════════════════
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! I'm JARVIS 🤖\n\nAsk me anything about Meena Agencies:\n• Top buyers this month\n• Pending orders\n• Who owes the most\n• Batches expiring in 30 days\n\nJust type below."
    }]

# Suggestions
st.markdown("**Try these:**")
c1, c2, c3, c4 = st.columns(4)
for col, q in zip([c1, c2, c3, c4],
                   ["Top buyers", "Pending orders", "Who owes most", "Expiring soon"]):
    with col:
        if st.button(q, key=f"s_{q[:10]}", use_container_width=True):
            st.session_state._pending = q
            st.rerun()

st.markdown("---")

# History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# Input
pending = st.session_state.pop("_pending", None) if "_pending" in st.session_state else None
user_input = st.chat_input("Ask JARVIS...") or pending

if user_input:
    clean = user_input.lower()
    for wake in ["hi jarvis", "hey jarvis", "jarvis"]:
        clean = clean.replace(wake, "")
    clean = clean.strip(" ,.") or "hello"

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("JARVIS thinking..."):
            result = ask_jarvis(clean)
            answer = result.get("answer", "No answer")
            source = result.get("source", "")
            emoji = {"cache": "⚡", "sql": "🗄️", "notes": "📝", "fallback": "💬"}.get(source, "💬")
            display = f"{answer}\n\n<sub style='color:#8892b0;font-size:0.75rem;'>— {emoji} {source}</sub>"
        st.markdown(display, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": display})
    if len(st.session_state.messages) > 50:
        st.session_state.messages = st.session_state.messages[-50:]

st.markdown("---")
if st.button("🗑️ Clear chat", key="clear"):
    st.session_state.messages = [{"role": "assistant", "content": "Chat cleared."}]
    st.rerun()

st.caption(f"🤖 JARVIS · {datetime.now().strftime('%d-%b-%Y %H:%M')}")
