from __future__ import annotations

import os
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

# All heavy imports happen lazily inside get_vectorstore()
# to keep app startup instant.


@dataclass
class VectorHit:
    id: str
    text: str
    metadata: dict
    distance: Optional[float] = None


class _VectorStoreWrapper:
    """
    Small helper around ChromaDB + Sentence-Transformers.

    Notes:
      - Uses a persistent Chroma client if RAG_PERSIST_DIR is set or the default folder is available.
      - Model is configurable via RAG_MODEL_NAME (default: all-MiniLM-L6-v2).
      - Thread-safe lazy singleton (created via get_vectorstore()).
    """

    def __init__(self, persist_dir: str, model_name: str) -> None:
        # Lazy import here (heavy)
        import chromadb  # noqa: WPS433
        from chromadb.config import Settings  # noqa: WPS433
        from chromadb.utils import embedding_functions  # noqa: WPS433

        from sentence_transformers import SentenceTransformer  # noqa: WPS433

        self._lock = threading.RLock()

        # Ensure directory exists (for persistent client)
        Path(persist_dir).mkdir(parents=True, exist_ok=True)

        # Initialize embedding model (download may happen here the first time)
        # You can swap to a different small model if you want faster cold starts.
        self._model = SentenceTransformer(model_name)

        # Chroma client + collection
        self._client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(
                anonymized_telemetry=False,
            ),
        )
        self._collection = self._client.get_or_create_collection(
            name="documents",
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=model_name
            ),
        )

    # --------------- Public API ---------------

    def add_texts(
        self,
        texts: Sequence[str],
        metadatas: Optional[Sequence[dict]] = None,
        ids: Optional[Sequence[str]] = None,
        batch_size: int = 64,
    ) -> int:
        """
        Add raw texts into the vector store.
        """
        if not texts:
            return 0

        with self._lock:
            total = 0
            # Insert in batches to keep memory in check
            for start in range(0, len(texts), batch_size):
                end = start + batch_size
                batch_texts = list(texts[start:end])
                batch_metas = list(metadatas[start:end]) if metadatas else None
                batch_ids = list(ids[start:end]) if ids else None

                self._collection.add(
                    documents=batch_texts,
                    metadatas=batch_metas,
                    ids=batch_ids,
                )
                total += len(batch_texts)
            return total

    def query(
        self,
        query_text: str,
        k: int = 5,
        where: Optional[dict] = None,
        include_embeddings: bool = False,
    ) -> List[VectorHit]:
        """
        Perform a similarity search.
        """
        if not query_text:
            return []

        results = self._collection.query(
            query_texts=[query_text],
            n_results=k,
            where=where,
            include=["metadatas", "documents", "distances"]
            + (["embeddings"] if include_embeddings else []),
        )
        hits: List[VectorHit] = []
        # results fields are lists of lists (per-query); we query a single item
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        dists = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]

        for i, text in enumerate(docs):
            hits.append(
                VectorHit(
                    id=ids[i] if i < len(ids) else str(i),
                    text=text,
                    metadata=metas[i] if i < len(metas) else {},
                    distance=dists[i] if i < len(dists) else None,
                )
            )
        return hits

    def count(self) -> int:
        return self._collection.count()

    def reset(self) -> None:
        """
        Danger: clears the entire collection.
        """
        with self._lock:
            self._client.delete_collection("documents")
            self._collection = self._client.get_or_create_collection(name="documents")


# --------------- Lazy Singleton Accessor ---------------

_store_singleton: Optional[_VectorStoreWrapper] = None
_store_lock = threading.Lock()


def get_vectorstore() -> _VectorStoreWrapper:
    """
    Lazily create and return the global vector store instance.

    Env:
      - RAG_MODEL_NAME   (default: 'sentence-transformers/all-MiniLM-L6-v2')
      - RAG_PERSIST_DIR  (default: '<repo>/backend/.chroma')
    """
    global _store_singleton  # noqa: PLW0603
    if _store_singleton is not None:
        return _store_singleton

    with _store_lock:
        if _store_singleton is not None:
            return _store_singleton

        model_name = os.getenv(
            "RAG_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"
        )

        # Default persist dir: backend/.chroma
        default_persist = str(Path(__file__).resolve().parents[2] / ".chroma")
        persist_dir = os.getenv("RAG_PERSIST_DIR", default_persist)

        print(
            f"[vectorstore] Initializing with model='{model_name}', persist_dir='{persist_dir}'"
        )
        _store_singleton = _VectorStoreWrapper(
            persist_dir=persist_dir,
            model_name=model_name,
        )
        print(
            f"[vectorstore] Ready | docs={_store_singleton.count()} at '{persist_dir}'"
        )
        return _store_singleton

