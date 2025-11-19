#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : corporate_exception_report_agent.py
"""

from supplygraphai_a2a_sdk.client import BaseAgent


class CorporateExceptionReportAgent(BaseAgent):
    def __init__(self, client):
        super().__init__(client, agent_id="corporate_exception_report")
