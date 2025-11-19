#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : test_openai_adapter.py
"""

import pytest
import json
from types import GeneratorType

from supplygraphai_a2a_sdk.adapters.openai_a2a_adapter import (
    OpenAIA2AAdapter,
)
from supplygraphai_a2a_sdk.utils.error_handler import SupplyGraphAPIError


# -------------------------------------------------------------------
# Fake AgentClient for mocking
# -------------------------------------------------------------------
class FakeAgentClient:
    def __init__(self):
        self.manifest_called = False
        self.run_called = False
        self.status_called = False
        self.results_called = False

        # default return values
        self._manifest = {"agent_id": "x", "capabilities": [], "protocol": {}}
        self._run = {"code": "TASK_ACCEPTED", "data": {"task_id": "t1"}}
        self._status = {"code": "TASK_RUNNING", "data": {"task_id": "t1"}}
        self._results = {"code": "TASK_COMPLETED", "data": {"task_id": "t1", "content": "ok"}}

        self._stream = iter([])

    def manifest(self, agent_id):
        self.manifest_called = True
        return self._manifest

    def run(self, agent_id, text, **kwargs):
        self.run_called = True
        if kwargs.get("stream"):
            return self._stream
        return self._run

    def status(self, agent_id, task_id):
        self.status_called = True
        return self._status

    def results(self, agent_id, task_id):
        self.results_called = True
        return self._results


# -------------------------------------------------------------------
# Create adapter with injected FakeClient
# -------------------------------------------------------------------
def build_adapter_with_fake_client():
    adapter = OpenAIA2AAdapter(api_key="k")
    adapter.client = FakeAgentClient()
    return adapter, adapter.client


# -------------------------------------------------------------------
# TESTS
# -------------------------------------------------------------------

# 1) manifest()
def test_manifest_success():
    adapter, client = build_adapter_with_fake_client()
    resp = adapter.manifest("x")

    assert client.manifest_called
    assert resp["object"] == "agent"
    assert resp["id"] == "x"


def test_manifest_sg_error():
    adapter, client = build_adapter_with_fake_client()

    client.manifest = lambda _: (_ for _ in ()).throw(
        SupplyGraphAPIError("INVALID_REQUEST", "bad")
    )

    resp = adapter.manifest("x")

    assert resp["object"] == "agent.error"
    assert resp["code"] == "INVALID_REQUEST"


def test_manifest_exception():
    adapter, client = build_adapter_with_fake_client()

    client.manifest = lambda _: (_ for _ in ()).throw(RuntimeError("boom"))

    resp = adapter.manifest("x")
    assert resp["object"] == "agent.error"
    assert resp["code"] == "INTERNAL_ERROR"


# 2) run()
def test_run_success():
    adapter, client = build_adapter_with_fake_client()
    resp = adapter.run("x", "hello")

    assert client.run_called
    assert resp["object"] == "agent.run"
    assert resp["status"] in ("in_progress", "requires_action", "completed")


def test_run_sg_error():
    adapter, client = build_adapter_with_fake_client()
    client.run = lambda *args, **kwargs: (_ for _ in ()).throw(
        SupplyGraphAPIError("UNAUTHORIZED", "bad key")
    )
    resp = adapter.run("x", "hello")
    assert resp["object"] == "agent.error"
    assert resp["code"] == "UNAUTHORIZED"


def test_run_exception():
    adapter, client = build_adapter_with_fake_client()
    client.run = lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("crash"))
    resp = adapter.run("x", "hello")
    assert resp["object"] == "agent.error"
    assert resp["code"] == "INTERNAL_ERROR"


# 3) status()
def test_status_success():
    adapter, client = build_adapter_with_fake_client()
    resp = adapter.status("x", "t1")

    assert client.status_called
    assert resp["object"] == "agent.run.status"


def test_status_missing_task():
    adapter, client = build_adapter_with_fake_client()
    resp = adapter.status("x", "")

    assert resp["object"] == "agent.error"
    assert resp["code"] == "INVALID_REQUEST"


def test_status_sg_error():
    adapter, client = build_adapter_with_fake_client()
    client.status = lambda *a, **k: (_ for _ in ()).throw(
        SupplyGraphAPIError("INVALID_REQUEST", "err")
    )
    resp = adapter.status("x", "t1")
    assert resp["object"] == "agent.error"
    assert resp["code"] == "INVALID_REQUEST"


def test_status_exception():
    adapter, client = build_adapter_with_fake_client()
    client.status = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
    resp = adapter.status("x", "t1")
    assert resp["object"] == "agent.error"
    assert resp["code"] == "INTERNAL_ERROR"


# 4) result()
def test_result_success():
    adapter, client = build_adapter_with_fake_client()
    resp = adapter.result("x", "t1")

    assert client.results_called
    assert resp["object"] == "agent.run.result"
    assert resp["status"] in ("completed", "failed", "in_progress")


def test_result_missing_task():
