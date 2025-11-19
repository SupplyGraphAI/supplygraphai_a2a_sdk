# SupplyGraph Airflow Adapter

## Overview

The **SupplyGraph Airflow Adapter** enables seamless integration of any SupplyGraph A2A agent  
into **Apache Airflow DAGs** without adding Airflow as a dependency to the SDK.

This adapter:

- Does **not** import Airflow internally
- Provides a mixin that gives Airflow operators the ability to run A2A agents
- Supports:
  - `run` — start a task, including multi-round workflows  
  - `status` — poll task progress  
  - `results` — fetch final output  
  - `stream=True` — enables THINKING/streaming mode (SSE)
- Provides a **factory helper** for dynamically creating new operator classes


## Installation Requirements

Install SDK in your Airflow environment:

```
pip install supplygraphai-a2a-sdk
```

Install Airflow in your project (SDK does *not* include Airflow):

```
pip install apache-airflow
```


## 1. Using the Mixin Directly (Recommended)

```python
from airflow.models import BaseOperator
from supplygraphai_a2a_sdk.adapters.airflow_adapter import SupplyGraphAirflowOperatorMixin

class TariffCalcOperator(BaseOperator, SupplyGraphAirflowOperatorMixin):
    pass
```

### Example DAG usage:

```python
task = TariffCalcOperator(
    task_id="tariff_job",
    agent_id="tariff_calc",
    api_key="sk-xxx",
    text="import 100kg ice cream from CN",
    mode="run",
)
```

The operator will execute the agent and push the full A2A result into XCom.


## 2. Using the Factory Helper

You can also generate a fully functional operator dynamically:

```python
from airflow.models import BaseOperator
from supplygraphai_a2a_sdk.adapters.airflow_adapter import create_airflow_operator

TariffOperator = create_airflow_operator(
    BaseOperator,
    agent_id="tariff_calc",
    api_key="sk-xxx",
)

task = TariffOperator(
    task_id="job1",
    text="import 50kg cheese from FR",
    mode="run",
)
```


## 3. Supported Modes

| Mode         | Behavior |
|--------------|----------|
| `run`        | Begins an A2A workflow or continues one via `task_id_override` |
| `status`     | Polls task state |
| `results`    | Fetches final output |


## 4. Multi-Round Workflow Example

### Round 1

```python
task1 = TariffCalcOperator(
    task_id="start",
    agent_id="tariff_calc",
    api_key="sk",
    text="Import laptop",
    mode="run",
)
```

Response:

```json
{
  "code": "WAITING_USER",
  "message": "Please specify the country of origin.",
  "data": { "task_id": "tsk_abc123" }
}
```

### Round 2 — Continue

```python
task2 = TariffCalcOperator(
    task_id="continue",
    agent_id="tariff_calc",
    api_key="sk",
    text="Country is Vietnam",
    mode="run",
    task_id_override="tsk_abc123",
)
```


## 5. Streaming Mode (THINKING Frames)

```python
task = TariffCalcOperator(
    task_id="streaming_job",
    agent_id="tariff_calc",
    api_key="sk",
    text="classify steel bolts",
    mode="run",
    stream=True,
)
```

Airflow logs will show thinking events.


## 6. Error Handling

Handled via Python exceptions:

- Missing `task_id_override` for `status` or `results`
- Unsupported modes
- Network/API errors surfaced as `SupplyGraphAPIError`


## 7. Best Practices

- Store `task_id` in XCom for multi-round workflows  
- Use scheduled polling tasks for long-running A2A operations  
- Keep `execute()` idempotent in Airflow DAGs  


## 8. Class Reference

### SupplyGraphAirflowOperatorMixin Parameters

| Parameter | Description |
|----------|-------------|
| `agent_id` | A2A agent name |
| `api_key` | SupplyGraph API key |
| `text` | Input for run-mode |
| `mode` | run/status/results |
| `task_id_override` | Multi-round continuation |
| `stream` | Enable SSE |
| `base_url` | A2A gateway URL |
