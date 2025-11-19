#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : __init__.py

Public export surface for all SupplyGraph A2A Adapters.
"""

# ---------------------------------------------------------
# Airflow Adapter
# ---------------------------------------------------------
from supplygraphai_a2a_sdk.adapters.airflow_adapter import (
    SupplyGraphAirflowOperatorMixin,
    create_airflow_operator,
)

# ---------------------------------------------------------
# AutoGen Adapter
# ---------------------------------------------------------
from supplygraphai_a2a_sdk.adapters.autogen_adapter import AutoGenTool

# ---------------------------------------------------------
# BentoML Adapter
# ---------------------------------------------------------
from supplygraphai_a2a_sdk.adapters.bentoml_adapter import (
    BentoMLRunnerWrapper,
    BentoMLServiceWrapper,
    create_bentoml_runner,
    create_bentoml_service,
)

# ---------------------------------------------------------
# CrewAI Adapter
# ---------------------------------------------------------
from supplygraphai_a2a_sdk.adapters.crewai_adapter import CrewAITool

# ---------------------------------------------------------
# DSPy Adapter
# ---------------------------------------------------------
from supplygraphai_a2a_sdk.adapters.dspy_adapter import (
    DSPyPredictorWrapper,
    create_dspy_predictor,
)

# ---------------------------------------------------------
# Flowise Adapter
# ---------------------------------------------------------
from supplygraphai_a2a_sdk.adapters.flowise_adapter import (
    FlowiseToolWrapper,
    create_flowise_tool,
)

# ---------------------------------------------------------
# Google A2A Adapter
# ---------------------------------------------------------
from supplygraphai_a2a_sdk.adapters.google_a2a_adapter import GoogleA2AAdapter

# ---------------------------------------------------------
# Haystack Adapter
# ---------------------------------------------------------
from supplygraphai_a2a_sdk.adapters.haystack_adapter import (
    SupplyGraphHaystackNode,
    create_haystack_node,
)

# ---------------------------------------------------------
# LangChain Adapter
# ---------------------------------------------------------
from supplygraphai_a2a_sdk.adapters.langchain_adapter import (
    SupplyGraphLangChainTool,
    create_langchain_tool,
)

# ---------------------------------------------------------
# LangGraph Adapter
# ---------------------------------------------------------
from supplygraphai_a2a_sdk.adapters.langgraph_adapter import create_langgraph_tool

# ---------------------------------------------------------
# LlamaIndex Adapter
# ---------------------------------------------------------
from supplygraphai_a2a_sdk.adapters.llamaindex_adapter import (
    LlamaIndexToolWrapper,
    create_llamaindex_tool,
)

# ---------------------------------------------------------
# MCP Adapter
# ---------------------------------------------------------
from supplygraphai_a2a_sdk.adapters.mcp_adapter import (
    MCPAdapter,
    create_mcp_tool,
)

# ---------------------------------------------------------
# Semantic Kernel Adapter
# ---------------------------------------------------------
from supplygraphai_a2a_sdk.adapters.semantic_kernel_adapter import make_semantic_skill

# ---------------------------------------------------------
# OpenAI A2A Adapter (NEW)
# ---------------------------------------------------------
from supplygraphai_a2a_sdk.adapters.openai_a2a_adapter import OpenAIA2AAdapter


# ---------------------------------------------------------
# Public Exports
# ---------------------------------------------------------
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

    # OpenAI A2A
    "OpenAIA2AAdapter",
]
