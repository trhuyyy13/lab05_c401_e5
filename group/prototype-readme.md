# Prototype — NEO VinFast AI Assistant

## Mô tả
Trợ lý AI cho xe điện VinFast: nhận cảnh báo lỗi, hướng dẫn tự xử lý, tìm gara gần nhất, tìm trạm sạc và đặt lịch dịch vụ. Giao diện mobile-style, backend FastAPI + agent LangGraph ReAct.

## Level: Prototype
- UI: HTML/CSS/JS (mobile UI)
- Backend: FastAPI + LangGraph tools (mock dữ liệu)
- Agent: xử lý hội thoại, gọi tool chẩn đoán + trạm sạc + đặt lịch

## Thành phần chính
- Frontend: cảnh báo lỗi, pin yếu, luồng tự sửa/đặt lịch
- Backend tools: chẩn đoán lỗi, tìm trạm sạc, đặt lịch, thời tiết
- Agent: ReAct loop gọi tool theo ngữ cảnh

## Phân công
| Thành viên | Phần | Output |
|-----------|------|--------|
| Đăng + Tuấn | ChatBot AI | Agent + hội thoại trong frontend/backend |
| Huy Sơn | Agent cảnh báo & xử lý lỗi | Luồng chẩn đoán + hướng dẫn tự sửa |
| Đạt + Dũng | Cảnh báo & hỗ trợ pin yếu | UI cảnh báo pin yếu + tìm trạm sạc |