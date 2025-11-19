# CrewAI Adapter — SupplyGraph A2A SDK

## Overview

The `CrewAITool` adapter exposes any SupplyGraph A2A Agent as a **CrewAI Tool**, supporting:
- Multi‑round execution via `task_id`
- WAITING_USER workflow continuation
- Streaming (“THINKING” events via SSE)
- Auto‑loading manifest (name, description)
- Unified error handling


## Import

```python
from supplygraphai_a2a_sdk.adapters import CrewAITool
```


## Basic Usage

```python
from autogen import AssistantAgent

sg_tool = CrewAITool(agent_id="tariff_calc", api_key="sk-...")

assistant = AssistantAgent(
    name="assistant",
    tools=[sg_tool.run],   # CrewAI expects a callable
)

resp = sg_tool.run("Import 100kg ice cream from CN")
print(resp)
```


## Multi‑Round Tasks

CrewAI workflows often require multiple turns.  
When the agent requires more information (`WAITING_USER`), the adapter returns:

```json
{
  "type": "waiting_user",
  "message": "Please specify the country of origin.",
  "task_id": "tsk_123",
  "agent": "tariff_calc"
}
```

Your CrewAI code should then call:

```python
sg_tool.run("China", task_id="tsk_123")
```


## Streaming Mode

```python
events = sg_tool.run("Import 5 tons of EV motors", stream=True)

for ev in events:
    print(ev)
```

You will receive SSE frames containing **THINKING** steps from the agent.


## Error Handling

Errors are normalized for CrewAI:

```json
{
  "type": "error",
  "agent": "tariff_calc",
  "error": "...",
  "api_code": "...",
  "http_status": 400,
  "details": {...}
}
```


## Full Class Reference

```python
class CrewAITool:
    def __init__(self, agent_id: str, api_key: str, base_url: str = "..."):
        ...

    def run(
        self,
        text: str,
        task_id: Optional[str] = None,
        stream: bool = False,
        **kwargs
    ) -> Any:
        ...
```

<<<<<<< HEAD
=======

>>>>>>> fc3d68b75723eb846127633d630c19c772b31c77
This adapter enables complete compatibility between **CrewAI** and **SupplyGraph A2A Agents**, including stateful workflows and manifest‑aware behavior.
