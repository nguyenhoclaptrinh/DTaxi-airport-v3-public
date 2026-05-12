import json
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from engine.scenario_validator import ScenarioValidator  # noqa: E402


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def main() -> int:
    paths_file = ROOT_DIR / "data" / "paths.json"
    scenarios_dir = ROOT_DIR / "data" / "scenarios"

    paths = load_json(paths_file) if paths_file.exists() else {}
    validator = ScenarioValidator()
    has_errors = False

    for scenario_file in sorted(scenarios_dir.glob("*.json")):
        scenario_data = load_json(scenario_file)
        issues = validator.validate(scenario_data, paths)
        if not issues:
            print(f"[OK] {scenario_file.name}")
            continue

        has_errors = True
        print(f"[ERROR] {scenario_file.name}: {len(issues)} issue(s)")
        for issue in issues:
            print(f"  - {issue}")

    return 1 if has_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
