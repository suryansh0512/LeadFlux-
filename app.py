import streamlit as st
import os
from agent.graph import agent_graph
from config.settings import PRODUCT_NAME, COMPANY_TAGLINE, MAX_CONVERSATION_TURNS, MOCK_MODE, LLM_PROVIDER
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page Configuration
st.set_page_config(
    page_title=f"{PRODUCT_NAME} | AI Sales Agent",
    page_icon="✨",
    layout="centered"
)

# Custom CSS for 'Pro Creative Studio' Aesthetics
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Poppins:wght@400;600&display=swap');

    /* Global Overrides */
    .stApp {
        background: #0f172a; /* Deep Slate */
        color: #f8fafc;
        font-family: 'Outfit', sans-serif;
    }

    h1, h2, h3, b, strong {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    /* Sidebar - Ultra Dark */
    [data-testid="stSidebar"] {
        background-color: #020617 !important;
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
        background: linear-gradient(90deg, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Glassmorphism Chat Bubbles */
    .stChatMessage {
        background: rgba(30, 41, 59, 0.5) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        margin-bottom: 1.2rem !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* User Message - Indigo Accent */
    [data-testid="stChatMessageUser"] {
        border-right: 4px solid #6366f1 !important;
    }
    
    /* Assistant Message - Purple Accent */
    [data-testid="stChatMessageAssistant"] {
        border-left: 4px solid #a855f7 !important;
    }

    /* Chat Input */
    [data-testid="stChatInput"] {
        background-color: #1e293b !important;
        border-radius: 12px !important;
        border: 1px solid #334155 !important;
    }

    /* Button - Gradient Pro Look */
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.4);
    }

    /* Progress Indicators */
    .stInfo {
        background-color: rgba(99, 102, 241, 0.1) !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        color: #818cf8 !important;
    }
    .stSuccess {
        background-color: rgba(34, 197, 94, 0.1) !important;
        border: 1px solid rgba(34, 197, 94, 0.2) !important;
        color: #4ade80 !important;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0f172a;
    }
    ::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialise Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent_state" not in st.session_state:
    st.session_state.agent_state = {
        "messages": [],
        "current_intent": "",
        "turn_count": 0,
        "lead_info": {"name": None, "email": None, "creator_platform": None},
        "lead_captured": False,
        "response": "",
    }

# Sidebar Info
with st.sidebar:
    st.markdown(f"<h1 style='font-size: 2.5rem; background: linear-gradient(90deg, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>🎬 {PRODUCT_NAME}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-style: italic; color: #94a3b8;'>{COMPANY_TAGLINE}</p>", unsafe_allow_html=True)
    st.divider()
    
    st.subheader("System Status")
    mode_label = "🔴 Mock Mode (Active)" if MOCK_MODE else "🟢 Live AI (Active)"
    st.info(mode_label)
    st.caption(f"Provider: {LLM_PROVIDER.upper()}")
    
    st.divider()
    st.subheader("Lead Progress")
    lead_info = st.session_state.agent_state["lead_info"]
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("Name:")
        st.write("Email:")
        st.write("Platform:")
    with col2:
        st.write(f"**{lead_info.get('name') or '---'}**")
        st.write(f"**{lead_info.get('email') or '---'}**")
        st.write(f"**{lead_info.get('creator_platform') or '---'}**")
    
    if st.session_state.agent_state["lead_captured"]:
        st.success("🎯 Lead Captured!")
    
    st.divider()
    if st.button("Reset Conversation"):
        st.session_state.messages = []
        st.session_state.agent_state = {
            "messages": [],
            "current_intent": "",
            "turn_count": 0,
            "lead_info": {"name": None, "email": None, "creator_platform": None},
            "lead_captured": False,
            "response": "",
        }
        st.rerun()

# Main Header
st.title("Chat with AutoStream")
st.write("Ask about our plans, features, or sign up today!")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("How can I help you?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare state for LangGraph
    current_state = st.session_state.agent_state
    current_state["messages"].append({"role": "user", "content": prompt})
    current_state["turn_count"] += 1

    # Run the agent
    with st.spinner("Agent is thinking..."):
        try:
            result = agent_graph.invoke(current_state)
            
            # Update session state
            st.session_state.agent_state["current_intent"] = result.get("current_intent", current_state["current_intent"])
            st.session_state.agent_state["lead_info"] = result.get("lead_info", current_state["lead_info"])
            st.session_state.agent_state["lead_captured"] = result.get("lead_captured", current_state["lead_captured"])
            
            response = result.get("response", "I'm sorry, I encountered an issue.")
            st.session_state.agent_state["response"] = response
            
            # Add assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.agent_state["messages"].append({"role": "assistant", "content": response})
            
            with st.chat_message("assistant"):
                st.markdown(response)
                
            # If lead captured, show a celebration
            if st.session_state.agent_state["lead_captured"]:
                st.balloons()
                st.toast("Lead captured successfully!", icon="🎯")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
            if "api_key" in str(e).lower():
                st.warning("Please check your API key in the .env file or turn on MOCK_MODE.")
