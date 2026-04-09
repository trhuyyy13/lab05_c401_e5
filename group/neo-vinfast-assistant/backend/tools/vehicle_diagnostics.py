"""
Tool: Chẩn đoán sự cố xe VinFast
Mô tả: Tra cứu mã lỗi, phân tích triệu chứng, đưa ra chẩn đoán và mức độ nghiêm trọng.

Author: [Tên thành viên]
"""

from langchain_core.tools import tool


# ── Mock database mã lỗi VinFast ─────────────────────────────────────
ERROR_DATABASE = {
    "E12": {
        "name": "Lỗi hệ thống pin cao áp",
        "severity": "high",
        "severity_label": "🔴 Nghiêm trọng",
        "description": "Hệ thống pin cao áp phát hiện bất thường về điện áp hoặc nhiệt độ.",
        "action": [
            "Dừng xe ở nơi an toàn ngay lập tức",
            "Không tự ý mở nắp capô hoặc can thiệp",
            "Liên hệ hotline VinFast: 1900 23 23 89",
            "Chờ đội ngũ kỹ thuật đến kiểm tra",
        ],
    },
    "E45": {
        "name": "Lỗi cảm biến áp suất lốp",
        "severity": "medium",
        "severity_label": "🟡 Trung bình",
        "description": "Một hoặc nhiều lốp có áp suất bất thường (quá thấp hoặc quá cao).",
        "action": [
            "Giảm tốc độ, tránh phanh gấp",
            "Tìm trạm bơm lốp gần nhất",
            "Kiểm tra trực quan các lốp",
            "Nếu lốp xẹp rõ → gọi cứu hộ",
        ],
    },
    "W03": {
        "name": "Cảnh báo bảo dưỡng định kỳ",
        "severity": "low",
        "severity_label": "🟢 Thấp",
        "description": "Xe đã đến hạn bảo dưỡng định kỳ theo km hoặc thời gian.",
        "action": [
            "Đặt lịch bảo dưỡng trong 7 ngày tới",
            "Có thể tiếp tục sử dụng xe bình thường",
            "Kiểm tra dầu phanh, nước làm mát cơ bản",
        ],
    },
    "E78": {
        "name": "Lỗi hệ thống phanh tái sinh",
        "severity": "high",
        "severity_label": "🔴 Nghiêm trọng",
        "description": "Phanh tái sinh không hoạt động đúng cách, ảnh hưởng đến khả năng giảm tốc.",
        "action": [
            "Sử dụng phanh cơ học (phanh chân) để giảm tốc",
            "Giảm tốc độ và giữ khoảng cách an toàn",
            "KHÔNG lái xe trên đường cao tốc",
            "Liên hệ cứu hộ VinFast ngay",
        ],
    },
    "W15": {
        "name": "Pin sắp hết — cần sạc",
        "severity": "medium",
        "severity_label": "🟡 Trung bình",
        "description": "Mức pin còn dưới 15%, cần tìm trạm sạc sớm.",
        "action": [
            "Bật chế độ tiết kiệm năng lượng (Eco mode)",
            "Tắt điều hòa nếu có thể",
            "Tìm trạm sạc gần nhất",
            "Hạn chế tăng tốc đột ngột",
        ],
    },
}

# ── Bảng triệu chứng → mã lỗi ───────────────────────────────────────
SYMPTOM_MAP = {
    "pin": "W15",
    "hết pin": "W15",
    "sắp hết pin": "W15",
    "battery": "W15",
    "lốp": "E45",
    "bánh xe": "E45",
    "áp suất": "E45",
    "phanh": "E78",
    "không phanh": "E78",
    "phanh yếu": "E78",
    "bảo dưỡng": "W03",
    "bảo hành": "W03",
    "định kỳ": "W03",
}


@tool
def diagnose_vehicle(symptom: str) -> str:
    """Chẩn đoán sự cố xe VinFast dựa trên mã lỗi hoặc mô tả triệu chứng.
    
    Args:
        symptom: Mã lỗi (VD: E12, E45) hoặc mô tả triệu chứng (VD: "xe hết pin", "lốp xẹp")
    
    Returns:
        Thông tin chẩn đoán bao gồm: tên lỗi, mức độ, mô tả, hướng xử lý.
    """
    symptom_upper = symptom.strip().upper()
    
    # Tìm theo mã lỗi trực tiếp
    if symptom_upper in ERROR_DATABASE:
        error = ERROR_DATABASE[symptom_upper]
    else:
        # Tìm theo triệu chứng keyword
        matched_code = None
        symptom_lower = symptom.lower()
        for keyword, code in SYMPTOM_MAP.items():
            if keyword in symptom_lower:
                matched_code = code
                break
        
        if matched_code:
            error = ERROR_DATABASE[matched_code]
        else:
            # Mặc định E12 cho demo
            error = ERROR_DATABASE["E12"]
    
    actions = "\n".join(f"  {i+1}. {a}" for i, a in enumerate(error["action"]))
    
    return (
        f"🔍 Kết quả chẩn đoán:\n"
        f"- Tên lỗi: {error['name']}\n"
        f"- Mức độ: {error['severity_label']}\n"
        f"- Mô tả: {error['description']}\n"
        f"- Hướng xử lý:\n{actions}"
    )
