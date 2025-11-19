# Haystack Adapter — SupplyGraph A2A SDK

## Overview

`SupplyGraphHaystackNode` provides a **Haystack-compatible node wrapper** for SupplyGraph A2A Agents.  
It avoids importing `haystack` directly, so the SDK does **not** introduce Haystack as a dependency.

You can integrate any SupplyGraph Agent into a Haystack pipeline by calling `sg_node.run()` inside your own node or function.


## Features

- ✔ Compatible with Haystack `Pipeline` and custom nodes  
- ✔ Supports A2A modes: `run`, `status`, `results`  
- ✔ Multiround workflows (`task_id`)  
- ✔ Streaming support (`stream=True` → SSE generator)  
- ✔ No dependency on Haystack inside the SDK  
- ✔ Simple factory `create_haystack_node`  


## Installation

```bash
pip install supplygraphai-a2a-sdk
```


## Importing

```python
from supplygraphai_a2a_sdk.adapters.haystack_adapter import (
    create_haystack_node,
    SupplyGraphHaystackNode
)
```


## Usage Example — As a Pipeline Node

```python
from haystack import Pipeline
from supplygraphai_a2a_sdk.adapters.haystack_adapter import create_haystack_node

# Create the wrapper
sg_node = create_haystack_node("tariff_calc", api_key="sk-...")

# Example pipeline
p = Pipeline()
p.add_node(component=sg_node.run, name="tariff_node", inputs=["Query"])

result = p.run(query="import 100kg ice cream from CN")
print(result)
```


## API Reference

### `class SupplyGraphHaystackNode`

#### **Constructor**
```
SupplyGraphHaystackNode(agent_id, api_key, base_url="")
```

| Parameter | Type | Description |
|----------|------|-------------|
| `agent_id` | str | The SupplyGraph agent ID |
| `api_key` | str | Your A2A API key |
| `base_url` | str | Custom A2A gateway URL (optional) |


### `run(query, mode="run", task_id=None, stream=False, **kwargs)`

Executes an A2A call following Haystack’s node conventions.

| Parameter | Type | Description |
|----------|------|-------------|
| `query` | str | Natural language input |
| `mode` | str | `"run"` / `"status"` / `"results"` |
| `task_id` | str? | For continuing multi-round tasks |
| `stream` | bool | If `True`, returns SSE generator |
| `kwargs` | any | Extra parameters passed to agent |

#### Returns

- A2A JSON envelope (normal modes)
- SSE generator (if `stream=True`)
- `{ "error": ... }` for invalid mode or missing arguments


## Example — Multi-round Workflow

```python
resp = sg_node.run(query="Import EV motor")

if resp["code"] == "WAITING_USER":
    task_id = resp["data"]["task_id"]
    resp2 = sg_node.run(
        query="China",
        mode="run",
        task_id=task_id
    )
```


## Factory Helper

### `create_haystack_node(agent_id, api_key, base_url)`

```python
sg_node = create_haystack_node("tariff_calc", api_key="sk-...")
```

Returns a ready-to-use `SupplyGraphHaystackNode`.
