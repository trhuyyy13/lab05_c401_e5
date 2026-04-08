# ROI 3 kịch bản
Ước lượng ROI cho 3 trường hợp: conservative, realistic, optimistic. Không cần chính xác — quan trọng là tư duy "có đáng build không?"

## Giả định chung
- Sản phẩm: hệ thống hỗ trợ thông minh cho người dùng xe (chẩn đoán, gợi ý hành động, đặt dịch vụ)
- Giá trị chính: tiết kiệm thời gian + giảm phụ thuộc tổng đài + tăng sử dụng dịch vụ hệ sinh thái
- Quy đổi: 1 giờ user ≈ $5 (ước lượng trung bình)

---

## ROI

|   | Conservative | Realistic | Optimistic |
|---|-------------|-----------|------------|
| **Assumption** | 1,000 user, 30% dùng thường xuyên, mỗi user tiết kiệm 5 phút/ngày | 5,000 user, 50% dùng, tiết kiệm 10 phút/ngày | 20,000 user, 70% dùng, tiết kiệm 15 phút/ngày |
| **Cost** | $100/ngày (API + infra cơ bản) | $300/ngày | $800/ngày |
| **Benefit** | ~25 giờ/ngày → ~$125/ngày | ~416 giờ/ngày → ~$2,080/ngày | ~3,500 giờ/ngày → ~$17,500/ngày |
| **Net** | +$25/ngày | +$1,780/ngày | +$16,700/ngày |

---

## Kill criteria

- Adoption rate <30% sau 2 tháng  
- Task success rate <60% → user không hoàn thành được mục tiêu  
- Cost > Benefit trong 2 tháng liên tiếp  
- Escalation rate >50% → AI không giảm tải được cho hệ thống hỗ trợ  

→ Nếu chạm bất kỳ điều kiện nào trên: **dừng hoặc pivot (giảm scope / chuyển sang assist tool thay vì full automation)**