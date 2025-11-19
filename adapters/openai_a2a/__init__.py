#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    :
@File    : __init__.py.py

OpenAI A2A Adapter Submodules for SupplyGraphAI A2A SDK.

This module exposes the internal building blocks used to construct
the unified OpenAIA2AAdapter located at:
    supplygraphai_a2a_sdk.adapters.openai_a2a_adapter

Most end-users should import and use OpenAIA2AAdapter directly,
but individual components are made available for advanced usage.
"""

# ---------------------------------------------------------
# Run Adapter
# ---------------------------------------------------------
from supplygraphai_a2a_sdk.adapters.openai_a2a.run_adapter import (
    OpenAIA2ARunAdapter,
    build_openai_run,
)

# ---------------------------------------------------------
# Status Adapter
# ---------------------------------------------------------
from supplygraphai_a2a_sdk.adapters.openai_a2a.status_adapter import (
    OpenAIA2AStatusAdapter,
    build_openai_status,
)

# ---------------------------------------------------------
# Results Adapter
# ---------------------------------------------------------
from supplygraphai_a2a_sdk.adapters.openai_a2a.results_adapter import (
    OpenAIA2AResultsAdapter,
    build_openai_result,
)

# ---------------------------------------------------------
# Manifest Builder
# ---------------------------------------------------------
from supplygraphai_a2a_sdk.adapters.openai_a2a.manifest_builder import (
    build_openai_manifest,
)

# ---------------------------------------------------------
# Reasoning / SSE Adapter
# ---------------------------------------------------------
from supplygraphai_a2a_sdk.adapters.openai_a2a.reasoning_sse_adapter import (
    OpenAIA2AReasoningSSEAdapter,
    wrap_openai_sse,
)

# ---------------------------------------------------------
# Error Adapter
# ---------------------------------------------------------
from supplygraphai_a2a_sdk.adapters.openai_a2a.error_adapter import (
    OpenAIA2AErrorAdapter,
    build_openai_error,
    build_openai_exception,
)

# ---------------------------------------------------------
# Public Exports
# ---------------------------------------------------------
__all__ = [
    # run
    "OpenAIA2ARunAdapter",
    "build_openai_run",

    # status
    "OpenAIA2AStatusAdapter",
    "build_openai_status",

    # results
    "OpenAIA2AResultsAdapter",
    "build_openai_result",

    # manifest
    "build_openai_manifest",

    # reasoning / sse
    "OpenAIA2AReasoningSSEAdapter",
    "wrap_openai_sse",

    # error
    "OpenAIA2AErrorAdapter",
    "build_openai_error",
    "build_openai_exception",
]
