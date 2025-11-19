#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    :
@File    : results_adapter.py

OpenAI A2A Results Adapter for SupplyGraph A2A Agents.

Converts SupplyGraph /run (mode=results) responses into
OpenAI-compatible `agent.run.result` objects.

Results objects represent the *final or failed* output of a task.
They contain a normalized `output` block and final metadata.
"""

from typing import Any, Dict, Optional
from supplygraphai_a2a_sdk.adapters.openai_a2a.status_map import map_sg_to_openai
from supplygraphai_a2a_sdk.adapters.openai_a2a.utils.extensions_builder import (
    build_sg_extensions,
)
from supplygraphai_a2a_sdk.adapters.openai_a2a.utils.timestamp import now_timestamp
from supplygraphai_a2a_sdk.adapters.openai_a2a.utils.content_extractor import (
    extract_output_from_sg_content,
)


class OpenAIA2AResultsAdapter:
    """
    Convert SupplyGraph results() responses → OpenAI Agent Run Result objects.

    Expected SG fields:

        {
          "code": "TASK_COMPLETED",
          "message": "...",
          "data": {
            "task_id": "...",
            "content": str | { "type": "result", "data": {...} },
            "timestamp": "...",
            "agent": "tariff_calc"
          },
          "metadata": {
            "credits_used": 10,
            "timestamp": "..."
          }
        }

    Output:

        {
          "id": "t_123",
          "object": "agent.run.result",
          "agent_id": "tariff_calc",
          "status": "completed",
          "created_at": <unix>,
          "output": {
              "type": "json",
              "content": {...}
          },
          "required_action": null,
          "last_error": null,
          "metadata": {...},
          "extensions": { "supplygraph": {...} }
        }
    """

    def __init__(self, agent_id: str):
        self.agent_id = agent_id

    # ----------------------------------------------------------------------
    # PUBLIC FACTORY
    # ----------------------------------------------------------------------
    def to_openai_result(self, sg_result: Dict[str, Any]) -> Dict[str, Any]:
        sg_code = sg_result.get("code", "")
        sg_data = sg_result.get("data", {}) or {}
        sg_meta = sg_result.get("metadata", {}) or {}

        # SG → OpenAI status
        openai_status = map_sg_to_openai(sg_code)

        # task_id
        task_id = (
            sg_data.get("task_id")
            or sg_result.get("task_id")
            or f"sg_task_{now_timestamp()}"
        )

        created_ts = now_timestamp()

        result_obj: Dict[str, Any] = {
            "id": task_id,
            "object": "agent.run.result",
            "agent_id": self.agent_id,
            "status": openai_status,
            "created_at": created_ts,
            "output": None,
            "required_action": None,
            "last_error": None,
            "metadata": self._extract_metadata(sg_result),
        }

        # SG extensions (non-breaking)
        result_obj.update(build_sg_extensions(sg_data, sg_meta))

        # ------------------------------------------------------------------
        # Output handling
        # ------------------------------------------------------------------
        # completed → output must exist
        if openai_status == "completed":
            content = sg_data.get("content")
            result_obj["output"] = extract_output_from_sg_content(content)

        # failed → attach last_error
        elif openai_status == "failed":
            result_obj["last_error"] = self._build_last_error(sg_result)

        # requires_action (shouldn't happen in /results, but safe)
        elif openai_status == "requires_action":
            result_obj["required_action"] = self._build_required_action(sg_result)

        # other states return null output
        return result_obj

    # ----------------------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------------------
    def _extract_metadata(self, sg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        md = {}

        if "message" in sg:
            md["message"] = sg["message"]

        meta = sg.get("metadata", {}) or {}
        for key in ("timestamp", "credits_used", "agent"):
            if key in meta:
                md[key] = meta[key]

        return md or None

    def _build_last_error(self, sg: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "code": sg.get("code"),
            "message": sg.get("message", "Task failed."),
            "details": sg.get("errors"),
        }

    def _build_required_action(self, sg: Dict[str, Any]) -> Dict[str, Any]:
        data = sg.get("data", {}) or {}
        content = data.get("content")
        message = sg.get("message", "")

        if isinstance(content, str):
            prompt = content
        elif isinstance(content, dict) and "prompt" in content:
            prompt = content["prompt"]
        else:
            prompt = message or "Additional user input is required."

        return {
            "type": "awaiting_user",
            "message": prompt,
        }


# ----------------------------------------------------------------------
# Functional helper
# ----------------------------------------------------------------------
def build_openai_result(agent_id: str, sg_result: Dict[str, Any]) -> Dict[str, Any]:
    adapter = OpenAIA2AResultsAdapter(agent_id)
    return adapter.to_openai_result(sg_result)
