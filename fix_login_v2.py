from pathlib import Path
import re

p = Path("apps_isolated/meena.py")
text = p.read_text()

# The new login function compatible with streamlit-authenticator >= 0.4.1
new_login = '''def login_screen():
    import yaml
    from yaml.loader import SafeLoader
    import streamlit_authenticator as stauth

    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    # v0.4.1 API: location is mandatory, fields are optional
    authenticator.login(location='main', fields={'Form name': 'Login'})

    # Retrieve status from session state
    auth_status = st.session_state.get("authentication_status")
    username = st.session_state.get("username")
    name = st.session_state.get("name")

    if auth_status:
        # Build the user object from config
        user_data = config['credentials']['usernames'].get(username, {})
        user_data['id'] = username
        user_data['name'] = name
        st.session_state.user = user_data
        st.session_state.page = "home"
        st.rerun()
    elif auth_status is False:
        st.error('❌ Username/password is incorrect')
    elif auth_status is None:
        st.warning('👋 Please enter your username and password')'''

# Find and replace the old login_screen entirely
pattern = re.compile(r'def login_screen\(\):.*?(?=\ndef |\Z)', re.DOTALL)
if pattern.search(text):
    text = pattern.sub(new_login + "\n\n", text)
    p.write_text(text)
    print("✅ Successfully patched login_screen() for v0.4.1 API")
else:
    print("❌ Could not find login_screen function")
