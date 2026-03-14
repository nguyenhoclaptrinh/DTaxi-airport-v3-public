class AircraftEntity:
    """
    Đại diện cho một máy bay trong không gian mô phỏng.
    """
    def __init__(self, ac_id, callsign, initial_pos):
        self.id = ac_id
        self.callsign = callsign
        self.x = initial_pos['x']
        self.y = initial_pos['y']
        
        # Trạng thái di chuyển
        self.target_path = [] # Danh sách waypoints còn lại
        self.current_speed = 0
        self.is_moving = False

    def set_path(self, path, speed):
        """Thiết lập lộ trình mới cho máy bay."""
        self.target_path = list(path)
        self.current_speed = speed
        self.is_moving = len(self.target_path) > 0

    def update(self, delta_time):
        """
        Cập nhật vị trí dựa trên Delta Time và lộ trình.
        Logic Lerp (Nội suy) sẽ được chi tiết hóa khi tích hợp với Frame Loop của Pygame.
        """
        if not self.is_moving or not self.target_path:
            return

        # TODO: Triển khai logic nội suy tọa độ mượt mà tại đây
        pass

    def get_pos(self):
        return {"x": self.x, "y": self.y}
