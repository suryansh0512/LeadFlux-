# AutoStream LeadFlux

Conversational AI sales agent for **AutoStream** (automated video editing SaaS). Built with LangGraph + LangChain.

Classifies user intent, answers product questions from a local knowledge base (no hallucination), and runs a multi-turn lead capture flow with tool gating.

## Architecture

```
User Input → classify_intent → ┬─ casual_greeting    → friendly response
                                ├─ product_pricing    → RAG lookup → grounded answer
                                └─ high_intent_lead   → collect name/email/platform → mock_lead_capture()
```

The whole thing is a LangGraph state machine — each node gets the full conversation state, does its thing, and returns a partial update. Routing is a conditional edge off the classifier.

## Project Layout

```
├── main.py                  # CLI chat loop
├── agent/
│   ├── graph.py             # LangGraph workflow
│   ├── nodes.py             # classify, greet, rag, lead capture nodes
│   ├── state.py             # AgentState (TypedDict)
│   └── tools.py             # mock_lead_capture
├── knowledge/
│   ├── knowledge_base.json  # product data, plans, policies, FAQ
│   └── retriever.py         # keyword-based retriever
├── config/
│   └── settings.py          # model config, swappable via env vars
├── prompts/
│   └── templates.py         # all prompt templates in one place
├── tests/
│   ├── test_agent.py        # integration tests (needs API key)
│   └── test_knowledge.py    # retriever tests (no API key needed)
└── docs/
    ├── demo_script.md       # 2-3 min demo walkthrough
    └── sample_conversations.md
```

## Interface Options

The project now supports two interfaces:

1.  **CLI (Terminal)**: Best for quick tests and development.
    ```bash
    python main.py
    ```
2.  **Web UI (Streamlit)**: A premium, interview-ready chat interface.
    ```bash
    streamlit run app.py
    ```

## Hosting & Deployment

The project is ready for hosting on **Render**, **Railway**, or **Streamlit Cloud**.

### Deploy to Render (Recommended)
1.  Connect your GitHub repo to **Render**.
2.  Create a new **Web Service**.
3.  Set the build command to `pip install -r requirements.txt` and the start command to `streamlit run app.py`.
4.  Add your `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY`) to the environment variables.

### Deploy with Docker
The included `Dockerfile` allows for easy deployment on any container platform:
```bash
docker build -t autostream-agent .
docker run -p 8501:8501 --env-file .env autostream-agent
```

## Configuration

Set these in `.env` or export them:

| Variable | Default | What it does |
|---|---|---|
| `OPENAI_API_KEY` | — | Required |
| `MODEL_NAME` | `gpt-4o-mini` | Any OpenAI chat model |
| `MODEL_TEMPERATURE` | `0.3` | Lower = more deterministic |

## How the pieces fit together

**Intent classification** — Every user message hits a classifier prompt first. Three buckets: greeting, product question, or sign-up intent. If we're mid-lead-capture (some fields collected), we skip re-classification and stay in that flow.

**RAG retrieval** — Product answers come from `knowledge_base.json` via keyword overlap scoring. No vector DB, no embeddings. The retriever flattens the JSON into chunks, scores them against the query, and returns the top-k. Simple, transparent, easy to debug.

**Lead capture** — When the user shows purchase intent, we collect three fields across turns: name, email, platform. Each turn, an extraction prompt pulls whatever info is in the message. `mock_lead_capture()` only fires once all three are present — never prematurely.

## Tests

```bash
# These don't need an API key
pytest tests/test_knowledge.py -v

# These call the LLM
pytest tests/test_agent.py -v
```

## Design choices worth noting

- **LangGraph** over raw chains — explicit state machine, easier to reason about and debug
- **JSON knowledge base** — no external dependencies, fully auditable, easy to extend
- **Keyword retrieval** over embeddings — transparent scoring, easy to explain in a review
- **All prompts in one file** — `prompts/templates.py` makes it easy to review and tweak
- **Tool gating** — the capture tool is only called on completion, not on partial data
