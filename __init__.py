#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    :
@File    : __init__.py

Public SDK entrypoint for SupplyGraph AI A2A Agent SDK.

Exposes:
- AgentClient
- BaseAgent
- Auto-generated agent wrappers
- Public adapters
"""

# ---------------------------------------------------------
# Core SDK Client + Base Agent
# ---------------------------------------------------------
from supplygraphai_a2a_sdk.client.agent_client import AgentClient
from supplygraphai_a2a_sdk.client.base_agent import BaseAgent

# ---------------------------------------------------------
# Auto-generated agent wrappers
# ---------------------------------------------------------
from supplygraphai_a2a_sdk import agents
from supplygraphai_a2a_sdk.agents import *  # Safe because agents.__all__ is defined


# ---------------------------------------------------------
# Public Adapters
# ---------------------------------------------------------
from supplygraphai_a2a_sdk.adapters import (
    # Google
    GoogleA2AAdapter,

    # CrewAI
    CrewAITool,

    # LangGraph
    create_langgraph_tool,

    # Semantic Kernel
    make_semantic_skill,

    # DSPy
    create_dspy_predictor,

    # Flowise
    FlowiseToolWrapper,
    create_flowise_tool,

    # LlamaIndex
    LlamaIndexToolWrapper,
    create_llamaindex_tool,

    # MCP (Model Context Protocol)
    MCPAdapter,
    create_mcp_tool,

    # BentoML
    create_bentoml_runner,
    create_bentoml_service,

    # Haystack
    SupplyGraphHaystackNode,
    create_haystack_node,

    # NEW — OpenAI A2A Adapter
    OpenAIA2AAdapter,
)


# ---------------------------------------------------------
# Public export surface
# ---------------------------------------------------------
__all__ = [
    # Core
    "AgentClient",
    "BaseAgent",

    # Auto-generated agents
    *agents.__all__,

    # Adapters
    "GoogleA2AAdapter",
    "CrewAITool",
    "create_langgraph_tool",
    "make_semantic_skill",
    "create_dspy_predictor",
    "FlowiseToolWrapper",
    "create_flowise_tool",
    "LlamaIndexToolWrapper",
    "create_llamaindex_tool",
    "MCPAdapter",
    "create_mcp_tool",
    "create_bentoml_runner",
    "create_bentoml_service",
    "SupplyGraphHaystackNode",
    "create_haystack_node",

    # NEW — OpenAI A2A Adapter
    "OpenAIA2AAdapter",
]

__version__ = "0.2.0"
