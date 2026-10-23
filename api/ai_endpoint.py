from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

def setup_ai_routes(app):
    @app.post("/api/ai-chat")
    def ai_chat(req: ChatRequest):
        msg = req.message.lower()
        
        if "dolo" in msg:
            return {"reply": "Dolo 650 is in stock. Current wholesale price is ₹30 per strip. Would you like to add 10 boxes to your cart?"}
        elif "order" in msg or "track" in msg:
            return {"reply": "Your last order ORD-8942 is currently out for delivery in Thanjavur and should arrive by 5 PM."}
        elif "credit" in msg or "balance" in msg:
            return {"reply": "Your current outstanding credit is ₹1,45,000. Your credit limit is ₹2,00,000. You have ₹55,000 available."}
        else:
            return {"reply": "I am your Meena AI assistant. I can help you find medicines, track orders, and check credit limits."}
