import datetime

def generate_invoice_pdf(order_id, retailer_name, items, total_amount, filepath="invoice.pdf"):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", "B", 24)
    pdf.set_text_color(11, 60, 93) # Medical Blue
    pdf.cell(200, 10, txt="MEENA AGENCIES", ln=True, align="C")
    
    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(200, 10, txt="Trusted Pharma Wholesale Partner | Thanjavur, TN", ln=True, align="C")
    pdf.ln(10)
    
    # Details
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(100, 10, txt=f"Invoice #: {order_id}", ln=False)
    pdf.cell(90, 10, txt=f"Date: {datetime.date.today()}", ln=True, align="R")
    
    pdf.set_font("Arial", "", 12)
    pdf.cell(100, 10, txt=f"Billed To: {retailer_name}", ln=True)
    pdf.ln(10)
    
    # Table Header
    pdf.set_fill_color(29, 131, 72) # Pharma Green
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(80, 10, "Medicine", border=1, fill=True)
    pdf.cell(30, 10, "Qty", border=1, fill=True, align="C")
    pdf.cell(40, 10, "Price", border=1, fill=True, align="C")
    pdf.cell(40, 10, "Total", border=1, fill=True, align="C")
    pdf.ln()
    
    # Rows
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 12)
    for item in items:
        pdf.cell(80, 10, str(item.get('name', 'Medicine'))[:30], border=1)
        pdf.cell(30, 10, str(item.get('qty', 1)), border=1, align="C")
        pdf.cell(40, 10, f"Rs. {item.get('price', 0):.2f}", border=1, align="R")
        pdf.cell(40, 10, f"Rs. {item.get('price', 0) * item.get('qty', 1):.2f}", border=1, align="R")
        pdf.ln()
        
    # Total
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(150, 10, "Grand Total:", align="R")
    pdf.cell(40, 10, f"Rs. {total_amount:.2f}", align="R")
    
    pdf.output(filepath)
    return filepath
