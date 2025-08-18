from fastapi import APIRouter

router = APIRouter(tags=["ingest"])

@router.post("/ingest/rss")
def ingest_rss():
    return {"ok": True, "added": 0}

