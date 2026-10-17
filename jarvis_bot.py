"""
jarvis_bot.py — 24/7 AI assistant for Meena Agencies.
Wake word: "jarvis"
Runs on port 8501.
"""
import streamlit as st
import os
import json
from datetime import datetime
from pathlib import Path

st.set_page_config(
    page_title="JARVIS — Meena Agencies",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════════════
# STYLING
# ═══════════════════════════════════════════════════
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(ellipse at top, #0a1535 0%, #050818 70%);
    }
    .jarvis-header {
        text-align: center;
        padding: 1.5rem 0;
        animation: pulse 3s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    .jarvis-title {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00d4ff, #7b61ff, #00d47a);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 4s linear infinite;
        letter-spacing: 2px;
    }
    @keyframes gradientShift {
        0% { background-position: 0% center; }
        100% { background-position: 200% center; }
    }
    .jarvis-sub {
        color: #8892b0;
        font-size: 0.85rem;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        background: rgba(0,212,122,0.15);
        border: 1px solid #00d47a;
        border-radius: 20px;
        color: #00d47a;
        font-size: 0.7rem;
        font-weight: 600;
        margin-top: 0.5rem;
        animation: pulse 2s infinite;
    }
    [data-testid="stChatMessage"] {
        background: rgba(26,31,58,0.6);
        border-radius: 14px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(0,212,255,0.15);
    }
    .suggestion-chip {
        display: inline-block;
        padding: 0.5rem 1rem;
        background: rgba(0,212,255,0.08);
        border: 1px solid rgba(0,212,255,0.3);
        border-radius: 20px;
        color: #00d4ff;
        font-size: 0.8rem;
        margin: 0.3rem;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════
st.markdown("""
<div class="jarvis-header">
    <div style="font-size:3rem;">🤖</div>
    <div class="jarvis-title">JARVIS</div>
    <div class="jarvis-sub">Meena Agencies · AI Assistant</div>
    <div class="status-badge">● ONLINE 24/7</div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
# BRAIN — connects to ai_brain.py if available
# ═══════════════════════════════════════════════════
def get_brain():
    """Try to load ai_brain; fallback to direct Groq."""
    try:
        import ai_brain
        return ai_brain.ask
    except ImportError:
        return None


def fallback_ask(question: str) -> str:
    """Simple Groq chat when ai_brain not available."""
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
                {"role": "system", "content": "You are JARVIS, AI assistant for Meena Agencies pharmaceutical wholesale business. Be concise, professional, helpful. Use ₹ for currency."},
                {"role": "user", "content": question},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        return r.choices[0].message.content or "No response"
    except Exception as e:
        return f"⚠️ Brain unavailable: {e}"


def ask_jarvis(question: str) -> dict:
    """Main entry. Returns {answer, source}."""
    brain = get_brain()
    if brain:
        try:
            result = brain(question)
            if isinstance(result, dict):
                return result
            return {"answer": str(result), "source": "ai_brain"}
        except Exception as e:
            return {"answer": fallback_ask(question), "source": "fallback"}
    else:
        return {"answer": fallback_ask(question), "source": "fallback"}


# ═══════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm JARVIS 🤖\n\nAsk me anything about your business:\n• Top buyers this month\n• Pending orders\n• Who owes the most\n• Batches expiring in 30 days\n\nSay \"hi jarvis\" to wake me up."}
    ]

if "jarvis_awake" not in st.session_state:
    st.session_state.jarvis_awake = True  # Always awake in 24/7 mode


# ═══════════════════════════════════════════════════
# SUGGESTED QUESTIONS
# ═══════════════════════════════════════════════════
st.markdown("**Quick questions:**")
_c1, _c2, _c3, _c4 = st.columns(4)
suggestions = [
    "Top 3 buyers this month",
    "Pending orders count",
    "Who owes the most",
    "Batches expiring in 30 days",
]
for _col, _q in zip([_c1, _c2, _c3, _c4], suggestions):
    with _col:
        if st.button(_q, key=f"jarvis_sug_{_q[:20]}", use_container_width=True):
            st.session_state._pending = _q
            st.rerun()

st.markdown("---")

# ═══════════════════════════════════════════════════
# CHAT HISTORY
# ═══════════════════════════════════════════════════
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])


# ═══════════════════════════════════════════════════
# INPUT
# ═══════════════════════════════════════════════════
_pending = st.session_state.pop("_pending", None) if "_pending" in st.session_state else None
user_input = st.chat_input("Type your question... (or say 'hi jarvis')") or _pending

if user_input:
    # Wake word detection — strip "jarvis"
    _clean = user_input.lower().replace("hi jarvis", "").replace("jarvis", "").replace("hey jarvis", "").strip(" ,.")
    if not _clean:
        _clean = "hello"

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("JARVIS thinking..."):
            result = ask_jarvis(_clean)
            answer = result.get("answer", "No answer")
            source = result.get("source", "")
            emoji = {"cache": "⚡", "sql": "🗄️", "notes": "📝", "fallback": "💬"}.get(source, "💬")
            display = f"{answer}\n\n<sub>— {emoji} {source}</sub>"
        st.markdown(display, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": display})

    # Cap at 50 messages
    if len(st.session_state.messages) > 50:
        st.session_state.messages = st.session_state.messages[-50:]


# ═══════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════
st.markdown("---")
_c1, _c2, _c3 = st.columns([2, 1, 1])
with _c2:
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Chat cleared. Ask me anything."}
        ]
        st.rerun()
with _c3:
    _voice_on = st.toggle("🔊 Voice", value=False, key="jarvis_voice")

st.caption(f"🤖 JARVIS · Meena Agencies · {datetime.now().strftime('%d-%b-%Y %H:%M')}")

# Voice output via browser TTS
if _voice_on and st.session_state.messages:
    _last = st.session_state.messages[-1]["content"] if st.session_state.messages else ""
    _clean_text = _last.replace("<sub>", "").replace("</sub>", "").replace("*", "")
    if _last and _clean_text:
        st.components.v1.html(f"""
        <script>
        var msg = new SpeechSynthesisUtterance({json.dumps(_clean_text[:300])});
        msg.rate = 1.0; msg.pitch = 1.0;
        window.speechSynthesis.speak(msg);
        </script>
        """, height=0)
