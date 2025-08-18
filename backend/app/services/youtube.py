from __future__ import annotations

import os
from typing import Dict, List

import requests

_YT_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"


def search_youtube(query: str, max_results: int = 5) -> List[Dict]:
    """
    Lightweight YouTube search.
    - If YOUTUBE_API_KEY is missing OR Google returns 4xx/5xx, we return [] instead of raising.
    - This keeps your API responsive even when the key is restricted/invalid.

    Returns a list of normalized items:
      {
        "id": "...", "title": "...", "description": "...", "channel": "...",
        "publishedAt": "...", "url": "https://www.youtube.com/watch?v=...", "thumbnail": "...",
        "source": "youtube"
      }
    """
    key = os.getenv("YOUTUBE_API_KEY")
    if not key:
        print("[youtube] YOUTUBE_API_KEY not set; skipping YouTube.")
        return []

    params = {
        "part": "snippet",
        "type": "video",
        "q": query,
        "maxResults": max(1, min(int(max_results or 5), 25)),
        "key": key,
    }

    try:
        r = requests.get(_YT_SEARCH_URL, params=params, timeout=10)
        if r.status_code == 403:
            # Most common cause in Render: API key restricted by HTTP referrer or IP.
            print("[youtube] 403 Forbidden. Check API key restrictions in Google Cloud → Credentials.")
            return []
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as exc:
        print(f"[youtube] request failed: {exc}")
        return []

    items: List[Dict] = []
    for obj in data.get("items", []):
        vid = ((obj or {}).get("id") or {}).get("videoId")
        snip = (obj or {}).get("snippet") or {}
        if not vid:
            continue
        thumbs = (snip.get("thumbnails") or {})
        thumb = (thumbs.get("medium") or thumbs.get("default") or {}).get("url")
        items.append(
            {
                "id": vid,
                "title": snip.get("title"),
                "description": snip.get("description"),
                "channel": snip.get("channelTitle"),
                "publishedAt": snip.get("publishedAt"),
                "url": f"https://www.youtube.com/watch?v={vid}",
                "thumbnail": thumb,
                "source": "youtube",
            }
        )
    return items
