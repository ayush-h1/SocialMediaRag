from fastapi import APIRouter, Query
from typing import Dict, Any, List

from app.services.youtube import search_youtube
# If you have reddit/twitter helpers, import them too; otherwise keep stubs:
try:
    from app.services.reddit import search_reddit
except Exception:  # pragma: no cover
    def search_reddit(q: str) -> List[Dict[str, Any]]: return []

try:
    from app.services.twitter import search_twitter
except Exception:  # pragma: no cover
    def search_twitter(q: str) -> List[Dict[str, Any]]: return []

router = APIRouter(prefix="/api", tags=["search"])

@router.get("/search")
def search(q: str = Query(..., min_length=1)) -> Dict[str, Any]:
    """
    Aggregates results from local RAG + social sources.
    NEVER raises – returns partial results and an 'errors' list.
    """
    errors: List[str] = []
    yt: List[Dict[str, Any]] = []
    rd: List[Dict[str, Any]] = []
    tw: List[Dict[str, Any]] = []
    rag: List[Dict[str, Any]] = []

    # Local RAG (optional – wrap in try to avoid hard failures)
    try:
        # from app.services.rag import rag_search
        # rag = rag_search(q)
        rag = []  # keep empty if you don't have RAG wired yet
    except Exception as e:
        errors.append(f"RAG: {e}")

    # YouTube
    try:
        yt = search_youtube(q)
    except Exception as e:
        errors.append(f"YouTube: {e}")

    # Reddit
    try:
        rd = search_reddit(q)
    except Exception as e:
        errors.append(f"Reddit: {e}")

    # Twitter/X
    try:
        tw = search_twitter(q)
    except Exception as e:
        errors.append(f"Twitter: {e}")

    return {
        "query": q,
        "rag": rag,
        "youtube": yt,
        "reddit": rd,
        "twitter": tw,
        "errors": errors,
    }
