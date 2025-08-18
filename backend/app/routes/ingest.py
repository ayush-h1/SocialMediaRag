from fastapi import APIRouter, Body

router = APIRouter(prefix="/ingest", tags=["ingest"])

@router.post("/rss")
def ingest_rss(feed_url: str = Body(..., embed=True, description="RSS/Atom feed URL")):
    # Minimal stub; replace with real ingest later.
    return {"ok": True, "added": 0, "feed_url": feed_url}


