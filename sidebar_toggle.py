import streamlit as st

def apply():
    try:
        import streamlit.components.v1 as components
        components.html("""
        <style>
        #ma-sb-toggle {
             top: 12px; left: 12px;
            z-index: 2147483647;
            width: 46px; height: 46px;
            border: none; border-radius: 12px;
            background: linear-gradient(135deg, #4f46e5, #7b61ff);
            color: #fff; font-size: 22px; font-weight: 900;
            cursor: pointer;
            box-shadow: 0 6px 18px rgba(79,70,229,0.45);
            display: flex; align-items: center; justify-content: center;
        }
        #ma-sb-toggle:hover { transform: scale(1.08); }
        section[data-testid="stSidebar"] {
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        @media (max-width: 768px) {
            section[data-testid="stSidebar"] {
                
                top: 0 !important; left: 0 !important;
                height: 100vh !important;
                width: 78vw !important;
                max-width: 300px !important;
                z-index: 999998 !important;
                box-shadow: 4px 0 24px rgba(0,0,0,0.25) !important;
            }
            section[data-testid="stSidebar"][aria-expanded="false"] {
                transform: translateX(-100%) !important;
            }
        }
        </style>
        <script>
        (function(){
            var pdoc = window.parent.document;
            function isOpen() {
                var sb = pdoc.querySelector('section[data-testid="stSidebar"]');
                if (!sb) return false;
                return sb.getAttribute('aria-expanded') !== 'false';
            }
            function nativeToggle() {
                var t = pdoc.querySelector(
                    '[data-testid="stSidebarCollapseButton"] button, ' +
                    '[data-testid="stSidebarCollapsedControl"] button, ' +
                    '[data-testid="collapsedControl"] button'
                );
                if (t) { t.click(); return true; }
                return false;
            }
            function manualToggle() {
                var sb = pdoc.querySelector('section[data-testid="stSidebar"]');
                if (!sb) return;
                sb.setAttribute('aria-expanded', isOpen() ? 'false' : 'true');
            }
            function makeBtn() {
                if (pdoc.getElementById('ma-sb-toggle')) return;
                var b = pdoc.createElement('button');
                b.id = 'ma-sb-toggle';
                b.type = 'button';
                b.innerHTML = '☰';
                b.onclick = function(){
                    if (!nativeToggle()) manualToggle();
                };
                pdoc.body.appendChild(b);
            }
            function boot() {
                if (!pdoc || !pdoc.body) { setTimeout(boot, 200); return; }
                makeBtn();
                try { new MutationObserver(makeBtn).observe(pdoc.body, {childList:true, subtree:true}); } catch(e) {}
            }
            boot();
        })();
        </script>
        """, height=0, width=0)
    except Exception as e:
        print("sidebar_toggle skipped:", e)

try:
    apply()
except Exception:
    pass
