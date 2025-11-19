#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : mcp_example.py.py

MCP (Model Context Protocol) Example for SupplyGraph AI A2A SDK.

This example demonstrates how to:
    - Instantiate the MCPAdapter
    - Call list_tools() to expose the agent to MCP clients
    - Execute call_tool() in run / status / results modes
    - Work with multi-turn task_id workflows

This does NOT require ChatGPT Desktop / Cursor / Windsurf / Zed.
You can run it locally to understand how the MCP adapter behaves.

MCPAdapter emits JSON-like dicts that match the MCP protocol schema
expected by any MCP-compatible client.
"""

from supplygraphai_a2a_sdk.adapters import create_mcp_tool

# ----------------------------------------------------------------------
# 1. Create the MCP tool
# ----------------------------------------------------------------------
mcp_tool = create_mcp_tool(
    agent_id="tariff_calc",
    api_key="YOUR_API_KEY",
)

print("\n=== MCP list_tools() ===")
tools = mcp_tool.list_tools()
print(tools)


# ----------------------------------------------------------------------
# 2. Single-turn Run
# ----------------------------------------------------------------------
print("\n=== MCP call_tool(run) ===")

resp = mcp_tool.call_tool(
    name="tariff_calc",
    arguments={
        "mode": "run",
        "text": "Import 100kg of citrus from Morocco",
    },
)
print(resp)


# ----------------------------------------------------------------------
# 3. Multi-turn Example (WAITING_USER)
# ----------------------------------------------------------------------
print("\n=== Multi-turn (WAITING_USER) ===")

first = mcp_tool.call_tool(
    name="tariff_calc",
    arguments={
        "mode": "run",
        "text": "Calculate tariffs for leather shoes",
    },
)
print("Initial:", first)

task_id = (
    first.get("data", {}) or {}
).get("task_id")

if task_id and first.get("code") == "WAITING_USER":
    print("Agent requires additional information...")

    follow = mcp_tool.call_tool(
        name="tariff_calc",
        arguments={
            "mode": "run",
            "text": "Country is Vietnam",
            "task_id": task_id,
        },
    )
    print("Follow-up:", follow)


# ----------------------------------------------------------------------
# 4. Direct Status / Results
# ----------------------------------------------------------------------
if task_id:
    print("\n=== MCP call_tool(status) ===")
    status_resp = mcp_tool.call_tool(
        name="tariff_calc",
        arguments={
            "mode": "status",
            "task_id": task_id,
        },
    )
    print(status_resp)

    print("\n=== MCP call_tool(results) ===")
    results_resp = mcp_tool.call_tool(
        name="tariff_calc",
        arguments={
            "mode": "results",
            "task_id": task_id,
        },
    )
    print(results_resp)


# ----------------------------------------------------------------------
# 5. Error handling example
# ----------------------------------------------------------------------
print("\n=== MCP error example ===")

error_test = mcp_tool.call_tool(
    name="tariff_calc",
    arguments={
        "mode": "status",
        # Missing task_id
    },
)
print(error_test)
