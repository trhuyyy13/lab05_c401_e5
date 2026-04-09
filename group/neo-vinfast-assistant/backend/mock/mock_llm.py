"""
Mock LLM — Giả lập LLM response cho demo local không cần API key.

Cơ chế: keyword matching trên input → trả response có cấu trúc ReAct.
Khi có API key thật, thay MockLLM bằng ChatOpenAI hoặc model khác.
"""

from __future__ import annotations
import re
import json
from langchain_core.messages import AIMessage, ToolMessage


# ── Bảng keyword → response ──────────────────────────────────────────
MOCK_RESPONSES = {
    # Lỗi xe / chẩn đoán
    "lỗi|error|báo lỗi|mã lỗi|e12|e45|w03|cảnh báo|warning": {
        "thought": "Người dùng đang gặp vấn đề với xe, cần chẩn đoán lỗi. Tôi sẽ sử dụng tool vehicle_diagnostics để tra cứu.",
        "tool": "diagnose_vehicle",
        "tool_input": {"symptom": ""},  # sẽ fill từ user input
        "fallback_answer": (
            "🔍 **Phân tích sự cố:**\n\n"
            "Dựa trên mô tả của bạn, hệ thống nhận diện đây có thể là **lỗi hệ thống pin cao áp** (mức độ: ⚠️ Trung bình).\n\n"
            "**Khuyến nghị:**\n"
            "1. 🅿️ Dừng xe ở nơi an toàn\n"
            "2. 🔌 Tìm trạm sạc gần nhất để kiểm tra\n"
            "3. 📞 Liên hệ hotline VinFast: **1900 23 23 89**\n\n"
            "Bạn muốn tôi tìm trạm sạc gần nhất không?"
        ),
    },
    # Sạc / pin / trạm sạc
    "sạc|pin|battery|charge|trạm sạc|hết pin|sắp hết pin|charging": {
        "thought": "Người dùng cần thông tin về sạc/pin. Tôi sẽ tìm trạm sạc gần nhất.",
        "tool": "find_charging_station",
        "tool_input": {"location": "Hà Nội"},
        "fallback_answer": (
            "⚡ **Trạm sạc gần bạn:**\n\n"
            "1. **VinFast Charging — Vincom Bà Triệu**\n"
            "   📍 191 Bà Triệu, Hai Bà Trưng — 1.2 km\n"
            "   🟢 Còn trống 3/5 trụ | Loại: DC 60kW\n\n"
            "2. **VinFast Charging — Times City**\n"
            "   📍 458 Minh Khai, Hai Bà Trưng — 2.8 km\n"
            "   🟢 Còn trống 2/4 trụ | Loại: DC 150kW\n\n"
            "3. **VinFast Charging — Royal City**\n"
            "   📍 72A Nguyễn Trãi, Thanh Xuân — 4.1 km\n"
            "   🟡 Còn trống 1/6 trụ | Loại: DC 60kW\n\n"
            "Bạn muốn điều hướng đến trạm nào?"
        ),
    },
    # Đặt lịch / bảo dưỡng / dịch vụ
    "đặt lịch|bảo dưỡng|dịch vụ|booking|sửa|service|lịch hẹn|bảo hành": {
        "thought": "Người dùng muốn đặt lịch dịch vụ. Tôi sẽ hỗ trợ đặt lịch.",
        "tool": "book_service",
        "tool_input": {"service_type": "bảo dưỡng định kỳ"},
        "fallback_answer": (
            "📅 **Đặt lịch dịch vụ:**\n\n"
            "Tôi có thể giúp bạn đặt lịch tại các trung tâm VinFast Service:\n\n"
            "**Gần bạn nhất:**\n"
            "🔧 VinFast Service — Long Biên\n"
            "📍 KĐT Vinhomes Riverside, Long Biên\n"
            "⏰ Khung giờ trống: 9:00, 10:30, 14:00, 15:30\n\n"
            "**Thông tin cần xác nhận:**\n"
            "- Loại dịch vụ: Bảo dưỡng định kỳ\n"
            "- Xe: VF 8 Plus\n"
            "- Thời gian dự kiến: ~2 giờ\n\n"
            "Bạn muốn chọn khung giờ nào?"
        ),
    },
    # Thời tiết
    "thời tiết|weather|mưa|nắng|nhiệt độ|temperature": {
        "thought": "Người dùng hỏi về thời tiết. Tôi sẽ kiểm tra thời tiết để tư vấn lái xe.",
        "tool": "check_weather",
        "tool_input": {"location": "Hà Nội"},
        "fallback_answer": (
            "🌤️ **Thời tiết hiện tại — Hà Nội:**\n\n"
            "- Nhiệt độ: 28°C (Cảm giác: 32°C)\n"
            "- Trời: Nắng nhẹ, có mây\n"
            "- Độ ẩm: 65%\n"
            "- Gió: 12 km/h Đông Nam\n\n"
            "💡 **Lưu ý lái xe:** Điều kiện tốt cho di chuyển. "
            "Nên bật điều hòa ở mức 24-25°C để tiết kiệm pin."
        ),
    },
    # Cứu hộ / khẩn cấp
    "cứu hộ|khẩn cấp|emergency|kẹt|hỏng|tai nạn|va chạm": {
        "thought": "Đây là tình huống khẩn cấp! Cần ưu tiên an toàn cho người dùng.",
        "tool": None,
        "tool_input": {},
        "fallback_answer": (
            "🚨 **TÌNH HUỐNG KHẨN CẤP**\n\n"
            "**Bước 1:** Đảm bảo an toàn cho bạn và hành khách\n"
            "**Bước 2:** Bật đèn cảnh báo nguy hiểm\n"
            "**Bước 3:** Đặt tam giác phản quang (nếu có)\n\n"
            "📞 **Hotline cứu hộ VinFast:** **1900 23 23 89**\n"
            "📞 **Cấp cứu:** **115**\n"
            "📞 **Công an:** **113**\n\n"
            "⚠️ *Tình huống này cần hỗ trợ trực tiếp từ chuyên gia. "
            "Tôi đang chuyển yêu cầu đến đội ngũ cứu hộ VinFast.*"
        ),
    },
}

# Default response khi không match keyword nào
DEFAULT_RESPONSE = (
    "Xin chào! Tôi là **NEO** — trợ lý AI của VinFast 🚗\n\n"
    "Tôi có thể giúp bạn:\n"
    "- 🔍 **Chẩn đoán sự cố** — mô tả triệu chứng hoặc nhập mã lỗi\n"
    "- ⚡ **Tìm trạm sạc** — trạm gần nhất, trạng thái trống\n"
    "- 📅 **Đặt lịch dịch vụ** — bảo dưỡng, sửa chữa\n"
    "- 🌤️ **Kiểm tra thời tiết** — tư vấn lái xe an toàn\n"
    "- 🚨 **Hỗ trợ khẩn cấp** — cứu hộ, tai nạn\n\n"
    "Hãy cho tôi biết bạn cần gì nhé!"
)


def mock_react_response(user_message: str) -> dict:
    """
    Simulate a ReAct agent response based on keyword matching.
    
    Returns:
        dict with keys: thought, tool_used, tool_input, tool_result, answer, reasoning_steps
    """
    user_lower = user_message.lower()
    
    matched = None
    for pattern, response_data in MOCK_RESPONSES.items():
        if re.search(pattern, user_lower):
            matched = response_data
            break
    
    if not matched:
        return {
            "thought": "Người dùng chào hỏi hoặc hỏi chung. Trả lời giới thiệu chức năng.",
            "tool_used": None,
            "tool_input": {},
            "tool_result": None,
            "answer": DEFAULT_RESPONSE,
            "reasoning_steps": [
                {"step": "Thought", "content": "Người dùng chào hỏi hoặc hỏi chung. Không cần sử dụng tool."},
                {"step": "Answer", "content": "Giới thiệu các chức năng có sẵn."},
            ],
        }
    
    # Fill tool_input với user message gốc
    tool_input = matched["tool_input"].copy()
    if "symptom" in tool_input:
        tool_input["symptom"] = user_message
    
    reasoning_steps = [
        {"step": "Thought", "content": matched["thought"]},
    ]
    
    if matched["tool"]:
        reasoning_steps.append({"step": "Action", "content": f"Gọi tool: {matched['tool']}({json.dumps(tool_input, ensure_ascii=False)})"})
        reasoning_steps.append({"step": "Observation", "content": "Đã nhận kết quả từ tool."})
    
    reasoning_steps.append({"step": "Answer", "content": "Tổng hợp câu trả lời cho người dùng."})
    
    return {
        "thought": matched["thought"],
        "tool_used": matched["tool"],
        "tool_input": tool_input,
        "tool_result": "Mock result — dữ liệu demo",
        "answer": matched["fallback_answer"],
        "reasoning_steps": reasoning_steps,
    }
