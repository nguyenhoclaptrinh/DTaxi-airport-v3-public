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
        self.map_renderer = MapRenderer(800, 600)
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
    def setup(self):
        """Khoi phoi du lieu ban dau."""
        try:
            self.map_renderer.init_pygame()
            self.load_scenario("dep_01.json")
        except Exception as e:
            print(f"Setup Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

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
            )
            self.aircraft_entities.append(entity)

        self.ui_manager.clear_log()
        self._apply_step(current_step, start_movement=False)

        info = self.scenario_manager.get_scenario_info()
        self.ui_manager.set_status(f"Loaded: {info.get('name', filename)}")

    # ------------------------------------------------------------------
    # Xu ly Step Atomic
    # ------------------------------------------------------------------
    def _apply_step(self, step: dict | None, start_movement: bool = True):
        """Ap dung noi dung cua mot step nguyen tu."""
        if not step:
            self.ui_manager.set_status("Kich ban da ket thuc.")
            return

        step_type = step.get("type")
        step_id = step.get("id", "?")

        if step_type == "MESSAGE":
            sender = step.get("sender", "?")
            target = step.get("target", "?")
            text = step.get("text", "")
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
                self.ui_manager.set_status(
                    f"[{step_id}] {ac_id} ROTATE {angle}deg")

            elif action == "MOVE_ALONG_PATH":
                path_name = step.get("path_name", "")
                speed = step.get("speed", 5)
                path_coords = self.scenario_manager.resolve_path(path_name)
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
        """Chuyen sang step tiep theo."""
        # Hoan thanh chuyen dong hien tai neu co
        current = self.scenario_manager.get_current_step()
        if current and current.get("type") == "ACTION":
            ac_id = current.get("aircraft")
            for entity in self.aircraft_entities:
                if entity.id == ac_id:
                    entity.complete_path()

        step = self.scenario_manager.next_step()
        self._apply_step(step, start_movement=True)

    def handle_prev(self):
        """Quay lai step truoc."""
        step = self.scenario_manager.prev_step()
        if step:
            # Dua may bay ve dau path neu la MOVE action
            if step.get("type") == "ACTION" and step.get("action") == "MOVE_ALONG_PATH":
                path_coords = self.scenario_manager.resolve_path(
                    step.get("path_name", ""))
                if path_coords:
                    ac_id = step.get("aircraft")
                    for entity in self.aircraft_entities:
                        if entity.id == ac_id:
                            entity.teleport(path_coords[0])
            self._apply_step(step, start_movement=False)

    def handle_stop(self):
        """Tam dung tai step hien tai."""
        self.scenario_manager.stop()
        info = self.scenario_manager.get_scenario_info()
        self.ui_manager.set_status(
            f"PAUSED at step {info.get('current_step')}/{info.get('total_steps')}")

    def handle_reset(self):
        """Dat lai kich ban."""
        step = self.scenario_manager.reset()
        for entity in self.aircraft_entities:
            new_pos = self.scenario_manager.aircraft_states[entity.id]["pos"]
            entity.teleport(new_pos)
        self._apply_step(step, start_movement=False)
        self.ui_manager.set_status("Scenario Reset")

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

            # Cap nhat logic
            for entity in self.aircraft_entities:
                entity.update(delta_time)
                self.scenario_manager.update_aircraft_pos(
                    entity.id, {"x": entity.x, "y": entity.y})

            # Ve ban do
            current_step = self.scenario_manager.get_current_step()
            active_path = None
            if current_step and current_step.get("action") == "MOVE_ALONG_PATH":
                active_path = self.scenario_manager.resolve_path(
                    current_step.get("path_name", "")
                )

            self.map_renderer.draw(
                self.aircraft_entities,
                active_path=active_path,
            )

        except Exception as e:
            print(f"Update Loop Warning: {e}")

        if self.running:
            self.ui_manager.root.after(20, self.update_loop)


if __name__ == "__main__":
    app = DTaxiApp()
    app.run()
