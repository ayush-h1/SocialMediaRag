from fastapi import APIRouter, Query
from ..services.youtube import search_youtube
from ..services.reddit import search_reddit
from ..services.twitter import search_twitter
from ..services.rag import RAG

router = APIRouter()

@router.get("/search")
def search(q: str = Query("", description="query string")):
    yt = search_youtube(q)
    rd = search_reddit(q)
    tw = search_twitter(q)
    rag_hits = RAG.search(q, k=5)

    return {
        "query": q,
        "sources": [yt, rd, tw],
        "rag": rag_hits,
    }
