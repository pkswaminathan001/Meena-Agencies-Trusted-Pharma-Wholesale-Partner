from pathlib import Path
import re

p = Path("apps_isolated/meena.py")
text = p.read_text()

new_login = '''def login_screen():
    import yaml
    import bcrypt
    from yaml.loader import SafeLoader

    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        st.title("🦚 Meena Agencies")
        st.caption("Trusted Pharma Wholesale Partner")
        
        with open('config.yaml') as file:
            config = yaml.load(file, Loader=SafeLoader)

        with st.form("login_form"):
            st.info("Please enter your Retailer ID and PIN.")
            uid = st.text_input("User ID").strip().lower() # 👈 FORCES LOWERCASE
            pin = st.text_input("PIN", type="password").strip()
            
            if st.form_submit_button("Login", use_container_width=True):
                users = config.get("credentials", {}).get("usernames", {})
                user = users.get(uid)
                
                if user:
                    stored_hash = user["password"]
                    if bcrypt.checkpw(pin.encode(), stored_hash.encode()):
                        user['id'] = uid
                        st.session_state.user = user
                        st.session_state.page = "home"
                        st.rerun()
                    else:
                        st.error("❌ Incorrect PIN")
                else:
                    st.error("❌ Invalid User ID")'''

pattern = re.compile(r'def login_screen\(\):.*?(?=\ndef |\Z)', re.DOTALL)
if pattern.search(text):
    text = pattern.sub(new_login + "\n\n", text)
    p.write_text(text)
    print("✅ login_screen replaced with Custom Case-Insensitive Login")
else:
    print("❌ Could not find login_screen")
