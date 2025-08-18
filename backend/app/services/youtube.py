import os
import requests

YOUTUBE_API_KEY = os.getenv("AIzaSyAIpEAAsNPUMBTSNoCgmMGr6tnKt1nRuj0", "")

def search_youtube(q: str, max_results: int = 5):
    """
    Returns a list of videos. If API key is missing/invalid, returns [] and logs a warning.
    """
    if not YOUTUBE_API_KEY:
        # No key configured – quietly skip
        return []

    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "type": "video",
        "q": q,
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY,
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        out = []
        for it in data.get("items", []):
            vid = (it.get("id") or {}).get("videoId")
            sn = it.get("snippet") or {}
            if not vid:
                continue
            out.append({
                "id": vid,
                "title": sn.get("title", ""),
                "channel": sn.get("channelTitle", ""),
                "publishedAt": sn.get("publishedAt", ""),
                "url": f"https://www.youtube.com/watch?v={vid}",
            })
        return out
    except Exception as e:
        print(f"[youtube] warn: {e}")
        return []
