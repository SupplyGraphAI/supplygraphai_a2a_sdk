# Google A2A Adapter

## Overview
The `GoogleA2AAdapter` enables SupplyGraph A2A agents to be used with **Google-style A2A RPC (task.run / task.status / task.results)**.  
It converts RPC-style JSON calls into actual SupplyGraph REST operations.


## Class: `GoogleA2AAdapter`

### Initialization
```python
adapter = GoogleA2AAdapter(
    api_key="YOUR_KEY",
    base_url="https://agent.supplygraph.ai/api/v1/agents"
)
```


## RPC Entry Point

### `call(method: str, params: dict) -> dict`

Supported methods:

| RPC Method | Maps To |
|-----------|---------|
| `a2a.task.run` / `task.run` | `AgentClient.run()` |
| `a2a.task.status` / `task.status` | `AgentClient.status()` |
| `a2a.task.results` / `task.results` | `AgentClient.results()` |

Example:
```python
adapter.call("a2a.task.run", {
    "agent": "tariff_calc",
    "input": "import 100kg citrus",
})
```


## Behavior Summary

### ✔ `task.run`
Input fields:
- `text` or `input`
- `task_id` (optional, for multi-round)
- `stream` (optional)

Streaming mode returns a generator:
```python
{"result": <generator>}
```

WAITING_USER is normalized:
```json
{
  "result": {
    "status": "WAITING_USER",
    "message": "...",
    "task_id": "...",
    "agent": "tariff_calc"
  }
}
```


### ✔ `task.status`
```python
adapter.call("task.status", {
    "agent": "tariff_calc",
    "task_id": "tsk_xxx"
})
```


### ✔ `task.results`
```python
adapter.call("task.results", {
    "agent": "tariff_calc",
    "task_id": "tsk_xxx"
})
```


## Error Handling

Google‑style error envelope:
```json
{
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "missing 'agent'"
  }
}
```

Mapped from SupplyGraph errors when possible:
```json
{
  "error": {
    "code": "INTERNAL",
    "message": "...",
    "details": {...},
    "http_status": 500
  }
}
```


## File Generated
This document is the official adapter reference for Google A2A.

