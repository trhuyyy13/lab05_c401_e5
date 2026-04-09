# SPEC — AI Product Hackathon

**Nhóm:** ___
**Track:** ☐ VinFast · ☐ Vinmec · ☐ VinUni-VinSchool · ☐ XanhSM · ☐ Open
**Problem statement (1 câu):** *Ai gặp vấn đề gì, hiện giải thế nào, AI giúp được gì*

---

## 1. AI Product Canvas

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Câu hỏi guide** | User nào? Pain gì? AI giải quyết gì mà cách hiện tại không giải được? | Khi AI sai thì user bị ảnh hưởng thế nào? User biết AI sai bằng cách nào? User sửa bằng cách nào? | Cost bao nhiêu/request? Latency bao lâu? Risk chính là gì? |
| **Trả lời** | Người dùng xe thường mất thời gian tra cứu và gọi hỗ trợ khi xe báo lỗi, sắp hết pin/nhiên liệu hoặc cần dịch vụ. AI giúp nhận diện tình huống, giải thích vấn đề, đề xuất hướng xử lý và hỗ trợ đặt dịch vụ ngay trong ứng dụng. | AI có thể gợi ý sai mức độ nghiêm trọng hoặc hành động chưa phù hợp. User cần thấy gợi ý rõ ràng, có thể sửa nhanh tình trạng thực tế, và luôn có tùy chọn gọi tổng đài/kỹ thuật viên. Với trường hợp rủi ro cao, hệ thống phải chuyển sang con người. | Có thể triển khai bằng cách kết hợp rule engine, knowledge base và AI hội thoại. Latency mục tiêu 1–3 giây, cost thấp nếu chỉ dùng AI ở bước hiểu ngôn ngữ và diễn giải. Risk chính là chẩn đoán sai, dữ liệu xe không đủ chính xác, và khuyến nghị không đồng bộ với quy trình kỹ thuật. |

**Automation hay augmentation?** 
☐ Automation — AI làm thay, user không can thiệp

◼ Augmentation — AI gợi ý, user quyết định cuối cùng

**Justify:** ___
Đây nên là bài toán augmentation hơn là automation, vì các tình huống lỗi xe có độ rủi ro cao
user vẫn cần quyền quyết định ở bước cuối
AI phù hợp nhất để rút ngắn thời gian hiểu vấn đề và đề xuất next action
các hành động như đặt lịch, gọi cứu hộ, tới trạm sạc nên để user xác nhận

**Learning signal:**

| # | Câu hỏi | Trả lời |
|---|---------|---------|
| 1 | User correction đi vào đâu? | Mỗi lần user sửa tình huống, đổi hành động hoặc từ chối gợi ý, hệ thống ghi correction log để cải thiện phân loại sự cố, ranking hành động tiếp theo và cập nhật knowledge base/rule xử lý. |
| 2 | Product thu signal gì để biết tốt lên hay tệ đi? | Implicit: acceptance rate, click-through vào hành động gợi ý, booking rate, rescue rate sau gợi ý, repeat contact rate. Explicit: thumbs down, báo “gợi ý không đúng”. Correction: user sửa loại sự cố hoặc chọn hành động khác. Outcome: sự cố có được giải quyết không, có phải kéo xe/cứu hộ không, có quay lại xưởng sau đó không.|
| 3 | Data thuộc loại nào? ☐ User-specific · ☐ Domain-specific · ☐ Real-time · ☐ Human-judgment · ☐ Khác: ___ | *User-specific + Real-time + Human-judgment* |

**Có marginal value không?** Có. Model nền không có dữ liệu proprietary về mã lỗi, trạng thái xe real-time, workflow dịch vụ và outcome thực tế. Data này khó đối thủ bên ngoài thu thập đầy đủ, nên tạo lợi thế rõ nhất ở triage, next-best-action, personalization và safety escalation.



## 2. User Stories — 4 paths

Mỗi feature chính = 1 bảng. AI trả lời xong → chuyện gì xảy ra?
### Feature 1: Nhận diện sự cố / nhu cầu từ user input

**Trigger:** User nhập mô tả (“xe báo lỗi E12”, “xe sắp hết pin”) hoặc gửi ảnh/log → AI phân tích → xác định vấn đề

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| **Happy** — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | User nhập “xe báo lỗi E12” → AI nhận diện lỗi pin (confidence 92%) → hiển thị lỗi, mô tả, mức độ nguy hiểm → CTA “Tìm garage phù hợp” |
| **Low-confidence** — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | User nhập “xe hơi yếu” → AI không chắc (confidence 60%) → hiển thị 2 khả năng (pin / động cơ) + câu hỏi làm rõ → user chọn |
| **Failure** — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | AI hiểu sai lỗi → user thấy mô tả không đúng → bấm “Không đúng” → hệ thống yêu cầu nhập lại hoặc chọn từ danh sách |
| **Correction** — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | User chọn lại lỗi đúng → hệ thống log (input + prediction + correction) → dùng để cải thiện model |

---

### Feature 2: Hướng dẫn xử lý theo tình huống

**Trigger:** Sau khi nhận diện vấn đề → AI đưa ra hướng dẫn từng bước

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| **Happy** | User thấy gì? Flow kết thúc ra sao? | AI đưa checklist xử lý (dừng xe, kiểm tra, xử lý) → user làm theo → xác nhận “đã xử lý xong” |
| **Low-confidence** | System báo bằng cách nào? | AI không chắc nguyên nhân → hiển thị nhiều phương án xử lý → user chọn tình huống phù hợp |
| **Failure** | User biết sai bằng cách nào? | User làm theo nhưng không hiệu quả → bấm “Không hiệu quả” → hệ thống đề xuất phương án khác hoặc gọi hỗ trợ |
| **Correction** | User sửa bằng cách nào? Data đi vào đâu? | User feedback “hướng dẫn không phù hợp” → hệ thống lưu mismatch → cải thiện recommendation |

---

### Feature 3: Gợi ý hành động tiếp theo

**Trigger:** Sau khi hiểu vấn đề → AI đề xuất action (trạm sạc, trạm xăng, cứu hộ, bảo dưỡng)

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| **Happy** | User thấy gì? Flow kết thúc ra sao? | AI đề xuất danh sách trạm gần nhất + ETA → user chọn → mở bản đồ điều hướng |
| **Low-confidence** | System báo bằng cách nào? | AI không chắc ưu tiên → hiển thị nhiều option (gần nhất, nhanh nhất, ít đông) → user chọn |
| **Failure** | User biết sai bằng cách nào? | Trạm đề xuất không hoạt động → user đến nơi phát hiện lỗi → quay lại app báo “không khả dụng” |
| **Correction** | User sửa bằng cách nào? Data đi vào đâu? | User report trạm lỗi → hệ thống cập nhật dữ liệu real-time → cải thiện ranking |

---

### Feature 4: Thực hiện hành động (đặt lịch / gọi dịch vụ)

**Trigger:** User chọn action → AI hỗ trợ thực hiện (đặt lịch sửa xe, gọi cứu hộ…)

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| **Happy** | User thấy gì? Flow kết thúc ra sao? | AI auto điền thông tin → user xác nhận → nhận lịch hẹn / yêu cầu thành công |
| **Low-confidence** | System báo bằng cách nào? | AI thiếu thông tin → hỏi thêm (loại dịch vụ, thời gian) → user cung cấp |
| **Failure** | User biết sai bằng cách nào? | Thông tin đặt sai → user thấy ở màn confirm → chỉnh sửa trước khi submit |
| **Correction** | User sửa bằng cách nào? Data đi vào đâu? | User chỉnh thông tin → hệ thống lưu preference → dùng cho lần sau |


---

## 3. Eval metrics + threshold
### Precision hay recall?

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

### Metrics table

| Metric | Threshold | Red flag (dừng khi) |
|--------|-----------|---------------------|
| Action recommendation precision | ≥92% (critical), ≥85% (non-critical) | <85% (critical) → nguy hiểm |
| Task success rate | ≥80% | <65% → flow không usable |
| User satisfaction | ≥4/5 | <3/5 trong 2 tuần |
---

## 4. Top 3 failure modes


| # | Trigger | Hậu quả | Mitigation |
|---|---------|---------|------------|
| 1 | Hệ thống **hiểu sai tình trạng xe** (ví dụ: đọc sai sensor, hoặc NLP hiểu sai mô tả của user) | Gợi ý hành động sai (ví dụ: tiếp tục đi khi xe sắp hết pin / lỗi phanh) — **user không biết bị sai**, có thể gây nguy hiểm | Confidence score + uncertainty detection. Nếu dưới ngưỡng → fallback: yêu cầu xác nhận thêm (triệu chứng, ảnh, log xe) hoặc đề xuất liên hệ hỗ trợ |
| 2 | **Dữ liệu dịch vụ không cập nhật** (trạm sạc hết chỗ, cây xăng đóng cửa, gara không hoạt động) | User di chuyển đến địa điểm không khả dụng → mất thời gian, có thể bị kẹt giữa đường | Real-time data sync + verify availability (API / crowdsourcing). Hiển thị trạng thái (open/close, availability). Luôn đưa ≥2 phương án dự phòng |
| 3 | **Automation hành động sai** (auto đặt lịch sửa chữa / gọi cứu hộ không đúng nhu cầu) | Phát sinh chi phí không cần thiết hoặc delay xử lý vấn đề thực → **đã xảy ra rồi mới biết** | Human-in-the-loop: yêu cầu confirm trước action quan trọng. Delay + undo (30–60s). Hiển thị rõ thông tin trước khi thực hiện (giá, địa điểm, thời gian) |

---


---

## 5. ROI 3 kịch bản


Ước lượng ROI cho 3 trường hợp: conservative, realistic, optimistic. Không cần chính xác — quan trọng là tư duy "có đáng build không?"

### Giả định chung
- Sản phẩm: hệ thống hỗ trợ thông minh cho người dùng xe (chẩn đoán, gợi ý hành động, đặt dịch vụ)
- Giá trị chính: tiết kiệm thời gian + giảm phụ thuộc tổng đài + tăng sử dụng dịch vụ hệ sinh thái
- Ước tính 2025 Vinfast phải đối mặt với 5000 ca sự cố ô tô và 20000-25000 ca với xe máy điện các dòng. Con số này sẽ tăng cao hơn trong tương lai khi số lượng và tuổi thọ xe cao hơn.

---

### ROI

|   | Conservative | Realistic | Optimistic |
|---|-------------|-----------|------------|
| **Assumption** | 1,000 user,  mỗi user tiết kiệm 3-4 tiếng/sự cố | 5,000 user, tiết kiệm 3-4 tiếng/sự cố | 50,000 user, 3-4 tiếng/sự cố|
| **Cost** | ? | ? | ? |
| **Benefit** | ~250 giờ/tháng | ~900 giờ/tháng| ~9000 giờ/tháng |

---

### Kill criteria

- Adoption rate <30% sau 2 tháng  
- Task success rate <60% → user không hoàn thành được mục tiêu  
- Satisfaction rate <2 sau 2 tháng 

→ Nếu chạm bất kỳ điều kiện nào trên: **dừng hoặc pivot (giảm scope / chuyển sang assist tool thay vì full automation)


## 6. Prototype
- Prototype mô phỏng cách hệ thống tiếp nhận cảnh báo từ xe hoặc từ input của người dùng, hỗ trợ người dùng hiểu vấn đề, đề xuất hướng xử lý phù hợp và liên tục cải thiện chất lượng hỗ trợ thông qua phản hồi thực tế từ người dùng.

- Các bước trong prototype:

Step 1: Hệ thống nhận cảnh báo từ xe, như lỗi kỹ thuật, pin sắp hết hoặc cần bảo dưỡng 

Step 2: Ứng dụng hiển thị thông báo kèm hai lựa chọn: Bỏ qua hoặc Đi tới hỗ trợ.

Step 3: Nếu người dùng chọn hỗ trợ, AI sẽ giải thích ngắn gọn vấn đề, mức độ nghiêm trọng và việc nên làm ngay.

Step 4: Hệ thống đề xuất hành động phù hợp như đi tới trạm sạc, gọi tổng đài, gọi cứu hộ hoặc đặt lịch dịch vụ.

Step 5: Người dùng thực hiện trực tiếp trong app, giúp quá trình xử lý nhanh và liền mạch hơn.

Step 6: Sau khi nhận hỗ trợ, người dùng gửi phản hồi về chất lượng gợi ý, như mức độ chính xác, hữu ích và mức độ hài lòng.

Step 7: Một agent trong hệ thống sẽ kiểm tra và xác minh lại phản hồi cùng kết quả xử lý thực tế; sau khi được xác thực, thông tin này sẽ được bổ sung vào knowledge base để cải thiện các lần hỗ trợ sau.
## 7. Mini AI spec (1 trang)


### Bài toán
- Người dùng xe thường mất thời gian hiểu cảnh báo, tìm cách xử lý và liên hệ hỗ trợ
- AI giúp:
  - nhận diện vấn đề
  - giải thích ngắn gọn
  - gợi ý hành động phù hợp
  - hỗ trợ thực hiện ngay trong app

### Người dùng
- Người dùng xe trong hệ sinh thái
- Đặc biệt hữu ích khi:
  - không hiểu mã lỗi
  - cần xử lý nhanh
  - đang ở tình huống khẩn cấp

### Vai trò của AI
- Nhận input từ:
  - mô tả user
  - ảnh / log / cảnh báo từ xe
  - dữ liệu real-time
- Đầu ra:
  - vấn đề đang xảy ra
  - mức độ nghiêm trọng
  - hành động tiếp theo phù hợp

### Automation hay augmentation
- **Augmentation**
- AI chỉ gợi ý, user quyết định cuối cùng
- Các action quan trọng như gọi cứu hộ, đặt lịch dịch vụ vẫn cần xác nhận

### Chất lượng cần đạt
- Critical flows: ưu tiên **precision**
- Non-critical flows: ưu tiên **recall**
- Mục tiêu:
  - intent accuracy >= 90%
  - critical precision >= 92%
  - latency < 2s

### Risk chính
- Hiểu sai tình trạng xe
- Dữ liệu dịch vụ không cập nhật
- Gợi ý / thực hiện action sai

### Mitigation
- Confidence score + hỏi lại khi không chắc
- Fallback sang tổng đài / kỹ thuật viên
- Real-time data sync
- Bắt buộc confirm trước action quan trọng

### Data flywheel
- User accept / reject / sửa gợi ý
- Hệ thống lưu correction + outcome
- Dùng để cải thiện:
  - phân loại sự cố
  - ranking hành động
  - knowledge base
  - personalization

### Kết luận
- Đây là AI assistant hỗ trợ xử lý sự cố xe
- Giá trị chính:
  - nhanh hơn cho user
  - giảm tải hỗ trợ
  - tăng sử dụng dịch vụ hệ sinh thái
- Nên build theo hướng **AI hỗ trợ, không full automation**
*Tóm tắt tự do — viết bằng ngôn ngữ tự nhiên, không format bắt buộc.*
*Gom lại: product giải gì, cho ai, AI làm gì (auto/aug), quality thế nào (precision/recall), risk chính, data flywheel ra sao.*

# PHÂN CÔNG Lab 05
| Mục | Nội dung chính | Người phụ trách |
|-----|----------------|-----------------|
| 1 | **AI Product Canvas**: xác định user, pain point, AI value, trust, feasibility, learning signal, loại data và marginal value của sản phẩm | Sơn |
| 2 | **User Stories — 4 paths**: mô tả các flow chính của sản phẩm theo 4 case gồm happy path, low-confidence, failure, correction cho từng feature | Đăng |
| 3 | **Eval Metrics + Threshold**: xác định ưu tiên precision/recall, các metric chính, ngưỡng đạt và red flag để đánh giá chất lượng hệ thống | Tuấn |
| 4 | **Top 3 Failure Modes**: liệt kê 3 lỗi nghiêm trọng nhất, hậu quả và cách giảm thiểu rủi ro | Dũng |
| 5 | **ROI — 3 kịch bản**: ước lượng cost, benefit, net value theo 3 mức conservative / realistic / optimistic và kill criteria | Đạt |
| 6 | **Prototype**: mô phỏng luồng hệ thống từ khi nhận cảnh báo, hỗ trợ user, đề xuất action, thực hiện action và thu feedback | Huy |
| 7 | **Mini AI Spec**: tóm tắt ngắn gọn sản phẩm giải gì, cho ai, AI làm gì, augmentation hay automation, quality, risk và data flywheel | Huy |