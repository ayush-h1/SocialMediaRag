from __future__ import annotations

from typing import Any, Dict, List
from fastapi import APIRouter, Query

# These service modules already exist in your repo
# and each exposes a simple search_* function.
try:
    from app.services.youtube import search_youtube
except Exception:  # keep app booting even if a service import fails
    search_youtube = None  # type: ignore

try:
    from app.services.reddit import search_reddit
except Exception:
    search_reddit = None  # type: ignore

try:
    from app.services.twitter import search_twitter
except Exception:
    search_twitter = None  # type: ignore


router = APIRouter(tags=["search"])


def _safe_call(fn, *args, **kwargs) -> List[Dict[str, Any]]:
    """Call a source function, never let it 500."""
    if fn is None:
        return []
    try:
        res = fn(*args, **kwargs)
        return res or []
    except Exception as exc:
        print(f"[search] source error: {exc}")
        return []


@router.get("/search")
def search(
    q: str = Query(..., min_length=1, description="Search query"),
) -> Dict[str, Any]:
    """
    Aggregates sources (YouTube/Reddit/Twitter). Each source is optional:
    if its key/env is missing or it errors, it just returns [] for that source.
    """
    yt = _safe_call(search_youtube, q)
    rd = _safe_call(search_reddit, q)
    tw = _safe_call(search_twitter, q)

    return {
        "query": q,
        "rag": [],  # fill from vectorstore later if you want
        "sources": {
            "youtube": yt,
            "reddit": rd,
            "twitter": tw,
        },
    }



