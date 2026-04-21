"""
Configuration settings for the AutoStream LeadFlux Agent.

Centralizes model selection and parameters for easy swapping.
To change the LLM, simply update MODEL_NAME below or set
the MODEL_NAME environment variable.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM Configuration ──────────────────────────────────────────────
# Swap models by changing MODEL_NAME. Supported: any OpenAI chat model.
# Examples OpenAI: "gpt-4o-mini", "gpt-4o"
# Examples Anthropic: "claude-3-5-sonnet-20240620"
# Examples Google: "gemini-1.5-pro", "gemini-1.5-flash"
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai").lower()

def _get_default_model(provider: str) -> str:
    if provider == "google": return "gemini-1.5-flash"
    if provider == "anthropic": return "claude-3-5-sonnet-20240620"
    return "gpt-4o-mini"

MODEL_NAME: str = os.getenv("MODEL_NAME", _get_default_model(LLM_PROVIDER))
MODEL_TEMPERATURE: float = float(os.getenv("MODEL_TEMPERATURE", "0.3"))

# ── API Keys ────────────────────────────────────────────────────────
def _get_secret(key: str, default: str = "") -> str:
    # Try environment variable first
    val = os.getenv(key)
    if val: return val
    
    # Try Streamlit Secrets as fallback
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return default

OPENAI_API_KEY: str = _get_secret("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY: str = _get_secret("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY: str = _get_secret("GOOGLE_API_KEY", "")

# ── Developer Mock Mode ──────────────────────────────────────────
# Set to True to run the agent without calling OpenAI (uses rule-based logic).
MOCK_MODE: bool = _get_secret("MOCK_MODE", "false").lower() == "true"

# ── Agent Behaviour ────────────────────────────────────────────────
MAX_CONVERSATION_TURNS: int = 10
PRODUCT_NAME: str = "AutoStream"
COMPANY_TAGLINE: str = "Automated Video Editing Tools for Content Creators"
