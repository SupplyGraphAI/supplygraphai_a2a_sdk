#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : stream_parser.py

Improved SSE parser for SupplyGraph A2A Agents
Compatible with full SSE standard + SupplyGraph THINKING events
"""

import json
from typing import Any, Dict, Generator


def parse_sse(response) -> Generator[Dict[str, Any], None, None]:
    """
    SSE Parser for SupplyGraph A2A streaming.

    Supports:
    - event: stream
    - multi-line data
    - THINKING events (interpreting/executing)
    - [DONE] termination
    """

    event_type = "stream"
    data_buffer = []

    for raw_line in response.iter_lines(decode_unicode=True):
        if raw_line is None:
            continue

        line = raw_line.strip()

        # Blank line = event boundary
        if not line:
            if data_buffer:
                payload_str = "\n".join(data_buffer).strip()
                data_buffer = []

                if payload_str == "[DONE]":
                    yield {"event": "end", "data": "[DONE]"}
                    return

                try:
                    payload = json.loads(payload_str)
                except Exception:
                    payload = payload_str

                yield {"event": event_type, "data": payload}

            continue

        # event: ...
        if line.startswith("event:"):
            event_type = line[len("event:"):].strip()
            continue

        # data: ...
        if line.startswith("data:"):
            data_buffer.append(line[len("data:"):].strip())
            continue

        # fallback: treat entire line as data
        data_buffer.append(line.strip())
