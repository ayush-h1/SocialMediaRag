from typing import Any, Dict, List
import requests
import os
import urllib.parse

# Public JSON endpoint; needs a decent UA or it 429s.
_UA = os.getenv("REDDIT_USER_AGENT", "SocialMediaRAG/0.1 by yourusername")
_BASE = "https://www.reddit.com/search.json"

def search_reddit(q: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Anonymous reddit search via the public JSON endpoint.
    Returns [] on any network/HTTP error.
    """
    try:
        r = requests.get(
            _BASE,
            params={"q": q, "sort": "relevance", "t": "year", "limit": max(1, min(limit, 25))},
            headers={"User-Agent": _UA},
            timeout=12,
        )
        if r.status_code != 200:
            return []
        data = r.json()
    except requests.RequestException:
        return []

    items: List[Dict[str, Any]] = []
    for child in ((data or {}).get("data") or {}).get("children", []):
        d = child.get("data") or {}
        permalink = d.get("permalink") or ""
        url = f"https://www.reddit.com{permalink}" if permalink.startswith("/") else (d.get("url") or "")
        items.append(
            {
                "title": d.get("title"),
                "description": d.get("selftext") or "",
                "url": url,
                "subreddit": d.get("subreddit"),
                "score": d.get("score"),
                "num_comments": d.get("num_comments"),
                "source": "reddit",
            }
        )
    return items
