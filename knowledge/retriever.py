"""
Local RAG Retriever for the AutoStream knowledge base.

Uses keyword-based retrieval over the JSON knowledge base.
This avoids the need for an external vector store while still
providing relevant, grounded answers from local data.
"""

import json
import os
from typing import List, Dict, Any


_KB_PATH = os.path.join(os.path.dirname(__file__), "knowledge_base.json")


def _load_knowledge_base() -> Dict[str, Any]:
    """Load the JSON knowledge base from disk."""
    with open(_KB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _flatten_kb_to_chunks(kb: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Flatten the structured knowledge base into searchable text chunks.
    Each chunk has a 'topic' and 'content' field.
    """
    chunks: List[Dict[str, str]] = []

    # Product overview
    product = kb.get("product", {})
    chunks.append({
        "topic": "product_overview",
        "content": (
            f"{product.get('name', '')} - {product.get('tagline', '')}. "
            f"{product.get('description', '')}"
        ),
    })

    # Plans
    for plan in kb.get("plans", []):
        features = ", ".join(plan.get("features", []))
        chunks.append({
            "topic": f"plan_{plan['name'].lower().replace(' ', '_')}",
            "content": (
                f"{plan['name']} Pricing: {plan['price']}. "
                f"Features: {features}. "
                f"Best for: {plan.get('best_for', 'N/A')}."
            ),
        })

    # Policies
    policies = kb.get("policies", {})
    if "refund" in policies:
        chunks.append({
            "topic": "refund_policy",
            "content": f"Refund Policy: {policies['refund']}",
        })
    if "support" in policies:
        support = policies["support"]
        chunks.append({
            "topic": "support_policy",
            "content": (
                f"Support - Basic Plan: {support.get('basic', 'N/A')}. "
                f"Support - Pro Plan: {support.get('pro', 'N/A')}."
            ),
        })
    if "trial" in policies:
        chunks.append({
            "topic": "trial_policy",
            "content": f"Trial Policy: {policies['trial']}",
        })
    if "cancellation" in policies:
        chunks.append({
            "topic": "cancellation_policy",
            "content": f"Cancellation Policy: {policies['cancellation']}",
        })

    # FAQ
    for faq in kb.get("faq", []):
        chunks.append({
            "topic": "faq",
            "content": f"Q: {faq['question']} A: {faq['answer']}",
        })

    return chunks


def retrieve(query: str, top_k: int = 3) -> str:
    """
    Retrieve the most relevant knowledge base chunks for a given query.

    Uses simple keyword overlap scoring (TF-based).
    Returns a formatted string of the top-k most relevant chunks.

    Args:
        query: The user's question or message.
        top_k: Number of top results to return.

    Returns:
        A formatted string containing the most relevant knowledge.
    """
    kb = _load_knowledge_base()
    chunks = _flatten_kb_to_chunks(kb)

    # Tokenise and clean the query
    stop_words = {"what", "is", "the", "a", "an", "for", "of", "to", "in", "on", "at", "with", "about", "your", "does", "do"}
    
    def clean_tokens(text: str) -> set:
        # Lowercase and strip common punctuation
        cleaned = text.lower()
        for char in "?.,!:;()\"'":
            cleaned = cleaned.replace(char, " ")
        words = cleaned.split()
        return {w for w in words if w not in stop_words}

    query_tokens = clean_tokens(query)

    # Score each chunk by keyword overlap
    scored: List[tuple] = []
    for chunk in chunks:
        content_tokens = clean_tokens(chunk["content"])
        # Number of overlapping tokens
        overlap = len(query_tokens & content_tokens)
        if overlap > 0:
            # Score weighted by overlap and inverse chunk length to favor specific matches
            score = overlap / (len(content_tokens) ** 0.5)
            scored.append((score, chunk))

    # Sort by descending score
    scored.sort(key=lambda x: x[0], reverse=True)

    # Build context string from top-k results
    top_chunks = scored[:top_k]
    if not top_chunks:
        return "No relevant information found in the knowledge base."

    context_parts = []
    for _score, chunk in top_chunks:
        context_parts.append(f"[{chunk['topic']}]\n{chunk['content']}")

    return "\n\n".join(context_parts)


def get_full_knowledge_base_summary() -> str:
    """Return a complete summary of the knowledge base for system prompts."""
    kb = _load_knowledge_base()
    chunks = _flatten_kb_to_chunks(kb)
    return "\n\n".join(
        f"[{chunk['topic']}]\n{chunk['content']}" for chunk in chunks
    )
