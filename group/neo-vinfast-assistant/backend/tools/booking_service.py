"""
Tool: Đặt lịch dịch vụ VinFast Service
Mô tả: Hỗ trợ đặt lịch bảo dưỡng, sửa chữa tại trung tâm dịch vụ VinFast.

Author: [Tên thành viên]
"""

from langchain_core.tools import tool
from datetime import datetime, timedelta


# ── Mock service centers ──────────────────────────────────────────────
SERVICE_CENTERS = [
    {
        "name": "VinFast Service — Long Biên",
        "address": "KĐT Vinhomes Riverside, Long Biên, Hà Nội",
        "distance_km": 5.2,
        "available_slots": ["09:00", "10:30", "14:00", "15:30"],
    },
    {
        "name": "VinFast Service — Thanh Xuân",
        "address": "12 Khuất Duy Tiến, Thanh Xuân, Hà Nội",
        "distance_km": 3.8,
        "available_slots": ["08:30", "11:00", "14:30"],
    },
    {
        "name": "VinFast Service — Cầu Giấy",
        "address": "168 Trần Duy Hưng, Cầu Giấy, Hà Nội",
        "distance_km": 6.1,
        "available_slots": ["09:30", "13:00", "16:00"],
    },
]

SERVICE_TYPES = {
    "bảo dưỡng": {"name": "Bảo dưỡng định kỳ", "duration": "~2 giờ", "price": "1.500.000đ - 3.000.000đ"},
    "sửa chữa": {"name": "Sửa chữa", "duration": "~3-5 giờ", "price": "Tuỳ hạng mục"},
    "kiểm tra": {"name": "Kiểm tra tổng quát", "duration": "~1 giờ", "price": "500.000đ"},
    "lốp": {"name": "Thay/sửa lốp", "duration": "~1 giờ", "price": "800.000đ - 2.000.000đ/lốp"},
    "pin": {"name": "Kiểm tra hệ thống pin", "duration": "~2 giờ", "price": "Miễn phí (trong bảo hành)"},
}


@tool
def book_service(service_type: str) -> str:
    """Đặt lịch dịch vụ tại trung tâm VinFast Service.
    
    Args:
        service_type: Loại dịch vụ cần đặt (VD: "bảo dưỡng", "sửa chữa", "kiểm tra", "lốp", "pin")
    
    Returns:
        Danh sách trung tâm dịch vụ gần nhất, khung giờ trống, và thông tin dịch vụ.
    """
    # Xác định loại dịch vụ
    service_lower = service_type.lower()
    matched_service = None
    for key, info in SERVICE_TYPES.items():
        if key in service_lower:
            matched_service = info
            break
    
    if not matched_service:
        matched_service = SERVICE_TYPES["bảo dưỡng"]
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")
    
    # Chọn trung tâm gần nhất
    center = SERVICE_CENTERS[1]  # Thanh Xuân — gần nhất
    slots = " | ".join(center["available_slots"])
    
    return (
        f"📅 Đặt lịch dịch vụ:\n\n"
        f"Dịch vụ: {matched_service['name']}\n"
        f"Thời gian ước tính: {matched_service['duration']}\n"
        f"Chi phí dự kiến: {matched_service['price']}\n\n"
        f"Trung tâm gần nhất:\n"
        f"🔧 {center['name']}\n"
        f"📍 {center['address']} — {center['distance_km']} km\n"
        f"📆 Ngày: {tomorrow}\n"
        f"⏰ Khung giờ trống: {slots}\n\n"
        f"Vui lòng xác nhận khung giờ để hoàn tất đặt lịch."
    )


@tool
def find_nearest_service_center(location: str = "VinUni") -> str:
    """Tìm gara VinFast gần nhất dựa trên vị trí (mock tại VinUni).

    Args:
        location: Vị trí người dùng (mặc định VinUni)

    Returns:
        Thông tin gara gần nhất và các lựa chọn thay thế.
    """
    sorted_centers = sorted(SERVICE_CENTERS, key=lambda item: item["distance_km"])
    nearest = sorted_centers[0]
    alternatives = sorted_centers[1:3]

    lines = [
        "🏁 Gara gần nhất:",
        f"- Vị trí người dùng (mock): {location}",
        f"- Gara đề xuất: {nearest['name']}",
        f"  📍 {nearest['address']} — {nearest['distance_km']} km",
        f"  ⏰ Slot trống: {' | '.join(nearest['available_slots'])}",
        "",
        "Các gara thay thế:",
    ]

    for center in alternatives:
        lines.append(f"- {center['name']} — {center['distance_km']} km")
        lines.append(f"  📍 {center['address']}")
        lines.append(f"  ⏰ Slot trống: {' | '.join(center['available_slots'])}")

    return "\n".join(lines)
