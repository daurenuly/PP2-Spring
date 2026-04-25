"""ui.py — Reusable UI helpers (buttons, text, screens) for Racer."""

import pygame

# ── Palette ───────────────────────────────────────────────────────
BLACK   = (0,   0,   0)
WHITE   = (255, 255, 255)
GRAY    = (60,  60,  60)
LGRAY   = (180, 180, 180)
RED     = (220, 50,  50)
GREEN   = (50,  200, 80)
BLUE    = (50,  120, 220)
YELLOW  = (240, 200, 30)
ORANGE  = (255, 140, 0)
DARK    = (18,  18,  28)
PANEL   = (30,  30,  48)
ACCENT  = (0,   220, 180)


class Button:
    """Simple rectangular button with hover highlight."""

    def __init__(self, rect, text, color=GRAY, text_color=WHITE, font=None):
        self.rect       = pygame.Rect(rect)
        self.text       = text
        self.color      = color
        self.text_color = text_color
        self._font      = font

    def draw(self, surface, font=None):
        f = self._font or font
        mx, my = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mx, my)
        color = tuple(min(c + 40, 255) for c in self.color) if hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, ACCENT, self.rect, 2, border_radius=8)
        if f:
            label = f.render(self.text, True, self.text_color)
            lr = label.get_rect(center=self.rect.center)
            surface.blit(label, lr)

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


def draw_text(surface, text, font, color, cx, cy, anchor="center"):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if anchor == "center":
        rect.center = (cx, cy)
    elif anchor == "topleft":
        rect.topleft = (cx, cy)
    elif anchor == "midleft":
        rect.midleft = (cx, cy)
    surface.blit(surf, rect)


def draw_road(surface, road_offset, W, H, ROAD_L, ROAD_R, LANE_W):
    """Draw the scrolling road background."""
    surface.fill((40, 40, 40))
    # Grass sides
    pygame.draw.rect(surface, (30, 100, 30), (0, 0, ROAD_L, H))
    pygame.draw.rect(surface, (30, 100, 30), (ROAD_R, 0, W - ROAD_R, H))
    # Road
    pygame.draw.rect(surface, (70, 70, 70), (ROAD_L, 0, ROAD_R - ROAD_L, H))
    # Lane markings (dashed)
    for lane in range(1, 3):
        lx = ROAD_L + lane * LANE_W
        for y in range(-(road_offset % 60), H, 60):
            pygame.draw.rect(surface, (200, 200, 60), (lx - 2, y, 4, 35))
    # Road edges
    pygame.draw.rect(surface, WHITE, (ROAD_L, 0, 4, H))
    pygame.draw.rect(surface, WHITE, (ROAD_R - 4, 0, 4, H))
