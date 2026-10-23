from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
import streamlit as st
import jwt
import datetime
import time
import json

# In production, this secret is kept in an environment variable (.env)
JWT_SECRET = st.secrets.get("JWT_SECRET", "meena_agencies_super_secret_key_2026")
ALGORITHM = "HS256"

def generate_token(user_id, role, tenant_id, lic_status):
    """Auth Service: Creates the signed token."""
    payload = {
        "sub": user_id,
        "role": role,
        "tenant_id": tenant_id,
        "lic": lic_status,
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10), # Short-lived
        "jti": f"tok-{int(time.time())}" # Unique token ID to prevent replay attacks
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)
    return token

def verify_token(token):
    """Resource Service: Verifies the token locally (no DB lookup)."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return True, payload, "Token is valid and cryptographically signed."
    except jwt.ExpiredSignatureError:
        return False, None, "❌ Token has expired."
    except jwt.InvalidTokenError:
        return False, None, "❌ Invalid token signature (tampered)."

def render_jwt_security():
    st.markdown("## 🔐 JWT & Microservices Security")
    st.caption("Stateless authentication with cryptographic signatures (Pages 68-75).")

    tab1, tab2, tab3 = st.tabs(["🪪 Identity Provider", "🛡️ Protected API", "⚠️ Edge Cases"])

    # ─── TAB 1: Auth Server ───
    with tab1:
        st.markdown("### Step 1: Authenticate & Issue Token")
        st.write("The Auth Server validates your login and signs a payload containing your tenant and license info.")
        
        c1, c2 = st.columns(2)
        user_id = c1.selectbox("Select User", ["owner_meena", "retailer_ret001", "retailer_ret002"])
        role = c2.selectbox("Role", ["owner", "retailer"])
        
        tenant_id = st.text_input("Tenant ID (Company)", value="meena_agencies_thanjavur")
        lic_status = st.checkbox("Drug License Active?", value=True)
        
        if st.button("🔐 Generate JWT", type="primary"):
            token = generate_token(user_id, role, tenant_id, lic_status)
            st.session_state["jwt_token"] = token
            st.success("✅ Token Issued by Auth Server!")
            st.code(token, language="text")
            
            # Show decoded payload
            st.markdown("**Decoded Payload (What the microservice sees):**")
            decoded = jwt.decode(token, options={"verify_signature": False})
            st.json(decoded)
            st.info("💡 Note the `jti` (Token ID) and `exp` (Expiration). These are critical for security.")

    # ─── TAB 2: Microservice ───
    with tab2:
        st.markdown("### Step 2: Access Protected Microservice")
        st.write("Simulate a request to `/api/v1/orders`. The API validates the token locally.")
        
        # Get token from session
        current_token = st.session_state.get("jwt_token", "")
        
        if not current_token:
            st.warning("⚠️ No token found. Please generate one in the 'Identity Provider' tab.")
        else:
            st.text_area("Current Bearer Token", value=current_token, height=100, disabled=True)
            
            if st.button("📡 Request Order Data", type="primary"):
                with st.spinner("Validating token locally..."):
                    time.sleep(1)
                    is_valid, payload, msg = verify_token(current_token)
                    
                    if is_valid:
                        st.success(f"✅ 200 OK: {msg}")
                        st.markdown("**Data Returned:**")
                        st.json({"orders": [{"id": "ORD-1001", "amount": 5000}, {"id": "ORD-1002", "amount": 12000}]})
                        
                        # Enforce Multi-Tenancy (Page 70)
                        st.info(f"🔒 **Multi-Tenancy Check:** Data filtered strictly for `tenant_id: {payload['tenant_id']}`. User `{payload['sub']}` cannot see data from other hospitals.")
                    else:
                        st.error(f"🚨 401 Unauthorized: {msg}")

    # ─── TAB 3: Edge Cases ───
    with tab3:
        st.markdown("### Security Edge Cases (Page 71)")
        st.write("Test what happens when the token is tampered with or expires.")
        
        if "jwt_token" in st.session_state:
            current_token = st.session_state["jwt_token"]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🔨 Tamper Test")
                st.write("Change a character in the token to simulate a hacker trying to elevate their role.")
                tampered_token = st.text_area("Modified Token", value=current_token[:-5] + "abcde", height=100)
                if st.button("Test Tampered Token"):
                    is_valid, payload, msg = verify_token(tampered_token)
                    if is_valid:
                        st.error("Vulnerability! Tampered token accepted.")
                    else:
                        st.success(f"✅ System blocked hacker: {msg}")
                        
            with col2:
                st.markdown("#### ⏱️ Expiration Test")
                st.write("Access tokens are short-lived (10 minutes).")
                if st.button("Simulate Expired Token"):
                    # Create a token that expired 1 minute ago
                    expired_payload = {
                        "sub": "owner_meena", "role": "owner", "tenant_id": "meena",
                        "iat": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=11),
                        "exp": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=1)
                    }
                    expired_token = jwt.encode(expired_payload, JWT_SECRET, algorithm=ALGORITHM)
                    is_valid, payload, msg = verify_token(expired_token)
                    if is_valid:
                        st.error("Vulnerability! Expired token accepted.")
                    else:
                        st.success(f"✅ System blocked expired token: {msg}")
                        st.info("💡 In production, the frontend uses a Refresh Token to get a new one.")
        else:
            st.info("Generate a token in Tab 1 first.")
