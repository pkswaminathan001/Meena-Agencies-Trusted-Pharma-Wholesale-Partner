"""animations_v2.py — Phase 1 UI polish."""
import streamlit as st

def inject_css():
    if st.session_state.get("_anim_v2_done"):
        return
    st.markdown("""
    <style>
    @keyframes animFadeUp {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    div[data-testid="stVerticalBlock"] > div {
        animation: animFadeUp .35s ease-out;
    }
    [data-testid="stMetric"] {
        transition: transform .18s ease, box-shadow .18s ease;
        border-radius: 12px !important;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 28px rgba(0,212,170,0.22);
    }
    .stButton > button,
    .stDownloadButton > button,
    .stFormSubmitButton > button {
        transition: transform .15s ease, box-shadow .15s ease, filter .15s ease !important;
    }
    .stButton > button:hover,
    .stDownloadButton > button:hover,
    .stFormSubmitButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 22px rgba(0,212,170,0.35);
        filter: brightness(1.08);
    }
    button[data-baseweb="tab"] {
        transition: color .18s ease, transform .18s ease !important;
    }
    button[data-baseweb="tab"]:hover { transform: translateY(-1px); }
    [data-testid="stExpander"] {
        transition: border-color .18s ease, box-shadow .18s ease !important;
    }
    [data-testid="stExpander"]:hover {
        border-color: rgba(0,212,170,0.35) !important;
        box-shadow: 0 4px 14px rgba(0,212,170,0.12);
    }
    .js-plotly-plot { animation: animFadeUp .45s ease-out; }
    [data-testid="stDataFrame"] { animation: animFadeUp .4s ease-out; }
    [data-testid="stAlert"] { animation: animFadeUp .3s ease-out; }
    @keyframes animPulseBell {
        0%,100% { transform: scale(1);   box-shadow: 0 0 0 0 rgba(255,77,109,0.7); }
        50%     { transform: scale(1.08); box-shadow: 0 0 0 8px rgba(255,77,109,0); }
    }
    .ma-bell-badge { animation: animPulseBell 1.6s ease-in-out infinite !important; }
    div[data-testid="stVerticalBlock"] > div:nth-child(1) { animation-delay: .02s; }
    div[data-testid="stVerticalBlock"] > div:nth-child(2) { animation-delay: .06s; }
    div[data-testid="stVerticalBlock"] > div:nth-child(3) { animation-delay: .10s; }
    div[data-testid="stVerticalBlock"] > div:nth-child(4) { animation-delay: .14s; }
    div[data-testid="stVerticalBlock"] > div:nth-child(5) { animation-delay: .18s; }
    @media (prefers-reduced-motion: reduce) {
        * { animation: none !important; transition: none !important; }
    }
    </style>
    """, unsafe_allow_html=True)
    st.session_state["_anim_v2_done"] = True

def inject_countup_kpis():
    if st.session_state.get("_anim_countup_done"):
        return
    st.markdown("""
    <script>
    (function () {
        function ready(fn) {
            if (document.readyState !== 'loading') fn();
            else document.addEventListener('DOMContentLoaded', fn);
        }
        ready(function () {
            var done = new WeakSet();
            function countup(el) {
                var text = el.textContent.trim();
                var m = text.match(/^([^0-9\\-]*)([-0-9,\\.]+)(.*)$/);
                if (!m) return;
                var prefix = m[1], numStr = m[2].replace(/,/g,''), suffix = m[3];
                var target = parseFloat(numStr);
                if (isNaN(target)) return;
                var isInt = (target % 1 === 0);
                var t0 = performance.now();
                function step(t) {
                    var p = Math.min(1, (t - t0) / 700);
                    var eased = 1 - Math.pow(1 - p, 3);
                    var val = target * eased;
                    el.textContent = prefix + (isInt ? Math.round(val).toLocaleString('en-IN') : val.toFixed(2)) + suffix;
                    if (p < 1) requestAnimationFrame(step);
                }
                requestAnimationFrame(step);
            }
            function scan() {
                document.querySelectorAll('[data-testid="stMetricValue"]').forEach(function (el) {
                    if (done.has(el)) return;
                    done.add(el);
                    countup(el);
                });
            }
            scan();
            setInterval(scan, 400);
        });
    })();
    </script>
    """, unsafe_allow_html=True)
    st.session_state["_anim_countup_done"] = True

def apply():
    inject_css()
    inject_countup_kpis()
