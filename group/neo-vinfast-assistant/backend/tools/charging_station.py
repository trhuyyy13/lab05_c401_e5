"""
Tool: Tìm trạm sạc VinFast gần nhất
Mô tả: Tra cứu danh sách trạm sạc dựa trên vị trí người dùng, trạng thái còn trụ và loại sạc.

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

KNOWN_USER_LOCATIONS = {
    "vinuni": {
        "label": "VinUniversity, Vinhomes Ocean Park, Gia Lâm, Hà Nội",
        "latitude": 21.00031,
        "longitude": 105.93967,
    },
    "vin uni": {
        "label": "VinUniversity, Vinhomes Ocean Park, Gia Lâm, Hà Nội",
        "latitude": 21.00031,
        "longitude": 105.93967,
    },
    "vinuniversity": {
        "label": "VinUniversity, Vinhomes Ocean Park, Gia Lâm, Hà Nội",
        "latitude": 21.00031,
        "longitude": 105.93967,
    },
    "ocean park": {
        "label": "Vinhomes Ocean Park, Gia Lâm, Hà Nội",
        "latitude": 20.99892,
        "longitude": 105.93688,
    },
    "gia lâm": {
        "label": "Gia Lâm, Hà Nội",
        "latitude": 21.0288,
        "longitude": 105.95821,
    },
    "gia lam": {
        "label": "Gia Lâm, Hà Nội",
        "latitude": 21.0288,
        "longitude": 105.95821,
    },
}

DEFAULT_LOCATION_TEXT = "VinUniversity, Vinhomes Ocean Park, Gia Lâm, Hà Nội"
DEFAULT_COORDINATES = {
    "label": DEFAULT_LOCATION_TEXT,
    "latitude": 21.00031,
    "longitude": 105.93967,
}


def _log(message: str, payload: Any | None = None) -> None:
    if payload is None:
        print(f"[charging_station] {message}")
        return

    print(
        f"[charging_station] {message}: "
        f"{json.dumps(payload, ensure_ascii=False, default=str)}"
    )


def _extract_location_from_query(user_query: str) -> str:
    """Trích xuất địa điểm từ câu người dùng."""
    _log("raw_user_query", {"user_query": user_query})

    if llm is not None:
        try:
            prompt = (
                "Bạn là trợ lý AI hỗ trợ xe điện VinFast.\n"
                "Nhiệm vụ: trích xuất địa điểm hoặc khu vực từ câu người dùng.\n\n"
                "Quy tắc:\n"
                "1. Nếu câu có địa chỉ/khu vực rõ ràng, trả về đúng địa điểm đó.\n"
                "2. Nếu địa điểm nằm ngoài dữ liệu nội bộ, vẫn trả về địa điểm hợp lý nhất mà bạn suy ra được.\n"
                "3. Chỉ trả về duy nhất tên địa điểm hoặc khu vực, không giải thích.\n\n"
                f"Input: {user_query}"
            )
            extracted_location = llm.invoke(prompt).content.strip()
            _log(
                "location_extracted_by_llm",
                {"user_query": user_query, "location_text": extracted_location},
            )
            return extracted_location
        except Exception:
            pass

    fallback_location = user_query.strip() or DEFAULT_LOCATION_TEXT
    _log(
        "location_extracted_by_fallback",
        {"user_query": user_query, "location_text": fallback_location},
    )
    return fallback_location


def _lookup_known_location(location_text: str) -> dict[str, Any] | None:
    normalized = location_text.lower().strip()
    for keyword, location in KNOWN_USER_LOCATIONS.items():
        if keyword in normalized:
            return location
    return None


def _fallback_geocode(location_text: str) -> dict[str, Any]:
    """Fallback nội bộ: dùng vị trí mặc định VinUni hoặc vị trí gần VinUni đã biết."""
    known_location = _lookup_known_location(location_text)
    if known_location is not None:
        result = {
            "input": location_text,
            "resolved_location": known_location["label"],
            "latitude": known_location["latitude"],
            "longitude": known_location["longitude"],
            "source": "known_location_fallback",
        }
        _log("fallback_geocode_result", result)
        return result

    result = {
        "input": location_text,
        "resolved_location": DEFAULT_COORDINATES["label"],
        "latitude": DEFAULT_COORDINATES["latitude"],
        "longitude": DEFAULT_COORDINATES["longitude"],
        "source": "vinuni_default_fallback",
    }
    _log("fallback_geocode_result", result)
    return result


def _infer_coordinates(location_text: str) -> dict[str, Any]:
    """Cho agent/LLM tự suy ra tọa độ từ địa chỉ nhập vào."""
    _log("geocode_input", {"location_text": location_text})

    if llm is None:
        return _fallback_geocode(location_text)

    try:
        prompt = (
            "Bạn là hệ thống geocoding cho ứng dụng xe điện.\n"
            "Hãy suy ra tọa độ gần đúng của địa điểm người dùng cung cấp dựa trên tri thức địa lý bạn biết.\n"
            "Nếu địa chỉ không đầy đủ, hãy chọn khu vực trung tâm hợp lý nhất.\n"
            "Trả về JSON hợp lệ với đúng các key sau: "
            '"resolved_location", "latitude", "longitude".\n'
            "Latitude và longitude phải là số.\n"
            "Không trả về markdown, không giải thích.\n\n"
            f"Input: {location_text}"
        )
        response = llm.invoke(prompt).content.strip()
        payload = json.loads(response)

        if not all(key in payload for key in ("resolved_location", "latitude", "longitude")):
            raise ValueError("Missing geocode keys")

        result = {
            "input": location_text,
            "resolved_location": str(payload["resolved_location"]).strip() or location_text,
            "latitude": float(payload["latitude"]),
            "longitude": float(payload["longitude"]),
            "source": "llm_inferred",
        }
        _log("llm_geocode_result", result)
        return result
    except Exception:
        return _fallback_geocode(location_text)


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_km = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    return round(radius_km * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))), 2)


def get_nearest_charging_stations_data(location_text: str) -> dict[str, Any]:
    user_location = _infer_coordinates(location_text)
    stations = []

    for station in CHARGING_STATIONS:
        station_data = station.copy()
        station_data["distance_km"] = _haversine_km(
            user_location["latitude"],
            user_location["longitude"],
            station["latitude"],
            station["longitude"],
        )
        stations.append(station_data)

    stations.sort(key=lambda item: (item["available"] <= 0, item["distance_km"]))

    result = {
        "query": location_text,
        "resolved_location": user_location["resolved_location"],
        "latitude": user_location["latitude"],
        "longitude": user_location["longitude"],
        "source": user_location["source"],
        "stations": stations[:4],
    }
    _log(
        "nearest_stations_result",
        {
            "query": location_text,
            "resolved_location": result["resolved_location"],
            "source": result["source"],
            "station_ids": [station["id"] for station in result["stations"]],
        },
    )
    return result


@tool
def geocode_tool(location_text: str) -> dict[str, Any]:
    """Tool xác định tọa độ từ địa chỉ người dùng bằng suy luận của agent/LLM."""
    return _infer_coordinates(location_text)


@tool
def find_stations_tool(latitude: float, longitude: float) -> list[dict[str, Any]]:
    """Tính khoảng cách từ vị trí người dùng đến các trạm sạc và sắp xếp gần nhất."""
    stations = []

    for station in CHARGING_STATIONS:
        station_data = station.copy()
        station_data["distance_km"] = _haversine_km(
            latitude,
            longitude,
            station["latitude"],
            station["longitude"],
        )
        stations.append(station_data)

    stations.sort(key=lambda item: (item["available"] <= 0, item["distance_km"]))
    return stations[:4]


@tool
def find_charging_station(user_query: str) -> str:
    """Tìm 3 trạm sạc VinFast gần nhất từ câu hỏi tự nhiên của người dùng."""
    location_text = _extract_location_from_query(user_query)
    user_location = geocode_tool.invoke({"location_text": location_text})
    _log("find_charging_station_geocode", user_location)
    stations = find_stations_tool.invoke(
        {
            "latitude": user_location["latitude"],
            "longitude": user_location["longitude"],
        }
    )
    _log(
        "find_charging_station_top",
        {"location_text": location_text, "station_ids": [station["id"] for station in stations]},
    )

    if not stations:
        return "Không tìm thấy trạm sạc nào phù hợp."

    lines = [
        "Trạm sạc gần nhất:",
        f"- Vị trí yêu cầu: {location_text}",
        (
            f"- Tọa độ người dùng: {user_location['resolved_location']} "
            f"({user_location['latitude']}, {user_location['longitude']})"
        ),
    ]

    for index, station in enumerate(stations[:3], 1):
        lines.append(f"{index}. {station['name']} - {station['distance_km']} km")
        lines.append(f"   Địa chỉ: {station['address']}")
        lines.append(
            f"   Trạng thái: {station['status']} | Còn trống {station['available']}/{station['total']} trụ"
        )
        lines.append(
            f"   Loại sạc: {station['type']} | Thời gian ước tính: ~{station['charge_time_min']} phút"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    result = find_charging_station.invoke({"user_query": "Xe tôi sắp hết pin ở VinUni"})
    print(result)
