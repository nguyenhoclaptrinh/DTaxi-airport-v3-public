# Đặc tả `paths.json`

`data/paths.json` lưu các đường lăn/hành trình đã vẽ bằng visual editor. Runtime không lưu tọa độ path trực tiếp trong scenario step; scenario chỉ tham chiếu qua `path_name`.

## Cấu trúc root

```json
{
  "pathName": [
    {"x": 100, "y": 200},
    {"x": 120, "y": 210}
  ]
}
```

## Quy ước

| Thành phần | Kiểu | Bắt buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `pathName` | string | Có | Tên path duy nhất, được dùng bởi `ACTION/MOVE_ALONG_PATH.path_name` |
| `x` | number | Có | Tọa độ trục X trên canvas chuẩn 1200x744 |
| `y` | number | Có | Tọa độ trục Y trên canvas chuẩn 1200x744 |

## Rule runtime

- Mỗi path dùng để di chuyển nên có ít nhất 2 điểm.
- Điểm đầu path nên trùng với vị trí máy bay trước action, hoặc editor phải tạo đoạn nối hợp lệ.
- Không đổi tên path khi scenario đang tham chiếu tới path đó, trừ khi cập nhật đồng bộ scenario.
- Runtime vẽ active path trực tiếp từ `paths.json`, nên tọa độ phải dùng cùng hệ chuẩn với map renderer.

## Ví dụ

```json
{
  "fullPathTakeOff": [
    {"x": 787, "y": 438},
    {"x": 763, "y": 421},
    {"x": 765, "y": 408},
    {"x": 811, "y": 315}
  ],
  "gate_to_taxiway_a": [
    {"x": 500, "y": 420},
    {"x": 520, "y": 410},
    {"x": 550, "y": 405}
  ]
}
```

