"""
NEO — VinFast AI Assistant
FastAPI Backend Server

Chạy: python main.py
Hoặc: uvicorn main:app --reload --port 8000
"""

from __future__ import annotations
import sys
from pathlib import Path

# Thêm backend/ vào path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, Request, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from mock.mock_llm import mock_react_response
from tools import all_tools
from tools.charging_station import get_nearest_charging_stations_data


# ── FastAPI App ───────────────────────────────────────────────────────
app = FastAPI(
    title="NEO — VinFast AI Assistant",
    description="Multi-agent framework hỗ trợ người dùng xe VinFast",
    version="1.0.0",
)

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
        "mode": "mock",
        "tools_loaded": len(all_tools),
    }


@app.post("/api/chat")
async def chat(payload: dict = Body(...)):
    """
    Chat endpoint — nhận message từ user, trả response từ agent.
    """
    message = payload.get("message", "")
    session_id = payload.get("session_id", "default")
    
    result = mock_react_response(message)
    
    return {
        "answer": result["answer"],
        "reasoning_steps": result["reasoning_steps"],
        "tool_used": result.get("tool_used"),
        "tool_input": result.get("tool_input", {}),
    }


@app.get("/api/tools")
async def list_tools():
    """Liệt kê tất cả tools đã load."""
    return [
        {"name": t.name, "description": t.description}
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
    print("\n🚗 NEO — VinFast AI Assistant")
    print("=" * 40)
    print(f"📦 Tools loaded: {len(all_tools)}")
    for t in all_tools:
        print(f"   • {t.name}: {t.description[:60]}...")
    print(f"\n🌐 Server: http://localhost:8000")
    print(f"📱 Frontend: http://localhost:8000")
    print(f"📄 API docs: http://localhost:8000/docs")
    print("=" * 40 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
