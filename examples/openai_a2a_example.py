#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : openai_a2a_example.py.py

End-to-End OpenAI-style A2A Example for SupplyGraph Agents

This example mirrors the style and structure of OpenAI’s Agents Runtime
examples. It demonstrates a complete workflow using the unified
OpenAIA2AAdapter to drive any SupplyGraph A2A agent:

    • Fetch manifest (OpenAI-style agent manifest)
    • Start a run (non-streaming)
    • Handle requires_action automatically
    • Poll status until completion
    • Fetch final results
    • Resume previous tasks (optional)
    • Use streaming mode for reasoning (SSE)

This example is safe to run as-is. Replace AGENT_ID and API_KEY with
real values to test your own agents.
"""

import time
from supplygraphai_a2a_sdk.adapters.openai_a2a_adapter import (
    OpenAIA2AAdapter,
)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

AGENT_ID = "tariff_calc"
API_KEY = "YOUR_API_KEY"   # Replace with your real key


# ---------------------------------------------------------------------------
# Helper: Pretty banner output
# ---------------------------------------------------------------------------

def banner(title: str):
    print(f"\n{'=' * 25}  {title}  {'=' * 25}\n")


# ---------------------------------------------------------------------------
# Step 1 — Fetch Manifest (OpenAI A2A Format)
# ---------------------------------------------------------------------------

def fetch_manifest(adapter: OpenAIA2AAdapter):
    banner("MANIFEST")
    manifest = adapter.manifest(AGENT_ID)
    print(manifest)
    return manifest


# ---------------------------------------------------------------------------
# Step 2 — Start a Run
# ---------------------------------------------------------------------------

def start_run(adapter: OpenAIA2AAdapter):
    banner("START RUN")

    run = adapter.run(
        AGENT_ID,
        text="Calculate import duty for 100kg ice cream imported from China.",
    )

    print(run)
    return run


# ---------------------------------------------------------------------------
# Step 3 — Handle requires_action Automatically
# ---------------------------------------------------------------------------

def handle_requires_action(adapter: OpenAIA2AAdapter, run):
    """
    OpenAI-style: If the run returns status = "requires_action",
    the agent needs more user input to proceed (similar to multi-round chat).

    This shows how to send a follow-up run() request using the same task_id.
    """

    if run.get("status") != "requires_action":
        return run

    banner("REQUIRES_ACTION → SENDING FOLLOW-UP INPUT")

    task_id = run["id"]

    follow_up = adapter.run(
        AGENT_ID,
        text="Continue. Use country of origin CN.",
        task_id=task_id,
    )

    print(follow_up)
    return follow_up


# ---------------------------------------------------------------------------
# Step 4 — Poll Status Until Completed or Failed
# ---------------------------------------------------------------------------

def poll_until_completed(adapter: OpenAIA2AAdapter, run):
    banner("STATUS POLLING")

    task_id = run["id"]

    while True:
        status = adapter.status(AGENT_ID, task_id)
        print(status)

        if status["status"] in ("completed", "failed", "cancelled"):
            return status

        time.sleep(1)


# ---------------------------------------------------------------------------
# Step 5 — Fetch Final Results
# ---------------------------------------------------------------------------

def fetch_result(adapter: OpenAIA2AAdapter, run):
    banner("FINAL RESULT")

    result = adapter.result(AGENT_ID, run["id"])
    print(result)
    return result


# ---------------------------------------------------------------------------
# Optional: Step 6 — Demonstrate Resume Flow
# (for agents supporting multi-round + resume_mode)
# ---------------------------------------------------------------------------

def resume_example(adapter: OpenAIA2AAdapter, original_task_id: str):
    banner("RESUME EXISTING TASK")

    resumed = adapter.run(
        AGENT_ID,
        text="Resume: Provide updated merchandise value = $1000.",
        task_id=original_task_id,
    )

    print(resumed)
    return resumed


# ---------------------------------------------------------------------------
# Streaming Example (SSE)
# ---------------------------------------------------------------------------

def streaming_example(adapter: OpenAIA2AAdapter):
    banner("STREAMING (SSE)")

    stream = adapter.stream(
        AGENT_ID,
        text="Stream reasoning for tariff calculation of toys 9503.00.00 from China.",
    )

    for frame in stream:
        print(frame, end="", flush=True)


# ---------------------------------------------------------------------------
# Main — Full End-to-End Workflow
# ---------------------------------------------------------------------------

def main():
    adapter = OpenAIA2AAdapter(api_key=API_KEY)

    # 1. Manifest
    fetch_manifest(adapter)

    # 2. Start run
    run = start_run(adapter)

    # 3. If requires_action, send follow-up input
    run = handle_requires_action(adapter, run)

    # 4. Poll status
    final_status = poll_until_completed(adapter, run)

    # 5. Fetch result
    fetch_result(adapter, run)

    # 6. Resume (optional)
    # resume_example(adapter, run["id"])

    # 7. Streaming example
    banner("Starting Streaming Example")
    streaming_example(adapter)


if __name__ == "__main__":
    main()
