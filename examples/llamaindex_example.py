#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : llamaindex_example.py.py

LlamaIndex integration example for SupplyGraph AI A2A SDK.

Demonstrates:
    - Using create_llamaindex_tool()
    - Wrapping SupplyGraph agents as LlamaIndex FunctionTools
    - QueryEngine-style usage
    - run/status/results/task_id interactions

LlamaIndex is NOT bundled with this SDK.
Install it separately if you want to run this example:

    pip install llama-index
"""

from supplygraphai_a2a_sdk.adapters import create_llamaindex_tool

try:
    from llama_index.core.tools import FunctionTool
except ImportError:
    raise ImportError(
        "LlamaIndex is not installed.\n"
        "Install with: pip install llama-index"
    )


# ------------------------------------------------------------
# 1. Create SupplyGraph LlamaIndex tool
# ------------------------------------------------------------
sg_tool = create_llamaindex_tool(
    agent_id="tariff_calc",
    api_key="YOUR_API_KEY",
)

fn = sg_tool.as_function()

print("\n=== SupplyGraph → LlamaIndex FunctionTool ===")
print("Function name:", fn.__name__)


# ------------------------------------------------------------
# 2. Build FunctionTool for LlamaIndex Agents
# ------------------------------------------------------------
llama_tool = FunctionTool.from_defaults(
    fn=fn,
    name="tariff_calc",
    description="Tariff calculator using SupplyGraph AI A2A Agent",
)

print("\n=== FunctionTool metadata ===")
print("Name:", llama_tool.metadata.get("name"))
print("Description:", llama_tool.metadata.get("description"))


# ------------------------------------------------------------
# 3. Direct FunctionTool execution
# ------------------------------------------------------------
print("\n=== FunctionTool: single-turn run ===")

resp = llama_tool(
    text="Import 100kg citrus from Morocco",
    mode="run",
)
print("Response:", resp)


# ------------------------------------------------------------
# 4. Multi-turn example using task_id
# ------------------------------------------------------------
print("\n=== Multi-turn Example ===")

first = llama_tool(
    text="Calculate tariff for leather shoes",
    mode="run",
)
print("Initial:", first)

tid = first.get("data", {}).get("task_id")

if tid and first.get("code") == "WAITING_USER":
    print("Agent requires more information...")

    follow = llama_tool(
        text="Country is Vietnam",
        mode="run",
        task_id=tid,
    )
    print("Follow-up:", follow)


# ------------------------------------------------------------
# 5. QueryEngine-style usage
# ------------------------------------------------------------
print("\n=== QueryEngine: using as_query_engine() ===")

query_engine = sg_tool.as_query_engine()

qe_result = query_engine("Import 80kg chocolate from Germany")
print("QE Output:", qe_result)


# ------------------------------------------------------------
# 6. status() and results() via the FunctionTool
# ------------------------------------------------------------
print("\n=== status() / results() ===")

if tid:
    status_out = llama_tool(
        text="",
        mode="status",
        task_id=tid,
    )
    print("Status:", status_out)

    results_out = llama_tool(
        text="",
        mode="results",
        task_id=tid,
    )
    print("Results:", results_out)
