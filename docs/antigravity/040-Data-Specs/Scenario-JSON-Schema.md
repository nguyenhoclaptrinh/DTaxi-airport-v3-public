# Đặc tả Schema Dữ liệu Kịch bản (Scenario JSON v3 - Atomic Events)

Tài liệu này định nghĩa cấu trúc dữ liệu hiện hành để soạn thảo và sinh kịch bản mô phỏng cho hệ thống DTaxi.

Phiên bản hiện tại dùng mô hình **Atomic Events**: mỗi phần tử trong `steps` là một sự kiện đơn lẻ, hoặc là hội thoại (`MESSAGE`), hoặc là hành động mô phỏng (`ACTION`). Thiết kế này phù hợp với visual editor trong tương lai vì editor có thể tạo, sắp xếp, undo/redo và validate từng step độc lập.

> Lịch sử: bản schema cũ v2 được lưu tại `docs/antigravity/040-Data-Specs/archive/Scenario-JSON-Schema-v2-legacy.md`.

Tài liệu liên quan:

- `docs/antigravity/040-Data-Specs/Paths-JSON-Schema.md`
- `docs/antigravity/040-Data-Specs/Validation-Rules.md`

## 0. Lịch sử thay đổi

| Phiên bản | Ngày | Trạng thái | Ghi chú |
| :--- | :--- | :--- | :--- |
| v2 | Trước 2026-05-12 | Legacy | Mô tả step gộp `messages` và `path` trong cùng một object. |
| v3 | 2026-05-12 | Hiện hành | Chuẩn hóa atomic step `MESSAGE` / `ACTION`, path được tham chiếu qua `path_name`. |

## 1. Cấu trúc Root (Root Structure)

```json
{
  "scenario_id": "string",
  "name": "string",
  "airport_id": "string, optional (e.g., VVTS)",
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
| `initial_angle` | number, optional | Góc ban đầu theo độ. Nếu thiếu, hệ thống có thể tự tính theo path MOVE đầu tiên. |

## 3. Chi tiết các Bước (ScenarioStep)

Tất cả step dùng chung các trường nền sau:

| Trường | Kiểu | Mô tả |
| :--- | :--- | :--- |
| `id` | number | ID step duy nhất trong kịch bản, thường tăng dần từ 1 |
| `type` | string | `MESSAGE` hoặc `ACTION` |
| `timestamp` | string, optional | Thời gian mô phỏng hiển thị, ví dụ `08:00:15` |

### 3.1. MESSAGE step

```json
{
  "id": 1,
  "type": "MESSAGE",
  "sender": "string",
  "target": "string",
  "text": "string",
  "timestamp": "08:00:00"
}
```

| Trường | Kiểu | Mô tả |
| :--- | :--- | :--- |
| `sender` | string | Người gửi: `Pilot`, `KSV`, `ATC`, `SYSTEM`, hoặc định danh khác |
| `target` | string | Người nhận hoặc hệ thống nhận, ví dụ `D-TAXI` |
| `text` | string | Nội dung hội thoại/log |

### 3.2. ACTION: MOVE_ALONG_PATH

```json
{
  "id": 4,
  "type": "ACTION",
  "action": "MOVE_ALONG_PATH",
  "aircraft": "VNA123",
  "path_name": "fullPathTakeOff",
  "speed": 5,
  "report_text": "TAXIING VIA FULL ROUTE",
  "timestamp": "08:00:45"
}
```

| Trường | Kiểu | Mô tả |
| :--- | :--- | :--- |
| `action` | string | Hiện hỗ trợ `MOVE_ALONG_PATH` và `ROTATE` |
| `aircraft` | string | ID máy bay trong `aircraft_list` |
| `path_name` | string | Tên path trong `data/paths.json` |
| `speed` | number, optional | Tốc độ mục tiêu. Nếu thiếu, engine dùng tốc độ mặc định |
| `report_text` | string, optional | Nội dung position report khi action hoàn tất trong auto-play |

### 3.3. ACTION: ROTATE

```json
{
  "id": 5,
  "type": "ACTION",
  "action": "ROTATE",
  "aircraft": "VNA123",
  "value": 125,
  "timestamp": "08:01:00"
}
```

| Trường | Kiểu | Mô tả |
| :--- | :--- | :--- |
| `value` | number | Góc quay mới theo độ |

## 4. Đặc tả `data/paths.json`

`paths.json` là dictionary, trong đó key là `path_name`, value là danh sách tọa độ.

```json
{
  "fullPathTakeOff": [
    {"x": 787, "y": 438},
    {"x": 763, "y": 421},
    {"x": 765, "y": 408}
  ]
}
```

Quy tắc validate:

- Mọi `ACTION/MOVE_ALONG_PATH.path_name` phải tồn tại trong `data/paths.json`.
- Mỗi path nên có tối thiểu 2 điểm để tạo chuyển động nhìn thấy được.
- Điểm đầu của path nên khớp với trạng thái máy bay trước action, hoặc visual editor phải tự thêm segment nối.

## 5. Ví dụ kịch bản tối thiểu

```json
{
  "name": "Kịch bản Full Take-Off",
  "scenario_id": "FULL_TAKEOFF_01",
  "airport_id": "VVTS",
  "aircraft_list": [
    {
      "id": "VNA123",
      "callsign": "VN-A123",
      "type": "A321",
      "initial_pos": {"x": 787, "y": 438},
      "initial_angle": 125
    }
  ],
  "steps": [
    {
      "id": 1,
      "type": "MESSAGE",
      "sender": "Pilot",
      "target": "D-TAXI",
      "text": "VN-A123 REQUEST PUSHBACK AND START-UP",
      "timestamp": "08:00:00"
    },
    {
      "id": 2,
      "type": "ACTION",
      "action": "MOVE_ALONG_PATH",
      "aircraft": "VNA123",
      "path_name": "fullPathTakeOff",
      "report_text": "TAXIING VIA FULL ROUTE",
      "timestamp": "08:00:45"
    }
  ]
}
```

## 6. Ghi chú cho visual editor và nhiều máy bay

- Visual editor nên sinh cả `aircraft_list`, `steps`, và các path tương ứng trong `data/paths.json`.
- Với nhiều máy bay, `aircraft` trong từng `ACTION` là khóa liên kết bắt buộc.
- Nếu cần hai máy bay di chuyển đồng thời, schema hiện tại chưa đủ biểu diễn song song thật sự. Có thể mở rộng bằng `GROUP_ACTION` hoặc `parallel_group_id` trong phiên bản sau.
- Nên lưu metadata do editor sinh ra như `created_by`, `updated_at`, `map_asset`, `editor_version` ở root để trace nguồn dữ liệu.
