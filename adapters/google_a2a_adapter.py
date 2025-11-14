#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : google_a2a_adapter.py
"""
"""
Google A2A Adapter for SupplyGraph A2A Agents
Converts Google-style RPC calls (task.run/status/results)
into SupplyGraph A2A REST operations.
"""

from typing import Any, Dict, Optional

from ..client.agent_client import AgentClient
from ..utils.error_handler import SupplyGraphAPIError


class GoogleA2AAdapter:
    """
    Google-style A2A JSON-RPC adapter.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://agent.supplygraph.ai/api/v1/agents",
    ) -> None:
        self.client = AgentClient(api_key=api_key, base_url=base_url)

    # ------------------------------------------------------
    # Unified RPC call entry point
    # ------------------------------------------------------

    def call(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return self._dispatch(method, params)
        except SupplyGraphAPIError as e:
            return self._to_google_error(e)
        except Exception as e:
            return {
                "error": {
                    "code": "INTERNAL",
                    "message": str(e)
                }
            }

    # ------------------------------------------------------
    # Dispatcher for each RPC method
    # ------------------------------------------------------

    def _dispatch(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        agent = params.get("agent")
        if not agent:
            return self._simple_error("INVALID_ARGUMENT", "missing 'agent'")

        # ---------------- task.run ----------------
        if method in ("a2a.task.run", "task.run"):
            text = params.get("input") or params.get("text") or ""
            task_id = params.get("task_id")
            stream = bool(params.get("stream", False))

            extras = {
                k: v for (k, v) in params.items()
                if k not in ("agent", "input", "text", "task_id", "stream")
            }

            result = self.client.run(agent, text=text, task_id=task_id, stream=stream, **extras)

            # Streaming mode returns generator
            if stream:
                return {"result": result}

            # WAITING_USER mapping
            if result.get("code") == "WAITING_USER":
                return {
                    "result": {
                        "status": "WAITING_USER",
                        "message": result.get("message", ""),
                        "task_id": result.get("data", {}).get("task_id"),
                        "agent": agent,
                    }
                }

            return {"result": result}

        # ---------------- task.status ----------------
        if method in ("a2a.task.status", "task.status"):
            task_id = params.get("task_id")
            if not task_id:
                return self._simple_error("INVALID_ARGUMENT", "missing 'task_id'")
            result = self.client.status(agent, task_id)
            return {"result": result}

        # ---------------- task.results ----------------
        if method in ("a2a.task.results", "task.results"):
            task_id = params.get("task_id")
            if not task_id:
                return self._simple_error("INVALID_ARGUMENT", "missing 'task_id'")
            result = self.client.results(agent, task_id)
            return {"result": result}

        return self._simple_error("METHOD_NOT_FOUND", f"unsupported method {method}")

    # ------------------------------------------------------
    # Helper to generate Google-style JSON errors
    # ------------------------------------------------------

    def _simple_error(self, code: str, message: str) -> Dict[str, Any]:
        return {
            "error": {
                "code": code,
                "message": message
            }
        }

    def _to_google_error(self, e: SupplyGraphAPIError) -> Dict[str, Any]:
        return {
            "error": {
                "code": e.api_code or "INTERNAL",
                "message": e.args[0],
                "details": e.errors,
                "http_status": e.http_status,
            }
        }
