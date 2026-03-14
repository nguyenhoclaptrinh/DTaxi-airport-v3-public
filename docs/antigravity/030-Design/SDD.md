# SDD: Thiết kế Hệ thống DTaxi (v2 - Toàn diện)

Tài liệu này cung cấp cái nhìn chi tiết nhất về cấu trúc và cơ chế xử lý của hệ thống mô phỏng DTaxi.

## 1. Kiến trúc Hệ thống (System Architecture)

Hệ thống được thiết kế theo mô hình **Event-Condition-Action (ECA)** kết hợp với **State Synchronization**:
- **Scenario Core:** Trái tim của hệ thống, quản lý trình tự các bước và trạng thái của toàn bộ máy bay trong kịch bản.
- **Entity Manager:** Quản lý vòng đời và biểu diễn của nhiều máy bay (PC-1, PC-2, PC-n).
- **Control Overlay:** Lớp giao diện điều khiển (UI) tương tác với người dùng.
- **Chronos Engine:** Module quản lý thời gian và tốc độ mô phỏng (Delta Time).

## 2. Các module chi tiết (Detailed Modules)

### 2.1. Scenario Engine (`src/engine/scenario_core.py`)
- **JSON Parser:** Đọc kịch bản, kiểm tra tính hợp lệ của tọa độ và cấu trúc tin nhắn.
- **Global Clock:** Phối hợp các máy bay di chuyển đồng bộ. Nếu một bước yêu cầu PC-1 taxi và PC-2 chờ, Engine sẽ gửi lệnh tương ứng.
- **Undo/Redo Logic:** Lưu vết `state_history` để hỗ trợ nút `Prev` (quay lại trạng thái trước đó một cách chính xác).

### 2.2. Entity Logic (`src/entities/aircraft.py`)
- **Hành vi di chuyển (Locomotion):**
    - Sử dụng chuẩn **Linear Interpolation (Lerp)** giữa các Waypoints.
    - **Path Smoothing:** Tự động bo góc khi máy bay chuyển hướng giữa 2 đoạn thẳng (segment) để tránh hiệu ứng "giật" hướng.
    - **Status:** `PARKED`, `TAXIING`, `TAKING_OFF`, `AIRBORNE`.
- **Đồng bộ Tin nhắn:** Tin nhắn AeroMACS sẽ được "Push" vào log ngay khi `AircraftEntity` bắt đầu thực hiện một lộ trình (`path`) trong bước đó.

### 2.3. AeroMACS Scroll Log (`src/ui/log_system.py`)
- **Data Structure:** Sử dụng một `Buffer` giới hạn (ví dụ: 100 tin nhắn gần nhất).
- **Rendering:**
    - Tin nhắn mới luôn xuất hiện ở dưới cùng và đẩy các tin nhắn cũ lên trên (Auto-scroll).
    - Phân biệt màu sắc: Tin nhắn từ Pilot (màu xanh lục/trắng), tin nhắn từ ATC (màu hổ phách/vàng rơm) để tăng tính trực quan.
- **Timestamp:** Mỗi tin nhắn gắn với một `Simulation Time` (không phải thời gian thực).

### 2.4. Map Rendering (`src/ui/map_renderer.py`)
- **Layering:** 
    - Layer 0: Ảnh nền sơ đồ (`background.png`).
    - Layer 1: Vẽ các Waypoints và Path (chỉ hiển thị khi Debug).
    - Layer 2: Vẽ các `AircraftEntity` (Sprite máy bay có thể xoay hướng theo Vector di chuyển).
    - Layer 3: HUD (Heads-up Display) hiển thị thông tin máy bay đang chọn.

## 3. Cấu trúc Dữ liệu Kịch bản (JSON v2)

```json
{
  "project": "DTaxi-Airport-v3",
  "airport_id": "VVTS",
  "aircraft_list": [
    {"id": "PC01", "type": "A321", "initial_pos": {"x": 100, "y": 200}},
    {"id": "PC02", "type": "B789", "initial_pos": {"x": 500, "y": 800}}
  ],
  "steps": [
    {
      "id": 1,
      "label": "Pushback PC-01",
      "active_aircraft": "PC01",
      "path": [{"x": 100, "y": 200}, {"x": 80, "y": 200}],
      "speed": 5,
      "messages": [
        {"sender": "PC01", "text": "READY FOR PUSHBACK", "target": "ATC"},
        {"sender": "ATC", "text": "PUSHBACK APPROVED", "target": "PC01"}
      ]
    }
  ]
}
```

## 4. Xử lý Lỗi & Cạnh biên (Edge Cases)
- **Tọa độ ngoài biên:** Nếu tọa độ trong JSON lớn hơn kích thước ảnh map, máy bay sẽ dừng lại ở biên và in cảnh báo vào terminal.
- **Xung đột kịch bản:** Nếu 2 bước điều khiển 1 máy bay cùng lúc, Engine sẽ ưu tiên bước có ID cao hơn.
- **Tốc độ:** Hỗ trợ nhân hệ số tốc độ (1x, 2x, 5x) để xem nhanh kịch bản.

## 5. Danh mục Assets cần thiết
1. `airport_map.png`: Ảnh sơ đồ sân bay độ phân giải thực tế.
2. `aircraft_icon.png`: Sprite máy bay nhìn từ trên xuống (Top-down view).
3. `click_sound.wav`: Hiệu ứng âm thanh khi có tin nhắn mới (Tùy chọn).
