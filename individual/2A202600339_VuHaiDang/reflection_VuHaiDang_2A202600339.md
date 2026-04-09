# Individual reflection — Vũ Hải Đăng (2A202600339)

## 1. Role  
Backend Developer & Prompt Engineer. Phụ trách xây dựng core logic cho ReAct Agent chatbot, thiết kế system prompts và phát triển các tools phục vụ cho trợ lý NEO.

---

## 2. Đóng góp cụ thể  
- Thiết kế và triển khai kiến trúc ReAct Agent sử dụng `LangGraph` (`backend/agent/graph.py`, `state.py`).  
- Tích hợp mô hình LLM vào LangGraph, thiết lập cơ chế **Tool Binding (Function Calling)** để Agent có thể tự quyết định khi nào cần gọi tool.  
- Phát triển tool `parts_store_lookup.py` để tìm cửa hàng linh kiện gần nhất dựa trên tên linh kiện được trích xuất từ user input, đồng thời hợp nhất logic từ các phần của Huy và Sơn.  
- Tối ưu hệ thống `prompts.py` nhằm kiểm soát hành vi của LLM:  
  - Không tự suy đoán linh kiện khi input không rõ ràng  
  - Buộc Agent phải hỏi lại để thu thập thêm context trước khi gọi tool  

---

## 3. SPEC mạnh/yếu  

- **Mạnh nhất:**  
  Chatbot có khả năng **hỗ trợ 24/7**, giải quyết painpoint của các kênh hỗ trợ truyền thống (phụ thuộc hotline, thời gian chờ).Hệ thống xử lý tốt **failure mode (LLM Hallucination)** trong flow bảo dưỡng. Khi người dùng đưa input mơ hồ (ví dụ: “xe cần bảo dưỡng”), Agent không vội gọi tool mà được thiết kế để đánh giá độ rõ ràng của request, sau đó yêu cầu người dùng cung cấp thêm thông tin (ví dụ: chọn loại phụ tùng). Điều này giúp giảm đáng kể việc sinh ra thông tin sai nhưng vẫn giữ trải nghiệm hội thoại tự nhiên.  

- **Yếu nhất:**  
  Chưa có thước đo cụ thể về thời gian và chi phí để đánh giá cost–benefit một cách rõ ràng. Phần demo agent vẫn còn mang tính thử nghiệm: prompt chưa được test đầy đủ, dữ liệu chủ yếu là mock và chưa tích hợp hoàn chỉnh việc gọi tools với dữ liệu thực, nên chưa thể phản ánh chính xác hiệu quả thực tế của hệ thống.

---

## 4. Đóng góp khác  
- Tham gia làm rõ ý tưởng và pain point của bài toán.  
- Thiết kế slide phiên bản đầu (ver-1).

---

## 5. Điều học được  

- **Hiểu sâu cơ chế ReAct (Reason – Act):**  
  Qua quá trình triển khai với LangGraph, tôi nắm rõ cách LLM vận hành theo chuỗi *Thought → Action → Observation* và cách điều chỉnh suy luận dựa trên phản hồi từ tool, thay vì chỉ gọi API theo flow cố định. Đồng thời, tôi học được cách thiết kế system prompt có kiểm soát và nhận ra rằng conversation design quan trọng không kém bản thân model: một flow tốt có thể giảm đáng kể hallucination và cải thiện rõ rệt trải nghiệm người dùng.

- **Quản lý Scope (Scope Creep):**  
  Ban đầu dự định phát triển feature **Smart Trip Planner Agent** (tính toán lộ trình thông minh, đề xuất điểm dừng/sạc). Tuy nhiên do hạn chế thời gian, nhóm đã thu hẹp scope và tập trung vào các tool cốt lõi như `charging_station` và `parts_store` để đảm bảo hệ thống hoạt động ổn định trong phạm vi MVP.

---

## 6. Nếu làm lại  
- Xây dựng SPEC chi tiết và rõ ràng từ đầu.  
- Xác định kiến trúc agent ngay từ đầu (rõ ràng input/output và vai trò từng component) thay vì vừa phát triển vừa điều chỉnh.  
- Thiết lập hệ thống đánh giá sớm (test case, metric) để tránh việc demo mang tính cảm tính.  

---

## 7. AI giúp gì / AI sai gì  

- **Giúp:**  
  AI  hỗ trợ tốt trong việc tạo sample data có tính thực tế cao (tên linh kiện, thương hiệu, địa chỉ, khoảng cách), giúp nhanh chóng xây dựng dataset mock up kiểm thử cho `parts_store_lookup.py`.  Ngoài ra, AI còn giúp generate nhanh prompt, flow và ý tưởng, từ đó tăng tốc đáng kể quá trình thiết kế hệ thống.

- **Sai / Mislead:**  
  AI đôi khi đề xuất flow không thực tế, khó implement trong phạm vi dự án.  Ngoài ra, code sinh ra không hoàn toàn tương thích với system hiện tại, cần chỉnh sửa đáng kể để integrate.