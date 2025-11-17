# SupplyGraph AI – LlamaIndex Adapter Documentation

This document describes integration of **SupplyGraph A2A Agents** with **LlamaIndex** using the `LlamaIndexToolWrapper`.


## 1. Overview

`LlamaIndexToolWrapper` provides a **zero‑dependency** integration layer that exposes any SupplyGraph A2A agent as:

- A **LlamaIndex FunctionTool**
- A simple **QueryEngine-like callable**

The adapter does not import `llama_index`, meaning your SDK stays lightweight and avoids optional dependencies.


## 2. Initialization

```python
from supplygraphai_a2a_sdk.adapters.llamaindex_adapter import create_llamaindex_tool

tool = create_llamaindex_tool(
    agent_id="tariff_calc",
    api_key="sk-xxxx",
)
```


## 3. Using as a LlamaIndex FunctionTool

```python
from llama_index.core.tools import FunctionTool

sg_tool = create_llamaindex_tool("tariff_calc", api_key="sk-...")

function_tool = FunctionTool.from_defaults(
    fn=sg_tool.as_function(),
    name="tariff_calc",
)
```

### Supported Arguments

| Argument | Description |
|----------|-------------|
| `text` | Input query text |
| `mode` | `"run"` (default), `"status"`, `"results"` |
| `task_id` | For multi-round continuation |
| `stream` | Enables reasoning stream |
| `**kwargs` | Extra agent parameters |


## 4. Using as Query Engine

```python
qe = tool.as_query_engine()
resp = qe("Import 50kg almonds from US")
```

Functions exactly like:

```python
client.run(agent_id, text=query)
```


## 5. API Reference

### `LlamaIndexToolWrapper`

```
LlamaIndexToolWrapper(agent_id, api_key, base_url)
```

### Methods

#### `as_function()`
Returns a callable compatible with LlamaIndex `FunctionTool`.

#### `as_query_engine()`
Returns a callable that executes simple text queries.

### Factory

```python
create_llamaindex_tool(agent_id, api_key, base_url)
```


## 6. Example: Agent in LlamaIndex ReAct

```python
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool

sg_tool = create_llamaindex_tool("tariff_calc", api_key="sk-...")

react_agent = ReActAgent.from_tools([
    FunctionTool.from_defaults(
        fn=sg_tool.as_function(),
        name="tariff_calc",
        description="Tariff classification & cost estimation"
    )
])

react_agent.chat("Import 200kg fruit juice from MX")
```


## 7. Error Handling

Errors from the A2A gateway will be returned as Python exceptions or structured JSON.


## 8. Summary

The adapter provides:

- Full support for LlamaIndex tools
- Multiround task handling
- Streaming mode compatibility
- Zero-dependency integration
