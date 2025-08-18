from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from typing import Any, Dict, List

# Import your services (all of these are safe/fail-open now)
from app.services.youtube import search_youtube
from app.services.reddit import search_reddit
from app.services.vectorstore import search_local  # returns [] if no index

router = APIRouter(prefix="/api", tags=["search"])

@router.get("/search")
def search(q: str = Query(..., min_length=1, description="Query string")) -> Dict[str, Any]:
    """
    Aggregate search over:
      - Local RAG index
      - YouTube (optional API key)
      - Reddit (public endpoint with UA)
    This endpoint **never** raises; it returns partial results if any source fails.
    """
    out: Dict[str, List[Dict[str, Any]]] = {"rag": [], "youtube": [], "reddit": []}
    errors: Dict[str, str] = {}

    # Local corpus (vector store)
    try:
        out["rag"] = search_local(q, k=5) or []
    except Exception as e:  # noqa: BLE001
        errors["rag"] = str(e)

    # YouTube (optional)
    try:
        out["youtube"] = search_youtube(q, max_results=5) or []
    except Exception as e:  # noqa: BLE001
        errors["youtube"] = str(e)

    # Reddit (public)
    try:
        out["reddit"] = search_reddit(q, limit=5) or []
    except Exception as e:  # noqa: BLE001
        errors["reddit"] = str(e)

    # Always 200 so the browser never shows "Failed to fetch"
    return {"ok": True, "query": q, "results": out, "errors": errors}
