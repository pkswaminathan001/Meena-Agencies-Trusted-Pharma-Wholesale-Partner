import os
import requests
import streamlit as st
from fpdf import FPDF
import datetime

def generate_invoice_pdf(order, user):
    """Generates a professional PDF invoice in memory."""
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(200, 10, txt="MEENA AGENCIES", ln=True, align='C')
    pdf.set_font("Helvetica", size=10)
    pdf.cell(200, 5, txt="Trusted Pharma Wholesale Partner", ln=True, align='C')
    pdf.ln(10)
    
    # Invoice Details
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(200, 10, txt=f"Invoice: {order.get('order_id')}", ln=True)
    pdf.set_font("Helvetica", size=10)
    pdf.cell(200, 5, txt=f"Date: {order.get('date', str(datetime.date.today()))}", ln=True)
    pdf.cell(200, 5, txt=f"Retailer: {user.get('shop', 'N/A')} ({user.get('id', 'N/A')})", ln=True)
    pdf.ln(5)
    
    # Table Header
    pdf.set_font("Helvetica", 'B', 10)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(80, 10, "Item", border=1, fill=True)
    pdf.cell(30, 10, "Qty", border=1, align='C', fill=True)
    pdf.cell(40, 10, "Price", border=1, align='C', fill=True)
    pdf.cell(40, 10, "Total", border=1, align='C', fill=True, ln=True)
    
    # Table Items
    pdf.set_font("Helvetica", size=10)
    for item in order.get('items', []):
        name = item.get('name', '')[:40]
        qty = str(item.get('qty', 0))
        price = f"Rs {float(item.get('price', 0)):.2f}"
        total = f"Rs {float(item.get('price', 0)) * int(item.get('qty', 0)):.2f}"
        
        pdf.cell(80, 10, name, border=1)
        pdf.cell(30, 10, qty, border=1, align='C')
        pdf.cell(40, 10, price, border=1, align='C')
        pdf.cell(40, 10, total, border=1, align='C', ln=True)
        
    # Total
    pdf.ln(5)
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(150, 10, "Grand Total:", border=0, align='R')
    pdf.cell(40, 10, f"Rs {float(order.get('total', 0)):.2f}", border=1, align='C', ln=True)
    
    # Footer
    pdf.ln(10)
    pdf.set_font("Helvetica", size=9)
    pdf.cell(200, 10, txt="Payment Status: VERIFIED & PAID", ln=True)
    pdf.cell(200, 10, txt="Thank you for your business!", ln=True, align='C')
    
    return bytes(pdf.output())

def send_invoice_to_telegram(chat_id, pdf_bytes, order_id):
    """Sends the generated PDF to the retailer's Telegram."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    try:
        token = st.secrets["TELEGRAM_BOT_TOKEN"]
    except:
        pass
        
    if not token or not chat_id:
        return False
        
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    files = {'document': (f"Invoice_{order_id}.pdf", pdf_bytes, 'application/pdf')}
    data = {'chat_id': chat_id, 'caption': f'✅ Payment Verified! Here is your invoice for Order {order_id}.'}
    
    try:
        res = requests.post(url, files=files, data=data, timeout=10)
        return res.status_code == 200
    except Exception:
        return False
