from engine.scenario_manager import ScenarioManager
import os

def test_headless_engine():
    print("=== DTaxi Headless Engine Test ===")
    
    manager = ScenarioManager()
    scenario_path = os.path.join("data", "scenarios", "departure_sample.json")
    
    try:
        current_step = manager.load_scenario(scenario_path)
        print(f"Loaded Scenario: {manager.scenario_data['scenario_name']}")
        
        while current_step:
            print(f"\n--- [STEP {current_step['id']}: {current_step['label']}] ---")
            print(f"Active Aircraft: {current_step['active_aircraft']}")
            
            # Hiển thị tin nhắn AeroMACS
            for msg in current_step.get('messages', []):
                print(f"[{msg['sender']} -> {msg['target']}]: {msg['text']}")
            
            # Giả lập chuyển bước
            cmd = input("\nNhấn Enter để tiếp tục (hoặc 'b' để quay lại, 'q' để thoát): ").lower()
            if cmd == 'q':
                break
            elif cmd == 'b':
                current_step = manager.prev_step()
            else:
                current_step = manager.next_step()
                if not current_step:
                    print("\n=== Kết thúc kịch bản ===")
                    
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    test_headless_engine()
