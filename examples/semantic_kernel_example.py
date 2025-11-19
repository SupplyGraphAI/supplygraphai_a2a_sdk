#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : semantic_kernel_example.py.py

Semantic Kernel Adapter Example

This example demonstrates how to use the Semantic Kernel skill adapter
to wrap a SupplyGraph A2A agent as an async SK skill function.

The adapter supports:
    - async execution
    - multiround (task_id continuation)
    - WAITING_USER handling
    - streaming (THINKING events)
"""

import asyncio

from supplygraphai_a2a_sdk.adapters.semantic_kernel_adapter import (
    make_semantic_skill,
)


# ------------------------------------------------------------
# 1. Initialize Semantic Kernel skill
# ------------------------------------------------------------
skill = make_semantic_skill(
    agent_id="tariff_calc",
    api_key="YOUR_API_KEY",
    base_url="https://agent.supplygraph.ai/api/v1/agents",
)


# ------------------------------------------------------------
# 2. Main async workflow
# ------------------------------------------------------------
async def main():
    print("\n=== Semantic Kernel Skill: RUN ===")

    resp = await skill("Import 200kg chocolate from FR")
    print(resp)

    # Extract task_id for multi-turn cases
    task_id = (
        resp.get("task_id")
        if resp.get("status") == "WAITING_USER"
        else None
    )

    # --------------------------------------------------------
    # 3. Multi-turn continuation (when WAITING_USER)
    # --------------------------------------------------------
    if resp.get("status") == "WAITING_USER":
        print("\n=== Continuing multi-turn (WAITING_USER) ===")

        follow = await skill(
            text="Country is France",  # user's additional input
            task_id=task_id
        )
        print(follow)
        task_id = follow.get("task_id")

    # --------------------------------------------------------
    # 4. Streaming mode
    # --------------------------------------------------------
    print("\n=== STREAMING (THINKING events) ===")

    async_stream = await skill(
        text="Stream reasoning for tariff classification",
        stream=True,
    )

    async for frame in async_stream:
        print(">>", frame)


# ------------------------------------------------------------
# Entry point
# ------------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())
