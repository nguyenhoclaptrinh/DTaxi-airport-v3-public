import json
import os

class ScenarioManager:
    """
    Quản lý luồng thực thi của một kịch bản mô phỏng.
    """
    def __init__(self):
        self.scenario_data = None
        self.current_step_index = -1
        self.aircraft_states = {} # Lưu vị trí và trạng thái của từng máy bay

    def load_scenario(self, file_path):
        """Đọc và khởi tạo dữ liệu kịch bản từ file JSON."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Không tìm thấy file kịch bản tại: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            self.scenario_data = json.load(f)
        
        # Khởi tạo trạng thái ban đầu cho các máy bay
        for ac in self.scenario_data.get('aircraft_list', []):
            self.aircraft_states[ac['id']] = {
                'pos': ac['initial_pos'].copy(),
                'callsign': ac['callsign'],
                'type': ac['type']
            }
        
        self.current_step_index = 0
        return self.get_current_step()

    def get_current_step(self):
        """Lấy dữ liệu của bước hiện tại."""
        if self.scenario_data and 0 <= self.current_step_index < len(self.scenario_data['steps']):
            return self.scenario_data['steps'][self.current_step_index]
        return None

    def next_step(self):
        """Chuyển sang bước tiếp theo."""
        if self.scenario_data and self.current_step_index < len(self.scenario_data['steps']) - 1:
            self.current_step_index += 1
            return self.get_current_step()
        return None

    def prev_step(self):
        """Quay lại bước trước đó."""
        if self.current_step_index > 0:
            self.current_step_index -= 1
            return self.get_current_step()
        return None

    def reset(self):
        """Đặt lại kịch bản về trạng thái ban đầu."""
        self.current_step_index = 0
        # Reset vị trí máy bay về initial_pos
        for ac in self.scenario_data.get('aircraft_list', []):
            self.aircraft_states[ac['id']]['pos'] = ac['initial_pos'].copy()
        return self.get_current_step()

    def update_aircraft_pos(self, ac_id, new_pos):
        """Cập nhật tọa độ thực tế của máy bay (gọi từ engine vật lý)."""
        if ac_id in self.aircraft_states:
            self.aircraft_states[ac_id]['pos'] = new_pos
