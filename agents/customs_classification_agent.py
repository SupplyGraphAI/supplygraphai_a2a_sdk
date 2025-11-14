#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : customs_classification_agent.py
"""

from ..client import BaseAgent


class CustomsClassificationAgent(BaseAgent):
    def __init__(self, client):
        super().__init__(client, agent_id="tariff_calc")
