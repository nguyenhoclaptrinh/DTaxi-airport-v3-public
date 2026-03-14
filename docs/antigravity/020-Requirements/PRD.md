# PRD: Hệ thống mô phỏng DataLink AeroMACS (DTaxi)

## 1. Mục tiêu (Goals)
Xây dựng một công cụ mô phỏng giao tiếp DataLink AeroMACS giữa Kiểm soát viên (ATC) và Phi công (Pilot) tại sân bay để đào tạo và trình diễn kịch bản.

## 2. Đối tượng mục tiêu
- Kiểm soát viên không lưu (KSV).
- Phi công thực tập.

## 3. Tính năng chính (Key Features)

### 3.1. Mô phỏng Kịch bản (Scenario Engine)
- Chạy kịch bản từ file JSON.
- Nút điều phối: **Start, Stop, Continue, Next, Prev, Reset**.
- Hỗ trợ chạy đồng thời nhiều máy bay theo Flight Plan.

### 3.2. Giao diện Hiển thị (Visualization)
- **Sơ đồ Sân bay:** Bản đồ 2D (Sử dụng ảnh nền sơ đồ thực tế).
- **Máy bay:** 
    - Hiển thị vị trí trực quan, cập nhật theo kịch bản.
    - **Di chuyển mượt mà (Smooth Path Movement):** Máy bay di chuyển từ từ dọc theo các đường lăn (taxiway), không nhảy cóc giữa các điểm. Quá trình di chuyển được chia nhỏ thành các đoạn thẳng (segments).
- **Log Giao tiếp:** Hiển thị tin nhắn dạng Plain Text (chuẩn Anh ngữ Phraseology).

## 4. Yêu cầu kỹ thuật
- **Ngôn ngữ:** Python 3.10+.
- **UI Framework:** Đề xuất `Pygame` hoặc `CustomTkinter`.

## 5. Quy tắc dữ liệu
- Tin nhắn: Plain text qua giả lập AeroMACS.
- Kịch bản: 9 bước tiêu chuẩn ICAO.
