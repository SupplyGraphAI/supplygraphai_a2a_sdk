#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : test_results_adapter.py
"""

import pytest

from supplygraphai_a2a_sdk.adapters.openai_a2a.results_adapter import (
    build_openai_result
)
from supplygraphai_a2a_sdk.adapters.openai_a2a.status_map import (
    SG_TO_OPENAI_STATUS
)


# ---------------------------------------------------------------------
# 1. TASK_COMPLETED → output: structured JSON
# ---------------------------------------------------------------------
def test_results_adapter_completed_structured_output():
    sg_result = {
        "code": "TASK_COMPLETED",
        "message": "Task completed.",
        "data": {
            "task_id": "t_final",
            "content": {
                "type": "result",
                "data": {
                    "value": 200,
                    "detail": "duty calculated"
                }
            },
            "stage": "executing",
            "progress": 100,
        },
        "metadata": {
            "credits_used": 10
        }
    }

    out = build_openai_result("tariff_calc", sg_result)

    assert out["object"] == "agent.run.result"
    assert out["status"] == "completed"
    assert out["agent_id"] == "tariff_calc"

    # Output must be normalized into JSON
    assert out["output"]["type"] == "json"
    assert out["output"]["content"] == {
        "value": 200,
        "detail": "duty calculated"
    }

    # No error or required action
    assert out["last_error"] is None
    assert out["required_action"] is None

    # Extensions block must exist
    assert "extensions" in out
    assert "supplygraph" in out["extensions"]


# ---------------------------------------------------------------------
# 2. TASK_COMPLETED → text output (fallback)
# ---------------------------------------------------------------------
def test_results_adapter_completed_text_output():
    sg_result = {
        "code": "TASK_COMPLETED",
        "data": {
            "task_id": "t_text",
            "content": "This is the final answer."
        }
    }

    out = build_openai_result("agent1", sg_result)

    assert out["status"] == "completed"
    assert out["output"]["type"] == "text"
    assert out["output"]["content"] == "This is the final answer."


# ---------------------------------------------------------------------
# 3. TASK_FAILED → failed with last_error
# ---------------------------------------------------------------------
def test_results_adapter_failed():
    sg_result = {
        "code": "TASK_FAILED",
        "message": "Execution failed.",
        "errors": {"error_detail": "Something went wrong."},
        "data": {
            "task_id": "t_fail"
        }
    }

    out = build_openai_result("calc", sg_result)

    assert out["status"] == "failed"
    assert out["last_error"]["code"] == "TASK_FAILED"
    assert out["last_error"]["message"] == "Execution failed."
    assert out["last_error"]["details"] == {"error_detail": "Something went wrong."}

    # No output for failed tasks
    assert out["output"] is None


# ---------------------------------------------------------------------
# 4. WAITING_USER → requires_action (rare in results)
# ---------------------------------------------------------------------
def test_results_adapter_requires_action():
    sg_result = {
        "code": "WAITING_USER",
        "message": "User input needed.",
        "data": {
            "task_id": "t_wait",
            "content": "Please confirm the HTS code."
        }
    }

    out = build_openai_result("agent_x", sg_result)

    assert out["status"] == "requires_action"

    ra = out["required_action"]
    assert ra["type"] == "awaiting_user"
    assert "confirm" in ra["message"].lower()

    # No output in requires_action
    assert out["output"] is None


# ---------------------------------------------------------------------
# 5. TASK_CANCELLED → cancelled
# ---------------------------------------------------------------------
def test_results_adapter_cancelled():
    sg_result = {
        "code": "TASK_CANCELLED",
        "data": {
            "task_id": "t_cancel"
        }
    }

    out = build_openai_result("agent_y", sg_result)
    assert out["status"] == "cancelled"


# ---------------------------------------------------------------------
# 6. TASK_RUNNING / INTERPRETING etc → output must be None
# ---------------------------------------------------------------------
@pytest.mark.parametrize("sg_code", ["TASK_RUNNING", "INTERPRETING"])
def test_results_adapter_in_progress_no_output(sg_code):
    sg_result = {
        "code": sg_code,
        "data": {
            "task_id": "t_np"
        }
    }

    out = build_openai_result("agent_z", sg_result)
    assert out["output"] is None


# ---------------------------------------------------------------------
# 7. Mapping consistency test: all SG codes map correctly
# ---------------------------------------------------------------------
@pytest.mark.parametrize("sg_code", list(SG_TO_OPENAI_STATUS.keys()))
def test_results_status_mapping(sg_code):
    sg_result = {
        "code": sg_code,
        "data": {
            "task_id": "t_map"
        }
    }

    out = build_openai_result("agent_map", sg_result)
    assert out["status"] == SG_TO_OPENAI_STATUS[sg_code]


# ---------------------------------------------------------------------
# 8. Metadata must be extracted correctly
# ---------------------------------------------------------------------
def test_results_metadata_extraction():
    sg_result = {
        "code": "TASK_COMPLETED",
        "message": "Done.",
        "data": {
            "task_id": "t_meta",
            "timestamp": "2025-01-01T00:00:00Z"
        },
        "metadata": {
            "credits_used": 7,
            "timestamp": "2025-01-01T00:00:00Z",
            "agent": "tariff_calc"
        }
    }

    out = build_openai_result("tariff_calc", sg_result)

    md = out["metadata"]
    assert md["message"] == "Done."
    assert md["credits_used"] == 7
    assert md["agent"] == "tariff_calc"


# ---------------------------------------------------------------------
# 9. Missing content → output must be None
# ---------------------------------------------------------------------
def test_results_missing_content():
    sg_result = {
        "code": "TASK_COMPLETED",
        "data": {
            "task_id": "t_missing"
        }
    }

    out = build_openai_result("calc", sg_result)
    assert out["output"] is None


# ---------------------------------------------------------------------
# 10. Structured dict but not type=result → treat as JSON
# ---------------------------------------------------------------------
def test_results_structured_json_fallback():
    sg_result = {
        "code": "TASK_COMPLETED",
        "data": {
            "task_id": "t_json",
            "content": {"foo": "bar"}
        }
    }

    out = build_openai_result("agent", sg_result)

    assert out["output"]["type"] == "json"
    assert out["output"]["content"] == {"foo": "bar"}
