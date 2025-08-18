from typing import Dict, Any
from fastapi import APIRouter, Query

router = APIRouter(tags=["search"])

@router.get("/search")
def search(q: str = Query(..., min_length=1, description="Search query")) -> Dict[str, Any]:
    # Minimal stub so Swagger shows GET /api/search and it never 500s.
    return {
        "query": q,
        "rag": [],
        "sources": {
            "youtube": [],
            "reddit": [],
            "twitter": [],
        },
    }


