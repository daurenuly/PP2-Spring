"""racer.py — Core game entities and mechanics for TSIS3 Racer."""

import pygame
import random
import math

# ── Colors ───────────────────────────────────────────────────────
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
RED    = (220, 50,  50)
BLUE   = (50,  120, 220)
GREEN  = (50,  200, 80)
YELLOW = (240, 200, 30)
ORANGE = (255, 140, 0)
GRAY   = (130, 130, 130)
LGRAY  = (190, 190, 190)
CYAN   = (0,   220, 180)
PURPLE = (160, 60,  220)
BROWN  = (120, 70,  20)

CAR_COLORS = {
    "red":    (220, 50,  50),
    "blue":   (50,  120, 220),
    "green":  (50,  200, 80),
    "yellow": (240, 200, 30),
}

# ── Road constants ────────────────────────────────────────────────
W, H    = 480, 640
ROAD_L  = 80
ROAD_R  = 400
LANE_W  = (ROAD_R - ROAD_L) // 3
LANES   = [ROAD_L + LANE_W * i + LANE_W // 2 for i in range(3)]  # lane centers


# ── Player Car ───────────────────────────────────────────────────

class PlayerCar:
    W, H = 36, 60

    def __init__(self, color_name="red"):
        self.color  = CAR_COLORS.get(color_name, RED)
        self.lane   = 1          # 0, 1, 2
        self.x      = float(LANES[self.lane])
        self.y      = float(H - 110)
        self.speed  = 5          # base road scroll speed
        self.shield = False
        self.nitro  = False
        self.alive  = True

    def move_left(self):
        if self.lane > 0:
            self.lane -= 1

    def move_right(self):
        if self.lane < 2:
            self.lane += 1

    def update(self):
        target_x = float(LANES[self.lane])
        self.x += (target_x - self.x) * 0.18   # smooth slide

    def get_rect(self):
        return pygame.Rect(self.x - self.W // 2, self.y - self.H // 2, self.W, self.H)

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        hw, hh = self.W // 2, self.H // 2

        # Body
        pygame.draw.rect(surface, self.color,
                         (cx - hw, cy - hh, self.W, self.H), border_radius=6)
        # Windshield
        pygame.draw.rect(surface, (180, 220, 255),
                         (cx - hw + 5, cy - hh + 8, self.W - 10, 16), border_radius=3)
        # Rear window
        pygame.draw.rect(surface, (180, 220, 255),
                         (cx - hw + 5, cy + hh - 22, self.W - 10, 12), border_radius=3)
        # Wheels
        for wx, wy in [(-hw - 4, -hh + 6), (hw, -hh + 6),
                        (-hw - 4, hh - 18), (hw, hh - 18)]:
            pygame.draw.rect(surface, BLACK, (cx + wx, cy + wy, 8, 14), border_radius=3)

        # Shield glow
        if self.shield:
            s = pygame.Surface((self.W + 20, self.H + 20), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (0, 180, 255, 80), s.get_rect())
            surface.blit(s, (cx - hw - 10, cy - hh - 10))

        # Nitro flame
        if self.nitro:
            for i in range(3):
                fx = cx - 8 + i * 8
                fy = cy + hh
                fh = random.randint(10, 24)
                pygame.draw.polygon(surface, ORANGE,
                                    [(fx, fy), (fx + 5, fy + fh), (fx + 10, fy)])


# ── Traffic Car ──────────────────────────────────────────────────

TRAFFIC_COLORS = [(180, 30, 30), (30, 80, 180), (30, 160, 60),
                  (180, 160, 30), (160, 60, 180), (80, 80, 80)]


class TrafficCar:
    W, H = 34, 58

    def __init__(self, speed):
        self.lane  = random.randint(0, 2)
        self.x     = float(LANES[self.lane])
        self.y     = float(-self.H)
        self.speed = speed
        self.color = random.choice(TRAFFIC_COLORS)

    def update(self, scroll_speed):
        self.y += scroll_speed + self.speed

    def get_rect(self):
        return pygame.Rect(self.x - self.W // 2, self.y - self.H // 2, self.W, self.H)

    def off_screen(self):
        return self.y > H + self.H

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        hw, hh = self.W // 2, self.H // 2
        pygame.draw.rect(surface, self.color,
                         (cx - hw, cy - hh, self.W, self.H), border_radius=5)
        pygame.draw.rect(surface, (180, 220, 255),
                         (cx - hw + 4, cy - hh + 6, self.W - 8, 14), border_radius=3)
        pygame.draw.rect(surface, (255, 220, 100),
                         (cx - hw + 4, cy + hh - 18, self.W - 8, 10), border_radius=3)
        for wx, wy in [(-hw - 3, -hh + 5), (hw - 1, -hh + 5),
                        (-hw - 3, hh - 17), (hw - 1, hh - 17)]:
            pygame.draw.rect(surface, BLACK, (cx + wx, cy + wy, 7, 13), border_radius=2)


# ── Coin ─────────────────────────────────────────────────────────

COIN_WEIGHTS = [(1, YELLOW, 10), (5, ORANGE, 30), (10, CYAN, 50)]


class Coin:
    R = 10

    def __init__(self, scroll_speed):
        weight, color, value = random.choices(
            COIN_WEIGHTS, weights=[6, 3, 1])[0]
        self.lane  = random.randint(0, 2)
        self.x     = float(LANES[self.lane])
        self.y     = float(-self.R)
        self.speed = scroll_speed
        self.color = color
        self.value = value
        self.angle = 0.0

    def update(self, scroll_speed):
        self.y     += scroll_speed
        self.angle += 0.05

    def off_screen(self):
        return self.y > H + self.R

    def get_rect(self):
        return pygame.Rect(self.x - self.R, self.y - self.R, self.R * 2, self.R * 2)

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        w = max(2, int(self.R * abs(math.cos(self.angle))))
        pygame.draw.ellipse(surface, self.color, (cx - w, cy - self.R, w * 2, self.R * 2))
        pygame.draw.ellipse(surface, WHITE,      (cx - w, cy - self.R, w * 2, self.R * 2), 1)


# ── Road Obstacles ───────────────────────────────────────────────

class Obstacle:
    """Oil spill, pothole, or speed bump."""

    TYPES = [
        ("oil",   (40, 40, 120), 50, 20),
        ("hole",  (20, 20, 20),  30, 30),
        ("bump",  (100, 60, 20), 60, 12),
    ]

    def __init__(self, scroll_speed):
        name, color, w, h = random.choice(self.TYPES)
        self.kind  = name
        self.lane  = random.randint(0, 2)
        self.x     = float(LANES[self.lane])
        self.y     = float(-h)
        self.speed = scroll_speed
        self.color = color
        self.w     = w
        self.h     = h

    def update(self, scroll_speed):
        self.y += scroll_speed

    def off_screen(self):
        return self.y > H + self.h

    def get_rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2, self.w, self.h)

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        if self.kind == "oil":
            pygame.draw.ellipse(surface, self.color,
                                (cx - self.w // 2, cy - self.h // 2, self.w, self.h))
            pygame.draw.ellipse(surface, (80, 80, 200),
                                (cx - self.w // 2, cy - self.h // 2, self.w, self.h), 2)
        elif self.kind == "hole":
            pygame.draw.ellipse(surface, self.color,
                                (cx - self.w // 2, cy - self.h // 2, self.w, self.h))
            pygame.draw.ellipse(surface, (50, 50, 50),
                                (cx - self.w // 2, cy - self.h // 2, self.w, self.h), 2)
        elif self.kind == "bump":
            pygame.draw.rect(surface, self.color,
                             (cx - self.w // 2, cy - self.h // 2, self.w, self.h),
                             border_radius=4)
            pygame.draw.rect(surface, (150, 90, 30),
                             (cx - self.w // 2, cy - self.h // 2, self.w, self.h),
                             2, border_radius=4)


# ── Power-Ups ────────────────────────────────────────────────────

POWERUP_TYPES = {
    "nitro":  (ORANGE, "NITRO",  "Boost speed!"),
    "shield": (CYAN,   "SHIELD", "Blocks 1 hit!"),
    "repair": (GREEN,  "REPAIR",  "Restore HP!"),
}


class PowerUp:
    R = 14
    LIFETIME = 8000   # ms before it disappears if not collected

    def __init__(self, scroll_speed, kind=None):
        self.kind   = kind or random.choice(list(POWERUP_TYPES.keys()))
        self.color, self.label, _ = POWERUP_TYPES[self.kind]
        self.lane   = random.randint(0, 2)
        self.x      = float(LANES[self.lane])
        self.y      = float(-self.R)
        self.speed  = scroll_speed
        self.born   = pygame.time.get_ticks()
        self.angle  = 0.0

    def update(self, scroll_speed):
        self.y     += scroll_speed
        self.angle += 0.04

    def off_screen(self):
        return self.y > H + self.R

    def expired(self):
        return pygame.time.get_ticks() - self.born > self.LIFETIME

    def get_rect(self):
        return pygame.Rect(self.x - self.R, self.y - self.R, self.R * 2, self.R * 2)

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        pulse = int(3 * math.sin(self.angle * 3))
        r = self.R + pulse
        pygame.draw.circle(surface, self.color, (cx, cy), r)
        pygame.draw.circle(surface, WHITE, (cx, cy), r, 2)
        font = pygame.font.SysFont("segoeuiemoji", 14)
        sym = {"nitro": "N", "shield": "S", "repair": "R"}[self.kind]
        t = font.render(sym, True, BLACK)
        surface.blit(t, t.get_rect(center=(cx, cy)))


# ── Moving Barrier (road event) ──────────────────────────────────

class Barrier:
    """A moving barrier that sweeps across lanes."""

    def __init__(self, scroll_speed):
        self.x     = float(ROAD_L)
        self.y     = float(-20)
        self.w     = ROAD_R - ROAD_L
        self.h     = 18
        self.speed = scroll_speed
        self.gap_lane = random.randint(0, 2)   # one safe lane gap
        self.gap_w    = LANE_W - 8

    def update(self, scroll_speed):
        self.y += scroll_speed

    def off_screen(self):
        return self.y > H + self.h

    def get_rects(self):
        """Return solid parts (excluding the gap lane)."""
        rects = []
        for lane in range(3):
            lx = ROAD_L + lane * LANE_W
            if lane == self.gap_lane:
                continue
            rects.append(pygame.Rect(lx, int(self.y), LANE_W, self.h))
        return rects

    def draw(self, surface):
        for lane in range(3):
            lx = ROAD_L + lane * LANE_W
            if lane == self.gap_lane:
                # Draw gap marker
                pygame.draw.rect(surface, GREEN,
                                 (lx + 4, int(self.y), LANE_W - 8, self.h),
                                 border_radius=3)
            else:
                pygame.draw.rect(surface, (180, 30, 30),
                                 (lx, int(self.y), LANE_W, self.h),
                                 border_radius=3)
                pygame.draw.rect(surface, (255, 60, 60),
                                 (lx, int(self.y), LANE_W, self.h), 2,
                                 border_radius=3)


# ── Nitro Strip ──────────────────────────────────────────────────

class NitroStrip:
    """A yellow strip in one lane that gives a short speed boost."""

    def __init__(self, scroll_speed):
        self.lane  = random.randint(0, 2)
        self.x     = ROAD_L + self.lane * LANE_W
        self.y     = float(-24)
        self.w     = LANE_W
        self.h     = 24
        self.speed = scroll_speed

    def update(self, scroll_speed):
        self.y += scroll_speed

    def off_screen(self):
        return self.y > H + self.h

    def get_rect(self):
        return pygame.Rect(self.x, int(self.y), self.w, self.h)

    def draw(self, surface):
        pygame.draw.rect(surface, ORANGE,
                         (self.x + 2, int(self.y), self.w - 4, self.h),
                         border_radius=4)
        font = pygame.font.SysFont("arial", 10, bold=True)
        t = font.render("NITRO", True, BLACK)
        surface.blit(t, t.get_rect(center=(self.x + self.w // 2, int(self.y) + self.h // 2)))


# ── Score Calculator ──────────────────────────────────────────────

def calc_score(coins: int, distance: int, powerup_bonus: int) -> int:
    return coins * 10 + distance // 5 + powerup_bonus
