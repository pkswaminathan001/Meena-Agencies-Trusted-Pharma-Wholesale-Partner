import json
import yaml
import bcrypt
from pathlib import Path

print("🔐 Rebuilding config.yaml...")

retailers_file = Path("retailers.json")
config = {
    "credentials": {"usernames": {}},
    "cookie": {"expiry_days": 30, "key": "meena_secret_key_987", "name": "meena_cookie"}
}

# Default password
default_pw = "Meena@123"
hashed_pw = bcrypt.hashpw(default_pw.encode(), bcrypt.gensalt()).decode()

# Verify the hash works before we save it
assert bcrypt.checkpw(default_pw.encode(), hashed_pw.encode()), "Bcrypt failed!"

if retailers_file.exists():
    users = json.loads(retailers_file.read_text())
    print(f"Found {len(users)} users in retailers.json")
    
    for u in users:
        # Try to find the username/ID
        uid = u.get("id") or u.get("Username") or u.get("username")
        if not uid: 
            continue
            
        config["credentials"]["usernames"][str(uid)] = {
            "email": u.get("email", f"{uid.lower()}@meena.com"),
            "name": u.get("shop", uid),
            "password": hashed_pw,
            "role": u.get("role", "Retailer"),
            "shop": u.get("shop", "Partner")
        }
        
    print("\n✅ Valid Usernames to log in with:")
    for name in config["credentials"]["usernames"].keys():
        print(f"   👉 Username: '{name}' | Password: '{default_pw}'")
else:
    print("⚠️ retailers.json not found!")

Path("config.yaml").write_text(yaml.dump(config, default_flow_style=False))
print("\n✅ config.yaml saved successfully.")
