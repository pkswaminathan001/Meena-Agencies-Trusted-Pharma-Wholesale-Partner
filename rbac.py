def get_security_mode(company=None):
    """Fallback security mode function."""
    return "standard"

import streamlit as st

def get_user_role():
    retailer = st.session_state.get("retailer", {})
    rid = st.session_state.get("retailer_id", "Unknown")
    
    if rid.startswith("OWNER") or retailer.get("role") == "owner":
        return "owner"
    return "retailer"

def filter_menu(menu_items):
    role = get_user_role()
    
    # Owner sees EVERYTHING
    if role == "owner":
        return menu_items

    # Retailer ONLY sees these specific pages
    allowed_for_retailer = [
        "home", 
        "order", 
        "cart", 
        "track_orders", 
        "stock", 
        "ledger", 
        "contact", 
        "profile"
    ]

    filtered_menu = []
    for item in menu_items:
        if item[0] in allowed_for_retailer:
            filtered_menu.append(item)
            
    return filtered_menu

    def get_security_mode(company=None):
        """Fallback security mode function."""
        return "standard"
