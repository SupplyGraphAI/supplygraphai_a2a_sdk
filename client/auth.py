#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : auth.py
"""
from typing import Dict, Optional


def get_auth_header(api_key: Optional[str] = None) -> Dict[str, str]:
    """
    Build HTTP headers for authenticated requests.
    """
    headers: Dict[str, str] = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers
