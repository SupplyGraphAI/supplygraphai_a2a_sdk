#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : openai_a2a_adapter.py.py

Unified OpenAI A2A Adapter for SupplyGraph A2A Agents.

This adapter exposes a unified interface that behaves like
OpenAI's Agent-to-Agent (A2A) protocol, wrapping the internal
SupplyGraph A2A /manifest, /run, /status, /results and SSE APIs.

Public methods:

    - manifest(agent_id) -> OpenAI-style agent manifest
    - run(agent_id, text, **kwargs) -> OpenAI agent.run
    - status(agent_id, task_id) -> OpenAI agent.run.status
    - result(agent_id, task_id) -> OpenAI agent.run.result
    - stream(agent_id, text, **kwargs) -> SSE generator (OpenAI style)
"""

from typing import Any, Dict, Generator

import json

from supplygraphai_a2a_sdk.client.agent_client import AgentClient
from supplygraphai_a2a_sdk.utils.error_handler import SupplyGraphAPIError

from supplygraphai_a2a_sdk.adapters.openai_a2a.manifest_builder import (
    build_openai_manifest,
)
from supplygraphai_a2a_sdk.adapters.openai_a2a.run_adapter import (
    build_openai_run,
)
from supplygraphai_a2a_sdk.adapters.openai_a2a.status_adapter import (
    build_openai_status,
)
from supplygraphai_a2a_sdk.adapters.openai_a2a.results_adapter import (
    build_openai_result,
)
from supplygraphai_a2a_sdk.adapters.openai_a2a.reasoning_sse_adapter import (
    wrap_openai_sse,
)
from supplygraphai_a2a_sdk.adapters.openai_a2a.error_adapter import (
    build_openai_error,
    build_openai_exception,
)


class OpenAIA2AAdapter:
    """
    Unified OpenAI-style adapter that wraps SupplyGraph A2A APIs.

    It provides OpenAI Agent Runtime–compatible envelopes while
    internally calling the SupplyGraph A2A gateway.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://agent.supplygraph.ai/api/v1/agents",
    ) -> None:
        """
        :param api_key: SupplyGraph A2A API key (Bearer token).
        :param base_url: Base URL of the SupplyGraph agent gateway.
        """
        self.client = AgentClient(api_key=api_key, base_url=base_url)

    # ------------------------------------------------------------------
    # MANIFEST
    # ------------------------------------------------------------------
    def manifest(self, agent_id: str) -> Dict[str, Any]:
        """
        Retrieve and normalize the agent manifest into an
        OpenAI-compatible A2A manifest object.
        """
        try:
            sg_meta = self.client.manifest(agent_id)
            return build_openai_manifest(sg_meta)

        except SupplyGraphAPIError as e:
            # Convert SG API errors → OpenAI error envelope
            return build_openai_error(e.api_code, str(e), e.errors)

        except Exception as e:
            # Convert raw Python exceptions → OpenAI error envelope
            return build_openai_exception(e)

    # ------------------------------------------------------------------
    # RUN
    # ------------------------------------------------------------------
    def run(self, agent_id: str, text: str, **kwargs) -> Dict[str, Any]:
        """
        OpenAI-style run() wrapper.

        Parameters:
            agent_id: SupplyGraph agent identifier, e.g. "tariff_calc".
            text:     Natural language input or serialized task input.
            **kwargs: Extra SupplyGraph fields, e.g. mode, extra, etc.
                      In most OpenAI-like usage, callers just pass text.

        Returns:
            OpenAI-style run object:
            {
              "id": "...",
              "object": "agent.run",
              "agent_id": "...",
              "status": "...",
              "created_at": ...,
              "input": {...},
              "output": {...} | null,
              "required_action": {...} | null,
              "last_error": {...} | null,
              "metadata": {...},
              "extensions": { "supplygraph": {...} }
            }
        """
        try:
            # Delegate to SupplyGraph A2A client
            sg_result = self.client.run(agent_id, text=text, **kwargs)
            # Normalize into OpenAI run object
            return build_openai_run(agent_id, sg_result)

        except SupplyGraphAPIError as e:
            return build_openai_error(e.api_code, str(e), e.errors)

        except Exception as e:
            return build_openai_exception(e)

    # ------------------------------------------------------------------
    # STATUS
    # ------------------------------------------------------------------
    def status(self, agent_id: str, task_id: str) -> Dict[str, Any]:
        """
        OpenAI-style status() wrapper.

        Parameters:
            agent_id: SupplyGraph agent identifier.
            task_id:  Task id returned from a previous run().

        Returns:
            OpenAI-style run.status object.
        """
        try:
            if not task_id:
                return build_openai_error(
                    "INVALID_REQUEST",
                    "Missing required parameter: task_id.",
                    {},
                )

            sg_status = self.client.status(agent_id, task_id)
            return build_openai_status(agent_id, sg_status)

        except SupplyGraphAPIError as e:
            return build_openai_error(e.api_code, str(e), e.errors)

        except Exception as e:
            return build_openai_exception(e)

    # ------------------------------------------------------------------
    # RESULTS
    # ------------------------------------------------------------------
    def result(self, agent_id: str, task_id: str) -> Dict[str, Any]:
        """
        OpenAI-style result() wrapper.

        Parameters:
            agent_id: SupplyGraph agent identifier.
            task_id:  Task id returned from a previous run().

        Returns:
            OpenAI-style run.result object.
        """
        try:
            if not task_id:
                return build_openai_error(
                    "INVALID_REQUEST",
                    "Missing required parameter: task_id.",
                    {},
                )

            sg_result = self.client.results(agent_id, task_id)
            return build_openai_result(agent_id, sg_result)

        except SupplyGraphAPIError as e:
            return build_openai_error(e.api_code, str(e), e.errors)

        except Exception as e:
            return build_openai_exception(e)

    # ------------------------------------------------------------------
    # STREAM (SSE)
    # ------------------------------------------------------------------
    def stream(
        self,
        agent_id: str,
        text: str,
        **kwargs,
    ) -> Generator[str, None, None]:
        """
        OpenAI-style streaming wrapper.

        Produces OpenAI-compatible SSE frames:

            event: step.delta
            data: {"delta": "..."}

            event: step
            data: {"type": "reasoning", "content": [...], "timestamp": ...}

            event: completed
            data: {"message": "completed", "timestamp": ...}

        On errors, emits:

            event: error
            data: {<OpenAI error envelope>}
        """
        try:
            # Ensure streaming mode for SG call
            sg_stream = self.client.run(
                agent_id=agent_id,
                text=text,
                stream=True,
                **kwargs,
            )

            # Wrap SG stream into OpenAI-compatible SSE
            print('cq_debug: openai a2a adapter -> stream!')
            return wrap_openai_sse(agent_id, sg_stream)

        except SupplyGraphAPIError as e:
            def err_gen():
                yield self._error_as_sse(e)
            return err_gen()

        except Exception as e:
            def exc_gen():
                yield self._exception_as_sse(e)
            return exc_gen()

    # ------------------------------------------------------------------
    # SSE error helpers
    # ------------------------------------------------------------------
    def _error_as_sse(self, e: SupplyGraphAPIError) -> str:
        """
        Convert SG API error → OpenAI error envelope SSE event.
        """
        err = build_openai_error(e.api_code, str(e), e.errors)
        return f"event: error\ndata: {json.dumps(err)}\n\n"

    def _exception_as_sse(self, exc: Exception) -> str:
        """
        Convert raw exception → OpenAI error envelope SSE event.
        """
        err = build_openai_exception(exc)
        return f"event: error\ndata: {json.dumps(err)}\n\n"
