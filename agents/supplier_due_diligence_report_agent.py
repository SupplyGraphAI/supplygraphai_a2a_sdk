#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : supplier_due_diligence_report_agent.py
"""

from supplygraphai_a2a_sdk.client import BaseAgent


class SupplierDueDiligenceReportAgent(BaseAgent):
    def __init__(self, client):
        super().__init__(client, agent_id="due_diligence_report")
