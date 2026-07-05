"""
ChromaDB client — Gemini text-embedding-004
--------------------------------------------
Uses Gemini's text-embedding-004 model (768 dimensions) for all
vector embeddings. The local sentence-transformers model is NOT used.

On first startup the old collection (if any) is deleted and recreated
so there are no stale vectors from a different embedding model.
"""

import os

import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings
import google.generativeai as genai

from app.schemas.settings import settings

COLLECTION_NAME = "citizen_submissions"
EMBEDDING_MODEL = "models/text-embedding-004"


# ---------------------------------------------------------------------------
# Gemini embedding function (ChromaDB interface)
# ---------------------------------------------------------------------------

class _GeminiEmbeddings(EmbeddingFunction):
    """Wraps Gemini embed_content for use as a ChromaDB EmbeddingFunction."""

    def __call__(self, input: Documents) -> Embeddings:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        embeddings = []
        for text in input:
            result = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=text,
                task_type="retrieval_document",
            )
            embeddings.append(result["embedding"])
        return embeddings


_embed_fn = _GeminiEmbeddings()
_collection = None


# ---------------------------------------------------------------------------
# Collection management
# ---------------------------------------------------------------------------

_SENTINEL_ID = "__embedding_model__"
_SENTINEL_VALUE = EMBEDDING_MODEL


def get_collection():
    """
    Return the ChromaDB collection, creating it if necessary.

    We use a sentinel document to detect whether the on-disk collection was
    built with the current embedding model. If the model changed (or the
    collection is new), we wipe and recreate it so there are no stale vectors.
    Submissions indexed in a previous session with the SAME model are kept.
    """
    global _collection
    if _collection is not None:
        return _collection

    client = chromadb.PersistentClient(path=settings.chroma_path)

    # Check if an existing collection was built with the same embedding model
    needs_reset = False
    try:
        existing = client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=_embed_fn,
        )
        sentinel = existing.get(ids=[_SENTINEL_ID])
        if not sentinel["ids"] or sentinel["metadatas"][0].get("model") != _SENTINEL_VALUE:
            needs_reset = True
        else:
            _collection = existing
    except Exception:
        needs_reset = True

    if needs_reset:
        try:
            client.delete_collection(name=COLLECTION_NAME)
        except Exception:
            pass
        _collection = client.create_collection(
            name=COLLECTION_NAME,
            embedding_function=_embed_fn,
            metadata={"hnsw:space": "cosine"},
        )
        # Write sentinel so future restarts know which model built this collection
        _collection.add(
            ids=[_SENTINEL_ID],
            documents=["sentinel"],
            metadatas=[{"model": _SENTINEL_VALUE}],
        )

    return _collection


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def add_submission(submission_id: str, text: str, metadata: dict) -> None:
    col = get_collection()
    col.add(
        ids=[submission_id],
        documents=[text],
        metadatas=[metadata],
    )


def query_similar(text: str, category: str, top_k: int = 10) -> list[dict]:
    col = get_collection()
    if col.count() == 0:
        return []

    # Use retrieval_query task type for the query embedding
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    query_embedding = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=text,
        task_type="retrieval_query",
    )["embedding"]

    results = col.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, col.count()),
        where={"category": category},
    )

    items = []
    for i, doc_id in enumerate(results["ids"][0]):
        items.append({
            "submission_id": doc_id,
            "summary": results["documents"][0][i],
            "location": results["metadatas"][0][i].get("location", "unspecified"),
            "similarity_score": 1.0 - results["distances"][0][i],
        })
    return items
