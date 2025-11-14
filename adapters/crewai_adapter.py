#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : crewai_adapter.py
"""
"""
CrewAI Adapter for SupplyGraph A2A Agents
Fully manifest-aware and multiround-capable.
"""

from typing import Any, Dict, Optional

from ..client.agent_client import AgentClient
from ..client.base_agent import BaseAgent
from ..utils.error_handler import SupplyGraphAPIError


class CrewAITool:
    """
    Expose a SupplyGraph Agent as a CrewAI Tool.

    Supports:
    - multiround execution (task_id)
    - WAITING_USER (request for more info)
    - streaming (THINKING)
    - manifest-aware name & description
    """

    def __init__(
        self,
        agent_id: str,
        api_key: str,
        base_url: str = "https://agent.supplygraph.ai/api/v1/agents",
    ) -> None:
        self.agent_id = agent_id
        self.client = AgentClient(api_key=api_key, base_url=base_url)

        # Use BaseAgent to load manifest & helpers
        self.agent = BaseAgent(self.client, agent_id)

        # CrewAI needs a name and description
        self.name = self.agent.manifest.get("name", agent_id)
        self.description = self.agent.manifest.get("description", "")

    # ------------------------------------------------------
    # CrewAI entry point
    # ------------------------------------------------------

    def run(
        self,
        text: str,
        task_id: Optional[str] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        """
        Execute the agent via CrewAI.

        Returns:
            - normal result (run/status/results)
            - WAITING_USER → special cue for CrewAI to continue the chain
        """

        try:
            resp = self.agent.run(text, task_id=task_id, stream=stream, **kwargs)

            # -----------------------------
            # STREAM MODE
            # -----------------------------
            if stream:
                return resp  # parse_sse generator

            # -----------------------------
            # WAITING_USER → Needs more info
            # -----------------------------
            if self.agent.needs_user_input(resp):
                return {
                    "type": "waiting_user",
                    "message": resp.get("message", ""),
                    "task_id": self.agent.extract_task_id(resp),
                    "agent": self.agent_id,
                }

            return resp

        except SupplyGraphAPIError as e:
            # CrewAI friendly error structure
            return {
                "type": "error",
                "agent": self.agent_id,
                "error": str(e),
                "api_code": e.api_code,
                "http_status": e.http_status,
                "details": e.errors,
            }
