# 🔒 Security & Deployment Checklist

## 1. Environment Variables (NEVER commit to GitHub)
Create a `.env` file in the root folder and in `api/`:
```env
# Streamlit Secrets (convert to .env for local testing)
TELEGRAM_BOT_TOKEN=your_token
UPI_ID=your_business_upi@okicici
ENV=production
FRONTEND_URL=https://your-netlify-url.netlify.app
cd "/home/swaminathan/Desktop/swami/AGI Pharma Application/pharma-agi"

echo "🛠️ Applying Safe File-Based Patch..."

# 1. Create the Python patch script safely
cat << 'EOF' > /tmp/fix_meena.py
from pathlib import Path
import re
import sys

meena_file = Path("apps_isolated/meena.py")
if not meena_file.exists():
    print("❌ meena.py not found.")
    sys.exit(1)

text = meena_file.read_text()

# 1. Ensure Path Fix
if "sys.path.insert(0, str(BASE_DIR))" not in text:
    top_fix = "import sys\nfrom pathlib import Path\nBASE_DIR = Path(__file__).resolve().parent.parent\nsys.path.insert(0, str(BASE_DIR))\n"
    text = re.sub(r'^from meena_modules\..*?\n', '', text, flags=re.MULTILINE)
    text = top_fix + text
    print("✅ Path fix injected.")

# 2. Add Imports safely
if "from meena_modules.owner_verification import render_owner_verification" not in text:
    text = text.replace("import streamlit as st", "import streamlit as st\nfrom meena_modules.owner_verification import render_owner_verification", 1)
    print("✅ Owner Verification import added.")

if "from meena_modules.upi_payment import render_upi_payment" not in text:
    text = text.replace("import streamlit as st", "import streamlit as st\nfrom meena_modules.upi_payment import render_upi_payment", 1)
    print("✅ UPI Payment import added.")

# 3. Inject Owner Verification into Owner Dashboard
# Find 'def page_owner' or 'def owner_dashboard'
match = re.search(r'def (page_owner|owner_dashboard|page_owner_dashboard)\(.*?\):', text)
if match and "render_owner_verification()" not in text:
    end_match = re.search(r'\ndef ', text[match.end():])
    insert_pos = match.end() + end_match.start() if end_match else len(text)
    inject = "\n    st.divider()\n    render_owner_verification()\n"
    text = text[:insert_pos] + inject + text[insert_pos:]
    print("✅ Owner Verification dashboard injected.")

# 4. Inject UPI Payment into Cart
match = re.search(r'def page_cart\(.*?\):', text)
if match and "render_upi_payment(" not in text:
    end_match = re.search(r'\ndef ', text[match.end():])
    insert_pos = match.end() + end_match.start() if end_match else len(text)
    inject = "\n    if 'cart' in st.session_state and len(st.session_state.cart) > 0:\n        total = sum(i.get('price', 0) * i.get('qty', 1) for i in st.session_state.cart)\n        render_upi_payment({'total': total, 'order_id': 'NEW'}, r)\n"
    text = text[:insert_pos] + inject + text[insert_pos:]
    print("✅ UPI Payment gateway injected into Cart.")

meena_file.write_text(text)

# Compile check
try:
    compile(text, "meena.py", "exec")
    print("✅ meena.py compiles cleanly.")
except SyntaxError as e:
    print(f"❌ Syntax error: {e}")
