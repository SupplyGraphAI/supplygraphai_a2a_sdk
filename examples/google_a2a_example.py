#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : google_a2a_example.py.py

Google A2A Adapter example for SupplyGraph AI A2A SDK.

This example demonstrates how to:
    - initialize GoogleA2AAdapter
    - call Google-style RPC methods:
        * task.run
        * task.status
        * task.results
    - handle WAITING_USER → multi-turn
    - handle streaming (if enabled)

Google A2A protocol is based on JSON-RPC style calls.
This example shows how a caller would structure requests.
"""

from supplygraphai_a2a_sdk.adapters import GoogleA2AAdapter


# ------------------------------------------------------------
# 1. Initialize adapter
# ------------------------------------------------------------
adapter = GoogleA2AAdapter(
    api_key="YOUR_API_KEY",
)

AGENT_ID = "tariff_calc"


# ------------------------------------------------------------
# 2. task.run (single-turn)
# ------------------------------------------------------------
print("\n=== Google A2A: task.run ===")

resp = adapter.call(
    method="task.run",
    params={
        "agent": AGENT_ID,
        "input": "Import 100kg oranges from Egypt",
    },
)

print(resp)


# ------------------------------------------------------------
# 3. WAITING_USER → multi-turn logic
# ------------------------------------------------------------
print("\n=== Google A2A: WAITING_USER multi-turn ===")

first = adapter.call(
    method="task.run",
    params={
        "agent": AGENT_ID,
        "input": "Calculate tariff for leather shoes",
    },
)

print("Initial:", first)

result = first.get("result", {})
if result.get("status") == "WAITING_USER":
    tid = result.get("task_id")
    print(f"Agent requested more info. task_id={tid}")

    follow = adapter.call(
        method="task.run",
        params={
            "agent": AGENT_ID,
            "task_id": tid,
            "input": "Country of origin is Vietnam",
        },
    )

    print("Follow-up:", follow)


# ------------------------------------------------------------
# 4. task.status
# ------------------------------------------------------------
print("\n=== Google A2A: task.status ===")

if "tid" in locals():
    status_resp = adapter.call(
        method="task.status",
        params={
            "agent": AGENT_ID,
            "task_id": tid,
        },
    )
    print(status_resp)


# ------------------------------------------------------------
# 5. task.results
# ------------------------------------------------------------
print("\n=== Google A2A: task.results ===")

if "tid" in locals():
    result_resp = adapter.call(
        method="task.results",
        params={
            "agent": AGENT_ID,
            "task_id": tid,
        },
    )
    print(result_resp)


# ------------------------------------------------------------
# 6. Optional: Streaming Mode (task.run with stream=True)
# ------------------------------------------------------------
print("\n=== Google A2A: Streaming Example ===")

stream_resp = adapter.call(
    method="task.run",
    params={
        "agent": AGENT_ID,
        "input": "Import 20kg cheese from FR",
        "stream": True,
    },
)

# Streaming returns {"result": generator}
stream_gen = stream_resp.get("result")

if stream_gen:
    for frame in stream_gen:
        print("SSE:", frame)
