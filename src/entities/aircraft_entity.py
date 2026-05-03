import math


class AircraftEntity:
    """
    Đại diện cho một máy bay trong không gian mô phỏng.
    """

    STRAIGHT_SPEED = 5.0
    CURVE_SPEED = 2.78
    ACCELERATION = 2.0  # m/s^2

    def __init__(self, ac_id, callsign, x, y, initial_angle=0.0):
        self.id = ac_id
        self.callsign = callsign
        self.x = float(x)
        self.y = float(y)
        self.angle = float(initial_angle)  # Hướng mũi máy bay (độ)

        # Trạng thái di chuyển
        self.target_path = []  # Danh sách waypoints còn lại
        self.target_speed = 0.0
        self.current_speed = 0.0
        self.is_moving = False
        # Khoảng cách coi như đã đến điểm (pixels)
        self.arrival_threshold = 2.0

    def set_path(self, path, speed=None):
        """Thiết lập lộ trình mới cho máy bay."""
        # Chuyển đổi tọa độ sang float để tính toán chính xác
        self.target_path = [
            {"x": float(p['x']), "y": float(p['y'])} for p in path]
        
        # Neu khong truyen speed, mac dinh dung STRAIGHT_SPEED
        self.target_speed = float(speed) if speed is not None else self.STRAIGHT_SPEED
        self.is_moving = len(self.target_path) > 0

    def teleport(self, pos):
        """Nhảy vọt máy bay đến vị trí mới và dừng mọi hành trình cũ."""
        self.x = float(pos['x'])
        self.y = float(pos['y'])
        self.target_path = []
        self.is_moving = False
        self.current_speed = 0.0

    def complete_path(self):
        """Lap tuc hoan thanh hanh trinh hien tai (nhay den waypoint cuoi cung)."""
        if self.target_path:
            last_target = self.target_path[-1]
            
            # Tinh toan goc quay truoc khi teleport
            if len(self.target_path) >= 2:
                p1 = self.target_path[-2]
                p2 = self.target_path[-1]
                dx = p2['x'] - p1['x']
                dy = p2['y'] - p1['y']
            else:
                dx = last_target['x'] - self.x
                dy = last_target['y'] - self.y
            
            if dx != 0 or dy != 0:
                self.angle = math.degrees(math.atan2(dy, dx))
                
            self.teleport(last_target)

    def set_angle(self, angle: float):
        """Dat goc quay cua may bay (do), dung cho lenh ROTATE."""
        self.angle = float(angle)

    def _calculate_dynamic_speed(self):
        """Tinh toan toc do muc tieu dua tren do cong cua duong di."""
        if len(self.target_path) < 2:
            return self.target_speed

        # Lay vector hien tai (tu vi tri hien tai den waypoint 0)
        p0 = self.target_path[0]
        v1_x = p0['x'] - self.x
        v1_y = p0['y'] - self.y

        # Lay vector tiep theo (tu waypoint 0 den waypoint 1)
        p1 = self.target_path[1]
        v2_x = p1['x'] - p0['x']
        v2_y = p1['y'] - p0['y']

        # Tinh goc giua hai vector
        mag1 = math.sqrt(v1_x**2 + v1_y**2)
        mag2 = math.sqrt(v2_x**2 + v2_y**2)

        if mag1 < 0.1 or mag2 < 0.1:
            return self.target_speed

        # Dot product / (mag1 * mag2) = cos(theta)
        cos_theta = (v1_x * v2_x + v1_y * v2_y) / (mag1 * mag2)
        # Kep gia tri trong [-1, 1] de tranh loi math domain
        cos_theta = max(-1.0, min(1.0, cos_theta))
        angle_diff = math.degrees(math.acos(cos_theta))

        # Neu goc cua > 15 do -> Dung toc do cua
        if angle_diff > 15:
            return self.CURVE_SPEED
        return self.STRAIGHT_SPEED

    def update(self, delta_time):
        """
        Cập nhật vị trí dựa trên Delta Time và lộ trình.
        """
        if not self.is_moving or not self.target_path:
            self.is_moving = False
            self.current_speed = 0.0
            return

        # 1. Cap nhat toc do muc tieu va gia toc
        dynamic_target = self._calculate_dynamic_speed()
        if self.current_speed < dynamic_target:
            self.current_speed = min(self.current_speed + self.ACCELERATION * delta_time, dynamic_target)
        elif self.current_speed > dynamic_target:
            self.current_speed = max(self.current_speed - self.ACCELERATION * delta_time, dynamic_target)

        # 2. Di chuyen
        target = self.target_path[0]
        dx = target['x'] - self.x
        dy = target['y'] - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance > self.arrival_threshold:
            move_dist = self.current_speed * delta_time
            ratio = min(move_dist / distance, 1.0)

            self.x += dx * ratio
            self.y += dy * ratio
            self.angle = math.degrees(math.atan2(dy, dx))
        else:
            self.x = target['x']
            self.y = target['y']
            self.target_path.pop(0)

            if not self.target_path:
                self.is_moving = False
                self.current_speed = 0.0

    def get_pos(self):
        return {"x": self.x, "y": self.y}
