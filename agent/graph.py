"""
LangGraph workflow definition for the AutoStream LeadFlux Agent.

Builds a state machine with nodes for intent classification, greeting,
RAG-powered product responses, and lead capture. Routing is handled
by a conditional edge after the classify_intent node.
"""

from langgraph.graph import StateGraph, END

from agent.state import AgentState
from agent.nodes import (
    classify_intent,
    greeting_node,
    rag_node,
    lead_capture_node,
)


def _route_by_intent(state: AgentState) -> str:
    """
    Conditional edge: route to the appropriate handler based on
    the classified intent.
    """
    intent = state.get("current_intent", "casual_greeting")

    routing = {
        "casual_greeting": "greeting_node",
        "product_pricing_inquiry": "rag_node",
        "high_intent_lead": "lead_capture_node",
    }
    return routing.get(intent, "greeting_node")


def build_graph() -> StateGraph:
    """
    Construct and compile the LangGraph workflow.

    Graph topology:
        START → classify_intent → (conditional) → greeting_node  → END
                                                 → rag_node       → END
                                                 → lead_capture   → END
    """
    workflow = StateGraph(AgentState)

    # ── Add nodes ──────────────────────────────────────────────────
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("greeting_node", greeting_node)
    workflow.add_node("rag_node", rag_node)
    workflow.add_node("lead_capture_node", lead_capture_node)

    # ── Entry point ────────────────────────────────────────────────
    workflow.set_entry_point("classify_intent")

    # ── Conditional routing ────────────────────────────────────────
    workflow.add_conditional_edges(
        "classify_intent",
        _route_by_intent,
        {
            "greeting_node": "greeting_node",
            "rag_node": "rag_node",
            "lead_capture_node": "lead_capture_node",
        },
    )

    # ── Terminal edges ─────────────────────────────────────────────
    workflow.add_edge("greeting_node", END)
    workflow.add_edge("rag_node", END)
    workflow.add_edge("lead_capture_node", END)

    return workflow.compile()


# Pre-built graph instance for convenience
agent_graph = build_graph()
