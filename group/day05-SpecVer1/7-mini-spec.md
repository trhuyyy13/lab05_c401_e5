# 7. Mini AI Spec

## Bài toán
- Người dùng xe thường mất thời gian hiểu cảnh báo, tìm cách xử lý và liên hệ hỗ trợ
- AI giúp:
  - nhận diện vấn đề
  - giải thích ngắn gọn
  - gợi ý hành động phù hợp
  - hỗ trợ thực hiện ngay trong app

## Người dùng
- Người dùng xe trong hệ sinh thái
- Đặc biệt hữu ích khi:
  - không hiểu mã lỗi
  - cần xử lý nhanh
  - đang ở tình huống khẩn cấp

## Vai trò của AI
- Nhận input từ:
  - mô tả user
  - ảnh / log / cảnh báo từ xe
  - dữ liệu real-time
- Đầu ra:
  - vấn đề đang xảy ra
  - mức độ nghiêm trọng
  - hành động tiếp theo phù hợp

## Automation hay augmentation
- **Augmentation**
- AI chỉ gợi ý, user quyết định cuối cùng
- Các action quan trọng như gọi cứu hộ, đặt lịch dịch vụ vẫn cần xác nhận

## Chất lượng cần đạt
- Critical flows: ưu tiên **precision**
- Non-critical flows: ưu tiên **recall**
- Mục tiêu:
  - intent accuracy >= 90%
  - critical precision >= 92%
  - latency < 2s

## Risk chính
- Hiểu sai tình trạng xe
- Dữ liệu dịch vụ không cập nhật
- Gợi ý / thực hiện action sai

## Mitigation
- Confidence score + hỏi lại khi không chắc
- Fallback sang tổng đài / kỹ thuật viên
- Real-time data sync
- Bắt buộc confirm trước action quan trọng

## Data flywheel
- User accept / reject / sửa gợi ý
- Hệ thống lưu correction + outcome
- Dùng để cải thiện:
  - phân loại sự cố
  - ranking hành động
  - knowledge base
  - personalization

## Kết luận
- Đây là AI assistant hỗ trợ xử lý sự cố xe
- Giá trị chính:
  - nhanh hơn cho user
  - giảm tải hỗ trợ
  - tăng sử dụng dịch vụ hệ sinh thái
- Nên build theo hướng **AI hỗ trợ, không full automation**