#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : flowise_example.py.py

Flowise integration example for SupplyGraph AI A2A SDK.

This example demonstrates how to:
    - create a Flowise-compatible Tool using FlowiseToolWrapper
    - expose the tool metadata (tool_info)
    - run Flowise-style calls (run/status/results)
    - handle multi-turn task_id logic

Flowise itself is NOT installed with this SDK.
This example shows how to define a custom tool that Flowise can load.
"""

from supplygraphai_a2a_sdk.adapters import create_flowise_tool


# ------------------------------------------------------------
# 1. Create a Flowise Tool Wrapper
# ------------------------------------------------------------
tool = create_flowise_tool(
    agent_id="tariff_calc",
    api_key="YOUR_API_KEY",
)

print("\n=== Tool Metadata (Flowise Format) ===")
print(tool.tool_info())


# ------------------------------------------------------------
# 2. Flowise-style: call() with mode='run'
# ------------------------------------------------------------
print("\n=== Flowise: Run ===")

resp = tool.call({
    "mode": "run",
    "text": "Import 200kg meat from Australia",
    "task_id": None,
    "stream": False,
})

print(resp)


# ------------------------------------------------------------
# 3. Multi-turn usage (task_id)
# ------------------------------------------------------------
print("\n=== Flowise: Multi-turn (task_id) ===")

initial = tool.call({
    "mode": "run",
    "text": "Calculate tariff for leather shoes",
})

print("Initial:", initial)

tid = initial.get("data", {}).get("task_id")

if tid and initial.get("code") == "WAITING_USER":
    print("Providing additional user info...")

    follow = tool.call({
        "mode": "run",
        "text": "Country is Vietnam",
        "task_id": tid,
    })

    print("Follow-up:", follow)


# ------------------------------------------------------------
# 4. STATUS and RESULTS modes
# ------------------------------------------------------------
print("\n=== Flowise: Status ===")
if tid:
    status_resp = tool.call({
        "mode": "status",
        "task_id": tid,
    })
    print(status_resp)

print("\n=== Flowise: Results ===")
if tid:
    result_resp = tool.call({
        "mode": "results",
        "task_id": tid,
    })
    print(result_resp)
