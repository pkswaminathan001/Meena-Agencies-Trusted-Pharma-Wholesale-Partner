import streamlit as st

def get_user_role():
    """Reads the role from the session state. Defaults to retailer for safety."""
    # In your login logic, you set st.session_state.retailer
    # We'll assume if the ID starts with 'OWNER', they are the owner.
    retailer = st.session_state.get("retailer", {})
    rid = st.session_state.get("retailer_id", "Unknown")
    
    if rid.startswith("OWNER") or retailer.get("role") == "owner":
        return "owner"
    return "retailer"

def filter_menu(menu_items):
    """Filters the sidebar menu based on the user's role."""
    role = get_user_role()
    
    # Pages that ONLY the owner can see
    owner_only_pages = [
        "finance", "adv_finance", "schema", "harness", 
        "jwt", "ragas", "qc", "audit", "pricing", "forecast"
    ]
    
    filtered_menu = []
    for item in menu_items:
        page_key = item[0]
        
        if role == "owner":
            filtered_menu.append(item)
        else:
            # If retailer, only add if it's NOT an owner-only page
            if page_key not in owner_only_pages:
                filtered_menu.append(item)
                
    return filtered_menu
