from fastapi import APIRouter, HTTPException

from app.schemas.models import AgentState, Explanation
from app.services.store import STORE

# ---------------------------------------------------------------------------
# Explainability Agent — defensive import
# ---------------------------------------------------------------------------
try:
    from app.supervisor import explainability_node
    _AGENT_AVAILABLE = True
except ImportError:
    _AGENT_AVAILABLE = False

router = APIRouter()


# ---------------------------------------------------------------------------
# Private helper
# ---------------------------------------------------------------------------

def _invoke_explainability(state: AgentState) -> Explanation:
    # explainability_node handles the AgentState -> MessagesState translation
    result_dict = explainability_node(state)
    rec = result_dict.get("recommendation", state.recommendation)

    if rec is not None and rec.explanation is not None:
        return rec.explanation

    raise ValueError("Explainability Agent did not produce an explanation.")


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------

@router.get("/api/explain/{project_id}", response_model=Explanation)
def explain_project(project_id: str) -> Explanation:
    """
    Generate a fresh on-demand explanation for a single recommendation.
    Called when the MP clicks a recommendation card. Never cached.
    """
    if not _AGENT_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail=(
                "Explainability Agent is not available. "
                "Ensure backend/app/agents/explainability_agent.py is present."
            ),
        )

    rec = STORE.get_recommendation(project_id)
    if rec is None:
        raise HTTPException(
            status_code=404,
            detail=f"No recommendation found for project_id '{project_id}'.",
        )

    ctx = STORE.get_context(project_id)
    if ctx is None:
        raise HTTPException(
            status_code=404,
            detail=f"No FusedContext found for project_id '{project_id}'.",
        )

    state = AgentState(
        submission_id=f"explain__{project_id}",
        input_type="text",
        recommendation=rec,
        knowledge_context=ctx,
    )

    try:
        return _invoke_explainability(state)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Agent produced no output: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent failed: {str(e)}")
