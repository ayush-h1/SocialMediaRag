from collections import Counter
import math, json, os, re
from typing import List, Dict, Any

WORD_RE = re.compile(r"[a-zA-Z0-9_]+")

def tokenize(text: str) -> list[str]:
    return [w.lower() for w in WORD_RE.findall(text or "")]

class TinyRAG:
    def __init__(self, docs: List[Dict[str, Any]]):
        self.docs = docs
        self.N = len(docs)
        self.doc_tokens = [tokenize(d.get("text","")) for d in docs]
        # build idf
        df = Counter()
        for toks in self.doc_tokens:
            for term in set(toks):
                df[term] += 1
        self.idf = {t: math.log((1 + self.N) / (1 + df[t])) + 1 for t in df}

        # build vectors
        self.doc_vecs = [self._tfidf(toks) for toks in self.doc_tokens]

    def _tfidf(self, toks: list[str]) -> Dict[str, float]:
        tf = Counter(toks)
        vec = {}
        for term, freq in tf.items():
            vec[term] = (freq / max(1,len(toks))) * self.idf.get(term, 0.0)
        return vec

    @staticmethod
    def _cos(a: Dict[str,float], b: Dict[str,float]) -> float:
        keys = set(a) | set(b)
        dot = sum(a.get(k,0.0)*b.get(k,0.0) for k in keys)
        na = math.sqrt(sum(v*v for v in a.values()))
        nb = math.sqrt(sum(v*v for v in b.values()))
        if na == 0 or nb == 0: return 0.0
        return dot/(na*nb)

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        qv = self._tfidf(tokenize(query))
        scored = [(self._cos(qv, dv), i) for i, dv in enumerate(self.doc_vecs)]
        scored.sort(reverse=True)
        out = []
        for score, idx in scored[:k]:
            d = self.docs[idx].copy()
            d["score"] = round(score, 4)
            out.append(d)
        return out

# load sample docs
def load_default_corpus():
    here = os.path.dirname(__file__)
    path = os.path.join(here, "..", "data", "sample_docs.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

RAG = TinyRAG(load_default_corpus())
