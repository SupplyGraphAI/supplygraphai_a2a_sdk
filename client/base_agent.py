#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : base_agent.py

Base class for all SupplyGraph A2A agents.
Manifest-aware, supports multi-round execution and helper utilities.
"""

from typing import Any, Dict, Optional
from supplygraphai_a2a_sdk.client.agent_client import AgentClient


class BaseAgent:
    """
    Base class for all SupplyGraph agents.

    Provides:
    - automatic manifest loading
    - unified run/status/results
    - multi-round helpers (task_id extraction, WAITING_USER detection)
    """

    def __init__(self, client: AgentClient, agent_id: str) -> None:
        self.client = client
        self.agent_id = agent_id
        self.manifest: Dict[str, Any] = self.client.manifest(agent_id)

    # ------------------------------------------------------
    # Unified high-level API wrappers
    # ------------------------------------------------------

    def run(
        self,
        text: str,
        task_id: Optional[str] = None,
        stream: bool = False,
        **kwargs,
    ) -> Any:
        """
        Start or continue an agent task.

        - If task_id=None: create a new task
        - If task_id provided: continue an existing task (multiround)
        """
        payload = {}
        if task_id:
            payload["task_id"] = task_id

        return self.client.run(
            agent_id=self.agent_id,
            text=text,
            stream=stream,
            **payload,
            **kwargs,
        )

    def status(self, task_id: str, **kwargs) -> Dict[str, Any]:
        """Query task status."""
        return self.client.status(
            agent_id=self.agent_id,
            task_id=task_id,
            **kwargs,
        )

    def results(self, task_id: str, **kwargs) -> Dict[str, Any]:
        """Retrieve final task results."""
        return self.client.results(
            agent_id=self.agent_id,
            task_id=task_id,
            **kwargs,
        )

    # ------------------------------------------------------
    # Helper utilities for multiround execution
    # ------------------------------------------------------

    @staticmethod
    def extract_task_id(response: Dict[str, Any]) -> Optional[str]:
        """Extract task_id from the agent response."""
        return response.get("data", {}).get("task_id")

    @staticmethod
    def needs_user_input(response: Dict[str, Any]) -> bool:
        """Return True if the agent requires user confirmation or more info."""
        return response.get("code") == "WAITING_USER"

    @staticmethod
    def is_finished(response: Dict[str, Any]) -> bool:
        """Return True if agent completed successfully."""
        return response.get("code") == "TASK_COMPLETED"

    @staticmethod
    def is_failed(response: Dict[str, Any]) -> bool:
        """Return True if agent failed."""
        return response.get("code") == "TASK_FAILED"
