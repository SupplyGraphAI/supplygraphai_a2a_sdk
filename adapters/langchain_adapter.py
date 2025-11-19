#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : langchain_adapter.py
"""

from typing import Any, Dict, Optional, Callable, Union

from supplygraphai_a2a_sdk.client.agent_client import AgentClient


class SupplyGraphLangChainTool:
    """
    LangChain-compatible Tool wrapper for SupplyGraph A2A agents.

    Does NOT require LangChain to be installed in this SDK.
    The LangChain user can wrap this into langchain.tools.Tool:

        from langchain.tools import Tool
        sg_tool = SupplyGraphLangChainTool("tariff_calc", api_key="sk-...")
        tool = Tool(
            name="tariff_calc",
            description="SupplyGraph Tariff Calculation Agent",
            func=sg_tool.run,
        )
    """

    def __init__(
        self,
        agent_id: str,
        api_key: str,
        base_url: str = "https://agent.supplygraph.ai/api/v1/agents",
    ):
        self.agent_id = agent_id
        self.client = AgentClient(api_key=api_key, base_url=base_url)

    # --------------------------
    # Core execution wrapper
    # --------------------------
    def run(
        self,
        text: str,
        mode: str = "run",
        task_id: Optional[str] = None,
        stream: bool = False,
        **kwargs
    ) -> Any:
        """
        Unified interface for LangChain usage.

        Supports:
            - Normal run
            - Multi-turn (task_id)
            - status
            - results
        """
        if mode == "run":
            return self.client.run(
                self.agent_id, text=text, task_id=task_id, stream=stream, **kwargs
            )

        elif mode == "status":
            return self.client.status(self.agent_id, task_id)

        elif mode == "results":
            return self.client.results(self.agent_id, task_id)

        else:
            raise ValueError(f"Unsupported mode: {mode}")

    # --------------------------
    # LCEL Runnable version
    # --------------------------
    def as_runnable(self) -> Callable[[Dict[str, Any]], Any]:
        """
        Provide a Runnable-compatible function for LCEL:

        Example:
            tool = sg_tool.as_runnable()
            chain = tool | some_other_runnable
        """

        def runnable(input_dict: Dict[str, Any]) -> Any:
            text = input_dict.get("text", "")
            mode = input_dict.get("mode", "run")
            task_id = input_dict.get("task_id")
            stream = bool(input_dict.get("stream", False))
            extras = {
                k: v
                for k, v in input_dict.items()
                if k not in ("text", "mode", "task_id", "stream")
            }
            return self.run(
                text=text,
                mode=mode,
                task_id=task_id,
                stream=stream,
                **extras
            )

        runnable.__name__ = f"{self.agent_id}_runnable"
        return runnable


# ----------------------------------------------------------------------
# Helper factory
# ----------------------------------------------------------------------
def create_langchain_tool(
    agent_id: str,
    api_key: str,
    base_url: str = "https://agent.supplygraph.ai/api/v1/agents",
) -> SupplyGraphLangChainTool:
    """
    Helper to quickly create a LangChain tool instance.
        sg_tool = create_langchain_tool("tariff_calc", api_key="sk-...")
    """
    return SupplyGraphLangChainTool(agent_id, api_key, base_url)
