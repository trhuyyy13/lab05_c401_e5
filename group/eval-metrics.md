# Eval metrics + threshold

## Precision hay recall?

☑ Precision — khi AI nói "có" thì thực sự đúng (ít false positive)  

☑ Recall — tìm được hết những cái cần tìm (ít false negative)

👉 Chọn hybrid nhưng ưu tiên Precision trong tình huống critical

---

**Tại sao?**  
- Với các tình huống **nguy hiểm hoặc ảnh hưởng lớn** (lỗi kỹ thuật, cảnh báo pin/nhiên liệu), cần **precision cao** để tránh hướng dẫn sai gây rủi ro.  
- Với các tình huống **dịch vụ và tiện ích** (tìm trạm sạc, bảo dưỡng), cần **recall cao** để không bỏ sót phương án cho người dùng.  

→ Vì vậy:  
- Critical flows → Precision-first  
- Non-critical flows → Recall-first  

---

**Nếu sai ngược lại thì sao?**  
- Nếu precision thấp: gợi ý sai → mất niềm tin, có thể nguy hiểm  
- Nếu recall thấp: không tìm ra giải pháp → user phải tự xử lý → hệ thống mất giá trị  

---

## Metrics table

| Metric | Threshold | Red flag (dừng khi) |
|--------|-----------|---------------------|
| Intent detection accuracy | ≥90% | <80% → hiểu sai nhu cầu user |
| Action recommendation precision | ≥92% (critical), ≥85% (non-critical) | <85% (critical) → nguy hiểm |
| Service recall | ≥90% | <75% → bỏ sót nhiều |
| Task success rate | ≥80% | <65% → flow không usable |
| Escalation rate | <25% | >40% → AI chưa đủ tốt |
| Latency | <2s | >4s → UX kém |
| User satisfaction | ≥4/5 | <3/5 trong 2 tuần |

---