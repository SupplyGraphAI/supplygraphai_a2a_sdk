#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : agent_client.py.py
"""
"""
AgentClient — fully manifest-aware implementation for SupplyGraph A2A
"""

import time
from typing import Any, Dict, Generator, Optional, Union

import requests

from .auth import get_auth_header
from ..utils.stream_parser import parse_sse
from ..utils.error_handler import SupplyGraphAPIError


A2A_NON_FATAL_CODES = {"WAITING_USER", "INTERPRETING"}  # not errors
A2A_FATAL_CODES = {"INVALID_REQUEST", "UNAUTHORIZED", "TASK_FAILED", "TASK_CANCELLED"}


class AgentClient:
    def __init__(
        self,
        base_url: str = "https://agent.supplygraph.ai/api/v1/agents",
        api_key: Optional[str] = None,
        timeout: int = 60,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    # ------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------

    def _validate_agent_id(self, agent_id: str) -> None:
        if not agent_id or not isinstance(agent_id, str):
            raise ValueError("agent_id must be a non-empty string")

    def _validate_text_for_run(self, text: str) -> None:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text must be a non-empty string for mode='run'")

    def _validate_task_id(self, task_id: str) -> None:
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError("task_id must be a non-empty string")

    def _should_retry(self, status: Optional[int]) -> bool:
        return status in (None, 429) or (status >= 500)

    def _get_retry_delay(self, attempt: int, response=None) -> float:
        if response:
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                try:
                    return float(retry_after)
                except ValueError:
                    pass
        return self.backoff_factor * (2 ** (attempt - 1))

    # ------------------------------------------------------
    # Generic request executor
    # ------------------------------------------------------

    def _request_with_retry(
        self,
        method: str,
        url: str,
        *,
        json_payload: Optional[Dict[str, Any]] = None,
        stream: bool = False,
    ) -> Union[requests.Response, Dict[str, Any]]:
        headers = get_auth_header(self.api_key)

        last_error = None

        for attempt in range(1, self.max_retries + 1):
            response = None
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    json=json_payload,
                    headers=headers,
                    timeout=self.timeout,
                    stream=stream,
                )
            except requests.RequestException as e:
                error = SupplyGraphAPIError(
                    message=f"Network error calling {url}: {e}",
                    http_status=None,
                    payload={},
                )
                last_error = error
                if attempt >= self.max_retries:
                    raise error
                time.sleep(self._get_retry_delay(attempt))
                continue

            # Streaming mode does not parse JSON
            if stream:
                if response.status_code >= 400:
                    raise SupplyGraphAPIError(
                        message=f"HTTP {response.status_code} error in streaming mode",
                        http_status=response.status_code,
                        payload={"text": response.text},
                    )
                return response

            # -------- Non-stream mode --------
            try:
                data = response.json()
            except Exception:
                error = SupplyGraphAPIError(
                    message="Response is not valid JSON",
                    http_status=response.status_code,
                    payload={"raw": response.text},
                )
                last_error = error
                if self._should_retry(response.status_code) and attempt < self.max_retries:
                    time.sleep(self._get_retry_delay(attempt, response))
                    continue
                raise error

            # HTTP 4xx/5xx
            if response.status_code >= 400:
                raise SupplyGraphAPIError(
                    message=data.get("message", "HTTP error"),
                    http_status=response.status_code,
                    api_code=data.get("code"),
                    errors=data.get("errors"),
                    payload=data,
                )

            # -------- Check A2A business-level success --------
            success = data.get("success", True)
            code = data.get("code")

            if not success and code in A2A_FATAL_CODES:
                raise SupplyGraphAPIError(
                    message=data.get("message", ""),
                    http_status=response.status_code,
                    api_code=code,
                    errors=data.get("errors"),
                    payload=data,
                )

            # WAITING_USER is not an error → return to user
            return data

        if last_error:
            raise last_error
        raise SupplyGraphAPIError("Unknown error after retries")

    # ------------------------------------------------------
    # Public Agent APIs
    # ------------------------------------------------------

    def run(self, agent_id: str, text: str, task_id: Optional[str] = None, stream=False, **kwargs):
        self._validate_agent_id(agent_id)
        self._validate_text_for_run(text)

        url = f"{self.base_url}/{agent_id}/run"
        payload = {"mode": "run", "text": text, "stream": bool(stream)}

        if task_id:
            payload["task_id"] = task_id

        payload.update(kwargs)

        if stream:
            resp = self._request_with_retry("POST", url, json_payload=payload, stream=True)
            return parse_sse(resp)

        return self._request_with_retry("POST", url, json_payload=payload)

    def status(self, agent_id: str, task_id: str, **kwargs):
        self._validate_agent_id(agent_id)
        self._validate_task_id(task_id)

        url = f"{self.base_url}/{agent_id}/run"
        payload = {"mode": "status", "task_id": task_id}
        payload.update(kwargs)

        return self._request_with_retry("POST", url, json_payload=payload)

    def results(self, agent_id: str, task_id: str, **kwargs):
        self._validate_agent_id(agent_id)
        self._validate_task_id(task_id)

        url = f"{self.base_url}/{agent_id}/run"
        payload = {"mode": "results", "task_id": task_id}
        payload.update(kwargs)

        return self._request_with_retry("POST", url, json_payload=payload)

    def manifest(self, agent_id: str):
        self._validate_agent_id(agent_id)

        url = f"{self.base_url}/{agent_id}/manifest"
        resp = self._request_with_retry("GET", url)
        return resp
