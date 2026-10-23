import streamlit as st
import streamlit.components.v1 as components

def inject_pwa():
    """Injects the PWA manifest and service worker registration."""
    # Note: Streamlit Cloud might block service workers from root,
    # but the Manifest injection allows "Add to Home Screen" on mobile.
    
    pwa_html = """
    <script>
    // 1. Inject Manifest
    var link = document.createElement('link');
    link.rel = 'manifest';
    link.href = window.location.origin + '/manifest.json';
    document.head.appendChild(link);

    // 2. Add Meta Tags for Mobile
    var metaTheme = document.createElement('meta');
    metaTheme.name = 'theme-color';
    metaTheme.content = '#0B3C5D';
    document.head.appendChild(metaTheme);

    var metaApple = document.createElement('meta');
    metaApple.name = 'apple-mobile-web-app-capable';
    metaApple.content = 'yes';
    document.head.appendChild(metaApple);
    </script>
    """
    components.html(pwa_html, height=0, width=0)
