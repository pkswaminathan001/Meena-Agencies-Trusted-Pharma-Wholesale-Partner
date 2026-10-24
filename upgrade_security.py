import json
import yaml
import bcrypt
from pathlib import Path
import re

# ── 1. Create the secure config.yaml from existing retailers.json ──
print("🔐 Migrating users to secure config.yaml...")
retailers_file = Path("retailers.json")
config = {
    "credentials": {"usernames": {}},
    "cookie": {"expiry_days": 30, "key": "meena_secret_key_987", "name": "meena_cookie"}
}

if retailers_file.exists():
    users = json.loads(retailers_file.read_text())
    for u in users:
        uid = u.get("id")
        if not uid: continue
        # We generate a secure bcrypt hash for a default password: Meena@123
        default_pw = "Meena@123"
        hashed_pw = bcrypt.hashpw(default_pw.encode(), bcrypt.gensalt()).decode()
        
        config["credentials"]["usernames"][uid] = {
            "email": u.get("email", f"{uid.lower()}@meena.com"),
            "name": u.get("shop", uid),
            "password": hashed_pw,
            "role": u.get("role", "Retailer"),
            "shop": u.get("shop", "Partner")
        }
else:
    print("⚠️ retailers.json not found. Creating an empty config.")

Path("config.yaml").write_text(yaml.dump(config, default_flow_style=False))
print("✅ config.yaml created with default password: Meena@123")

# ── 2. Patch meena.py to use the new Authenticator ──
print("🛠️ Patching meena.py...")
p = Path("apps_isolated/meena.py")
text = p.read_text()

# Add imports
if "import streamlit_authenticator as stauth" not in text:
    text = text.replace("import streamlit as st", "import streamlit as st\nimport streamlit_authenticator as stauth\nimport yaml\nfrom yaml.loader import SafeLoader")

# Replace login_screen
new_login = '''def login_screen():
    # Load secure config
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    # Render login UI
    name, auth_status, username = authenticator.login('main')

    if auth_status:
        st.session_state.user = config['credentials']['usernames'][username]
        st.session_state.user['id'] = username
        st.session_state.page = "home"
        st.rerun()
    elif auth_status is False:
        st.error('❌ Username/password is incorrect')
    elif auth_status is None:
        st.warning('👋 Please enter your username and password')'''

# Regex replace the old login_screen
pattern = re.compile(r'def login_screen\(\):.*?(?=\ndef |\Z)', re.DOTALL)
if pattern.search(text):
    text = pattern.sub(new_login + "\n\n", text)
    print("✅ login_screen replaced with Secure Authenticator")

# Update sidebar Logout to clear new authenticator session
old_logout = '''        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()'''
new_logout = '''        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.query_params.clear()
            st.rerun()'''

if old_logout in text:
    text = text.replace(old_logout, new_logout)
    print("✅ Sidebar logout updated")

p.write_text(text)
