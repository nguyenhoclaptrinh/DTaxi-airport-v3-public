import json
import os


class ScenarioManager:
    """
    Quan ly luong thuc thi cua mot kich ban mo phong.

    Kich ban su dung cau truc Atomic Events voi hai loai step:
      - MESSAGE: Giao tiep giua PC (Phi cong) va ATC (Kiem soat vien).
      - ACTION:  Hanh dong cua may bay (di chuyen, xoay, ...).

    Dieu huong:
      - next_step(): Chuyen den step tiep theo.
      - prev_step(): Quay lai step truoc.
      - stop():      Tam dung tai step hien tai.
      - go_to_step(step_id): Nhay thang den step theo id.
    """

    PATHS_FILE = os.path.join("data", "paths.json")

    def __init__(self):
        self.scenario_data = None
        self.current_step_index = -1
        self.aircraft_states: dict = {}
        self.paths: dict = {}          # {"path_name": [{"x":..,"y":..}, ...]}
        self._step_index_map: dict = {}  # {step_id: list_index}
        self.is_paused: bool = False

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------
    def load_scenario(self, file_path: str):
        """
        Tai kich ban tu file JSON.
        Paths duoc load tu PATHS_FILE (data/paths.json).
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Khong tim thay kich ban: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            self.scenario_data = json.load(f)

        # Load paths
        self.paths = {}
        if os.path.exists(self.PATHS_FILE):
            with open(self.PATHS_FILE, "r", encoding="utf-8") as f:
                self.paths = json.load(f)

        # Xay dung step_index_map
        self._step_index_map = {}
        steps = self.scenario_data.get("steps", [])
        for idx, step in enumerate(steps):
            step_id = step.get("id")
            if step_id is not None:
                self._step_index_map[step_id] = idx

        # Reset state
        self.current_step_index = 0
        self.is_paused = False
        self.aircraft_states = {}

        # Khoi tao trang thai may bay
        for ac in self.scenario_data.get("aircraft_list", []):
            self.aircraft_states[ac["id"]] = {
                "callsign": ac["callsign"],
                "type": ac.get("type", "Unknown"),
                "pos": dict(ac.get("initial_pos", {"x": 0, "y": 0})),
                "angle": 0.0,
                "speed": 0.0,
            }

        return self.get_current_step()

    # ------------------------------------------------------------------
    # Dieu huong (Navigation)
    # ------------------------------------------------------------------
    def get_current_step(self):
        """Tra ve step hien tai hoac None neu het kich ban."""
        steps = self.scenario_data.get("steps", [])
        if 0 <= self.current_step_index < len(steps):
            return steps[self.current_step_index]
        return None

    def next_step(self):
        """Chuyen sang step tiep theo. Tra ve step moi hoac None neu da het."""
        steps = self.scenario_data.get("steps", [])
        if self.current_step_index < len(steps) - 1:
            self.current_step_index += 1
            self.is_paused = False
            return self.get_current_step()
        return None

    def prev_step(self):
        """Quay lai step truoc do."""
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self.is_paused = False
            return self.get_current_step()
        return None

    def stop(self):
        """Tam dung tai step hien tai (khong auto-advance)."""
        self.is_paused = True
        return self.get_current_step()

    def resume(self):
        """Tiep tuc sau khi stop."""
        self.is_paused = False
        return self.get_current_step()

    def go_to_step(self, step_id: int):
        """Nhay thang den step co id cho truoc."""
        idx = self._step_index_map.get(step_id)
        if idx is None:
            raise ValueError(f"Khong tim thay step id={step_id}")
        self.current_step_index = idx
        self.is_paused = False
        return self.get_current_step()

    def reset(self):
        """Dat lai kich ban ve buoc dau tien."""
        self.current_step_index = 0
        self.is_paused = False
        for ac in self.scenario_data.get("aircraft_list", []):
            self.aircraft_states[ac["id"]]["pos"] = dict(
                ac.get("initial_pos", {"x": 0, "y": 0}))
            self.aircraft_states[ac["id"]]["angle"] = 0.0
        return self.get_current_step()

    # ------------------------------------------------------------------
    # Tien ich
    # ------------------------------------------------------------------
    def resolve_path(self, path_name: str) -> list:
        """Lay list toa do [{x,y}, ...] cua mot Path theo ten."""
        pts = self.paths.get(path_name)
        if pts is None:
            print(
                f"[WARNING] Path '{path_name}' khong ton tai trong paths.json.")
            return []
        return pts

    def update_aircraft_pos(self, ac_id: str, new_pos: dict):
        """Cap nhat toa do thuc te cua may bay (goi tu engine vat ly)."""
        if ac_id in self.aircraft_states:
            self.aircraft_states[ac_id]["pos"] = new_pos

    def update_aircraft_angle(self, ac_id: str, angle: float):
        """Cap nhat goc xoay cua may bay."""
        if ac_id in self.aircraft_states:
            self.aircraft_states[ac_id]["angle"] = angle

    def is_finished(self) -> bool:
        """Kiem tra kich ban da ket thuc chua."""
        steps = self.scenario_data.get("steps", [])
        return self.current_step_index >= len(steps)

    def get_scenario_info(self) -> dict:
        """Tra ve thong tin tong quat cua kich ban."""
        if not self.scenario_data:
            return {}
        total = len(self.scenario_data.get("steps", []))
        current = self.current_step_index + 1
        return {
            "id": self.scenario_data.get("scenario_id"),
            "name": self.scenario_data.get("scenario_name"),
            "total_steps": total,
            "current_step": current,
            "progress_pct": round(current / total * 100) if total > 0 else 0,
            "is_paused": self.is_paused,
        }
