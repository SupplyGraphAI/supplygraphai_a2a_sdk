
# SupplyGraph AI – A2A Python SDK (Developer Lite Guide)

## 1. Initialize Client

```python
from supplygraphai_a2a_sdk import AgentClient

client = AgentClient(
    api_key="YOUR_API_KEY",
    base_url="https://agent.supplygraph.ai/api/v1/agents"
)
```

---

## 2. High-Level Agent Wrapper (Recommended)

```python
from supplygraphai_a2a_sdk import USTariffCalculationAgent

agent = USTariffCalculationAgent(client)

resp = agent.run("Importing 100kg of ice cream from China")
print(resp)
```

---

## 3. A2A Response Structure (Simplified for Developers)

Every agent response follows this envelope:

```json
{
  "success": true,
  "code": "WAITING_USER",
  "message": "Please provide the country of origin.",
  "data": {
    "task_id": "tsk_xxx",
    "stage": "interpreting",
    "code": "WAITING_USER",
    "content": "Please specify the country."
  }
}
```

Developer essentials:

- `code` → **Primary state** (`WAITING_USER`, `TASK_ACCEPTED`, `TASK_RUNNING`, `TASK_COMPLETED`, etc.)
- `data.task_id` → Used to **continue the same task**
- `data.content` → Response content (text or structured JSON)
- `message` → Always safe to show to user

---

# 4. Multi-Step Workflow (Core Developer Logic)

A2A tasks often require:

- Initial run  
- Agent requests more info (`WAITING_USER`)  
- Continue with `task_id`  
- Agent accepts task (`TASK_ACCEPTED`)  
- Task runs (`TASK_RUNNING`)  
- Complete (`TASK_COMPLETED`) → call `results()`  

Here is the full recommended implementation:

```python
resp = agent.run("Import 100kg ice cream")
task_id = resp["data"]["task_id"]
code = resp["code"]

while True:

    # --- Interpreting Stage ---
    if code == "WAITING_USER":
        print(resp["message"])
        user_reply = input("> ")
        resp = agent.run(text=user_reply, task_id=task_id)
        code = resp["code"]
        continue

    if code == "INVALID_REQUEST":
        print("Invalid:", resp["message"])
        break

    if code == "UNAUTHORIZED":
        print("API key invalid.")
        break

    # --- Executing Stage ---
    if code == "TASK_ACCEPTED":
        resp = agent.status(task_id)
        code = resp["code"]
        continue

    if code == "TASK_RUNNING":
        import time; time.sleep(1)
        resp = agent.status(task_id)
        code = resp["code"]
        continue

    # --- Completed Stage ---
    if code == "TASK_COMPLETED":
        result = agent.results(task_id)
        print("Final:", result["data"]["content"])
        break

    if code == "TASK_FAILED":
        print("Task failed:", resp["message"])
        break
```

---

# 5. Handling `data.content` (Text & Structured JSON)

```python
content = resp["data"]["content"]

if isinstance(content, str):
    print("Text:", content)

elif isinstance(content, dict) and content.get("type") == "result":
    print("Structured:", content["data"])
```

---

# 6. Streaming Mode (THINKING events)

SSE frames:

```json
{
  "event": "stream",
  "data": {
    "code": "THINKING",
    "reasoning": ["..."]
  }
}
```

Developer usage:

```python
events = agent.run("Import 100kg citrus", stream=True)

for ev in events:
    for r in ev["data"]["reasoning"]:
        print("> ", r)
```

---

# 7. Fetching Manifest

```python
manifest = client.manifest("tariff_classification")
print(manifest["pricing"])
print(manifest["input_schema"])
```

---

# 8. Custom Agent Wrapper

```python
from supplygraphai_a2a_sdk.client.base_agent import BaseAgent

class MyCustomAgent(BaseAgent):
    def __init__(self, client):
        super().__init__(client, agent_id="my_custom_agent")

agent = MyCustomAgent(client)
print(agent.run("Hello"))
```

---

# 9. Adapter Ecosystem (Quick Reference)

The SDK includes first-class adapters for popular agent and tooling ecosystems.
These adapters are **optional** and only needed when you integrate with a specific framework.

Supported ecosystems include (non-exhaustive):
- [**Google A2A / Gemini Agents**](./docs/adapters/google_a2a_adapter.md)
- **LangGraph / LangChain**
- **Semantic Kernel**
- **CrewAI**
- **DSPy**
- **Flowise**
- **LlamaIndex**
- **MCP (ChatGPT, Cursor, Zed, etc.)**
- **BentoML**
- **Haystack**

Each adapter:

- Wraps a SupplyGraph A2A Agent as a native tool / node / skill / runner
- Has **no hard dependency** inside the SDK (you install the framework in your own project)
- Uses the same A2A lifecycle: `run → status → results` with `task_id` and streaming support

Adapter-specific usage examples and best practices are provided in the dedicated docs
(e.g. `docs/adapters/langgraph.md`, `docs/adapters/crewai.md`, etc.).

