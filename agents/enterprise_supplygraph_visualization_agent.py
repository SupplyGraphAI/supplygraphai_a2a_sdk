#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : enterprise_supplygraph_visualization_agent.py
"""

from supplygraphai_a2a_sdk.client import BaseAgent


class EnterpriseSupplyGraphVisualizationAgent(BaseAgent):
    def __init__(self, client):
        super().__init__(client, agent_id="sg_visualization")
