#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : autogen_example.py.py

AutoGen integration example for SupplyGraph AI A2A SDK.

This example demonstrates how to use:
    - AutoGenTool
    - Connecting a SupplyGraph agent as an AutoGen tool
    - Single-turn and multi-turn usage

AutoGen is NOT installed by default.
Install it separately if you want to run this example:

    pip install pyautogen
"""

from supplygraphai_a2a_sdk.adapters import AutoGenTool

try:
    from autogen import AssistantAgent, Tool
except ImportError:
    raise ImportError(
        "AutoGen is not installed.\n"
        "Install it with: pip install pyautogen"
    )


# ------------------------------------------------------------
# 1. Create a SupplyGraph → AutoGen tool mapping
# ------------------------------------------------------------
sg_tool = AutoGenTool(
    agent_id="tariff_calc",
    api_key="YOUR_API_KEY",
)

autogen_tool = sg_tool.to_autogen_tool()


# ------------------------------------------------------------
# 2. Create an AutoGen assistant with the tool
# ------------------------------------------------------------
assistant = AssistantAgent(
    name="assistant",
    tools=[Tool(autogen_tool)],
)


# ------------------------------------------------------------
# 3. Single-turn run
# ------------------------------------------------------------
print("\n=== Single-turn AutoGen Tool Call ===")
response = assistant.run("Import 100kg citrus from CN")
print(response)


# ------------------------------------------------------------
# 4. Multi-turn (task_id-based) run
# ------------------------------------------------------------
print("\n=== Multi-turn AutoGen Tool Call ===")
first = sg_tool.run("Calculate duty for shoes", task_id=None)

task_id = first.get("data", {}).get("task_id")
print("Initial Response:", first)

if first.get("code") == "WAITING_USER" and task_id:
    print("Agent needs more info. Sending follow-up message...")
    follow = sg_tool.run("Country of origin is Vietnam", task_id=task_id)
    print("Follow-up Response:", follow)
