
# Individual reflection — Sơn TN (Per2)

## 1. Role
- Backend + agent engineer. Phụ trách phát triển agent tự động và tích hợp tools cho chẩn đoán lỗi xe VinFast.
- Team chia thành 3 nhóm chính: ChatBot AI (Đăng + Tuấn), Error Agent (Huy + Sơn), Battery Warnings (Đạt + Dũng). Cùng với Huy hoàn thiện Error Agent.

## 2. Đóng góp cụ thể
- Đưa ra bài toán và xác định vấn đề: Phân tích yêu cầu backend cho agent, xác định cần LangGraph và tools.
- Xây dựng luồng agent thân thiện với người dùng: Phát triển logic agent để phản hồi tự nhiên, tích hợp tools như chẩn đoán lỗi.
- Viết code backend với FastAPI, tích hợp OpenAI cho agent.
- Đưa ra test case để test agent, tối ưu sản phẩm bằng cách cải thiện logic và giảm mock.

## 3. SPEC mạnh/yếu
- Mạnh nhất: Đặt ra được bài toán và đưa ra solution đề xuất giải quyết trực tiếp được pain point của người dùng
- Yếu nhất: Metrics còn chưa thật sự chặt. Phần ROI không có thang đo về "Return", chưa ước lượng được cost. Phần demo agent — chưa test prompt đầy đủ, mock còn nhiều, chưa gọi tools lấy data thật..

## 4. Đóng góp khác
- Tích hợp tools cho vehicle diagnostics và booking service.
- Debug backend và agent, ghi log cho tool calls.
- Cùng với Huy làm frontend và UX.
- Sửa lại SPEC theo feedback giáo viên

## 5. Điều học được
Kinh nghiệm merge code trong dự án có nhiều người. Cách lên kế hoạch phát triển sản phẩm thật.

## 6. Nếu làm lại
Tập trung nhiều hơn vào các phần mà AI Agent thật sự có nhiều impact. Bọn em bị sa đà vào việc làm 1 cái luồng thật mượt dành cho user trong khi phần chat bot thì không làm thật sự kĩ. Điều này cũng một phần là vì hơi khó để có đủ knowledge cụ thể để cung cấp cho Agent về mảng nay.

## 7. AI giúp gì / AI sai gì
- **Giúp:** Dùng AI để code snippets cho LangGraph và brainstorm test case.
- **Sai/mislead:** AI gợi ý tools không phù hợp EV, lúc vibe flow nhiều chỗ bị lủng củng/lặp lại vô nghĩa