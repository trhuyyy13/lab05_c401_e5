# AI Product Canvas — template

Điền Canvas cho product AI của nhóm. Mỗi ô có câu hỏi guide — trả lời trực tiếp, xóa phần in nghiêng khi điền.

---

## Canvas

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Câu hỏi guide** | User nào? Pain gì? AI giải quyết gì mà cách hiện tại không giải được? | Khi AI sai thì user bị ảnh hưởng thế nào? User biết AI sai bằng cách nào? User sửa bằng cách nào? | Cost bao nhiêu/request? Latency bao lâu? Risk chính là gì? |
| **Trả lời** | Người dùng xe thường mất thời gian tra cứu và gọi hỗ trợ khi xe báo lỗi, sắp hết pin/nhiên liệu hoặc cần dịch vụ. AI giúp nhận diện tình huống, giải thích vấn đề, đề xuất hướng xử lý và hỗ trợ đặt dịch vụ ngay trong ứng dụng. | AI có thể gợi ý sai mức độ nghiêm trọng hoặc hành động chưa phù hợp. User cần thấy gợi ý rõ ràng, có thể sửa nhanh tình trạng thực tế, và luôn có tùy chọn gọi tổng đài/kỹ thuật viên. Với trường hợp rủi ro cao, hệ thống phải chuyển sang con người. | Có thể triển khai bằng cách kết hợp rule engine, knowledge base và AI hội thoại. Latency mục tiêu 1–3 giây, cost thấp nếu chỉ dùng AI ở bước hiểu ngôn ngữ và diễn giải. Risk chính là chẩn đoán sai, dữ liệu xe không đủ chính xác, và khuyến nghị không đồng bộ với quy trình kỹ thuật. |

---

## Automation hay augmentation?

☐ Automation — AI làm thay, user không can thiệp

◼ Augmentation — AI gợi ý, user quyết định cuối cùng

**Justify:** ___
Đây nên là bài toán augmentation hơn là automation, vì các tình huống lỗi xe có độ rủi ro cao
user vẫn cần quyền quyết định ở bước cuối
AI phù hợp nhất để rút ngắn thời gian hiểu vấn đề và đề xuất next action
các hành động như đặt lịch, gọi cứu hộ, tới trạm sạc nên để user xác nhận


---

## Learning signal

| # | Câu hỏi | Trả lời |
|---|---------|---------|
| 1 | User correction đi vào đâu? | Mỗi lần user sửa tình huống, đổi hành động hoặc từ chối gợi ý, hệ thống ghi correction log để cải thiện phân loại sự cố, ranking hành động tiếp theo và cập nhật knowledge base/rule xử lý. |
| 2 | Product thu signal gì để biết tốt lên hay tệ đi? | Implicit: acceptance rate, click-through vào hành động gợi ý, booking rate, rescue rate sau gợi ý, repeat contact rate. Explicit: thumbs down, báo “gợi ý không đúng”. Correction: user sửa loại sự cố hoặc chọn hành động khác. Outcome: sự cố có được giải quyết không, có phải kéo xe/cứu hộ không, có quay lại xưởng sau đó không.|
| 3 | Data thuộc loại nào? ☐ User-specific · ☐ Domain-specific · ☐ Real-time · ☐ Human-judgment · ☐ Khác: ___ | *User-specific + Real-time + Human-judgment* |

**Có marginal value không?** Có. Model nền không có dữ liệu proprietary về mã lỗi, trạng thái xe real-time, workflow dịch vụ và outcome thực tế. Data này khó đối thủ bên ngoài thu thập đầy đủ, nên tạo lợi thế rõ nhất ở triage, next-best-action, personalization và safety escalation.
___

