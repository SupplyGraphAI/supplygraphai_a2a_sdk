#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : timestamp.py

Timestamp utilities for OpenAI A2A adapters.
"""

import time


def now_timestamp() -> int:
    """
    Return current timestamp (int, seconds since epoch).
    """
    return int(time.time())
