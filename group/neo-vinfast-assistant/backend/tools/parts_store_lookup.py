"""
Tool: Tìm cửa hàng linh kiện VinFast gần nhất
Mô tả: Tra cứu cửa hàng/đại lý VinFast có linh kiện mà user yêu cầu,
       sắp xếp theo khoảng cách gần nhất.

NGUYÊN TẮC: Tool này CHỈ được gọi khi user nói rõ tên linh kiện cần tìm.
            KHÔNG tự suy đoán linh kiện nếu user không chỉ định.

Author: NEO Team
"""

from langchain_core.tools import tool


# ── Mock database cửa hàng linh kiện VinFast ─────────────────────────
PARTS_STORES = [
    {
        "name": "VinFast Parts — Thanh Xuân",
        "address": "12 Khuất Duy Tiến, Thanh Xuân, Hà Nội",
        "phone": "024 1234 5601",
        "distance_km": 3.2,
        "hours": "08:00 – 18:00",
        "inventory": {
            "lốp": {
                "full_name": "Lốp Michelin Primacy 4 — 235/55R19",
                "price": "3.200.000đ/lốp",
                "stock": 12,
                "compatible": ["VF 8", "VF 8 Plus", "VF 9"],
            },
            "má phanh": {
                "full_name": "Má phanh trước OEM VinFast",
                "price": "1.800.000đ/bộ",
                "stock": 8,
                "compatible": ["VF 8", "VF 8 Plus", "VF 9", "VF e34"],
            },
            "dầu phanh": {
                "full_name": "Dầu phanh DOT4 Bosch 500ml",
                "price": "250.000đ/chai",
                "stock": 20,
                "compatible": ["Tất cả dòng VinFast"],
            },
            "gạt mưa": {
                "full_name": "Gạt mưa Bosch Aerotwin 600/450mm",
                "price": "380.000đ/bộ",
                "stock": 15,
                "compatible": ["VF 8", "VF 8 Plus"],
            },
            "bóng đèn": {
                "full_name": "Bóng đèn LED pha OEM VinFast",
                "price": "1.200.000đ/bóng",
                "stock": 6,
                "compatible": ["VF 8", "VF 8 Plus", "VF 9"],
            },
        },
    },
    {
        "name": "VinFast Parts — Long Biên",
        "address": "KĐT Vinhomes Riverside, Long Biên, Hà Nội",
        "phone": "024 1234 5602",
        "distance_km": 5.1,
        "hours": "08:00 – 17:30",
        "inventory": {
            "lốp": {
                "full_name": "Lốp Continental PremiumContact 6 — 235/55R19",
                "price": "3.500.000đ/lốp",
                "stock": 8,
                "compatible": ["VF 8", "VF 8 Plus", "VF 9"],
            },
            "bộ lọc gió": {
                "full_name": "Bộ lọc gió điều hòa OEM VinFast",
                "price": "450.000đ/cái",
                "stock": 10,
                "compatible": ["VF 8", "VF 8 Plus", "VF 9", "VF e34", "VF 5"],
            },
            "nước làm mát": {
                "full_name": "Nước làm mát động cơ Coolant VinFast 4L",
                "price": "180.000đ/lít",
                "stock": 25,
                "compatible": ["Tất cả dòng VinFast"],
            },
            "gạt mưa": {
                "full_name": "Gạt mưa Denso DUR-060L 600/400mm",
                "price": "420.000đ/bộ",
                "stock": 5,
                "compatible": ["VF 8", "VF 8 Plus", "VF 9"],
            },
        },
    },
    {
        "name": "VinFast Parts — Cầu Giấy",
        "address": "168 Trần Duy Hưng, Cầu Giấy, Hà Nội",
        "phone": "024 1234 5603",
        "distance_km": 6.0,
        "hours": "08:30 – 18:00",
        "inventory": {
            "má phanh": {
                "full_name": "Má phanh sau OEM VinFast",
                "price": "1.500.000đ/bộ",
                "stock": 6,
                "compatible": ["VF 8", "VF 8 Plus", "VF 9"],
            },
            "dầu phanh": {
                "full_name": "Dầu phanh DOT4 Castrol 1L",
                "price": "280.000đ/chai",
                "stock": 14,
                "compatible": ["Tất cả dòng VinFast"],
            },
            "bộ lọc gió": {
                "full_name": "Bộ lọc gió cabin Carbon VinFast",
                "price": "520.000đ/cái",
                "stock": 7,
                "compatible": ["VF 8", "VF 8 Plus", "VF 9"],
            },
            "nước làm mát": {
                "full_name": "Nước làm mát Prestone 50/50 4L",
                "price": "200.000đ/lít",
                "stock": 18,
                "compatible": ["Tất cả dòng VinFast"],
            },
            "bóng đèn": {
                "full_name": "Bóng đèn LED sương mù OEM VinFast",
                "price": "850.000đ/bóng",
                "stock": 10,
                "compatible": ["VF 8", "VF 8 Plus"],
            },
        },
    },
    {
        "name": "VinFast Parts — Hai Bà Trưng",
        "address": "191 Bà Triệu, Hai Bà Trưng, Hà Nội",
        "phone": "024 1234 5604",
        "distance_km": 2.5,
        "hours": "09:00 – 18:30",
        "inventory": {
            "lốp": {
                "full_name": "Lốp Hankook Ventus S1 evo3 — 235/55R19",
                "price": "2.900.000đ/lốp",
                "stock": 4,
                "compatible": ["VF 8", "VF 8 Plus"],
            },
            "gạt mưa": {
                "full_name": "Gạt mưa Valeo First Flat 600/450mm",
                "price": "350.000đ/bộ",
                "stock": 20,
                "compatible": ["VF 8", "VF 8 Plus", "VF e34"],
            },
            "bóng đèn": {
                "full_name": "Bóng đèn LED xi-nhan OEM VinFast",
                "price": "450.000đ/bóng",
                "stock": 18,
                "compatible": ["Tất cả dòng VinFast"],
            },
            "dầu phanh": {
                "full_name": "Dầu phanh DOT4 Mobil 500ml",
                "price": "230.000đ/chai",
                "stock": 9,
                "compatible": ["Tất cả dòng VinFast"],
            },
        },
    },
    {
        "name": "VinFast Parts — Hoàng Mai",
        "address": "365 Giải Phóng, Hoàng Mai, Hà Nội",
        "phone": "024 1234 5605",
        "distance_km": 4.7,
        "hours": "08:00 – 17:00",
        "inventory": {
            "lốp": {
                "full_name": "Lốp Bridgestone Turanza T005 — 235/55R19",
                "price": "3.100.000đ/lốp",
                "stock": 6,
                "compatible": ["VF 8", "VF 8 Plus", "VF 9"],
            },
            "má phanh": {
                "full_name": "Má phanh trước Brembo Performance",
                "price": "2.200.000đ/bộ",
                "stock": 3,
                "compatible": ["VF 8 Plus", "VF 9"],
            },
            "bộ lọc gió": {
                "full_name": "Bộ lọc gió động cơ K&N High Performance",
                "price": "680.000đ/cái",
                "stock": 4,
                "compatible": ["VF 8", "VF 8 Plus"],
            },
            "nước làm mát": {
                "full_name": "Nước làm mát Motul Inugel Optimal 5L",
                "price": "220.000đ/lít",
                "stock": 12,
                "compatible": ["Tất cả dòng VinFast"],
            },
            "gạt mưa": {
                "full_name": "Gạt mưa SWF VisioNext 600/450mm",
                "price": "400.000đ/bộ",
                "stock": 8,
                "compatible": ["VF 8", "VF 8 Plus", "VF 9"],
            },
        },
    },
]


# ── Bảng alias linh kiện (keyword → tên chuẩn) ──────────────────────
PART_ALIASES = {
    # Lốp
    "lốp": "lốp",
    "bánh xe": "lốp",
    "vỏ xe": "lốp",
    "tire": "lốp",
    "lốp xe": "lốp",
    # Má phanh
    "má phanh": "má phanh",
    "phanh": "má phanh",
    "brake pad": "má phanh",
    "bố phanh": "má phanh",
    # Dầu phanh
    "dầu phanh": "dầu phanh",
    "brake fluid": "dầu phanh",
    "dot4": "dầu phanh",
    # Bộ lọc gió
    "bộ lọc gió": "bộ lọc gió",
    "lọc gió": "bộ lọc gió",
    "filter": "bộ lọc gió",
    "air filter": "bộ lọc gió",
    "lọc gió điều hòa": "bộ lọc gió",
    # Nước làm mát
    "nước làm mát": "nước làm mát",
    "coolant": "nước làm mát",
    "nước giải nhiệt": "nước làm mát",
    # Gạt mưa
    "gạt mưa": "gạt mưa",
    "cần gạt": "gạt mưa",
    "wiper": "gạt mưa",
    "gạt nước": "gạt mưa",
    # Bóng đèn
    "bóng đèn": "bóng đèn",
    "đèn pha": "bóng đèn",
    "đèn": "bóng đèn",
    "led": "bóng đèn",
    "đèn xe": "bóng đèn",
    "đèn xi nhan": "bóng đèn",
    "đèn sương mù": "bóng đèn",
}


def _resolve_part_name(user_input: str) -> str | None:
    """
    Trích xuất tên linh kiện chuẩn từ input của user.
    Trả về None nếu KHÔNG tìm thấy linh kiện nào được nhắc đến.
    """
    user_lower = user_input.lower()
    for keyword, canonical in PART_ALIASES.items():
        if keyword in user_lower:
            return canonical
    return None


@tool
def find_parts_store(part_name: str, location: str = "Hà Nội") -> str:
    """Tìm cửa hàng/đại lý VinFast gần nhất có linh kiện mà người dùng yêu cầu.

    QUAN TRỌNG: Chỉ gọi tool này khi người dùng NÓI RÕ tên linh kiện cần tìm.
    KHÔNG gọi nếu người dùng chỉ nói "bảo dưỡng" chung chung mà không chỉ định linh kiện.

    Args:
        part_name: Tên linh kiện cần tìm (VD: "lốp", "má phanh", "dầu phanh",
                   "bộ lọc gió", "nước làm mát", "gạt mưa", "bóng đèn")
        location: Khu vực tìm kiếm (mặc định: Hà Nội)

    Returns:
        Danh sách cửa hàng gần nhất có linh kiện, kèm giá và tồn kho.
    """
    # Chuẩn hóa tên linh kiện
    resolved = _resolve_part_name(part_name)
    if not resolved:
        resolved = part_name.lower().strip()

    # Tìm cửa hàng có linh kiện này, sắp xếp theo khoảng cách
    matching_stores = []
    for store in PARTS_STORES:
        if resolved in store["inventory"]:
            part_info = store["inventory"][resolved]
            if part_info["stock"] > 0:
                matching_stores.append({
                    "store": store,
                    "part": part_info,
                })

    # Sắp xếp theo khoảng cách gần nhất
    matching_stores.sort(key=lambda x: x["store"]["distance_km"])

    if not matching_stores:
        available_parts = set()
        for store in PARTS_STORES:
            available_parts.update(store["inventory"].keys())
        parts_list = ", ".join(sorted(available_parts))

        return (
            f"❌ Không tìm thấy cửa hàng nào có linh kiện \"{part_name}\" trong khu vực {location}.\n\n"
            f"📋 Các linh kiện hiện có trong hệ thống:\n"
            f"   {parts_list}\n\n"
            f"Bạn có muốn tìm linh kiện khác không?"
        )

    # Format kết quả
    results = []
    for i, match in enumerate(matching_stores[:3], 1):
        store = match["store"]
        part = match["part"]
        compatible = ", ".join(part["compatible"]) if isinstance(part["compatible"], list) else part["compatible"]
        stock_emoji = "🟢" if part["stock"] >= 5 else "🟡" if part["stock"] >= 2 else "🔴"

        results.append(
            f"{i}. **{store['name']}**\n"
            f"   📍 {store['address']} — {store['distance_km']} km\n"
            f"   📞 {store['phone']}\n"
            f"   🕐 {store['hours']}\n"
            f"   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
            f"   🔩 {part['full_name']}\n"
            f"   💰 Giá: {part['price']}\n"
            f"   {stock_emoji} Tồn kho: {part['stock']} sản phẩm\n"
            f"   🚗 Tương thích: {compatible}"
        )

    header = (
        f"🔍 Tìm thấy {len(matching_stores)} cửa hàng có **{resolved}** "
        f"tại {location}:\n\n"
    )
    footer = (
        "\n\n💡 Bạn muốn tôi đặt lịch thay linh kiện tại cửa hàng nào?"
    )

    return header + "\n\n".join(results) + footer
