from langgraph.prebuilt import create_react_agent
from app.core.llm import get_model
from app.tools.policy_tools import compute_priority_score, rank_projects

SYSTEM_PROMPT = """
You are the Policy Recommendation Agent for MeriAwaaz AI.

Your job is to rank development projects using a deterministic formula.
You MUST use the compute_priority_score tool — never invent or estimate scores yourself.

Always follow this sequence:
1. For each candidate project, call compute_priority_score with the four normalised inputs:
   - citizen_demand: derived from cluster_size (divide by max expected submissions, cap at 1.0)
   - infrastructure_gap: taken directly from knowledge_fusion output
   - population_impact: population normalised against constituency average
   - cost_feasibility: 1.0 minus normalised estimated cost
2. Call rank_projects to sort them.
3. Return the top-ranked project as a structured JSON with:
   project_id, title, priority_score, breakdown, reason (one sentence).

The LLM explains the result — it never changes the score.
"""

policy_recommendation_agent = create_react_agent(
    model=get_model(),
    tools=[compute_priority_score, rank_projects],
    prompt=SYSTEM_PROMPT,
    name="policy_recommendation_agent",
)
