#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    :
@File    : llamaindex_adapter.py
"""

from typing import Any, Dict, Optional, Callable

from supplygraphai_a2a_sdk.client.agent_client import AgentClient


class LlamaIndexToolWrapper:
    """
    LlamaIndex-compatible tool wrapper for SupplyGraph A2A agents.

    Zero dependency on llama_index itself.
    The host project can do:

        from llama_index.core.tools import FunctionTool
        tool = FunctionTool.from_defaults(
            fn=sg_tool.as_function(),
            name="tariff_calc"
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

    # ------------------------------------------------------------------
    # Unified Run Function (for LlamaIndex FunctionTool)
    # ------------------------------------------------------------------
    def as_function(self) -> Callable[..., Any]:
        """
        Return a callable that matches LlamaIndex's FunctionTool requirements.
        """
        def fn(
            text: str,
            mode: str = "run",
            task_id: Optional[str] = None,
            stream: bool = False,
            **kwargs: Any
        ) -> Any:

            if mode == "run":
                return self.client.run(
                    self.agent_id, text=text, task_id=task_id, stream=stream, **kwargs
                )

            elif mode == "status":
                if not task_id:
                    raise ValueError("task_id required for status()")
                return self.client.status(self.agent_id, task_id)

            elif mode == "results":
                if not task_id:
                    raise ValueError("task_id required for results()")
                return self.client.results(self.agent_id, task_id)

            else:
                raise ValueError(f"Unsupported mode: {mode}")

        fn.__name__ = f"{self.agent_id}_tool"
        return fn

    # ------------------------------------------------------------------
    # QueryEngine wrapper (for non-tool use)
    # ------------------------------------------------------------------
    def as_query_engine(self) -> Callable[[str], Any]:
        """
        Provide a simple QueryEngine-like callable.
        Useful when integrating with LlamaIndex agent tool pipelines.
        """
        def query_engine(query: str) -> Any:
            return self.client.run(self.agent_id, text=query)

        query_engine.__name__ = f"{self.agent_id}_query_engine"
        return query_engine


# ----------------------------------------------------------------------
# Factory Helper
# ----------------------------------------------------------------------
def create_llamaindex_tool(
    agent_id: str,
    api_key: str,
    base_url: str = "https://agent.supplygraph.ai/api/v1/agents",
) -> LlamaIndexToolWrapper:
    return LlamaIndexToolWrapper(agent_id=agent_id, api_key=api_key, base_url=base_url)
