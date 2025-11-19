#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    :
@File    : run_adapter.py

OpenAI A2A Run Adapter for SupplyGraph A2A Agents.

Converts SupplyGraph /run responses into OpenAI-compatible `agent.run`
objects.

This adapter is the central bridge between the SupplyGraph A2A protocol
and the OpenAI Agent Runtime run object schema.
"""

from typing import Any, Dict, Optional

from supplygraphai_a2a_sdk.adapters.openai_a2a.status_map import map_sg_to_openai
from supplygraphai_a2a_sdk.adapters.openai_a2a.utils.content_extractor import (
    extract_output_from_sg_content,
)
from supplygraphai_a2a_sdk.adapters.openai_a2a.utils.extensions_builder import (
    build_sg_extensions,
)
from supplygraphai_a2a_sdk.adapters.openai_a2a.utils.timestamp import now_timestamp


class OpenAIA2ARunAdapter:
    """
    Convert SupplyGraph A2A /run responses → OpenAI Agent Run objects.

    Expected SG envelope (simplified):

        {
          "success": true,
          "code": "TASK_ACCEPTED",
          "message": "Task accepted and queued for execution.",
          "data": {
            "task_id": "t_123",
            "agent": "example_agent",
            "stage": "executing",
            "code": "TASK_ACCEPTED",
            "progress": 0,
            "timestamp": "2025-11-12T09:00:10Z",
            "is_final": true,
            "content": ""
          },
          "metadata": {
            "agent": "example_agent",
            "timestamp": "2025-11-12T09:00:10Z",
            "credits_used": 0
          },
          "errors": null
        }

    Output (OpenAI-style run object):

        {
          "id": "t_123",
          "object": "agent.run",
          "agent_id": "tariff_calc",
          "status": "in_progress",
          "created_at": 1731970000,
          "input": {...},
          "output": {...} | null,
          "required_action": {...} | null,
          "last_error": {...} | null,
          "metadata": {...},
          "extensions": {
              "supplygraph": {...}
          }
        }
    """

    def __init__(self, agent_id: str):
        self.agent_id = agent_id

    # ------------------------------------------------------------------
    # Public entry
    # ------------------------------------------------------------------
    def to_openai_run(self, sg_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a single SG /run response → OpenAI run object.
        """

        sg_code = sg_result.get("code") or ""
        sg_data = sg_result.get("data", {}) or {}
        sg_meta = sg_result.get("metadata", {}) or {}

        # Map SG code → OpenAI run.status
        openai_status = map_sg_to_openai(sg_code)

        # Task id resolution
        task_id = (
            sg_data.get("task_id")
            or sg_result.get("task_id")
            or f"sg_task_{now_timestamp()}"
        )

        created_ts = self._extract_created_at(sg_data, sg_meta)

        run_obj: Dict[str, Any] = {
            "id": task_id,
            "object": "agent.run",
            "agent_id": self.agent_id,
            "status": openai_status,          # in_progress / requires_action / completed / failed / cancelled
            "created_at": created_ts,
            "input": self._extract_input(sg_result),
            "output": None,
            "required_action": None,
            "last_error": None,
            "metadata": self._extract_metadata(sg_result),
        }

        # Attach extensions.supplygraph with SG-specific fields
        run_obj.update(build_sg_extensions(sg_data, sg_meta))

        # Attach output (only when it makes sense)
        run_obj["output"] = self._build_output_block(openai_status, sg_data)

        # Attach required_action when WAITING_USER / requires_action
        if openai_status == "requires_action":
            run_obj["required_action"] = self._build_required_action(sg_result)

        # Attach last_error for failed states
        if openai_status == "failed":
            run_obj["last_error"] = self._build_last_error(sg_result)

        return run_obj

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _extract_created_at(self, sg_data: Dict[str, Any], sg_meta: Dict[str, Any]) -> int:
        """
        Normalize created_at timestamp (int seconds).
        Prefer SG metadata timestamps if present, otherwise use now().
        """
        # You could parse SG ISO8601 timestamps to epoch here if needed.
        # For now we just use now_timestamp() for simplicity.
        return now_timestamp()

    def _extract_input(self, sg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract the logical "input" payload for the run.

        For SupplyGraph A2A, the original request is not fully echoed
        back in the response, but we typically at least include:

            data.input      → original text (if agent chooses to return)
            data.extra      → any extra structured arguments

        This method is defensive and will return None when no input
        information is available.
        """
        data = sg.get("data", {}) or {}
        inp: Dict[str, Any] = {}

        if "input" in data:
            inp["text"] = data["input"]

        extra = data.get("extra")
        if isinstance(extra, dict):
            # Merge extra fields as top-level input properties
            for k, v in extra.items():
                if k not in inp:
                    inp[k] = v

        return inp or None

    def _extract_metadata(self, sg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract lightweight metadata to attach directly to the run object.

        Heavier or SG-specific fields should go into extensions.supplygraph.
        """
        md: Dict[str, Any] = {}

        if "message" in sg:
            md["message"] = sg["message"]

        sg_meta = sg.get("metadata", {}) or {}
        for key in ("agent", "timestamp", "version"):
            if key in sg_meta:
                md[key] = sg_meta[key]

        return md or None

    def _build_output_block(self, openai_status: str, sg_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Build the OpenAI-style 'output' block.

        Rules:
          - When status == completed: use final structured/text content.
          - When status == requires_action: expose human-readable text content
            to guide the caller on what to do next.
          - Otherwise: do not attach output (return None).
        """
        content = sg_data.get("content")

        # Only completed or requires_action should expose content.
        if openai_status not in ("completed", "requires_action"):
            return None

        output = extract_output_from_sg_content(content)
        if not output:
            return None

        # Normalize to OpenAI-like structure:
        #   { "type": "text" | "json", "content": ... }
        return output

    def _build_required_action(self, sg: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build OpenAI-style required_action block.

        For SG WAITING_USER (mapped to requires_action), we represent it as:
            {
              "type": "awaiting_user",
              "message": "<text to present to the user>"
            }
        """
        data = sg.get("data", {}) or {}
        content = data.get("content")
        message = sg.get("message") or ""

        # Prefer SG content text as prompt to the user
        text_message = None
        if isinstance(content, str):
            text_message = content
        elif isinstance(content, dict) and "prompt" in content:
            text_message = content.get("prompt")

        if not text_message:
            text_message = message or "Additional user input is required to continue this task."

        return {
            "type": "awaiting_user",
            "message": text_message,
        }

    def _build_last_error(self, sg: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build a minimal last_error block for failed runs.

        OpenAI run.last_error typically looks like:
            {
              "code": "INVALID_REQUEST",
              "message": "Missing required field ..."
            }
        """
        return {
            "code": sg.get("code"),
            "message": sg.get("message", "An error occurred."),
        }


# ----------------------------------------------------------------------
# Functional helper (SDK convenience)
# ----------------------------------------------------------------------
def build_openai_run(agent_id: str, sg_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience helper: build OpenAI run from SG /run response.

    This preserves the previous public API shape while routing through
    the new, fully OpenAI-compatible adapter.
    """
    adapter = OpenAIA2ARunAdapter(agent_id=agent_id)
    return adapter.to_openai_run(sg_result)
