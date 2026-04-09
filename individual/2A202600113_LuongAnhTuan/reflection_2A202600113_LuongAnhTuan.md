# Individual reflection - Lương Anh Tuấn (2A202600113)

## 1. Role
- Agent designer, UX designer . Phụ trách thiết kế flow agent chatbot, hội thoại.
- Team chia thành 3 nhóm chính: ChatBot AI (Đăng + Tuấn), Error Agent (Huy + Sơn), Battery Warnings (Đạt + Dũng).

## 2. Đóng góp cụ thể
- Thiết kế conversation flow end-to-end: user input → intent detection → function calling → response → feedback loop.
- Thiết kế agent interaction giữa Chatbot AI – Error Agent – Battery Agent (phân vai rõ ràng, dễ mở rộng).
- Xây dựng system prompt có kiểm soát: giới hạn domain, xử lý fallback, định nghĩa khi nào gọi tool vs trả lời trực tiếp.
- Thiết kế UX chatbot: hiển thị confidence, multiple options (low-confidence), CTA rõ ràng cho next action.

## 3. SPEC mạnh/yếu
- Mạnh nhất: Flow thiết kế rõ ràng theo 4 paths (happy / low-confidence / failure / correction) → sát thực tế, dễ implement và eval. Định hướng đúng augmentation (không automation) → đảm bảo safety cho bài toán có rủi ro cao.
- Yếu nhất: Data layer còn yếu (mock data, thiếu real-time) → khó validate giá trị thực. Evaluation chưa đủ sâu: thiếu test set, edge cases, offline benchmark. Thiếu thiết kế chi tiết cho fallback sang human / escalation flow.

## 4. Đóng góp khác
- Hỗ trợ merge code, fix bug cross-team, đảm bảo flow end-to-end chạy được
- Tham gia refine problem & solution, tránh over-engineering.
- Align giữa các nhóm (Chatbot – Error – Battery) để flow thống nhất.

## 5. Điều học được
- Thiết kế agent architecture upfront cực kỳ quan trọng → quyết định khả năng scale và maintain.
- Conversation design ≈ model quality: flow tốt giúp giảm hallucination và tăng UX đáng kể.
- Hiểu rõ hơn về function calling strategy:: biết khi nào nên gọi tool, khi nào nên trả lời trực tiếp.
- Học cách viết system prompt có kiểm soát (scope, fallback, refusal).
- Hiểu trade-off giữa demo nhanh vs hệ thống thực tế (mock data vs real data, UX vs độ chính xác).

## 6. Nếu làm lại
- Define agent architecture sớm (ai làm gì, input/output) thay vì vừa làm vừa chỉnh.
- Làm evaluation sớm (test case, metric) để không bị “cảm tính” khi demo.
- Làm rõ AI value vs non-AI solution (tại sao cần AI, không chỉ là UI đẹp hơn).
- Đầu tư vào feedback loop + data pipeline (log → validate → update model/KB).
- Thiết kế rõ fallback & escalation (AI → human) cho các case critical.

## 7. AI giúp gì / AI sai gì
- **Giúp:** Tăng tốc thiết kế: generate prompt, flow, idea nhanh. Hỗ trợ implement: function calling, API integration, boilerplate code. Mở rộng tư duy: gợi ý nhiều hướng tiếp cận.

- **Sai/mislead:** Đề xuất over-engineering (flow phức tạp nhưng không cần thiết cho demo). Code sinh ra không consistent với system hiện tại, cần chỉnh lại nhiều. Một số giải pháp không thực tế với constraint (latency, data, infra).
