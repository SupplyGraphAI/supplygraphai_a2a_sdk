# DSPy Adapter — SupplyGraph A2A SDK

The **DSPy Adapter** enables any SupplyGraph A2A Agent to be used as a predictor inside the **DSPy** ecosystem, including:

- `dspy.Predictor`
- `dspy.Module`
- Signature‑based inference pipelines
- Custom DSPy logic

This adapter **does not import DSPy** directly.  
The host application wraps the provided predictor function into DSPy modules.


## Import

```python
from supplygraphai_a2a_sdk.adapters import create_dspy_predictor
```


## 1. Creating a DSPy Predictor

```python
from supplygraphai_a2a_sdk.adapters import create_dspy_predictor

predictor_wrapper = create_dspy_predictor(
    "tariff_calc",
    api_key="sk-...",
)
predict = predictor_wrapper.as_predictor()
```


## 2. Using in a DSPy Module

```python
import dspy
from supplygraphai_a2a_sdk.adapters import create_dspy_predictor

sg = create_dspy_predictor("tariff_calc", api_key="sk-...")

class MyModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.tool = sg.as_predictor()

    def forward(self, text: str):
        resp = self.tool(text=text)
        return resp["data"]["content"]

m = MyModule()
print(m("import 100kg chocolate from FR"))
```


## 3. Predictor Interface

The predictor follows DSPy's expected signature:

```python
output = predictor(
    text="...",
    mode="run" | "status" | "results",
    task_id="...",
    stream=False,
    **kwargs
)
```

### Supported modes:

| Mode        | Description |
|-------------|-------------|
| `"run"`     | Starts a new A2A task or continues one if task_id is passed |
| `"status"`  | Query status of a running multiround agent task |
| `"results"` | Fetch final results for a completed task |


## Multi‑Round Workflow Support

If the DSPy model must continue a task:

```python
resp = predict(text="Start task", mode="run")
task_id = resp["data"]["task_id"]

resp2 = predict(
    text="Additional info",
    mode="run",
    task_id=task_id
)
```


## Streaming Support

```python
predict(text="...", stream=True)
```

Returns an **SSE generator**, identical to core A2A behavior.


## Factory Helper

```python
sg = create_dspy_predictor("agent_id", api_key="sk-...")
predict = sg.as_predictor()
```


## Source Overview

The adapter provides:

- `DSPyPredictorWrapper`
- `create_dspy_predictor()`

No external dependencies are added to the SDK.


## Example Output

```json
{
  "success": true,
  "code": "TASK_COMPLETED",
  "data": {
    "task_id": "tsk_123",
    "content": "Final result..."
  }
}
```
