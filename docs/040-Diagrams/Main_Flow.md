# Sơ đồ khối Luồng xử lý chính (main.py)

Tài liệu này mô tả kiến trúc vận hành của ứng dụng DTaxi Simulator.

```mermaid
graph TD
    A[Bắt đầu: main.py] --> B[Khởi tạo DTaxiApp]
    B --> C[Thiết lập UI: WindowManager]
    B --> D[Khởi tạo Engine: ScenarioManager & MapRenderer]
    
    C --> E{Người dùng chọn kịch bản?}
    E -- Có --> F[Tải file JSON kịch bản]
    F --> G[Khởi tạo danh sách AircraftEntity]
    G --> H[Cập nhật UI & Bản đồ ban đầu]
    
    H --> I[Vòng lặp chính: update_loop]
    
    subgraph "Simulation Loop (Mỗi Frame)"
        I --> J[Tính toán Delta Time * Sim Speed]
        J --> K{Simulation Paused?}
        K -- No --> L[Cập nhật vị trí AircraftEntity]
        K -- Yes --> M[Giữ nguyên vị trí]
        
        L --> N{Auto Play Mode?}
        M --> Q
        N -- No --> Q
        
        N -- Yes --> O{Loại Step?}
        O -- ACTION --> P{Máy bay dừng?}
        O -- MESSAGE --> PA[Hết thời gian chờ?]
        
        P -- Yes --> NEXT[handle_next]
        PA -- Yes --> NEXT
        
        NEXT --> FIN{Hết kịch bản?}
        FIN -- Yes --> RESET[Chờ 3s & Reset Scenario]
        FIN -- No --> Q
        RESET --> I
    end
    
    Q[MapRenderer: Vẽ lại toàn bộ Scene] --> R[WindowManager: Cập nhật Log & Status]
    
    R --> S{Sự kiện từ người dùng?}
    S -- NEXT/PREV --> T[Điều hướng kịch bản]
    S -- STOP/RESUME --> U[Bật/Tắt Pause]
    S -- Slider --> V[Thay đổi Sim Speed]
    
    T --> I
    U --> I
    V --> I
    P -- No --> Q
    PA -- No --> Q
```

## Giải thích các thành phần chính:
1.  **DTaxiApp**: Trái tim của ứng dụng, điều phối giữa giao diện (Tkinter) và engine mô phỏng (Pygame).
2.  **update_loop**: Chạy liên tục để tính toán vật lý máy bay. Tốc độ mô phỏng (`sim_speed`) tác động trực tiếp vào `delta_time` ở đây.
3.  **ScenarioManager**: Quản lý logic kịch bản, biết được bước nào là hội thoại, bước nào là di chuyển.
4.  **MapRenderer**: Chịu trách nhiệm render hình ảnh bản đồ sân bay và các lớp đồ họa máy bay đè lên trên.
