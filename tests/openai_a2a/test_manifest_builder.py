#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : test_manifest_builder.py
"""
import json
import pytest

from supplygraphai_a2a_sdk.adapters.openai_a2a.manifest_builder import (
    build_openai_manifest
)


def load_golden(name: str):
    """
    Load a golden snapshot test case from the JSON file.
    """
    path = "tests/openai_a2a/test_manifest_builder_golden.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data[name]


# ----------------------------------------------------------------------
# 1. Basic mapping test
# ----------------------------------------------------------------------
def test_manifest_basic():
    sg_manifest = {
        "agent_id": "tariff_calc",
        "name": "Tariff Agent",
        "version": "1.0.0",
        "description": "Test agent",
        "capabilities": ["run", "status", "results"],
        "protocol": {
            "streaming": True,
            "base_url": "https://agent.example/v1",
            "endpoints": {"run": "/run", "manifest": "/manifest"},
            "methods": ["GET", "POST"],
        },
        "input_schema": {"type": "object"},
        "output_schema": {"type": "object"},
        "pricing": {"unit": "credits", "per_run": 5},
        "auth": {"required": True},
    }

    oai = build_openai_manifest(sg_manifest)

    assert oai["object"] == "agent"
    assert oai["id"] == "tariff_calc"
    assert oai["name"] == "Tariff Agent"
    assert oai["type"] == "agent"

    assert oai["capabilities"]["run"] is True
    assert oai["capabilities"]["status"] is True
    assert oai["capabilities"]["results"] is True
    assert oai["capabilities"]["streaming"] is True

    assert oai["pricing"]["unit"] == "credits"
    assert oai["pricing"]["per_run"] == 5

    assert oai["api_key_required"] is True
    assert "extended" in oai


# ----------------------------------------------------------------------
# 2. Missing-field resilience test
# ----------------------------------------------------------------------
def test_manifest_missing_fields():
    sg_manifest = {
        "agent_id": "simple_agent",
        "name": "Simple Agent",
    }

    oai = build_openai_manifest(sg_manifest)

    assert oai["id"] == "simple_agent"
    assert oai["name"] == "Simple Agent"
    assert oai["version"] == "1.0.0"  # default fallback
    assert "extended" in oai


# ----------------------------------------------------------------------
# 3. Extra fields must be placed in extended.extra_fields
# ----------------------------------------------------------------------
def test_manifest_extra_fields_are_segregated():
    sg_manifest = {
        "agent_id": "x",
        "name": "X Agent",
        "extra_setting_1": 123,
        "extra_setting_2": {"a": 1},
    }

    oai = build_openai_manifest(sg_manifest)

    assert "extra_setting_1" not in oai
    assert "extra_setting_2" not in oai

    extra = oai["extended"]["extra_fields"]
    assert extra["extra_setting_1"] == 123
    assert extra["extra_setting_2"] == {"a": 1}


# ----------------------------------------------------------------------
# 4. Golden snapshot test
# ----------------------------------------------------------------------
def test_manifest_golden_snapshot():
    sg_manifest = load_golden("input_tariff_agent")
    expected = load_golden("output_tariff_agent")

    oai = build_openai_manifest(sg_manifest)

    assert oai == expected
