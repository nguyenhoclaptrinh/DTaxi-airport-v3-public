import pygame
import os
import sys
import time
from engine.scenario_manager import ScenarioManager
from entities.aircraft_entity import AircraftEntity
from ui.map_renderer import MapRenderer
from ui.window_manager import WindowManager


class DTaxiApp:
    """Ung dung mo phong mat dat san bay DTaxi."""

    SCENARIO_DIR = os.path.join("data", "scenarios")

    def __init__(self):
        self.scenario_manager = ScenarioManager()
        self.map_renderer = MapRenderer(1200, 744)
        self.ui_manager = WindowManager(
            on_next=self.handle_next,
            on_prev=self.handle_prev,
            on_reset=self.handle_reset,
            on_stop=self.handle_stop,
            on_scenario_change=self.handle_scenario_change,
        )

        self.aircraft_entities: list[AircraftEntity] = []
        self.clock = pygame.time.Clock()
        self.running = True

    # ------------------------------------------------------------------
    # Khoi tao
    # ------------------------------------------------------------------
    def set_stop_state(self, paused: bool):
        """Cap nhat trang thai nut Stop/Resume."""
        self.ui_manager.set_stop_state(paused)

    def setup(self):
        """Khoi phoi du lieu ban dau."""
        try:
            self.map_renderer.init_pygame()
            
            # Quet danh sach kich ban thuc te
            scenarios = self.get_available_scenarios()
            self.ui_manager.set_scenario_list(scenarios)

            if scenarios:
                self.load_scenario(scenarios[0])
            else:
                self.ui_manager.set_status("❌ Error: No scenarios found in data/scenarios")
                
        except Exception as e:
            print(f"Setup Error: {e}")
            import traceback
            traceback.print_exc()
            # Khong sys.exit nua de user co the reload sau khi fix file
            self.ui_manager.set_status(f"Critical Error: {str(e)}")

    def get_available_scenarios(self) -> list[str]:
        """Lay danh sach cac file .json trong thu muc scenarios."""
        if not os.path.exists(self.SCENARIO_DIR):
            return []
        
        files = [f for f in os.listdir(self.SCENARIO_DIR) if f.endswith(".json")]
        return sorted(files)

    def load_scenario(self, filename: str):
        """Tai kich ban tu ten file."""
        scenario_path = os.path.join(self.SCENARIO_DIR, filename)
        current_step = self.scenario_manager.load_scenario(scenario_path)

        # Khoi tao entity may bay
        self.aircraft_entities = []
        for ac_id, ac_data in self.scenario_manager.aircraft_states.items():
            entity = AircraftEntity(
                ac_id,
                ac_data["callsign"],
                ac_data["pos"]["x"],
                ac_data["pos"]["y"],
                initial_angle=ac_data.get("angle", 0.0)
            )
            self.aircraft_entities.append(entity)

        self.ui_manager.clear_log()
        # Voi index -1, setup ban dau se khong goi _apply_step hoac chi goi de show 'Ready'
        self._apply_step(current_step, start_movement=False)

        info = self.scenario_manager.get_scenario_info()
        self.ui_manager.set_status(f"Loaded: {info.get('name', filename)}")

    # ------------------------------------------------------------------
    # Xu ly Step Atomic
    # ------------------------------------------------------------------
    def _apply_step(self, step: dict | None, start_movement: bool = True, add_to_log: bool = True):
        """Ap dung noi dung cua mot step nguyen tu."""
        if not step:
            if self.scenario_manager.current_step_index == -1:
                self.ui_manager.set_status("Sẵn sàng bắt đầu kịch bản. Nhấn NEXT.")
            else:
                self.ui_manager.set_status("Kịch bản đã kết thúc.")
            return

        step_type = step.get("type")
        step_id = step.get("id", "?")

        if step_type == "MESSAGE":
            sender = step.get("sender", "?")
            target = step.get("target", "?")
            text = step.get("text", "")
            if add_to_log:
                self.ui_manager.add_log(sender, text, target)
            label = f"[{step_id}] {sender} -> {target}"
            self.ui_manager.set_status(label)

        elif step_type == "ACTION":
            action = step.get("action")
            ac_id = step.get("aircraft")

            if action == "ROTATE":
                angle = step.get("value", 0)
                for entity in self.aircraft_entities:
                    if entity.id == ac_id:
                        entity.set_angle(angle)
                
                if add_to_log:
                    self.ui_manager.add_log("SYSTEM", f"{ac_id} rotated to {angle}°")
                
                self.ui_manager.set_status(
                    f"[{step_id}] {ac_id} ROTATE {angle}deg")

            elif action == "MOVE_ALONG_PATH":
                path_name = step.get("path_name", "")
                speed = step.get("speed", 5)
                path_coords = self.scenario_manager.resolve_path(path_name)
                
                if add_to_log:
                    self.ui_manager.add_log("SYSTEM", f"{ac_id} moving via '{path_name}' (Speed: {speed})")

                if start_movement and path_coords:
                    for entity in self.aircraft_entities:
                        if entity.id == ac_id:
                            entity.set_path(path_coords, speed)
                self.ui_manager.set_status(
                    f"[{step_id}] {ac_id} MOVE via '{path_name}'")

            else:
                self.ui_manager.set_status(f"[{step_id}] ACTION: {action}")

    # ------------------------------------------------------------------
    # Callbacks tu UI
    # ------------------------------------------------------------------
    def handle_next(self):
        """Chuyen sang step tiep theo hoac hoan thanh hanh dong dang chay."""
        current = self.scenario_manager.get_current_step()
        
        # 1. Kiem tra neu co hanh dong dang chay thi chi hoan thanh no (Khong chuyen step)
        if current and current.get("type") == "ACTION":
            ac_id = current.get("aircraft")
            for entity in self.aircraft_entities:
                if entity.id == ac_id and entity.is_moving:
                    entity.complete_path()
                    self.ui_manager.set_status(f"Hành động hoàn tất: {ac_id}")
                    return # Dung lai o day, khong chuyen sang step tiep theo

        # 2. Neu khong co hanh dong chay, thuc hien step tiep theo nhu binh thuong
        step = self.scenario_manager.next_step()
        self._apply_step(step, start_movement=True)

    def handle_prev(self):
        """Quay lai step truoc."""
        current = self.scenario_manager.get_current_step()
        if not current:
            return

        # 1. Hoan tac (Undo) step HIEN TAI
        if current.get("type") in ["MESSAGE", "ACTION"]:
            self.ui_manager.remove_last_log()
            
        if current.get("type") == "ACTION" and current.get("action") == "MOVE_ALONG_PATH":
            path_coords = self.scenario_manager.resolve_path(current.get("path_name", ""))
            if path_coords:
                ac_id = current.get("aircraft")
                for entity in self.aircraft_entities:
                    if entity.id == ac_id:
                        # Quay ve diem BAT DAU cua path (Undo move)
                        entity.teleport(path_coords[0])

        # 2. Lui pointer
        step = self.scenario_manager.prev_step()
        
        # 3. Hien thi status cua step moi (nhung khong move hay ghi log)
        if step:
            self._apply_step(step, start_movement=False, add_to_log=False)
        else:
            self.ui_manager.set_status("Sẵn sàng bắt đầu kịch bản.")

    def handle_stop(self):
        """Tam dung hoac tiep tuc mo phong (Toggle)."""
        if self.scenario_manager.is_paused:
            self.scenario_manager.resume()
            self.ui_manager.set_status("Simulation Resumed")
        else:
            self.scenario_manager.stop()
            self.ui_manager.set_status("Simulation Paused")
            
        self.ui_manager.set_stop_state(self.scenario_manager.is_paused)

    def handle_reset(self):
        """Dat lai kich ban."""
        self.scenario_manager.reset()
        for entity in self.aircraft_entities:
            ac_id = entity.id
            # Lay initial state tu aircraft_list trong scenario_data
            for ac_info in self.scenario_manager.scenario_data.get("aircraft_list", []):
                if ac_info["id"] == ac_id:
                    init_pos = ac_info.get("initial_pos", {"x": 0, "y": 0})
                    entity.teleport(init_pos)
                    # Goc quay lay tu states cua manager (da auto-calc)
                    state = self.scenario_manager.aircraft_states.get(ac_id, {})
                    entity.set_angle(state.get("angle", 0.0))
        
        self.ui_manager.clear_log()
        self.ui_manager.set_status("Scenario Reset. Sẵn sàng bắt đầu.")

    def handle_scenario_change(self, filename: str):
        """Thay doi kich ban theo ten file."""
        self.load_scenario(filename)

    # ------------------------------------------------------------------
    # Vong lap chinh
    # ------------------------------------------------------------------
    def run(self):
        self.setup()
        self._last_time = time.perf_counter()
        self.update_loop()
        self.ui_manager.root.mainloop()
        self.running = False
        pygame.quit()

    def update_loop(self):
        """Vong lap cap nhat an toan."""
        if not self.running:
            return

        try:
            now = time.perf_counter()
            delta_time = min(now - self._last_time, 0.1)
            self._last_time = now

            # Xu ly su kien Pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.ui_manager.root.quit()
                    return

            pygame.event.pump()

            # Cap nhat logic may bay (Chi khi khong bi Pause)
            if not self.scenario_manager.is_paused:
                for entity in self.aircraft_entities:
                    entity.update(delta_time)
                self.scenario_manager.update_aircraft_pos(
                    entity.id, {"x": entity.x, "y": entity.y})

            # Ve ban do
            current_step = self.scenario_manager.get_current_step()
            active_path = None
            current_time_str = "00:00:00"
            if current_step:
                current_time_str = current_step.get("timestamp", "--:--:--")
                if current_step.get("action") == "MOVE_ALONG_PATH":
                    active_path = self.scenario_manager.resolve_path(
                        current_step.get("path_name", "")
                    )

            self.map_renderer.draw(
                self.aircraft_entities,
                active_path=active_path,
                current_time_str=current_time_str
            )

        except Exception as e:
            print(f"Update Loop Warning: {e}")

        if self.running:
            self.ui_manager.root.after(20, self.update_loop)


if __name__ == "__main__":
    app = DTaxiApp()
    app.run()
