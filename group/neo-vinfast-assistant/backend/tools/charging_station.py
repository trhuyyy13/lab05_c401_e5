"""
Tool: Tìm trạm sạc VinFast gần nhất
Mô tả: Tra cứu danh sách trạm sạc theo vị trí, trạng thái trống/đầy, loại sạc.

Author: [Tên thành viên]
"""

from langchain_core.tools import tool


# ── Mock database trạm sạc ───────────────────────────────────────────
CHARGING_STATIONS = [
    {
        "name": "VinFast Charging — Vincom Bà Triệu",
        "address": "191 Bà Triệu, Hai Bà Trưng, Hà Nội",
        "distance_km": 1.2,
        "available": 3,
        "total": 5,
        "type": "DC 60kW",
        "status": "open",
        "charge_time_min": 45,
    },
    {
        "name": "VinFast Charging — Times City",
        "address": "458 Minh Khai, Hai Bà Trưng, Hà Nội",
        "distance_km": 2.8,
        "available": 2,
        "total": 4,
        "type": "DC 150kW",
        "status": "open",
        "charge_time_min": 25,
    },
    {
        "name": "VinFast Charging — Royal City",
        "address": "72A Nguyễn Trãi, Thanh Xuân, Hà Nội",
        "distance_km": 4.1,
        "available": 1,
        "total": 6,
        "type": "DC 60kW",
        "status": "open",
        "charge_time_min": 45,
    },
    {
        "name": "VinFast Charging — Vinhomes Riverside",
        "address": "KĐT Vinhomes Riverside, Long Biên, Hà Nội",
        "distance_km": 6.5,
        "available": 4,
        "total": 8,
        "type": "DC 150kW",
        "status": "open",
        "charge_time_min": 25,
    },
    {
        "name": "VinFast Charging — Aeon Mall Long Biên",
        "address": "27 Cổ Linh, Long Biên, Hà Nội",
        "distance_km": 7.2,
        "available": 0,
        "total": 4,
        "type": "DC 60kW",
        "status": "full",
        "charge_time_min": 45,
    },
]


@tool
def find_charging_station(location: str) -> str:
    """Tìm trạm sạc VinFast gần nhất theo vị trí.
    
    Args:
        location: Vị trí hiện tại hoặc khu vực muốn tìm (VD: "Hai Bà Trưng", "Hà Nội")
    
    Returns:
        Danh sách trạm sạc gần nhất kèm trạng thái, khoảng cách, loại sạc.
    """
    # Filter trạm đang mở và còn trống
    available_stations = [s for s in CHARGING_STATIONS if s["available"] > 0]
    
    results = []
    for i, station in enumerate(available_stations[:3], 1):
        status_emoji = "🟢" if station["available"] >= 2 else "🟡"
        results.append(
            f"{i}. {station['name']}\n"
            f"   📍 {station['address']} — {station['distance_km']} km\n"
            f"   {status_emoji} Còn trống {station['available']}/{station['total']} trụ | "
            f"Loại: {station['type']} | ⏱️ ~{station['charge_time_min']} phút"
        )
    
    return "⚡ Trạm sạc gần nhất:\n\n" + "\n\n".join(results)
