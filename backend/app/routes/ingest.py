from __future__ import annotations

from typing import Dict, List
from fastapi import APIRouter
from pydantic import BaseModel, HttpUrl, field_validator

import requests
import feedparser

router = APIRouter(tags=["ingest"])

# --- In-memory store for demo purposes ---
# key -> doc dict
FEED_DOCS: Dict[str, Dict[str, str]] = {}

UA = "SocialMediaRAG/1.0 (+https://example.com)"
TIMEOUT = 10           # seconds per feed
MAX_BYTES = 1_000_000  # 1 MB per feed


class RssBody(BaseModel):
    feeds: List[HttpUrl]

    @field_validator("feeds")
    @classmethod
    def _not_empty(cls, v: List[HttpUrl]) -> List[HttpUrl]:
        if not v:
            raise ValueError("at least one feed URL is required")
        return v


@router.post("/ingest/rss")
def ingest_rss(body: RssBody) -> Dict[str, object]:
    """
    Fetch feeds quickly (timeouts), parse with feedparser, and store entries in memory.
    """
    by_feed: Dict[str, int] = {}
    total_added = 0

    for url in body.feeds:
        added = 0
        try:
            r = requests.get(
                str(url),
                headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8"},
                timeout=TIMEOUT,
            )
            if r.status_code != 200:
                print(f"[ingest] {url} -> HTTP {r.status_code}")
                by_feed[str(url)] = 0
                continue

            content = r.content[:MAX_BYTES]
            parsed = feedparser.parse(content)
            entries = getattr(parsed, "entries", []) or []

            for e in entries:
                title = (e.get("title") or "").strip()
                link = (e.get("link") or "").strip()
                summary = (e.get("summary") or e.get("subtitle") or "").strip()

                # dedupe key: prefer guid/id, then link+title
                key = (e.get("id") or link or f"{url}::{title}").strip()
                if not key:
                    continue

                FEED_DOCS[key] = {
                    "title": title or "(untitled)",
                    "url": link,
                    "snippet": summary,
                    "source": "rss",
                }
                added += 1

        except requests.Timeout:
            print(f"[ingest] timeout: {url}")
        except Exception as exc:
            print(f"[ingest] {url} error: {exc}")

        by_feed[str(url)] = added
        total_added += added

    return {"ok": True, "added": total_added, "by_feed": by_feed}


# Optional quick sanity check
@router.post("/ingest/rss/ping")
def ingest_ping():
    return {"ok": True}





