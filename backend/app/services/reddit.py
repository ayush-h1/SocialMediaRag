import requests, os

def search_reddit(query: str, max_results: int = 5):
    # Uses public Reddit JSON. May be rate-limited without auth.
    ua = os.getenv("REDDIT_USER_AGENT", "SocialMediaRAG/0.1 by example")
    headers = {"User-Agent": ua}
    url = "https://www.reddit.com/search.json"
    params = {"q": query, "limit": max_results, "sort": "relevance", "t": "all"}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        items = []
        for child in (data.get("data", {}).get("children", []) or []):
            d = child.get("data", {})
            items.append({
                "title": d.get("title"),
                "description": d.get("selftext") or d.get("url_overridden_by_dest"),
                "url": "https://www.reddit.com" + d.get("permalink",""),
                "subreddit": d.get("subreddit"),
                "author": d.get("author"),
            })
        return {"source": "reddit", "items": items}
    except Exception as e:
        return {"source": "reddit", "items": [], "note": f"Reddit search failed: {e}"}
