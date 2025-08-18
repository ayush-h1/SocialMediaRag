
from fastapi import APIRouter, Query
from typing import Any, Dict, List

# services
from app.services.vectorstore import search_local
from app.services.youtube import search_youtube
from app.services.reddit import search_reddit

router = APIRouter(prefix="/api", tags=["search"])

@router.get("/search")
def search(q: str = Query(..., min_length=1)) -> Dict[str, Any]:
    """
    Returns partial results even if one or more sources fail.
    Always 200 to avoid 'Failed to fetch' in the browser.
    """
    results: Dict[str, List[Dict[str, Any]]] = {"rag": [], "youtube": [], "reddit": []}
    errors: Dict[str, str] = {}

    try:
        results["rag"] = search_local(q, k=5) or []
    except Exception as e:  # noqa: BLE001
        errors["rag"] = str(e)

    try:
        results["youtube"] = search_youtube(q, max_results=5) or []
    except Exception as e:  # noqa: BLE001
        errors["youtube"] = str(e)

    try:
        results["reddit"] = search_reddit(q, limit=5) or []
    except Exception as e:  # noqa: BLE001
        errors["reddit"] = str(e)

    return {"ok": True, "query": q, "results": results, "errors": errors}
