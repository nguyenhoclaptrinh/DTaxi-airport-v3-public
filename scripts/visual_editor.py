"""
DTaxi - Visual Path Editor
==========================
Cong cu de ve lo trinh may bay truc tiep tren ban do san bay.

HUONG DAN:
  - Click trai: Them diem vao lo trinh hien tai.
  - Click phai: Xoa diem cuoi cung (Undo).
  - Nhan [S]: Luu lo trinh hien tai (se hoi ten Path).
  - Nhan [R]: Xoa lo trinh hien tai va bat dau lai.
  - Nhan [L]: Hien thi danh sach tat ca Path da luu.
  - Nhan [ESC]: Thoat.

OUTPUT: data/paths.json
"""
import pygame
import json
import os
import sys
import math

# --- Cau hinh ---
MAP_IMAGE = os.path.join("assets", "images", "tsn_airport_map.jpg")
PATHS_FILE = os.path.join("data", "paths.json")
SCREEN_W, SCREEN_H = 1200, 744

# Mau sac
COLOR_BG = (30, 30, 30)
COLOR_POINT = (255, 100, 0)
COLOR_POINT_SAVED = (0, 200, 100)
COLOR_LINE = (255, 220, 0)
COLOR_LINE_SAVED = (0, 200, 100)
COLOR_TEXT = (255, 255, 255)
COLOR_PATH = (0, 255, 0)
COLOR_INIT_MODE = (255, 255, 0) # Vang cho che do Initial
COLOR_AC = (0, 255, 255)
COLOR_UI_BG = (20, 20, 20, 210)

# Cac che do cho bien
MODE_PATH = "PATH"
MODE_INITIAL = "INITIAL"
MODE_SCENARIO = "SCENARIO"
SCENARIOS_DIR = os.path.join("data", "scenarios")

class InputBox:
    def __init__(self, x, y, w, h, text='', label='', color_active=(0, 255, 255), color_inactive=(150, 150, 150)):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_active = color_active
        self.color_inactive = color_inactive
        self.color = color_inactive
        self.text = str(text)
        self.label = label
        self.active = False
        self.font = pygame.font.SysFont("Consolas", 14)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = self.color_inactive
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

    def draw(self, screen):
        # Draw label
        lbl_surf = self.font.render(self.label, True, (200, 200, 200))
        screen.blit(lbl_surf, (self.rect.x, self.rect.y - 18))
        # Draw box
        pygame.draw.rect(screen, (10, 10, 10), self.rect)
        pygame.draw.rect(screen, self.color, self.rect, 2 if self.active else 1)
        # Draw text
        txt_surf = self.font.render(self.text, True, (255, 255, 255))
        screen.blit(txt_surf, (self.rect.x + 5, self.rect.y + 5))


def load_paths():
    """Tai paths.json neu ton tai."""
    if os.path.exists(PATHS_FILE):
        with open(PATHS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_paths(paths_data):
    """Luu paths_data vao paths.json."""
    os.makedirs(os.path.dirname(PATHS_FILE), exist_ok=True)
    with open(PATHS_FILE, "w", encoding="utf-8") as f:
        json.dump(paths_data, f, indent=2)


def load_scenario(name):
    """Tai kich ban tu thu muc data/scenarios."""
    if not name.endswith(".json"):
        name += ".json"
    path = os.path.join(SCENARIOS_DIR, name)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), name
    return None, name


def save_scenario(data, name):
    """Luu kich ban vao file."""
    if not name.endswith(".json"):
        name += ".json"
    os.makedirs(SCENARIOS_DIR, exist_ok=True)
    path = os.path.join(SCENARIOS_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Da luu kich ban vao: {path}")


def draw_ui(screen, font, small_font, current_points, saved_paths, show_list, bg_w, bg_h):
    """Ve giao dien overlay."""
    # --- Panel thong tin goc trai ---
    lines = [
        "DTaxi Visual Path Editor",
        f"Diem hien tai: {len(current_points)}",
        f"Paths da luu: {len(saved_paths)}",
        "",
        "[Click Trai]  Them diem",
        "[Click Phai] Xoa diem cuoi",
        "[S] Luu Path",
        "[R] Reset",
        "[L] Danh sach Path",
        "[I] Lay toa do (Mode Initial)",
        "[O] Mo Kich ban",
        "[N] Tao Kich ban moi",
        "[[ / ]] Chon may bay",
        "[A] Them may bay",
        "[Drag] Di chuyen AC",
        "[R] Reset kich ban",
        "[P] Gan Path cho AC",
        "[DELETE] Xoa may bay",
        "[H] An/Hien Scenario UI",
        "[SPACE] Them diem (khi ve)",
        "[ESC] Quay lai / Thoat",
    ]
    panel_w, panel_h = 240, len(lines) * 20 + 16
    panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel_surf.fill((20, 20, 20, 200))
    screen.blit(panel_surf, (5, 5))
    for i, line in enumerate(lines):
        col = (180, 220, 255) if line.startswith("[") else COLOR_TEXT
        if i == 0:
            col = (255, 200, 50)
        txt = small_font.render(line, True, col)
        screen.blit(txt, (12, 10 + i * 20))

    # --- Danh sach paths da luu (Ben phai) ---
    if show_list and saved_paths:
        names = list(saved_paths.keys())
        list_w = 260
        list_h = len(names) * 22 + 40
        list_surf = pygame.Surface((list_w, list_h), pygame.SRCALPHA)
        list_surf.fill((20, 20, 20, 220))
        # Dat o phia ben phai, duoi sidebar neu co
        screen.blit(list_surf, (SCREEN_W - list_w - 5, 10))
        header = small_font.render("--- DANH SACH PATH ---", True, (255, 200, 50))
        screen.blit(header, (SCREEN_W - list_w + 10, 20))
        for i, name in enumerate(names):
            pts = saved_paths[name]
            txt = small_font.render(f"{i+1}. {name} ({len(pts)} pts)", True, (0, 255, 150))
            screen.blit(txt, (SCREEN_W - list_w + 10, 50 + i * 22))


def draw_scenario_ui(screen, font, small_font, scenario_data, active_ac_idx, scenario_name, show_list, saved_paths):
    """Ve bang dieu khien kich ban."""
    if not scenario_data:
        return

    # Sidebar ben phai cho Timeline/Aircraft Property
    side_w = 280
    side_rect = pygame.Rect(SCREEN_W - side_w - 5, 5, side_w, SCREEN_H - 10)
    pygame.draw.rect(screen, (20, 20, 20, 140), side_rect) # Tang transparency (140)
    pygame.draw.rect(screen, (100, 100, 100, 200), side_rect, 1)

    y = 20
    header = font.render(f"SCENARIO: {scenario_name}", True, (255, 255, 0))
    screen.blit(header, (SCREEN_W - side_w, y))
    
    y += 40
    # Aircraft List
    ac_list = scenario_data.get("aircraft_list", [])
    ac_header = small_font.render(f"AIRCRAFT ({len(ac_list)}):", True, (200, 200, 200))
    screen.blit(ac_header, (SCREEN_W - side_w, y))
    
    y += 25
    for i, ac in enumerate(ac_list):
        col = (0, 255, 255) if i == active_ac_idx else (150, 150, 150)
        prefix = "> " if i == active_ac_idx else "  "
        txt = small_font.render(f"{prefix}{ac.get('id')} - {ac.get('callsign')}", True, col)
        screen.blit(txt, (SCREEN_W - side_w, y))
        y += 20

    # Steps Timeline (Simplified) - DICH XUONG DUOI
    y = SCREEN_H - 180
    steps = scenario_data.get("steps", [])
    step_header = small_font.render(f"TIMELINE ({len(steps)} steps):", True, (200, 200, 200))
    screen.blit(step_header, (SCREEN_W - side_w, y))
    
    y += 25
    max_visible_steps = 8
    for i, step in enumerate(steps[-max_visible_steps:]):
        stype = step.get("type", "")
        detail = ""
        if stype == "MESSAGE":
            detail = f"{step.get('sender')} -> {step.get('text')[:15]}..."
        elif stype == "ACTION":
            detail = f"{step.get('aircraft')} {step.get('action')} {step.get('path_name', '')}"
        
        txt = small_font.render(f"{i+1}. {stype}: {detail}", True, (120, 120, 120))
        screen.blit(txt, (SCREEN_W - side_w, y))
        y += 18



def draw_scene(screen, bg, bg_rect, current_points, saved_paths):
    """Ve nen ban do va cac path."""
    screen.fill(COLOR_BG)
    screen.blit(bg, bg_rect)

    # Ve cac path da luu
    for path_name, points in saved_paths.items():
        if len(points) > 1:
            pygame.draw.lines(screen, COLOR_LINE_SAVED, False, points, 2)
        for p in points:
            pygame.draw.circle(screen, COLOR_POINT_SAVED, p, 5)
            pygame.draw.circle(screen, (255, 255, 255), p, 5, 1)

    # Ve path hien tai
    if len(current_points) > 1:
        pygame.draw.lines(screen, COLOR_LINE, False, current_points, 2)
    for i, p in enumerate(current_points):
        col = (255, 50, 50) if i == 0 else COLOR_POINT
        pygame.draw.circle(screen, col, p, 6)
        pygame.draw.circle(screen, (255, 255, 255), p, 6, 1)

def draw_initial_marker(screen, font, pos, angle, bg_x, bg_y, bg_w, bg_h):
    """Ve ky hieu may bay tai vi tri va goc duoc chon."""
    if not pos:
        return
    
    # Ve hinh tam giac bieu dien may bay
    size = 20
    import math
    rad = math.radians(angle + 90) # Bu 90 vi 0 degree la North trong tam mat tool
    
    p1 = (pos[0] + size * math.cos(rad - 2.5), pos[1] + size * math.sin(rad - 2.5))
    p2 = (pos[0] + size * math.cos(rad + 2.5), pos[1] + size * math.sin(rad + 2.5))
    p3 = (pos[0] + size * 1.5 * math.cos(rad), pos[1] + size * 1.5 * math.sin(rad))
    
    pygame.draw.polygon(screen, (255, 200, 0), [p1, p2, p3])
    pygame.draw.circle(screen, (255, 255, 255), pos, 5)

    # Chuyen doi sang toa do normalized
    rel_x = (pos[0] - bg_x) / bg_w
    rel_y = (pos[1] - bg_y) / bg_h
    nx, ny = round(rel_x * SCREEN_W), round(rel_y * SCREEN_H)
    
    info = font.render(f"INIT: pos({nx}, {ny}) angle({int(angle)})", True, (255, 255, 0))
    screen.blit(info, (pos[0] + 20, pos[1] + 10))


def draw_scenario_entities(screen, font, scenario_data, active_idx, bg_x, bg_y, bg_w, bg_h, saved_paths):
    """Ve tat ca may bay va duong bay cua chung trong kich ban."""
    import math
    aircraft_list = scenario_data.get("aircraft_list", [])
    steps = scenario_data.get("steps", [])
    for i, ac in enumerate(aircraft_list):
        pos_data = ac.get("initial_pos", {"x": 0, "y": 0})
        angle = ac.get("initial_angle", 0)
        # Chuyen normalized sang screen
        sx = bg_x + (pos_data["x"] / SCREEN_W) * bg_w
        sy = bg_y + (pos_data["y"] / SCREEN_H) * bg_h
        ac_id = ac.get("id")
        is_active = (i == active_idx)
        color = (0, 255, 255) if is_active else (150, 150, 150)

        # Neu la may bay dang chon, ve cac Path ma no se di qua
        if is_active:
            for step in steps:
                if step.get("aircraft") == ac_id and step.get("type") == "ACTION" and step.get("action") == "MOVE_ALONG_PATH":
                    pname = step.get("path_name")
                    if pname in saved_paths:
                        # Lay list diem da duoc chuyen sang pixel screen
                        pts = saved_paths[pname]
                        if len(pts) >= 2:
                            pygame.draw.lines(screen, (200, 100, 255), False, pts, 3)
        
        # Ve ky hieu quay may bay (tam giac)
        size = 18 if is_active else 12
        rad = math.radians(angle + 90)
        p1 = (sx + size * math.cos(rad - 2.5), sy + size * math.sin(rad - 2.5))
        p2 = (sx + size * math.cos(rad + 2.5), sy + size * math.sin(rad + 2.5))
        p3 = (sx + size * 2.0 * math.cos(rad), sy + size * 2.0 * math.sin(rad))
        
        pygame.draw.polygon(screen, color, [p1, p2, p3])
        if is_active:
            # Hieu ung glow cho may bay dang chon
            pygame.draw.circle(screen, (255, 255, 255), (int(sx), int(sy)), 6, 1)
            
        label = font.render(f"{ac.get('id')}", True, color)
        screen.blit(label, (sx + 15, sy - 10))


def prompt_path_name(screen, font, small_font):
    """Hien thi hop nhap ten Path."""
    name = ""
    active = True
    clock = pygame.time.Clock()
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    active = False
                elif event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 40:
                        name += event.unicode

        # Ve hop nhap
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        box_w, box_h = 500, 120
        box_x = SCREEN_W // 2 - box_w // 2
        box_y = SCREEN_H // 2 - box_h // 2
        pygame.draw.rect(screen, (40, 40, 40),
                         (box_x, box_y, box_w, box_h), border_radius=8)
        pygame.draw.rect(screen, (100, 100, 200),
                         (box_x, box_y, box_w, box_h), 2, border_radius=8)

        title = font.render("Dat ten cho Path nay:", True, (255, 200, 50))
        screen.blit(title, (box_x + 20, box_y + 16))

        # Truong nhap
        input_rect = pygame.Rect(box_x + 20, box_y + 56, box_w - 40, 36)
        pygame.draw.rect(screen, (60, 60, 80), input_rect, border_radius=4)
        pygame.draw.rect(screen, (120, 120, 220),
                         input_rect, 1, border_radius=4)
        name_surf = font.render(name + "|", True, (255, 255, 255))
        screen.blit(name_surf, (input_rect.x + 8, input_rect.y + 6))

        hint = small_font.render(
            "[Enter] Xac nhan  [Esc] Huy", True, (150, 150, 150))
        screen.blit(hint, (box_x + 20, box_y + 98))

        pygame.display.flip()
        clock.tick(60)

    return name.strip() if name.strip() else None


def list_scenario_files():
    """Lay danh sach cac file kich ban JSON."""
    if not os.path.exists(SCENARIOS_DIR):
        return []
    return [f for f in os.listdir(SCENARIOS_DIR) if f.endswith(".json")]


def prompt_list_selection(screen, font, small_font, title_str, items):
    """Hien thi danh sach de nguoi dung chon."""
    selected_idx = 0
    active = True
    clock = pygame.time.Clock()
    if not items:
        return None

    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_idx = (selected_idx - 1) % len(items)
                elif event.key == pygame.K_DOWN:
                    selected_idx = (selected_idx + 1) % len(items)
                elif event.key == pygame.K_RETURN:
                    active = False
                elif event.key == pygame.K_ESCAPE:
                    return None

        screen.fill((20, 20, 20))
        title = font.render(title_str, True, (255, 200, 50))
        screen.blit(title, (50, 50))
        
        for i, item in enumerate(items):
            color = (0, 255, 255) if i == selected_idx else (150, 150, 150)
            prefix = " > " if i == selected_idx else "   "
            txt = small_font.render(f"{prefix}{item}", True, color)
            screen.blit(txt, (50, 100 + i * 25))

        pygame.display.flip()
        clock.tick(60)

    return items[selected_idx]


def run_editor():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("DTaxi - Visual Path Editor")

    font = pygame.font.SysFont("Arial", 16, bold=True)
    small_font = pygame.font.SysFont("Consolas", 14)

    # Load ban do
    if not os.path.exists(MAP_IMAGE):
        print(f"[ERROR] Khong tim thay ban do: {MAP_IMAGE}")
        pygame.quit()
        sys.exit(1)

    raw_bg = pygame.image.load(MAP_IMAGE).convert()
    # Scale anh vao screen, giu ti le
    img_w, img_h = raw_bg.get_size()
    scale = min(SCREEN_W / img_w, SCREEN_H / img_h)
    bg_w = int(img_w * scale)
    bg_h = int(img_h * scale)
    bg = pygame.transform.scale(raw_bg, (bg_w, bg_h))
    # Can giua
    bg_x = (SCREEN_W - bg_w) // 2
    bg_y = (SCREEN_H - bg_h) // 2
    bg_rect = pygame.Rect(bg_x, bg_y, bg_w, bg_h)

    saved_paths = load_paths()
    current_points = []
    show_list = False
    show_scenario_ui = True
    clock = pygame.time.Clock()
    running = True

    print("--- DTaxi Visual Path Editor ---")
    print(f"Ban do: {MAP_IMAGE} ({bg_w}x{bg_h} px tren man hinh)")
    print(f"Paths file: {PATHS_FILE}")
    print(f"Da tai {len(saved_paths)} path.")

    status_msg = ""
    status_timer = 0
    current_mode = MODE_PATH
    init_pos = None
    init_angle = 0
    is_dragging_angle = False

    # Studio Scenario State
    scenario_data = None
    scenario_name = ""
    active_ac_idx = -1
    input_boxes = []

    def refresh_inputs():
        nonlocal input_boxes
        input_boxes = []
        if active_ac_idx >= 0 and scenario_data:
            ac = scenario_data["aircraft_list"][active_ac_idx]
            # Dat cac o nhap lieu o phia duoi danh sach may bay nhung tren timeline
            start_y = 300
            input_boxes = [
                InputBox(SCREEN_W - 270, start_y, 250, 28, ac.get('id', ''), "AIRCRAFT ID"),
                InputBox(SCREEN_W - 270, start_y + 50, 250, 28, ac.get('callsign', ''), "CALLSIGN"),
                InputBox(SCREEN_W - 270, start_y + 100, 250, 28, ac.get('type', ''), "AIRCRAFT TYPE")
            ]

    while running:
        dt = clock.tick(60)
        if status_timer > 0:
            status_timer -= dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Handle InputBoxes in Scenario Mode
            if current_mode == MODE_SCENARIO:
                for box in input_boxes:
                    box.handle_event(event)
                # Sync back to scenario_data
                if active_ac_idx >= 0:
                    ac = scenario_data["aircraft_list"][active_ac_idx]
                    ac["id"] = input_boxes[0].text
                    ac["callsign"] = input_boxes[1].text
                    ac["type"] = input_boxes[2].text

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if event.button == 1:  # Left Click
                    if current_mode == MODE_PATH:
                        current_points.append((mx, my))
                    elif current_mode == MODE_INITIAL:
                        init_pos = (mx, my)
                        is_dragging_angle = True
                    elif current_mode == MODE_SCENARIO and scenario_data:
                        # Check if clicking on an aircraft to select it
                        clicked_ac = -1
                        for i, ac in enumerate(scenario_data.get("aircraft_list", [])):
                            px = bg_x + (ac["initial_pos"]["x"] / SCREEN_W) * bg_w
                            py = bg_y + (ac["initial_pos"]["y"] / SCREEN_H) * bg_h
                            if (mx - px)**2 + (my - py)**2 < 400: # 20px radius
                                clicked_ac = i
                                break
                        
                        if clicked_ac >= 0:
                            active_ac_idx = clicked_ac
                            refresh_inputs()
                            is_dragging_angle = True
                            init_pos = (mx, my)
                        else:
                            # If not clicking aircraft, maybe clicking elsewhere?
                            pass

                elif event.button == 3:  # Right Click
                    if current_mode == MODE_PATH and current_points:
                        current_points.pop()

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    is_dragging_angle = False

            elif event.type == pygame.MOUSEMOTION:
                if is_dragging_angle and current_mode == MODE_INITIAL:
                    mx, my = event.pos
                    init_angle = math.degrees(math.atan2(my - init_pos[1], mx - init_pos[0]))
                elif is_dragging_angle and current_mode == MODE_SCENARIO and active_ac_idx >= 0:
                    mx, my = event.pos
                    ac = scenario_data["aircraft_list"][active_ac_idx]
                    
                    if pygame.key.get_mods() & pygame.KMOD_CTRL:
                        # ROTATE mode (hold CTRL)
                        px = bg_x + (ac["initial_pos"]["x"] / SCREEN_W) * bg_w
                        py = bg_y + (ac["initial_pos"]["y"] / SCREEN_H) * bg_h
                        ac["initial_angle"] = int(math.degrees(math.atan2(my - py, mx - px)))
                    else:
                        # MOVE mode (default drag)
                        rel_x = (mx - bg_x) / bg_w
                        rel_y = (my - bg_y) / bg_h
                        ac["initial_pos"] = {"x": round(rel_x * SCREEN_W), "y": round(rel_y * SCREEN_H)}

            elif event.type == pygame.KEYDOWN:
                # Prioritize deactivating InputBox with ESC
                is_typing = any(box.active for box in input_boxes)
                if event.key == pygame.K_ESCAPE:
                    if is_typing:
                        for box in input_boxes:
                            box.active = False
                    elif current_mode != MODE_PATH:
                        current_mode = MODE_PATH
                        status_msg = "Chuyen ve che do VE PATH."
                        status_timer = 120
                    else:
                        running = False
                    continue

                # Handle Hotkeys (Only if not typing in InputBox)
                if not is_typing:
                    if event.key == pygame.K_o:
                        files = list_scenario_files()
                        fname = prompt_list_selection(screen, font, small_font, "MO KICH BAN:", files)
                        if fname:
                            data, name = load_scenario(fname)
                            if data:
                                scenario_data = data
                                scenario_name = name
                                current_mode = MODE_SCENARIO
                                active_ac_idx = 0 if scenario_data.get("aircraft_list") else -1
                                refresh_inputs()
                                status_msg = f"Da mo kich ban: {name}"
                                status_timer = 2000

                    elif event.key == pygame.K_n:
                        scenario_data = {"name": "New Scenario", "aircraft_list": [], "steps": []}
                        scenario_name = "new_scenario.json"
                        current_mode = MODE_SCENARIO
                        active_ac_idx = -1
                        status_msg = "Da tao kich ban moi (Chua luu)."
                        status_timer = 2000

                    elif event.key == pygame.K_i:
                        if current_mode == MODE_INITIAL:
                            current_mode = MODE_PATH
                            status_msg = "Quay lai che do VE PATH."
                        else:
                            current_mode = MODE_INITIAL
                            status_msg = "Che do LAY TOA DO tu do."
                        status_timer = 120

                    elif event.key == pygame.K_l:
                        show_list = not show_list
                        status_msg = f"{'Hien' if show_list else 'An'} danh sach Path."
                        status_timer = 1500

                    elif event.key == pygame.K_h:
                        show_scenario_ui = not show_scenario_ui
                        status_msg = f"{'Hien' if show_scenario_ui else 'An'} Sidebar kịch bản."
                        status_timer = 1500

                    elif event.key == pygame.K_LEFTBRACKET:
                        if scenario_data and scenario_data["aircraft_list"]:
                            active_ac_idx = (active_ac_idx - 1) % len(scenario_data["aircraft_list"])
                            refresh_inputs()

                    elif event.key == pygame.K_RIGHTBRACKET:
                        if scenario_data and scenario_data["aircraft_list"]:
                            active_ac_idx = (active_ac_idx + 1) % len(scenario_data["aircraft_list"])
                            refresh_inputs()

                    elif event.key == pygame.K_a and current_mode == MODE_SCENARIO:
                        new_ac = {"id": "NEW", "callsign": "NEW CALLSIGN", "type": "A321", "initial_pos": {"x": 400, "y": 300}, "initial_angle": 0}
                        scenario_data["aircraft_list"].append(new_ac)
                        active_ac_idx = len(scenario_data["aircraft_list"]) - 1
                        refresh_inputs()
                        status_msg = "Da them may bay moi."
                        status_timer = 2000

                    elif event.key == pygame.K_DELETE and current_mode == MODE_SCENARIO and active_ac_idx >= 0:
                        if scenario_data and scenario_data["aircraft_list"]:
                            ac_id = scenario_data["aircraft_list"][active_ac_idx].get("id")
                            scenario_data["aircraft_list"].pop(active_ac_idx)
                            active_ac_idx = -1
                            refresh_inputs()
                            status_msg = f"Da xoa may bay {ac_id}"
                            status_timer = 2000

                    elif event.key == pygame.K_p and current_mode == MODE_SCENARIO and active_ac_idx >= 0:
                        # Assign path to aircraft
                        path_files = list(saved_paths.keys())
                        chosen_path = prompt_list_selection(screen, font, small_font, "CHON PATH DE GAN:", path_files)
                        if chosen_path:
                            ac_id = scenario_data["aircraft_list"][active_ac_idx]["id"]
                            new_step = {
                                "id": len(scenario_data["steps"]) + 1,
                                "type": "ACTION",
                                "action": "MOVE_ALONG_PATH",
                                "aircraft": ac_id,
                                "path_name": chosen_path
                            }
                            scenario_data["steps"].append(new_step)
                            status_msg = f"Da gan path '{chosen_path}' cho {ac_id}"
                            status_timer = 2500

                    elif event.key == pygame.K_s:
                        if current_mode == MODE_PATH:
                            # Save Path logic (already exists)
                            if len(current_points) >= 2:
                                norm_pts = [{"x": round((p[0]-bg_x)/bg_w*SCREEN_W), "y": round((p[1]-bg_y)/bg_h*SCREEN_H)} for p in current_points]
                                pname = prompt_path_name(screen, font, small_font)
                                if pname:
                                    saved_paths[pname] = norm_pts
                                    save_paths(saved_paths)
                                    status_msg = f"Da luu Path '{pname}'"
                                    current_points = []
                        elif current_mode == MODE_SCENARIO and scenario_data:
                            save_scenario(scenario_data, scenario_name)
                            status_msg = f"Da luu kich ban: {scenario_name}"
                        status_timer = 2000

                    elif event.key == pygame.K_r:
                        current_points = []
                        init_pos = None
                        init_angle = 0
                        is_dragging_angle = False
                        status_msg = "Reset."
                        status_timer = 1500

        # --- DRAWING ---
        mapped_paths = {
            name: [(int(p["x"] / SCREEN_W * bg_w) + bg_x, int(p["y"] / SCREEN_H * bg_h) + bg_y)
                   for p in pts]
            for name, pts in saved_paths.items()
        }

        draw_scene(screen, bg, bg_rect, current_points, mapped_paths)

        if scenario_data:
            draw_scenario_entities(screen, font, scenario_data, active_ac_idx, bg_x, bg_y, bg_w, bg_h, mapped_paths)

        if current_mode == MODE_INITIAL:
            draw_initial_marker(screen, font, init_pos, init_angle, bg_x, bg_y, bg_w, bg_h)
        elif current_mode == MODE_SCENARIO and scenario_data:
            if show_scenario_ui:
                draw_scenario_ui(screen, font, small_font, scenario_data, active_ac_idx, scenario_name, show_list, saved_paths)
                for box in input_boxes:
                    box.draw(screen)

        draw_ui(screen, font, small_font, current_points,
                saved_paths, show_list, bg_w, bg_h)

        # Display Current Mode (Always visible)
        mode_label = font.render(f"CHE DO: {current_mode}", True, (255, 255, 0))
        pygame.draw.rect(screen, (0, 0, 0, 180), (5, SCREEN_H - 110, 200, 32))
        screen.blit(mode_label, (15, SCREEN_H - 105))

        # Status bar
        if status_timer > 0:
            bar = pygame.Surface((SCREEN_W, 28), pygame.SRCALPHA)
            bar.fill((30, 30, 60, 220))
            screen.blit(bar, (0, SCREEN_H - 28))
            st = font.render(status_msg, True, (100, 220, 255))
            screen.blit(st, (10, SCREEN_H - 24))

        # Toa do chuot realtime
        mx, my = pygame.mouse.get_pos()
        rel_x = (mx - bg_x) / bg_w if bg_w > 0 else 0
        rel_y = (my - bg_y) / bg_h if bg_h > 0 else 0
        norm_x = round(rel_x * SCREEN_W)
        norm_y = round(rel_y * SCREEN_H)
        coord_txt = small_font.render(
            f"Chuot: screen({mx},{my})  norm({norm_x},{norm_y})", True, (180, 180, 180))
        screen.blit(
            coord_txt, (SCREEN_W - coord_txt.get_width() - 8, SCREEN_H - 22))

        pygame.display.flip()

    pygame.quit()
    print(f"\nDa luu {len(saved_paths)} path vao {PATHS_FILE}")


if __name__ == "__main__":
    run_editor()
