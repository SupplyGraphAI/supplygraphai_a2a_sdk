#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : reasoning_sse_adapter.py

OpenAI A2A SSE (Server-Sent Events) Adapter for SupplyGraph A2A Agents.

SupplyGraph SSE event format (example):
{
  "event": "stream",
  "data": {
      "task_id": "t_123",
      "agent": "tariff_calc",
      "stage": "interpreting",
      "code": "THINKING",
      "reasoning": ["Analyzing input..."],
      "timestamp": "...",
      "is_final": false
  }
}

This adapter converts SupplyGraph A2A streaming events into
OpenAI-compatible reasoning events:

    - event: step.delta
      data: {"delta": {"thinking": "<string>"}, "index": <int>, "delta_index": <int>, ...}

    - event: step
      data: {"step": {"thinking": ["<string>", ...]}, "index": <int>, ...}

    - event: completed
      data: {"status": "completed", ...}

The goal is to be as close as possible to the OpenAI Agents Runtime
reasoning streaming format, so that upstream runtimes and UIs can
consume these frames without any SupplyGraph-specific knowledge.
"""

from typing import Dict, Any, Generator, Iterable, List
import json
import time


class OpenAIA2AReasoningSSEAdapter:
    """
    Convert SupplyGraph A2A streaming events into OpenAI-style
    reasoning SSE events.
    """

    def __init__(self, agent_id: str) -> None:
        # agent_id is kept for potential future extensions (e.g. tracing),
        # but it is intentionally not included in the public payload
        # to keep the format strictly OpenAI-compatible.
        self.agent_id = agent_id

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def wrap_stream(
        self,
        sg_sse_stream: Iterable[Dict[str, Any]],
    ) -> Generator[str, None, None]:
        """
        Wrap a SupplyGraph SSE generator/iterator and yield OpenAI
        SSE frames as raw strings.

        Input items must be dicts shaped like:

            {"event": "stream", "data": {...}}
            {"event": "end", "data": "[DONE]"}

        or other event types that can be safely ignored.

        Output frames are strings formatted as:

            event: step.delta
            data: {...}

            event: step
            data: {...}

            event: completed
            data: {...}

        Each frame is terminated by a blank line, as required by SSE.
        """

        def generator() -> Generator[str, None, None]:
            step_index = 0
            delta_index = 0

            for sg_evt in sg_sse_stream:
                evt_type = sg_evt.get("event")
                payload = sg_evt.get("data", {})

                # Explicit end-of-stream marker from the server
                if evt_type == "end":
                    break

                # We only care about streaming events
                if evt_type != "stream":
                    continue

                # Extract reasoning lines from the SupplyGraph payload
                reasoning_lines = self._extract_reasoning_lines(payload)
                if not reasoning_lines:
                    # No reasoning content in this event → skip
                    continue

                # Emit one step.delta per reasoning line
                for line in reasoning_lines:
                    delta_body = {
                        "delta": {
                            "thinking": line
                        },
                        # index is the logical step index this delta belongs to
                        "index": step_index,
                        # monotonically increasing delta index (global within stream)
                        "delta_index": delta_index,
                        "timestamp": int(time.time()),
                    }
                    delta_index += 1
                    yield self._format_sse("step.delta", delta_body)

                # Emit a consolidated step event for this batch
                step_body = {
                    "step": {
                        "thinking": reasoning_lines
                    },
                    "index": step_index,
                    "timestamp": int(time.time()),
                }
                step_index += 1
                yield self._format_sse("step", step_body)

            # When the SupplyGraph stream finishes (normally or via "end"),
            # emit a final OpenAI-compatible "completed" event.
            completed_body = {
                "status": "completed",
                "timestamp": int(time.time()),
            }
            yield self._format_sse("completed", completed_body)

        return generator()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _extract_reasoning_lines(self, payload: Dict[str, Any]) -> List[str]:
        """
        Extract reasoning lines from a SupplyGraph SSE payload.

        Supported shapes:

        1) Direct THINKING frame (stream_event_schema):
            {
              "task_id": "...",
              "agent": "...",
              "stage": "interpreting" | "executing",
              "code": "THINKING",
              "reasoning": ["...", "..."],
              ...
            }

        2) Wrapped in a full A2A envelope:
            {
              "success": true,
              "code": "TASK_ACCEPTED",
              "data": {
                "task_id": "...",
                "reasoning": ["...", "..."],
                ...
              },
              ...
            }
        """
        # Case 1: direct reasoning array
        if isinstance(payload, dict) and isinstance(payload.get("reasoning"), list):
            return [str(x) for x in payload["reasoning"]]

        # Case 2: full envelope with nested data.reasoning
        if isinstance(payload, dict):
            data = payload.get("data")
            if isinstance(data, dict) and isinstance(data.get("reasoning"), list):
                return [str(x) for x in data["reasoning"]]

        return []

    def _format_sse(self, event: str, body: Dict[str, Any]) -> str:
        """
        Format a single SSE frame:

            event: <event>
            data: <json>

        Followed by a blank line, as required by the SSE protocol.
        """
        return f"event: {event}\ndata: {json.dumps(body, ensure_ascii=False)}\n\n"


# ----------------------------------------------------------------------
# Convenience wrapper
# ----------------------------------------------------------------------
def wrap_openai_sse(
    agent_id: str,
    sg_stream: Iterable[Dict[str, Any]],
) -> Generator[str, None, None]:
    """
    Convenience function used by the OpenAIA2AAdapter.

    Example:

        sg_stream = agent_client.run(..., stream=True)
        return wrap_openai_sse(agent_id, sg_stream)
    """
    adapter = OpenAIA2AReasoningSSEAdapter(agent_id)
    return adapter.wrap_stream(sg_stream)
