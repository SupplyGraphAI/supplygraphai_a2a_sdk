#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : airflow_example.py.py

Airflow integration example for SupplyGraph AI A2A SDK.

This example demonstrates how to use:
    - SupplyGraphAirflowOperatorMixin
    - create_airflow_operator()

IMPORTANT:
    This file is intended to be placed inside an Airflow DAGs directory.
    Airflow must be installed separately (it is NOT a dependency of the SDK).
"""

from datetime import datetime
from airflow import DAG
from airflow.models import BaseOperator

from supplygraphai_a2a_sdk.adapters import (
    SupplyGraphAirflowOperatorMixin,
    create_airflow_operator,
)

# -------------------------------------------------------------------
# Example 1: Manual MixIn (recommended for full customization)
# -------------------------------------------------------------------
class TariffCalcOperator(BaseOperator, SupplyGraphAirflowOperatorMixin):
    """
    Example operator showing how to manually mix SupplyGraphAirflowOperatorMixin
    into a custom Airflow operator class.
    """
    def __init__(self, agent_id, api_key, text, **kwargs):
        BaseOperator.__init__(self, **kwargs)
        SupplyGraphAirflowOperatorMixin.__init__(
            self,
            agent_id=agent_id,
            api_key=api_key,
            text=text,
            mode="run",
        )


# -------------------------------------------------------------------
# Example 2: Dynamic operator creation (no class definition needed)
# -------------------------------------------------------------------
TariffOperatorDynamic = create_airflow_operator(
    BaseOperator,
    agent_id="tariff_calc",
    api_key="YOUR_API_KEY",
)


# -------------------------------------------------------------------
# Build DAG
# -------------------------------------------------------------------
with DAG(
    dag_id="supplygraph_airflow_example",
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    # Example 1: Custom operator
    run_tariff_task = TariffCalcOperator(
        task_id="tariff_op_custom",
        agent_id="tariff_calc",
        api_key="YOUR_API_KEY",
        text="import 100kg ice cream from CN",
    )

    # Example 2: Dynamic operator
    run_dynamic_tariff_task = TariffOperatorDynamic(
        task_id="tariff_op_dynamic",
        text="import 50kg cheese from FR",
        mode="run",
    )

    run_tariff_task >> run_dynamic_tariff_task
