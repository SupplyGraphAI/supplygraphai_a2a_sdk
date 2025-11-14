#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    :
@File    : autogen_adapter.py
"""

from typing import Any, Dict, Optional, Callable

from ..client.agent_client import AgentClient


class AutoGenTool:
    """
    Adapter to expose a SupplyGraph A2A Agent as an AutoGen tool.

    Usage example (AutoGen):
        from autogen import AssistantAgent, Tool

        sg_tool = AutoGenTool(agent_id="tariff_calc", api_key="sk-...")

        assistant = AssistantAgent(
            name="assistant",
            tools=[sg_tool.to_autogen_tool()],
        )

    The tool supports:
    - Single-turn run()
    - Multi-turn run() with task_id
    """

    def __init__(
        self,
        agent_id: str,
        api_key: str,
        base_url: str = "https://agent.supplygraph.ai/api/v1/agents",
    ) -> None:
        self.agent_id = agent_id
        self.client = AgentClient(api_key=api_key, base_url=base_url)

    # ------------------------
    # Core execution method
    # ------------------------
    def run(
        self,
        text: str,
        task_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        return self.client.run(
            agent_id=self.agent_id,
            text=text,
            task_id=task_id,
            **kwargs,
        )

    def status(self, task_id: str, **kwargs: Any) -> Dict[str, Any]:
        return self.client.status(
            agent_id=self.agent_id,
            task_id=task_id,
            **kwargs,
        )

    def results(self, task_id: str, **kwargs: Any) -> Dict[str, Any]:
        return self.client.results(
            agent_id=self.agent_id,
            task_id=task_id,
            **kwargs,
        )

    # ------------------------
    # AutoGen Tool wrapper
    # ------------------------
    def to_autogen_tool(self) -> Callable[..., Any]:
        """
        Returns a callable suitable for AutoGen's Tool API.

        AutoGen expects a signature like:
            tool(input: str, **kwargs) -> Any
        """
        def tool(text: str, **kwargs: Any) -> Any:
            return self.run(text=text, **kwargs)

        tool.__name__ = self.agent_id
        tool.__doc__ = f"AutoGen tool wrapper for SupplyGraph agent '{self.agent_id}'."

        return tool
