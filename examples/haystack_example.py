#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : haystack_example.py.py

Haystack integration example for SupplyGraph AI A2A SDK.

Demonstrates:
    - create_haystack_node()
    - Using SupplyGraph A2A Agents inside a Haystack Pipeline
    - run/status/results modes
    - Multi-turn task_id flow

Haystack is NOT bundled with this SDK.
To run this example, install Haystack separately:

    pip install haystack-ai
"""

from supplygraphai_a2a_sdk.adapters import create_haystack_node

try:
    from haystack import Pipeline  # Optional dependency
except ImportError:
    raise ImportError(
        "Haystack is not installed.\n"
        "Install with: pip install haystack-ai"
    )


# ------------------------------------------------------------
# 1. Create a Haystack node wrapping a SupplyGraph agent
# ------------------------------------------------------------
sg_node = create_haystack_node(
    agent_id="tariff_calc",
    api_key="YOUR_API_KEY",
)

print("\n=== Haystack Node Metadata ===")
print("Agent:", sg_node.agent_id)


# ------------------------------------------------------------
# 2. Direct invocation (Haystack-style signature)
# ------------------------------------------------------------
print("\n=== Direct Node Call (mode='run') ===")

resp = sg_node.run(
    query="Import 300kg apples from Chile",
    mode="run",
)

print("Response:", resp)


# ------------------------------------------------------------
# 3. Multi-step (task_id) — WAITING_USER handling
# ------------------------------------------------------------
print("\n=== Multi-turn Example ===")

initial = sg_node.run(
    query="Calculate tariff for leather shoes",
    mode="run",
)

print("Initial:", initial)

task_id = initial.get("data", {}).get("task_id")

if task_id and initial.get("code") == "WAITING_USER":
    print("Agent requires more info...")

    follow = sg_node.run(
        query="Country of origin is Vietnam",
        mode="run",
        task_id=task_id,
    )

    print("Follow-up:", follow)


# ------------------------------------------------------------
# 4. Status and Results modes
# ------------------------------------------------------------
print("\n=== Status ===")
if task_id:
    status = sg_node.run(
        query="",  # query ignored in status mode
        mode="status",
        task_id=task_id,
    )
    print(status)


print("\n=== Results ===")
if task_id:
    result = sg_node.run(
        query="",  # query ignored in results mode
        mode="results",
        task_id=task_id,
    )
    print(result)


# ------------------------------------------------------------
# 5. Embedding the node into a Haystack Pipeline
# ------------------------------------------------------------
print("\n=== Haystack Pipeline Example ===")

pipeline = Pipeline()
pipeline.add_node(component=sg_node, name="supplygraph", inputs=["Query"])

# Execute pipeline
result_pipeline = pipeline.run(
    query="Import 20kg cheese from France"
)

print(result_pipeline)
