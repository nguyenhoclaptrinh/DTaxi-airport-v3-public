import pygame
import os


class MapRenderer:
    """
    Xử lý việc vẽ bản đồ sân bay và các thực thể máy bay bằng Pygame.
    """

    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.screen = None
        self.background_image = None
        self.aircraft_icon = None
        self.debug_mode = True  # Thống nhất debug mode

        # Màu sắc cơ bản
        self.COLOR_BG = (30, 30, 30)  # Dark theme
        self.COLOR_PATH = (100, 100, 100)
        self.COLOR_TEXT = (255, 255, 255)
        self.COLOR_DEBUG = (255, 0, 255)  # Pink for debug

    def init_pygame(self, embed_window_id=None):
        """Khởi tạo Pygame display và font."""
        if embed_window_id:
            os.environ['SDL_WINDOWID'] = str(embed_window_id)
            os.environ['SDL_VIDEODRIVER'] = 'windib'

        pygame.display.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("DTaxi - Airport Visualization")

        self.load_assets()
        # Khởi tạo font một lần duy nhất
        self.label_font = pygame.font.SysFont("Arial", 14, bold=True)

    def load_assets(self):
        """Tải các tệp hình ảnh."""
        # Ưu tiên tsn_airport_map_1.jpg, nếu không có thì dùng tsn_airport_map.jpg
        map_path_new = os.path.join("assets", "images", "tsn_airport_map_1.jpg")
        map_path_old = os.path.join("assets", "images", "tsn_airport_map.jpg")
        map_path_png = os.path.join("assets", "images", "airport_map.png")

        if os.path.exists(map_path_new):
            target_path = map_path_new
        elif os.path.exists(map_path_old):
            target_path = map_path_old
        else:
            target_path = map_path_png

        if os.path.exists(target_path):
            self.background_image = pygame.image.load(target_path).convert()
            self.background_image = pygame.transform.scale(
                self.background_image, (self.width, self.height))

        ac_path = os.path.join("assets", "images", "aircraft_icon.png")
        if os.path.exists(ac_path):
            self.aircraft_icon = pygame.image.load(ac_path).convert_alpha()
            icon_size = (32, 32)
            self.aircraft_icon = pygame.transform.scale(
                self.aircraft_icon, icon_size)
        else:
            self.aircraft_icon = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.polygon(self.aircraft_icon, (255, 200, 0), [
                                (15, 0), (30, 30), (15, 22), (0, 30)])

    def draw(self, aircraft_entities, active_path=None, current_time_str="00:00:00"):
        """Ve toan bo cac thanh phan len man hinh."""
        if not self.screen:
            return

        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill(self.COLOR_BG)

        # Ve Path dang active
        if active_path and len(active_path) > 1:
            points = [(int(p["x"]), int(p["y"])) for p in active_path]
            pygame.draw.lines(self.screen, (255, 220, 0), False, points, 2)
            for p in points:
                pygame.draw.circle(self.screen, (255, 140, 0), p, 4)

        # Ve may bay
        for ac in aircraft_entities:
            # Bù góc -90 độ vì icon gốc hướng lên trên (North), 
            # trong khi logic di chuyển coi 0 độ là bên phải (East).
            rotated_icon = pygame.transform.rotate(
                self.aircraft_icon, -ac.angle - 90)
            rect = rotated_icon.get_rect(center=(int(ac.x), int(ac.y)))
            self.screen.blit(rotated_icon, rect.topleft)

            label = self.label_font.render(ac.callsign, True, (0, 255, 0))
            self.screen.blit(label, (int(ac.x) + 20, int(ac.y) - 10))

        # Ve dong ho (Time clock)
        if current_time_str:
            time_font = pygame.font.SysFont("Consolas", 24, bold=True)
            time_surface = time_font.render(f"SIM TIME: {current_time_str} UTC+7", True, (0, 255, 255))
            rect = time_surface.get_rect(topright=(self.width - 20, 20))
            bg_rect = rect.copy()
            bg_rect.inflate_ip(20, 10)
            # Ve hop den vien cyan
            pygame.draw.rect(self.screen, (20, 20, 20), bg_rect)
            pygame.draw.rect(self.screen, (0, 255, 255), bg_rect, 2)
            self.screen.blit(time_surface, rect)

        pygame.display.update()
