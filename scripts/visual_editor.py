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

# --- Cau hinh ---
MAP_IMAGE = os.path.join("assets", "images", "tsn_airport_map.jpg")
PATHS_FILE = os.path.join("data", "paths.json")
SCREEN_W, SCREEN_H = 1200, 750

# Mau sac
COLOR_BG = (30, 30, 30)
COLOR_POINT = (255, 100, 0)
COLOR_POINT_SAVED = (0, 200, 100)
COLOR_LINE = (255, 220, 0)
COLOR_LINE_SAVED = (0, 200, 100)
COLOR_TEXT = (255, 255, 255)
COLOR_UI_BG = (20, 20, 20, 210)


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
        "[L] Hien/an danh sach Path",
        "[ESC] Thoat",
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

    # --- Danh sach paths da luu ---
    if show_list and saved_paths:
        names = list(saved_paths.keys())
        list_w = 320
        list_h = len(names) * 22 + 24
        list_surf = pygame.Surface((list_w, list_h), pygame.SRCALPHA)
        list_surf.fill((20, 20, 20, 210))
        screen.blit(list_surf, (SCREEN_W - list_w - 5, 5))
        header = small_font.render("Paths da luu:", True, (255, 200, 50))
        screen.blit(header, (SCREEN_W - list_w, 10))
        for i, name in enumerate(names):
            pts = saved_paths[name]
            txt = small_font.render(
                f"  {name}  ({len(pts)} diem)", True, (0, 220, 120))
            screen.blit(txt, (SCREEN_W - list_w, 32 + i * 22))


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
    clock = pygame.time.Clock()
    running = True

    print("--- DTaxi Visual Path Editor ---")
    print(f"Ban do: {MAP_IMAGE} ({bg_w}x{bg_h} px tren man hinh)")
    print(f"Paths file: {PATHS_FILE}")
    print(f"Da tai {len(saved_paths)} path.")

    status_msg = ""
    status_timer = 0

    while running:
        dt = clock.tick(60)
        if status_timer > 0:
            status_timer -= dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if event.button == 1:  # Click trai: them diem
                    # Doi toa do man hinh sang toa do anh (normalized ve 800x600 de dung voi metadata cu)
                    # Luu toa do pixel goc theo ti le 800x600 de tuong thich voi engine
                    rel_x = (mx - bg_x) / bg_w  # 0.0 -> 1.0
                    rel_y = (my - bg_y) / bg_h
                    # Norm sang khong gian 800x600
                    norm_x = round(rel_x * 800)
                    norm_y = round(rel_y * 600)
                    current_points.append((mx, my))
                    print(
                        f"  Diem {len(current_points)}: screen=({mx},{my})  norm=({norm_x},{norm_y})")

                elif event.button == 3:  # Click phai: xoa diem cuoi
                    if current_points:
                        current_points.pop()
                        status_msg = "Da xoa diem cuoi."
                        status_timer = 2000

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_r:
                    current_points = []
                    status_msg = "Da reset lo trinh."
                    status_timer = 2000

                elif event.key == pygame.K_l:
                    show_list = not show_list

                elif event.key == pygame.K_s:
                    if len(current_points) < 2:
                        status_msg = "Can it nhat 2 diem de luu!"
                        status_timer = 2500
                    else:
                        # Chuyen sang toa do normalized 800x600 de luu
                        norm_pts = []
                        for (px, py) in current_points:
                            rel_x = (px - bg_x) / bg_w
                            rel_y = (py - bg_y) / bg_h
                            norm_pts.append({
                                "x": round(rel_x * 800),
                                "y": round(rel_y * 600)
                            })

                        path_name = prompt_path_name(screen, font, small_font)
                        if path_name:
                            saved_paths[path_name] = norm_pts
                            save_paths(saved_paths)
                            status_msg = f"Da luu Path '{path_name}' ({len(norm_pts)} diem)."
                            status_timer = 3000
                            current_points = []
                            print(f"[SAVED] {path_name}: {norm_pts}")
                        else:
                            status_msg = "Huy luu."
                            status_timer = 1500

        # --- Ve scene ---
        draw_scene(screen, bg, bg_rect, current_points, {
            name: [(int(p["x"] / 800 * bg_w) + bg_x, int(p["y"] / 600 * bg_h) + bg_y)
                   for p in pts]
            for name, pts in saved_paths.items()
        })

        draw_ui(screen, font, small_font, current_points,
                saved_paths, show_list, bg_w, bg_h)

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
        norm_x = round(rel_x * 800)
        norm_y = round(rel_y * 600)
        coord_txt = small_font.render(
            f"Chuot: screen({mx},{my})  norm({norm_x},{norm_y})", True, (180, 180, 180))
        screen.blit(
            coord_txt, (SCREEN_W - coord_txt.get_width() - 8, SCREEN_H - 22))

        pygame.display.flip()

    pygame.quit()
    print(f"\nDa luu {len(saved_paths)} path vao {PATHS_FILE}")


if __name__ == "__main__":
    run_editor()
