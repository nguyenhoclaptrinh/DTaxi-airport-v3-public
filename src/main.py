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
        metadata_path = os.path.join("data", "vvts_metadata.json")
        try:
            current_step = self.scenario_manager.load_scenario(scenario_path, metadata_path)
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

    def _trigger_step_actions(self, step, start_movement=True):
        """Kích hoạt hành động và tin nhắn khi chuyển bước."""
        if not step:
            return
            
        # 1. Kích hoạt tin nhắn AeroMACS
        for msg in step.get('messages', []):
            self.ui_manager.add_log(msg['sender'], msg['text'], msg.get('target'))
            
        # 2. Kích hoạt di chuyển cho máy bay active (nếu được phép)
        if start_movement:
            ac_id = step.get('active_aircraft')
            if ac_id:
                for entity in self.aircraft_entities:
                    if entity.id == ac_id:
                        entity.set_path(step['path'], step['speed'])

    def handle_next(self):
        # 1. Hoàn thành hành động của bước hiện tại trước khi sang bước mới
        current_step = self.scenario_manager.get_current_step()
        if current_step:
            ac_id = current_step.get('active_aircraft')
            if ac_id:
                for entity in self.aircraft_entities:
                    if entity.id == ac_id:
                        entity.complete_path()

        # 2. Chuyển sang bước tiếp theo
        step = self.scenario_manager.next_step()
        if step:
            self._trigger_step_actions(step, start_movement=True)
            self.ui_manager.set_status(f"Step {step['id']}: {step['label']}")
        else:
            self.ui_manager.set_status("Kịch bản đã hoàn thành.")

    def handle_prev(self):
        # 1. Quay lại bước trước đó
        step = self.scenario_manager.prev_step()
        if step:
            # 2. Đưa máy bay về điểm xuất phát của bước này
            ac_id = step.get('active_aircraft')
            if ac_id and 'path' in step and step['path']:
                start_pos = step['path'][0]
                for entity in self.aircraft_entities:
                    if entity.id == ac_id:
                        entity.teleport(start_pos)

            self.ui_manager.clear_log() 
            # 3. Chỉ hiện tin nhắn, KHÔNG tự động di chuyển
            self._trigger_step_actions(step, start_movement=False)
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
        self._last_time = time.perf_counter()
        # Bắt đầu vòng lặp đồ họa thông qua Tkinter after
        self.update_loop()
        
        # Giao quyền điều khiển chính cho Tkinter Mainloop
        self.ui_manager.root.mainloop()
        
        # Khi thoát mainloop (đóng cửa sổ UI)
        self.running = False
        pygame.quit()

    def update_loop(self):
        """Vòng lặp cập nhật an toàn với GIL."""
        if not self.running:
            return

        try:
            # 1. Tính toán delta_time thủ công để tránh gọi clock.tick() gây giải phóng GIL
            now = time.perf_counter()
            delta_time = now - self._last_time
            self._last_time = now
            
            # Đảm bảo delta_time không quá lớn (ví dụ khi treo máy)
            delta_time = min(delta_time, 0.1) 

            # 2. Xử lý sự kiện Pygame tối giản
            # Dùng pump() để duy trì phản hồi cửa sổ mà không cần loop qua event queue
            pygame.event.pump()

            # 3. Cập nhật Logic
            for entity in self.aircraft_entities:
                entity.update(delta_time)
            
            # 4. Vẽ Map
            self.map_renderer.draw(self.aircraft_entities, self.scenario_manager.get_current_step())
            
        except Exception as e:
            print(f"Update Loop Warning: {e}")
        
        # 5. Lên lịch cho lần cập nhật tiếp theo (khoảng 20ms ~ 50FPS để giảm tải)
        if self.running:
            self.ui_manager.root.after(20, self.update_loop)

if __name__ == "__main__":
    app = DTaxiApp()
    app.run()
