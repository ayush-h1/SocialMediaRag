import os, requests

def search_youtube(query: str, api_key: str | None = None, max_results: int = 5):
    api_key = api_key or os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        return {"source": "youtube", "items": [], "note": "Set YOUTUBE_API_KEY to enable YouTube search."}

    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "type": "video",
        "q": query,
        "maxResults": max_results,
        "key": api_key,
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    items = []
    for it in data.get("items", []):
        vid = (it.get("id") or {}).get("videoId")
        sn = it.get("snippet") or {}
        items.append({
            "title": sn.get("title"),
            "description": sn.get("description"),
            "url": f"https://www.youtube.com/watch?v={vid}" if vid else None,
            "channel": sn.get("channelTitle"),
            "publishedAt": sn.get("publishedAt"),
        })
    return {"source": "youtube", "items": items}
