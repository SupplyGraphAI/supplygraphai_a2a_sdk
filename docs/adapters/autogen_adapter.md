# AutoGen Adapter — SupplyGraph A2A SDK

## Overview
The **AutoGen Adapter** allows any SupplyGraph A2A Agent to be registered as a Tool inside the AutoGen multi‑agent framework.  
It exposes a minimal, clean interface that maps directly to AutoGen's expectations (`tool(input) -> result`).

This adapter supports:

- Single‑turn execution  
- Multi‑turn execution with `task_id`  
- Fully compatible with AutoGen’s `AssistantAgent` / `Tool` APIs  
- Zero dependency on AutoGen inside the SDK (host project imports AutoGen)

---

## Importing the Adapter

```python
from supplygraphai_a2a_sdk.adapters.autogen_adapter import AutoGenTool
```

---

## Creating an AutoGen Tool

```python
sg_tool = AutoGenTool(
    agent_id="tariff_calc",
    api_key="sk-...",
)
```

---

## Registering the Tool in AutoGen

```python
from autogen import AssistantAgent

assistant = AssistantAgent(
    name="assistant",
    tools=[sg_tool.to_autogen_tool()],
)
```

AutoGen will automatically use the tool when the model detects a call pattern matching the agent’s function.

---

## Running the Agent Through AutoGen

### Single‑turn
```python
assistant.run("Import 100kg ice cream from CN")
```

---

## Multi‑turn (task_id continuation)

```python
resp = sg_tool.run("Import 100kg motors from JP")
task_id = resp["data"]["task_id"]

# Continue task
resp2 = sg_tool.run(
    text="Country is Japan",
    task_id=task_id
)
```

---

## API Reference

### `AutoGenTool(agent_id, api_key, base_url)`
Creates a wrapper for a specific A2A agent.

### `.run(text, task_id=None, **kwargs)`
Runs the agent once.  
- `task_id` → continues multi‑round tasks  
- Returns A2A JSON response

### `.status(task_id)`
Queries task status.

### `.results(task_id)`
Fetches final results.

### `.to_autogen_tool()`
Returns a callable object suitable for AutoGen’s `Tool` API.

AutoGen will treat it like:

```python
def tool(text: str, **kwargs) -> Any:
    ...
```

---

## Example: Full Multi‑Agent Usage

```python
from autogen import AssistantAgent, UserProxyAgent
from supplygraphai_a2a_sdk.adapters.autogen_adapter import AutoGenTool

tool = AutoGenTool(agent_id="tariff_calc", api_key="sk-xxx")

assistant = AssistantAgent(
    name="assistant",
    tools=[tool.to_autogen_tool()],
)

user = UserProxyAgent(name="user")

assistant.initiate_chat(
    user,
    message="Help me calculate duties for importing 500kg milk powder from NZ."
)
```

---

## Notes

- Streaming is supported only at the agent level (`run(stream=True)`), but AutoGen currently does not natively stream tool calls.
- Error handling follows A2A unified structure.
- No AutoGen imports inside the SDK — avoids hard dependency.

---

## File Info
Adapter source file: `autogen_adapter.py`  
This documentation corresponds to the enhanced, manifest‑aware version of the adapter.

