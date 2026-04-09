"""
Tool: Tim tram sac VinFast gan nhat
Mo ta: Tra cuu danh sach tram sac dua tren vi tri nguoi dung.

Author: [Luong Tien Dung]
"""

from __future__ import annotations

import json
import math
import os
from typing import Any

from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

try:
    from langchain_openai import ChatOpenAI
except Exception:
    ChatOpenAI = None


llm = None
if OPENAI_API_KEY and ChatOpenAI is not None:
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=OPENAI_API_KEY,
        )
    except Exception:
        llm = None


def extract_user_location(user_query: str) -> dict[str, Any]:
    """Tra ve vi tri nguoi dung kem toa do ro rang."""
    if llm is not None:
        try:
            prompt = (
                "Ban la he thong xac dinh vi tri cho tro ly xe dien VinFast.\n"
                "Tu cau nguoi dung, hay suy ra vi tri hop ly va tra ve JSON hop le "
                'voi dung 3 key: "resolved_location", "latitude", "longitude".\n'
                "Khong giai thich, khong markdown.\n\n"
                f"Input: {user_query}"
            )
            payload = json.loads(llm.invoke(prompt).content.strip())
            return {
                "resolved_location": str(payload["resolved_location"]).strip(),
                "latitude": float(payload["latitude"]),
                "longitude": float(payload["longitude"]),
            }
        except Exception:
            pass

    query_lower = user_query.lower()
    for keyword, location in MOCK_USER_LOCATIONS.items():
        if keyword in query_lower:
            return location

    return DEFAULT_USER_LOCATION


def calculate_distance_km(
    user_latitude: float,
    user_longitude: float,
    station_latitude: float,
    station_longitude: float,
) -> float:
    """Tinh khoang cach giua user va tram sac theo km."""
    radius_km = 6371.0
    d_lat = math.radians(station_latitude - user_latitude)
    d_lon = math.radians(station_longitude - user_longitude)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(user_latitude))
        * math.cos(math.radians(station_latitude))
        * math.sin(d_lon / 2) ** 2
    )
    return round(radius_km * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))), 2)


def get_nearest_charging_stations_data(user_query: str) -> dict[str, Any]:
    """Wrapper gon cho frontend/API."""
    user_location = extract_user_location(user_query)
    stations = []

    for station in CHARGING_STATIONS:
        station_data = station.copy()
        station_data["distance_km"] = calculate_distance_km(
            user_location["latitude"],
            user_location["longitude"],
            station["latitude"],
            station["longitude"],
        )
        stations.append(station_data)

    stations.sort(key=lambda item: (item["available"] <= 0, item["distance_km"]))
    return {
        "query": user_query,
        "resolved_location": user_location["resolved_location"],
        "latitude": user_location["latitude"],
        "longitude": user_location["longitude"],
        "stations": stations[:3],
    }


@tool
def find_charging_station(user_query: str) -> str:
    """Tìm 3 trạm sạc VinFast gần nhất từ câu hỏi tự nhiên của người dùng."""
    result = get_nearest_charging_stations_data(user_query)
    stations = result["stations"][:3]

    if not stations:
        return "Không tìm thấy trạm sạc nào phù hợp."

    lines = [
        "Trạm sạc gần nhất:",
        f"- Vị trí yêu cầu: {result['resolved_location']}",
        f"- Tọa độ người dùng: ({result['latitude']}, {result['longitude']})",
    ]

    for index, station in enumerate(stations, 1):
        lines.append(f"{index}. {station['name']} - {station['distance_km']} km")
        lines.append(f"   Địa chỉ: {station['address']}")
        lines.append(
            f"   Trạng thái: {station['status']} | Còn trống {station['available']}/{station['total']} trụ"
        )
        lines.append(
            f"   Loại sạc: {station['type']} | Thời gian ước tính: ~{station['charge_time_min']} phút"
        )

    return "\n".join(lines)


DEFAULT_USER_LOCATION = {
    "resolved_location": "VinUniversity, Vinhomes Ocean Park, Gia Lâm, Hà Nội",
    "latitude": 21.00031,
    "longitude": 105.93967,
}


MOCK_USER_LOCATIONS = {
    "vinuni": DEFAULT_USER_LOCATION,
    "vin uni": DEFAULT_USER_LOCATION,
    "vinuniversity": DEFAULT_USER_LOCATION,
    "ocean park": {
        "resolved_location": "Vinhomes Ocean Park, Gia Lâm, Hà Nội",
        "latitude": 20.99892,
        "longitude": 105.93688,
    },
    "gia lâm": {
        "resolved_location": "Gia Lâm, Hà Nội",
        "latitude": 21.0288,
        "longitude": 105.95821,
    },
    "gia lam": {
        "resolved_location": "Gia Lâm, Hà Nội",
        "latitude": 21.0288,
        "longitude": 105.95821,
    },
    "hoàn kiếm": {
        "resolved_location": "Hoàn Kiếm, Hà Nội",
        "latitude": 21.02817,
        "longitude": 105.85227,
    },
    "hoan kiem": {
        "resolved_location": "Hoàn Kiếm, Hà Nội",
        "latitude": 21.02817,
        "longitude": 105.85227,
    },
    "đà nẵng": {
        "resolved_location": "Đà Nẵng",
        "latitude": 16.05441,
        "longitude": 108.20217,
    },
    "da nang": {
        "resolved_location": "Đà Nẵng",
        "latitude": 16.05441,
        "longitude": 108.20217,
    },
    "quận 1": {
        "resolved_location": "Quận 1, TP. Hồ Chí Minh",
        "latitude": 10.77689,
        "longitude": 106.70081,
    },
    "quan 1": {
        "resolved_location": "Quận 1, TP. Hồ Chí Minh",
        "latitude": 10.77689,
        "longitude": 106.70081,
    },
}


CHARGING_STATIONS = [
    {
        "id": "vinuni-main-gate",
        "name": "VinFast Charging - VinUni Main Gate",
        "address": "Cổng chính VinUniversity, Vinhomes Ocean Park, Gia Lâm, Hà Nội",
        "latitude": 20.99962,
        "longitude": 105.93984,
        "available": 5,
        "total": 8,
        "type": "DC 150kW",
        "status": "open",
        "charge_time_min": 25,
    },
    {
        "id": "vinuni-parking-a",
        "name": "VinFast Charging - VinUni Parking A",
        "address": "Bãi đỗ xe A, VinUniversity, Vinhomes Ocean Park, Gia Lâm, Hà Nội",
        "latitude": 21.00091,
        "longitude": 105.93831,
        "available": 4,
        "total": 6,
        "type": "DC 60kW",
        "status": "open",
        "charge_time_min": 45,
    },
    {
        "id": "vinuni-dormitory",
        "name": "VinFast Charging - VinUni Dormitory",
        "address": "Khu ký túc xá VinUniversity, Vinhomes Ocean Park, Gia Lâm, Hà Nội",
        "latitude": 21.00234,
        "longitude": 105.94112,
        "available": 2,
        "total": 4,
        "type": "DC 60kW",
        "status": "open",
        "charge_time_min": 45,
    },
    {
        "id": "vinuni-sports-complex",
        "name": "VinFast Charging - VinUni Sports Complex",
        "address": "Khu thể thao VinUniversity, Vinhomes Ocean Park, Gia Lâm, Hà Nội",
        "latitude": 20.99874,
        "longitude": 105.94208,
        "available": 3,
        "total": 5,
        "type": "DC 60kW",
        "status": "open",
        "charge_time_min": 45,
    },
    {
        "id": "ocean-park-gateway",
        "name": "VinFast Charging - Ocean Park Gateway",
        "address": "Cổng vào Vinhomes Ocean Park, Gia Lâm, Hà Nội",
        "latitude": 20.99583,
        "longitude": 105.93468,
        "available": 1,
        "total": 4,
        "type": "DC 60kW",
        "status": "open",
        "charge_time_min": 45,
    },
]


if __name__ == "__main__":
    result = find_charging_station.invoke({"user_query": "Xe tôi sắp hết pin ở VinUni"})
    print(result)
