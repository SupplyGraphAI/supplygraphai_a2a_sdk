#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : content_extractor.py

Unified content extractor for SupplyGraph → OpenAI output formats.

This module normalizes SG's 'data.content' field into a consistent
OpenAI A2A output structure.
"""

from typing import Any, Dict, Optional


def extract_output_from_sg_content(content: Any) -> Optional[Dict[str, Any]]:
    """
    Convert SG's content (string | dict | structured result) into
    OpenAI output format:

    {
        "type": "text" | "json",
        "content": ...
    }

    Returns None if no output should be returned (e.g., in intermediate states).
    """

    if content is None:
        return None

    # Plain text → text output
    if isinstance(content, str):
        return {
            "type": "text",
            "content": content
        }

    # Structured dict
    if isinstance(content, dict):
        # Structured SG result: { type: "result", data: {...} }
        if content.get("type") == "result":
            return {
                "type": "json",
                "content": content.get("data", {})
            }

        # Fallback: treat dict as plain JSON
        return {
            "type": "json",
            "content": content
        }

    # Fallback: convert to string
    return {
        "type": "text",
        "content": str(content)
    }
