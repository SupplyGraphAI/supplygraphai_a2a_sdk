#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    :
@File    : airflow_adapter.py

Airflow integration adapter for SupplyGraph A2A agents.

This module does NOT import Airflow directly. This avoids introducing
Airflow as a dependency inside the SDK. Instead, users can mix this class
into any Airflow BaseOperator within their own Airflow project.

Example usage inside an Airflow project:

    from airflow.models import BaseOperator
    from supplygraphai_a2a_sdk.adapters.airflow_adapter import SupplyGraphAirflowOperatorMixin

    class TariffCalcOperator(BaseOperator, SupplyGraphAirflowOperatorMixin):
        pass

    task = TariffCalcOperator(
        task_id="tariff_job",
        agent_id="tariff_calc",
        api_key="sk-...",
        text="import 100kg ice cream from CN",
        mode="run",
        task_id_override=None,
    )
"""

from typing import Any, Dict, Optional
from supplygraphai_a2a_sdk.client.agent_client import AgentClient


class SupplyGraphAirflowOperatorMixin:
    """
    A mixin that injects SupplyGraph A2A Agent execution logic into an
    Airflow BaseOperator.

    Notes:
    - Airflow BaseOperator must appear BEFORE this mixin in the class MRO.
    - The subclass must call super().__init__(...) to initialize BaseOperator.
    - This mixin implements only the execute() method and the A2A agent logic.
    """

    def __init__(
        self,
        *,
        agent_id: str,
        api_key: str,
        text: Optional[str] = "",
        mode: str = "run",
        task_id_override: Optional[str] = None,
        stream: bool = False,
        base_url: str = "https://agent.supplygraph.ai/api/v1/agents",
        **kwargs,
    ) -> None:
        """
        Initialize the mixin and its A2A client.

        Parameters:
            agent_id        - SupplyGraph A2A agent identifier
            api_key         - API key for the agent service
            text            - User text input for mode='run'
            mode            - 'run', 'status', or 'results'
            task_id_override - Existing A2A task_id for multi-round workflows
            stream          - Whether to enable SSE streaming (run mode only)
            base_url        - Base URL of the SupplyGraph A2A gateway

        This constructor MUST be invoked AFTER BaseOperator.__init__(...) in
        the subclass’s __init__().
        """
        self.agent_id = agent_id
        self.text = text
        self.mode = mode
        self.task_id_override = task_id_override
        self.stream = stream

        self.client = AgentClient(api_key=api_key, base_url=base_url)

        # Pass through any remaining keyword arguments to BaseOperator
        super().__init__(**kwargs)

    # ----------------------------------------------------------------------
    # Airflow execution entrypoint
    # ----------------------------------------------------------------------
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the operator inside an Airflow DAG.

        Returns:
            A dictionary containing the A2A agent response, which is also
            pushed via XCom automatically by Airflow.
        """
        if self.mode == "run":
            result = self.client.run(
                agent_id=self.agent_id,
                text=self.text,
                task_id=self.task_id_override,
                stream=self.stream,
            )

        elif self.mode == "status":
            if not self.task_id_override:
                raise ValueError("task_id_override is required for mode='status'")
            result = self.client.status(
                agent_id=self.agent_id,
                task_id=self.task_id_override,
            )

        elif self.mode == "results":
            if not self.task_id_override:
                raise ValueError("task_id_override is required for mode='results'")
            result = self.client.results(
                agent_id=self.agent_id,
                task_id=self.task_id_override,
            )

        else:
            raise ValueError(f"Unsupported mode '{self.mode}' for Airflow operator")

        return result


# ----------------------------------------------------------------------
# Factory helper
# ----------------------------------------------------------------------
def create_airflow_operator(
    operator_cls,
    *,
    agent_id: str,
    api_key: str,
    **kwargs,
):
    """
    Dynamically create an Airflow operator class mixed with
    SupplyGraphAirflowOperatorMixin.

    Example:

        from airflow.models import BaseOperator
        from supplygraphai_a2a_sdk.adapters.airflow_adapter import create_airflow_operator

        TariffOperator = create_airflow_operator(
            BaseOperator,
            agent_id="tariff_calc",
            api_key="sk-...",
        )

        task = TariffOperator(
            task_id="job1",
            text="import 50kg cheese from FR",
            mode="run",
        )

    The returned operator class inherits:
        operator_cls          (e.g., BaseOperator)
        SupplyGraphAirflowOperatorMixin
    """

    class _DynamicAirflowOperator(operator_cls, SupplyGraphAirflowOperatorMixin):
        """Dynamically generated Airflow operator class."""
        pass

    return _DynamicAirflowOperator(agent_id=agent_id, api_key=api_key, **kwargs)
