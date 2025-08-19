# backend/app/services/vectorstore.py
from __future__ import annotations

import os
import hashlib
from typing import Iterable, List, Dict, Any

import chromadb
from chromadb.utils import embedding_functions


# Use a persistent folder (ephemeral on free Render, persists across app restarts but not deploys)
CHROMA_PATH = os.getenv("CHROMA_PATH", "/opt/render/project/.chroma")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "docs")

_client = None
_collection = None


def get_collection():
    """Singleton Chroma collection with SentenceTransformer embeddings."""
    global _client, _collection
    if _collection is not None:
        return _collection

    # Make sure the directory exists
    os.makedirs(CHROMA_PATH, exist_ok=True)

    _client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Lightweight, good default
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
    )

    _collection = _client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    return _collection


def _hash_id(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def add_documents(items: Iterable[Dict[str, Any]]) -> int:
    """
    items: [{id?, text, url?, source?, title?, extra...}]
    Returns number added/upserted.
    """
    col = get_collection()

    ids: List[str] = []
    docs: List[str] = []
    metas: List[Dict[str, Any]] = []

    for it in items:
        text = (it.get("text") or "").strip()
        if not text:
            continue
        # Stable id (prefer url if provided)
        rid = it.get("id") or it.get("url") or _hash_id(text)
        ids.append(str(rid))
        docs.append(text)
        metas.append({k: v for k, v in it.items() if k not in {"id", "text"}})

    if not ids:
        return 0

    col.upsert(ids=ids, documents=docs, metadatas=metas)
    return len(ids)


def search(query: str, k: int = 10) -> List[Dict[str, Any]]:
    col = get_collection()
    res = col.query(query_texts=[query], n_results=k)
    out: List[Dict[str, Any]] = []

    ids = res.get("ids", [[]])[0]
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0] or []

    for i, doc in enumerate(docs):
        meta = metas[i] if i < len(metas) else {}
        out.append(
            {
                "id": ids[i] if i < len(ids) else None,
                "text": doc,
                "score": (1 - dists[i]) if i < len(dists) else None,  # higher is better
                "meta": meta,
            }
        )
    return out

