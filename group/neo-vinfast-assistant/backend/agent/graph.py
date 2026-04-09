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
import json
import logging
import os
from pathlib import Path

from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from .state import AgentState
from .prompts import SYSTEM_PROMPT
from tools import all_tools


LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "tool_calls.log"

DEFAULT_LOCATION = "VinUni, Ha Noi"

logger = logging.getLogger("neo.tools")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


def _get_llm() -> ChatOpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    return ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)


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
    llm = _get_llm()
    llm_with_tools = llm.bind_tools(all_tools)

    messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(state["messages"])
    response = llm_with_tools.invoke(messages)

    return {"messages": [response]}


def act_node(state: AgentState) -> dict:
    """
    Node ACT: Thực thi tool được chọn bởi LLM.
    
    Trong production: tự động gọi tool từ tool_calls.
    """
    tool_map = {t.name: t for t in all_tools}
    last_message = state["messages"][-1]
    results = []
    steps = list(state.get("reasoning_steps", []))

    for tc in last_message.tool_calls:
        tool_name = tc.get("name")
        tool_args = dict(tc.get("args", {}) or {})
        if tool_name == "find_charging_station":
            if not str(tool_args.get("user_query", "")).strip():
                tool_args["user_query"] = DEFAULT_LOCATION
        if tool_name == "find_nearest_service_center":
            if not str(tool_args.get("location", "")).strip():
                tool_args["location"] = DEFAULT_LOCATION
        tool = tool_map.get(tool_name)

        if tool is None:
            tool_result = f"Tool not found: {tool_name}"
        else:
            try:
                tool_result = tool.invoke(tool_args)
            except Exception as exc:
                tool_result = f"Tool error: {exc}"

        results.append(ToolMessage(content=str(tool_result), tool_call_id=tc.get("id")))

        args_json = json.dumps(tool_args, ensure_ascii=True)
        result_text = str(tool_result)
        if len(result_text) > 500:
            result_text = result_text[:500] + "..."

        logger.info("tool_call name=%s args=%s result=%s", tool_name, args_json, result_text)
        steps.append({
            "step": "tool",
            "content": f"{tool_name}({args_json})",
        })

    return {"messages": results, "reasoning_steps": steps}


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
