# Roadmap Dự án DTaxi (Antigravity Edition)

Dự án tập trung vào việc xây dựng một hệ thống mô phỏng giao tiếp AeroMACS đơn giản, ổn định và dễ bảo trì, sử dụng ngôn ngữ Python.

## Giai đoạn 1: Thiết kế & Chuẩn bị (Tuần 1 - Tuần 2)
- [x] **Hoàn thiện Đặc tả (PRD & SDD):** Chuyển đổi các yêu cầu thành tài liệu thiết kế kỹ thuật tinh giản.
- [x] **Thiết kế Kịch bản mẫu:** Soạn thảo 9 bước cất cánh và 9 bước hạ cánh dựa trên chuẩn ICAO phraseology (Tiếng Anh).
- [x] **Lựa chọn Stack công nghệ:** Quyết định thư viện Visualization (Đề xuất: `Pygame` cho đồ họa 2D hoặc `CustomTkinter` cho UI hiện đại).

## Giai đoạn 2: Phát triển Core Engine (Tuần 3 - Tuần 4)
- [ ] **Module Kịch bản (Scenario Engine):** Trình đọc file JSON kịch bản, quản lý trạng thái Next/Prev/Stop/Continue.
- [ ] **Module AeroMACS Simulator:** Logic truyền nhận tin nhắn (Plain text), giả lập độ trễ AeroMACS.
- [ ] **Mô hình hóa Sân bay:** Xây dựng sơ đồ sân bay bằng tọa độ XY đơn giản.

## Giai đoạn 3: Hiện thực hóa UI & Log (Tuần 5 - Tuần 6)
- [ ] **Màn hình Tổng quát:** Hiển thị sơ đồ sân bay và vị trí các máy bay (PC-1, PC-2...).
- [ ] **Màn hình Log (Pilot & ATC):** Hiển thị luồng trao đổi tin nhắn thời gian thực.
- [ ] **Điều khiển:** Gắn các sự kiện nút bấm vào logic chạy kịch bản.

## Giai đoạn 4: Kiểm thử & Đóng gói (Tuần 7)
- [ ] **Validation:** Chạy thử toàn bộ kịch bản từ đầu đến cuối.
- [ ] **Fix bug & Phản hồi:** Chỉnh sửa theo ý kiến leader/người dùng.
- [ ] **Đóng gói dự án:** Hướng dẫn cài đặt và sử dụng (README cập nhật).

---

## Cột mốc quan trọng (Milestones)
- **M1 (30/03):** Hoàn thành khung kịch bản và khung phần mềm cơ bản.
- **M2 (15/04):** UI hoàn thiện, máy bay di chuyển trên sơ đồ theo kịch bản.
- **M3 (25/04):** Hoàn thiện toàn bộ log và fix lỗi.
- **D-Day (30/04/2026):** Bàn giao dự án.
