#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : extensions_builder.py

Build OpenAI extensions.supplygraph payloads.

All SG-specific metadata should be stored in:
{
  "extensions": {
       "supplygraph": { ... }
  }
}
"""

from typing import Dict, Any


def build_sg_extensions(sg_data: Dict[str, Any], sg_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Extract meaningful SG fields and put them into extensions.supplygraph.

    Allowed fields:
    - stage
    - code
    - progress
    - timestamp
    - agent
    - credits_used
    - is_final
    """
    sg_metadata = sg_metadata or {}
    data = sg_data or {}

    ext = {
        "stage": data.get("stage"),
        "code": data.get("code"),
        "progress": data.get("progress"),
        "timestamp": data.get("timestamp"),
        "agent": data.get("agent"),
        "is_final": data.get("is_final"),
        "credits_used": sg_metadata.get("credits_used"),
    }

    # Remove None fields for cleanliness
    ext = {k: v for k, v in ext.items() if v is not None}

    return {
        "extensions": {
            "supplygraph": ext
        }
    }
