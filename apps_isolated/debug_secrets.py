"""Debug page — shows what Streamlit Cloud sees in secrets."""
import streamlit as st

st.title("🔍 Secrets Debug")

st.write("**`st.secrets` keys visible:**")
try:
    for key in st.secrets:
        val = st.secrets[key]
        if isinstance(val, str):
            masked = val[:5] + "..." + val[-5:] if len(val) > 15 else "(short)"
            st.write(f"- `{key}` = `{masked}` (len={len(val)})")
        else:
            st.write(f"- `{key}` = (type: {type(val).__name__})")
except Exception as e:
    st.error(f"Error reading secrets: {e}")

st.write("**Direct access test:**")
for key in ("TELEGRAM_BOT_TOKEN", "OWNER_CHAT_ID"):
    try:
        val = st.secrets.get(key)
        if val:
            masked = val[:5] + "..." + val[-5:] if len(val) > 15 else val
            st.success(f"✅ `{key}` = `{masked}`")
        else:
            st.error(f"❌ `{key}` is EMPTY or MISSING")
    except Exception as e:
        st.error(f"❌ `{key}`: {e}")

st.write("**block15_otp._get_secret test:**")
try:
    import block15_otp
    for key in ("TELEGRAM_BOT_TOKEN", "OWNER_CHAT_ID"):
        val = block15_otp._get_secret(key)
        if val:
            masked = val[:5] + "..." + val[-5:] if len(val) > 15 else val
            st.success(f"✅ `{key}` = `{masked}`")
        else:
            st.error(f"❌ `{key}` returns EMPTY")
except Exception as e:
    st.error(f"Import error: {e}")

st.write("**Live Telegram send test:**")
if st.button("Send test OTP now"):
    try:
        import block15_otp
        result = block15_otp.send_otp_telegram(
            "DEBUG", "Debug Shop", "123456", 0.01, 1
        )
        st.write(f"Result: `{result}`")
        if result and result[0]:
            st.success("✅ Telegram API accepted the message. Check your phone.")
        else:
            st.error(f"❌ {result}")
    except Exception as e:
        st.error(f"Exception: {e}")
