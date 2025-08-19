# backend/app/routes/search.py
from __future__ import annotations

from typing import Dict, Any
from fastapi import APIRouter, Query

from app.services.vectorstore import search as vs_search

router = APIRouter(tags=["search"])


@router.get("/search")
def search(q: str = Query(..., min_length=1, description="Search query"),
           k: int = Query(10, ge=1, le=50)) -> Dict[str, Any]:
    results = vs_search(q, k=k)
    return {
        "query": q,
        "rag": results,       # vector results from your ingested docs
        "sources": {},        # keep shape compatible with your UI
        "count": len(results)
    }

