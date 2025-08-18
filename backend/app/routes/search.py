from __future__ import annotations

from typing import Any, Dict, List
from fastapi import APIRouter, Query

# Import the in-memory docs from ingest
from .ingest import FEED_DOCS

router = APIRouter(tags=["search"])


@router.get("/search")
def search(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
) -> Dict[str, Any]:
    """
    Super-simple substring match over ingested RSS docs (demo).
    Returns matches in the 'rag' section so your UI shows them under 'RAG (local corpus)'.
    """
    ql = q.lower().strip()
    hits: List[Dict[str, str]] = []

    for doc in FEED_DOCS.values():
        hay = f"{doc.get('title','')} {doc.get('snippet','')}".lower()
        if ql in hay:
            hits.append(doc)
            if len(hits) >= limit:
                break

    return {
        "query": q,
        "rag": hits,                # your UI shows this under “RAG (local corpus)”
        "sources": {
            "youtube": [],
            "reddit": [],
            "twitter": [],
        },
    }




