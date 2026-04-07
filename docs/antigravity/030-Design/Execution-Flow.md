# Phân tích Luồng thực thi (Execution Flow) DTaxiApp

Tài liệu này mô tả chi tiết luồng chạy của ứng dụng mô phỏng DTaxi-airport-v3, từ quá trình khởi tạo, vòng lặp chính, cho tới các luồng sự kiện tương tác của người dùng.

## 1. Khởi tạo và Thiết lập (Initialization & Setup)

Ứng dụng khởi chạy bắt đầu từ `main.py`, tạo đối tượng `DTaxiApp` và gọi phương thức `run()`.

```mermaid
sequenceDiagram
    participant Main as main.py
    participant App as DTaxiApp
    participant SM as ScenarioManager
    participant MR as MapRenderer
    participant WM as WindowManager
    
    Main->>App: app = DTaxiApp()
    activate App
    App->>SM: init()
    App->>MR: init(800, 600)
    App->>WM: init(callbacks: on_next, on_prev, ...)
    
    Main->>App: app.run()
    App->>App: setup()
    activate App
    App->>MR: init_pygame()
    App->>App: load_scenario("Departure Scenario")
    App->>SM: load_scenario(scenario_path, metadata_path)
    SM-->>App: current_step
    App->>WM: set_status("Loaded...")
    deactivate App
    
    App->>App: update_loop() (Khởi chạy lần đầu)
    App->>WM: root.mainloop() (Chuyển quyền điều khiển cho Tkinter loop)
    deactivate App
```

## 2. Vòng lặp Chính (Main Update Loop)

Vòng lặp chính được điều khiển qua cơ chế ngắt nhịp `after()` của đối tượng Tkinter trong WindowManager, giúp kết hợp an toàn cả hai framework UI (Tkinter cho bảng điều khiển, và Pygame cho bản đồ).

```mermaid
flowchart TD
    Start((Bắt đầu update_loop)) --> CheckRunning{self.running == True?}
    CheckRunning -- Sai --> End((Kết thúc loop))
    
    CheckRunning -- Đúng --> CalcDelta[Tính toán delta_time]
    CalcDelta --> PumpEvent["pygame.event.pump() <br/> Bắt sự kiện Window"]
    
    PumpEvent --> CheckQuit{Event == QUIT?}
    CheckQuit -- Đúng --> SetRunningFalse["self.running = False <br/> root.quit()"] --> End
    
    CheckQuit -- Sai --> UpdateEntities[Loop qua từng AircraftEntity]
    UpdateEntities --> EntityUpdate["entity.update(delta_time)"]
    EntityUpdate --> DrawMap["map_renderer.draw(...)"]
    
    DrawMap --> ScheduleNext["Lên lịch gọi lại: root.after(20, update_loop)"]
    ScheduleNext --> Wait((Chờ 20ms))
```

## 3. Luồng Cập nhật Thực thể Máy bay (Aircraft Entity Update)

Giai đoạn cập nhật logic di chuyển vật lý của từng máy bay trong mỗi frame.

```mermaid
flowchart TD
    Start(("entity.update")) --> CheckMoving{"is_moving == True <br/> VÀ <br/> có target_path?"}
    CheckMoving -- Không --> Stop[is_moving = False] --> End((Kết thúc update))
    
    CheckMoving -- Có --> GetTarget[Lấy waypoint đích đầu tiên trong path]
    GetTarget --> CalcDist[Tính khoảng cách dx, dy từ vị trí hiện tại đến đích]
    
    CalcDist --> CheckDist{Khoảng cách > arrival_threshold?}
    CheckDist -- Có --> Move[Di chuyển x, y tịnh tiến theo tỷ lệ delta_time * tốc độ]
    Move --> Rotate["Cập nhật góc quay mũi máy bay bằng arctan2"] --> End
    
    CheckDist -- Không --> Arrived["Đã đến nơi: Đặt tọa độ x, y = đích, <br/> xóa waypoint này khỏi target_path"]
    Arrived --> CheckPath{target_path còn điểm nào không?}
    CheckPath -- Có --> End
    CheckPath -- Không --> SetStop[is_moving = False] --> End
```

## 4. Luồng Xử lý Điều khiển của Người dùng (Scenario Controls)

Hành vi ứng dụng khi người dùng tương tác với Controller của AeroMACS (NEXT, PREV, RESET).

```mermaid
sequenceDiagram
    participant User
    participant WM as WindowManager
    participant App as DTaxiApp
    participant SM as ScenarioManager
    participant Entity as AircraftEntity

    alt Nhấn nút NEXT (Chuyển bước kế tiếp)
        User->>WM: Click NEXT
        WM->>App: handle_next()
        App->>Entity: complete_path() (Ép máy bay nhảy tới điểm đích cuối của bước cũ nếu chưa tới nơi)
        App->>SM: next_step()
        SM-->>App: return step_data
        App->>App: _trigger_step_actions(start_movement=True)
        App->>WM: add_log(messages) (Hiển thị tin nhắn vô tuyến mới)
        App->>Entity: set_path(path, speed) (Bắt đầu di chuyển cho bước mới)
        App->>WM: set_status(...)
        
    else Nhấn nút PREV (Trở về bước trước)
        User->>WM: Click PREV
        WM->>App: handle_prev()
        App->>SM: prev_step()
        SM-->>App: return step_data
        App->>Entity: teleport(start_pos) (Hủy path cũ, quay ngược về vị trí khởi đầu của bước này)
        App->>WM: clear_log()
        App->>App: _trigger_step_actions(start_movement=False) (Chỉ nạp lại log tin nhắn, bỏ qua phần di chuyển)
        App->>WM: add_log(messages)
        
    else Nhấn nút RESET SCENARIO
        User->>WM: Click RESET
        WM->>App: handle_reset()
        App->>SM: reset()
        SM-->>App: return initial_step
        App->>Entity: teleport(initial_pos) (Mang lại vị trí từ trạng thái ban đầu xuất phát)
        App->>App: _trigger_step_actions()
    end
```
