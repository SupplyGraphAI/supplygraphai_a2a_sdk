# LangGraph / LangChain Adapter

This document describes how to use the **LangGraph / LangChain adapter** for SupplyGraph A2A agents.

Adapter source file: `adapters/langgraph_adapter.py`

---

## Overview

The LangGraph adapter exposes a SupplyGraph A2A agent as a **callable tool function** that can be used inside:

- **LangGraph** graphs (as a node / tool)
- **LangChain** tool stacks (wrapped into `Tool` objects or similar)

Key capabilities:

- Uses the shared `AgentClient` + `BaseAgent` stack
- Automatically loads the agent **manifest**
- Supports **multi-round** workflows via `task_id`
- Handles **WAITING_USER** states consistently
- Supports **streaming** (`THINKING` SSE events) when `stream=True`

You create the tool with a single factory function:

```python
from supplygraphai_a2a_sdk.adapters import create_langgraph_tool

tool = create_langgraph_tool(
    agent_id="tariff_classification",
    api_key="YOUR_API_KEY",
)
```

The returned `tool` is a plain Python callable with signature:

```python
tool(
    text: str,
    task_id: Optional[str] = None,
    stream: bool = False,
    **kwargs
) -> Any
```

---

## Import and Initialization

```python
from supplygraphai_a2a_sdk.adapters import create_langgraph_tool

agent_id = "tariff_classification"
api_key = "YOUR_API_KEY"

sg_tool = create_langgraph_tool(
    agent_id=agent_id,
    api_key=api_key,
    base_url="https://agent.supplygraph.ai/api/v1/agents",  # default
)
```

Internally this will:

1. Create an `AgentClient` with the given `api_key` / `base_url`
2. Wrap it into a `BaseAgent`
3. Fetch and cache the **manifest** for `agent_id`
4. Attach metadata to the returned function:

   - `sg_tool.__name__` → agent name from manifest (or `agent_id`)
   - `sg_tool.__doc__` / `sg_tool.description` → agent description
   - `sg_tool.agent_id` → the underlying agent ID
   - `sg_tool.manifest` → raw manifest dict

This makes it much easier to auto-register tools in LangGraph / LangChain based on manifest info.

---

## Basic Usage (Single-Turn)

```python
resp = sg_tool("Import 100kg ice cream from China")
print(resp["code"], resp["message"])
```

Under the hood, this is equivalent to:

- `mode="run"`
- `task_id=None`
- `stream=False`

The response is the standard SupplyGraph A2A envelope, e.g.:

```json
{
  "success": true,
  "code": "TASK_COMPLETED",
  "message": "Task completed successfully.",
  "data": {
    "task_id": "tsk_xxx",
    "stage": "completed",
    "code": "TASK_COMPLETED",
    "content": {
      "type": "result",
      "data": { ... }
    }
  }
}
```

---

## Multi-Round Workflow (task_id)

The tool fully supports the A2A **multi-round** lifecycle (`WAITING_USER`, `TASK_ACCEPTED`, etc.).

```python
# 1) First call — start the task
resp = sg_tool("Import 100kg ice cream")
task_id = resp["data"]["task_id"]
code = resp["code"]

if code == "WAITING_USER":
    print(resp["message"])  # e.g. "Please provide country of origin"
    user_reply = "Country of origin is CN"

    # 2) Continue the same task with task_id
    resp2 = sg_tool(
        text=user_reply,
        task_id=task_id,
    )
```

When the underlying agent returns `WAITING_USER`, the adapter will **not** obscure the structure. It simply returns the original envelope so you can implement your own interaction loop or let LangGraph manage the continuation logic.

---

## Handling WAITING_USER (Helper Structure)

When used via this adapter, a typical `WAITING_USER` envelope from the agent looks like:

```json
{
  "success": true,
  "code": "WAITING_USER",
  "message": "Please provide the country of origin.",
  "data": {
    "task_id": "tsk_xxx",
    "stage": "interpreting",
    "code": "WAITING_USER",
    "content": "Please specify the country.",
    "is_final": false
  }
}
```

You can either:

- Use `code == "WAITING_USER"` directly, or
- In some higher-level orchestration, interpret this as a cue to ask the human for more info.

The adapter **does not** auto-convert this into another shape; it keeps the A2A envelope intact for maximum control on the LangGraph side.

> Note: for CrewAI / Google-A2A adapters we provide more specialized mappings. For LangGraph we keep it closer to raw A2A so users can design their own graph logic.

---

## Streaming Mode (THINKING / SSE)

If you call the tool with `stream=True`, it will return a **generator** that yields SSE frames parsed into Python dicts.

```python
events = sg_tool(
    text="Import 100 EV motors from Mexico",
    stream=True,
)

for ev in events:
    # Typical SSE frame:
    # {
    #   "event": "stream",
    #   "data": {
    #       "task_id": "...",
    #       "stage": "interpreting" | "executing",
    #       "code": "THINKING",
    #       "reasoning": ["...", "..."],
    #       "timestamp": "...",
    #       "is_final": false
    #   }
    # }
    print(">>", ev["data"].get("reasoning", []))
```

In LangGraph, you can either:

- Wrap this generator into a custom node that surfaces incremental reasoning to the user UI, or
- Consume the generator internally and only emit the final state to the graph state.

---

## Using in LangGraph

A minimal example (pseudo-code style):

```python
from langgraph.graph import StateGraph
from supplygraphai_a2a_sdk.adapters import create_langgraph_tool

sg_tool = create_langgraph_tool("tariff_classification", api_key="sk-...")

def classification_node(state):
    user_input = state["input"]
    resp = sg_tool(text=user_input)
    return {"a2a_response": resp}

graph = StateGraph(dict)
graph.add_node("classify", classification_node)
graph.set_entry_point("classify")
app = graph.compile()
```

You can then add other nodes that read `state["a2a_response"]`, check `code` / `data.content`, and route accordingly.

---

## Using in LangChain

You can easily wrap the tool into a LangChain `Tool` or LCEL `Runnable`.

### As a LangChain Tool

```python
from langchain.tools import Tool
from supplygraphai_a2a_sdk.adapters import create_langgraph_tool

sg_tool = create_langgraph_tool("tariff_calc", api_key="sk-...")

lc_tool = Tool(
    name=sg_tool.__name__,
    description=sg_tool.description,
    func=lambda query: sg_tool(text=query),
)
```

### As an LCEL Runnable

```python
from supplygraphai_a2a_sdk.adapters import create_langgraph_tool

sg_tool = create_langgraph_tool("tariff_calc", api_key="sk-...")

def a2a_runnable(input_dict):
    text = input_dict.get("text", "")
    task_id = input_dict.get("task_id")
    stream = bool(input_dict.get("stream", False))
    extras = {
        k: v for k, v in input_dict.items()
        if k not in ("text", "task_id", "stream")
    }
    return sg_tool(text=text, task_id=task_id, stream=stream, **extras)
```

You can then plug `a2a_runnable` into a LangChain / LCEL pipeline.

---

## Error Handling

If the underlying A2A gateway raises a `SupplyGraphAPIError`, the adapter catches it and returns a normalized error structure:

```python
{
  "status": "ERROR",
  "message": str(e),
  "api_code": e.api_code,
  "http_status": e.http_status,
  "details": e.errors,
}
```

You can check `status == "ERROR"` inside your graph or chain, and route failures to a separate handler node or fallback strategy.

---

## Summary

- `create_langgraph_tool()` gives you a **manifest-aware**, **multi-round**, **streaming-capable** tool callable.
- Ideal for LangGraph / LangChain graphs that need to integrate SupplyGraph A2A agents.
- Leaves the full A2A envelope intact so you have complete control over task lifecycle and routing.
