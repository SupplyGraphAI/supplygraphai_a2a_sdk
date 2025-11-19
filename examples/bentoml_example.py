#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : bentoml_example.py.py

BentoML integration example for SupplyGraph AI A2A SDK.

This example demonstrates how to use:
    - create_bentoml_runner()
    - BentoMLRunnerWrapper
    - BentoMLServiceWrapper
    - Wiring SupplyGraph agents into a BentoML Service

IMPORTANT:
    BentoML is NOT installed with this SDK.
    To run this example, install BentoML first:

        pip install bentoml
"""

from supplygraphai_a2a_sdk.adapters import (
    create_bentoml_runner,
    create_bentoml_service,
)

try:
    from bentoml import Service, Runner, io
except ImportError:
    raise ImportError(
        "BentoML is not installed.\n"
        "Install it with: pip install bentoml"
    )


# ------------------------------------------------------------
# 1. Build a SupplyGraph Runner via Adapter
# ------------------------------------------------------------
runner_wrapper = create_bentoml_runner(
    agent_id="tariff_calc",
    api_key="YOUR_API_KEY",
)

# BentoML requires a Runner object, constructed from a callable
runner = Runner(runner_wrapper.run_task)

# ------------------------------------------------------------
# 2. Build a BentoML Service
# ------------------------------------------------------------
svc = Service(
    name="tariff_calc_service",
    runners=[runner],
)

# Wrap the runner with the SDK's service wrapper
sg_service = create_bentoml_service(runner_wrapper)


# ------------------------------------------------------------
# 3. Define service endpoints
# ------------------------------------------------------------
@svc.api(input=io.JSON(), output=io.JSON())
def run_task(data: dict):
    """
    Example request payload:

        {
            "mode": "run",
            "text": "import 100kg apples from CN",
            "task_id": null,
            "stream": false
        }
    """
    return sg_service.handle_request(data)


@svc.api(input=io.JSON(), output=io.JSON())
def check_status(data: dict):
    """
    Example:

        {
            "mode": "status",
            "task_id": "tsk_123"
        }
    """
    return sg_service.handle_request(data)


@svc.api(input=io.JSON(), output=io.JSON())
def fetch_results(data: dict):
    """
    Example:

        {
            "mode": "results",
            "task_id": "tsk_123"
        }
    """
    return sg_service.handle_request(data)

