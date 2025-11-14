#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : __init__.py.py
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Public export surface for all SupplyGraph A2A Adapters.
"""

from .airflow_adapter import (
    SupplyGraphAirflowOperatorMixin,
    create_airflow_operator,
)

from .autogen_adapter import AutoGenTool

from .bentoml_adapter import (
    BentoMLRunnerWrapper,
    BentoMLServiceWrapper,
    create_bentoml_runner,
    create_bentoml_service,
)

from .crewai_adapter import CrewAITool

from .dspy_adapter import (
    DSPyPredictorWrapper,
    create_dspy_predictor
)

from .flowise_adapter import (
    FlowiseToolWrapper,
    create_flowise_tool
)

from .google_a2a_adapter import GoogleA2AAdapter

from .haystack_adapter import (
    SupplyGraphHaystackNode,
    create_haystack_node,
)

from .langchain_adapter import (
    SupplyGraphLangChainTool,
    create_langchain_tool,
)

from .langgraph_adapter import create_langgraph_tool

from .llamaindex_adapter import (
    LlamaIndexToolWrapper,
    create_llamaindex_tool,
)

from .mcp_adapter import (
    MCPAdapter,
    create_mcp_tool
)

from .semantic_kernel_adapter import make_semantic_skill


__all__ = [
    # Airflow
    "SupplyGraphAirflowOperatorMixin",
    "create_airflow_operator",

    # AutoGen
    "AutoGenTool",

    # BentoML
    "BentoMLRunnerWrapper",
    "BentoMLServiceWrapper",
    "create_bentoml_runner",
    "create_bentoml_service",

    # CrewAI
    "CrewAITool",

    # DSPy
    "DSPyPredictorWrapper",
    "create_dspy_predictor",

    # Flowise
    "FlowiseToolWrapper",
    "create_flowise_tool",

    # Google A2A
    "GoogleA2AAdapter",

    # Haystack
    "SupplyGraphHaystackNode",
    "create_haystack_node",

    # LangChain
    "SupplyGraphLangChainTool",
    "create_langchain_tool",

    # LangGraph
    "create_langgraph_tool",

    # LlamaIndex
    "LlamaIndexToolWrapper",
    "create_llamaindex_tool",

    # MCP
    "MCPAdapter",
    "create_mcp_tool",

    # Semantic Kernel
    "make_semantic_skill",
]
