# MCP Adapter — SupplyGraph AI A2A SDK

This document describes the **MCP (Model Context Protocol) Adapter** for exposing SupplyGraph A2A agents as MCP tools.

## Overview

The MCP adapter allows SupplyGraph agents to function inside **ChatGPT Desktop, Cursor, Windsurf, Zed**, and any other MCP‑compatible clients.

It implements two required RPC behaviors:

- `list_tools` → Advertise available tools with input/output schema  
- `call_tool` → Execute A2A agent operations (`run`, `status`, `results`)

The adapter does **not** require any MCP packages; it implements the protocol minimally.

---

## MCPAdapter Class

### Initialization

```python
mcp = MCPAdapter(
    agent_id="tariff_calc",
    api_key="sk-...",
)
```

---

## list_tools()

Returns a list of all tools provided by this adapter (usually one).

Includes:

- name  
- description  
- input schema  
- output schema  

Example response:

```json
[
  {
    "name": "tariff_calc",
    "description": "SupplyGraph A2A Agent",
    "input_schema": {
      "type": "object",
      "properties": {
        "text": {"type": "string"},
        "task_id": {"type": ["string", "null"]},
        "mode": {
          "type": "string",
          "enum": ["run", "status", "results"],
          "default": "run"
        },
        "stream": {"type": "boolean", "default": false}
      },
      "required": ["mode"]
    },
    "output_schema": {}
  }
]
```

---

## call_tool()

Executes the tool.  
Supported modes:

| mode      | Description |
|-----------|-------------|
| `run`     | Start or continue an A2A job |
| `status`  | Check job progress |
| `results` | Retrieve final results |

Example:

```python
resp = mcp.call_tool(
    "tariff_calc",
    {"mode": "run", "text": "Import 100kg cheese from FR"}
)
```

---

## Error Behavior

Unknown tool:

```json
{"error": {"message": "Unknown tool: xxx"}}
```

Missing `task_id`:

```json
{"error": "task_id is required for results"}
```

---

## Factory Helper

```python
from supplygraphai_a2a_sdk.adapters import create_mcp_tool

mcp = create_mcp_tool("tariff_calc", api_key="sk-...")
```

---

## Summary

The MCP adapter makes SupplyGraph agents usable in any MCP-based IDE or assistant environment with minimal integration effort.

