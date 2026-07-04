import chromadb
from app.schemas.settings import settings

_collection = None


def get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=settings.chroma_path)
        _collection = client.get_or_create_collection(
            name="citizen_submissions",
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


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
    results = col.query(
        query_texts=[text],
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