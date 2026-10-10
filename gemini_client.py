"""gemini_client.py — Gemini fallback for ask_engine."""
import os
from dotenv import load_dotenv
load_dotenv()

try:
    import google.generativeai as genai
    GEMINI_OK = True
except ImportError:
    GEMINI_OK = False

def gemini_ask(prompt: str) -> dict:
    """Ask Gemini. Returns dict like Groq."""
    if not GEMINI_OK:
        return {"error": "google-generativeai not installed. Run: pip install --user google-generativeai"}

    key = os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6Kltr_AlkggXpR0_4ObooYgZCGsapZslh2_7g2UlJ7FEQ").strip()
    if not key:
        return {"error": "GEMINI_API_KEY missing in .env"}

    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-3.5-flash-lite")
        response = model.generate_content(prompt)
        return {"text": response.text}
    except Exception as e:
        return {"error": str(e)}
