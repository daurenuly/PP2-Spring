"""
main.py — Racer Game Extended (TSIS3)

Screens: Main Menu → Username Entry → Game → Game Over → Leaderboard
Settings: sound toggle, car color, difficulty
"""

import pygame
import sys
import os
import random

# Убедимся что Python видит все файлы проекта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from racer import (
    PlayerCar, TrafficCar, Coin, Obstacle, PowerUp, Barrier, NitroStrip,
    calc_score, W, H, ROAD_L, ROAD_R, LANE_W, LANES,
    WHITE, BLACK, RED, GREEN, BLUE, YELLOW, ORANGE, CYAN, GRAY, LGRAY, PURPLE
)
from ui import Button, draw_text, draw_road
from persistence import load_settings, save_settings, load_leaderboard, save_score

# ── Init ─────────────────────────────────────────────────────────

pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Racer — TSIS3")
clock = pygame.time.Clock()
FPS = 60

# Fonts
F_BIG   = pygame.font.SysFont("impact", 52)
F_MED   = pygame.font.SysFont("impact", 32)
F_SMALL = pygame.font.SysFont("arial", 20, bold=True)
F_TINY  = pygame.font.SysFont("arial", 15)

# Settings
settings = load_settings()

# Difficulty presets: (base_speed, traffic_mult, obstacle_mult)
DIFF = {
    "easy":   (4, 0.6, 0.6),
    "normal": (5, 1.0, 1.0),
    "hard":   (7, 1.5, 1.5),
}

DARK  = (18, 18, 28)
PANEL = (30, 30, 48)
ACCENT= (0, 220, 180)


# ── Helpers ──────────────────────────────────────────────────────

def draw_bg(surface, offset=0):
    surface.fill(DARK)
    # Subtle star field
    random.seed(42)
    for _ in range(60):
        x = random.randint(0, W)
        y = (random.randint(0, H) + offset) % H
        pygame.draw.circle(surface, (80, 80, 100), (x, y), 1)
    random.seed()


def make_btn(rect, text):
    return Button(rect, text, color=(40, 40, 65), text_color=WHITE, font=F_SMALL)


# ── SCREEN: Main Menu ─────────────────────────────────────────────

def screen_menu():
    btn_play  = make_btn((W//2 - 100, 230, 200, 48), "PLAY")
    btn_lb    = make_btn((W//2 - 100, 295, 200, 48), "LEADERBOARD")
    btn_set   = make_btn((W//2 - 100, 360, 200, 48), "SETTINGS")
    btn_quit  = make_btn((W//2 - 100, 425, 200, 48), "QUIT")
    offset = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if btn_play.is_clicked(event):  return "username"
            if btn_lb.is_clicked(event):    return "leaderboard"
            if btn_set.is_clicked(event):   return "settings"
            if btn_quit.is_clicked(event):
                pygame.quit(); sys.exit()

        offset = (offset + 1) % H
        draw_bg(screen, offset)

        # Title
        t1 = F_BIG.render("RACER", True, ACCENT)
        screen.blit(t1, t1.get_rect(center=(W//2, 120)))
        t2 = F_SMALL.render("Extended Edition — TSIS3", True, LGRAY)
        screen.blit(t2, t2.get_rect(center=(W//2, 175)))

        for btn in (btn_play, btn_lb, btn_set, btn_quit):
            btn.draw(screen, F_SMALL)

        pygame.display.flip()
        clock.tick(FPS)


# ── SCREEN: Username Entry ────────────────────────────────────────

def screen_username():
    name = ""
    btn_ok = make_btn((W//2 - 80, 360, 160, 44), "START")
    error = ""

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu", ""
                elif event.key == pygame.K_RETURN:
                    if name.strip():
                        return "game", name.strip()
                    error = "Enter a name first!"
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 16:
                        name += event.unicode
            if btn_ok.is_clicked(event):
                if name.strip():
                    return "game", name.strip()
                error = "Enter a name first!"

        draw_bg(screen)
        draw_text(screen, "ENTER YOUR NAME", F_MED, ACCENT, W//2, 160)
        draw_text(screen, "Type your racer name below:", F_TINY, LGRAY, W//2, 210)

        # Input box
        box = pygame.Rect(W//2 - 130, 260, 260, 48)
        pygame.draw.rect(screen, PANEL, box, border_radius=8)
        pygame.draw.rect(screen, ACCENT, box, 2, border_radius=8)
        draw_text(screen, name + "|", F_SMALL, WHITE, box.centerx, box.centery)

        if error:
            draw_text(screen, error, F_TINY, RED, W//2, 325)

        btn_ok.draw(screen, F_SMALL)
        draw_text(screen, "Press Enter or click START", F_TINY, GRAY, W//2, 420)

        pygame.display.flip()
        clock.tick(FPS)


# ── SCREEN: Settings ─────────────────────────────────────────────

def screen_settings():
    global settings
    btn_back  = make_btn((W//2 - 80, 530, 160, 40), "BACK")
    colors    = ["red", "blue", "green", "yellow"]
    diffs     = ["easy", "normal", "hard"]

    # Button rects for click detection
    btn_sound = pygame.Rect(W//2 - 70, 195, 140, 40)
    btn_color = pygame.Rect(W//2 - 70, 305, 140, 40)
    btn_diff  = pygame.Rect(W//2 - 70, 415, 140, 40)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                save_settings(settings); return "menu"
            if btn_back.is_clicked(event):
                save_settings(settings); return "menu"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if btn_sound.collidepoint(mx, my):
                    settings["sound"] = not settings["sound"]
                if btn_color.collidepoint(mx, my):
                    idx = colors.index(settings["car_color"])
                    settings["car_color"] = colors[(idx + 1) % len(colors)]
                if btn_diff.collidepoint(mx, my):
                    idx = diffs.index(settings["difficulty"])
                    settings["difficulty"] = diffs[(idx + 1) % len(diffs)]

        draw_bg(screen)
        draw_text(screen, "SETTINGS", F_MED, ACCENT, W//2, 80)

        rows = [
            ("SOUND",      "ON" if settings["sound"] else "OFF", btn_sound),
            ("CAR COLOR",  settings["car_color"].upper(),        btn_color),
            ("DIFFICULTY", settings["difficulty"].upper(),       btn_diff),
        ]

        for label, value, btn_r in rows:
            # Label above button
            draw_text(screen, label, F_SMALL, LGRAY, W//2, btn_r.top - 22)
            # Button
            mx, my = pygame.mouse.get_pos()
            hovered = btn_r.collidepoint(mx, my)
            bg = (60, 60, 90) if hovered else PANEL
            pygame.draw.rect(screen, bg, btn_r, border_radius=8)
            pygame.draw.rect(screen, ACCENT, btn_r, 2, border_radius=8)
            draw_text(screen, value, F_SMALL, WHITE, btn_r.centerx, btn_r.centery)
            draw_text(screen, "click to change", F_TINY, GRAY, W//2, btn_r.bottom + 10)

        btn_back.draw(screen, F_SMALL)
        pygame.display.flip()
        clock.tick(FPS)


# ── SCREEN: Leaderboard ───────────────────────────────────────────

def screen_leaderboard():
    btn_back = make_btn((W//2 - 80, 570, 160, 40), "BACK")
    board    = load_leaderboard()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "menu"
            if btn_back.is_clicked(event):
                return "menu"

        draw_bg(screen)
        draw_text(screen, "LEADERBOARD", F_MED, YELLOW, W//2, 60)

        headers = ["#", "NAME", "SCORE", "DIST", "COINS"]
        xs      = [30, 70, 220, 320, 400]
        draw_text(screen, "  #    NAME            SCORE   DIST  COINS",
                  F_TINY, ACCENT, 30, 105, anchor="topleft")
        pygame.draw.line(screen, ACCENT, (20, 125), (W - 20, 125), 1)

        if not board:
            draw_text(screen, "No scores yet — go race!", F_SMALL, GRAY, W//2, 300)
        for i, entry in enumerate(board[:10]):
            y = 140 + i * 38
            bg = PANEL if i % 2 == 0 else (22, 22, 38)
            pygame.draw.rect(screen, bg, (20, y - 2, W - 40, 36), border_radius=4)
            color = YELLOW if i == 0 else (LGRAY if i == 1 else WHITE)
            line = (f"  {i+1:<3}  {entry['name']:<14}  "
                    f"{entry['score']:<8}  {entry['distance']:<6}  {entry['coins']}")
            draw_text(screen, line, F_TINY, color, 22, y + 8, anchor="topleft")

        btn_back.draw(screen, F_SMALL)
        pygame.display.flip()
        clock.tick(FPS)


# ── SCREEN: Game Over ─────────────────────────────────────────────

def screen_gameover(name, score, distance, coins, powerup_bonus):
    save_score(name, score, distance, coins)
    btn_retry = make_btn((W//2 - 110, 420, 200, 48), "RETRY")
    btn_menu  = make_btn((W//2 - 110, 480, 200, 48), "MAIN MENU")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if btn_retry.is_clicked(event): return "game"
            if btn_menu.is_clicked(event):  return "menu"

        draw_bg(screen)
        draw_text(screen, "GAME OVER", F_BIG, RED, W//2, 130)
        draw_text(screen, f"Racer: {name}", F_SMALL, LGRAY, W//2, 210)

        stats = [
            ("SCORE",    str(score),    YELLOW),
            ("DISTANCE", f"{distance}m", CYAN),
            ("COINS",    str(coins),     ORANGE),
            ("BONUSES",  f"+{powerup_bonus}", GREEN),
        ]
        for i, (label, val, col) in enumerate(stats):
            y = 260 + i * 38
            draw_text(screen, label + ":", F_SMALL, GRAY, W//2 - 80, y, anchor="midleft")
            draw_text(screen, val, F_SMALL, col, W//2 + 80, y, anchor="midleft")

        btn_retry.draw(screen, F_SMALL)
        btn_menu.draw(screen, F_SMALL)
        pygame.display.flip()
        clock.tick(FPS)


# ── GAME LOOP ─────────────────────────────────────────────────────

def run_game(player_name: str):
    diff_name  = settings.get("difficulty", "normal")
    base_speed, traffic_mult, obs_mult = DIFF[diff_name]
    car_color  = settings.get("car_color", "red")

    # State
    player       = PlayerCar(car_color)
    scroll_speed = float(base_speed)
    road_offset  = 0
    distance     = 0
    coins_count  = 0
    powerup_bonus = 0
    hp           = 3       # crash lives

    traffic      : list[TrafficCar] = []
    coins_list   : list[Coin]       = []
    obstacles    : list[Obstacle]   = []
    powerups     : list[PowerUp]    = []
    barriers     : list[Barrier]    = []
    nitro_strips : list[NitroStrip] = []

    # Timers (ms)
    t_traffic   = 0
    t_coin      = 0
    t_obstacle  = 0
    t_powerup   = 0
    t_barrier   = 0
    t_nitrostr  = 0
    TRAFFIC_INT  = int(2200 / traffic_mult)
    OBS_INT      = int(2800 / obs_mult)
    POWERUP_INT  = 8000
    BARRIER_INT  = 12000
    NITROSTR_INT = 10000

    # Active power-up state
    active_pu   = None   # "nitro" | "shield" | "repair"
    pu_end_ms   = 0
    NITRO_DUR   = 4000   # ms

    # Input cooldown for lane switching
    last_move   = 0
    MOVE_CD     = 160    # ms

    paused = False

    def spawn_safe(SpawnCls, *args):
        obj = SpawnCls(*args)
        # Retry if too close to player
        for _ in range(5):
            if obj.lane == player.lane and abs(obj.y - player.y) < 120:
                obj.lane = random.randint(0, 2)
                obj.x = float(LANES[obj.lane])
            else:
                break
        return obj

    while True:
        now = pygame.time.get_ticks()
        dt  = clock.tick(FPS)

        # ── Events ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused
                if not paused:
                    if event.key in (pygame.K_LEFT, pygame.K_a) and now - last_move > MOVE_CD:
                        player.move_left(); last_move = now
                    if event.key in (pygame.K_RIGHT, pygame.K_d) and now - last_move > MOVE_CD:
                        player.move_right(); last_move = now

        if paused:
            draw_text(screen, "PAUSED — ESC to resume", F_MED, ACCENT, W//2, H//2)
            pygame.display.flip()
            continue

        # ── Difficulty scaling ──
        scroll_speed = base_speed + distance / 800
        player.speed = scroll_speed
        player.nitro = (active_pu == "nitro")

        # ── Spawning ──
        if now - t_traffic > TRAFFIC_INT:
            traffic.append(spawn_safe(TrafficCar, scroll_speed * 0.5))
            t_traffic = now

        if now - t_coin > 900:
            coins_list.append(spawn_safe(Coin, scroll_speed))
            t_coin = now

        if now - t_obstacle > OBS_INT:
            obstacles.append(spawn_safe(Obstacle, scroll_speed))
            t_obstacle = now

        if now - t_powerup > POWERUP_INT:
            powerups.append(PowerUp(scroll_speed))
            t_powerup = now

        if now - t_barrier > BARRIER_INT:
            barriers.append(Barrier(scroll_speed))
            t_barrier = now

        if now - t_nitrostr > NITROSTR_INT:
            nitro_strips.append(NitroStrip(scroll_speed))
            t_nitrostr = now

        # ── Update ──
        player.update()
        road_offset  = (road_offset + int(scroll_speed)) % 60
        distance    += 1

        effective_speed = scroll_speed * (1.5 if active_pu == "nitro" else 1.0)

        for obj in traffic:      obj.update(effective_speed)
        for obj in coins_list:   obj.update(effective_speed)
        for obj in obstacles:    obj.update(effective_speed)
        for obj in powerups:     obj.update(effective_speed)
        for obj in barriers:     obj.update(effective_speed)
        for obj in nitro_strips: obj.update(effective_speed)

        # Expire active power-up
        if active_pu and now > pu_end_ms:
            if active_pu == "nitro":
                player.nitro = False
            active_pu = None

        # Clean up off-screen
        traffic      = [x for x in traffic      if not x.off_screen()]
        coins_list   = [x for x in coins_list   if not x.off_screen()]
        obstacles    = [x for x in obstacles    if not x.off_screen()]
        powerups     = [x for x in powerups     if not x.off_screen() and not x.expired()]
        barriers     = [x for x in barriers     if not x.off_screen()]
        nitro_strips = [x for x in nitro_strips if not x.off_screen()]

        pr = player.get_rect()

        # ── Collisions: Traffic ──
        for car in traffic[:]:
            if pr.colliderect(car.get_rect()):
                if active_pu == "shield":
                    active_pu = None
                    player.shield = False
                    traffic.remove(car)
                else:
                    hp -= 1
                    traffic.remove(car)
                    if hp <= 0:
                        score = calc_score(coins_count, distance, powerup_bonus)
                        return screen_gameover(player_name, score, distance, coins_count, powerup_bonus)

        # ── Collisions: Obstacles ──
        for obs in obstacles[:]:
            if pr.colliderect(obs.get_rect()):
                if active_pu == "shield":
                    active_pu = None
                    player.shield = False
                    obstacles.remove(obs)
                elif obs.kind == "bump":
                    scroll_speed = max(2, scroll_speed - 1)
                    obstacles.remove(obs)
                else:
                    hp -= 1
                    obstacles.remove(obs)
                    if hp <= 0:
                        score = calc_score(coins_count, distance, powerup_bonus)
                        return screen_gameover(player_name, score, distance, coins_count, powerup_bonus)

        # ── Collisions: Barriers ──
        for barrier in barriers:
            for r in barrier.get_rects():
                if pr.colliderect(r):
                    if active_pu == "shield":
                        active_pu = None
                        player.shield = False
                    else:
                        hp -= 1
                        if hp <= 0:
                            score = calc_score(coins_count, distance, powerup_bonus)
                            return screen_gameover(player_name, score, distance, coins_count, powerup_bonus)

        # ── Collisions: Coins ──
        for coin in coins_list[:]:
            if pr.colliderect(coin.get_rect()):
                coins_count += coin.value
                coins_list.remove(coin)

        # ── Collisions: Power-Ups ──
        for pu in powerups[:]:
            if pr.colliderect(pu.get_rect()):
                if pu.kind == "nitro":
                    active_pu = "nitro"
                    pu_end_ms = now + NITRO_DUR
                    player.nitro = True
                elif pu.kind == "shield":
                    active_pu = "shield"
                    pu_end_ms = now + 999999
                    player.shield = True
                elif pu.kind == "repair":
                    hp = min(hp + 1, 3)
                    powerup_bonus += 50
                powerups.remove(pu)
                powerup_bonus += 20

        # ── Collisions: Nitro Strips ──
        for ns in nitro_strips[:]:
            if pr.colliderect(ns.get_rect()) and player.lane == ns.lane:
                if active_pu != "nitro":
                    active_pu = "nitro"
                    pu_end_ms = now + 2000
                    player.nitro = True
                nitro_strips.remove(ns)

        # ── Draw ──
        draw_road(screen, road_offset, W, H, ROAD_L, ROAD_R, LANE_W)

        for obj in nitro_strips: obj.draw(screen)
        for obj in barriers:     obj.draw(screen)
        for obj in obstacles:    obj.draw(screen)
        for obj in coins_list:   obj.draw(screen)
        for obj in powerups:     obj.draw(screen)
        for obj in traffic:      obj.draw(screen)
        player.draw(screen)

        # ── HUD ──
        # Top bar
        pygame.draw.rect(screen, (0, 0, 0, 160), (0, 0, W, 44))

        draw_text(screen, f"COINS: {coins_count}", F_SMALL, YELLOW, 10, 12, anchor="topleft")
        draw_text(screen, f"DIST: {distance}m",   F_SMALL, CYAN,   W//2, 12, anchor="topleft")
        draw_text(screen, f"HP: {'■' * hp + '□' * (3 - hp)}", F_SMALL, RED, W - 10, 22, anchor="midleft")

        # Active power-up
        if active_pu:
            remaining = max(0, (pu_end_ms - now) // 1000)
            from racer import POWERUP_TYPES
            col = POWERUP_TYPES[active_pu][0]
            label = POWERUP_TYPES[active_pu][1]
            time_str = f"{remaining}s" if active_pu == "nitro" else "ACTIVE"
            draw_text(screen, f"{label} {time_str}", F_TINY, col, W//2, 50)

        # Score preview
        score = calc_score(coins_count, distance, powerup_bonus)
        draw_text(screen, f"SCORE {score}", F_TINY, WHITE, W - 10, 44, anchor="midleft")

        # Speed indicator
        bar_w = int((scroll_speed / 20) * 80)
        pygame.draw.rect(screen, GRAY,   (10, H - 18, 80, 8), border_radius=3)
        pygame.draw.rect(screen, ORANGE, (10, H - 18, bar_w, 8), border_radius=3)
        draw_text(screen, "SPD", F_TINY, GRAY, 95, H - 14, anchor="midleft")

        pygame.display.flip()


# ── Main State Machine ────────────────────────────────────────────

def main():
    global settings
    state       = "menu"
    player_name = "Player"

    while True:
        if state == "menu":
            state = screen_menu()

        elif state == "username":
            result, name = screen_username()
            if result == "game":
                player_name = name
                state = "game"
            else:
                state = "menu"

        elif state == "settings":
            state = screen_settings()
            settings = load_settings()

        elif state == "leaderboard":
            state = screen_leaderboard()

        elif state == "game":
            state = run_game(player_name)
            # run_game returns result of screen_gameover ("game" or "menu")

        else:
            state = "menu"


if __name__ == "__main__":
    main()
