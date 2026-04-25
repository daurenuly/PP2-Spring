"""
main.py — Snake Game Extended (TSIS4)
Screens: Main Menu → Game → Game Over → Leaderboard → Settings
DB: PostgreSQL via psycopg2
"""

import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import *
from game import GameState, load_settings, save_settings, UP, DOWN, LEFT, RIGHT
import db

pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Snake — TSIS4")
clock = pygame.time.Clock()

F_BIG   = pygame.font.SysFont("impact", 48)
F_MED   = pygame.font.SysFont("impact", 30)
F_SMALL = pygame.font.SysFont("arial", 18, bold=True)
F_TINY  = pygame.font.SysFont("arial", 14)


# ── UI helpers ────────────────────────────────────────────────────

def draw_bg():
    screen.fill(DARK)
    for i in range(0, W, 40):
        pygame.draw.line(screen, (28, 28, 44), (i, 0), (i, H))
    for j in range(0, H, 40):
        pygame.draw.line(screen, (28, 28, 44), (0, j), (W, j))


def txt(text, font, color, cx, cy):
    s = font.render(text, True, color)
    screen.blit(s, s.get_rect(center=(cx, cy)))


def txt_left(text, font, color, x, y):
    s = font.render(text, True, color)
    screen.blit(s, (x, y))


class Button:
    def __init__(self, rect, label):
        self.rect  = pygame.Rect(rect)
        self.label = label

    def draw(self):
        mx, my = pygame.mouse.get_pos()
        hov = self.rect.collidepoint(mx, my)
        bg  = (60, 60, 90) if hov else (35, 35, 55)
        pygame.draw.rect(screen, bg, self.rect, border_radius=8)
        pygame.draw.rect(screen, ACCENT, self.rect, 2, border_radius=8)
        txt(self.label, F_SMALL, WHITE, self.rect.centerx, self.rect.centery)

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


# ── SCREEN: Main Menu ─────────────────────────────────────────────

def screen_menu() -> tuple:
    """Returns (next_state, username, player_id)"""
    settings   = load_settings()
    username   = ""
    error      = ""
    db_ok      = True

    try:
        db.init_db()
    except Exception as e:
        db_ok = False
        error = f"DB offline: {e}"

    btn_play = Button((W//2 - 90, 310, 180, 44), "PLAY")
    btn_lb   = Button((W//2 - 90, 365, 180, 44), "LEADERBOARD")
    btn_set  = Button((W//2 - 90, 420, 180, 44), "SETTINGS")
    btn_quit = Button((W//2 - 90, 475, 180, 44), "QUIT")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif event.key == pygame.K_RETURN:
                    if username.strip() and db_ok:
                        pid  = db.get_or_create_player(username.strip())
                        best = db.get_personal_best(pid)
                        return "game", username.strip(), pid, best
                    elif not username.strip():
                        error = "Enter username first!"
                else:
                    if len(username) < 18:
                        username += event.unicode

            if btn_play.clicked(event):
                if username.strip() and db_ok:
                    pid  = db.get_or_create_player(username.strip())
                    best = db.get_personal_best(pid)
                    return "game", username.strip(), pid, best
                elif not db_ok:
                    error = "Cannot connect to DB. Check config.py"
                else:
                    error = "Enter username first!"
            if btn_lb.clicked(event):  return "leaderboard", "", 0, 0
            if btn_set.clicked(event): return "settings", "", 0, 0
            if btn_quit.clicked(event):
                pygame.quit(); sys.exit()

        draw_bg()
        txt("SNAKE", F_BIG, ACCENT, W//2, 90)
        txt("Extended Edition — TSIS4", F_TINY, LGRAY, W//2, 145)

        txt("YOUR NAME:", F_SMALL, LGRAY, W//2, 210)
        box = pygame.Rect(W//2 - 120, 228, 240, 44)
        pygame.draw.rect(screen, PANEL, box, border_radius=8)
        pygame.draw.rect(screen, ACCENT, box, 2, border_radius=8)
        txt(username + "|", F_SMALL, WHITE, box.centerx, box.centery)

        if error:
            txt(error, F_TINY, RED, W//2, 283)

        for b in (btn_play, btn_lb, btn_set, btn_quit):
            b.draw()

        if not db_ok:
            txt("DB OFFLINE — scores won't save", F_TINY, RED, W//2, H - 20)

        pygame.display.flip()
        clock.tick(60)


# ── SCREEN: Game ──────────────────────────────────────────────────

def screen_game(username: str, player_id: int, personal_best: int) -> tuple:
    settings = load_settings()
    state    = GameState(settings, personal_best)
    move_acc = 0   # accumulate time between moves

    while True:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    state.snake.set_direction(UP)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    state.snake.set_direction(DOWN)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    state.snake.set_direction(LEFT)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    state.snake.set_direction(RIGHT)
                elif event.key == pygame.K_ESCAPE:
                    return "menu", state.score, state.level

        # Move snake at controlled speed
        ms_per_move = 1000 // state.current_fps()
        move_acc   += dt
        if move_acc >= ms_per_move:
            move_acc = 0
            result   = state.update()
            if result == "gameover":
                try:
                    db.save_session(player_id, state.score, state.level)
                except Exception:
                    pass
                return "gameover", state.score, state.level

        state.draw(screen, F_SMALL, F_TINY)
        pygame.display.flip()


# ── SCREEN: Game Over ─────────────────────────────────────────────

def screen_gameover(username: str, score: int, level: int, best: int) -> str:
    new_best = score > best
    btn_retry = Button((W//2 - 100, 390, 190, 44), "RETRY")
    btn_menu  = Button((W//2 - 100, 445, 190, 44), "MAIN MENU")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if btn_retry.clicked(event): return "game"
            if btn_menu.clicked(event):  return "menu"

        draw_bg()
        txt("GAME OVER", F_BIG, RED, W//2, 110)
        txt(username, F_MED, LGRAY, W//2, 168)

        stats = [
            (f"SCORE:  {score}",          YELLOW),
            (f"LEVEL:  {level}",          CYAN),
            (f"BEST:   {max(score,best)}", ACCENT),
        ]
        for i, (line, col) in enumerate(stats):
            txt(line, F_SMALL, col, W//2, 230 + i * 48)

        if new_best:
            txt("NEW PERSONAL BEST!", F_SMALL, ORANGE, W//2, 360)

        btn_retry.draw()
        btn_menu.draw()
        pygame.display.flip()
        clock.tick(60)


# ── SCREEN: Leaderboard ───────────────────────────────────────────

def screen_leaderboard() -> str:
    btn_back = Button((W//2 - 70, H - 60, 140, 40), "BACK")
    try:
        board = db.get_leaderboard()
        error = ""
    except Exception as e:
        board = []
        error = f"Cannot load: {e}"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "menu"
            if btn_back.clicked(event): return "menu"

        draw_bg()
        txt("LEADERBOARD", F_MED, YELLOW, W//2, 50)

        if error:
            txt(error, F_TINY, RED, W//2, 100)
        elif not board:
            txt("No scores yet — go play!", F_SMALL, GRAY, W//2, 200)
        else:
            header = f"{'#':<3}  {'NAME':<16}  {'SCORE':<8}  {'LVL':<5}  DATE"
            txt_left(header, F_TINY, ACCENT, 20, 90)
            pygame.draw.line(screen, ACCENT, (20, 110), (W - 20, 110), 1)
            for i, row in enumerate(board):
                y   = 120 + i * 36
                col = YELLOW if i == 0 else (LGRAY if i == 1 else WHITE)
                bg  = PANEL if i % 2 == 0 else (22, 22, 38)
                pygame.draw.rect(screen, bg, (18, y - 2, W - 36, 32), border_radius=4)
                line = (f"{i+1:<3}  {row['username']:<16}  "
                        f"{row['score']:<8}  {row['level_reached']:<5}  {row['date']}")
                txt_left(line, F_TINY, col, 22, y + 6)

        btn_back.draw()
        pygame.display.flip()
        clock.tick(60)


# ── SCREEN: Settings ─────────────────────────────────────────────

COLOR_OPTIONS = [
    ("Green",  [60,  200, 80]),
    ("Blue",   [50,  120, 220]),
    ("Red",    [220, 50,  50]),
    ("Yellow", [240, 200, 30]),
    ("Purple", [160, 60,  220]),
]


def screen_settings() -> str:
    settings  = load_settings()
    btn_save  = Button((W//2 - 80, H - 70, 160, 44), "SAVE & BACK")
    color_idx = next((i for i, (_, c) in enumerate(COLOR_OPTIONS)
                      if c == settings["snake_color"]), 0)

    btn_grid  = pygame.Rect(W//2 - 50, 195, 100, 36)
    btn_sound = pygame.Rect(W//2 - 50, 275, 100, 36)
    btn_col_l = pygame.Rect(W//2 - 110, 355, 36, 36)
    btn_col_r = pygame.Rect(W//2 + 74, 355,  36, 36)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if btn_save.clicked(event):
                settings["snake_color"] = COLOR_OPTIONS[color_idx][1]
                save_settings(settings)
                return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_grid.collidepoint(event.pos):
                    settings["grid"] = not settings["grid"]
                if btn_sound.collidepoint(event.pos):
                    settings["sound"] = not settings["sound"]
                if btn_col_l.collidepoint(event.pos):
                    color_idx = (color_idx - 1) % len(COLOR_OPTIONS)
                if btn_col_r.collidepoint(event.pos):
                    color_idx = (color_idx + 1) % len(COLOR_OPTIONS)

        draw_bg()
        txt("SETTINGS", F_MED, ACCENT, W//2, 70)

        def toggle_btn(rect, label, value, on_col, off_col):
            col = on_col if value else off_col
            pygame.draw.rect(screen, col, rect, border_radius=8)
            pygame.draw.rect(screen, WHITE, rect, 2, border_radius=8)
            txt("ON" if value else "OFF", F_SMALL, WHITE, rect.centerx, rect.centery)
            txt(label, F_TINY, LGRAY, W//2, rect.top - 18)

        toggle_btn(btn_grid,  "GRID OVERLAY", settings["grid"],  (40,160,40), GRAY)
        toggle_btn(btn_sound, "SOUND",        settings["sound"], (40,160,40), GRAY)

        # Color picker
        txt("SNAKE COLOR", F_TINY, LGRAY, W//2, 337)
        cname, cval = COLOR_OPTIONS[color_idx]
        preview = pygame.Rect(W//2 - 36, 355, 72, 36)
        pygame.draw.rect(screen, tuple(cval), preview, border_radius=8)
        pygame.draw.rect(screen, WHITE, preview, 2, border_radius=8)
        txt(cname, F_TINY, WHITE, preview.centerx, preview.centery)

        for brect, label in [(btn_col_l, "<"), (btn_col_r, ">")]:
            pygame.draw.rect(screen, PANEL, brect, border_radius=6)
            pygame.draw.rect(screen, ACCENT, brect, 2, border_radius=6)
            txt(label, F_SMALL, WHITE, brect.centerx, brect.centery)

        btn_save.draw()
        pygame.display.flip()
        clock.tick(60)


# ── State Machine ─────────────────────────────────────────────────

def main():
    state        = "menu"
    username     = "Player"
    player_id    = 0
    personal_best = 0
    last_score   = 0
    last_level   = 1

    while True:
        if state == "menu":
            result = screen_menu()
            state  = result[0]
            if state == "game":
                _, username, player_id, personal_best = result

        elif state == "game":
            state, last_score, last_level = screen_game(username, player_id, personal_best)
            if state == "gameover":
                personal_best = max(personal_best, last_score)

        elif state == "gameover":
            state = screen_gameover(username, last_score, last_level, personal_best)

        elif state == "leaderboard":
            state = screen_leaderboard()

        elif state == "settings":
            state = screen_settings()

        else:
            state = "menu"


if __name__ == "__main__":
    main()