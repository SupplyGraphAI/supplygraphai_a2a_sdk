#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : test_status_adapter.py
"""

import pytest

from supplygraphai_a2a_sdk.adapters.openai_a2a.status_adapter import (
    build_openai_status
)
from supplygraphai_a2a_sdk.adapters.openai_a2a.status_map import (
    SG_TO_OPENAI_STATUS
)


# ---------------------------------------------------------------------
# 1. Basic test: TASK_RUNNING → in_progress (OpenAI)
# ---------------------------------------------------------------------
def test_status_adapter_in_progress():
    sg_status = {
        "code": "TASK_RUNNING",
        "message": "Running...",
        "data": {
            "task_id": "t_001",
            "stage": "executing",
            "progress": 55,
            "intermediate_steps": [
                {"type": "thinking", "content": "Analyzing..."},
                {"type": "action", "content": "Resolving..."}
            ]
        }
    }

    out = build_openai_status("tariff_calc", sg_status)

    assert out["object"] == "agent.run.status"
    assert out["agent_id"] == "tariff_calc"
    assert out["status"] == "in_progress"

    # Steps must be converted
    assert len(out["steps"]) == 2
    assert out["steps"][0]["type"] == "thinking"
    assert "Analyzing" in out["steps"][0]["content"]

    # Metadata fields
    meta = out["metadata"]
    assert meta["stage"] == "executing"
    assert meta["progress"] == 55


# ---------------------------------------------------------------------
# 2. WAITING_USER → requires_action (OpenAI)
# ---------------------------------------------------------------------
def test_status_adapter_requires_action():
    sg_status = {
        "code": "WAITING_USER",
        "message": "User input needed.",
        "data": {
            "task_id": "t_100",
            "stage": "interpreting",
            "progress": 0
        }
    }

    out = build_openai_status("calc", sg_status)

    assert out["status"] == "requires_action"

    # Status adapter should NOT include required_action here.
    assert "required_action" not in out

    # No output for status object
    assert "output" not in out


# ---------------------------------------------------------------------
# 3. TASK_COMPLETED → completed
# ---------------------------------------------------------------------
def test_status_adapter_completed():
    sg_status = {
        "code": "TASK_COMPLETED",
        "message": "Done",
        "data": {
            "task_id": "t_complete",
            "stage": "executing",
            "progress": 100,
        }
    }

    out = build_openai_status("agent_x", sg_status)

    assert out["status"] == "completed"
    assert out["metadata"]["progress"] == 100


# ---------------------------------------------------------------------
# 4. TASK_FAILED → failed
# ---------------------------------------------------------------------
def test_status_adapter_failed():
    sg_status = {
        "code": "TASK_FAILED",
        "message": "Error while processing.",
        "data": {
            "task_id": "t_fail",
            "stage": "executing"
        },
        "errors": {"detail": "Error detail"}
    }

    out = build_openai_status("agent_y", sg_status)
    assert out["status"] == "failed"


# ---------------------------------------------------------------------
# 5. TASK_CANCELLED → cancelled
# ---------------------------------------------------------------------
def test_status_adapter_cancelled():
    sg_status = {
        "code": "TASK_CANCELLED",
        "data": {"task_id": "t_cancel"}
    }

    out = build_openai_status("agent_c", sg_status)
    assert out["status"] == "cancelled"


# ---------------------------------------------------------------------
# 6. Missing task_id → auto-generated
# ---------------------------------------------------------------------
def test_status_adapter_missing_task_id():
    sg_status = {"code": "TASK_RUNNING"}
    out = build_openai_status("calc", sg_status)

    assert out["id"].startswith("sg_task_")  # generated fallback id


# ---------------------------------------------------------------------
# 7. Missing steps array → empty list
# ---------------------------------------------------------------------
def test_status_adapter_no_steps():
    sg_status = {
        "code": "TASK_RUNNING",
        "data": {
            "task_id": "t_empty",
            # No intermediate_steps
        }
    }

    out = build_openai_status("agent", sg_status)

    assert isinstance(out["steps"], list)
    assert len(out["steps"]) == 0


# ---------------------------------------------------------------------
# 8. Verify SG→OpenAI status mapping consistency
# ---------------------------------------------------------------------
@pytest.mark.parametrize("sg_code", list(SG_TO_OPENAI_STATUS.keys()))
def test_status_mapping_consistency(sg_code):
    sg_status = {"code": sg_code, "data": {"task_id": "t_sg"}}
    out = build_openai_status("agent", sg_status)

    assert out["status"] == SG_TO_OPENAI_STATUS[sg_code]


# ---------------------------------------------------------------------
# 9. Metadata extraction correctness
# ---------------------------------------------------------------------
def test_status_adapter_metadata_extraction():
    sg_status = {
        "code": "TASK_RUNNING",
        "message": "Processing...",
        "data": {
            "task_id": "t_meta",
            "progress": 20,
            "stage": "executing"
        }
    }

    out = build_openai_status("calc", sg_status)

    meta = out["metadata"]
    assert meta["message"] == "Processing..."
    assert meta["progress"] == 20
    assert meta["stage"] == "executing"
