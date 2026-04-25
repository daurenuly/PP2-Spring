"""game.py — Snake game core: snake, food, power-ups, obstacles."""

import pygame
import random
import json
import os
from config import *


# ── Settings helpers ──────────────────────────────────────────────

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "snake_color": [60, 200, 80],
    "grid":        True,
    "sound":       False,
}


def load_settings() -> dict:
    if os.path.isfile(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                return {**DEFAULT_SETTINGS, **json.load(f)}
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(s: dict) -> None:
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=2)


# ── Direction constants ───────────────────────────────────────────
UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)
OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}


# ── Food ─────────────────────────────────────────────────────────

class Food:
    LIFETIME = 7000   # ms before disappearing

    def __init__(self, pos, weight=1):
        self.pos    = pos
        self.weight = weight
        self.color  = FOOD_COLORS.get(weight, RED)
        self.born   = pygame.time.get_ticks()

    def expired(self) -> bool:
        return pygame.time.get_ticks() - self.born > self.LIFETIME

    def time_left_frac(self) -> float:
        elapsed = pygame.time.get_ticks() - self.born
        return max(0.0, 1.0 - elapsed / self.LIFETIME)

    def draw(self, surface):
        x, y = self.pos
        cx = x * CELL + CELL // 2
        cy = y * CELL + CELL // 2 + PANEL_H
        r  = CELL // 2 - 2

        # Pulse shrinks as food ages
        pr = max(4, int(r * self.time_left_frac()))
        pygame.draw.circle(surface, self.color, (cx, cy), pr)
        pygame.draw.circle(surface, WHITE, (cx, cy), pr, 1)


class PoisonFood:
    def __init__(self, pos):
        self.pos   = pos
        self.color = POISON
        self.born  = pygame.time.get_ticks()

    def expired(self) -> bool:
        return pygame.time.get_ticks() - self.born > 6000

    def draw(self, surface):
        x, y = self.pos
        cx = x * CELL + CELL // 2
        cy = y * CELL + CELL // 2 + PANEL_H
        r  = CELL // 2 - 2
        pygame.draw.circle(surface, self.color, (cx, cy), r)
        # X mark
        d = r - 3
        pygame.draw.line(surface, WHITE, (cx - d, cy - d), (cx + d, cy + d), 2)
        pygame.draw.line(surface, WHITE, (cx + d, cy - d), (cx - d, cy + d), 2)


# ── Power-Up ─────────────────────────────────────────────────────

class PowerUp:
    FIELD_LIFETIME = 8000    # disappears from field after 8s

    DURATIONS = {"speed": 5000, "slow": 5000, "shield": None}
    LABELS    = {"speed": "SPD+", "slow": "SLO", "shield": "SHD"}

    def __init__(self, pos, kind):
        self.pos   = pos
        self.kind  = kind
        self.color = PU_COLORS[kind]
        self.born  = pygame.time.get_ticks()

    def expired_on_field(self) -> bool:
        return pygame.time.get_ticks() - self.born > self.FIELD_LIFETIME

    def draw(self, surface):
        x, y = self.pos
        rx = x * CELL + 2
        ry = y * CELL + 2 + PANEL_H
        rw = rh = CELL - 4
        # Pulsing border
        pulse = int(2 * abs((pygame.time.get_ticks() % 800) / 400 - 1))
        pygame.draw.rect(surface, self.color, (rx, ry, rw, rh), border_radius=5)
        pygame.draw.rect(surface, WHITE, (rx - pulse, ry - pulse,
                                          rw + pulse * 2, rh + pulse * 2), 2,
                         border_radius=5)
        font = pygame.font.SysFont("arial", 9, bold=True)
        t = font.render(self.LABELS[self.kind], True, BLACK)
        surface.blit(t, t.get_rect(center=(rx + rw // 2, ry + rh // 2)))


# ── Obstacle block ────────────────────────────────────────────────

class Obstacle:
    def __init__(self, pos):
        self.pos = pos

    def draw(self, surface):
        x, y = self.pos
        rx = x * CELL
        ry = y * CELL + PANEL_H
        pygame.draw.rect(surface, LGRAY, (rx + 1, ry + 1, CELL - 2, CELL - 2), border_radius=3)
        pygame.draw.rect(surface, GRAY,  (rx + 1, ry + 1, CELL - 2, CELL - 2), 2, border_radius=3)


# ── Snake ─────────────────────────────────────────────────────────

class Snake:
    def __init__(self, color):
        self.color  = tuple(color)
        cx, cy      = COLS // 2, ROWS // 2
        self.body   = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.dir    = RIGHT
        self.grew   = False

    def set_direction(self, new_dir):
        if new_dir != OPPOSITE.get(self.dir):
            self.dir = new_dir

    def head(self):
        return self.body[0]

    def move(self):
        hx, hy = self.head()
        dx, dy = self.dir
        new_head = (hx + dx, hy + dy)   # no % wrapping — wall = death
        self.body.insert(0, new_head)
        if not self.grew:
            self.body.pop()
        self.grew = False

    def grow(self, n=1):
        for _ in range(n):
            self.body.append(self.body[-1])

    def shorten(self, n=2):
        for _ in range(n):
            if len(self.body) > 1:
                self.body.pop()

    def collides_self(self):
        return self.head() in self.body[1:]

    def collides_wall(self):
        hx, hy = self.head()
        return not (0 <= hx < COLS and 0 <= hy < ROWS)

    def draw(self, surface):
        for i, (x, y) in enumerate(self.body):
            rx = x * CELL + 1
            ry = y * CELL + 1 + PANEL_H
            rw = rh = CELL - 2
            shade = max(40, 255 - i * 8)
            color = tuple(min(255, int(c * shade / 255)) for c in self.color)
            pygame.draw.rect(surface, color, (rx, ry, rw, rh), border_radius=4)
            if i == 0:
                # Eyes
                ex1 = rx + 5
                ex2 = rx + rw - 8
                ey  = ry + 5
                pygame.draw.circle(surface, WHITE, (ex1, ey), 3)
                pygame.draw.circle(surface, WHITE, (ex2, ey), 3)
                pygame.draw.circle(surface, BLACK, (ex1, ey), 1)
                pygame.draw.circle(surface, BLACK, (ex2, ey), 1)


# ── Obstacle generator ────────────────────────────────────────────

def generate_obstacles(level: int, snake_body: list, occupied: set) -> list:
    """Place wall blocks starting at level 3, avoiding the snake area."""
    if level < 3:
        return []
    count   = min(4 + (level - 3) * 2, 20)
    blocks  = []
    banned  = set(snake_body) | occupied
    # Ban 3-cell radius around snake head
    hx, hy = snake_body[0]
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            banned.add(((hx + dx) % COLS, (hy + dy) % ROWS))

    attempts = 0
    while len(blocks) < count and attempts < 500:
        pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
        if pos not in banned:
            blocks.append(Obstacle(pos))
            banned.add(pos)
        attempts += 1
    return blocks


# ── Game state ────────────────────────────────────────────────────

class GameState:
    FOOD_WEIGHTS = [1, 1, 1, 3, 3, 5]

    def __init__(self, settings: dict, personal_best: int = 0):
        self.settings      = settings
        self.personal_best = personal_best
        self.snake         = Snake(settings["snake_color"])
        self.score         = 0
        self.level         = 1
        self.food_eaten    = 0
        self.move_timer    = 0
        self.fps           = FPS_DEFAULT

        self.foods    : list[Food]    = []
        self.poison   : PoisonFood | None = None
        self.powerup  : PowerUp | None    = None
        self.obstacles: list[Obstacle]    = []

        # Active effect
        self.active_effect    = None   # "speed" | "slow" | "shield"
        self.effect_end_ms    = 0
        self.shield_triggered = False

        self._spawn_food()

    def _occupied(self) -> set:
        s = set(self.snake.body)
        s.update(f.pos for f in self.foods)
        if self.poison:      s.add(self.poison.pos)
        if self.powerup:     s.add(self.powerup.pos)
        s.update(o.pos for o in self.obstacles)
        return s

    def _free_pos(self) -> tuple:
        occ = self._occupied()
        for _ in range(200):
            pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
            if pos not in occ:
                return pos
        return None

    def _spawn_food(self):
        if len(self.foods) < 2:
            pos = self._free_pos()
            if pos:
                w = random.choice(self.FOOD_WEIGHTS)
                self.foods.append(Food(pos, w))

    def _maybe_spawn_poison(self):
        if self.poison is None and random.random() < 0.008:
            pos = self._free_pos()
            if pos:
                self.poison = PoisonFood(pos)

    def _maybe_spawn_powerup(self):
        if self.powerup is None and random.random() < 0.004:
            pos = self._free_pos()
            if pos:
                kind = random.choice(["speed", "slow", "shield"])
                self.powerup = PowerUp(pos, kind)

    def current_fps(self) -> int:
        if self.active_effect == "speed":
            return self.fps + 4
        if self.active_effect == "slow":
            return max(2, self.fps - 3)
        return self.fps

    def update(self) -> str:
        """Advance one move. Returns 'ok' or 'gameover'."""
        now = pygame.time.get_ticks()

        # Expire active effect
        if self.active_effect and self.active_effect != "shield" and now > self.effect_end_ms:
            self.active_effect = None

        self.snake.move()
        head = self.snake.head()

        # Wall / self collision
        if self.snake.collides_wall() or self.snake.collides_self():
            if self.active_effect == "shield" and not self.shield_triggered:
                self.shield_triggered = True
                # Warp to safe spot if wall
                hx, hy = head
                hx = max(0, min(COLS - 1, hx))
                hy = max(0, min(ROWS - 1, hy))
                self.snake.body[0] = (hx, hy)
            else:
                return "gameover"

        # Obstacle collision
        obs_positions = {o.pos for o in self.obstacles}
        if head in obs_positions:
            if self.active_effect == "shield" and not self.shield_triggered:
                self.shield_triggered = True
            else:
                return "gameover"

        # Eat normal food
        for food in self.foods[:]:
            if head == food.pos:
                self.score      += food.weight * 10
                self.food_eaten += 1
                self.snake.grew  = True
                self.foods.remove(food)
                # Level up every 5 food items
                if self.food_eaten % 5 == 0:
                    self.level += 1
                    self.fps = min(FPS_DEFAULT + self.level - 1, 20)
                    occ = self._occupied()
                    self.obstacles = generate_obstacles(self.level, self.snake.body, occ)

        # Eat poison
        if self.poison and head == self.poison.pos:
            self.snake.shorten(2)
            self.poison = None
            if len(self.snake.body) <= 1:
                return "gameover"

        # Collect power-up
        if self.powerup and head == self.powerup.pos:
            kind = self.powerup.kind
            self.powerup = None
            self.active_effect = kind
            if kind == "shield":
                self.shield_triggered = False
                self.effect_end_ms = now + 999_999
            else:
                self.effect_end_ms = now + 5000

        # Clean up expired items
        self.foods = [f for f in self.foods if not f.expired()]
        if self.poison and self.poison.expired():
            self.poison = None
        if self.powerup and self.powerup.expired_on_field():
            self.powerup = None

        self._spawn_food()
        self._maybe_spawn_poison()
        self._maybe_spawn_powerup()

        return "ok"

    def draw(self, surface, font_small, font_tiny):
        # Background
        surface.fill(DARK)

        # Grid overlay
        if self.settings.get("grid"):
            for x in range(COLS):
                for y in range(ROWS):
                    pygame.draw.rect(surface, (28, 28, 44),
                                     (x * CELL, y * CELL + PANEL_H, CELL, CELL), 1)

        # Obstacles, food, snake
        for obs in self.obstacles: obs.draw(surface)
        for food in self.foods:    food.draw(surface)
        if self.poison:   self.poison.draw(surface)
        if self.powerup:  self.powerup.draw(surface)
        self.snake.draw(surface)

        # Visible border walls
        field_rect = pygame.Rect(0, PANEL_H, W, H - PANEL_H)
        pygame.draw.rect(surface, ACCENT, field_rect, 3)

        # HUD panel
        pygame.draw.rect(surface, PANEL, (0, 0, W, PANEL_H))
        pygame.draw.line(surface, ACCENT, (0, PANEL_H), (W, PANEL_H), 1)

        draw_hud(surface, font_small, font_tiny,
                 self.score, self.level, self.personal_best,
                 self.active_effect, self.effect_end_ms)


def draw_hud(surface, fs, ft, score, level, best, effect, effect_end):
    now = pygame.time.get_ticks()

    def txt(text, color, x, y, f=None):
        f = f or fs
        s = f.render(text, True, color)
        surface.blit(s, s.get_rect(midleft=(x, y)))

    txt(f"SCORE  {score}", YELLOW, 10, 20)
    txt(f"LVL {level}", ACCENT, W // 2 - 40, 20)
    txt(f"BEST {best}", LGRAY, W - 140, 20, ft)

    if effect:
        remaining = max(0, (effect_end - now) // 1000)
        labels = {"speed": ("SPD+", ORANGE), "slow": ("SLOW", CYAN), "shield": ("SHIELD", PURPLE)}
        label, col = labels[effect]
        time_str = f"{label} {remaining}s" if effect != "shield" else f"{label} ACTIVE"
        txt(time_str, col, W // 2 + 40, 20, ft)