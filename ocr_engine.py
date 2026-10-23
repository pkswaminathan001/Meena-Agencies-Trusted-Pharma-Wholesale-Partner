import streamlit as st
import pandas as pd
import difflib
import os
import json
import time
import random

def extract_text_from_image(file):
    """Simulates an OCR/Vision model extracting text from an image."""
    # In production, this connects to GPT-4o Vision or Tesseract.
    # Here, we return a mock extraction to demonstrate the pipeline.
    mock_extractions = [
        "Dolo 650 - 10 boxes\nAmoxicilin 500 - 5 boxes\nORS powder - 20",
        "Paracetamol 500 - 15\nInsulin Glargine - 2\nDolo650 - 5",
        "Amoxy 500 - 10\nORS - 50\nParacetamol - 10"
    ]
    return random.choice(mock_extractions)

def match_sku(extracted_text, inventory_df):
    """Fuzzy matches extracted text to inventory SKUs."""
    skus = inventory_df["SKU"].tolist()
    matches = []
    
    lines = extracted_text.strip().split("\n")
    for line in lines:
        if not line.strip(): continue
        
        # Simple parsing: split by ' - ' or just look for the drug name
        parts = line.split(" - ")
        raw_name = parts[0].strip()
        try:
            qty = int(''.join(filter(str.isdigit, parts[1]))) if len(parts) > 1 else 1
        except:
            qty = 1
            
        # Fuzzy match against real SKUs
        close_matches = difflib.get_close_matches(raw_name, skus, n=1, cutoff=0.4)
        
        if close_matches:
            matched_sku = close_matches[0]
            # Calculate confidence (0 to 100)
            confidence = round(difflib.SequenceMatcher(None, raw_name.lower(), matched_sku.lower()).ratio() * 100, 1)
            matches.append({
                "Extracted Text": raw_name,
                "Matched SKU": matched_sku,
                "Quantity": qty,
                "Confidence (%)": confidence,
                "Status": "✅ High" if confidence > 80 else "⚠️ Needs Review"
            })
        else:
            matches.append({
                "Extracted Text": raw_name,
                "Matched SKU": "UNKNOWN",
                "Quantity": qty,
                "Confidence (%)": 0.0,
                "Status": "❌ Not Found"
            })
            
    return matches

def render_ocr_intake():
    st.markdown("## 📸 AI Vision Order Intake")
    st.caption("Upload a photo of a handwritten order. The AI extracts items and matches them to your catalog.")

    inventory_path = "inventory.csv"
    if not os.path.exists(inventory_path):
        st.error("inventory.csv not found. Please go to Expiry Engine first to generate it.")
        return

    inventory_df = pd.read_csv(inventory_path)

    uploaded_file = st.file_uploader("Upload Order Image (JPG/PNG) or Text File", type=["jpg", "png", "jpeg", "txt"])

    if uploaded_file is not None:
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        
        if st.button("🤖 Run AI Extraction & Matching", type="primary", use_container_width=True):
            with st.spinner("Scanning image, running OCR, and fuzzy-matching SKUs..."):
                time.sleep(1.5) # Simulate processing time
                
                # Extract text
                if uploaded_file.name.endswith(".txt"):
                    extracted_text = uploaded_file.read().decode("utf-8")
                else:
                    extracted_text = extract_text_from_image(uploaded_file)

                st.markdown("### 📝 Extracted Text")
                st.info(extracted_text)

                # Match SKUs
                st.markdown("### 🔍 SKU Matching Engine")
                matches = match_sku(extracted_text, inventory_df)
                match_df = pd.DataFrame(matches)

                st.dataframe(match_df, use_container_width=True, hide_index=True)

                # Flag low confidence
                needs_review = match_df[match_df["Confidence (%)"] < 80]
                if not needs_review.empty:
                    st.warning(f"⚠️ {len(needs_review)} item(s) need manual review before generating the draft.")

                # Generate Draft
                if st.button("✅ Approve & Create Draft Order", use_container_width=True):
                    # Create draft
                    draft = {
                        "draft_id": f"DRF-{random.randint(1000, 9999)}",
                        "date": str(pd.Timestamp.now()),
                        "retailer_id": st.session_state.get("retailer_id", "Unknown"),
                        "items": match_df.to_dict("records"),
                        "status": "Draft"
                    }
                    
                    # Save to orders.json
                    orders = []
                    if os.path.exists("orders.json"):
                        with open("orders.json", "r") as f:
                            orders = json.load(f)
                    orders.append(draft)
                    with open("orders.json", "w") as f:
                        json.dump(orders, f, indent=2)

                    st.success(f"🎉 Draft Order {draft['draft_id']} created successfully!")
                    st.balloons()
                    st.info("The draft is now awaiting owner approval in the 'Track Orders' section.")
