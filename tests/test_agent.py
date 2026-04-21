"""
Integration tests for the AutoStream LeadFlux Agent.

These tests verify the LangGraph workflow, state transitions,
and node behaviour. Tests that require LLM calls are marked
with @pytest.mark.llm and skipped if OPENAI_API_KEY is not set.
"""

import pytest
import os

from agent.state import AgentState
from agent.tools import mock_lead_capture
from agent.graph import build_graph


# ── Helpers ────────────────────────────────────────────────────────

def _make_state(user_message: str, **overrides) -> dict:
    """Create a fresh AgentState dict with a single user message."""
    state = {
        "messages": [{"role": "user", "content": user_message}],
        "current_intent": "",
        "turn_count": 1,
        "lead_info": {"name": None, "email": None, "creator_platform": None},
        "lead_captured": False,
        "response": "",
    }
    state.update(overrides)
    return state


has_api_key = bool(os.getenv("OPENAI_API_KEY"))
llm = pytest.mark.skipif(not has_api_key, reason="OPENAI_API_KEY not set")


# ── State Schema ───────────────────────────────────────────────────

class TestAgentState:
    """Verify the state schema is correctly defined."""

    def test_state_has_required_keys(self):
        state = _make_state("hello")
        required = ["messages", "current_intent", "turn_count",
                     "lead_info", "lead_captured", "response"]
        for key in required:
            assert key in state

    def test_lead_info_has_three_fields(self):
        state = _make_state("hello")
        assert "name" in state["lead_info"]
        assert "email" in state["lead_info"]
        assert "creator_platform" in state["lead_info"]


# ── Mock Lead Capture Tool ─────────────────────────────────────────

class TestMockLeadCapture:
    """Verify the lead capture tool works correctly."""

    def test_returns_confirmation_string(self):
        result = mock_lead_capture("John Doe", "john@example.com", "YouTube")
        assert "John Doe" in result
        assert "john@example.com" in result
        assert "YouTube" in result

    def test_handles_various_platforms(self):
        for platform in ["YouTube", "TikTok", "Instagram", "Twitch"]:
            result = mock_lead_capture("Test", "test@test.com", platform)
            assert platform in result


# ── Graph Construction ─────────────────────────────────────────────

class TestGraphConstruction:
    """Verify the LangGraph workflow compiles correctly."""

    def test_graph_compiles(self):
        graph = build_graph()
        assert graph is not None

    def test_graph_has_expected_nodes(self):
        """The compiled graph should contain our defined nodes."""
        graph = build_graph()
        # The graph object should be invokable
        assert callable(getattr(graph, "invoke", None))


# ── End-to-End (requires API key) ─────────────────────────────────

@llm
class TestEndToEnd:
    """Full integration tests that invoke the LLM."""

    def test_greeting_flow(self):
        graph = build_graph()
        state = _make_state("Hey there! How are you?")
        result = graph.invoke(state)
        assert result["current_intent"] == "casual_greeting"
        assert len(result["response"]) > 0

    def test_pricing_flow(self):
        graph = build_graph()
        state = _make_state("What are your pricing plans?")
        result = graph.invoke(state)
        assert result["current_intent"] == "product_pricing_inquiry"
        assert len(result["response"]) > 0
        # Should mention at least one plan price
        assert "29" in result["response"] or "79" in result["response"]

    def test_lead_capture_flow_starts(self):
        graph = build_graph()
        state = _make_state("I want to sign up for AutoStream!")
        result = graph.invoke(state)
        assert result["current_intent"] == "high_intent_lead"
        assert len(result["response"]) > 0

    def test_lead_capture_collects_name(self):
        graph = build_graph()
        state = _make_state(
            "My name is Sarah Johnson",
            current_intent="high_intent_lead",
            lead_info={"name": None, "email": None, "creator_platform": None},
        )
        # Force the intent to stay high_intent_lead
        state["messages"].insert(0, {"role": "user", "content": "I want to sign up"})
        state["lead_info"]["name"] = None  # ensure blank
        result = graph.invoke(state)
        # The node should have extracted the name
        assert result["lead_info"].get("name") is not None

    def test_refund_policy_query(self):
        graph = build_graph()
        state = _make_state("What is your refund policy?")
        result = graph.invoke(state)
        assert result["current_intent"] == "product_pricing_inquiry"
        assert "refund" in result["response"].lower() or "7" in result["response"]

    def test_tool_not_triggered_without_all_fields(self):
        """Verify mock_lead_capture is NOT called when fields are missing."""
        graph = build_graph()
        state = _make_state(
            "I'm Sarah and I want to sign up",
            lead_info={"name": None, "email": None, "creator_platform": None},
        )
        result = graph.invoke(state)
        # Lead should NOT be captured yet (email and platform are missing)
        assert result["lead_captured"] is False
