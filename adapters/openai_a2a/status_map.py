#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    :
@File    : status_map.py

Unified SupplyGraph → OpenAI A2A status mapping.

This module is the SINGLE source of truth for how SupplyGraph A2A
status codes map into the OpenAI Agent Runtime standard run.status
categories:

    - in_progress
    - requires_action
    - completed
    - failed
    - cancelled

All adapters (run_adapter, status_adapter, results_adapter, SSE, etc.)
MUST depend on this centralized mapping for correctness and consistency.
"""

from typing import Dict, List

# ---------------------------------------------------------------------------
# SupplyGraph A2A status codes (canonical list)
# ---------------------------------------------------------------------------
#
# Stages and codes (from SG A2A docs):
#
# interpreting stage:
#   INTERPRETING          user input is being analyzed
#   INVALID_REQUEST       out-of-scope input, bad parameters, or chit-chat
#   UNAUTHORIZED          auth failure / invalid API key
#   WAITING_USER          requires more user input / confirmation
#   INSUFFICIENT_CREDITS  not enough credits
#
# executing stage:
#   TASK_ACCEPTED         task accepted and queued / about to run
#   TASK_RUNNING          task is currently executing
#
# completed stage:
#   TASK_COMPLETED        task finished successfully
#   TASK_FAILED           task finished with error
#
# cancelled stage:
#   TASK_CANCELLED        task was cancelled by user
#
# generic / infra / error codes (from A2A error docs):
#   INVALID_INTENT        unsupported semantic intent
#   RATE_LIMITED          too many requests
#   TARGET_UNAVAILABLE    downstream / target service unavailable
#   TIMEOUT               no response within the allowed window
#
# streaming-only code (SSE thinking):
#   THINKING              reasoning / thinking frame in stream events
#
# NOTE:
#   THINKING is used primarily in SSE events (stream_event_schema),
#   not in the main JSON envelope. For mapping purposes we normalize
#   it to "in_progress".
# ---------------------------------------------------------------------------

# Codes that correspond to an "in_progress" run.status
SG_STATUS_IN_PROGRESS = {
    "INTERPRETING",
    "TASK_ACCEPTED",
    "TASK_RUNNING",
    "THINKING",  # streaming reasoning frames
}

# Codes that require further user input / confirmation
SG_STATUS_REQUIRES_ACTION = {
    "WAITING_USER",
}

# Codes that represent a successfully completed task
SG_STATUS_COMPLETED = {
    "TASK_COMPLETED",
}

# Codes that represent a failed task or hard error
SG_STATUS_FAILED = {
    "TASK_FAILED",
    "INVALID_REQUEST",
    "UNAUTHORIZED",
    "INSUFFICIENT_CREDITS",
    "INVALID_INTENT",
    "RATE_LIMITED",
    "TARGET_UNAVAILABLE",
    "TIMEOUT",
}

# Codes that represent cancellation
SG_STATUS_CANCELLED = {
    "TASK_CANCELLED",
}

# ---------------------------------------------------------------------------
# Forward mapping: SG → OpenAI
# ---------------------------------------------------------------------------

SG_TO_OPENAI_STATUS: Dict[str, str] = {}

for code in SG_STATUS_IN_PROGRESS:
    SG_TO_OPENAI_STATUS[code] = "in_progress"

for code in SG_STATUS_REQUIRES_ACTION:
    SG_TO_OPENAI_STATUS[code] = "requires_action"

for code in SG_STATUS_COMPLETED:
    SG_TO_OPENAI_STATUS[code] = "completed"

for code in SG_STATUS_FAILED:
    SG_TO_OPENAI_STATUS[code] = "failed"

for code in SG_STATUS_CANCELLED:
    SG_TO_OPENAI_STATUS[code] = "cancelled"


# ---------------------------------------------------------------------------
# Reverse mapping: OpenAI → SG
# Useful for debugging, tests, or future bi-directional adapters.
# ---------------------------------------------------------------------------

OPENAI_TO_SG_STATUS: Dict[str, List[str]] = {
    "in_progress": sorted(SG_STATUS_IN_PROGRESS),
    "requires_action": sorted(SG_STATUS_REQUIRES_ACTION),
    "completed": sorted(SG_STATUS_COMPLETED),
    "failed": sorted(SG_STATUS_FAILED),
    "cancelled": sorted(SG_STATUS_CANCELLED),
}


# ---------------------------------------------------------------------------
# Helper API
# ---------------------------------------------------------------------------

def map_sg_to_openai(code: str) -> str:
    """
    Convert a SupplyGraph A2A status code → OpenAI run.status.

    Unknown / unexpected codes default to "in_progress" to avoid breaking
    consumer runtimes, but such cases SHOULD be logged by callers.
    """
    if not code:
        return "in_progress"
    return SG_TO_OPENAI_STATUS.get(code, "in_progress")


def map_openai_to_sg(status: str) -> List[str]:
    """
    Convert an OpenAI run.status → list of corresponding SG status codes.
    (Useful for testing or validating flows.)

    Unknown statuses return an empty list.
    """
    if not status:
        return []
    return OPENAI_TO_SG_STATUS.get(status, [])
