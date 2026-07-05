from langchain_core.tools import tool


@tool
def build_evidence_bullets(
    cluster_size: int,
    infrastructure_gap: float,
    population: int,
    facility_count: int,
    category: str,
) -> list[str]:
    """Build a list of 2–3 concise evidence bullets for a recommendation.

    Use this to ground the explanation in real numbers before generating
    the final human-readable summary.

    Args:
        cluster_size: number of citizens who raised this issue
        infrastructure_gap: gap score from knowledge_fusion (0.0–1.0)
        population: total population of the affected area
        facility_count: number of existing facilities of the relevant type
        category: issue category (e.g. 'Education', 'Healthcare')

    Returns:
        list of evidence bullet strings
    """
    bullets = [
        f"{cluster_size} citizens submitted {category.lower()} related requests.",
        f"Only {facility_count} existing {category.lower()} facilit{'y' if facility_count == 1 else 'ies'} serving a population of {population:,}.",
        f"Infrastructure gap score: {infrastructure_gap:.0%}.",
    ]
    return bullets


@tool
def compute_confidence_score(
    priority_score: float,
    cluster_size: int,
    data_completeness: float,
) -> float:
    """Compute a confidence score for the recommendation.

    Confidence reflects how reliable the recommendation is based on
    volume of citizen demand, score strength, and data completeness.

    Args:
        priority_score: the computed priority score (0.0–1.0)
        cluster_size: number of supporting submissions
        data_completeness: fraction of expected data fields that were available (0.0–1.0)

    Returns:
        confidence score between 0.0 and 1.0
    """
    demand_signal = min(cluster_size / 50, 1.0)  # caps at 50 submissions = full signal
    confidence = round(
        0.50 * priority_score + 0.30 * demand_signal + 0.20 * data_completeness, 4
    )
    return confidence
