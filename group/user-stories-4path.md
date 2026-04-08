# User stories — 4 paths

Mỗi feature AI chính = 1 bảng. AI trả lời xong → chuyện gì xảy ra? Viết cả 4 trường hợp.

---

## Feature 1: Nhận diện sự cố / nhu cầu từ user input

**Trigger:** User nhập mô tả (“xe báo lỗi E12”, “xe sắp hết pin”) hoặc gửi ảnh/log → AI phân tích → xác định vấn đề

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| **Happy** — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | User nhập “xe báo lỗi E12” → AI nhận diện lỗi pin (confidence 92%) → hiển thị lỗi, mô tả, mức độ nguy hiểm → CTA “Tìm trạm sạc gần nhất” |
| **Low-confidence** — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | User nhập “xe hơi yếu” → AI không chắc (confidence 60%) → hiển thị 2 khả năng (pin / động cơ) + câu hỏi làm rõ → user chọn |
| **Failure** — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | AI hiểu sai lỗi → user thấy mô tả không đúng → bấm “Không đúng” → hệ thống yêu cầu nhập lại hoặc chọn từ danh sách |
| **Correction** — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | User chọn lại lỗi đúng → hệ thống log (input + prediction + correction) → dùng để cải thiện model |

---

## Feature 2: Hướng dẫn xử lý theo tình huống

**Trigger:** Sau khi nhận diện vấn đề → AI đưa ra hướng dẫn từng bước

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| **Happy** | User thấy gì? Flow kết thúc ra sao? | AI đưa checklist xử lý (dừng xe, kiểm tra, xử lý) → user làm theo → xác nhận “đã xử lý xong” |
| **Low-confidence** | System báo bằng cách nào? | AI không chắc nguyên nhân → hiển thị nhiều phương án xử lý → user chọn tình huống phù hợp |
| **Failure** | User biết sai bằng cách nào? | User làm theo nhưng không hiệu quả → bấm “Không hiệu quả” → hệ thống đề xuất phương án khác hoặc gọi hỗ trợ |
| **Correction** | User sửa bằng cách nào? Data đi vào đâu? | User feedback “hướng dẫn không phù hợp” → hệ thống lưu mismatch → cải thiện recommendation |

---

## Feature 3: Gợi ý hành động tiếp theo

**Trigger:** Sau khi hiểu vấn đề → AI đề xuất action (trạm sạc, trạm xăng, cứu hộ, bảo dưỡng)

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| **Happy** | User thấy gì? Flow kết thúc ra sao? | AI đề xuất danh sách trạm gần nhất + ETA → user chọn → mở bản đồ điều hướng |
| **Low-confidence** | System báo bằng cách nào? | AI không chắc ưu tiên → hiển thị nhiều option (gần nhất, nhanh nhất, ít đông) → user chọn |
| **Failure** | User biết sai bằng cách nào? | Trạm đề xuất không hoạt động → user đến nơi phát hiện lỗi → quay lại app báo “không khả dụng” |
| **Correction** | User sửa bằng cách nào? Data đi vào đâu? | User report trạm lỗi → hệ thống cập nhật dữ liệu real-time → cải thiện ranking |

---

## Feature 4: Thực hiện hành động (đặt lịch / gọi dịch vụ)

**Trigger:** User chọn action → AI hỗ trợ thực hiện (đặt lịch sửa xe, gọi cứu hộ…)

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| **Happy** | User thấy gì? Flow kết thúc ra sao? | AI auto điền thông tin → user xác nhận → nhận lịch hẹn / yêu cầu thành công |
| **Low-confidence** | System báo bằng cách nào? | AI thiếu thông tin → hỏi thêm (loại dịch vụ, thời gian) → user cung cấp |
| **Failure** | User biết sai bằng cách nào? | Thông tin đặt sai → user thấy ở màn confirm → chỉnh sửa trước khi submit |
| **Correction** | User sửa bằng cách nào? Data đi vào đâu? | User chỉnh thông tin → hệ thống lưu preference → dùng cho lần sau |

---

## Feature 5: Chủ động dự đoán & gợi ý (Optional)

**Trigger:** System theo dõi trạng thái xe → dự đoán nhu cầu → đưa ra khuyến nghị

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| **Happy** | User thấy gì? Flow kết thúc ra sao? | AI phát hiện pin sắp hết → gửi gợi ý → user click → điều hướng đến trạm |
| **Low-confidence** | System báo bằng cách nào? | AI không chắc nhu cầu → hiển thị suggestion nhẹ → user chọn ignore hoặc accept |
| **Failure** | User biết sai bằng cách nào? | AI cảnh báo không cần thiết → user dismiss → giảm trust |
| **Correction** | User sửa bằng cách nào? Data đi vào đâu? | User tắt loại thông báo → hệ thống học preference → cá nhân hóa về sau |

---

## Notes

- Luôn thiết kế đủ 4 paths: Happy / Low-confidence / Failure / Correction  
- Failure path là quan trọng nhất: user phải nhận ra AI sai  
- Correction path = nguồn data cho feedback loop  
- Không chỉ tập trung vào happy path  