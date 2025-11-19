#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : dspy_example.py.py

DSPy integration example for SupplyGraph AI A2A SDK.

This example demonstrates:
    - Using create_dspy_predictor()
    - Using DSPyPredictorWrapper.as_predictor()
    - Integrating SupplyGraph agents into DSPy Modules
    - Single-turn and multi-turn (task_id-based) execution

IMPORTANT:
    DSPy is NOT included in the SDK.
    Install it separately if you want to run this example:

        pip install dspy
"""

from supplygraphai_a2a_sdk.adapters import create_dspy_predictor

try:
    import dspy
except ImportError:
    raise ImportError(
        "DSPy is not installed.\n"
        "Install it with: pip install dspy"
    )


# ------------------------------------------------------------
# 1. Build predictor with SupplyGraph adapter
# ------------------------------------------------------------
predictor_wrapper = create_dspy_predictor(
    agent_id="tariff_calc",
    api_key="YOUR_API_KEY",
)

predict_fn = predictor_wrapper.as_predictor()


# ------------------------------------------------------------
# 2. Use predictor directly
# ------------------------------------------------------------
print("\n=== DSPy Direct Predictor Call ===")

resp = predict_fn(
    text="Import 100kg oranges from Egypt",
    mode="run",
)

print("Response:", resp)


# ------------------------------------------------------------
# 3. Define a DSPy Module using the SupplyGraph predictor
# ------------------------------------------------------------
class TariffModule(dspy.Module):
    """
    Example DSPy module that calls the SupplyGraph agent internally.
    """
    def __init__(self):
        super().__init__()
        self.predict = predict_fn

    def forward(self, text: str):
        result = self.predict(text=text)
        return result.get("data", {}).get("content")


# ------------------------------------------------------------
# 4. Run module inference
# ------------------------------------------------------------
print("\n=== DSPy Module Inference ===")
module = TariffModule()

output = module("Import 50kg chocolate from FR")
print("Module Output:", output)


# ------------------------------------------------------------
# 5. Multi-turn execution (task_id)
# ------------------------------------------------------------
print("\n=== Multi-turn Example ===")

first = predict_fn(
    text="Calculate tariff for leather shoes",
    mode="run",
)

print("Initial:", first)

task_id = first.get("data", {}).get("task_id")

if task_id and first.get("code") == "WAITING_USER":
    print("Agent requested more info, providing follow-up...")

    follow = predict_fn(
        text="Country of origin is Vietnam",
        mode="run",
        task_id=task_id,
    )

    print("Follow-up:", follow)
