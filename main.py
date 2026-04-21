"""
AutoStream LeadFlux — CLI Chat Interface

Entry point for the conversational AI agent. Runs an interactive
loop in the terminal, passing user messages through the LangGraph
workflow and printing the agent's responses.
"""

import sys
from agent.graph import agent_graph
from config.settings import PRODUCT_NAME, COMPANY_TAGLINE, MAX_CONVERSATION_TURNS


BANNER = f"""
--------------------------------------------------------------
   {PRODUCT_NAME} LeadFlux -- AI Sales Agent
   {COMPANY_TAGLINE}
--------------------------------------------------------------
   Type your message and press Enter.
   Type 'quit' or 'exit' to end the conversation.
--------------------------------------------------------------
"""


def run_chat():
    """Run the interactive chat loop."""
    print(BANNER)

    # Initialise conversation state
    state = {
        "messages": [],
        "current_intent": "",
        "turn_count": 0,
        "lead_info": {"name": None, "email": None, "creator_platform": None},
        "lead_captured": False,
        "response": "",
    }

    while state["turn_count"] < MAX_CONVERSATION_TURNS:
        # Get user input
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye! 👋")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "bye", "q"):
            print("\nAutoStream Agent: Thanks for chatting! Have a great day! 🎬✨\n")
            break

        # Add user message to history
        state["messages"].append({"role": "user", "content": user_input})
        state["turn_count"] += 1

        # Run the graph
        try:
            result = agent_graph.invoke(state)
        except Exception as e:
            print(f"\n⚠️  Error: {e}")
            print("Please make sure your OPENAI_API_KEY is set in .env\n")
            continue

        # Update state with graph output
        state["current_intent"] = result.get("current_intent", state["current_intent"])
        state["lead_info"] = result.get("lead_info", state["lead_info"])
        state["lead_captured"] = result.get("lead_captured", state["lead_captured"])
        response = result.get("response", "I'm sorry, I didn't catch that.")
        state["response"] = response

        # Add assistant response to history
        state["messages"].append({"role": "assistant", "content": response})

        # Display
        print(f"\nAutoStream Agent: {response}\n")

        # If lead was just captured, congratulate and offer to continue
        if state["lead_captured"]:
            print("─" * 50)
            print("✅ Lead capture complete! The conversation can continue.")
            print("─" * 50 + "\n")
            # Reset lead state for potential new conversation
            state["lead_captured"] = False
            state["lead_info"] = {"name": None, "email": None, "creator_platform": None}

    if state["turn_count"] >= MAX_CONVERSATION_TURNS:
        print("\n📋 Maximum conversation turns reached. Thanks for chatting!\n")


if __name__ == "__main__":
    run_chat()
