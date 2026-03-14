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
        
        # Màu sắc cơ bản
        self.COLOR_BG = (30, 30, 30) # Dark theme
        self.COLOR_PATH = (100, 100, 100)
        self.COLOR_TEXT = (255, 255, 255)

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
        map_path = os.path.join("assets", "images", "airport_map.png")
        if os.path.exists(map_path):
            self.background_image = pygame.image.load(map_path).convert()
            self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))
        
        ac_path = os.path.join("assets", "images", "aircraft_icon.png")
        if os.path.exists(ac_path):
            self.aircraft_icon = pygame.image.load(ac_path).convert_alpha()
            icon_size = (32, 32) 
            self.aircraft_icon = pygame.transform.scale(self.aircraft_icon, icon_size)
        else:
            self.aircraft_icon = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.polygon(self.aircraft_icon, (255, 200, 0), [(15, 0), (30, 30), (15, 22), (0, 30)])

    def draw(self, aircraft_entities, current_step=None):
        """Vẽ toàn bộ các thành phần lên màn hình."""
        if not self.screen:
            return

        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill(self.COLOR_BG)

        if current_step and 'path' in current_step:
            path = current_step['path']
            if len(path) > 1:
                points = [(p['x'], p['y']) for p in path]
                pygame.draw.lines(self.screen, self.COLOR_PATH, False, points, 2)

        for ac in aircraft_entities:
            rotated_icon = pygame.transform.rotate(self.aircraft_icon, -ac.angle)
            rect = rotated_icon.get_rect(center=(ac.x, ac.y))
            self.screen.blit(rotated_icon, rect.topleft)
            
            # Sử dụng font đã cache
            label = self.label_font.render(ac.callsign, True, (0, 255, 0))
            self.screen.blit(label, (ac.x + 20, ac.y - 10))

        pygame.display.update() # update() thường nhẹ hơn flip() trong một số trường hợp
