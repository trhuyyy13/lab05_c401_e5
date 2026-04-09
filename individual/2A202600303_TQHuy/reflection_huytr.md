# Individual reflection — Trần Quang Huy (2A202600303) - Per1

## 1. Role
- UI + UX + prompt engineer. Phụ trách thiết kế luồng chức năng và agent tự động khi VinFast gặp cảnh báo các lỗi của xe
- Team chia thành 3 nhóm chính: ChatBot AI (Đăng + Tuấn), Error Agent (Huy + Sơn), Battery Warnings (Đạt + Dũng). Cùng với mem Sơn hoàn thiện agent.

## 2. Đóng góp cụ thể
- Đưa ra bài toán và xác định vấn đề: Phân tích yêu cầu của dự án VinFast AI Assistant, xác định cần chatbot cho EV với agent tự động.
- Xây dựng luồng agent thân thiện với người dùng: Thiết kế conversation flow đơn giản (hỏi lỗi → gợi ý giải pháp), tập trung vào UX để người dùng dễ tương tác.
- Thiết kế UX cho mobile app, bao gồm giao diện chat, luồng tương tác, và poster layout cho demo.
- Phát triển frontend chatbot với HTML/CSS/JS, tích hợp onclick handlers.

## 3. SPEC mạnh/yếu
- Mạnh nhất: Pain point nhóm đặt ra rất thực tế -> Và có đưa giải pháp giải quyết được vấn đề của user
- Yếu nhất: ROI -> Chưa có thước đo vể thời gian để tính cost, benefit cho ROI. Phần demo agent — chưa test prompt đầy đủ, mock còn nhiều, chưa gọi tools lấy data thật..

## 4. Đóng góp khác
- Viết prompt cho agent để cải thiện phản hồi.
- Giúp debug giao diện và luồng, đảm bảo tương tác mượt mà.
- Cùng với Sơn làm backend và agent logic.

## 5. Điều học được
Trước dự án nghĩ nghiệp vụ xe điện chỉ là kỹ thuật cơ bản. Sau khi thiết kế agent cho VinFast mới hiểu tầm quan trọng của việc hiểu domain EV trước khi code, và cách xây dựng luồng thân thiện để tăng trải nghiệm người dùng. Cũng học được cách collab với teammate để phân chia task hiệu quả.

## 6. Nếu làm lại
Sẽ test agent sớm hơn — ngày đầu chỉ thiết kế spec, đến giữa dự án mới bắt đầu demo. Nếu test sớm thì có thể iterate tốt hơn.

## 7. AI giúp gì / AI sai gì
- **Giúp:** Dùng AI để brainstorm ý tưởng cho luồng agent và code frontend.
- **Sai/mislead:** AI gợi ý feature phức tạp, suýt scope creep. Bài học: AI tốt cho ý tưởng nhưng cần kiểm soát scope.
