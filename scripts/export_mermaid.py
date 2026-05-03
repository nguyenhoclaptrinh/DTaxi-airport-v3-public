import zlib
import base64
import requests
import os

mermaid_code = """graph LR
    subgraph MainFlow [DTaxi System Flow]
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
        N -- Yes --> O[Kiểm tra điều kiện Auto-Next]
        O --> P[Tự động chuyển Step nếu máy bay dừng]
    end
    
    I --> Q[MapRenderer: Vẽ lại toàn bộ Scene]
    Q --> R[WindowManager: Cập nhật Log & Status]
    
    R --> S{Sự kiện từ người dùng?}
    S -- NEXT/PREV --> T[Điều hướng kịch bản]
    S -- STOP/RESUME --> U[Bật/Tắt Pause]
    S -- Slider --> V[Thay đổi Sim Speed]
    
    T --> I
    U --> I
    V --> I
    P --> I
    end"""

def export_mermaid_kroki():
    # Kroki algorithm: UTF-8 -> Zlib Compress -> Base64 URL Safe
    payload = mermaid_code.encode('utf-8')
    compressed = zlib.compress(payload, 9)
    encoded = base64.urlsafe_b64encode(compressed).decode('ascii')
    
    url = f"https://kroki.io/mermaid/png/{encoded}"
    
    print(f"Dang tai anh tu Kroki: {url}")
    response = requests.get(url)
    
    if response.status_code == 200:
        output_path = "docs/040-Diagrams/Main_Flow.png"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"Da luu anh vao: {output_path}")
    else:
        print(f"Loi khi tai anh tu Kroki: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    export_mermaid_kroki()
