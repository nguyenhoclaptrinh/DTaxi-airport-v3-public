# Quy tắc Validation cho Scenario và Path

Tài liệu này là contract chung cho simulator, visual editor, và script kiểm tra dữ liệu.

## Công cụ validate

Validator runtime nằm ở:

- `src/engine/scenario_validator.py`

Script kiểm tra toàn bộ scenario:

```bash
python scripts/validate_scenarios.py
```

## Scenario root

- Root phải là JSON object.
- `aircraft_list` phải là array.
- `steps` phải là array.
- `scenario_id` nên có để định danh ổn định.
- `name` nên có để hiển thị UI.

## Aircraft

Mỗi aircraft trong `aircraft_list` phải có:

- `id`: duy nhất trong scenario.
- `callsign`: tên gọi hiển thị/log.
- `initial_pos`: object `{x, y}` với `x`, `y` là number.

Khuyến nghị:

- `type`: loại máy bay.
- `initial_angle`: góc ban đầu. Nếu thiếu, runtime sẽ cố tính từ path MOVE đầu tiên.

## Step chung

Mỗi step phải có:

- `id`: duy nhất trong scenario.
- `type`: `MESSAGE` hoặc `ACTION`.

`timestamp` là optional, dùng để hiển thị đồng hồ mô phỏng.

## MESSAGE

MESSAGE step phải có:

- `sender`
- `target`
- `text`

Ví dụ:

```json
{
  "id": 1,
  "type": "MESSAGE",
  "sender": "Pilot",
  "target": "D-TAXI",
  "text": "VN-A123 REQUEST PUSHBACK",
  "timestamp": "08:00:00"
}
```

## ACTION / MOVE_ALONG_PATH

MOVE step phải có:

- `action`: `MOVE_ALONG_PATH`
- `aircraft`: tồn tại trong `aircraft_list`
- `path_name`: tồn tại trong `data/paths.json`

Path được tham chiếu phải có ít nhất 2 điểm.

Ví dụ:

```json
{
  "id": 4,
  "type": "ACTION",
  "action": "MOVE_ALONG_PATH",
  "aircraft": "VNA123",
  "path_name": "fullPathTakeOff",
  "report_text": "TAXIING VIA FULL ROUTE"
}
```

## ACTION / ROTATE

ROTATE step phải có:

- `action`: `ROTATE`
- `aircraft`: tồn tại trong `aircraft_list`
- `value`: number, đơn vị độ

Ví dụ:

```json
{
  "id": 5,
  "type": "ACTION",
  "action": "ROTATE",
  "aircraft": "VNA123",
  "value": 125
}
```

## Hành vi khi có lỗi

Simulator:

- Load scenario và hiển thị số lượng validation issue.
- Nếu chạy tới `MOVE_ALONG_PATH` thiếu path, hệ thống log lỗi và tự chuyển sang pause để tránh auto-play skip action.

Visual editor:

- Khi save scenario, editor chạy validator và in warning ra console nếu dữ liệu chưa hợp lệ.
- Editor vẫn lưu file để người dùng không mất dữ liệu đang làm, nhưng warning phải được xử lý trước khi demo/chạy chính thức.

