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
        self.metadata = {}

    def load_scenario(self, file_path, metadata_path=None):
        """Tải kịch bản từ file JSON và mapping tọa độ từ Metadata nếu có."""
        self.metadata = {}
        if metadata_path and os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f).get('waypoints', {})

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Không tìm thấy file kịch bản tại: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            self.scenario_data = json.load(f)
            
        self.current_step_index = 0
        self.aircraft_states = {}
        
        # Khởi tạo trạng thái ban đầu cho các máy bay
        for ac in self.scenario_data.get('aircraft_list', []):
            pos = self._resolve_pos(ac['initial_pos'])
            self.aircraft_states[ac['id']] = {
                'callsign': ac['callsign'],
                'pos': pos,
                'type': ac['type'] # Giữ lại 'type' nếu có trong dữ liệu gốc
            }
            
        # Tiền xử lý các bước để mapping Waypoint tên sang tọa độ
        for step in self.scenario_data['steps']:
            if 'path' in step:
                step['path'] = [self._resolve_pos(p) for p in step['path']]
            
        return self.get_current_step()

    def _resolve_pos(self, pos_data):
        """Chuyển đổi tên điểm (STAND_A1) hoặc dict XY sang tọa độ dict chuẩn {x, y}."""
        if isinstance(pos_data, str):
            # Tra cứu từ metadata
            resolved = self.metadata.get(pos_data)
            if resolved:
                return {'x': resolved['x'], 'y': resolved['y']}
            else:
                print(f"Warning: Waypoint '{pos_data}' not found in metadata. Returning {{'x': 0, 'y': 0}}.")
                return {'x': 0, 'y': 0}
        return pos_data # Giả định đã là {x, y}

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
