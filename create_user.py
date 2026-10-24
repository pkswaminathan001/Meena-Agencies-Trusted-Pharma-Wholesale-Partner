import yaml
import bcrypt
from pathlib import Path

# Create the hash for password '3210'
hashed_pw = bcrypt.hashpw("3210".encode(), bcrypt.gensalt()).decode()

config = {
    "credentials": {"usernames": {
        "ret001": {
            "email": "ret001@meena.com",
            "name": "Sri Balaji Medicals",
            "password": hashed_pw,
            "role": "Retailer",
            "shop": "Sri Balaji Medicals"
        },
        "owner": {
            "email": "owner@meena.com",
            "name": "Owner",
            "password": bcrypt.hashpw("admin".encode(), bcrypt.gensalt()).decode(),
            "role": "Owner",
            "shop": "Meena Agencies HQ"
        }
    }},
    "cookie": {"expiry_days": 30, "key": "meena_secret_key_987", "name": "meena_cookie"}
}

Path("config.yaml").write_text(yaml.dump(config, default_flow_style=False))
print("✅ config.yaml created with ret001 / 3210")
