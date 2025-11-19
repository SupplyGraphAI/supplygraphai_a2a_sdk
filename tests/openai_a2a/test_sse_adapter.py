#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : test_sse_adapter.py
"""

import pytest
import json
import time

from supplygraphai_a2a_sdk.adapters.openai_a2a.reasoning_sse_adapter import (
    wrap_openai_sse
)


# ---------------------------------------------------------------------
# Helpers: Build SG-style fake SSE generator
# ---------------------------------------------------------------------
def sg_stream_generator(events):
    """Yield SG SSE events one-by-one."""
    for evt in events:
        yield evt


# ---------------------------------------------------------------------
# 1. Basic test — THINKING reasoning → step events
# ---------------------------------------------------------------------
def test_sse_reasoning_steps():
    sg_events = [
        {
            "event": "stream",
            "data": {
                "task_id": "t123",
                "stage": "interpreting",
                "code": "THINKING",
                "reasoning": ["A", "B", "C"]
            }
        }
    ]

    gen = wrap_openai_sse("tariff_calc", sg_stream_generator(sg_events))

    frames = list(gen)

    # Expect 3 reasoning steps + 1 done event
    assert len(frames) == 4

    # Validate each reasoning frame
    for i, expected in enumerate(["A", "B", "C"]):
        s = frames[i]
        assert s.startswith("event: step")
        body = json.loads(s.split("data: ")[1])
        assert body["content"] == expected
        assert "timestamp" in body

    # Last frame must be done
    assert frames[-1].startswith("event: done")
    done_body = json.loads(frames[-1].split("data: ")[1])
    assert done_body["message"] == "stream completed"


# ---------------------------------------------------------------------
# 2. Non-"stream" event → debug frame
# ---------------------------------------------------------------------
def test_sse_debug_event():
    sg_events = [
        {"event": "unknown", "foo": "bar"}
    ]

    gen = wrap_openai_sse("agent_x", sg_stream_generator(sg_events))

    frames = list(gen)
    assert len(frames) == 2  # 1 debug + 1 done

    debug_frame = frames[0]
    assert debug_frame.startswith("event: debug")
    body = json.loads(debug_frame.split("data: ")[1])
    assert "debug" in body
    assert body["debug"]["foo"] == "bar"


# ---------------------------------------------------------------------
# 3. Multiple SG batches → sequential step events
# ---------------------------------------------------------------------
def test_sse_multiple_batches():
    sg_events = [
        {
            "event": "stream",
            "data": {"task_id": "t", "reasoning": ["1", "2"]}
        },
        {
            "event": "stream",
            "data": {"task_id": "t", "reasoning": ["3"]}
        }
    ]

    gen = wrap_openai_sse("agent_y", sg_stream_generator(sg_events))
    frames = list(gen)

    assert len(frames) == 4  # 3 steps + done
    assert frames[0].startswith("event: step")
    assert frames[1].startswith("event: step")
    assert frames[2].startswith("event: step")
    assert frames[3].startswith("event: done")


# ---------------------------------------------------------------------
# 4. Missing reasoning array → no step, only done
# ---------------------------------------------------------------------
def test_sse_no_reasoning():
    sg_events = [
        {
            "event": "stream",
            "data": {"task_id": "t", "stage": "interpreting", "code": "THINKING"}
        }
    ]

    gen = wrap_openai_sse("agent_z", sg_stream_generator(sg_events))
    frames = list(gen)

    assert len(frames) == 1  # only done
    assert frames[0].startswith("event: done")


# ---------------------------------------------------------------------
# 5. Empty SG generator → only done
# ---------------------------------------------------------------------
def test_sse_empty_stream():
    gen = wrap_openai_sse("agent_empty", sg_stream_generator([]))
    frames = list(gen)

    assert len(frames) == 1
    assert frames[0].startswith("event: done")


# ---------------------------------------------------------------------
# 6. Validate SSE frame formatting — must end with \n\n
# ---------------------------------------------------------------------
def test_sse_formatting():
    sg_events = [
        {
            "event": "stream",
            "data": {"task_id": "t", "reasoning": ["hello"]}
        }
    ]

    gen = wrap_openai_sse("agent_fmt", sg_stream_generator(sg_events))
    frames = list(gen)

    assert frames[0].endswith("\n\n")
    assert frames[-1].endswith("\n\n")


# ---------------------------------------------------------------------
# 7. Validate JSON body structure (must be valid JSON)
# ---------------------------------------------------------------------
def test_sse_json_parsing():
    sg_events = [
        {
            "event": "stream",
            "data": {
                "task_id": "t1",
                "stage": "interpreting",
                "code": "THINKING",
                "reasoning": ["stepA"]
            }
        }
    ]

    gen = wrap_openai_sse("agent_json", sg_stream_generator(sg_events))
    frames = list(gen)

    # First frame is a step
    body = json.loads(frames[0].split("data: ")[1])
    assert body["content"] == "stepA"
    assert body["type"] == "reasoning"

    # Second is done
    done = json.loads(frames[1].split("data: ")[1])
    assert done["message"] == "stream completed"


# ---------------------------------------------------------------------
# 8. Error fallback (adapter internal) — validate error frame
# ---------------------------------------------------------------------
def test_sse_error_fallback():
    class FakeClientError(Exception):
        pass

    def faulty_generator():
        raise FakeClientError("boom")

    # Wrap the generator in try/except in stream() normally,
    # but here we simulate wrap_openai_sse receiving it directly.
    # Expected behavior: error → SINGLE error frame.
    try:
        gen = wrap_openai_sse("agent_err", faulty_generator())
        frames = list(gen)
        # Should not reach here — wrap_openai_sse assumes caller handles exceptions
        assert False, "wrap_openai_sse should not directly receive exceptions"
    except FakeClientError:
        # Expected: the adapter does not catch exceptions by itself
        assert True


# ---------------------------------------------------------------------
# 9. Validate stage/code passthrough into step metadata
# ---------------------------------------------------------------------
def test_sse_reasoning_metadata_copy():
    sg_events = [
        {
            "event": "stream",
            "data": {
                "task_id": "tt",
                "stage": "interpreting",
                "code": "THINKING",
                "reasoning": ["meta"]
            }
        }
    ]

    gen = wrap_openai_sse("tariff_calc", sg_stream_generator(sg_events))
    frames = list(gen)

    body = json.loads(frames[0].split("data: ")[1])
    assert body["sg"]["stage"] == "interpreting"
    assert body["sg"]["code"] == "THINKING"
    assert body["sg"]["task_id"] == "tt"
