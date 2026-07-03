from langchain_core.tools import tool


@tool
def search_similar_submissions(summary: str, category: str, top_k: int = 10) -> list[dict]:
    """Search ChromaDB for citizen submissions similar to the current one.

    Use this to find how many people have raised the same or related issues.

    Args:
        summary: short text summary of the current submission
        category: issue category (e.g. 'Education', 'Roads', 'Healthcare')
        top_k: number of similar results to retrieve

    Returns:
        list of dicts, each with keys: submission_id, summary, location, similarity_score
    """
    # Real implementation will embed summary and query ChromaDB.
    return []


@tool
def cluster_submissions(submissions: list[dict]) -> dict:
    """Group similar submissions into a demand cluster.

    Use this after search_similar_submissions to identify the hotspot
    and calculate total demand size.

    Args:
        submissions: list of similar submission dicts from search_similar_submissions

    Returns:
        dict with keys: cluster_name, cluster_size, center_location
    """
    return {
        "cluster_name": "",
        "cluster_size": 0,
        "center_location": "",
    }
