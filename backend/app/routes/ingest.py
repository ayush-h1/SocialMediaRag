# backend/app/routes/ingest.py
from __future__ import annotations

from typing import List, Dict, Any
from datetime import datetime

import feedparser
from fastapi import APIRouter, Body

from app.services.vectorstore import add_documents

router = APIRouter(tags=["ingest"])


@router.post("/ingest/rss")
def ingest_rss(body: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """
    Body:
    {
      "feeds": ["https://hnrss.org/frontpage", "https://www.theverge.com/rss/index.xml"]
    }
    """
    feeds: List[str] = list(body.get("feeds") or [])
    by_feed: Dict[str, int] = {}
    total = 0

    for feed_url in feeds:
        parsed = feedparser.parse(feed_url)
        items: List[Dict[str, Any]] = []
        for e in parsed.entries:
            title = (getattr(e, "title", "") or "").strip()
            link = (getattr(e, "link", "") or "").strip()
            summary = (getattr(e, "summary", "") or "").strip()
            content = summary or title

            if not content:
                continue

            items.append(
                {
                    "id": link or None,
                    "url": link or None,
                    "source": "rss",
                    "feed": feed_url,
                    "title": title,
                    "text": content,
                    "published": getattr(e, "published", None),
                    "ingested_at": datetime.utcnow().isoformat() + "Z",
                }
            )

        added = add_documents(items)
        by_feed[feed_url] = added
        total += added

    return {"ok": True, "added": total, "by_feed": by_feed}
