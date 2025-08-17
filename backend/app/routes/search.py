from fastapi import APIRouter, Query
import os, requests
from ..services.vectorstore import search as vs_search

router = APIRouter()

def _gen_answer(query: str, context: list[str]) -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key or not context:
        return "\n\n".join(context[:3])[:1500]
    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type":"application/json"},
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role":"system","content":"Answer concisely using the context; cite snippets if helpful."},
                {"role":"user","content": f"Q: {query}\n\nContext:\n" + "\n---\n".join(context[:8])}
            ],
            "temperature": 0.2
        },
        timeout=30
    )
    return r.json()["choices"][0]["message"]["content"].strip()

@router.get("/search")
def search(q: str = Query(..., min_length=2), k: int = 6):
    hits = vs_search(q, k)
    ctx = [h["text"] for h in hits]
    ans = _gen_answer(q, ctx)
    return {"hits": hits, "answer": ans}
