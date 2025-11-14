# Semantic Kernel Adapter for SupplyGraph A2A Agents

This document describes the **Semantic Kernel adapter** implementation provided by the SupplyGraph A2A Python SDK.

The adapter enables any SupplyGraph Agent to be exposed as an **async Semantic Kernel skill function**, supporting:
- Multi‑round A2A workflows  
- Streaming THINKING events  
- WAITING_USER continuation  
- Manifest‑aware metadata  
- Async‑safe execution via `run_in_executor`

---

## 📌 File: `semantic_kernel_adapter.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Semantic Kernel Adapter for SupplyGraph A2A Agents  
Async-safe, multiround-capable, streaming-capable, manifest-aware.
"""

import asyncio
from typing import Any, Awaitable, Callable, Dict, Optional

from ..client.agent_client import AgentClient
from ..client.base_agent import BaseAgent
from ..utils.error_handler import SupplyGraphAPIError


def make_semantic_skill(
    agent_id: str,
    api_key: str,
    base_url: str = "https://agent.supplygraph.ai/api/v1/agents",
) -> Callable[..., Awaitable[Any]]:
    """
    Creates an async Semantic Kernel skill function for a SupplyGraph Agent.
    """

    client = AgentClient(api_key=api_key, base_url=base_url)
    agent = BaseAgent(client, agent_id)

    skill_name = agent.manifest.get("name", agent_id)
    skill_description = agent.manifest.get("description", "")

    async def skill(
        text: str,
        task_id: Optional[str] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        """
        Semantic Kernel entry-point for SupplyGraph A2A Agents.

        Supports:
        - multiround
        - WAITING_USER continuation
        - streaming THINKING events
        """

        # ---- run synchronous client.run safely in async env ----
        loop = asyncio.get_running_loop()

        try:
            result = await loop.run_in_executor(
                None,
                lambda: agent.run(
                    text=text,
                    task_id=task_id,
                    stream=stream,
                    **kwargs,
                ),
            )

            # ---------------- STREAMING -----------------
            if stream:
                # result is a generator
                async def async_streamer():
                    for frame in result:
                        yield frame
                return async_streamer()

            # ---------------- WAITING_USER --------------
            if agent.needs_user_input(result):
                return {
                    "status": "WAITING_USER",
                    "message": result.get("message", ""),
                    "task_id": agent.extract_task_id(result),
                    "agent": agent_id,
                }

            return result

        except SupplyGraphAPIError as e:
            return {
                "status": "ERROR",
                "message": str(e),
                "api_code": e.api_code,
                "details": e.errors,
                "http_status": e.http_status,
            }

    # Attach metadata for SK
    skill.__name__ = skill_name
    skill.__doc__ = skill_description
    skill.description = skill_description
    skill.agent_id = agent_id
    skill.manifest = agent.manifest

    return skill
```

---

## ✅ **What this adapter provides**

### **1. Fully async-compatible**
The underlying SDK is synchronous, so the adapter uses:
```python
loop.run_in_executor(None, lambda: agent.run(...))
```
This prevents blocking the SK event loop.

---

### **2. Streaming support (THINKING frames)**
When `stream=True`:
- `agent.run()` returns a generator  
- The adapter wraps it into an async generator  
- Semantic Kernel can iterate normally

---

### **3. Multi-round task continuation**
The adapter recognizes `WAITING_USER` via:
```python
agent.needs_user_input(result)
```

And returns a structured task‑continuation payload:
```json
{
  "status": "WAITING_USER",
  "message": "...",
  "task_id": "...",
  "agent": "<agent_id>"
}
```

---

### **4. Manifest-aware metadata**
Automatically exposes:

- `skill.__name__`
- `skill.__doc__`
- `skill.description`
- `skill.agent_id`
- `skill.manifest`

So SK can autodiscover the tool's metadata.
