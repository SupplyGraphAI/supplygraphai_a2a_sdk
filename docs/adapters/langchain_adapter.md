# LangChain Adapter for SupplyGraph AI A2A SDK

## Overview
The **LangChain Adapter** allows any SupplyGraph A2A agent to be used as a native LangChain Tool or LCEL Runnable without requiring LangChain as a dependency inside the SDK.

File: `langchain_adapter.py`


## Features
- Works with **langchain.tools.Tool**
- Works with **LCEL Runnable**
- Supports:
  - Single-turn run
  - Multi-turn workflows (task_id)
  - status()
  - results()
  - streaming mode


## Usage: LangChain Tool

```python
from langchain.tools import Tool
from supplygraphai_a2a_sdk.adapters.langchain_adapter import create_langchain_tool

sg_tool = create_langchain_tool("tariff_calc", api_key="sk-...")

tool = Tool(
    name="tariff_calc",
    description="SupplyGraph Tariff Calculation Agent",
    func=sg_tool.run,
)
```


## Usage: LCEL Runnable

```python
sg_tool = create_langchain_tool("tariff_calc", api_key="sk-...")

runnable = sg_tool.as_runnable()

result = runnable({
    "text": "Import 100kg chocolate from FR",
    "mode": "run"
})
```


## API Details

### Initialize

```python
sg_tool = SupplyGraphLangChainTool(
    agent_id="tariff_calc",
    api_key="sk-...",
)
```


### `.run(...)`

| Param     | Type      | Description |
|----------|-----------|-------------|
| text     | str       | Input text |
| mode     | str       | run \| status \| results |
| task_id  | str/None  | For multi-turn |
| stream   | bool      | Enable SSE |
| kwargs   | dict      | Additional fields |


### `.as_runnable()`

Returns a function compatible with LangChain’s LCEL, taking:

```python
{
    "text": "...",
    "mode": "run",
    "task_id": null,
    "stream": false
}
```


## Factory Helper

```python
tool = create_langchain_tool("tariff_calc", api_key="sk-...")
```


## Notes
- Adapter does **not** import LangChain.
- Pure Python, minimal interface surface.
- Mirrors BaseAgent behavior.
