"""
NEO Agent State — Schema cho trạng thái của ReAct agent.
"""

from __future__ import annotations
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State schema cho LangGraph ReAct loop.
    
    Attributes:
        messages: Lịch sử hội thoại (auto-append nhờ add_messages reducer)
        reasoning_steps: Các bước suy luận của agent (hiển thị cho user xem)
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    reasoning_steps: list[dict]
