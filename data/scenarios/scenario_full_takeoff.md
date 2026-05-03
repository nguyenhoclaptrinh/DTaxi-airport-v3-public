# Kịch bản Mô phỏng: Full Take-Off (Lộ trình liên tục)

Kịch bản này sử dụng tuyến đường `fullPathTakeOff` đã được tối ưu hóa để thực hiện mô phỏng xuyên suốt từ điểm đỗ đến khi cất cánh.

## Thông tin kịch bản
- **Tên**: Full Take-Off (Bản đồ mới)
- **Máy bay**: VN-A123 (A321)
- **Lộ trình**: `fullPathTakeOff` (Liên tục)

---

## Các bước mô phỏng

| Thứ tự | Loại | Đối tượng | Nội dung |
| :--- | :--- | :--- | :--- |
| 1 | MESSAGE | Pilot | VN-A123 REQUEST PUSHBACK AND START-UP |
| 2 | MESSAGE | KSV | VN-A123 CLEARED PUSHBACK AND START-UP. TAXI TO RUNWAY 25L VIA FULL ROUTE. |
| 3 | MESSAGE | Pilot | WILCO, TAXI TO 25L - VN-A123 |
| 4 | **ACTION** | VN-A123 | **DI CHUYỂN TOÀN BỘ LỘ TRÌNH** (Báo cáo: TAXIING VIA FULL ROUTE) |
| 5 | MESSAGE | KSV | VN-A123, WIND 240/12, RWY 25L, CLEARED FOR TAKE OFF. |
| 6 | MESSAGE | Pilot | CLEARED FOR TAKE OFF, VN-A123 |
| 7 | MESSAGE | SYSTEM | VN-A123 AIRBORNE. SWITCHING TO VDL/SATCOM. |

---

### Lưu ý khi vận hành:
*   Vì lộ trình là một dải điểm liên tục, máy bay sẽ tự động giảm tốc tại các khúc cua đã được anh vẽ trong Editor.
*   Trong chế độ **AUTO PLAY**, hệ thống sẽ đợi máy bay đi hết toàn bộ `fullPathTakeOff` trước khi hiện thông báo Cất cánh ở bước 5.
