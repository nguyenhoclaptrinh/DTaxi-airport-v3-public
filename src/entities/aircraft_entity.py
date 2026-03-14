import math

class AircraftEntity:
    """
    Đại diện cho một máy bay trong không gian mô phỏng.
    """
    def __init__(self, ac_id, callsign, initial_pos):
        self.id = ac_id
        self.callsign = callsign
        self.x = float(initial_pos['x'])
        self.y = float(initial_pos['y'])
        self.angle = 0.0 # Hướng mũi máy bay (độ)
        
        # Trạng thái di chuyển
        self.target_path = [] # Danh sách waypoints còn lại
        self.current_speed = 0.0
        self.is_moving = False
        self.arrival_threshold = 2.0 # Khoảng cách coi như đã đến điểm (pixels)

    def set_path(self, path, speed):
        """Thiết lập lộ trình mới cho máy bay."""
        # Chuyển đổi tọa độ sang float để tính toán chính xác
        self.target_path = [{"x": float(p['x']), "y": float(p['y'])} for p in path]
        self.current_speed = float(speed)
        self.is_moving = len(self.target_path) > 0

    def update(self, delta_time):
        """
        Cập nhật vị trí dựa trên Delta Time và lộ trình.
        """
        if not self.is_moving or not self.target_path:
            self.is_moving = False
            return

        target = self.target_path[0]
        dx = target['x'] - self.x
        dy = target['y'] - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance > self.arrival_threshold:
            # Tính toán vector di chuyển
            move_dist = self.current_speed * delta_time
            # Đảm bảo không đi quá đích
            ratio = min(move_dist / distance, 1.0)
            
            self.x += dx * ratio
            self.y += dy * ratio
            
            # Cập nhật góc quay (math.atan2 trả về radian, chuyển sang độ)
            # Pygame góc 0 là hướng phải, quay theo chiều kim đồng hồ
            self.angle = math.degrees(math.atan2(dy, dx))
        else:
            # Đã đến waypoint hiện tại, chuyển sang waypoint tiếp theo
            self.x = target['x']
            self.y = target['y']
            self.target_path.pop(0)
            
            if not self.target_path:
                self.is_moving = False

    def get_pos(self):
        return {"x": self.x, "y": self.y}
