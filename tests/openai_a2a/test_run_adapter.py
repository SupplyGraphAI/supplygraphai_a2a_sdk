#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : test_run_adapter.py
"""

import pytest

from supplygraphai_a2a_sdk.adapters.openai_a2a.run_adapter import (
    build_openai_run
)
from supplygraphai_a2a_sdk.adapters.openai_a2a.status_map import (
    SG_TO_OPENAI_STATUS
)


# ---------------------------------------------------------------------
# 1. Run adapter basic: TASK_COMPLETED → completed with output
# ---------------------------------------------------------------------
def test_run_adapter_completed_with_output():
    sg_response = {
        "code": "TASK_COMPLETED",
        "message": "Task completed successfully.",
        "data": {
            "task_id": "t_123",
            "input": "calculate duty",
            "content": {
                "type": "result",
                "data": {"value": 100}
            },
            "stage": "executing",
            "progress": 100
        },
        "metadata": {"credits_used": 5}
    }

    out = build_openai_run("tariff_calc", sg_response)

    assert out["object"] == "agent.run"
    assert out["agent_id"] == "tariff_calc"
    assert out["status"] == "completed"

    # Output must be normalized into OpenAI format
    assert out["output"]["type"] == "json"
    assert out["output"]["content"] == {"value": 100}

    # No required_action or last_error for completed tasks
    assert out["required_action"] is None
    assert out["last_error"] is None

    # SupplyGraph extensions should exist
    assert "extensions" in out
    assert "supplygraph" in out["extensions"]


# ---------------------------------------------------------------------
# 2. Run adapter: TASK_FAILED → failed + last_error
# ---------------------------------------------------------------------
def test_run_adapter_failed():
    sg_response = {
        "code": "TASK_FAILED",
        "message": "Execution error.",
        "data": {
            "task_id": "t_999",
            "content": None,
            "stage": "executing"
        },
        "errors": {"detail": "Internal error"}
    }

    out = build_openai_run("tariff_calc", sg_response)

    assert out["status"] == "failed"
    assert out["last_error"]["code"] == "TASK_FAILED"
    assert out["last_error"]["message"] == "Execution error."
    assert out["output"] is None


# ---------------------------------------------------------------------
# 3. Run adapter: WAITING_USER → requires_action
# ---------------------------------------------------------------------
def test_run_adapter_requires_action():
    sg_response = {
        "code": "WAITING_USER",
        "message": "More information required.",
        "data": {
            "task_id": "t_555",
            "content": "Please provide the country of origin.",
            "stage": "interpreting",
        }
    }

    out = build_openai_run("tariff_calc", sg_response)

    assert out["status"] == "requires_action"
    assert out["output"] is None

    # Required action shall contain a meaningful message
    ra = out["required_action"]
    assert ra["type"] == "awaiting_user"
    assert "provide" in ra["message"].lower()


# ---------------------------------------------------------------------
# 4. Run adapter: interpreting TASK_RUNNING → in_progress + intermediate steps flag
# ---------------------------------------------------------------------
def test_run_adapter_in_progress():
    sg_response = {
        "code": "TASK_RUNNING",
        "message": "Running...",
        "data": {
            "task_id": "t_321",
            "content": None,
            "stage": "executing",
            "progress": 30,
        },
    }

    out = build_openai_run("tariff_calc", sg_response)

    assert out["status"] == "in_progress"
    assert out["output"] is None
    # Should show that intermediate steps exist
    assert out["has_intermediate_steps"] is True


# ---------------------------------------------------------------------
# 5. Run adapter: verify SG→OpenAI status mapping
# ---------------------------------------------------------------------
@pytest.mark.parametrize("sg_code", list(SG_TO_OPENAI_STATUS.keys()))
def test_run_adapter_status_mapping(sg_code):
    sg_response = {
        "code": sg_code,
        "data": {"task_id": "t_x"},
    }

    out = build_openai_run("agent_x", sg_response)
    assert out["status"] == SG_TO_OPENAI_STATUS[sg_code]


# ---------------------------------------------------------------------
# 6. Run adapter: missing content must result in output None
# ---------------------------------------------------------------------
def test_run_adapter_missing_content():
    sg_response = {
        "code": "TASK_COMPLETED",
        "data": {"task_id": "t_nc"},
    }

    out = build_openai_run("calc", sg_response)
    assert out["output"] is None


# ---------------------------------------------------------------------
# 7. Run adapter: string content → text output
# ---------------------------------------------------------------------
def test_run_adapter_text_output():
    sg_response = {
        "code": "TASK_COMPLETED",
        "data": {
            "task_id": "t_text",
            "content": "Hello world"
        }
    }

    out = build_openai_run("agent1", sg_response)

    assert out["output"]["type"] == "text"
    assert out["output"]["content"] == "Hello world"


# ---------------------------------------------------------------------
# 8. Run adapter: structured dict but not type=result → json output
# ---------------------------------------------------------------------
def test_run_adapter_structured_json_output():
    sg_response = {
        "code": "TASK_COMPLETED",
        "data": {
            "task_id": "t_json",
            "content": {"foo": "bar"}
        }
    }

    out = build_openai_run("agent1", sg_response)

    assert out["output"]["type"] == "json"
    assert out["output"]["content"] == {"foo": "bar"}


# ---------------------------------------------------------------------
# 9. Run adapter: metadata correctness
# ---------------------------------------------------------------------
def test_run_adapter_metadata():
    sg_response = {
        "code": "TASK_RUNNING",
        "message": "Processing...",
        "data": {
            "task_id": "t_meta",
            "stage": "executing",
            "progress": 40,
        },
    }

    out = build_openai_run("calc_agent", sg_response)

    meta = out["metadata"]
    assert meta["message"] == "Processing..."
    assert meta["stage"] == "executing"
    assert meta["progress"] == 40
