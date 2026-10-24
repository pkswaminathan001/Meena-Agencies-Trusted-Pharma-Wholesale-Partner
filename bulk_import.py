import streamlit as st
import pandas as pd
import json
import hashlib
from pathlib import Path

def render_bulk_import():
    st.title("📥 Bulk Import Customers")
    st.caption("Upload a CSV/Excel file to register 1,000+ customers instantly.")
    
    st.info("Your file must have these columns exactly: `Retailer ID`, `Shop Name`, `Owner Name`, `Phone`, `PIN`, `Role`")
    
    uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
                
            st.write("### Data Preview")
            st.dataframe(df, use_container_width=True)
            
            if st.button("🚀 Import All Customers", type="primary"):
                # Load existing data
                rj_path = Path("retailers.json")
                if rj_path.exists():
                    with open(rj_path, "r") as f:
                        existing = json.load(f)
                else:
                    existing = []
                    
                existing_ids = {u["id"] for u in existing}
                
                added_count = 0
                for index, row in df.iterrows():
                    rid = str(row["Retailer ID"]).strip().upper()
                    if rid in existing_ids:
                        continue # Skip duplicates
                        
                    new_user = {
                        "id": rid,
                        "shop": str(row["Shop Name"]),
                        "owner": str(row["Owner Name"]),
                        "phone": str(row["Phone"]),
                        "pin": str(row["PIN"]),
                        "pin_hash": hashlib.sha256(str(row["PIN"]).encode()).hexdigest(),
                        "role": str(row["Role"]).lower(),
                        "telegram_chat_id": "", # Will be auto-filled later
                        "status": "Active",
                        "outstanding": 0
                    }
                    existing.append(new_user)
                    added_count += 1
                    
                with open(rj_path, "w") as f:
                    json.dump(existing, f, indent=2)
                    
                st.success(f"✅ Successfully imported {added_count} new customers! Total users: {len(existing)}")
                st.rerun()
                
        except Exception as e:
            st.error(f"Error reading file: {e}")
