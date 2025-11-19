#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : error_handler.py

Enhanced API error model for SupplyGraph A2A
Matches manifest error schema exactly
"""

from typing import Any, Dict, Optional


class SupplyGraphAPIError(Exception):
    """
    Unified API error for SupplyGraph A2A responses.

    Includes:
    - http_status: underlying HTTP status code (if any)
    - api_code: logical A2A code (INVALID_REQUEST, TASK_FAILED, etc.)
    - message: human-readable message
    - errors: field from manifest ("string" | object | null)
    - payload: full raw response for debugging
    """

    def __init__(
        self,
        message: str,
        http_status: Optional[int] = None,
        api_code: Optional[str] = None,
        errors: Optional[Any] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:

        super().__init__(message)

        self.http_status = http_status
        self.api_code = api_code
        self.errors = errors
        self.payload = payload or {}

    def __str__(self) -> str:
        base = f"[SupplyGraphAPIError] {self.api_code or ''} {self.args[0]}"
        if self.http_status:
            base += f" (HTTP {self.http_status})"
        return base
