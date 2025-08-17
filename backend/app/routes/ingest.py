from fastapi import APIRouter, Query, HTTPException
import os, time, requests, feedparser, praw
from bs4 import BeautifulSoup
from ..services.vectorstore import upsert_docs

router = APIRouter()

def _clean(s: str) -> str:
    try:
        return " ".join(BeautifulSoup(s or "", "html.parser").get_text(" ").split())
    except Exception:
        return " ".join((s or "").split())

@router.post("/ingest/rss")
def ingest_rss(url: str = Query(..., description="RSS/Atom feed URL")):
    feed = feedparser.parse(url)
    if getattr(feed, "bozo", 0):
        raise HTTPException(400, "Invalid RSS/Atom feed")
    docs = []
    ts = int(time.time())
    for i, e in enumerate(feed.entries[:50]):
        text = _clean(f"{e.get('title','')} {e.get('summary','')}")
        docs.append({"id": f"rss:{ts}:{i}",
                     "text": text,
                     "meta": {"source":"rss","url":e.get('link')}})
    return {"ok": True, "count": upsert_docs(docs)}

@router.post("/ingest/youtube")
def ingest_youtube(channel_id: str):
    key = os.getenv("YOUTUBE_API_KEY")
    if not key:
        raise HTTPException(400, "Set YOUTUBE_API_KEY")
    url = ("https://www.googleapis.com/youtube/v3/search"
           f"?key={key}&channelId={channel_id}&part=snippet,id&order=date&maxResults=25")
    data = requests.get(url, timeout=20).json()
    docs = []
    for item in data.get("items", []):
        sn = item.get("snippet", {})
        text = _clean(f"{sn.get('title','')} {sn.get('description','')}")
        vid = item.get('id', {}).get('videoId') or f"yt:{int(time.time())}"
        docs.append({"id": f"yt:{vid}", "text": text,
                     "meta": {"source":"youtube","channelId":channel_id}})
    return {"ok": True, "count": upsert_docs(docs)}

@router.post("/ingest/reddit")
def ingest_reddit(subreddit: str):
    try:
        reddit = praw.Reddit(client_id=os.getenv("REDDIT_CLIENT_ID"),
                             client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                             user_agent=os.getenv("REDDIT_USER_AGENT","smrag/1.0"))
    except Exception as e:
        raise HTTPException(400, f"PRAW init failed: {e}")
    sub = reddit.subreddit(subreddit)
    docs = []
    for p in sub.hot(limit=50):
        text = _clean(f"{p.title} {p.selftext or ''}")
        docs.append({"id": f"rd:{p.id}", "text": text,
                     "meta": {"source":"reddit","subreddit":subreddit,"permalink": f"https://reddit.com{p.permalink}"}})
    return {"ok": True, "count": upsert_docs(docs)}
