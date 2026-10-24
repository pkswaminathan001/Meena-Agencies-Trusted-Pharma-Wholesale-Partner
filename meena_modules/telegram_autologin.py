import streamlit as st
import streamlit.components.v1 as components
import json, os, urllib.parse

def run_telegram_autologin():
    if "tg_user_id" not in st.session_state:
        try:
            qp = st.query_params
        except:
            qp = dict(urllib.parse.parse_qsl(os.environ.get("QUERY_STRING", "")))
        
        if "tg_user_id" not in qp:
            components.html("""
            <script src="https://telegram.org/js/telegram-web-app.js"></script>
            <script>
            window.onload = function() {
                const tg = window.Telegram.WebApp;
                tg.ready();
                if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
                    const u = tg.initDataUnsafe.user;
                    const url = new URL(window.parent.location.href);
                    if (!url.searchParams.has('tg_user_id')) {
                        url.searchParams.set('tg_user_id', u.id);
                        url.searchParams.set('tg_user_name', u.first_name || 'User');
                        window.parent.location.href = url.href;
                    }
                }
            };
            </script>
            """, height=0)

    tg_user_id = qp.get("tg_user_id") or st.session_state.get("tg_user_id")
    tg_user_name = qp.get("tg_user_name") or st.session_state.get("tg_user_name")

    if tg_user_id and st.session_state.get("role") is None:
        st.session_state.tg_user_id = tg_user_id
        st.session_state.tg_user_name = tg_user_name
        
        if os.path.exists("retailers.json"):
            with open("retailers.json") as f:
                retailers = json.load(f)
            matched = next((r for r in retailers if str(r.get("telegram_chat_id", "")) == str(tg_user_id)), None)
            if matched:
                st.session_state.retailer = matched
                st.session_state.role = "retailer"
                st.rerun()
        
        st.session_state.role = "customer"
        st.session_state.retailer = {
            "id": f"TG_{tg_user_id}", "shop": f"{tg_user_name}'s Pharmacy", 
            "owner": tg_user_name, "phone": "", "credit_limit": 0, 
            "outstanding": 0, "status": "Active"
        }
        st.rerun()
