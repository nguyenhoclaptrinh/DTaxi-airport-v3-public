# Walkthrough: Hệ thống Mô phỏng DTaxi v2

Dự án DTaxi hiện đã hoàn thành giai đoạn **Core Visualization**. Ứng dụng đã có giao diện đồ họa hoàn chỉnh, hỗ trợ mô phỏng di chuyển thực tế và log giao tiếp AeroMACS.

## 1. Các tính năng đã triển khai
- **Smooth Movement (Lerp):** Máy bay di chuyển từ từ dọc theo đường lăn, không còn hiện tượng nhảy cóc tọa độ.
- **Integrated UI:** Kết hợp sức mạnh đồ họa của **Pygame** và giao diện điều khiển hiện đại của **CustomTkinter**.
- **AeroMACS Scroll Log:** Tin nhắn giao tiếp được hiển thị dưới dạng scroll board, hỗ trợ theo dõi lịch sử.
- **Premium Assets:** Bản đồ sân bay và icon máy bay được thiết kế chuyên nghiệp.

## 2. Hướng dẫn chạy ứng dụng

### Bước 1: Cài đặt thư viện
Mở terminal tại thư mục dự án và chạy lệnh:
```bash
pip install -r requirements.txt
```

### Bước 2: Khởi chạy mô phỏng
Chạy file main:
```bash
python src/main.py
```

## 3. Cách vận hành
- **Cửa sổ Map (Pygame):** Hiển thị trực quan máy bay và lộ trình di chuyển.
- **Cửa sổ Controller (CustomTkinter):**
    - Nhấn **NEXT** để chuyển bước tiếp theo. Tin nhắn AeroMACS sẽ xuất hiện và máy bay sẽ bắt đầu di chuyển mượt mà.
    - Nhấn **PREV** để quay lại bước trước.
    - Nhấn **RESET** để đưa kịch bản về trạng thái ban đầu.

## 4. Kết quả hình ảnh
Sơ đồ sân bay và icon máy bay được lưu tại thư mục `assets/images/`.
- Sơ đồ: `airport_map.png`
- Biểu tượng: `aircraft_icon.png`
