#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : langchain_example.py.py

LangChain integration example for SupplyGraph AI A2A SDK.

This example demonstrates:
    - Using SupplyGraphLangChainTool with LangChain Tool API
    - Using .as_runnable() with LCEL pipeline logic
    - run / status / results modes
    - Multi-turn task_id flow

LangChain is NOT installed with this SDK.
Install it separately if running this example:

    pip install langchain langchain-core
"""

from supplygraphai_a2a_sdk.adapters import create_langchain_tool

try:
    from langchain.tools import Tool           # For classic LC tool usage
    from langchain_core.runnables import RunnableLambda  # For LCEL pipelines
except ImportError:
    raise ImportError(
        "LangChain is not installed.\n"
        "Install with: pip install langchain langchain-core"
    )


# ------------------------------------------------------------
# 1. Create SupplyGraph LangChain Tool wrapper
# ------------------------------------------------------------
sg_tool = create_langchain_tool(
    agent_id="tariff_calc",
    api_key="YOUR_API_KEY",
)

print("\n=== SupplyGraph LangChain Tool Created ===")
print("Agent:", sg_tool.agent_id)


# ------------------------------------------------------------
# 2. Classic LangChain Tool usage
# ------------------------------------------------------------
print("\n=== LangChain Tool: single-turn run ===")

lc_tool = Tool(
    name="tariff_calc",
    description="SupplyGraph Tariff Calculation Agent",
    func=sg_tool.run,
)

resp = lc_tool.run(
    "Import 120kg oranges from Egypt"
)
print("Tool Response:", resp)


# ------------------------------------------------------------
# 3. Multi-turn (task_id) example
# ------------------------------------------------------------
print("\n=== LangChain Tool: Multi-turn Example ===")

first = lc_tool.run("Calculate tariff for leather shoes")
print("Initial:", first)

task_id = first.get("data", {}).get("task_id")

if task_id and first.get("code") == "WAITING_USER":
    print("Agent needs more information...")

    follow = lc_tool.run({
        "text": "Country is Vietnam",
        "mode": "run",
        "task_id": task_id,
    })
    print("Follow-up:", follow)


# ------------------------------------------------------------
# 4. Using SupplyGraph A2A via LCEL Runnable
# ------------------------------------------------------------
print("\n=== LCEL Runnable Example ===")

# Convert to LCEL Runnable
runnable_tool = sg_tool.as_runnable()

# Build a simple LCEL chain (tool → lambda)
chain = runnable_tool | RunnableLambda(
    lambda result: result.get("data", {}).get("content")
)

out = chain.invoke({
    "text": "Import 50kg chocolate from France",
    "mode": "run",
})
print("LCEL Output:", out)


# ------------------------------------------------------------
# 5. Direct status() and results() via Runnable
# ------------------------------------------------------------
print("\n=== LCEL: status/results example ===")

if task_id:
    status_out = runnable_tool.invoke({
        "mode": "status",
        "task_id": task_id,
    })
    print("Status:", status_out)

    results_out = runnable_tool.invoke({
        "mode": "results",
        "task_id": task_id,
    })
    print("Results:", results_out)
