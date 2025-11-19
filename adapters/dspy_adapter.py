#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    :
@File    : dspy_adapter.py
"""

from typing import Any, Optional, Dict, Callable

from supplygraphai_a2a_sdk.client.agent_client import AgentClient


class DSPyPredictorWrapper:
    """
    DSPy-compatible predictor wrapper for SupplyGraph A2A agents.

    Designed to be used with:
        - dspy.Predictor
        - dspy.Module
        - dspy.Signature-based inference

    This adapter does NOT import DSPy inside the SDK.
    The host project will import DSPy and wrap this class’ predict() method.

    Example:

        import dspy
        sg = create_dspy_predictor("tariff_calc", api_key="sk-...")

        class MyModule(dspy.Module):
            def __init__(self):
                super().__init__()
                self.tool = sg.as_predictor()

            def forward(self, text: str):
                return self.tool(text=text)["data"]["content"]

        m = MyModule()
        m("import 100kg chocolate from FR")
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
    # DSPy-style predictor function
    # ------------------------------------------------------------------
    def as_predictor(self) -> Callable[..., Any]:
        """
        Return a function matching DSPy's Predictor signature:
            output = predictor(**inputs)

        Input:
            - text
            - mode/run
            - task_id
            - stream
            - Any additional A2A agent parameters

        Output:
            Direct A2A JSON.
        """

        def predictor(
                text: str,
                mode: str = "run",
                task_id: Optional[str] = None,
                stream: bool = False,
                **kwargs
        ) -> Any:

            if mode == "run":
                return self.client.run(
                    self.agent_id, text=text, task_id=task_id, stream=stream, **kwargs
                )

            elif mode == "status":
                if not task_id:
                    raise ValueError("task_id is required for status()")
                return self.client.status(self.agent_id, task_id)

            elif mode == "results":
                if not task_id:
                    raise ValueError("task_id is required for results()")
                return self.client.results(self.agent_id, task_id)

            else:
                raise ValueError(f"Unsupported DSPy predictor mode: {mode}")

        predictor.__name__ = f"{self.agent_id}_dspy_predictor"
        return predictor


# ----------------------------------------------------------------------
# Factory Helper
# ----------------------------------------------------------------------
def create_dspy_predictor(
        agent_id: str,
        api_key: str,
        base_url: str = "https://agent.supplygraph.ai/api/v1/agents"
) -> DSPyPredictorWrapper:
    return DSPyPredictorWrapper(agent_id=agent_id, api_key=api_key, base_url=base_url)
