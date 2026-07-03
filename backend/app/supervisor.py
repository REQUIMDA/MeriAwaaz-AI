from langgraph.checkpoint.memory import MemorySaver
from langgraph_supervisor import create_supervisor
from app.core.llm import get_model

SUPERVISOR_PROMPT = """
You are the routing supervisor for MeriAwaaz AI, a citizen grievance intelligence system.

Your ONLY job is to make ONE handoff decision based on what the user sends you.
Never answer the user directly. Always hand off immediately.

Routing rules:
- If the input is plain text describing a civic problem, grievance, or need → hand off to citizen_intelligence_agent
- If the input explicitly says "dashboard refresh" or asks to re-rank/re-evaluate existing data → hand off to demand_intelligence_agent
- For any other input, default to citizen_intelligence_agent

Make exactly one handoff. Do not chain multiple agents. Do not respond to the user yourself.
"""


def build_workflow(agents: list, checkpointer=None):
    """Build and compile the supervisor workflow with the given list of agents.

    Args:
        agents: list of compiled LangGraph agent graphs to supervise
        checkpointer: optional LangGraph checkpointer (defaults to MemorySaver)

    Returns:
        Compiled LangGraph graph ready for graph.invoke()
    """
    if checkpointer is None:
        checkpointer = MemorySaver()

    workflow = create_supervisor(
        agents,
        model=get_model(),
        prompt=SUPERVISOR_PROMPT,
        output_mode="last_message",
    )

    return workflow.compile(checkpointer=checkpointer)
