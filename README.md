# AutoStream LeadFlux: AI Sales Agent

AutoStream LeadFlux is a production-grade conversational AI agent designed to automate lead generation and product inquiries for video creators. Built with **LangGraph** and **Streamlit**, it features a robust RAG (Retrieval-Augmented Generation) system and multi-turn state management.

---

## 🚀 How to Run Locally

### 1. Prerequisites
- Python 3.10+
- OpenAI, Anthropic, or Google Gemini API Key

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/suryansh0512/LeadFlux-.git
cd LeadFlux-

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and add your API key (OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY)
```

### 3. Launch
- **Web Interface (Recommended)**:
  ```bash
  streamlit run app.py
  ```
- **CLI Interface**:
  ```bash
  python main.py
  ```

---

## 🏗️ Architecture Explanation

### Why LangGraph?
We chose **LangGraph** over simpler frameworks like AutoGen or basic chains because of its focus on **controllable, cyclic workflows**. Lead capture and sales inquiries are rarely linear; they require loops (e.g., asking for missing fields until complete) and precise routing. LangGraph allows us to define the agent as a state machine where nodes represent logical steps (classification, retrieval, extraction) and edges define the conditional transitions. This ensures the agent doesn't "hallucinate" its way out of the sales funnel and follows a predictable business logic.

### State Management
State is managed using a centralized **AgentState** schema (built on Python's `TypedDict`). This state acts as the "single source of truth" that persists throughout the conversation. It tracks:
- **Messages**: The full conversation history.
- **Intent**: The current classification (Greeting, Inquiry, or Lead).
- **Lead Info**: A structured dictionary (Name, Email, Platform) that is updated incrementally across turns.
- **Metadata**: Flags like `lead_captured` to trigger backend tools only when conditions are met.
Each node in the graph receives this state, performs a specific transformation, and returns only the fields it modified, ensuring clean and traceable data flow.

---

## 💬 WhatsApp Deployment (Webhooks)

To integrate this agent with WhatsApp, we would use a **Webhook-based architecture** using the **Meta WhatsApp Business API** or **Twilio**.

### Integration Workflow:
1.  **Incoming Message**: A user sends a message on WhatsApp.
2.  **Webhook Trigger**: WhatsApp/Twilio sends an HTTP POST request (Webhook) to our backend server (e.g., a FastAPI or Flask app).
3.  **Agent Processing**: The backend extracts the text, identifies the user's `From` number (as a unique session ID), and invokes the **LangGraph Agent** with the existing state for that ID.
4.  **Response Generation**: The agent retrieves data from the knowledge base or extracts lead info and returns a structured response.
5.  **Outgoing Message**: The backend uses the WhatsApp API to send the generated response back to the user's phone number.
6.  **Persistence**: The conversation state is stored in a database (like PostgreSQL or Redis) between messages to maintain context across the asynchronous webhook calls.

---

## 🛠️ Tech Stack
- **Framework**: LangGraph (LangChain)
- **UI**: Streamlit
- **LLMs**: GPT-4o-mini / Claude 3.5 Sonnet / Gemini 1.5 Flash
- **Database**: Local JSON Knowledge Base (RAG)
- **DevOps**: Docker
