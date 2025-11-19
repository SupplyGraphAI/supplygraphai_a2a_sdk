#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    :
@File    : haystack_adapter.py
"""

from typing import Any, Dict, Optional

from supplygraphai_a2a_sdk.client.agent_client import AgentClient


class SupplyGraphHaystackNode:
    """
    Haystack-compatible node wrapper for SupplyGraph A2A agents.

    Design philosophy:
    - Does NOT inherit from haystack.Component to avoid hard SDK dependency.
    - Provides a run() method so users can integrate it into Haystack pipelines
      by wrapping or subclassing this class inside their own projects.

    Typical usage (inside the user's own code):

        from haystack import Pipeline
        from supplygraphai_a2a_sdk.adapters.haystack_adapter import create_haystack_node

        sg_node = create_haystack_node("tariff_calc", api_key="sk-...")

        # Use sg_node.run inside the pipeline as a node:
        result = sg_node.run(query="import 100kg ice cream from CN")
    """

    def __init__(
        self,
        agent_id: str,
        api_key: str,
        base_url: str = "https://agent.supplygraph.ai/api/v1/agents",
    ) -> None:
        self.agent_id = agent_id
        self.client = AgentClient(api_key=api_key, base_url=base_url)

    # ------------------------------------------------------------------
    # Haystack-style run() interface
    # ------------------------------------------------------------------
    def run(
        self,
        query: str,
        mode: str = "run",
        task_id: Optional[str] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Haystack nodes typically use the signature run(query=..., **kwargs).

        Parameters:
            query   : Natural-language input text from the pipeline.
            mode    : "run", "status", or "results"
            task_id : Required for continuing a multi-round task.
            stream  : Whether SSE streaming should be activated.
                      If True, the method returns a generator.

        Returns:
            The raw A2A JSON structure, or SSE generator when stream=True.
        """
        if mode == "run":
            return self.client.run(
                agent_id=self.agent_id,
                text=query,
                task_id=task_id,
                stream=stream,
                **kwargs,
            )

        if mode == "status":
            if not task_id:
                return {"error": "task_id is required for mode='status'"}
            return self.client.status(self.agent_id, task_id, **kwargs)

        if mode == "results":
            if not task_id:
                return {"error": "task_id is required for mode='results'"}
            return self.client.results(self.agent_id, task_id, **kwargs)

        return {"error": f"Unsupported mode: {mode}"}


# ----------------------------------------------------------------------
# Simple factory helper
# ----------------------------------------------------------------------
def create_haystack_node(
    agent_id: str,
    api_key: str,
    base_url: str = "https://agent.supplygraph.ai/api/v1/agents",
) -> SupplyGraphHaystackNode:
    """
    Factory function to quickly construct a Haystack node wrapper.
    """
    return SupplyGraphHaystackNode(agent_id=agent_id, api_key=api_key, base_url=base_url)
