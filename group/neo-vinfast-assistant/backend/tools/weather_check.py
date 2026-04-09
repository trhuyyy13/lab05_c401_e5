"""
Tool: Kiểm tra thời tiết
Mô tả: Lấy thông tin thời tiết hiện tại để tư vấn lái xe an toàn.

Author: [Tên thành viên]
"""

from langchain_core.tools import tool
import random


# ── Mock weather data ─────────────────────────────────────────────────
WEATHER_DATA = {
    "hà nội": {
        "city": "Hà Nội",
        "temp": 28,
        "feels_like": 32,
        "condition": "Nắng nhẹ, có mây",
        "humidity": 65,
        "wind_speed": 12,
        "wind_dir": "Đông Nam",
        "uv_index": 6,
        "rain_chance": 20,
    },
    "hồ chí minh": {
        "city": "TP. Hồ Chí Minh",
        "temp": 33,
        "feels_like": 38,
        "condition": "Nắng nóng, ít mây",
        "humidity": 55,
        "wind_speed": 8,
        "wind_dir": "Tây Nam",
        "uv_index": 9,
        "rain_chance": 40,
    },
    "đà nẵng": {
        "city": "Đà Nẵng",
        "temp": 30,
        "feels_like": 34,
        "condition": "Mây rải rác",
        "humidity": 70,
        "wind_speed": 15,
        "wind_dir": "Đông",
        "uv_index": 7,
        "rain_chance": 30,
    },
}

DRIVING_TIPS = {
    "hot": "☀️ Trời nóng — nên bật điều hòa 24-25°C để tiết kiệm pin. Kiểm tra áp suất lốp.",
    "rain": "🌧️ Có khả năng mưa — giảm tốc độ, giữ khoảng cách. Bật gạt mưa tự động.",
    "normal": "✅ Điều kiện lái xe tốt. Chúc bạn có chuyến đi an toàn!",
    "wind": "💨 Gió mạnh — cẩn thận khi chuyển làn, đặc biệt trên cầu/đường cao tốc.",
}


@tool
def check_weather(location: str) -> str:
    """Kiểm tra thời tiết hiện tại theo vị trí để tư vấn lái xe an toàn.
    
    Args:
        location: Thành phố hoặc khu vực (VD: "Hà Nội", "Hồ Chí Minh", "Đà Nẵng")
    
    Returns:
        Thông tin thời tiết kèm lời khuyên lái xe.
    """
    location_lower = location.lower()
    
    # Tìm weather data
    weather = None
    for key, data in WEATHER_DATA.items():
        if key in location_lower:
            weather = data
            break
    
    if not weather:
        weather = WEATHER_DATA["hà nội"]
    
    # Chọn driving tip
    if weather["temp"] >= 35:
        tip = DRIVING_TIPS["hot"]
    elif weather["rain_chance"] >= 50:
        tip = DRIVING_TIPS["rain"]
    elif weather["wind_speed"] >= 20:
        tip = DRIVING_TIPS["wind"]
    else:
        tip = DRIVING_TIPS["normal"]
    
    return (
        f"🌤️ Thời tiết — {weather['city']}:\n\n"
        f"🌡️ Nhiệt độ: {weather['temp']}°C (Cảm giác: {weather['feels_like']}°C)\n"
        f"☁️ Trời: {weather['condition']}\n"
        f"💧 Độ ẩm: {weather['humidity']}%\n"
        f"💨 Gió: {weather['wind_speed']} km/h — {weather['wind_dir']}\n"
        f"🌧️ Khả năng mưa: {weather['rain_chance']}%\n\n"
        f"🚗 Lưu ý lái xe: {tip}"
    )
