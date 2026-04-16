# Phân Tích & Nghiên Cứu Kiến Trúc Mo Phỏng DTaxi (DTaxi-airport-v3)

## 1. Mục Đích Nghiên Cứu
Nhằm đánh giá hệ thống mô phỏng di chuyển mặt đất của sân bay hiện tại tại `DTaxi-airport-v3` theo tiêu chuẩn kỹ nghệ phần mềm 2026. Tìm kiếm các mẫu kiến trúc hiện đại tối ưu cho "Discrete Event Simulation" (Mô phỏng sự kiện rời rạc) kết hợp UI lai.

## 2. Kết Quả Nghiên Cứu Hiện Đại (Industry Standards 2026)

### 2.1. Hybrid Architecture (Pygame + Tkinter/CustomTkinter)
Việc nhúng vòng lặp của Pygame vào cơ chế `after()` của `Tkinter` (như cách đang làm) là một **Anti-pattern** cổ điển.
- **Vấn đề rủi ro**: Tkinter không thread-safe và `after()` không sinh ra để gánh chịu tick-rate của game engine (dễ delay, frame drop, và freeze GUI).
- **Giải pháp chuẩn**: 
  - *Phương pháp 1*: Tách biệt Process/Thread với Data Queue (Multiprocessing Queue).
  - *Phương pháp 2*: Dùng UI Native của Game Engine (ví dụ: `pygame-gui` hoặc `pygame-menu`) thay vì kết hợp 2 framework khác biệt triết lý vòng lặp.
  - *Phương pháp 3*: Đưa Core Simulation thành server (Python/FastAPI) và Frontend thành Web (React/Canvas/WebGL) -> *Premium Approach*.

### 2.2. Discrete Event Simulation (DES) & State Machine
Code hiện tại dùng cấu trúc `ScenarioManager` dựa trên mảng tĩnh và `current_step_index`. Đây là cách tiếp cận tuyến tính (Linear Scripting). Trong thực tế, hệ thống sân bay phải hoạt động song song và bất ngờ.
- **Tiêu chuẩn công nghiệp**: Sử dụng **DES (Discrete Event Simulation)** kết hợp **State Machine**.
- **Công nghệ đề xuất**:
  - `SimPy`: Standard tool cho DES trong Python (quản lý Time, Locks trên các Taxiway).
  - `transitions`: Thư viện State Machine phổ biến cho Python. Máy bay nên có các state: `AtGate` -> `Pushback` -> `Taxiing` -> `Holding` -> `Takeoff`.
  - Phát hiện va chạm & Locking: Taxiway/Runway phải là các `Resource` (tài nguyên dùng chung). Airplane nào không lấy được lock thì tự động rơi vào state `Holding` thay vì lao thẳng qua nhau như hiện tại.

## 3. Khuyến Nghị Áp Dụng
- Không nên duy trì mô hình tuyến tính "đọc từng json step và áp dụng". Nó không cho phép "mô phỏng" thực sự mà chỉ là "trình diễn" (playback) 1 kịch bản cứng.
- Cần tái kiến trúc theo mô hình OOP + State Machine ngay trong lớp `AircraftEntity`.
