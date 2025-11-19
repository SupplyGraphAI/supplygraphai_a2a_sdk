#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : crewai_example.py.py

CrewAI integration example for SupplyGraph AI A2A SDK.

This example demonstrates how to use:
    - CrewAITool (SupplyGraph Adapter)
    - Registering SupplyGraph agents as CrewAI tools
    - Single-turn and multi-turn (task_id) calls
    - Handling WAITING_USER in a CrewAI workflow

CrewAI is NOT bundled with this SDK.
Install it separately:

    pip install crewai
"""

from supplygraphai_a2a_sdk.adapters import CrewAITool

try:
    from crewai import Agent, Task, Crew
except ImportError:
    raise ImportError(
        "CrewAI is not installed.\n"
        "Install it with: pip install crewai"
    )


# ------------------------------------------------------------
# 1. Create SupplyGraph → CrewAI tool
# ------------------------------------------------------------
sg_tool = CrewAITool(
    agent_id="tariff_calc",
    api_key="YOUR_API_KEY",
)

# CrewAI requires a callable
tool_callable = sg_tool.run


# ------------------------------------------------------------
# 2. Build a CrewAI Agent using the tool
# ------------------------------------------------------------
assistant = Agent(
    name=sg_tool.name,
    role="Tariff Calculation Assistant",
    goal="Help users compute U.S. tariffs and duties.",
    backstory="This agent is powered by SupplyGraph AI's tariff computation engine.",
    tools=[tool_callable],
    verbose=True,
)


# ------------------------------------------------------------
# 3. Create a Crew task
# ------------------------------------------------------------
task = Task(
    description="Compute import duty for 100kg of ice cream from China.",
    agent=assistant,
)


# ------------------------------------------------------------
# 4. Execute the Crew
# ------------------------------------------------------------
print("\n=== Running CrewAI Task ===")
result = Crew(agents=[assistant], tasks=[task]).run()

print("\n=== Result ===")
print(result)


# ------------------------------------------------------------
# 5. Manual demonstration of multi-turn (task_id) logic
# ------------------------------------------------------------
print("\n=== Multi-turn Example (Manual) ===")

# First call
first = sg_tool.run("Calculate tariff for shoes")
print("Initial:", first)

if first.get("type") == "waiting_user":
    tid = first["task_id"]
    print(f"Agent needs additional info, task_id={tid}")

    # Provide additional info
    follow = sg_tool.run("Country is Vietnam", task_id=tid)
    print("Follow-up:", follow)
