from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter, Query

router = APIRouter(prefix="", tags=["social"])


def _safe_call(fn, *args, **kwargs) -> List[Dict]:
    try:
        return fn(*args, **kwargs) or []
    except Exception as exc:  # noqa: BLE001
        # Never let a single source take down the endpoint
        print(f"[social] source error in {getattr(fn, '__name__', fn)}: {exc}")
        return []


@router.get("/search")
def search(q: str = Query(..., min_length=1), limit: int = Query(5, ge=1, le=25)) -> Dict:
    """
    Aggregate search across sources. Each source is best-effort.
    Returns:
      { "query": q, "count": N, "items": [...] }
    """
    results: List[Dict] = []

    # YouTube (best-effort; returns [] on 403/missing key)
    try:
        from app.services.youtube import search_youtube  # lazy import
        results += _safe_call(search_youtube, q, max_results=limit)
    except Exception as exc:  # noqa: BLE001
        print(f"[social] youtube import/use failed: {exc}")

    # Reddit (optional)
    try:
        from app.services.reddit import search_reddit  # if you have it
        results += _safe_call(search_reddit, q, limit=limit)
    except Exception as exc:  # noqa: BLE001
        # Ok if not implemented
        print(f"[social] reddit unavailable: {exc}")

    # RSS/News (optional)
    try:
        from app.services.rss import search_rss  # if you have it
        results += _safe_call(search_rss, q, limit=limit)
    except Exception as exc:  # noqa: BLE001
        print(f"[social] rss unavailable: {exc}")

    return {"query": q, "count": len(results), "items": results}

