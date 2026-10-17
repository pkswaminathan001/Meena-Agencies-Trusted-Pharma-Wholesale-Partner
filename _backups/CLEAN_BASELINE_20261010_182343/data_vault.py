"""data_vault.py — Encrypt data at rest. Stolen files become useless."""
import os, json, base64
from pathlib import Path
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_OK = True
except ImportError:
    CRYPTO_OK = False

VAULT_DIR = Path("_vault")
KEY_FILE = Path(".vault_key")
SALT_FILE = Path(".vault_salt")
SENSITIVE_EXT = {".json", ".csv", ".db", ".jsonl"}
EXCLUDE_FILES = {"company.json", ".vault_salt", ".vault_key", ".env"}

def _get_or_create_salt():
    if SALT_FILE.exists(): return SALT_FILE.read_bytes()
    salt = os.urandom(16); SALT_FILE.write_bytes(salt); return salt

def _derive_key(password):
    salt = _get_or_create_salt()
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=200_000)
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def init_vault(owner_password):
    if not CRYPTO_OK:
        return {"ok": False, "msg": "Install: pip install --user cryptography"}
    key = _derive_key(owner_password)
    KEY_FILE.write_bytes(key)
    os.chmod(KEY_FILE, 0o600)
    VAULT_DIR.mkdir(exist_ok=True)
    return {"ok": True, "msg": "Vault initialized"}

def _get_fernet():
    if not CRYPTO_OK or not KEY_FILE.exists(): return None
    return Fernet(KEY_FILE.read_bytes())

def encrypt_file(filepath, password=None):
    f = Path(filepath)
    if not f.exists(): return {"ok": False, "msg": f"Not found: {filepath}"}
    if f.name in EXCLUDE_FILES: return {"ok": False, "msg": "Skipped"}
    if password is not None:
        if not KEY_FILE.exists() or _derive_key(password) != KEY_FILE.read_bytes():
            return {"ok": False, "msg": "Wrong password"}
    fernet = _get_fernet()
    if not fernet: return {"ok": False, "msg": "Vault not initialized"}
    vault_path = VAULT_DIR / (f.name + ".vault")
    vault_path.write_bytes(fernet.encrypt(f.read_bytes()))
    f.unlink()
    return {"ok": True, "msg": f"Encrypted: {f.name}"}

def encrypt_all(password):
    results = {"encrypted": [], "skipped": [], "failed": []}
    for f in Path(".").glob("*"):
        if not f.is_file(): continue
        if f.suffix not in SENSITIVE_EXT: continue
        if f.name in EXCLUDE_FILES:
            results["skipped"].append(f.name); continue
        r = encrypt_file(str(f), password)
        if r["ok"]: results["encrypted"].append(f.name)
        else: results["failed"].append(f"{f.name}: {r['msg']}")
    return results

def vault_status():
    return {
        "initialized": KEY_FILE.exists(),
        "encrypted_count": len(list(VAULT_DIR.glob("*.vault"))) if VAULT_DIR.exists() else 0,
        "crypto_available": CRYPTO_OK,
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(json.dumps(vault_status(), indent=2))
    elif sys.argv[1] == "init" and len(sys.argv) >= 3:
        print(init_vault(sys.argv[2]))
    elif sys.argv[1] == "status":
        print(json.dumps(vault_status(), indent=2))
    elif sys.argv[1] == "encrypt-all" and len(sys.argv) >= 3:
        print(json.dumps(encrypt_all(sys.argv[2]), indent=2))

def decrypt_file(vault_name, output_path=None, password=None):
    """Decrypt a .vault file. If output_path None, returns bytes only."""
    if not CRYPTO_OK:
        return {"ok": False, "msg": "cryptography not installed"}
    if password is not None:
        if not KEY_FILE.exists() or _derive_key(password) != KEY_FILE.read_bytes():
            return {"ok": False, "msg": "Wrong owner password"}
    vault_path = VAULT_DIR / vault_name
    if not vault_path.exists():
        vault_path = Path(vault_name)
        if not vault_path.exists():
            return {"ok": False, "msg": f"Vault file {vault_name} not found"}
    fernet = _get_fernet()
    if not fernet:
        return {"ok": False, "msg": "Vault not initialized"}
    encrypted = vault_path.read_bytes()
    try:
        data = fernet.decrypt(encrypted)
    except Exception as e:
        return {"ok": False, "msg": f"Decryption failed: {e}"}
    if output_path:
        Path(output_path).write_bytes(data)
        return {"ok": True, "msg": f"Decrypted to {output_path}", "bytes": len(data)}
    return {"ok": True, "data": data}
