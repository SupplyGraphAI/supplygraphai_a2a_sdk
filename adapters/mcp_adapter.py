#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    :
@File    : mcp_adapter.py
"""
import json
from typing import Any, Dict, Optional, List

from supplygraphai_a2a_sdk.client.agent_client import AgentClient


class MCPAdapter:
    """
    Minimal MCP (Model Context Protocol) server-side adapter
    exposing a SupplyGraph A2A Agent as an MCP tool.

    MCP Overview:
        - list_tools → returns metadata for this agent
        - call_tool  → runs the agent (run/status/results)

    The adapter conforms to the MCP JSON-RPC interface expected by
    ChatGPT Desktop, Cursor, Windsurf, Zed, and all MCP-capable clients.
    """

    def __init__(
            self,
            agent_id: str,
            api_key: str,
            base_url: str = "https://agent.supplygraph.ai/api/v1/agents",
    ) -> None:
        self.agent_id = agent_id
        self.client = AgentClient(api_key=api_key, base_url=base_url)

    # ----------------------------------------------------------------------
    # MCP: list_tools
    # ----------------------------------------------------------------------
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        Return a list describing this agent as an MCP tool.
        """
        manifest = self.client.manifest(self.agent_id)

        return [
            {
                "name": self.agent_id,
                "description": manifest.get("description", "SupplyGraph A2A Agent"),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "task_id": {"type": ["string", "null"]},
                        "mode": {
                            "type": "string",
                            "enum": ["run", "status", "results"],
                            "default": "run",
                        },
                        "stream": {"type": "boolean", "default": False},
                    },
                    "required": ["mode"],
                },
                "output_schema": manifest.get("output_schema", {}),
            }
        ]

    # ----------------------------------------------------------------------
    # MCP: call_tool
    # ----------------------------------------------------------------------
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool call via the A2A agent.
        MCP standard fields:
            - name      : tool name
            - arguments : dict

        Supported:
            mode="run"     → client.run()
            mode="status"  → client.status()
            mode="results" → client.results()
        """

        if name != self.agent_id:
            return {
                "error": {"message": f"Unknown tool: {name}"}
            }

        mode = arguments.get("mode", "run")
        text = arguments.get("text", "")
        task_id = arguments.get("task_id")
        stream = bool(arguments.get("stream", False))

        try:
            if mode == "run":
                return self.client.run(
                    agent_id=self.agent_id,
                    text=text,
                    task_id=task_id,
                    stream=stream,
                )

            elif mode == "status":
                if not task_id:
                    return {"error": "task_id is required for status()"}
                return self.client.status(self.agent_id, task_id)

            elif mode == "results":
                if not task_id:
                    return {"error": "task_id is required for results()"}
                return self.client.results(self.agent_id, task_id)

            else:
                return {"error": f"Unsupported mode: {mode}"}

        except Exception as e:
            return {
                "error": {
                    "message": str(e),
                    "type": "A2AExecutionError"
                }
            }


# ----------------------------------------------------------------------
# Helper factory (recommended)
# ----------------------------------------------------------------------
def create_mcp_tool(
        agent_id: str,
        api_key: str,
        base_url: str = "https://agent.supplygraph.ai/api/v1/agents",
) -> MCPAdapter:
    """
    Factory helper for ease of use:
        mcp_tool = create_mcp_tool("tariff_calc", api_key="sk-...")
    """
    return MCPAdapter(agent_id=agent_id, api_key=api_key, base_url=base_url)
