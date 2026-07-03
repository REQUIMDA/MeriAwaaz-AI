from langgraph.checkpoint.memory import MemorySaver
from langgraph_supervisor import create_supervisor
from app.core.llm import get_model

# Agent imports — each file will be implemented as that milestone is built
from app.agents.citizen_intelligence_agent import citizen_intelligence_agent
from app.agents.demand_intelligence_agent import demand_intelligence_agent
from app.agents.knowledge_fusion_agent import knowledge_fusion_agent
from app.agents.policy_recommendation_agent import policy_recommendation_agent
from app.agents.explainability_agent import explainability_agent

model = get_model()

workflow = create_supervisor(
    [
        citizen_intelligence_agent,
        demand_intelligence_agent,
        knowledge_fusion_agent,
        policy_recommendation_agent,
        explainability_agent,
    ],
    model=model,
    prompt="",
    output_mode="last_message",
)

orchestrator = workflow.compile(
    checkpointer=MemorySaver()
)
