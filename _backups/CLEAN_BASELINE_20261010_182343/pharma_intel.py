"""
pharma_intel.py v3 — FAST live intel feed.
- First import: fetches once synchronously (3-5s one-time cost)
- After that: instant from cache, refreshes in background
- Never blocks page render after first load
"""
import json, random, re, threading
from datetime import datetime, timedelta
from pathlib import Path

try:
    import feedparser
    HAS_FEEDPARSER = True
except ImportError:
    HAS_FEEDPARSER = False

try:
    import streamlit as st
    HAS_ST = True
except ImportError:
    HAS_ST = False


CACHE_FILE = Path("pharma_intel_cache.json")
SEEN_FILE = Path("pharma_intel_seen.json")
CACHE_TTL_MINUTES = 60
MAX_SEEN = 400

FEEDS = [
    {"url": "https://www.expresspharma.in/feed/",
     "tag": "📊 Market Policy", "source": "Express Pharma"},
    {"url": "https://news.google.com/rss/search?q=pharma+India&hl=en-IN&gl=IN&ceid=IN:en",
     "tag": "📊 Market Policy", "source": "Google News"},
    {"url": "https://news.google.com/rss/search?q=AI+pharma+supply+chain&hl=en-IN&gl=IN&ceid=IN:en",
     "tag": "🤖 AI & Tech", "source": "Google News"},
]

_MEM_ITEMS = []
_MEM_FETCHED_AT = None
_FETCH_LOCK = threading.Lock()


def _load_json(path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def _save_json(path, data):
    try:
        path.write_text(json.dumps(data, indent=2))
    except Exception:
        pass


def _clean(raw):
    if not raw:
        return ""
    t = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", t).strip()


def _fetch_one(feed_cfg):
    if not HAS_FEEDPARSER:
        return []
    try:
        feed = feedparser.parse(feed_cfg["url"])
        out = []
        for e in feed.entries[:10]:
            t = _clean(e.get("title", ""))
            if not t or len(t) < 15:
                continue
            out.append({
                "title": t,
                "content": _clean(e.get("summary", ""))[:300],
                "link": e.get("link", ""),
                "tag": feed_cfg["tag"],
                "source": feed_cfg["source"],
            })
        return out
    except Exception:
        return []


def _fetch_all():
    items = []
    for cfg in FEEDS:
        items.extend(_fetch_one(cfg))
    seen = set()
    uniq = []
    for it in items:
        k = it["title"].lower()[:80]
        if k in seen:
            continue
        seen.add(k)
        uniq.append(it)
    return uniq


def _cache_is_fresh():
    cache = _load_json(CACHE_FILE, {})
    fa = cache.get("fetched_at")
    if not fa:
        return False
    try:
        return datetime.now() - datetime.fromisoformat(fa) < timedelta(minutes=CACHE_TTL_MINUTES)
    except Exception:
        return False


def _load_cache_into_memory():
    """Load cache from disk into memory. Fast, always safe."""
    global _MEM_ITEMS, _MEM_FETCHED_AT
    cache = _load_json(CACHE_FILE, {})
    if cache.get("items"):
        _MEM_ITEMS = cache["items"]
        try:
            _MEM_FETCHED_AT = datetime.fromisoformat(cache.get("fetched_at", ""))
        except Exception:
            _MEM_FETCHED_AT = None


def _background_refresh():
    """Fetch feeds in background. Updates memory + disk. Never blocks."""
    global _MEM_ITEMS, _MEM_FETCHED_AT
    with _FETCH_LOCK:
        items = _fetch_all()
        if items:
            _MEM_ITEMS = items
            _MEM_FETCHED_AT = datetime.now()
            _save_json(CACHE_FILE, {
                "fetched_at": _MEM_FETCHED_AT.isoformat(),
                "items": items,
            })


def _synchronous_first_fetch():
    """Do the initial fetch synchronously — used only once when cache is empty."""
    global _MEM_ITEMS, _MEM_FETCHED_AT
    items = _fetch_all()
    if items:
        _MEM_ITEMS = items
        _MEM_FETCHED_AT = datetime.now()
        _save_json(CACHE_FILE, {
            "fetched_at": _MEM_FETCHED_AT.isoformat(),
            "items": items,
        })
    return len(items)


# ═══════════════════════════════════════════════════════════
# INIT — runs once when module first imported
# ═══════════════════════════════════════════════════════════
def _initialize():
    _load_cache_into_memory()
    if _MEM_ITEMS:
        # We have something. If stale, refresh in background.
        if not _cache_is_fresh():
            threading.Thread(target=_background_refresh, daemon=True).start()
    else:
        # No cache at all — must fetch synchronously so UI has data
        print("[pharma_intel] First run — fetching feeds now (one-time ~4s)…")
        n = _synchronous_first_fetch()
        print(f"[pharma_intel] Fetched {n} items. Cache written.")


_initialize()


def _pick_unseen():
    if not _MEM_ITEMS:
        return None
    seen = set(_load_json(SEEN_FILE, []))
    unseen = [it for it in _MEM_ITEMS if it["title"].lower()[:80] not in seen]
    if not unseen:
        _save_json(SEEN_FILE, [])
        unseen = _MEM_ITEMS
    pick = random.choice(unseen)
    k = pick["title"].lower()[:80]
    seen_list = list(seen)
    seen_list.append(k)
    if len(seen_list) > MAX_SEEN:
        seen_list = seen_list[-MAX_SEEN:]
    _save_json(SEEN_FILE, seen_list)
    return pick


def get_intel_css() -> str:
    return """
    <style>
    .corp-intel-card {
        background: linear-gradient(135deg, rgba(14,29,74,0.95) 0%, rgba(26,42,85,0.95) 100%);
        border-left: 4px solid #00d4ff;
        border-radius: 14px;
        padding: 20px 22px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.35), 0 0 0 1px rgba(0,212,255,0.18) inset;
        color: #e8eaf6;
        font-family: Inter, -apple-system, sans-serif;
        max-width: 460px;
        margin-left: auto;
    }
    .corp-intel-tag {
        font-size: 0.72rem; font-weight: 700; color: #00d4ff;
        letter-spacing: 1.4px; text-transform: uppercase; margin-bottom: 10px;
    }
    .corp-intel-title {
        font-size: 1.05rem; font-weight: 700; color: #ffffff;
        margin: 0 0 8px 0; line-height: 1.28;
    }
    .corp-intel-body {
        font-size: 0.85rem; line-height: 1.55; color: #b8c0d8;
        margin: 0; max-height: 130px; overflow: hidden;
    }
    .corp-intel-foot {
        font-size: 0.72rem; color: #8892b0; margin-top: 12px; overflow: hidden;
    }
    .corp-intel-foot a:hover { color: #7b61ff !important; }
    </style>
    """


def _fallback(msg):
    return f"""
    <div class="corp-intel-card">
        <div class="corp-intel-tag">📰 Pharma Intel</div>
        <div class="corp-intel-title">Loading…</div>
        <div class="corp-intel-body">{msg}</div>
        <div class="corp-intel-foot">{datetime.now().strftime('%d %b · %H:%M')}</div>
    </div>
    """


def get_intel_html() -> str:
    if not _MEM_ITEMS:
        return _fallback("Fetching live updates… refresh in a moment.")
    pick = _pick_unseen()
    if not pick:
        return _fallback("No updates available.")
    content = pick["content"] or "Click below to read the full article."
    return f"""
    <div class="corp-intel-card">
        <div class="corp-intel-tag">{pick['tag']} · {pick['source']}</div>
        <div class="corp-intel-title">{pick['title']}</div>
        <div class="corp-intel-body">{content}</div>
        <div class="corp-intel-foot">
            <a href="{pick['link']}" target="_blank" style="color:#00d4ff;text-decoration:none;">Read more →</a>
            <span style="float:right;">{datetime.now().strftime('%d %b · %H:%M')}</span>
        </div>
    </div>
    """


def render_intel_card():
    if HAS_ST:
        st.markdown(get_intel_css() + get_intel_html(), unsafe_allow_html=True)


def force_refresh():
    """Call manually if you want to refetch feeds now."""
    return _synchronous_first_fetch()


if __name__ == "__main__":
    print("=== pharma_intel.py self-test ===")
    print(f"feedparser: {HAS_FEEDPARSER}")
    print(f"Cached items in memory: {len(_MEM_ITEMS)}")
    if not _MEM_ITEMS:
        print("Fetching...")
        n = _synchronous_first_fetch()
        print(f"Fetched: {n}")
    for it in _MEM_ITEMS[:5]:
        print(f"  [{it['tag']}] {it['title'][:70]}")
