#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : error_adapter.py.py

OpenAI A2A Error Adapter for SupplyGraph A2A Agents.

Converts SupplyGraph error responses or raw Python exceptions into
OpenAI-compatible `agent.error` envelopes.

This module is part of the lowest-level adapter layer. All higher-level
adapters (run/status/result/stream) should rely on this module to ensure
consistent and fully OpenAI-compliant error output.
"""

from typing import Dict, Any, Optional
import traceback


class OpenAIA2AErrorAdapter:
    """
    Convert SupplyGraph A2A errors → OpenAI A2A error envelopes.

    OpenAI A2A error format:

    {
      "object": "agent.error",
      "type": "<string>",      # standardized OpenAI error type
      "message": "<string>",   # human readable message
      "code": "<string>",      # domain-specific error code
      "param": null,           # reserved (not used)
      "details": {...}         # additional structured information
    }
    """

    # ----------------------------------------------------------------------
    # SupplyGraph → OpenAI error type mapping
    # ----------------------------------------------------------------------
    SG_TO_OPENAI_TYPE = {
        "INVALID_REQUEST": "invalid_request_error",
        "INVALID_INTENT": "invalid_request_error",

        "UNAUTHORIZED": "authentication_error",

        "INSUFFICIENT_CREDITS": "payment_required_error",
        "RATE_LIMITED": "rate_limit_error",

        "TASK_CANCELLED": "operation_canceled_error",

        # SG execution/infrastructure failures
        "TASK_FAILED": "server_error",
        "TARGET_UNAVAILABLE": "server_error",
        "TIMEOUT": "server_error",
    }

    DEFAULT_ERROR_TYPE = "server_error"

    # ----------------------------------------------------------------------
    # Core API: Convert an explicit SG error → OpenAI error
    # ----------------------------------------------------------------------
    def to_openai_error(
        self,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Convert SG error fields → OpenAI error envelope.
        """

        error_type = self.SG_TO_OPENAI_TYPE.get(code, self.DEFAULT_ERROR_TYPE)

        return {
            "object": "agent.error",
            "type": error_type,
            "message": message or "An error occurred.",
            "code": code or "UNKNOWN_ERROR",
            "param": None,
            "details": details or {}
        }

    # ----------------------------------------------------------------------
    # Core API: Convert raw Python exceptions → OpenAI INTERNAL_ERROR
    # ----------------------------------------------------------------------
    def from_exception(self, exc: Exception) -> Dict[str, Any]:
        """
        Convert raw Python exceptions into OpenAI `agent.error` envelopes.
        """

        # human friendly message
        message = str(exc) or "Internal server error."

        # full traceback
        tb = traceback.format_exc()

        return {
            "object": "agent.error",
            "type": self.DEFAULT_ERROR_TYPE,
            "message": message,
            "code": "INTERNAL_ERROR",
            "param": None,
            "details": {
                "traceback": tb
            }
        }


# ----------------------------------------------------------------------
# Public helper functions (SDK stable API)
# ----------------------------------------------------------------------

def build_openai_error(
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Build an OpenAI A2A error envelope from explicit SG fields.
    """
    adapter = OpenAIA2AErrorAdapter()
    return adapter.to_openai_error(code, message, details)


def build_openai_exception(exc: Exception) -> Dict[str, Any]:
    """
    Build an OpenAI A2A error envelope from a raw exception.
    """
    adapter = OpenAIA2AErrorAdapter()
    return adapter.from_exception(exc)
