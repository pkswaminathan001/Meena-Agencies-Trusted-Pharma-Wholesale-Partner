import streamlit as st

def apply_design_system():
    st.markdown("""
    <style>
    /* Page 60: Global Design System Tokens */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    :root {
        --primary-regulatory: #0B3C5D; /* Deep Medical Blue */
        --success-approved: #1D8348;   /* Pharma Green */
        --warning-quarantine: #D35400; /* Amber Alert */
        --danger-rejected: #C0392B;    /* Critical Crimson */
        --neutral-dark: #1C2833;       /* Charcoal Black */
        --neutral-light: #F4F6F7;      /* Soft Gray */
    }

    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, sans-serif !important;
    }

    /* Headers */
    h1, h2, h3 {
        color: var(--primary-regulatory) !important;
        font-weight: 700 !important;
    }

    /* Primary Buttons */
    .stButton > button {
        background-color: var(--primary-regulatory) !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
    }
    
    .stButton > button:hover {
        background-color: #092e47 !important;
        color: white !important;
    }

    /* Success/Error/Warning Overrides */
    .stAlert [data-testid="stMarkdownContainer"] {
        color: var(--neutral-dark);
    }
    
    /* Metric Cards */
    [data-testid="stMetricValue"] {
        color: var(--primary-regulatory) !important;
        font-weight: 700 !important;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: var(--neutral-light) !important;
        border-right: 2px solid var(--primary-regulatory) !important;
    }
    
    /* Dataframes */
    .stDataFrame {
        border: 1px solid var(--neutral-light);
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)
