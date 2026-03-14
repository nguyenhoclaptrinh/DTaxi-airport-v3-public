import pygame
import os
import sys
import time
from engine.scenario_manager import ScenarioManager
from entities.aircraft_entity import AircraftEntity
from ui.map_renderer import MapRenderer
from ui.window_manager import WindowManager

class DTaxiApp:
    def __init__(self):
        self.scenario_manager = ScenarioManager()
        self.map_renderer = MapRenderer(800, 600)
        self.ui_manager = WindowManager(
            on_next=self.handle_next,
            on_prev=self.handle_prev,
            on_reset=self.handle_reset
        )
        
        self.aircraft_entities = []
        self.clock = pygame.time.Clock()
        self.running = True

    def setup(self):
        """Khởi phối dữ liệu ban đầu."""
        scenario_path = os.path.join("data", "scenarios", "departure_sample.json")
        try:
            current_step = self.scenario_manager.load_scenario(scenario_path)
            self.map_renderer.init_pygame()
            
            # Khởi tạo thực thể máy bay từ kịch bản
            for ac_id, data in self.scenario_manager.aircraft_states.items():
                entity = AircraftEntity(ac_id, data['callsign'], data['pos'])
                self.aircraft_entities.append(entity)
            
            self._trigger_step_actions(current_step)
            self.ui_manager.set_status(f"Loaded: {self.scenario_manager.scenario_data['scenario_name']}")
            
        except Exception as e:
            print(f"Setup Error: {e}")
            sys.exit(1)

    def _trigger_step_actions(self, step):
        """Kích hoạt hành động và tin nhắn khi chuyển bước."""
        if not step:
            return
            
        # 1. Kích hoạt tin nhắn AeroMACS
        for msg in step.get('messages', []):
            self.ui_manager.add_log(msg['sender'], msg['text'], msg.get('target'))
            
        # 2. Kích hoạt di chuyển cho máy bay active
        ac_id = step.get('active_aircraft')
        if ac_id:
            for entity in self.aircraft_entities:
                if entity.id == ac_id:
                    entity.set_path(step['path'], step['speed'])

    def handle_next(self):
        step = self.scenario_manager.next_step()
        if step:
            self._trigger_step_actions(step)
            self.ui_manager.set_status(f"Step {step['id']}: {step['label']}")
        else:
            self.ui_manager.set_status("Kịch bản đã hoàn thành.")

    def handle_prev(self):
        # Lưu ý: Logic Prev thực tế cần reset vị trí máy bay về đầu bước trước
        step = self.scenario_manager.prev_step()
        if step:
            self.ui_manager.clear_log() # Hoặc giữ lại tùy thiết kế
            # Trong mô phỏng đơn giản, ta Reset vị trí về đầu kịch bản hoặc vị trí bước trước
            # TODO: Hoàn thiện logic quay lui vị trí chính xác
            self._trigger_step_actions(step)
            self.ui_manager.set_status(f"Back to Step {step['id']}")

    def handle_reset(self):
        step = self.scenario_manager.reset()
        self.ui_manager.clear_log()
        for entity in self.aircraft_entities:
            # Reset vị trí thực thể
            idx = next(i for i, ac in enumerate(self.scenario_manager.scenario_data['aircraft_list']) if ac['id'] == entity.id)
            init_pos = self.scenario_manager.scenario_data['aircraft_list'][idx]['initial_pos']
            entity.x, entity.y = float(init_pos['x']), float(init_pos['y'])
            entity.target_path = []
            entity.is_moving = False
        self._trigger_step_actions(step)
        self.ui_manager.set_status("Scenario Reset")

    def run(self):
        self.setup()
        
        while self.running:
            # 1. Cửa sổ Pygame
            delta_time = self.clock.tick(60) / 1000.0 # Giới hạn 60 FPS
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            # Cập nhật vị trí máy bay
            for entity in self.aircraft_entities:
                entity.update(delta_time)
            
            # Vẽ Map
            self.map_renderer.draw(self.aircraft_entities, self.scenario_manager.get_current_step())
            
            # 2. Cửa sổ UI (CustomTkinter)
            try:
                self.ui_manager.run_step()
            except Exception:
                # Nếu cửa sổ UI bị đóng
                self.running = False

        pygame.quit()

if __name__ == "__main__":
    app = DTaxiApp()
    app.run()
