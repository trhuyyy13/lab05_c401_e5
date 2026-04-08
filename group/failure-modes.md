# Top 3 failure modes

Liệt kê cách product có thể fail — không phải list features.

> **"Failure mode nào user KHÔNG BIẾT bị sai? Đó là cái nguy hiểm nhất."**

---

## Top 3

| # | Trigger | Hậu quả | Mitigation |
|---|---------|---------|------------|
| 1 | Hệ thống **hiểu sai tình trạng xe** (ví dụ: đọc sai sensor, hoặc NLP hiểu sai mô tả của user) | Gợi ý hành động sai (ví dụ: tiếp tục đi khi xe sắp hết pin / lỗi phanh) — **user không biết bị sai**, có thể gây nguy hiểm | Confidence score + uncertainty detection. Nếu dưới ngưỡng → fallback: yêu cầu xác nhận thêm (triệu chứng, ảnh, log xe) hoặc đề xuất liên hệ hỗ trợ |
| 2 | **Dữ liệu dịch vụ không cập nhật** (trạm sạc hết chỗ, cây xăng đóng cửa, gara không hoạt động) | User di chuyển đến địa điểm không khả dụng → mất thời gian, có thể bị kẹt giữa đường | Real-time data sync + verify availability (API / crowdsourcing). Hiển thị trạng thái (open/close, availability). Luôn đưa ≥2 phương án dự phòng |
| 3 | **Automation hành động sai** (auto đặt lịch sửa chữa / gọi cứu hộ không đúng nhu cầu) | Phát sinh chi phí không cần thiết hoặc delay xử lý vấn đề thực → **đã xảy ra rồi mới biết** | Human-in-the-loop: yêu cầu confirm trước action quan trọng. Delay + undo (30–60s). Hiển thị rõ thông tin trước khi thực hiện (giá, địa điểm, thời gian) |

---

## Ghi chú

- Failure mode #1 là nguy hiểm nhất vì **silent failure** (user tin hệ thống).
- Failure mode #3 thuộc dạng **irreversible action** → cần prevention mạnh hơn detection.
- Với hệ thống này, càng nhiều automation → càng phải thiết kế **guardrails + fallback** tốt.
