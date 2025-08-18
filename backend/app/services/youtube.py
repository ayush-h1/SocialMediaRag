import os
import logging
from typing import List, Dict, Any
import requests

log = logging.getLogger(__name__)

YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/search"

def search_youtube(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Best-effort YouTube search. Returns [] on any error (no exceptions).
    """
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        log.info("YOUTUBE_API_KEY not set; returning empty YouTube results.")
        return []

    params = {
        "part": "snippet",
        "type": "video",
        "q": query,
        "maxResults": max_results,
        "key": api_key,
    }
    try:
        r = requests.get(YOUTUBE_API_URL, params=params, timeout=10)
        # If key is invalid/over quota this will be 4xx; treat as empty.
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        log.warning("YouTube search failed: %s", e)
        return []

    items = []
    for it in data.get("items", []):
        vid = (it.get("id") or {}).get("videoId")
        sn = it.get("snippet") or {}
        if not vid:
            continue
        items.append({
            "id": vid,
            "title": sn.get("title"),
            "description": sn.get("description"),
            "channelTitle": sn.get("channelTitle"),
            "publishedAt": sn.get("publishedAt"),
            "thumbnail": ((sn.get("thumbnails") or {}).get("default") or {}).get("url"),
            "url": f"https://www.youtube.com/watch?v={vid}",
        })
    return items
