# OpenAI A2A Adapter for SupplyGraph Agents

The **OpenAI A2A Adapter** provides a fully unified interface that allows any
SupplyGraph A2A Agent to be used as if it were an **OpenAI Agent Runtime**
endpoint.

This adapter transforms native SupplyGraph A2A responses into OpenAI-compatible
objects:

- `agent.run`
- `agent.run.status`
- `agent.run.result`
- `agent.error`
- `step` and `done` SSE events for reasoning streams

It allows developers to integrate SupplyGraph A2A Agents using the same
interaction patterns used for OpenAI Agents—ideal for multi-agent frameworks,
agent pipelines, or custom business logic.

---

## 🚀 Features

- **OpenAI-compatible Run API**
  - `run()`, `status()`, `result()`
  - Consistent OpenAI-style envelopes and field names  

- **Full Support for SupplyGraph Multi-Stage Lifecycle**
  - interpreting → executing → completed / failed / cancelled  
  - automatic mapping into `in_progress`, `requires_action`, etc.

- **Streaming (SSE) Reasoning**
  - Converts SupplyGraph THINKING / reasoning frames into:
    - `event: step`
    - `event: done`

- **Error Model Standardization**
  - Unifies SupplyGraph error codes into OpenAI-style:
    - `invalid_request_error`
    - `authentication_error`
    - `payment_required_error`
    - `server_error`
    - `rate_limit_error`

- **Multi-Round Continuation Support**
  - Use the same `task_id` to continue a partially completed task.

- **Drop-in Compatible**
  - Works with LangChain, LangGraph, AutoGen, CrewAI, DSPy, Semantic Kernel,
    and any framework expecting OpenAI-like run/stream patterns.

---

## 📦 Installation

```bash
pip install supplygraphai-a2a-sdk
```

## Import and Initialize
```python
from supplygraphai_a2a_sdk.adapters.openai_a2a_adapter import (
    OpenAIA2AAdapter,
)

adapter = OpenAIA2AAdapter(
    api_key="YOUR_API_KEY",
    base_url="https://agent.supplygraph.ai/api/v1/agents",
)
```

### 1. Fetching the Manifest
```python
manifest = adapter.manifest("tariff_calc")
print(manifest)
```
Returns an OpenAI-style manifest:
```json
{
  "object": "agent",
  "id": "tariff_calc",
  "name": "...",
  "capabilities": {
    "run": true,
    "status": true,
    "results": true,
    "streaming": true
  },
  "input_schema": {...},
  "output_schema": {...},
  "reasoning_schema": {...},
  "pricing": {...},
  "metadata": {...},
  "extended": {...}
}
```

### 2. Running a Task (Non-Streaming)
```python
run = adapter.run(
    "tariff_calc",
    text="Calculate import duty for 100kg ice cream from CN.",
)
print(run)
```
Example OpenAI-style response:
```json
{
  "object": "agent.run",
  "id": "t_123",
  "status": "in_progress",
  "input": {"text": "..."},
  "metadata": {
    "stage": "executing",
    "code": "TASK_ACCEPTED"
  }
}
```

### 3. Handling `requires_action`
If an agent needs more user input, the adapter returns:
```json
{ "status": "requires_action" }
```
Example continuation:
```python
if run["status"] == "requires_action":
    run = adapter.run(
        "tariff_calc",
        text="Country of origin is China.",
        task_id=run["id"],
    )
```
No need to specify `mode="run"`—the adapter manages the lifecycle.

### 4. Polling Status
```python
status = adapter.status("tariff_calc", run["id"])
print(status)
```
Example:
```json
{
  "object": "agent.run.status",
  "id": "t_123",
  "status": "in_progress",
  "steps": [...],
  "metadata": {
    "stage": "executing",
    "progress": 55
  }
}
```

### 5. Fetching Final Results
```python
result = adapter.result("tariff_calc", run["id"])
print(result)
```

Example:
```json
{
  "object": "agent.run.result",
  "id": "t_123",
  "status": "completed",
  "output_type": "json",
  "output_json": {
    "calculation_result": "..."
  }
}
```

### 6. Streaming (SSE) Example
```python
stream = adapter.stream(
    "tariff_calc",
    text="Stream reasoning for tariff calculation."
)

for frame in stream:
    print(frame, end="", flush=True)
```

Emits:
```csharp
event: step
data: {"type":"reasoning","content":"Analyzing input..."}

event: step
data: {"type":"reasoning","content":"Identifying tariff provisions..."}

event: done
data: {"message":"stream completed"}
```

### 7. Error Handling
```python
try:
    resp = adapter.run("tariff_calc", text="")
except Exception as e:
    print(e)
```

OpenAI-style error:
```python
{
  "object": "agent.error",
  "type": "invalid_request_error",
  "code": "INVALID_REQUEST",
  "message": "Input not valid."
}
```

### 8. Task Resume (Optional)
If the agent supports supports_resume:
```python
resumed = adapter.run(
    "tariff_calc",
    text="Resume with updated merchandise value = 500.",
    task_id="t_123",
)
```

### 9. End-to-End Workflow Example
```python
from supplygraphai_a2a_sdk.adapters.openai_a2a_adapter import OpenAIA2AAdapter
import time

adapter = OpenAIA2AAdapter(api_key="YOUR_KEY")

# Start
run = adapter.run("tariff_calc", text="Calculate duty for 100kg ice cream from CN.")
print(run)

# Continue if required
if run["status"] == "requires_action":
    run = adapter.run("tariff_calc", text="Country is CN.", task_id=run["id"])

# Poll
while True:
    status = adapter.status("tariff_calc", run["id"])
    print(status)
    if status["status"] in ("completed", "failed"):
        break
    time.sleep(1)

# Final output
result = adapter.result("tariff_calc", run["id"])
print(result)
```

## Testing
Each adapter component has dedicated test files:
```bash
tests/openai_a2a/
    test_error_adapter.py
    test_sse_adapter.py
    test_run_adapter.py
    test_status_adapter.py
    test_results_adapter.py
    test_openai_adapter.py
```

Run:
```bash
pytest -q
```

## License
SupplyGraph AI Commercial License — see repository license file.

## Support
For questions or integration help:
- GitHub Issues
- SupplyGraph AI support (Enterprise customers)