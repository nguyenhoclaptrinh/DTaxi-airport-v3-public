class ScenarioValidator:
    """Validate cau truc scenario va lien ket toi paths.json."""

    SUPPORTED_STEP_TYPES = {"MESSAGE", "ACTION"}
    SUPPORTED_ACTIONS = {"MOVE_ALONG_PATH", "ROTATE"}

    def validate(self, scenario_data: dict, paths: dict | None = None) -> list[str]:
        paths = paths or {}
        issues: list[str] = []

        if not isinstance(scenario_data, dict):
            return ["Scenario root phai la object JSON."]

        aircraft_list = scenario_data.get("aircraft_list", [])
        steps = scenario_data.get("steps", [])

        if not isinstance(aircraft_list, list):
            issues.append("aircraft_list phai la array.")
            aircraft_list = []
        if not isinstance(steps, list):
            issues.append("steps phai la array.")
            steps = []

        aircraft_ids = self._validate_aircraft_list(aircraft_list, issues)
        self._validate_steps(steps, aircraft_ids, paths, issues)
        return issues

    def _validate_aircraft_list(self, aircraft_list: list, issues: list[str]) -> set[str]:
        aircraft_ids: set[str] = set()
        seen_ids: set[str] = set()

        for idx, aircraft in enumerate(aircraft_list):
            prefix = f"aircraft_list[{idx}]"
            if not isinstance(aircraft, dict):
                issues.append(f"{prefix} phai la object.")
                continue

            aircraft_id = aircraft.get("id")
            if not aircraft_id:
                issues.append(f"{prefix}.id la bat buoc.")
            elif aircraft_id in seen_ids:
                issues.append(f"{prefix}.id bi trung: {aircraft_id}.")
            else:
                seen_ids.add(aircraft_id)
                aircraft_ids.add(aircraft_id)

            if not aircraft.get("callsign"):
                issues.append(f"{prefix}.callsign la bat buoc.")

            self._validate_position(aircraft.get("initial_pos"), f"{prefix}.initial_pos", issues)

        return aircraft_ids

    def _validate_steps(
        self,
        steps: list,
        aircraft_ids: set[str],
        paths: dict,
        issues: list[str],
    ):
        seen_step_ids: set[int] = set()

        for idx, step in enumerate(steps):
            prefix = f"steps[{idx}]"
            if not isinstance(step, dict):
                issues.append(f"{prefix} phai la object.")
                continue

            step_id = step.get("id")
            if step_id is None:
                issues.append(f"{prefix}.id la bat buoc.")
            elif step_id in seen_step_ids:
                issues.append(f"{prefix}.id bi trung: {step_id}.")
            else:
                seen_step_ids.add(step_id)

            step_type = step.get("type")
            if step_type not in self.SUPPORTED_STEP_TYPES:
                issues.append(
                    f"{prefix}.type khong hop le: {step_type}. "
                    f"Ho tro: {', '.join(sorted(self.SUPPORTED_STEP_TYPES))}."
                )
                continue

            if step_type == "MESSAGE":
                self._validate_message_step(step, prefix, issues)
            elif step_type == "ACTION":
                self._validate_action_step(step, prefix, aircraft_ids, paths, issues)

    def _validate_message_step(self, step: dict, prefix: str, issues: list[str]):
        for field in ["sender", "target", "text"]:
            if not step.get(field):
                issues.append(f"{prefix}.{field} la bat buoc cho MESSAGE.")

    def _validate_action_step(
        self,
        step: dict,
        prefix: str,
        aircraft_ids: set[str],
        paths: dict,
        issues: list[str],
    ):
        action = step.get("action")
        aircraft_id = step.get("aircraft")

        if action not in self.SUPPORTED_ACTIONS:
            issues.append(
                f"{prefix}.action khong hop le: {action}. "
                f"Ho tro: {', '.join(sorted(self.SUPPORTED_ACTIONS))}."
            )
            return

        if aircraft_id not in aircraft_ids:
            issues.append(f"{prefix}.aircraft khong ton tai trong aircraft_list: {aircraft_id}.")

        if action == "MOVE_ALONG_PATH":
            path_name = step.get("path_name")
            if not path_name:
                issues.append(f"{prefix}.path_name la bat buoc cho MOVE_ALONG_PATH.")
                return
            if path_name not in paths:
                issues.append(f"{prefix}.path_name khong ton tai trong paths.json: {path_name}.")
                return
            path_points = paths.get(path_name, [])
            if not isinstance(path_points, list) or len(path_points) < 2:
                issues.append(f"{prefix}.path_name phai tham chieu path co it nhat 2 diem: {path_name}.")
            else:
                for point_idx, point in enumerate(path_points):
                    self._validate_position(
                        point,
                        f"paths.{path_name}[{point_idx}]",
                        issues,
                    )

        if action == "ROTATE" and not self._is_number(step.get("value")):
            issues.append(f"{prefix}.value phai la number cho ROTATE.")

    def _validate_position(self, pos, prefix: str, issues: list[str]):
        if not isinstance(pos, dict):
            issues.append(f"{prefix} phai la object {{x, y}}.")
            return
        if not self._is_number(pos.get("x")) or not self._is_number(pos.get("y")):
            issues.append(f"{prefix}.x va {prefix}.y phai la number.")

    def _is_number(self, value) -> bool:
        return isinstance(value, (int, float)) and not isinstance(value, bool)
