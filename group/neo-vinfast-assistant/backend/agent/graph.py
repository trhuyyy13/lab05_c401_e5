"""
NEO Agent — LangGraph ReAct Graph Definition.

Cơ chế ReAct loop:
  ┌─────────┐
  │  START   │
  └────┬─────┘
       ▼
  ┌─────────┐     tool call?     ┌─────────┐
  │  REASON  │ ───── yes ──────▶ │   ACT   │
  │ (Think)  │                   │ (Tool)  │
  └────┬─────┘                   └────┬────┘
       │ no                           │
       ▼                              │
  ┌─────────┐                         │
  │ RESPOND  │ ◀──────────────────────┘
  │ (Answer) │
  └─────────┘

Trong mock mode: bypass LangGraph, dùng MockLLM trực tiếp.
Khi có API key: uncomment phần LangGraph integration.
"""

from __future__ import annotations
from typing import Literal

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from .state import AgentState
from .prompts import SYSTEM_PROMPT


def should_continue(state: AgentState) -> Literal["act", "respond"]:
    """Conditional edge: kiểm tra xem agent có muốn gọi tool không."""
    last_message = state["messages"][-1]
    
    # Nếu message cuối có tool_calls → chuyển sang act
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "act"
    
    return "respond"


def reason_node(state: AgentState) -> dict:
    """
    Node REASON: LLM suy luận, quyết định dùng tool nào.
    
    Trong production: gọi LLM thật (ChatOpenAI, ChatAnthropic, etc.)
    Trong mock mode: node này không được dùng (bypass qua mock_llm)
    """
    # ── Production code (uncomment khi có API key) ──
    # from langchain_openai import ChatOpenAI
    # from tools import all_tools
    # 
    # llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    # llm_with_tools = llm.bind_tools(all_tools)
    # 
    # messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(state["messages"])
    # response = llm_with_tools.invoke(messages)
    # 
    # return {"messages": [response]}
    
    # ── Mock mode ──
    return {"messages": [AIMessage(content="Mock reasoning — use mock_llm.py for demo")]}


def act_node(state: AgentState) -> dict:
    """
    Node ACT: Thực thi tool được chọn bởi LLM.
    
    Trong production: tự động gọi tool từ tool_calls.
    """
    # ── Production code (uncomment khi có API key) ──
    # from langchain_core.messages import ToolMessage
    # from tools import all_tools
    #
    # tool_map = {t.name: t for t in all_tools}
    # last_message = state["messages"][-1]
    # results = []
    # for tc in last_message.tool_calls:
    #     tool = tool_map[tc["name"]]
    #     result = tool.invoke(tc["args"])
    #     results.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
    # return {"messages": results}
    
    return {"messages": []}


def respond_node(state: AgentState) -> dict:
    """Node RESPOND: Tổng hợp câu trả lời cuối cùng cho user."""
    return {}


def build_graph() -> StateGraph:
    """
    Build LangGraph StateGraph cho ReAct agent.
    
    Returns:
        Compiled StateGraph sẵn sàng .invoke()
    """
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("reason", reason_node)
    graph.add_node("act", act_node)
    graph.add_node("respond", respond_node)
    
    # Set entry point
    graph.set_entry_point("reason")
    
    # Conditional edge: reason → act (nếu có tool call) hoặc respond
    graph.add_conditional_edges("reason", should_continue)
    
    # act → reason (loop lại để xem kết quả tool)
    graph.add_edge("act", "reason")
    
    # respond → END
    graph.add_edge("respond", END)
    
    return graph.compile()
