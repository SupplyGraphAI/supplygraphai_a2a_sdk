#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    :
@File    : flowise_adapter.py
"""

from typing import Dict, Any, Optional

from ..client.agent_client import AgentClient


class FlowiseToolWrapper:
    """
    Flowise-compatible Tool Adapter for SupplyGraph A2A agents.

    Flowise Tool Contract:
    -----------------------
    A Flowise tool simply needs:
        - name
        - description
        - input schema (JSON)
        - an async/sync "call" method returning a dict

    Users will wrap this wrapper into a Flowise Custom Tool Node.

    This adapter covers:
        - run()
        - status()
        - results()
        - multi-turn interactions with task_id
    """

    def __init__(
        self,
        agent_id: str,
        api_key: str,
        base_url: str = "https://agent.supplygraph.ai/api/v1/agents",
    ):
        self.agent_id = agent_id
        self.client = AgentClient(api_key=api_key, base_url=base_url)

        # Preload manifest for schema
        self.manifest = self.client.manifest(agent_id)

    # ----------------------------------------------------------------------
    # Flowise Tool Introspection
    # ----------------------------------------------------------------------
    def tool_info(self) -> Dict[str, Any]:
        """
        Return Flowise-compatible metadata about this tool.
        """
        return {
            "name": self.agent_id,
            "description": self.manifest.get("description", "SupplyGraph A2A Agent Tool"),
            "input_schema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "mode": {
                        "type": "string",
                        "enum": ["run", "status", "results"],
                        "default": "run",
                    },
                    "task_id": {"type": ["string", "null"]},
                    "stream": {"type": "boolean", "default": False},
                },
                "required": ["mode"],
            },
        }

    # ----------------------------------------------------------------------
    # Core execution for Flowise Custom Tool Node
    # ----------------------------------------------------------------------
    def call(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the A2A agent through Flowise.

        Flowise will pass:
            args = {
                "text": "...",
                "mode": "run/status/results",
                "task_id": "...",
                "stream": false
            }
        """
        mode = args.get("mode", "run")
        text = args.get("text", "")
        task_id = args.get("task_id")
        stream = bool(args.get("stream", False))

        if mode == "run":
            return self.client.run(
                self.agent_id, text=text, task_id=task_id, stream=stream
            )

        elif mode == "status":
            if not task_id:
                return {"error": "task_id is required for status()"}
            return self.client.status(self.agent_id, task_id)

        elif mode == "results":
            if not task_id:
                return {"error": "task_id is required for results()"}
            return self.client.results(self.agent_id, task_id)

        return {"error": f"Unsupported Flowise mode: {mode}"}


# ----------------------------------------------------------------------
# Factory
# ----------------------------------------------------------------------
def create_flowise_tool(
    agent_id: str,
    api_key: str,
    base_url: str = "https://agent.supplygraph.ai/api/v1/agents",
) -> FlowiseToolWrapper:
    return FlowiseToolWrapper(agent_id, api_key, base_url)
