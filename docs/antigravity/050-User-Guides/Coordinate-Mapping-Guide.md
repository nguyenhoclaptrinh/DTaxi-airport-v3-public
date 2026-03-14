# Hướng dẫn Mapping Tọa độ Sân bay VVTS

Hệ thống DTaxi v2 hiện đã hỗ trợ cơ chế **Smart Mapping**, giúp việc thiết kế kịch bản trở nên trực quan hơn bằng cách sử dụng tên điểm thay vì tọa độ XY.

## 1. Cấu trúc Mapping
Tọa độ thực tế dựa trên ảnh bản đồ được quản lý tập trung tại:
`data/vvts_metadata.json`

Ví dụ định nghĩa một điểm:
```json
"STAND_A1": {"x": 680, "y": 420, "label": "Stand A1"}
```

## 2. Cách sử dụng trong Kịch bản
Trong các file JSON kịch bản (vận hành tại `data/scenarios/`), bạn không cần nhập tọa độ cứng nữa. Hãy sử dụng tên điểm đã định nghĩa ở bước 1:

```json
"initial_pos": "STAND_A1",
"path": ["STAND_A1", "TAXIWAY_W6", "HOLDING_POINT_25L"]
```

## 3. Cách lấy tọa độ thực tế từ ảnh
Để mapping chính xác các điểm khác trên bản đồ VVTS:
1. Mở ảnh `assets/images/airport_map.png` bằng các phần mềm chỉnh sửa ảnh cơ bản (Paint, Photoshop, v.v.).
2. Di chuột đến vị trí mong muốn và ghi lại tọa độ Pixel (X, Y).
3. Thêm tọa độ này vào `data/vvts_metadata.json` kèm theo một cái tên gợi nhớ (ví dụ: `TAXIWAY_E2`).
4. Sử dụng tên `TAXIWAY_E2` đó trong file kịch bản của bạn.

## 4. Lợi ích
- **Dễ bảo trì:** Khi bạn thay đổi ảnh bản đồ, bạn chỉ cần cập nhật tọa độ trong 1 file Metadata duy nhất, thay vì phải sửa hàng chục file kịch bản.
- **Dễ đọc:** Kịch bản giờ đây giống như một câu chuyện thực tế: *"Máy bay từ STAND A1 lăn qua con đường W6 để đến điểm chờ 25L"*.
