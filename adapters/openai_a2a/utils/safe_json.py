#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : safe_json.py

Safe JSON serialization helper.
"""

import json


def safe_json_dumps(data):
    try:
        return json.dumps(data)
    except Exception:
        return json.dumps(str(data))
