from __future__ import annotations

from typing import Dict, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl, field_validator

import requests
import feedparser

router = APIRouter(tags=["ingest"])


class RssBody(BaseModel):
    feeds: List[HttpUrl]

    # make sure there is at least one feed
    @field_validator("feeds")
    @classmethod
    def _not_empty(cls, v: List[HttpUrl]) -> List[HttpUrl]:
        if not v:
            raise ValueError("at least one feed URL is required")
        return v


UA = "SocialMediaRAG/1.0 (+https://example.com)"
TIMEOUT = 10  # seconds per feed
MAX_BYTES = 1_000_000  # 1 MB cap per feed to avoid big downloads


@router.post("/ingest/rss")
def ingest_rss(body: RssBody) -> Dict[str, object]:
    """Fetch each RSS URL with a short timeout, parse, and report counts.
    Never hangs; never raises unhandled exceptions.
    """
    results: Dict[str, int] = {}
    total = 0

    for url in body.feeds:
        count = 0
        try:
            r = requests.get(
                str(url),
                headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8"},
                timeout=TIMEOUT,
            )
            if r.status_code != 200:
                print(f"[ingest] {url} -> HTTP {r.status_code}")
            else:
                content = r.content[:MAX_BYTES]
                parsed = feedparser.parse(content)
                entries = getattr(parsed, "entries", []) or []
                count = len(entries)
        except requests.Timeout:
            print(f"[ingest] timeout: {url}")
        except Exception as exc:
            print(f"[ingest] {url} error: {exc}")

        results[str(url)] = count
        total += count

    return {"ok": True, "added": total, "by_feed": results}




