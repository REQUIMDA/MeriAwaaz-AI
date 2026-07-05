import json
import uuid

from langchain_core.tools import tool

from app.services import chroma_client
from app.services.store import STORE
from app.schemas.models import ClusterResult
from app.core.llm import get_model

_llm = None


def _get_llm():
    global _llm
    if _llm is None:
        _llm = get_model()
    return _llm


@tool
def search_similar_submissions(summary: str, category: str, top_k: int = 10) -> list[dict]:
    """Search ChromaDB for citizen submissions similar to the current one.

    Args:
        summary: short text summary of the current submission
        category: issue category (e.g. 'Education', 'Roads', 'Healthcare')
        top_k: number of similar results to retrieve

    Returns:
        list of dicts with keys: submission_id, summary, location, similarity_score
    """
    return chroma_client.query_similar(text=summary, category=category, top_k=top_k)


@tool
def cluster_submissions(
    submissions: list[dict],
    current_summary: str,
    category: str,
    location: str,
) -> dict:
    """Use Gemini to intelligently cluster the current submission with similar ones.

    Gemini reads all the similar submissions and decides:
    - What the common theme/cluster name is
    - Whether this matches an existing cluster or is a new one
    - What the representative location is

    Args:
        submissions: list of similar submissions from search_similar_submissions
        current_summary: summary of the current submission being processed
        category: issue category
        location: location from the parsed issue

    Returns:
        dict with keys: cluster_id, cluster_name, cluster_size, center_location
    """
    # Build context of existing clusters for Gemini to match against
    existing_clusters = [
        {
            "cluster_id": cid,
            "cluster_name": c.cluster_name,
            "center_location": c.center_location,
            "cluster_size": c.cluster_size,
        }
        for cid, c in STORE.clusters.items()
        if c.cluster_name.lower() == category.lower()
    ]

    # Build list of similar submission summaries for Gemini
    similar_texts = [s.get("summary", "") for s in submissions if s.get("summary")]

    prompt = f"""You are a demand clustering agent. Your job is to group citizen complaints into clusters.

Current submission:
  Category: {category}
  Location: {location}
  Summary: {current_summary}

Similar past submissions ({len(similar_texts)} found):
{json.dumps(similar_texts, indent=2) if similar_texts else "None yet."}

Existing clusters for this category:
{json.dumps(existing_clusters, indent=2) if existing_clusters else "None yet."}

Task:
1. Decide if this submission belongs to an existing cluster or needs a new one.
2. If it matches an existing cluster, return that cluster_id.
3. If it is a new cluster, set cluster_id to "new".
4. Give the cluster a short descriptive name (e.g. "School Infrastructure", "Road Repair", "Water Supply").
5. The center_location should be the most representative location.

Return ONLY valid JSON with these exact keys:
{{
  "cluster_id": "existing_cluster_id_or_new",
  "cluster_name": "short descriptive name",
  "center_location": "most representative location"
}}

No explanation, no markdown, just the JSON object."""

    response = _get_llm().invoke(prompt)
    content = response.content if hasattr(response, "content") else str(response)
    content = content.strip().strip("```json").strip("```").strip()

    try:
        gemini_result = json.loads(content)
    except Exception:
        # Fallback if Gemini returns unparseable response
        gemini_result = {
            "cluster_id": "new",
            "cluster_name": category,
            "center_location": location,
        }

    chosen_id = gemini_result.get("cluster_id", "new")
    cluster_name = gemini_result.get("cluster_name", category)
    center_location = gemini_result.get("center_location", location)

    if chosen_id != "new" and chosen_id in STORE.clusters:
        # Increment existing cluster
        STORE.clusters[chosen_id].cluster_size += 1
        cluster = STORE.clusters[chosen_id]
    else:
        # Create new cluster
        new_id = f"cluster_{uuid.uuid4().hex[:8]}"
        STORE.clusters[new_id] = ClusterResult(
            cluster_id=new_id,
            cluster_name=cluster_name,
            cluster_size=len(submissions) + 1,
            center_location=center_location,
        )
        cluster = STORE.clusters[new_id]

    return {
        "cluster_id": cluster.cluster_id,
        "cluster_name": cluster.cluster_name,
        "cluster_size": cluster.cluster_size,
        "center_location": cluster.center_location,
    }
