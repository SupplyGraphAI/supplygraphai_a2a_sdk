# BentoML Adapter — SupplyGraph AI A2A SDK

This document describes the **BentoML integration adapter** shipped in:

```
supplygraphai_a2a_sdk/adapters/bentoml_adapter.py
```

It explains usage, capabilities, streaming behavior, WAITING_USER handling, and the factory helpers.

---

## Overview

The BentoML adapter exposes any SupplyGraph A2A agent as:

- A **BentoML Runner-compatible wrapper**
- A **Service wrapper** that plugs into a BentoML `Service`

It is designed to:

- Avoid importing BentoML inside the SDK  
- Support **multi-round tasks** (`task_id`)
- Support **WAITING_USER**  
- Support **SSE streaming**  
- Stay consistent with all other A2A adapters

---

## 1. BentoMLRunnerWrapper

The runner wrapper exposes:

```python
runner = BentoMLRunnerWrapper(agent_id, api_key)
output = runner.run_task(payload_dict)
```

### Supported fields in `payload`:

```json
{
  "mode": "run" | "status" | "results",
  "text": "...",
  "task_id": "...",
  "stream": false
}
```

### Mode behavior

| mode | Behavior |
|------|----------|
| **run** | Calls `agent.run(...)` |
| **status** | Calls `agent.status(...)` |
| **results** | Calls `agent.results(...)` |

### WAITING_USER normalization

If the agent requires more info:

```json
{
  "status": "WAITING_USER",
  "message": "…",
  "task_id": "tsk_xxx",
  "agent": "tariff_calc"
}
```

### Streaming

If `stream=True`, the wrapper returns the SSE generator directly.

---

## 2. BentoMLServiceWrapper

Thin layer that forwards payload to the runner:

```python
svc_wrapper = BentoMLServiceWrapper(runner)
svc_wrapper.handle_request(payload)
```

This is intended for BentoML:

```python
@svc.api(input=io.JSON(), output=io.JSON())
def run_task(data):
    return sg_service.handle_request(data)
```

---

## 3. Factory Helpers

### Create Runner

```python
from supplygraphai_a2a_sdk.adapters import create_bentoml_runner

runner = create_bentoml_runner("tariff_calc", api_key="sk-...")
```

### Create Service Wrapper

```python
from supplygraphai_a2a_sdk.adapters import create_bentoml_service

svc_wrapper = create_bentoml_service(runner)
```

---

## 4. Full Example (Recommended)

```python
from bentoml import Service, Runner, io
from supplygraphai_a2a_sdk.adapters import (
    create_bentoml_runner,
    create_bentoml_service,
)

runner = Runner(create_bentoml_runner("tariff_calc", api_key="sk-...").run_task)
svc = Service("tariff_calc_service", runners=[runner])

sg_service = create_bentoml_service(runner)

@svc.api(input=io.JSON(), output=io.JSON())
def run_task(data):
    return sg_service.handle_request(data)
```

---

## 5. Error Handling

All SupplyGraph API errors are normalized to:

```json
{
  "status": "ERROR",
  "message": "...",
  "api_code": "...",
  "http_status": 400,
  "details": { ... }
}
```

---

## 6. Notes

- The adapter is **manifest-aware** (via BaseAgent)
- The adapter does **not** depend on BentoML
- Host applications (not SDK) import BentoML
