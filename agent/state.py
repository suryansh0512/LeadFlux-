"""
State schema for the AutoStream LeadFlux Agent.

Defines the conversation state that flows through every node
in the LangGraph workflow. Uses TypedDict for LangGraph compatibility.
"""

from typing import TypedDict, Optional, List, Dict, Any


class AgentState(TypedDict):
    """
    Conversation state managed across multi-turn interactions.

    Attributes:
        messages: List of (role, content) tuples tracking conversation history.
        current_intent: The classified intent for the current turn.
        turn_count: Number of conversation turns completed.
        lead_info: Dict tracking collected lead fields (name, email, creator_platform).
        lead_captured: Whether the lead has been successfully captured.
        response: The agent's response for the current turn.
    """
    messages: List[Dict[str, str]]
    current_intent: str
    turn_count: int
    lead_info: Dict[str, Optional[str]]
    lead_captured: bool
    response: str
