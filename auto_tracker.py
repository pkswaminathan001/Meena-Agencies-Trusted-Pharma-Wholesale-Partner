"""Auto break detection — browser visibility + idle tracking via JS bridge"""
import streamlit.components.v1 as components

def inject_tracker(worker_id, backend_url="http://localhost:8765"):
    """Inject JS that pings backend on visibility/idle changes."""
    js = f"""
    <script>
    (function() {{
        const worker = "{worker_id}";
        const pingUrl = "{backend_url}/_stcore/health";  // lightweight ping
        
        // Detect visibility change (Windows+L, minimize, alt-tab)
        let hiddenSince = null;
        document.addEventListener('visibilitychange', function() {{
            if (document.hidden) {{
                hiddenSince = Date.now();
                fetch(pingUrl + '?event=hidden&worker=' + worker, {{mode:'no-cors'}}).catch(()=>{{}});
            }} else if (hiddenSince) {{
                const duration = Math.floor((Date.now() - hiddenSince) / 1000 / 60);
                fetch(pingUrl + '?event=visible&worker=' + worker + '&dur=' + duration, {{mode:'no-cors'}}).catch(()=>{{}});
                hiddenSince = null;
            }}
        }});

        // Detect idle (no keyboard/mouse for 5 min)
        let idleTimer = null;
        function resetIdle() {{
            if (idleTimer) clearTimeout(idleTimer);
            idleTimer = setTimeout(function() {{
                fetch(pingUrl + '?event=idle&worker=' + worker, {{mode:'no-cors'}}).catch(()=>{{}});
            }}, 5 * 60 * 1000);
        }}
        ['mousemove','keydown','click','scroll','touchstart'].forEach(function(evt) {{
            document.addEventListener(evt, resetIdle, {{passive: true}});
        }});
        resetIdle();
    }})();
    </script>
    """
    components.html(js, height=0)
