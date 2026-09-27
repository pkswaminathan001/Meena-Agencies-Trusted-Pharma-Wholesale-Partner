"""
intent_router.py — classify retailer messages via Groq + rule fallback.
Categories: order_request | complaint | question | payment | chitchat
"""
import os, json, re
from pathlib import Path

try:
    import requests
    HAS_REQ = True
except ImportError:
    HAS_REQ = False


INTENTS = ["order_request", "complaint", "question", "payment", "chitchat"]

# Fast rule-based pre-classifier (runs before LLM)
RULES = [
    ("complaint",    [r"\b(late|delay|short|damaged|broken|wrong|missing|not received|bad|expired)\b"]),
    ("payment",      [r"\b(payment|paid|pay|cheque|neft|upi|outstanding|balance|settle)\b"]),
    ("order_request",[r"\b(need|order|want|send|deliver|stock|boxes?|strips?|units?|qty|quantity)\b"]),
    ("question",     [r"\b(price|rate|mrp|when|how much|available|stock\?|cost)\b"]),
]


def _env(key, default=""):
    p = Path(".env")
    if p.exists():
        for line in p.read_text().splitlines():
            if line.startswith(f"{key}="):
                return line.split("=", 1)[1].strip()
    return default


GROQ_KEY = _env("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def rule_classify(text):
    t = text.lower()
    for intent, patterns in RULES:
        for pat in patterns:
            if re.search(pat, t):
                return intent
    return None


def llm_classify(text):
    """Ask Groq to classify. Returns (intent, confidence, reason)."""
    if not HAS_REQ or not GROQ_KEY:
        return None

    prompt = (
        "You classify messages from pharmacy retailers to a pharma wholesaler.\n"
        "Pick ONE category: order_request, complaint, question, payment, chitchat.\n"
        "Reply in EXACT JSON: {\"intent\": \"...\", \"confidence\": 0.0-1.0}\n\n"
        f"Message: {text}"
    )
    try:
        r = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "response_format": {"type": "json_object"},
            },
            timeout=12,
        ).json()
        content = r["choices"][0]["message"]["content"]
        data = json.loads(content)
        intent = data.get("intent", "").strip()
        if intent in INTENTS:
            return intent, float(data.get("confidence", 0.7))
    except Exception as e:
        return None
    return None


def classify(text):
    """
    Returns dict: {intent, confidence, source, raw}
    source = 'rule' | 'llm' | 'fallback'
    """
    if not text or not text.strip():
        return {"intent": "chitchat", "confidence": 0.0, "source": "fallback"}

    # 1. Rules first (fast + cheap)
    rule = rule_classify(text)
    if rule:
        return {"intent": rule, "confidence": 0.9, "source": "rule"}

    # 2. LLM
    llm = llm_classify(text)
    if llm:
        return {"intent": llm[0], "confidence": llm[1], "source": "llm"}

    # 3. Fallback
    return {"intent": "chitchat", "confidence": 0.3, "source": "fallback"}


# Suggested auto-replies per intent — owner can override
AUTO_REPLIES = {
    "order_request": "📝 Got your request. Owner will confirm availability and price shortly.",
    "complaint":     "⚠️ Sorry to hear that. Owner has been notified and will reply personally.",
    "question":      "❓ Noted. Owner will reply with details shortly.",
    "payment":       "💳 Noted. Accounts team will confirm.",
    "chitchat":      "🙏 Thanks for your message. We'll reply shortly.",
}


if __name__ == "__main__":
    tests = [
        "Dolo 650 need 20 boxes urgent",
        "Last delivery was short by 3 boxes",
        "What is the MRP of Amoxicillin 500?",
        "Payment done today via NEFT",
        "Good morning",
    ]
    for t in tests:
        r = classify(t)
        print(f"[{r['intent']:>14} | {r['source']:>8} | {r['confidence']}] {t}")
