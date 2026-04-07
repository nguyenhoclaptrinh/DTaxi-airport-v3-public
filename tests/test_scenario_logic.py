import sys
import os
import json

# Add src to path
sys.path.append(os.path.abspath("src"))

from engine.scenario_manager import ScenarioManager
from entities.aircraft_entity import AircraftEntity

def test_scenario_manager():
    sm = ScenarioManager()
    
    # Mock data
    metadata = {
        "waypoints": {
            "STAND_A1": {"x": 100, "y": 200},
            "RUNWAY": {"x": 500, "y": 600}
        }
    }
    with open("data/test_metadata.json", "w") as f:
        json.dump(metadata, f)
        
    scenario = {
        "aircraft_list": [
            {"id": "AC001", "callsign": "HVN123", "type": "A321", "initial_pos": "STAND_A1"}
        ],
        "steps": [
            {
                "id": 1,
                "label": "Step 1",
                "active_aircraft": "AC001",
                "path": ["STAND_A1", "RUNWAY"],
                "speed": 10
            }
        ]
    }
    with open("data/test_scenario.json", "w") as f:
        json.dump(scenario, f)
        
    print("Testing load_scenario...")
    sm.load_scenario("data/test_scenario.json", "data/test_metadata.json")
    
    ac_state = sm.aircraft_states["AC001"]
    print(f"Initial Aircraft State: {ac_state}")
    assert ac_state["pos"]["x"] == 100
    assert ac_state["pos"]["y"] == 200
    
    current_step = sm.get_current_step()
    print(f"Current Step Path: {current_step['path']}")
    assert current_step["path"][0]["x"] == 100
    assert current_step["path"][1]["x"] == 500
    
    print("Testing reset...")
    # Change pos manually to simulate movement
    sm.aircraft_states["AC001"]["pos"] = {"x": 300, "y": 400}
    sm.reset()
    assert sm.aircraft_states["AC001"]["pos"]["x"] == 100
    assert sm.aircraft_states["AC001"]["pos"]["y"] == 200
    print("Reset successful!")

def test_aircraft_entity():
    print("Testing AircraftEntity...")
    entity = AircraftEntity("AC001", "HVN123", 100, 200)
    assert entity.x == 100.0
    assert entity.y == 200.0
    
    entity.set_path([{"x": 200, "y": 200}], 100)
    entity.update(0.5) # Should move 50 pixels
    print(f"Entity pos after 0.5s: {entity.x}, {entity.y}")
    assert entity.x == 150.0
    assert entity.y == 200.0
    
    entity.update(1.0) # Should arrive at destination
    assert entity.x == 200.0
    assert entity.is_moving == False
    print("AircraftEntity movement successful!")

if __name__ == "__main__":
    if not os.path.exists("data"):
        os.makedirs("data")
    try:
        test_scenario_manager()
        test_aircraft_entity()
        print("\nAll tests passed successfully!")
    finally:
        # Cleanup
        if os.path.exists("data/test_metadata.json"): os.remove("data/test_metadata.json")
        if os.path.exists("data/test_scenario.json"): os.remove("data/test_scenario.json")
