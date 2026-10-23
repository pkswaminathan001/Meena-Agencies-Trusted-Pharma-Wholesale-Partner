from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
import streamlit as st
import json
import os

def load_json(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

@st.cache_data(ttl=60)
def load_data():
    return load_json("retailers.json"), load_json("orders.json")

def answer_query(query: str) -> str:
    q = query.lower()
    
    # Load local data
    retailers = load_json(str(BASE_DIR / "retailers.json"))
    orders = load_json(str(BASE_DIR / "orders.json"))

    # 1. Questions about retailers
    if "retailer" in q or "shop" in q or "customer" in q:
        if "active" in q:
            active = [r for r in retailers if r.get("status") == "Active"]
            return f"📊 There are **{len(active)}** active retailers out of {len(retailers)} total."
        if "blocked" in q:
            blocked = [r for r in retailers if r.get("status") == "Blocked"]
            return f"⚠️ There are **{len(blocked)}** blocked retailers. You may need to review their credit."
        return f"🏪 You currently have **{len(retailers)}** retailers registered in the system."

    # 2. Questions about orders
    if "order" in q:
        if not orders:
            return "📦 I couldn't find any orders in `orders.json` right now."
        pending = [o for o in orders if o.get("status") == "Pending"]
        return f"📦 There are **{len(orders)}** total orders. **{len(pending)}** are currently pending."

    # 3. Questions about credit/dues
    if "credit" in q or "dues" in q or "balance" in q:
        total_due = sum(r.get("outstanding", 0) for r in retailers)
        return f"💰 The total outstanding balance across all retailers is **₹{total_due:,.2f}**."

    # Default response
    return "🤖 I'm still learning! I can answer questions about **retailers**, **orders**, and **credit/dues**. Try asking: *'How many active retailers do I have?'*"

def render_chatbot():
    st.markdown("### 🤖 Meena AI Assistant")
    st.caption("Ask me about your business data (retailers, orders, dues).")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Vanakkam! 🙏 I am your AI assistant. What would you like to know about the business today?"}
        ]

    # Display chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # React to user input
    if prompt := st.chat_input("E.g., How many active retailers do I have?"):
        # Display user message
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get response
        response = answer_query(prompt)

        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
