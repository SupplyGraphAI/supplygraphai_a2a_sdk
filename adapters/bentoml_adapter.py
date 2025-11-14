#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    :
@File    : bentoml_adapter.py
@Description:
    BentoML integration adapter for exposing SupplyGraph A2A agents
    as BentoML Runners and Services.

    This module does NOT import BentoML directly to avoid hard dependencies
    inside the SDK. The host application can use these classes to build
    BentoML Services without modifying the agent logic.

    Example usage inside a BentoML host application:

        from bentoml import Service, Runner, io
        from supplygraphai_a2a_sdk.adapters import (
            create_bentoml_runner,
            BentoMLServiceWrapper,
        )

        runner = Runner(create_bentoml_runner("tariff_calc", api_key="sk-...").run_task)
        svc = Service("tariff_calc_service", runners=[runner])
        sg_service = BentoMLServiceWrapper(runner)

        @svc.api(input=io.JSON(), output=io.JSON())
        def run_task(data):
            # data is a dict, e.g.:
            #   {"mode": "run", "text": "...", "task_id": null, "stream": false}
            return sg_service.handle_request(data)
"""

from typing import Any, Dict, Optional

from ..client.agent_client import AgentClient
from ..client.base_agent import BaseAgent
from ..utils.error_handler import SupplyGraphAPIError


class BentoMLRunnerWrapper:
    """
    BentoML Runner wrapper for SupplyGraph A2A agents.

    This wrapper provides a standard .run_task(payload: dict) method that
    BentoML Runner instances can call. The logic is:

        - mode = "run"     → agent.run(...)
        - mode = "status"  → agent.status(...)
        - mode = "results" → agent.results(...)

    It is:
        - manifest-aware
        - multiround-capable via task_id
        - WAITING_USER-aware
        - streaming-capable (returns generator when stream=True)

    Typical usage in a BentoML app:

        from bentoml import Runner
        from supplygraphai_a2a_sdk.adapters import create_bentoml_runner

        runner = Runner(create_bentoml_runner("tariff_calc", api_key="sk-...").run_task)
    """

    def __init__(
        self,
        agent_id: str,
        api_key: str,
        base_url: str = "https://agent.supplygraph.ai/api/v1/agents",
    ) -> None:
        self.agent_id = agent_id
        client = AgentClient(api_key=api_key, base_url=base_url)
        # Use BaseAgent so we share the same behavior as other adapters
        self.agent = BaseAgent(client, agent_id)

    def run_task(self, payload: Dict[str, Any]) -> Any:
        """
        Generic runner entrypoint. The payload may contain:

            {
                "mode": "run" | "status" | "results",
                "text": "...",
                "task_id": "...",
                "stream": false,
                ...
            }

        Returns:
            - For mode='run' with stream=False:
                final JSON envelope from the agent
            - For mode='run' with stream=True:
                SSE generator (to be handled by the host)
            - For mode='status' / 'results':
                status/results JSON
            - For WAITING_USER:
                normalized dict:
                    {
                        "status": "WAITING_USER",
                        "message": "...",
                        "task_id": "...",
                        "agent": "<agent_id>",
                    }
            - For errors:
                normalized error dict
        """
        mode = payload.get("mode", "run")
        text = payload.get("text") or payload.get("input") or ""
        task_id = payload.get("task_id")
        stream = bool(payload.get("stream", False))

        # Pass through any extra fields to the agent
        extras = {
            k: v
            for (k, v) in payload.items()
            if k not in ("mode", "text", "input", "task_id", "stream")
        }

        try:
            # ----------------- RUN -----------------
            if mode == "run":
                result = self.agent.run(
                    text=text,
                    task_id=task_id,
                    stream=stream,
                    **extras,
                )

                # Streaming: result is a generator, we return it as-is
                if stream:
                    return result

                # WAITING_USER: normalize for BentoML callers
                if self.agent.needs_user_input(result):
                    return {
                        "status": "WAITING_USER",
                        "message": result.get("message", ""),
                        "task_id": self.agent.extract_task_id(result),
                        "agent": self.agent_id,
                    }

                return result

            # ----------------- STATUS -----------------
            if mode == "status":
                if not task_id:
                    return {
                        "status": "ERROR",
                        "message": "task_id is required for mode='status'",
                    }
                return self.agent.status(task_id=task_id, **extras)

            # ----------------- RESULTS -----------------
            if mode == "results":
                if not task_id:
                    return {
                        "status": "ERROR",
                        "message": "task_id is required for mode='results'",
                    }
                return self.agent.results(task_id=task_id, **extras)

            # ----------------- UNSUPPORTED MODE -----------------
            return {
                "status": "ERROR",
                "message": f"Unsupported mode: {mode}",
            }

        except SupplyGraphAPIError as e:
            # Normalize API errors for BentoML callers
            return {
                "status": "ERROR",
                "message": str(e),
                "api_code": getattr(e, "api_code", None),
                "http_status": getattr(e, "http_status", getattr(e, "status_code", None)),
                "details": getattr(e, "errors", getattr(e, "payload", {})),
            }


class BentoMLServiceWrapper:
    """
    Thin service wrapper around BentoMLRunnerWrapper.

    This class is intentionally minimal. It simply forwards the request
    payload to the runner and returns the result. The host BentoML Service
    is responsible for wiring HTTP <-> JSON <-> this wrapper.

    Example:

        runner = Runner(create_bentoml_runner("tariff_calc", api_key="sk-...").run_task)
        svc = Service("tariff_calc_service", runners=[runner])
        sg_service = BentoMLServiceWrapper(runner)

        @svc.api(input=io.JSON(), output=io.JSON())
        def run_task(data):
            return sg_service.handle_request(data)
    """

    def __init__(self, runner: BentoMLRunnerWrapper) -> None:
        self.runner = runner

    def handle_request(self, payload: Dict[str, Any]) -> Any:
        """
        Entry point that a BentoML Service API function can call.
        """
        return self.runner.run_task(payload)


# ----------------------------------------------------------------------
# Helper factory functions
# ----------------------------------------------------------------------
def create_bentoml_runner(
    agent_id: str,
    api_key: str,
    base_url: str = "https://agent.supplygraph.ai/api/v1/agents",
) -> BentoMLRunnerWrapper:
    """
    Factory function for generating a BentoML Runner wrapper.

    Typical usage:

        from bentoml import Runner
        from supplygraphai_a2a_sdk.adapters import create_bentoml_runner

        runner = Runner(create_bentoml_runner("tariff_calc", api_key="sk-...").run_task)
    """
    return BentoMLRunnerWrapper(
        agent_id=agent_id,
        api_key=api_key,
        base_url=base_url,
    )


def create_bentoml_service(
    runner: BentoMLRunnerWrapper,
) -> BentoMLServiceWrapper:
    """
    Factory function for generating a BentoML Service wrapper.

    This does NOT create a bentoml.Service instance by itself. Instead, it
    returns a thin wrapper that you can call inside your BentoML Service:

        runner = Runner(create_bentoml_runner("tariff_calc", api_key="sk-...").run_task)
        svc = Service("tariff_calc_service", runners=[runner])
        sg_service = create_bentoml_service(runner)

        @svc.api(input=io.JSON(), output=io.JSON())
        def run_task(data):
            return sg_service.handle_request(data)
    """
    return BentoMLServiceWrapper(runner)
