# Đặc tả Schema Dữ liệu Kịch bản (Scenario JSON v2 - Legacy)

> Lưu trữ lịch sử: đây là bản schema cũ trước khi hệ thống chuyển sang mô hình Atomic Events (`MESSAGE` / `ACTION`). Không dùng tài liệu này để tạo kịch bản mới.

Tài liệu này định nghĩa cấu trúc dữ liệu chuẩn để soạn thảo các kịch bản mô phỏng cho hệ thống DTaxi.

## 1. Cấu trúc Root (Root Structure)

```json
{
  "scenario_id": "string",
  "scenario_name": "string",
  "airport_id": "string (e.g., VVTS)",
  "aircraft_list": "Array<AircraftDefinition>",
  "steps": "Array<ScenarioStep>"
}
```

## 2. Định nghĩa Máy bay (AircraftDefinition)

| Trường | Kiểu | Mô tả |
| :--- | :--- | :--- |
| `id` | string | Định danh duy nhất (ví dụ: PC01) |
| `callsign` | string | Tên gọi trao đổi (ví dụ: HVN123) |
| `type` | string | Loại máy bay (A321, B789, ...) |
| `initial_pos` | object | `{x: number, y: number}` Tọa độ khởi tạo |

## 3. Chi tiết các Bước (ScenarioStep)

| Trường | Kiểu | Mô tả |
| :--- | :--- | :--- |
| `id` | number | Thứ tự bước (bắt đầu từ 1) |
| `label` | string | Tên hiển thị của bước |
| `active_aircraft`| string | ID máy bay thực hiện hành động |
| `path` | Array<Pos> | Danh sách các tọa độ `{"x": n, "y": m}` tạo thành lộ trình di chuyển |
| `speed` | number | Tốc độ di chuyển (pixel/frame hoặc unit/sec) |
| `messages` | Array<Msg> | Danh sách tin nhắn trao đổi trong bước này |

### 3.1. Cấu trúc Tin nhắn (Msg)

```json
{
  "sender": "string (ID máy bay hoặc 'ATC')",
  "target": "string",
  "text": "string (Nội dung tin nhắn)",
  "type": "string ('URGENT', 'NORMAL')"
}
```

## 4. Ví dụ một bước kịch bản hoàn chỉnh

```json
{
  "id": 4,
  "label": "Taxi to Holding Point",
  "active_aircraft": "PC01",
  "path": [
    {"x": 100, "y": 250},
    {"x": 150, "y": 250},
    {"x": 150, "y": 300},
    {"x": 200, "y": 300}
  ],
  "speed": 10,
  "messages": [
    {
      "sender": "PC01",
      "target": "ATC",
      "text": "READY TO TAXI"
    },
    {
      "sender": "ATC",
      "target": "PC01",
      "text": "TAXI TO HOLDING POINT RWY 25L VIA A, B"
    }
  ]
}
```

