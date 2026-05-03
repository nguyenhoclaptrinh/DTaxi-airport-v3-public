# Kịch bản Mô phỏng VN-A123 (D-TAXI Standard)

Tài liệu này tổng hợp các bước mô phỏng di chuyển mặt đất của chuyến bay VN-A123 dựa trên yêu cầu từ feedback.

## Thông tin thực thể
- **Callsign**: VN-A123
*   **Loại máy bay**: A321
*   **Hệ thống liên lạc**: D-TAXI (thay thế AeroMACS)
*   **Tham số**: RCP 240, Latency <= 15ms

---

## GIAI ĐOẠN 1: PUSHBACK & START-UP

| Step | Loại | Từ | Đến | Nội dung thông điệp / Hành động |
| :--- | :--- | :--- | :--- | :--- |
| 1 | MESSAGE | Pilot | D-TAXI | "VN-A123 REQUEST PUSHBACK AND START-UP" |
| 2 | MESSAGE | KSV | D-TAXI | "VN-A123 CLEARED PUSHBACK AND START-UP. REQUEST TAXI ROUTE VIA TAXIWAY A – B – C, HOLDING POINT RWY 25R." |
| 3 | MESSAGE | Pilot | D-TAXI | "VN-A123 WILCO. PUSHBACK AND START-UP CLEARED, ROUTE CONFIRMED." |

---

## GIAI ĐOẠN 2: TAXI ĐẾN ĐIỂM CHỜ (HOLDING POINT)

| Step | Loại | Từ | Đến | Nội dung thông điệp / Hành động |
| :--- | :--- | :--- | :--- | :--- |
| 4 | **ACTION** | Pilot | - | **DI CHUYỂN QUA TAXIWAY A** (Auto msg: "TAXI STARTED") |
| 5 | MESSAGE | KSV | D-TAXI | "VN-A123 FOLLOW TAXI ROUTE A → B → C. REPORT HOLDING POINT RWY 25R." |
| 6 | MESSAGE | Pilot | D-TAXI | "VN-A123 WILCO, FOLLOWING ROUTE" |
| 7 | **ACTION** | Hệ thống | - | **DI CHUYỂN QUA TAXIWAY B** (Auto msg: "POSITION REPORT: VN-A123 PASSED NODE B") |
| 8 | **ACTION** | Hệ thống | - | **DI CHUYỂN QUA TAXIWAY C** (Auto msg: "POSITION REPORT: VN-A123 PASSED NODE C") |

---

## GIAI ĐOẠN 3: TẠI ĐIỂM CHỜ – CHỜ ƯU TIÊN

| Step | Loại | Từ | Đến | Nội dung thông điệp / Hành động |
| :--- | :--- | :--- | :--- | :--- |
| 9 | **ACTION** | Pilot | - | **DI CHUYỂN ĐẾN ĐIỂM CHỜ 25R** (Auto msg: "AT HOLDING POINT RWY 25R") |
| 10 | MESSAGE | KSV | D-TAXI | "VN-A123 HOLD POSITION. TRAFFIC ON FINAL RUNWAY 25R." |
| 11 | MESSAGE | Pilot | D-TAXI | "VN-A123 WILCO, HOLDING" |
| 12 | MESSAGE | KSV | D-TAXI | "VN-A123 LINE UP AND WAIT RUNWAY 25R." |
| 13 | **ACTION** | Pilot | - | **DI CHUYỂN VÀO ĐƯỜNG CHC** (Auto msg: "LINING UP RUNWAY 25R") |

---

## GIAI ĐOẠN 4: CẤT CÁNH (TAKE-OFF)

| Step | Loại | Từ | Đến | Nội dung thông điệp / Hành động |
| :--- | :--- | :--- | :--- | :--- |
| 14 | MESSAGE | KSV | D-TAXI | "VN-A123 WIND 240 DEGREES 8 KNOTS, RWY 25L, CLEARED FOR TAKE OFF." |
| 15 | MESSAGE | Pilot | D-TAXI | "CLEARED FOR TAKE OFF - VN A-123" |
| 16 | MESSAGE | SYSTEM | D-TAXI | "VN-A123 AIRBORNE. D-TAXI DISCONNECTED. SWITCHING TO VDL/SATCOM." |

---

> [!NOTE]
> Các bước **ACTION** sẽ tự động kích hoạt thông điệp báo cáo vị trí ngay khi máy bay hoàn thành hành trình tương ứng.
