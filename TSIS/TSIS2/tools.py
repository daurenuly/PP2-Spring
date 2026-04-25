"""
tools.py — Drawing tools for Paint application
Contains all shape-drawing and utility functions.
"""

import pygame
from collections import deque

# ── Shape Drawing Tools ──────────────────────────────────────────

def draw_rectangle(surface, color, start_pos, end_pos, thickness):
    """Draw a rectangle from start to end position."""
    x1, y1 = start_pos
    x2, y2 = end_pos
    rect = pygame.Rect(
        min(x1, x2), min(y1, y2),
        abs(x2 - x1), abs(y2 - y1)
    )
    pygame.draw.rect(surface, color, rect, thickness)


def draw_circle(surface, color, start_pos, end_pos, thickness):
    """Draw a circle — radius determined by distance to end_pos."""
    x1, y1 = start_pos
    x2, y2 = end_pos
    radius = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
    if radius > 0:
        pygame.draw.circle(surface, color, start_pos, radius, thickness)


def draw_line(surface, color, start_pos, end_pos, thickness):
    """Draw a straight line from start to end."""
    pygame.draw.line(surface, color, start_pos, end_pos, thickness)


def draw_square(surface, color, start_pos, end_pos, thickness):
    """Draw a square — side length is min of width/height."""
    x1, y1 = start_pos
    x2, y2 = end_pos
    side = min(abs(x2 - x1), abs(y2 - y1))
    x = min(x1, x2)
    y = min(y1, y2)
    rect = pygame.Rect(x, y, side, side)
    pygame.draw.rect(surface, color, rect, thickness)


def draw_right_triangle(surface, color, start_pos, end_pos, thickness):
    """Draw a right triangle (right angle at start position)."""
    x1, y1 = start_pos
    x2, y2 = end_pos
    points = [
        (x1, y1),      # right angle vertex
        (x2, y1),      # horizontal point
        (x1, y2),      # vertical point
    ]
    pygame.draw.polygon(surface, color, points, thickness)


def draw_equilateral_triangle(surface, color, start_pos, end_pos, thickness):
    """Draw an equilateral triangle."""
    x1, y1 = start_pos
    x2, y2 = end_pos
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    
    # Center and scale
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    size = max(width, height) / 2
    
    # Three vertices of equilateral triangle
    import math
    angle_offset = math.pi / 2
    points = [
        (
            cx + size * math.cos(angle_offset + i * 2 * math.pi / 3),
            cy + size * math.sin(angle_offset + i * 2 * math.pi / 3)
        )
        for i in range(3)
    ]
    points = [(int(p[0]), int(p[1])) for p in points]
    pygame.draw.polygon(surface, color, points, thickness)


def draw_rhombus(surface, color, start_pos, end_pos, thickness):
    """Draw a rhombus (diamond shape)."""
    x1, y1 = start_pos
    x2, y2 = end_pos
    
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    hw = abs(x2 - x1) / 2  # half-width
    hh = abs(y2 - y1) / 2  # half-height
    
    points = [
        (cx, cy - hh),      # top
        (cx + hw, cy),      # right
        (cx, cy + hh),      # bottom
        (cx - hw, cy),      # left
    ]
    points = [(int(p[0]), int(p[1])) for p in points]
    pygame.draw.polygon(surface, color, points, thickness)


# ── Pencil (Freehand) Drawing ────────────────────────────────────

def draw_pencil_stroke(surface, color, prev_pos, curr_pos, thickness):
    """Draw a line segment from prev_pos to curr_pos for freehand drawing."""
    if prev_pos and curr_pos:
        pygame.draw.line(surface, color, prev_pos, curr_pos, thickness)


# ── Eraser ───────────────────────────────────────────────────────

def erase(surface, pos, thickness, bg_color=(255, 255, 255)):
    """Erase pixels in a circular area."""
    radius = thickness // 2 + 1
    pygame.draw.circle(surface, bg_color, pos, radius)


# ── Flood Fill (Bucket) ──────────────────────────────────────────

def flood_fill(surface, pos, target_color):
    """
    Flood fill starting from pos with target_color.
    Stops at boundaries of different colors (exact match).
    Uses BFS to avoid stack overflow on large areas.
    """
    x, y = pos
    width, height = surface.get_size()
    
    # Check bounds
    if not (0 <= x < width and 0 <= y < height):
        return
    
    # Get the original color at the starting position
    original_color = surface.get_at(pos)
    
    # If colors are the same, no need to fill
    if original_color == target_color:
        return
    
    # BFS queue
    queue = deque([pos])
    visited = {pos}
    
    while queue:
        cx, cy = queue.popleft()
        
        # Fill the current pixel
        surface.set_at((cx, cy), target_color)
        
        # Check all 4 neighbors (up, down, left, right)
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = cx + dx, cy + dy
            
            # Check bounds and if already visited
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                neighbor_color = surface.get_at((nx, ny))
                
                # If neighbor has original color, add to queue
                if neighbor_color == original_color:
                    visited.add((nx, ny))
                    queue.append((nx, ny))


# ── Text Rendering ──────────────────────────────────────────────

def render_text(surface, text, pos, font, color):
    """Render text onto surface at given position."""
    if text:
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, pos)
