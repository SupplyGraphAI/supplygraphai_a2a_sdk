# SupplyGraph AI — Examples

This directory contains **minimal runnable Python examples** demonstrating how to use the SupplyGraph AI A2A SDK.

These examples focus on **executable code**, not documentation.  
For complete developer documentation, please refer to the root `README.md`.


## How to Run

```bash
python examples/basic_run.py
python examples/openai_a2a_example.py
python examples/google_a2a_example.py
python examples/stream_reasoning.py
python examples/custom_agent_wrapper.py
```

Each script is fully self‑contained and can be executed directly.


## Included Examples

### 1. `basic_run.py`
A minimal example showing how to:
- initialize `AgentClient`
- call `agent.run()`
- print raw responses

### 2. `stream_reasoning.py`
Demonstrates:
- streaming mode (`stream=True`)
- converting internal thinking frames into streamed reasoning output

### 3. `openai_a2a_example.py`
Shows how to:
- initialize `OpenAIA2AAdapter`
- run/status/result
- stream OpenAI‑style event messages

### 4. `google_a2a_example.py`
Demonstrates integration with:
- Google‑style A2A RPC interface

### 5. `custom_agent_wrapper.py`
Shows how to:
- extend the SDK
- build a custom agent using `BaseAgent`


## Purpose of This Directory

The purpose of `examples/` is to provide:

- **minimal, runnable code**
- **practical demonstrations**
- **fast onboarding**

It intentionally avoids duplicating conceptual explanations that belong in the main SDK documentation.
