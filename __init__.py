#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Public SDK entrypoint for SupplyGraph AI A2A Agent SDK.
Exposes:
- AgentClient
- BaseAgent
- Auto-generated agent wrappers
- Public adapters
"""

from .client.agent_client import AgentClient
from .client.base_agent import BaseAgent

# Agents (auto-generated wrappers)
from . import agents
from .agents import *  # safe because __all__ is explicitly defined

# Adapters — explicitly expose all adapter factory helpers
from .adapters import (
    GoogleA2AAdapter,
    CrewAITool,
    create_langgraph_tool,
    make_semantic_skill,
    create_dspy_predictor,
    FlowiseToolWrapper,
    create_flowise_tool,
    LlamaIndexToolWrapper,
    create_llamaindex_tool,
    MCPAdapter,
    create_mcp_tool,
    create_bentoml_runner,
    create_bentoml_service,
    SupplyGraphHaystackNode,
    create_haystack_node,
)

__all__ = [
    "AgentClient",
    "BaseAgent",

    # Agent wrappers
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
]

__version__ = "0.2.0"
