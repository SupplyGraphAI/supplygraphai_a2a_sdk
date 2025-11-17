# Flowise Adapter Documentation

## Overview
The `FlowiseToolWrapper` adapts a SupplyGraph A2A agent for direct use inside **Flowise Custom Tool Nodes**.

It provides:
- A Flowise-compatible metadata schema
- A unified `call()` handler for `run`, `status`, and `results`
- Support for multi‑round workflows using `task_id`
- Access to the agent manifest for dynamic schema generation


## Class: `FlowiseToolWrapper`

### Initialization
```python
tool = FlowiseToolWrapper(
    agent_id="tariff_calc",
    api_key="sk-...",
)
```

Arguments:

| Field | Type | Description |
|-------|------|-------------|
| `agent_id` | str | SupplyGraph Agent ID |
| `api_key` | str | API key |
| `base_url` | str | A2A gateway URL |


## Method: `tool_info()`

Returns Flowise metadata:

```json
{
  "name": "tariff_calc",
  "description": "...",
  "input_schema": {
    "type": "object",
    "properties": {
      "text": {"type": "string"},
      "mode": {"type": "string", "enum": ["run", "status", "results"]},
      "task_id": {"type": ["string", "null"]},
      "stream": {"type": "boolean"}
    },
    "required": ["mode"]
  }
}
```

Flowise uses this to display UI inputs automatically.


## Method: `call(args)`

Executes the agent.

### Supported modes

| mode | Behavior |
|------|----------|
| `"run"` | Creates or continues an A2A task |
| `"status"` | Polls a task |
| `"results"` | Fetches the final result |

### Example Flowise node execution:

```python
tool.call({
    "mode": "run",
    "text": "Import 50kg chocolate from BE",
    "task_id": None,
    "stream": False
})
```


## Factory: `create_flowise_tool()`

Recommended way to instantiate:

```python
from supplygraphai_a2a_sdk.adapters import create_flowise_tool

tool = create_flowise_tool("tariff_calc", api_key="sk-...")
```


## Multi‑Round Flow Example

```python
resp = tool.call({"mode": "run", "text": "Import EV motors"})

if resp["code"] == "WAITING_USER":
    tid = resp["data"]["task_id"]

    next_resp = tool.call({
        "mode": "run",
        "text": "Country: JP",
        "task_id": tid
    })
```


## Notes for Integrators

- This adapter does **not** import Flowise directly.
- Fully compatible with Flowise Custom Tool Nodes.
- All A2A behaviors are supported:
  - WAITING_USER
  - TASK_ACCEPTED
  - TASK_RUNNING
  - TASK_COMPLETED
  - streaming mode (generator)
