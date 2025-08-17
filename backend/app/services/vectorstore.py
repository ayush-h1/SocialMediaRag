import os
from typing import List, Dict
import chromadb
from sentence_transformers import SentenceTransformer

EMB_MODEL = os.getenv("EMB_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
CHROMA_PATH = os.getenv("CHROMA_PATH", "/tmp/chroma")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "social_posts")

_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _client.get_or_create_collection(name=CHROMA_COLLECTION)

_model = SentenceTransformer(EMB_MODEL)

def upsert_docs(docs: List[Dict]) -> int:
    # docs: [{"id": "doc1", "text": "...", "meta": {...}}, ...]
    ids = [d["id"] for d in docs]
    texts = [d["text"] for d in docs]
    metas = [d.get("meta", {}) for d in docs]
    embs = _model.encode(texts, normalize_embeddings=True).tolist()
    _collection.upsert(ids=ids, documents=texts, embeddings=embs, metadatas=metas)
    return len(ids)

def search(query: str, k: int = 5):
    q_emb = _model.encode([query], normalize_embeddings=True).tolist()[0]
    res = _collection.query(query_embeddings=[q_emb], n_results=k,
                            include=["documents", "metadatas", "distances", "ids"])
    hits = []
    for i in range(len(res["ids"][0])):
        hits.append({
            "id": res["ids"][0][i],
            "text": res["documents"][0][i],
            "meta": res["metadatas"][0][i],
            "score": 1 - res["distances"][0][i],  # higher is better
        })
    return hits
