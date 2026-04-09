"""
NEO — VinFast AI Assistant
FastAPI Backend Server

Chạy: python main.py
Hoặc: uvicorn main:app --reload --port 8000
"""

from __future__ import annotations
import os
import sys
from pathlib import Path

# Thêm backend/ vào path
sys.path.insert(0, str(Path(__file__).parent))

import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from agent.graph import build_graph
from tools import all_tools
from tools.charging_station import get_nearest_charging_stations_data
from langchain_core.messages import HumanMessage


# ── FastAPI App ───────────────────────────────────────────────────────
app = FastAPI(
    title="NEO — VinFast AI Assistant",
    description="Multi-agent framework hỗ trợ người dùng xe VinFast",
    version="1.0.0",
)

logger = logging.getLogger("neo.agent")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# CORS — cho phép frontend gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/css", StaticFiles(directory=str(frontend_dir / "css")), name="css")
    app.mount("/js", StaticFiles(directory=str(frontend_dir / "js")), name="js")
    app.mount("/assets", StaticFiles(directory=str(frontend_dir / "assets")), name="assets")


# ── Pydantic Models ──────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    answer: str
    reasoning_steps: list[dict]
    tool_used: str | None = None
    tool_input: dict = {}


class ToolInfo(BaseModel):
    name: str
    description: str


class ChargingStationSearchRequest(BaseModel):
    location: str = "VinUni"


# ── API Endpoints ────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve trang chủ frontend."""
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return HTMLResponse("<h1>NEO — VinFast AI Assistant</h1><p>Frontend not found.</p>")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "NEO — VinFast AI Assistant",
        "version": "1.0.0",
        "mode": "openai",
        "tools_loaded": len(all_tools),
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint — nhận message từ user, trả response từ agent.
    
    Hiện tại dùng Mock LLM. Khi có API key:
    1. Import build_graph từ agent.graph
    2. Thay mock_react_response bằng graph.invoke()
    """
    if not os.getenv("OPENAI_API_KEY"):
        return ChatResponse(
            answer="Chua thiet lap OPENAI_API_KEY. Vui long cau hinh de su dung chatbot.",
            reasoning_steps=[],
            tool_used=None,
            tool_input={},
        )

    graph = build_graph()
    result = graph.invoke({
        "messages": [HumanMessage(content=request.message)],
        "reasoning_steps": [],
    })

    messages = result.get("messages", [])
    answer = ""
    for message in reversed(messages):
        if getattr(message, "content", None):
            answer = message.content
            break

    reasoning_steps = result.get("reasoning_steps", [])
    if reasoning_steps:
        for step in reasoning_steps:
            if isinstance(step, dict):
                logger.info("reasoning step=%s content=%s", step.get("step"), step.get("content"))
    tool_used = None
    tool_input = {}
    if reasoning_steps:
        last_step = reasoning_steps[-1]
        if isinstance(last_step, dict) and last_step.get("step") == "tool":
            tool_used = "tool"
            tool_input = {"detail": last_step.get("content", "")}

    return ChatResponse(
        answer=answer or "Xin loi, hien tai toi chua co phan hoi.",
        reasoning_steps=reasoning_steps,
        tool_used=tool_used,
        tool_input=tool_input,
    )


@app.get("/api/tools", response_model=list[ToolInfo])
async def list_tools():
    """Liệt kê tất cả tools đã load."""
    return [
        ToolInfo(name=t.name, description=t.description)
        for t in all_tools
    ]


@app.post("/api/charging-stations")
async def search_charging_stations(request: ChargingStationSearchRequest):
    """Tìm 3 trạm sạc gần nhất từ địa chỉ nhập bằng văn bản."""
    return get_nearest_charging_stations_data(request.location)


@app.get("/api/vehicle/status")
async def vehicle_status():
    """Mock: Trạng thái xe hiện tại."""
    return {
        "model": "VinFast VF 8 Plus",
        "plate": "30A-123.45",
        "battery_percent": 15,
        "range_km": 42,
        "odometer_km": 15680,
        "next_service_km": 20000,
        "tire_pressure": {"fl": 2.3, "fr": 2.3, "rl": 2.4, "rr": 2.4},
        "warnings": [
            {"code": "W03", "message": "Sắp đến hạn bảo dưỡng", "severity": "low"},
            {"code": "W15", "message": "Pin sắp hết, cần sạc sớm", "severity": "medium"},
        ],
    }


# ── Run ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\nNEO - VinFast AI Assistant")
    print("=" * 40)
    print(f"Tools loaded: {len(all_tools)}")
    for t in all_tools:
        print(f"   - {t.name}: {t.description[:60]}...")
    print(f"\nServer: http://localhost:8000")
    print(f"Frontend: http://localhost:8000")
    print(f"API docs: http://localhost:8000/docs")
    print("=" * 40 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
