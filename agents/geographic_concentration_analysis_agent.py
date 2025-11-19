#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : geographic_concentration_analysis_agent.py
"""

from supplygraphai_a2a_sdk.client import BaseAgent


class GeographicConcentrationAnalysisAgent(BaseAgent):
    def __init__(self, client):
        super().__init__(client, agent_id="sg_chokepoint")
