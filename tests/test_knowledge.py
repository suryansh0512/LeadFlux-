"""
Tests for the knowledge base and retriever module.

These tests verify the local RAG pipeline works correctly
without requiring any API keys or LLM calls.
"""

import pytest
import json
import os

from knowledge.retriever import (
    _load_knowledge_base,
    _flatten_kb_to_chunks,
    retrieve,
    get_full_knowledge_base_summary,
)


# ── Knowledge Base Loading ─────────────────────────────────────────

class TestKnowledgeBaseLoading:
    """Verify the JSON knowledge base loads and has expected structure."""

    def test_loads_without_error(self):
        kb = _load_knowledge_base()
        assert isinstance(kb, dict)

    def test_has_product_section(self):
        kb = _load_knowledge_base()
        assert "product" in kb
        assert kb["product"]["name"] == "AutoStream"

    def test_has_plans(self):
        kb = _load_knowledge_base()
        assert "plans" in kb
        assert len(kb["plans"]) == 2

    def test_plan_names(self):
        kb = _load_knowledge_base()
        plan_names = [p["name"] for p in kb["plans"]]
        assert "Basic Plan" in plan_names
        assert "Pro Plan" in plan_names

    def test_has_policies(self):
        kb = _load_knowledge_base()
        assert "policies" in kb
        for key in ("refund", "support", "trial", "cancellation"):
            assert key in kb["policies"]

    def test_has_faq(self):
        kb = _load_knowledge_base()
        assert "faq" in kb
        assert len(kb["faq"]) >= 3

    def test_each_plan_has_price_and_features(self):
        kb = _load_knowledge_base()
        for plan in kb["plans"]:
            assert "price" in plan, f"{plan['name']} missing price"
            assert "features" in plan, f"{plan['name']} missing features"
            assert len(plan["features"]) > 0


# ── Chunk Flattening ───────────────────────────────────────────────

class TestChunkFlattening:
    """Verify the knowledge base is correctly flattened into chunks."""

    def test_returns_list_of_dicts(self):
        kb = _load_knowledge_base()
        chunks = _flatten_kb_to_chunks(kb)
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        for chunk in chunks:
            assert "topic" in chunk
            assert "content" in chunk

    def test_includes_product_overview(self):
        kb = _load_knowledge_base()
        chunks = _flatten_kb_to_chunks(kb)
        topics = [c["topic"] for c in chunks]
        assert "product_overview" in topics

    def test_includes_plans(self):
        kb = _load_knowledge_base()
        chunks = _flatten_kb_to_chunks(kb)
        topics = [c["topic"] for c in chunks]
        assert any("plan" in t for t in topics)

    def test_includes_policies(self):
        kb = _load_knowledge_base()
        chunks = _flatten_kb_to_chunks(kb)
        topics = [c["topic"] for c in chunks]
        assert "refund_policy" in topics
        assert "support_policy" in topics

    def test_includes_faq(self):
        kb = _load_knowledge_base()
        chunks = _flatten_kb_to_chunks(kb)
        faq_chunks = [c for c in chunks if c["topic"] == "faq"]
        assert len(faq_chunks) >= 3


# ── Retrieval ──────────────────────────────────────────────────────

class TestRetrieval:
    """Verify keyword-based retrieval returns relevant results."""

    def test_pricing_query_returns_plan_info(self):
        result = retrieve("What is the pricing?")
        assert "29" in result or "79" in result  # plan prices

    def test_refund_query_returns_policy(self):
        result = retrieve("What is your refund policy?")
        assert "refund" in result.lower()
        assert "7 day" in result.lower() or "7-day" in result.lower()

    def test_empty_query_returns_something(self):
        result = retrieve("")
        assert isinstance(result, str)

    def test_irrelevant_query_returns_graceful_fallback(self):
        result = retrieve("quantum physics dark matter")
        # Should either return best-effort results or the fallback message
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_query_returns_video_info(self):
        result = retrieve("What video formats are supported?")
        assert "mp4" in result.lower() or "mov" in result.lower()

    def test_top_k_limits_results(self):
        result = retrieve("AutoStream plan features pricing", top_k=1)
        # With top_k=1, should return fewer sections
        assert isinstance(result, str)

    def test_youtube_integration_query(self):
        result = retrieve("Does it work with YouTube?")
        assert "youtube" in result.lower()


# ── Full Summary ───────────────────────────────────────────────────

class TestFullSummary:
    """Verify the full knowledge base summary generation."""

    def test_returns_nonempty_string(self):
        summary = get_full_knowledge_base_summary()
        assert isinstance(summary, str)
        assert len(summary) > 100

    def test_contains_all_sections(self):
        summary = get_full_knowledge_base_summary()
        assert "product_overview" in summary
        assert "refund_policy" in summary
        assert "faq" in summary
