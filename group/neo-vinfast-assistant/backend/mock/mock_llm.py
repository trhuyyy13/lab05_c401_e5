"""
Mock LLM — Giả lập LLM response cho demo local không cần API key.

Cơ chế: keyword matching trên input → trả response có cấu trúc ReAct.
Khi có API key thật, thay MockLLM bằng ChatOpenAI hoặc model khác.

NGUYÊN TẮC QUAN TRỌNG:
- Với yêu cầu bảo dưỡng: KHÔNG tự suy đoán linh kiện
- Chỉ gọi find_parts_store khi user NÓI RÕ tên linh kiện
- Nếu user nói chung → hỏi lại cụ thể
"""

from __future__ import annotations
import re
import json
from langchain_core.messages import AIMessage, ToolMessage


# ── Danh sách keyword linh kiện cụ thể ───────────────────────────────
# Dùng để phát hiện user có nói RÕ linh kiện không
PART_KEYWORDS = {
    "lốp": "lốp",
    "bánh xe": "lốp",
    "vỏ xe": "lốp",
    "tire": "lốp",
    "má phanh": "má phanh",
    "bố phanh": "má phanh",
    "brake pad": "má phanh",
    "dầu phanh": "dầu phanh",
    "brake fluid": "dầu phanh",
    "dot4": "dầu phanh",
    "bộ lọc gió": "bộ lọc gió",
    "lọc gió": "bộ lọc gió",
    "filter": "bộ lọc gió",
    "nước làm mát": "nước làm mát",
    "coolant": "nước làm mát",
    "nước giải nhiệt": "nước làm mát",
    "gạt mưa": "gạt mưa",
    "cần gạt": "gạt mưa",
    "wiper": "gạt mưa",
    "gạt nước": "gạt mưa",
    "bóng đèn": "bóng đèn",
    "đèn pha": "bóng đèn",
    "đèn xe": "bóng đèn",
    "đèn xi nhan": "bóng đèn",
    "đèn sương mù": "bóng đèn",
    "led": "bóng đèn",
}


def _extract_part_name(user_message: str) -> str | None:
    """
    Trích xuất tên linh kiện cụ thể từ tin nhắn user.
    Trả về None nếu user KHÔNG nhắc đến linh kiện nào.
    """
    user_lower = user_message.lower()
    for keyword, canonical in PART_KEYWORDS.items():
        if keyword in user_lower:
            return canonical
    return None


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
    "sạc|battery|charge|trạm sạc|hết pin|sắp hết pin|charging": {
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


# ── Response cho yêu cầu bảo dưỡng CHUNG (KHÔNG nói linh kiện) ──────
GENERIC_MAINTENANCE_RESPONSE = {
    "thought": (
        "Người dùng yêu cầu bảo dưỡng nhưng KHÔNG chỉ rõ linh kiện cụ thể. "
        "Theo nguyên tắc, tôi KHÔNG ĐƯỢC tự suy đoán linh kiện. "
        "Tôi cần hỏi lại user muốn thay/mua linh kiện gì."
    ),
    "tool": None,
    "tool_input": {},
    "fallback_answer": (
        "🔧 **Bảo dưỡng xe VinFast**\n\n"
        "Tôi có thể giúp bạn tìm cửa hàng linh kiện gần nhất! "
        "Tuy nhiên, **bạn chưa cho tôi biết cần thay/mua linh kiện gì cụ thể**.\n\n"
        "📋 **Danh sách linh kiện có sẵn trong hệ thống:**\n"
        "1. 🛞 **Lốp** — lốp Michelin, Continental, Bridgestone, Hankook\n"
        "2. 🛑 **Má phanh** — má phanh trước/sau OEM, Brembo\n"
        "3. 🫗 **Dầu phanh** — DOT4 Bosch, Castrol, Mobil\n"
        "4. 🌀 **Bộ lọc gió** — lọc gió điều hòa, lọc gió động cơ\n"
        "5. 💧 **Nước làm mát** — Coolant VinFast, Prestone, Motul\n"
        "6. 🪥 **Gạt mưa** — Bosch, Denso, Valeo, SWF\n"
        "7. 💡 **Bóng đèn** — LED pha, LED sương mù, LED xi-nhan\n\n"
        "👉 **Bạn muốn thay/mua linh kiện nào?** Hãy cho tôi biết cụ thể để tôi tìm cửa hàng gần nhất có hàng nhé!"
    ),
}


# ── Response mẫu cho từng loại linh kiện (khi user NÓI RÕ) ──────────
PARTS_MOCK_RESULTS = {
    "lốp": (
        "🔍 Tìm thấy **4 cửa hàng** có **lốp** tại Hà Nội:\n\n"
        "1. **VinFast Parts — Hai Bà Trưng**\n"
        "   📍 191 Bà Triệu, Hai Bà Trưng — 2.5 km\n"
        "   📞 024 1234 5604\n"
        "   🕐 09:00 – 18:30\n"
        "   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        "   🔩 Lốp Hankook Ventus S1 evo3 — 235/55R19\n"
        "   💰 Giá: 2.900.000đ/lốp\n"
        "   🟡 Tồn kho: 4 sản phẩm\n"
        "   🚗 Tương thích: VF 8, VF 8 Plus\n\n"
        "2. **VinFast Parts — Thanh Xuân**\n"
        "   📍 12 Khuất Duy Tiến, Thanh Xuân — 3.2 km\n"
        "   📞 024 1234 5601\n"
        "   🕐 08:00 – 18:00\n"
        "   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        "   🔩 Lốp Michelin Primacy 4 — 235/55R19\n"
        "   💰 Giá: 3.200.000đ/lốp\n"
        "   🟢 Tồn kho: 12 sản phẩm\n"
        "   🚗 Tương thích: VF 8, VF 8 Plus, VF 9\n\n"
        "3. **VinFast Parts — Hoàng Mai**\n"
        "   📍 365 Giải Phóng, Hoàng Mai — 4.7 km\n"
        "   📞 024 1234 5605\n"
        "   🕐 08:00 – 17:00\n"
        "   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        "   🔩 Lốp Bridgestone Turanza T005 — 235/55R19\n"
        "   💰 Giá: 3.100.000đ/lốp\n"
        "   🟢 Tồn kho: 6 sản phẩm\n"
        "   🚗 Tương thích: VF 8, VF 8 Plus, VF 9\n\n"
        "💡 Bạn muốn tôi đặt lịch thay lốp tại cửa hàng nào?"
    ),
    "má phanh": (
        "🔍 Tìm thấy **3 cửa hàng** có **má phanh** tại Hà Nội:\n\n"
        "1. **VinFast Parts — Thanh Xuân**\n"
        "   📍 12 Khuất Duy Tiến, Thanh Xuân — 3.2 km\n"
        "   📞 024 1234 5601\n"
        "   🕐 08:00 – 18:00\n"
        "   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        "   🔩 Má phanh trước OEM VinFast\n"
        "   💰 Giá: 1.800.000đ/bộ\n"
        "   🟢 Tồn kho: 8 sản phẩm\n"
        "   🚗 Tương thích: VF 8, VF 8 Plus, VF 9, VF e34\n\n"
        "2. **VinFast Parts — Hoàng Mai**\n"
        "   📍 365 Giải Phóng, Hoàng Mai — 4.7 km\n"
        "   📞 024 1234 5605\n"
        "   🕐 08:00 – 17:00\n"
        "   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        "   🔩 Má phanh trước Brembo Performance\n"
        "   💰 Giá: 2.200.000đ/bộ\n"
        "   🟡 Tồn kho: 3 sản phẩm\n"
        "   🚗 Tương thích: VF 8 Plus, VF 9\n\n"
        "3. **VinFast Parts — Cầu Giấy**\n"
        "   📍 168 Trần Duy Hưng, Cầu Giấy — 6.0 km\n"
        "   📞 024 1234 5603\n"
        "   🕐 08:30 – 18:00\n"
        "   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        "   🔩 Má phanh sau OEM VinFast\n"
        "   💰 Giá: 1.500.000đ/bộ\n"
        "   🟢 Tồn kho: 6 sản phẩm\n"
        "   🚗 Tương thích: VF 8, VF 8 Plus, VF 9\n\n"
        "💡 Bạn muốn tôi đặt lịch thay má phanh tại cửa hàng nào?"
    ),
    "dầu phanh": (
        "🔍 Tìm thấy **3 cửa hàng** có **dầu phanh** tại Hà Nội:\n\n"
        "1. **VinFast Parts — Hai Bà Trưng**\n"
        "   📍 191 Bà Triệu, Hai Bà Trưng — 2.5 km\n"
        "   📞 024 1234 5604\n"
        "   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        "   🔩 Dầu phanh DOT4 Mobil 500ml\n"
        "   💰 Giá: 230.000đ/chai\n"
        "   🟢 Tồn kho: 9 sản phẩm\n\n"
        "2. **VinFast Parts — Thanh Xuân**\n"
        "   📍 12 Khuất Duy Tiến, Thanh Xuân — 3.2 km\n"
        "   📞 024 1234 5601\n"
        "   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        "   🔩 Dầu phanh DOT4 Bosch 500ml\n"
        "   💰 Giá: 250.000đ/chai\n"
        "   🟢 Tồn kho: 20 sản phẩm\n\n"
        "3. **VinFast Parts — Cầu Giấy**\n"
        "   📍 168 Trần Duy Hưng, Cầu Giấy — 6.0 km\n"
        "   📞 024 1234 5603\n"
        "   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        "   🔩 Dầu phanh DOT4 Castrol 1L\n"
        "   💰 Giá: 280.000đ/chai\n"
        "   🟢 Tồn kho: 14 sản phẩm\n\n"
        "💡 Bạn muốn mua dầu phanh ở cửa hàng nào?"
    ),
    "gạt mưa": (
        "🔍 Tìm thấy **4 cửa hàng** có **gạt mưa** tại Hà Nội:\n\n"
        "1. **VinFast Parts — Hai Bà Trưng**\n"
        "   📍 191 Bà Triệu, Hai Bà Trưng — 2.5 km\n"
        "   📞 024 1234 5604\n"
        "   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        "   🔩 Gạt mưa Valeo First Flat 600/450mm\n"
        "   💰 Giá: 350.000đ/bộ\n"
        "   🟢 Tồn kho: 20 sản phẩm\n\n"
        "2. **VinFast Parts — Thanh Xuân**\n"
        "   📍 12 Khuất Duy Tiến, Thanh Xuân — 3.2 km\n"
        "   📞 024 1234 5601\n"
        "   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        "   🔩 Gạt mưa Bosch Aerotwin 600/450mm\n"
        "   💰 Giá: 380.000đ/bộ\n"
        "   🟢 Tồn kho: 15 sản phẩm\n\n"
        "💡 Bạn muốn tôi đặt lịch thay gạt mưa tại cửa hàng nào?"
    ),
    "bộ lọc gió": (
        "🔍 Tìm thấy **3 cửa hàng** có **bộ lọc gió** tại Hà Nội:\n\n"
        "1. **VinFast Parts — Hoàng Mai**\n"
        "   📍 365 Giải Phóng, Hoàng Mai — 4.7 km\n"
        "   📞 024 1234 5605\n"
        "   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        "   🔩 Bộ lọc gió động cơ K&N High Performance\n"
        "   💰 Giá: 680.000đ/cái\n"
        "   🟡 Tồn kho: 4 sản phẩm\n\n"
        "2. **VinFast Parts — Long Biên**\n"
        "   📍 KĐT Vinhomes Riverside, Long Biên — 5.1 km\n"
        "   📞 024 1234 5602\n"
        "   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        "   🔩 Bộ lọc gió điều hòa OEM VinFast\n"
        "   💰 Giá: 450.000đ/cái\n"
        "   🟢 Tồn kho: 10 sản phẩm\n\n"
        "💡 Bạn muốn mua bộ lọc gió ở cửa hàng nào?"
    ),
    "nước làm mát": (
        "🔍 Tìm thấy **3 cửa hàng** có **nước làm mát** tại Hà Nội:\n\n"
        "1. **VinFast Parts — Hoàng Mai**\n"
        "   📍 365 Giải Phóng, Hoàng Mai — 4.7 km\n"
        "   📞 024 1234 5605\n"
        "   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        "   🔩 Nước làm mát Motul Inugel Optimal 5L\n"
        "   💰 Giá: 220.000đ/lít\n"
        "   🟢 Tồn kho: 12 sản phẩm\n\n"
        "2. **VinFast Parts — Long Biên**\n"
        "   📍 KĐT Vinhomes Riverside, Long Biên — 5.1 km\n"
        "   📞 024 1234 5602\n"
        "   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        "   🔩 Nước làm mát động cơ Coolant VinFast 4L\n"
        "   💰 Giá: 180.000đ/lít\n"
        "   🟢 Tồn kho: 25 sản phẩm\n\n"
        "💡 Bạn muốn mua nước làm mát ở cửa hàng nào?"
    ),
    "bóng đèn": (
        "🔍 Tìm thấy **3 cửa hàng** có **bóng đèn** tại Hà Nội:\n\n"
        "1. **VinFast Parts — Hai Bà Trưng**\n"
        "   📍 191 Bà Triệu, Hai Bà Trưng — 2.5 km\n"
        "   📞 024 1234 5604\n"
        "   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        "   🔩 Bóng đèn LED xi-nhan OEM VinFast\n"
        "   💰 Giá: 450.000đ/bóng\n"
        "   🟢 Tồn kho: 18 sản phẩm\n\n"
        "2. **VinFast Parts — Thanh Xuân**\n"
        "   📍 12 Khuất Duy Tiến, Thanh Xuân — 3.2 km\n"
        "   📞 024 1234 5601\n"
        "   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        "   🔩 Bóng đèn LED pha OEM VinFast\n"
        "   💰 Giá: 1.200.000đ/bóng\n"
        "   🟢 Tồn kho: 6 sản phẩm\n\n"
        "💡 Bạn muốn mua bóng đèn ở cửa hàng nào?"
    ),
}


# Default response khi không match keyword nào
DEFAULT_RESPONSE = (
    "Xin chào! Tôi là **NEO** — trợ lý AI của VinFast 🚗\n\n"
    "Tôi có thể giúp bạn:\n"
    "- 🔍 **Chẩn đoán sự cố** — mô tả triệu chứng hoặc nhập mã lỗi\n"
    "- ⚡ **Tìm trạm sạc** — trạm gần nhất, trạng thái trống\n"
    "- 📅 **Đặt lịch dịch vụ** — bảo dưỡng, sửa chữa\n"
    "- 🔧 **Tìm linh kiện** — cửa hàng gần nhất có linh kiện bạn cần\n"
    "- 🌤️ **Kiểm tra thời tiết** — tư vấn lái xe an toàn\n"
    "- 🚨 **Hỗ trợ khẩn cấp** — cứu hộ, tai nạn\n\n"
    "Hãy cho tôi biết bạn cần gì nhé!"
)


# ── Pattern bảo dưỡng chung (KHÔNG có linh kiện cụ thể) ─────────────
MAINTENANCE_GENERIC_PATTERN = r"bảo dưỡng|dịch vụ|service|bảo hành|sửa chữa|sửa xe"

# ── Pattern đặt lịch (chỉ đặt lịch, không liên quan linh kiện) ──────
BOOKING_PATTERN = r"đặt lịch|lịch hẹn|booking"


def _is_maintenance_request(user_lower: str) -> bool:
    """Kiểm tra xem user có đang hỏi về bảo dưỡng / dịch vụ không."""
    return bool(re.search(MAINTENANCE_GENERIC_PATTERN, user_lower))


def _is_booking_request(user_lower: str) -> bool:
    """Kiểm tra xem user có đang muốn đặt lịch không."""
    return bool(re.search(BOOKING_PATTERN, user_lower))


def mock_react_response(user_message: str) -> dict:
    """
    Simulate a ReAct agent response based on keyword matching.
    
    Logic ưu tiên:
    1. Kiểm tra user có nói linh kiện cụ thể không → tìm cửa hàng
    2. Kiểm tra yêu cầu bảo dưỡng chung → hỏi lại (KHÔNG suy đoán)
    3. Kiểm tra đặt lịch → book_service
    4. Fallback vào MOCK_RESPONSES (lỗi xe, sạc, thời tiết, cứu hộ...)
    5. Default greeting
    
    Returns:
        dict with keys: thought, tool_used, tool_input, tool_result, answer, reasoning_steps
    """
    user_lower = user_message.lower()
    
    # ── Bước 1: Kiểm tra có linh kiện cụ thể không ──────────────────
    part_name = _extract_part_name(user_message)
    
    if part_name:
        # User NÓI RÕ linh kiện → gọi find_parts_store
        tool_input = {"part_name": part_name, "location": "Hà Nội"}
        
        # Lấy mock result tương ứng
        mock_result = PARTS_MOCK_RESULTS.get(part_name, f"Đang tìm cửa hàng có {part_name}...")
        
        reasoning_steps = [
            {"step": "Thought", "content": f"Người dùng cần tìm linh kiện '{part_name}'. Tôi sẽ tìm cửa hàng gần nhất có linh kiện này."},
            {"step": "Action", "content": f"Gọi tool: find_parts_store({json.dumps(tool_input, ensure_ascii=False)})"},
            {"step": "Observation", "content": f"Đã tìm thấy cửa hàng có {part_name}."},
            {"step": "Answer", "content": "Trả về danh sách cửa hàng có linh kiện, sắp xếp theo khoảng cách."},
        ]
        
        return {
            "thought": f"Người dùng cần tìm linh kiện '{part_name}'. Tôi sẽ dùng tool find_parts_store để tìm cửa hàng gần nhất.",
            "tool_used": "find_parts_store",
            "tool_input": tool_input,
            "tool_result": mock_result,
            "answer": mock_result,
            "reasoning_steps": reasoning_steps,
        }
    
    # ── Bước 2: Yêu cầu bảo dưỡng chung (KHÔNG nói linh kiện) ──────
    if _is_maintenance_request(user_lower) and not _is_booking_request(user_lower):
        response = GENERIC_MAINTENANCE_RESPONSE
        
        reasoning_steps = [
            {"step": "Thought", "content": response["thought"]},
            {"step": "Observation", "content": "User KHÔNG chỉ rõ linh kiện cụ thể. Cần hỏi lại."},
            {"step": "Answer", "content": "Hỏi user cụ thể cần linh kiện gì, liệt kê danh mục có sẵn."},
        ]
        
        return {
            "thought": response["thought"],
            "tool_used": None,
            "tool_input": {},
            "tool_result": None,
            "answer": response["fallback_answer"],
            "reasoning_steps": reasoning_steps,
        }
    
    # ── Bước 3: Đặt lịch ─────────────────────────────────────────────
    if _is_booking_request(user_lower):
        return {
            "thought": "Người dùng muốn đặt lịch dịch vụ. Tôi sẽ hỗ trợ đặt lịch.",
            "tool_used": "book_service",
            "tool_input": {"service_type": "bảo dưỡng định kỳ"},
            "tool_result": "Mock result — dữ liệu demo",
            "answer": (
                "📅 **Đặt lịch dịch vụ:**\n\n"
                "Tôi có thể giúp bạn đặt lịch tại các trung tâm VinFast Service:\n\n"
                "**Gần bạn nhất:**\n"
                "🔧 VinFast Service — Thanh Xuân\n"
                "📍 12 Khuất Duy Tiến, Thanh Xuân — 3.8 km\n"
                "⏰ Khung giờ trống: 8:30, 11:00, 14:30\n\n"
                "**Thông tin cần xác nhận:**\n"
                "- Loại dịch vụ: Bảo dưỡng định kỳ\n"
                "- Xe: VF 8 Plus\n"
                "- Thời gian dự kiến: ~2 giờ\n\n"
                "Bạn muốn chọn khung giờ nào?"
            ),
            "reasoning_steps": [
                {"step": "Thought", "content": "Người dùng muốn đặt lịch dịch vụ. Tôi sẽ hỗ trợ đặt lịch."},
                {"step": "Action", "content": "Gọi tool: book_service({\"service_type\": \"bảo dưỡng định kỳ\"})"},
                {"step": "Observation", "content": "Đã nhận kết quả từ tool."},
                {"step": "Answer", "content": "Tổng hợp câu trả lời cho người dùng."},
            ],
        }
    
    # ── Bước 4: Fallback vào MOCK_RESPONSES (lỗi xe, sạc, thời tiết...)
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
