#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : us_tariff_calculation_agent.py
"""

from ..client import BaseAgent


class USTariffCalculationAgent(BaseAgent):
    def __init__(self, client):
        super().__init__(client, agent_id="tariff_calc")
