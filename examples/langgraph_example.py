#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    : 
@File    : langgraph_example.py.py

LangGraph integration example for SupplyGraph AI A2A SDK.

Demonstrates:
    - Using create_langgraph_tool() to create a LangGraph-compatible node
    - Calling the tool directly
    - Handling WAITING_USER → multi-turn
    - Building a full LangGraph state machine graph
    - Using streaming (SSE) generator

LangGraph is NOT included with the SDK.
To run this example, install LangGraph:

    pip install langgraph langchain-core
"""

from supplygraphai_a2a_sdk.adapters import create_langgraph_tool

try:
    from langgraph.graph import StateGraph, END
except ImportError:
    raise ImportError(
        "LangGraph is not installed.\n"
        "Install with: pip install langgraph langchain-core"
    )


# ------------------------------------------------------------
# 1. Create LangGraph tool
# ------------------------------------------------------------
tool = create_langgraph_tool(
    agent_id="tariff_calc",
    api_key="YOUR_API_KEY",
)

print("\n=== Tool Metadata ===")
print("Name:", tool.__name__)
print("Description:", tool.description)
print("Manifest keys:", list(tool.manifest.keys()))


# ------------------------------------------------------------
# 2. Direct single-turn execution
# ------------------------------------------------------------
print("\n=== Direct Call (Single-turn) ===")

resp = tool("Import 20kg cheese from France")
print("Response:", resp)


# ------------------------------------------------------------
# 3. Multi-turn (task_id) example
# ------------------------------------------------------------
print("\n=== Multi-turn Example ===")

initial = tool("Calculate tariff for leather shoes")
print("Initial:", initial)

tid = initial.get("task_id")

if initial.get("status") == "WAITING_USER" and tid:
    print("Agent requires more information...")

    follow = tool(
        "Country is Vietnam",
        task_id=tid,
    )
    print("Follow-up:", follow)


# ------------------------------------------------------------
# 4. Streaming example (SSE frames)
# ------------------------------------------------------------
print("\n=== Streaming Example ===")

stream_events = tool(
    "Import 100kg apples from Chile",
    stream=True,
)

for evt in stream_events:
    print("Stream:", evt)


# ------------------------------------------------------------
# 5. Building a LangGraph workflow
# ------------------------------------------------------------

# --- State definition ---
class State(dict):
    """
    LangGraph state must support dict-like storage.
    We store:
        - text     : user input text
        - task_id  : SupplyGraph multi-turn task id
        - response : last A2A response
    """
    pass


# --- Node function ---
def sg_node(state: State) -> State:
    text = state.get("text", "")
    task_id = state.get("task_id")

    resp = tool(
        text,
        task_id=task_id,
    )

    # Store response in state
    state["response"] = resp

    # Update task_id for multi-turn workflows
    if isinstance(resp, dict) and "task_id" in resp:
        state["task_id"] = resp["task_id"]

    return state


# --- Conditional edge: Continue if WAITING_USER ---
def should_continue(state: State) -> bool:
    resp = state.get("response", {})
    return resp.get("status") == "WAITING_USER"


# --- Build graph ---
graph = StateGraph(State)

graph.add_node("supplygraph", sg_node)
graph.set_entry_point("supplygraph")

graph.add_conditional_edges(
    "supplygraph",
    should_continue,
    {
        True: "supplygraph",  # Continue asking
        False: END,           # End workflow
    }
)

compiled = graph.compile()


# ------------------------------------------------------------
# 6. Run LangGraph state machine
# ------------------------------------------------------------
print("\n=== LangGraph Workflow Execution ===")

final_state = compiled.invoke({
    "text": "Calculate tariff for leather shoes"
})

print("Final Workflow Output:")
print(final_state)
