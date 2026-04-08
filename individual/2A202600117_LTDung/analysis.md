# # UX Exercise — MoMo Moni AI (Refined)

## Sản phẩm: MoMo — Moni AI Assistant (Phân loại chi tiêu tự động)

---

## 1. Phân tích 4 Paths (Trọng tâm: Auto-tagging)

### 1. AI Đúng (Confidence > 90%)
- **Scenario:** User thanh toán 35k tại Highland Coffee.
- **AI Action:** Tự động gán nhãn **"Ăn uống"**.
- **UI/UX:** Hiển thị tag gọn gàng dưới số tiền. Không làm phiền user.
- **Cảm giác:** Tiện lợi, "nó hiểu mình".

### 2. AI Không Chắc (Confidence 40-70%)
- **Scenario:** User chuyển khoản 2tr cho một cá nhân với nội dung "tien nha".
- **AI Action:** Không gán nhãn cứng.
- **UI/UX:** Hiển thị gợi ý dạng câu hỏi: *"Đây có phải 'Nhà cửa/Tiền thuê' không?"* kèm nút **[Đúng] / [Phân loại khác]**.
- **Cải tiến:** Chuyển từ bị động (chờ user tự vào chỉnh) sang chủ động hỏi (1-touch).

### 3. AI Sai (Confidence cao nhưng nhầm context)
- **Scenario:** Mua đồ điện tử trên Shopee để tặng quà, nhưng AI mặc định tag **"Mua sắm"**. User muốn đổi thành **"Biếu tặng"**.
- **UX Pain:** User sửa xong nhưng không biết AI có học không. Tháng sau mua lại vẫn bị tag sai.
- **To-be Fix:** Khi user sửa category, AI hiện thông báo: *"Đã ghi nhớ. Từ giờ các giao dịch từ Shopee sẽ được hỏi/gán vào mục 'Biếu tặng' cho riêng bạn"*.

### 4. User Mất Niềm Tin (Hồi phục lòng tin)
- **Scenario:** AI liên tục tag sai các khoản chuyển tiền nội bộ thành "Thu nhập". User cảm thấy báo cáo tháng bị rác.
- **UX Solution:** - Thêm nút **"Undo AI"**: Khôi phục trạng thái chưa phân loại cho toàn bộ giao dịch trong ngày.
    - Chế độ **"Duyệt hàng loạt"**: Cuối tuần gom các mục AI đã gán để user quẹt trái/phải xác nhận nhanh.

---

## 2. Path yếu nhất: Recovery Flow (Khi AI sai)
- **Vấn đề:** Hiện tại việc sửa lỗi mất quá nhiều bước (3-4 clicks). 
- **Giải pháp:** Cung cấp "Quick-fix" ngay tại màn hình Dashboard báo cáo. Cho phép thay đổi Category của nhiều giao dịch tương tự cùng lúc (Batch editing).

---

## 3. Gap Marketing vs Thực tế
- **Marketing:** "Quản lý tài chính tự động, không tốn một giây".
- **Thực tế:** Auto-tag chỉ đúng ~70% với các Merchant lớn. Các giao dịch chuyển khoản (P2P) vẫn là vùng tối.
- **Gap lớn nhất:** AI chưa có tính "cá nhân hóa" (Personalization). Nếu tôi coi việc mua game là "Học tập", AI không nên ép tôi đó là "Giải trí".

---

## 4. Sketch To-Be (Logic tinh chỉnh)

| Step | Luồng Hiện Tại (As-is) | Luồng Đề Xuất (To-be) |
|---|---|---|
| **Phân loại** | Auto-tag im lặng (dễ sai) | Gán nhãn kèm chỉ số tin cậy ngầm |
| **Xác nhận** | Không có | Nếu AI không chắc -> Hiện pop-up "Confirm" nhẹ |
| **Sửa lỗi** | Vào sâu từng giao dịch (vất vả) | Sửa 1 chỗ, áp dụng cho tất cả giao dịch tương tự |
| **Học tập** | Không rõ ràng | Hiện xác nhận: **"Moni đã học được thói quen này!"** |

---

## 5. Mini AI Spec
- **Input:** `Transaction_Desc`, `Amount`, `Merchant_Metadata`, `User_History_Correction`.
- **Core Logic:** Ưu tiên dữ liệu đã sửa của chính User đó (User-specific logic) hơn là logic chung của hệ thống.
- **Constraint:** Nếu `Confidence < 50%`, tuyệt đối không gán nhãn cứng, chỉ để ở trạng thái "Chờ duyệt".

---
*Moni AI — Tinh chỉnh trải nghiệm AI thực chiến — 2026*