import os
from typing import Any, Dict, List
import requests

_API = "https://www.googleapis.com/youtube/v3/search"
_API_KEY = os.getenv("YOUTUBE_API_KEY", "").strip()

def search_youtube(q: str, max_results: int = 5) -> List[Dict[str, Any]]:
    # No key? just return []
    if not _API_KEY:
        return []

    try:
        r = requests.get(
            _API,
            params={
                "part": "snippet",
                "type": "video",
                "q": q,
                "maxResults": max_results,
                "key": _API_KEY,
            },
            timeout=12,
        )
        if r.status_code != 200:
            return []
        data = r.json()
    except requests.RequestException:
        return []

    items: List[Dict[str, Any]] = []
    for it in (data or {}).get("items", []):
        vid = (it.get("id") or {}).get("videoId")
        sn = it.get("snippet") or {}
        if not vid:
            continue
        items.append(
            {
                "title": sn.get("title"),
                "description": sn.get("description"),
                "url": f"https://www.youtube.com/watch?v={vid}",
                "channel": sn.get("channelTitle"),
                "published_at": sn.get("publishedAt"),
                "thumbnail": ((sn.get("thumbnails") or {}).get("medium") or {}).get("url"),
                "source": "youtube",
            }
        )
    return items
