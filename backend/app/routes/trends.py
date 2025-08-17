from fastapi import APIRouter, Query
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import MiniBatchKMeans
from ..services.vectorstore import _collection

router = APIRouter()

@router.get("/trends")
def trends(k: int = Query(8, ge=2, le=20)):
    res = _collection.get(include=["documents","metadatas","ids"], limit=500)
    docs = res.get("documents") or []
    if not docs:
        return {"topics": [], "keywords": []}

    tfidf = TfidfVectorizer(max_features=2000, ngram_range=(1,2), stop_words="english")
    X = tfidf.fit_transform(docs)

    n_clusters = min(k, max(2, X.shape[0]//20))
    km = MiniBatchKMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    labels = km.fit_predict(X)

    terms = tfidf.get_feature_names_out()
    topic_keywords = []
    for c in range(n_clusters):
        center = km.cluster_centers_[c]
        top_idx = center.argsort()[-6:][::-1]
        topic_keywords.append({"topic": c, "keywords": [terms[i] for i in top_idx]})

    counts = [int((labels==c).sum()) for c in range(n_clusters)]
    topics = [{"topic": i, "count": counts[i]} for i in range(n_clusters)]
    topics.sort(key=lambda t: t["count"], reverse=True)
    return {"topics": topics[:k], "keywords": topic_keywords}
