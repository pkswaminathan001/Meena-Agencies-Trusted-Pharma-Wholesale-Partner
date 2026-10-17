"""
retailer_menu.py — Left-side hamburger menu (☰) with profile,
navigation, and Sign Out. Uses st.popover for a floating panel.
No extra install required (works on Streamlit >= 1.37).
"""
import streamlit as st



def _inject_position_css_via_js():
    """Fallback: inject CSS directly into the browser's parent document,
    bypassing Streamlit's CSS scoping. Only needed if st.markdown CSS fails."""
    import streamlit.components.v1 as _components
    _components.html(
        """
        <script>
        (function() {
            const doc = window.parent.document;
            const css = `
                div[data-testid="stPopover"],
                div[data-testid="stPopover"] > div,
                .stPopover,
                div[class*="stPopover"] {
                    
                    top: 45vh !important;
                    left: 0 !important;
                    z-index: 2147483647 !important;
                    transform: none !important;
                }
                div[data-testid="stPopover"] > button {
                    background: rgba(11,59,140,0.85) !important;
                    backdrop-filter: blur(10px) !important;
                    color: #FFFFFF !important;
                    border: none !important;
                    border-radius: 0 10px 10px 0 !important;
                    padding: 12px 10px 12px 12px !important;
                    font-size: 17px !important;
                    font-weight: 900 !important;
                    box-shadow: 3px 4px 14px rgba(11,59,140,.28) !important;
                    opacity: 0.78 !important;
                    min-width: 40px !important;
                    min-height: 40px !important;
                }
                div[data-testid="stPopover"] > button:hover {
                    background: #0B3B8C !important;
                    opacity: 1 !important;
                }
                div[data-testid="stPopoverBody"],
                div[data-testid="stPopoverBodyNoArrow"] {
                    
                    top: 45vh !important;
                    left: 56px !important;
                    z-index: 2147483646 !important;
                    transform: translateY(-50%) !important;
                }
            `;
            let styleEl = doc.getElementById('hm-fixed-pos');
            if (!styleEl) {
                styleEl = doc.createElement('style');
                styleEl.id = 'hm-fixed-pos';
                doc.head.appendChild(styleEl);
            }
            styleEl.textContent = css;
        })();
        </script>
        """,
        height=0,
        width=0,
    )





def render_hamburger(retailer=None, on_signout=None, on_nav=None):
    """
    Renders a floating ☰ button top-left.
    Opens a popover with profile + nav + Sign Out.

    Args:
        retailer: dict with owner, shop, id (or None for owner mode)
        on_signout: callable, invoked when Sign Out is clicked
        on_nav: callable(page_key), invoked when a nav item is clicked
    Returns:
        selected page key (str) or None
    """
    _inject_position_css_via_js()
    selected = None

    # The floating ☰ container
    st.markdown(
        """
        <style>
        /* ══════════════════════════════════════════════════════
           FLOATING HAMBURGER — pinned to left edge, mid-height.
           Forces fixed positioning on popover AND its ancestors.
           ══════════════════════════════════════════════════════ */

        /* Kill Streamlit's own top header + sidebar toggle completely */
        header[data-testid="stHeader"] { display: none !important; }
        button[data-testid="stBaseButton-headerNoPadding"],
        button[kind="header"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="collapsedControl"] {
            display: none !important;
        }

        /* ── Target the popover AND every wrapper the framework puts around it ── */
        div[data-testid="stPopover"],
        div[data-testid="stPopover"] > div,
        div[data-testid="stPopover"] > div > div,
        .stPopover,
        div[class*="stPopover"] {
            
            top: 45vh !important;
            left: 0 !important;
            z-index: 2147483647 !important;
            transform: none !important;
            margin: 0 !important;
            padding: 0 !important;
            background: transparent !important;
            width: auto !important;
            max-width: none !important;
        }

        /* The trigger button itself */
        div[data-testid="stPopover"] > button,
        div[data-testid="stPopover"] button[kind="secondary"],
        div[data-testid="stPopover"] button {
            background: rgba(11, 59, 140, 0.85) !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 0 10px 10px 0 !important;
            padding: 12px 10px 12px 12px !important;
            font-size: 17px !important;
            font-weight: 900 !important;
            line-height: 1 !important;
            box-shadow: 3px 4px 14px rgba(11,59,140,.28) !important;
            transition: all .22s ease !important;
            opacity: 0.78 !important;
            min-width: 40px !important;
            min-height: 40px !important;
            margin: 0 !important;
        }
        div[data-testid="stPopover"] > button:hover,
        div[data-testid="stPopover"] button:hover {
            background: #0B3B8C !important;
            opacity: 1 !important;
            padding-right: 14px !important;
            box-shadow: 4px 6px 22px rgba(11,59,140,.40) !important;
        }
        div[data-testid="stPopover"] > button:focus {
            outline: none !important;
            box-shadow: 4px 6px 22px rgba(11,59,140,.40) !important;
        }

        /* ── Panel content — opens beside the button ── */
        div[data-testid="stPopoverBody"],
        div[data-testid="stPopoverBodyNoArrow"],
        div[data-baseweb="popover"] {
            
            top: 45vh !important;
            left: 56px !important;
            z-index: 2147483646 !important;
            background: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 14px !important;
            box-shadow: 0 20px 50px rgba(11,59,140,.22) !important;
            padding: 16px !important;
            min-width: 260px !important;
            max-width: 300px !important;
            max-height: 80vh !important;
            overflow-y: auto !important;
            transform: translateY(-50%) !important;
            animation: slideInLeft .25s cubic-bezier(.2,.9,.3,1.2) !important;
        }
        @keyframes slideInLeft {
            from { opacity: 0; transform: translate(-20px, -50%); }
            to   { opacity: 1; transform: translate(0, -50%); }
        }

        div[data-testid="stPopoverBody"] *,
        div[data-testid="stPopoverBodyNoArrow"] * {
            color: #1A1A2E !important;
        }

        /* Profile card */
        .hm-profile {
            background: linear-gradient(120deg, #072A66 0%, #0B3B8C 40%, #1560BD 100%) !important;
            border-radius: 12px !important;
            padding: 14px 16px !important;
            margin-bottom: 12px !important;
        }
        .hm-profile * { color: #FFFFFF !important; }
        .hm-profile .who {
            font-size: 15px !important;
            font-weight: 800 !important;
            letter-spacing: -.2px !important;
            margin-bottom: 2px !important;
        }
        .hm-profile .what {
            font-size: 12px !important;
            font-weight: 500 !important;
            opacity: .9 !important;
        }
        .hm-profile .tag {
            display: inline-block !important;
            background: rgba(255,255,255,.18) !important;
            font-size: 10px !important;
            font-weight: 700 !important;
            letter-spacing: 1px !important;
            text-transform: uppercase !important;
            padding: 3px 10px !important;
            border-radius: 999px !important;
            margin-bottom: 6px !important;
        }

        .hm-label {
            color: #64748B !important;
            font-size: 11px !important;
            font-weight: 800 !important;
            letter-spacing: 1.2px !important;
            text-transform: uppercase !important;
            margin: 12px 4px 6px 4px !important;
        }

        /* Menu buttons */
        div[data-testid="stPopoverBody"] .stButton > button,
        div[data-testid="stPopoverBodyNoArrow"] .stButton > button {
            width: 100% !important;
            text-align: left !important;
            justify-content: flex-start !important;
            background: transparent !important;
            color: #1A1A2E !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 12px !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            margin-bottom: 2px !important;
            box-shadow: none !important;
        }
        div[data-testid="stPopoverBody"] .stButton > button:hover,
        div[data-testid="stPopoverBodyNoArrow"] .stButton > button:hover {
            background: #E8EFFB !important;
            color: #0B3B8C !important;
        }

        .signout-btn button {
            background: #FDE8E8 !important;
            color: #C81E1E !important;
            font-weight: 800 !important;
        }
        .signout-btn button:hover {
            background: #C81E1E !important;
            color: #FFFFFF !important;
        }

        /* Mobile — thumb height */
        @media (max-width: 768px) {
            div[data-testid="stPopover"],
            div[data-testid="stPopover"] > div,
            div[data-testid="stPopover"] > div > div {
                top: 55vh !important;
            }
            div[data-testid="stPopover"] > button {
                padding: 11px 9px 11px 11px !important;
                font-size: 16px !important;
                min-width: 38px !important;
                min-height: 38px !important;
                opacity: 0.82 !important;
            }
            div[data-testid="stPopoverBody"],
            div[data-testid="stPopoverBodyNoArrow"] {
                top: 55vh !important;
                left: 50px !important;
                min-width: 240px !important;
                max-width: calc(100vw - 60px) !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.popover("☰", help="Menu"):
        # Profile card
        if retailer:
            st.markdown(
                f"""
                <div class="hm-profile">
                  <div class="tag">Retailer · {retailer.get('id','—')}</div>
                  <div class="who">{retailer.get('owner','—')}</div>
                  <div class="what">{retailer.get('shop','—')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Navigation
        st.markdown('<div class="hm-label">Navigate</div>', unsafe_allow_html=True)
        if st.button("🏠  Home",       key="hm_home",     use_container_width=True):
            selected = "home"
        if st.button("🛒  Place Order", key="hm_order",    use_container_width=True):
            selected = "order"
        if st.button("📦  My Orders",   key="hm_orders",   use_container_width=True):
            selected = "orders"
        if st.button("🧾  Bills",       key="hm_bills",    use_container_width=True):
            selected = "bills"
        if st.button("📄  Statement",   key="hm_stmt",     use_container_width=True):
            selected = "statement"

        # Account
        st.markdown('<div class="hm-label">Account</div>', unsafe_allow_html=True)
        if st.button("🔑  Change PIN",       key="hm_pin",     use_container_width=True):
            selected = "change_pin"
        if st.button("📞  Update Contact",    key="hm_contact", use_container_width=True):
            selected = "update_contact"

        # Sign Out at the bottom, styled red
        st.markdown('<div class="signout-btn">', unsafe_allow_html=True)
        if st.button("🚪  Sign Out", key="hm_signout", use_container_width=True):
            if on_signout:
                on_signout()
        st.markdown('</div>', unsafe_allow_html=True)

    if selected and on_nav:
        on_nav(selected)
    return selected
