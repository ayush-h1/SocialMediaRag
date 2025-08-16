def search_twitter(query: str, max_results: int = 5):
    # Stub (no API calls). Replace with real X API if you have credentials.
    return {
        "source": "twitter",
        "items": [
            {"title": f"Tweet about: {query}", "description": "Demo tweet content", "url": None, "author": "demo_user"}
        ]
    }
