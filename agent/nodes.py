"""
Graph nodes for the AutoStream LeadFlux Agent.

Each function is a LangGraph node that receives the full AgentState,
performs its logic, and returns a partial state update dict.
"""

from typing import Dict, Any, Optional, List
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from config.settings import MODEL_NAME, MODEL_TEMPERATURE, MOCK_MODE, LLM_PROVIDER, GOOGLE_API_KEY
from prompts.templates import (
    INTENT_CLASSIFICATION_PROMPT,
    GREETING_PROMPT,
    RAG_RESPONSE_PROMPT,
    LEAD_CAPTURE_PROMPT,
    FIELD_EXTRACTION_PROMPT,
)
from knowledge.retriever import retrieve
from agent.tools import mock_lead_capture
from agent.state import AgentState


def _get_llm() -> Any:
    """Initialise the LLM with project-level settings."""
    if LLM_PROVIDER == "anthropic":
        return ChatAnthropic(model=MODEL_NAME, temperature=MODEL_TEMPERATURE)
    elif LLM_PROVIDER == "google":
        return ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=MODEL_TEMPERATURE, google_api_key=GOOGLE_API_KEY)
    
    # Default to OpenAI
    return ChatOpenAI(model=MODEL_NAME, temperature=MODEL_TEMPERATURE)


def _format_history(messages: list) -> str:
    """Format message history into a readable string for prompt injection."""
    if not messages:
        return "(no prior conversation)"
    lines = []
    for msg in messages[-10:]:  # keep last 10 turns for context window
        role = msg.get("role", "unknown").capitalize()
        content = msg.get("content", "")
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


# ── Node 1: Intent Classification ──────────────────────────────────

def classify_intent(state: AgentState) -> Dict[str, Any]:
    """
    Classify the user's latest message into one of three intents.

    If we are in the middle of lead capture (some fields collected but
    not all), we keep the intent as 'high_intent_lead' to continue
    the capture flow without re-classifying.
    """
    messages = state.get("messages", [])
    lead_info = state.get("lead_info", {})
    lead_captured = state.get("lead_captured", False)

    # If already in lead capture flow and not yet complete, stay there
    is_already_capturing = state.get("current_intent") == "high_intent_lead"
    all_collected = all(
        lead_info.get(f) for f in ["name", "email", "creator_platform"]
    )

    if is_already_capturing and not all_collected and not lead_captured:
        return {"current_intent": "high_intent_lead"}

    # Extract latest message
    user_message = messages[-1]["content"] if messages else ""

    if MOCK_MODE:
        msg_lower = f" {user_message.lower()} "
        if any(f" {w} " in msg_lower for w in ["hi", "hello", "hey", "greeting"]):
            return {"current_intent": "casual_greeting"}
        if any(w in msg_lower for w in ["price", "plan", "cost", "feature", "refund", "faq", "format"]):
            return {"current_intent": "product_pricing_inquiry"}
        if any(w in msg_lower for w in ["sign up", "subscribe", "buy", "join", "start", "interested"]):
            return {"current_intent": "high_intent_lead"}
        return {"current_intent": "casual_greeting"}

    # Otherwise, classify with the LLM
    history_str = _format_history(messages[:-1])

    prompt = INTENT_CLASSIFICATION_PROMPT.format(
        history=history_str,
        user_message=user_message,
    )

    llm = _get_llm()
    result = llm.invoke([HumanMessage(content=prompt)])
    intent = result.content.strip().lower()

    # Validate — default to greeting if unrecognised
    valid_intents = {"casual_greeting", "product_pricing_inquiry", "high_intent_lead"}
    if intent not in valid_intents:
        intent = "casual_greeting"

    return {"current_intent": intent}


# ── Node 2: Greeting ──────────────────────────────────────────────

def greeting_node(state: AgentState) -> Dict[str, Any]:
    """Handle casual greetings and small talk."""
    if MOCK_MODE:
        return {"response": "Hi there! I'm the AutoStream assistant. I can help you with information about our video editing plans or help you get signed up. What's on your mind?"}

    messages = state.get("messages", [])
    user_message = messages[-1]["content"] if messages else ""
    history_str = _format_history(messages[:-1])

    prompt = GREETING_PROMPT.format(
        history=history_str,
        user_message=user_message,
    )

    llm = _get_llm()
    result = llm.invoke([HumanMessage(content=prompt)])

    return {"response": result.content.strip()}


# ── Node 3: RAG-Powered Product/Pricing ───────────────────────────

def rag_node(state: AgentState) -> Dict[str, Any]:
    """Answer product/pricing questions using the local knowledge base."""
    messages = state.get("messages", [])
    user_message = messages[-1]["content"] if messages else ""
    history_str = _format_history(messages[:-1])

    # Retrieve relevant context from the knowledge base
    context = retrieve(user_message, top_k=3)

    if MOCK_MODE:
        return {"response": f"Based on our knowledge base:\n\n{context}\n\nIs there anything else you'd like to know?"}

    prompt = RAG_RESPONSE_PROMPT.format(
        context=context,
        history=history_str,
        user_message=user_message,
    )

    llm = _get_llm()
    result = llm.invoke([HumanMessage(content=prompt)])

    return {"response": result.content.strip()}


# ── Node 4: Lead Capture ──────────────────────────────────────────

def _extract_fields(user_message: str, collected: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
    """Use the LLM to extract lead fields from the user's message."""
    if MOCK_MODE:
        extracted: Dict[str, Optional[str]] = {}
        msg = user_message.lower()
        print(f"DEBUG: Extracting from '{msg}'")
        
        # Simple heuristic for mock mode
        if "@" in msg and "." in msg:
            # Look for something that looks like an email
            parts = msg.split()
            for p in parts:
                if "@" in p:
                    extracted["email"] = p.strip(".,!")
        
        if any(p in msg for p in ["youtube", "tiktok", "instagram", "twitch"]):
            for p in ["youtube", "tiktok", "instagram", "twitch"]:
                if p in msg:
                    extracted["creator_platform"] = p.capitalize()
                    
        # If there's a name-like phrase or just a capitalized word that isn't a platform
        if "my name is" in msg:
            name_part = msg.split("my name is")[-1].strip()
            extracted["name"] = name_part.split(".")[0].strip().capitalize()
        elif not extracted.get("email") and not extracted.get("creator_platform") and len(user_message.split()) <= 3:
            # Assume short message is a name if no other field detected
            extracted["name"] = user_message.strip(".,!")
            
        return extracted

    collected_str = ", ".join(
        f"{k}={v}" for k, v in collected.items() if v
    ) or "none"

    prompt = FIELD_EXTRACTION_PROMPT.format(
        collected_fields=collected_str,
        user_message=user_message,
    )

    llm = _get_llm()
    result = llm.invoke([HumanMessage(content=prompt)])
    raw = result.content.strip()

    # Parse the structured output
    extracted: Dict[str, Optional[str]] = {}
    for line in raw.split("\n"):
        line = line.strip()
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip().lower()
            value = value.strip()
            if key in ("name", "email", "creator_platform") and value.lower() != "null":
                extracted[key] = value

    return extracted


def lead_capture_node(state: AgentState) -> Dict[str, Any]:
    """
    Collect lead information (name, email, platform) across turns.

    When all three fields are collected, calls mock_lead_capture()
    and marks the lead as captured.
    """
    messages = state.get("messages", [])
    lead_info = state.get("lead_info", {
        "name": None, "email": None, "creator_platform": None
    })
    user_message = messages[-1]["content"] if messages else ""
    history_str = _format_history(messages[:-1])

    # Extract any new fields from the current message
    new_fields = _extract_fields(user_message, lead_info)
    for field, value in new_fields.items():
        if value and not lead_info.get(field):
            lead_info[field] = value

    # Check completion
    all_collected = all(
        lead_info.get(f) for f in ["name", "email", "creator_platform"]
    )

    lead_captured = False
    if all_collected:
        # Fire the lead capture tool
        mock_lead_capture(
            name=lead_info["name"],
            email=lead_info["email"],
            platform=lead_info["creator_platform"],
        )
        lead_captured = True

    if MOCK_MODE:
        if not lead_info.get("name"):
            resp = "I'd love to help you sign up! First, could you tell me your full name?"
        elif not lead_info.get("email"):
            resp = f"Thanks {lead_info['name']}! And what's your email address?"
        elif not lead_info.get("creator_platform"):
            resp = "Got it. Finally, which platform do you primarily create content for (YouTube, TikTok, etc.)?"
        else:
            resp = f"Awesome! I've captured your details. Our team will reach out to {lead_info['email']} soon. Welcome to AutoStream!"
        return {
            "response": resp,
            "lead_info": lead_info,
            "lead_captured": lead_captured,
        }

    # Build the response prompt
    collected_str = "\n".join(
        f"  - {k}: {v}" for k, v in lead_info.items() if v
    ) or "  (none yet)"

    missing_fields = [
        k for k in ["name", "email", "creator_platform"] if not lead_info.get(k)
    ]
    missing_str = ", ".join(missing_fields) if missing_fields else "ALL COLLECTED"

    prompt = LEAD_CAPTURE_PROMPT.format(
        collected_fields=collected_str,
        missing_fields=missing_str,
        history=history_str,
        user_message=user_message,
    )

    llm = _get_llm()
    result = llm.invoke([HumanMessage(content=prompt)])

    return {
        "response": result.content.strip(),
        "lead_info": lead_info,
        "lead_captured": lead_captured,
    }
