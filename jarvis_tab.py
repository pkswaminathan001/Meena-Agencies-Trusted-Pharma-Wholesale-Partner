"""
jarvis_tab.py — JARVIS chat tab for Meena Agencies.
This file is ADDITIVE. It does not modify any existing app.py code.
Call render_jarvis_tab() from app.py to show JARVIS inside your app.
"""
import streamlit as st
import os
from pathlib import Path
from datetime import datetime


def _get_brain():
    """Try ai_brain; else fallback to Groq."""
    try:
        import ai_brain
        return ai_brain.ask
    except ImportError:
        return None


def _fallback_ask(question: str) -> str:
    """Fallback if ai_brain isn't ready yet."""
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
                {"role": "system", "content": "You are JARVIS, AI assistant for Meena Agencies pharmaceutical wholesale. Be concise, professional. Use ₹ for currency. If asked about specific data (orders, buyers, stock), say the data module is not connected yet and suggest asking after setup."},
                {"role": "user", "content": question},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        return r.choices[0].message.content or "No response"
    except Exception as e:
        return f"⚠️ JARVIS unavailable: {e}"


def ask_jarvis(question: str) -> dict:
    brain = _get_brain()
    if brain:
        try:
            r = brain(question)
            if isinstance(r, dict):
                return r
            return {"answer": str(r), "source": "ai_brain"}
        except Exception:
            return {"answer": _fallback_ask(question), "source": "fallback"}
    return {"answer": _fallback_ask(question), "source": "fallback"}


def render_jarvis_tab():
    """Render JARVIS inside your existing app as a tab."""
    # Header
    st.markdown("""
    <div style="text-align:center;padding:1rem 0;">
        <div style="font-size:3rem;">🤖</div>
        <div style="font-size:2rem;font-weight:900;
                    background:linear-gradient(90deg,#00d4ff,#7b61ff,#00d47a);
                    -webkit-background-clip:text;
                    -webkit-text-fill-color:transparent;
                    letter-spacing:2px;">JARVIS</div>
        <div style="color:#8892b0;font-size:0.75rem;letter-spacing:1px;">
            Meena Agencies · AI Assistant
        </div>
        <div style="display:inline-block;padding:0.3rem 0.8rem;
                    background:rgba(0,212,122,0.15);border:1px solid #00d47a;
                    border-radius:20px;color:#00d47a;font-size:0.7rem;
                    font-weight:600;margin-top:0.5rem;">● ONLINE</div>
    </div>
    """, unsafe_allow_html=True)

    # Init history
    if "jarvis_history" not in st.session_state:
        st.session_state.jarvis_history = [
            {"role": "assistant", "content": "Hello! I'm JARVIS 🤖\n\nAsk me anything about your business:\n• Top buyers this month\n• Pending orders\n• Who owes the most\n• Batches expiring in 30 days\n\nOr just say **hi jarvis**."}
        ]

    # Suggestions
    st.markdown("**Quick questions:**")
    c1, c2, c3, c4 = st.columns(4)
    sugg = [
        "Top buyers this month",
        "Pending orders",
        "Who owes the most",
        "Batches expiring in 30 days",
    ]
    for col, q in zip([c1, c2, c3, c4], sugg):
        with col:
            if st.button(q, key=f"jv_sug_{q[:15]}", use_container_width=True):
                st.session_state._jarvis_pending = q
                st.rerun()

    st.markdown("---")

    # Chat history
    for msg in st.session_state.jarvis_history:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])

    # Input
    pending = st.session_state.pop("_jarvis_pending", None) if "_jarvis_pending" in st.session_state else None
    user_input = st.chat_input("Ask JARVIS... (try: hi jarvis, top buyers this month)") or pending

    if user_input:
        # Wake word strip
        clean = user_input.lower()
        for wake in ["hi jarvis", "hey jarvis", "jarvis"]:
            clean = clean.replace(wake, "")
        clean = clean.strip(" ,.") or "hello"

        st.session_state.jarvis_history.append({"role": "user", "content": user_input})
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

        st.session_state.jarvis_history.append({"role": "assistant", "content": display})

        # Cap
        if len(st.session_state.jarvis_history) > 50:
            st.session_state.jarvis_history = st.session_state.jarvis_history[-50:]

    # Footer
    st.markdown("---")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("🗑️ Clear chat", key="jv_clear", use_container_width=True):
            st.session_state.jarvis_history = [
                {"role": "assistant", "content": "Chat cleared. Ask me anything."}
            ]
            st.rerun()
    with c2:
        st.toggle("🔊 Voice reply", key="jv_voice")

    st.caption(f"🤖 JARVIS · {datetime.now().strftime('%d-%b-%Y %H:%M')}")
