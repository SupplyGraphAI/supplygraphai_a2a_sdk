#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : langgraph_adapter.py

LangGraph / LangChain Adapter for SupplyGraph A2A Agents
Fully manifest-aware, multiround-capable, streaming-capable.
"""

from typing import Any, Callable, Dict, Optional

from supplygraphai_a2a_sdk.client.agent_client import AgentClient
from supplygraphai_a2a_sdk.client.base_agent import BaseAgent
from supplygraphai_a2a_sdk.utils.error_handler import SupplyGraphAPIError


def create_langgraph_tool(
    agent_id: str,
    api_key: str,
    base_url: str = "https://agent.supplygraph.ai/api/v1/agents",
) -> Callable[..., Any]:
    """
    Returns a callable compatible with LangGraph / LangChain Tool usage.

    Supports:
    - multiround (task_id continuation)
    - WAITING_USER -> returns structured cue
    - streaming (returns SSE generator)
    - manifest-aware name & description
    """
    client = AgentClient(api_key=api_key, base_url=base_url)
    agent = BaseAgent(client, agent_id)

    name = agent.manifest.get("name", agent_id)
    description = agent.manifest.get("description", "")

    def tool(
        text: str,
        task_id: Optional[str] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        """
        LangGraph tool entry point — callable as a graph node.
        """
        try:
            resp = agent.run(text, task_id=task_id, stream=stream, **kwargs)

            # Streaming (THINKING events)
            if stream:
                return resp  # generator

            # WAITING_USER → LangGraph node must continue asking
            if agent.needs_user_input(resp):
                return {
                    "status": "WAITING_USER",
                    "message": resp.get("message", ""),
                    "task_id": agent.extract_task_id(resp),
                    "agent": agent_id,
                }

            # Normal return
            return resp

        except SupplyGraphAPIError as e:
            # Return LangGraph-friendly error response
            return {
                "status": "ERROR",
                "message": str(e),
                "api_code": e.api_code,
                "http_status": e.http_status,
                "details": e.errors,
            }

    # Attach metadata for LangChain/LangGraph
    tool.__name__ = name
    tool.__doc__ = description
    tool.description = description
    tool.agent_id = agent_id
    tool.manifest = agent.manifest

    return tool
