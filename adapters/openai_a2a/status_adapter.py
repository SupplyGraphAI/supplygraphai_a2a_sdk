#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    :
@File    : status_adapter.py

OpenAI A2A Status Adapter for SupplyGraph A2A Agents.

Converts SupplyGraph /run (mode=status) responses into
OpenAI-compatible `agent.run.status` objects.

Status objects represent the *current state* of an agent task,
including intermediate progress, reasoning steps, and metadata.

This file works in harmony with:
    - run_adapter.py
    - results_adapter.py
    - reasoning_sse_adapter.py
    - status_map.py
    - utils/
"""

from typing import Any, Dict, Optional, List

from supplygraphai_a2a_sdk.adapters.openai_a2a.status_map import map_sg_to_openai
from supplygraphai_a2a_sdk.adapters.openai_a2a.utils.extensions_builder import (
    build_sg_extensions,
)
from supplygraphai_a2a_sdk.adapters.openai_a2a.utils.timestamp import now_timestamp
from supplygraphai_a2a_sdk.adapters.openai_a2a.utils.content_extractor import (
    extract_output_from_sg_content,
)


class OpenAIA2AStatusAdapter:
    """
    Convert SupplyGraph status() responses → OpenAI Agent Run Status objects.

    Expected SG status envelope (simplified):

        {
          "success": true,
          "code": "TASK_RUNNING",
          "message": "Task in progress",
          "data": {
            "task_id": "t_123",
            "agent": "tariff_calc",
            "stage": "executing",
            "code": "TASK_RUNNING",
            "progress": 40,
            "intermediate_steps": [
                {"type": "thinking", "content": "Analyzing request..."},
            ],
            "timestamp": "2025-11-12T09:00:10Z",
            "content": null,
            "is_final": false
          }
        }

    Output:

        {
          "id": "t_123",
          "object": "agent.run.status",
          "agent_id": "tariff_calc",
          "status": "in_progress",
          "created_at": 1731970000,
          "steps": [...],
          "output": null,
          "required_action": null,
          "last_error": null,
          "metadata": {...},
          "extensions": {
              "supplygraph": {...}
          }
        }
    """

    def __init__(self, agent_id: str):
        self.agent_id = agent_id

    # ----------------------------------------------------------------------
    # Public factory
    # ----------------------------------------------------------------------
    def to_openai_status(self, sg_status: Dict[str, Any]) -> Dict[str, Any]:
        sg_code = sg_status.get("code", "")
        sg_data = sg_status.get("data", {}) or {}
        sg_meta = sg_status.get("metadata", {}) or {}

        # Map SG → OpenAI
        openai_status = map_sg_to_openai(sg_code)

        # Task ID resolution
        task_id = (
            sg_data.get("task_id")
            or sg_status.get("task_id")
            or f"sg_task_{now_timestamp()}"
        )

        created_ts = now_timestamp()

        status_obj: Dict[str, Any] = {
            "id": task_id,
            "object": "agent.run.status",
            "agent_id": self.agent_id,
            "status": openai_status,
            "created_at": created_ts,
            "steps": self._convert_steps(sg_data),
            "output": self._build_output_block(openai_status, sg_data),
            "required_action": None,
            "last_error": None,
            "metadata": self._extract_metadata(sg_status),
        }

        # SG extensions
        status_obj.update(build_sg_extensions(sg_data, sg_meta))

        # requires_action
        if openai_status == "requires_action":
            status_obj["required_action"] = self._build_required_action(sg_status)

        # failed
        if openai_status == "failed":
            status_obj["last_error"] = self._build_last_error(sg_status)

        return status_obj

    # ----------------------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------------------
    def _convert_steps(self, sg_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert SG "intermediate_steps" → OpenAI step objects.

        SG:
            [
              {"type": "thinking", "content": "..."},
              {"type": "action", "content": "..."},
            ]

        OpenAI:
            [
              {"type": "reasoning", "content": "...", "timestamp": ...}
            ]
        """
        sg_steps = sg_data.get("intermediate_steps", [])
        if not sg_steps:
            return []

        out = []
        for step in sg_steps:
            out.append({
                "type": step.get("type", "reasoning"),
                "content": step.get("content", ""),
                "timestamp": now_timestamp(),
            })
        return out

    def _extract_metadata(self, sg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        md = {}

        if "message" in sg:
            md["message"] = sg["message"]

        meta = sg.get("metadata", {}) or {}
        for key in ("agent", "timestamp", "credits_used"):
            if key in meta:
                md[key] = meta[key]

        return md or None

    def _build_output_block(self, openai_status: str, sg_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Only completed + requires_action should include output.
        """
        if openai_status not in ("completed", "requires_action"):
            return None

        content = sg_data.get("content")
        return extract_output_from_sg_content(content)

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

    def _build_last_error(self, sg: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "code": sg.get("code"),
            "message": sg.get("message", "Task failed."),
        }


# ----------------------------------------------------------------------
# Functional helper
# ----------------------------------------------------------------------
def build_openai_status(agent_id: str, sg_status: Dict[str, Any]) -> Dict[str, Any]:
    adapter = OpenAIA2AStatusAdapter(agent_id)
    return adapter.to_openai_status(sg_status)
