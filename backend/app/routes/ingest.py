from __future__ import annotations

from typing import List
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["ingest"])


class RssBody(BaseModel):
    feeds: List[str]


@router.post("/ingest/rss")
def ingest_rss(body: RssBody):
    """
    Minimal RSS ingest: parses the feeds and reports how many items were seen.
    (Hook up your vectorstore here if you want to persist content.)
    """
    try:
        import feedparser  # installed in your backend
    except Exception as exc:
        return {"ok": False, "error": f"feedparser not available: {exc}"}

    total = 0
    for url in body.feeds:
        try:
            d = feedparser.parse(url)
            total += len(getattr(d, "entries", []) or [])
        except Exception as exc:
            print(f"[ingest] failed {url}: {exc}")

    return {"ok": True, "added": total}



