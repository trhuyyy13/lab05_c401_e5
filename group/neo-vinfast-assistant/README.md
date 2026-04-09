# NEO — VinFast AI Assistant 🚗

> Multi-agent framework hỗ trợ người dùng xe VinFast, xây dựng trên **LangGraph** với cơ chế **ReAct**.

## 🚀 Chạy nhanh (3 bước)

```bash
# 1. Cài dependencies
cd backend
pip install -r requirements.txt

# 2. Chạy server
python main.py

# 3. Mở browser
# → http://localhost:8000
```

## 📂 Cấu trúc thư mục

```
neo-vinfast-assistant/
├── backend/
│   ├── main.py                    ← FastAPI server (entry point)
│   ├── agent/
│   │   ├── graph.py               ← LangGraph ReAct workflow
│   │   ├── state.py               ← Agent state schema
│   │   └── prompts.py             ← System prompts
│   ├── tools/                     ← ⭐ MỖI TOOL = 1 FILE PYTHON
│   │   ├── __init__.py            ← Auto-discovery (tự load tools)
│   │   ├── vehicle_diagnostics.py ← Chẩn đoán lỗi xe
│   │   ├── charging_station.py    ← Tìm trạm sạc
│   │   ├── booking_service.py     ← Đặt lịch dịch vụ
│   │   └── weather_check.py       ← Kiểm tra thời tiết
│   ├── mock/
│   │   └── mock_llm.py            ← Mock LLM (không cần API key)
│   └── requirements.txt
├── frontend/
│   ├── index.html                 ← Mobile-style UI
│   ├── css/style.css              ← VinFast Design System
│   └── js/app.js                  ← SPA logic + Chat
└── README.md
```

## 🔧 Cách thêm tool mới (cho team member)

### Bước 1: Tạo file mới trong `backend/tools/`

```python
# backend/tools/my_new_tool.py
from langchain_core.tools import tool

@tool
def my_tool_name(query: str) -> str:
    """Mô tả ngắn gọn tool làm gì — LLM sẽ đọc mô tả này để quyết định dùng tool.
    
    Args:
        query: Tham số đầu vào
    
    Returns:
        Kết quả dạng string
    """
    # Logic xử lý
    return f"Kết quả cho: {query}"
```

### Bước 2: Restart server
```bash
python main.py
# → Tool tự động được phát hiện và load ✅
```

## 📡 API Endpoints

| Method | Path | Mô tả |
|--------|------|--------|
| `GET`  | `/` | Serve frontend |
| `GET`  | `/api/health` | Health check |
| `POST` | `/api/chat` | Chat với agent |
| `GET`  | `/api/tools` | Danh sách tools |
| `GET`  | `/api/vehicle/status` | Mock trạng thái xe |

### Ví dụ gọi API

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "xe báo lỗi E12"}'
```

## 🏗️ Kiến trúc ReAct Agent

```
User Message
    ↓
┌──────────┐
│  REASON  │ ← LLM suy luận: "cần tool nào?"
└────┬─────┘
     │ tool_call?
     ├── YES → ┌──────┐
     │         │  ACT │ ← Gọi tool (chẩn đoán, tìm trạm sạc...)
     │         └──┬───┘
     │            └──→ quay lại REASON
     │
     └── NO → ┌─────────┐
              │ RESPOND │ ← Trả lời user
              └─────────┘
```

## 👥 Phân công

| Thành viên | Tool/Module |
|------------|-------------|
| ... | `vehicle_diagnostics.py` |
| ... | `charging_station.py` |
| ... | `booking_service.py` |
| ... | `weather_check.py` |
| ... | Thêm tool mới... |

## ⚙️ Chuyển sang production (có API key)

1. Uncomment code trong `agent/graph.py`
2. Set environment variable:
   ```bash
   set OPENAI_API_KEY=sk-xxx
   ```
3. Đổi `mock_react_response` thành `graph.invoke()` trong `main.py`
