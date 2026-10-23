import pytest
import sys
import os
import json

# Ensure the parent directory is in path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_chatbot import answer_query
from sql_engine import is_safe_query
from jwt_security import generate_token, verify_token

# ─── 1. Smoke Testing (Page 2) ───
def test_smoke_files_exist():
    """Checks if critical files are present before running deeper tests."""
    assert os.path.exists("retailers.json"), "Critical file missing: retailers.json"
    assert os.path.exists("inventory.csv"), "Critical file missing: inventory.csv"

# ─── 2. Unit Testing (Page 2) ───
def test_chatbot_active_retailers():
    """Tests if the chatbot correctly returns active retailers."""
    response = answer_query("How many active retailers do I have?")
    assert "active retailers" in response.lower()

# ─── 3. Security Testing (SQL Injection) (Page 3) ───
def test_sql_guardrail_blocks_delete():
    """Tests if the SQL engine blocks destructive commands."""
    is_safe, kw = is_safe_query("DELETE FROM retailers WHERE id = 'RET001'")
    assert is_safe is False, "Security Flaw: DELETE query was not blocked!"
    assert kw == "DELETE"

def test_sql_guardrail_allows_select():
    """Tests if safe read-only commands are allowed."""
    is_safe, kw = is_safe_query("SELECT * FROM retailers")
    assert is_safe is True

# ─── 4. Fuzz Testing (Page 3) ───
def test_fuzz_adversarial_prompt():
    """Injects garbage/chaos into the chatbot to ensure it doesn't crash."""
    chaotic_prompts = [
        "'; DROP TABLE users; --",
        "\x00\x01\x02 invalid bytes",
        "A" * 10000,  # Long string buffer overflow test
        '{"malformed_json": true,' # FIXED: Using single quotes here
    ]
    for prompt in chaotic_prompts:
        # Should return a safe string, not raise an exception
        response = answer_query(prompt)
        assert isinstance(response, str), f"Failed to handle chaotic input: {prompt[:10]}"

# ─── 5. JWT Security Testing (Page 3) ───
def test_jwt_tamper_detection():
    """Ensures tampered tokens are rejected."""
    token = generate_token("test_user", "owner", "tenant_1", True)
    is_valid, payload, msg = verify_token(token)
    assert is_valid is True, "Valid token was rejected!"
    
    # Tamper with the token
    tampered_token = token[:-5] + "abcde"
    is_valid_tampered, _, msg_tampered = verify_token(tampered_token)
    assert is_valid_tampered is False, "Security Flaw: Tampered token was accepted!"
    assert "Invalid token" in msg_tampered or "signature" in msg_tampered
