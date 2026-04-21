# AutoStream LeadFlux — Demo Script

> **Duration**: 2–3 minutes  
> **Goal**: Show intent classification, RAG answers, and full lead capture flow.

---

## Setup (before demo)

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your API key
copy .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 4. Run the agent
python main.py
```

---

## Demo Flow

### 1. Casual Greeting (Intent: `casual_greeting`)

**You type:**
```
Hey there! What's up?
```

**Expected**: A friendly greeting that introduces AutoStream naturally.  
**What to highlight**: The agent classified this as a casual greeting and responded warmly without pushing product info.

---

### 2. Product Inquiry (Intent: `product_pricing_inquiry`)

**You type:**
```
What plans do you offer and how much do they cost?
```

**Expected**: The agent retrieves pricing from the knowledge base and presents the Basic ($29/mo) and Pro ($79/mo) plans with features.  
**What to highlight**: This answer is grounded in the local JSON knowledge base via RAG retrieval — the agent doesn't hallucinate.

---

### 3. Follow-up Policy Question (Intent: `product_pricing_inquiry`)

**You type:**
```
What if I don't like it? Can I get a refund?
```

**Expected**: The agent cites the 7-day refund policy from the knowledge base.  
**What to highlight**: Multi-turn context — the agent understands this is a follow-up.

---

### 4. High Intent — Start Lead Capture (Intent: `high_intent_lead`)

**You type:**
```
That sounds great, I'd like to sign up!
```

**Expected**: The agent detects purchase intent and begins collecting lead info. It asks for your **name** first.

---

### 5. Provide Name

**You type:**
```
I'm Alex Rivera
```

**Expected**: Agent acknowledges the name and asks for **email**.

---

### 6. Provide Email

**You type:**
```
alex@contentcreator.com
```

**Expected**: Agent acknowledges and asks for **platform**.

---

### 7. Provide Platform → Lead Captured!

**You type:**
```
I mainly create content on YouTube
```

**Expected**:
- Agent extracts "YouTube" as the platform
- `mock_lead_capture()` fires — you'll see the capture confirmation in the terminal
- Agent confirms all info and thanks the user

**What to highlight**: The tool was ONLY called after all 3 fields were collected. Show the printed capture output.

---

## Key Talking Points

1. **3-way intent classification** — casual, product/pricing, high-intent lead
2. **RAG grounding** — all product answers come from `knowledge_base.json`, not hallucinated
3. **Stateful multi-turn** — lead capture persists across turns, doesn't re-ask collected fields
4. **Tool gating** — `mock_lead_capture()` only fires when all fields are present
5. **Clean architecture** — nodes, state, prompts, and config are fully separated
6. **Easily swappable LLM** — change `MODEL_NAME` in `.env` to switch models
