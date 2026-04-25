
import pygame
import sys
import os
from datetime import datetime
from tools import (
    draw_rectangle, draw_circle, draw_line, draw_square,
    draw_right_triangle, draw_equilateral_triangle, draw_rhombus,
    draw_pencil_stroke, erase, flood_fill, render_text
)

pygame.init()

WIDTH, HEIGHT = 1200, 700
TOOLBAR_W = 190
CANVAS_W = WIDTH - TOOLBAR_W
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint Application Extended (TSIS2)")
clock = pygame.time.Clock()

# Canvas & buffers
canvas = pygame.Surface((CANVAS_W, HEIGHT))
canvas.fill(WHITE)
preview_cache = None
needs_redraw = True

# Undo history (храним копии холста)
undo_stack = []
MAX_UNDO = 20  # максимум 20 шагов отмены

# Папка для сохранения
SAVE_DIR = os.path.expanduser("~/Pictures/Paint")
os.makedirs(SAVE_DIR, exist_ok=True)

# Tool state
current_tool = "pencil"
current_color = BLACK
brush_size = 5
is_drawing = False
start_pos = None
prev_pos = None
text_mode = False
text_input = ""
text_pos = None

BRUSH_SIZES = {1: 2, 2: 5, 3: 10}
SIZE_LABELS = {2: "S", 5: "M", 10: "L"}

font = pygame.font.SysFont("arial", 20)
small_font = pygame.font.SysFont("arial", 14)

TOOLBAR_X = CANVAS_W

# Toolbar buttons
toolbar_buttons = {
    "pencil":     ("Pencil", (TOOLBAR_X, 10)),
    "line":       ("Line", (TOOLBAR_X, 40)),
    "rectangle":  ("Rect", (TOOLBAR_X, 70)),
    "circle":     ("Circle", (TOOLBAR_X, 100)),
    "square":     ("Sq", (TOOLBAR_X, 130)),
    "r_triangle": ("RTriangle", (TOOLBAR_X, 160)),
    "e_triangle": ("ETriangle", (TOOLBAR_X, 190)),
    "rhombus":    ("Rhombus", (TOOLBAR_X, 220)),
    "bucket":     ("Bucket", (TOOLBAR_X, 250)),
    "text":       ("Text", (TOOLBAR_X, 280)),
    "eraser":     ("Erase", (TOOLBAR_X, 310)),
}

color_buttons = {
    BLACK:  (TOOLBAR_X + 10, 350),
    RED:    (TOOLBAR_X + 35, 350),
    GREEN:  (TOOLBAR_X + 60, 350),
    BLUE:   (TOOLBAR_X + 85, 350),
}

brush_size_buttons = {
    2:  (TOOLBAR_X + 5, 390),
    5:  (TOOLBAR_X + 35, 390),
    10: (TOOLBAR_X + 65, 390),
}


def save_undo_state():
    """Сохранить текущее состояние холста для отмены."""
    global undo_stack
    # Копируем текущее состояние
    state_copy = canvas.copy()
    undo_stack.append(state_copy)
    # Ограничиваем размер стека
    if len(undo_stack) > MAX_UNDO:
        undo_stack.pop(0)


def undo():
    """Отменить последнее действие."""
    global canvas, needs_redraw
    if undo_stack:
        canvas = undo_stack.pop()
        needs_redraw = True
        print("  Undo ✓")
    else:
        print("  Nothing to undo")


def clear_canvas():
    """Очистить весь холст."""
    global needs_redraw
    save_undo_state()
    canvas.fill(WHITE)
    needs_redraw = True
    print("  Canvas cleared ✓")


def save_canvas():
    """Сохранить холст в PNG с временной меткой в папку Pictures."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"canvas_{timestamp}.png"
    filepath = os.path.join(SAVE_DIR, filename)
    pygame.image.save(canvas, filepath)
    print(f"  Saved to: {filepath}")
    print(f"  📁 Open folder: {SAVE_DIR}")


def pick_color(pos):
    """Взять цвет с холста."""
    global current_color, needs_redraw
    x, y = pos
    if 0 <= x < CANVAS_W and 0 <= y < HEIGHT:
        current_color = canvas.get_at((x, y))
        needs_redraw = True


def get_button_click(pos):
    """Определить нажатую кнопку."""
    x, y = pos
    for tool, (_, (bx, by)) in toolbar_buttons.items():
        if bx <= x <= bx + 180 and by <= y <= by + 25:
            return ("tool", tool)
    for color, (cx, cy) in color_buttons.items():
        dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
        if dist <= 8: return ("color", color)
    for size, (bx, by) in brush_size_buttons.items():
        if bx <= x <= bx + 20 and by <= y <= by + 20:
            return ("size", size)
    return None


def draw_toolbar():
    """Отрисовать панель инструментов."""
    pygame.draw.rect(screen, LIGHT_BLUE, (TOOLBAR_X, 0, TOOLBAR_W, HEIGHT))
    
    # Tool buttons
    for tool, (label, pos) in toolbar_buttons.items():
        bg = BLUE if current_tool == tool else GRAY
        pygame.draw.rect(screen, bg, (pos[0], pos[1], 180, 25))
        pygame.draw.rect(screen, BLACK, (pos[0], pos[1], 180, 25), 1)
        text = small_font.render(label, True, BLACK)
        screen.blit(text, (pos[0] + 5, pos[1] + 5))
    
    # Color buttons
    for color, pos in color_buttons.items():
        pygame.draw.circle(screen, color, pos, 8)
        if color == current_color:
            pygame.draw.circle(screen, BLACK, pos, 8, 2)
    
    # Brush size
    size_label = small_font.render("Size:", True, BLACK)
    screen.blit(size_label, (TOOLBAR_X + 5, 375))
    for size, pos in brush_size_buttons.items():
        bg = DARK_GRAY if size == brush_size else GRAY
        pygame.draw.rect(screen, bg, (pos[0], pos[1], 20, 20))
        pygame.draw.rect(screen, BLACK, (pos[0], pos[1], 20, 20), 1)
        text = small_font.render(SIZE_LABELS[size], True, BLACK)
        screen.blit(text, (pos[0] + 3, pos[1] + 2))
    
    # Instructions
    y = 430
    instructions = [
        "Keys:",
        "1,2,3: Size",
        "C: Pick Color",
        "Ctrl+S: Save",
        "Del: Clear",
    ]
    for instr in instructions:
        text = small_font.render(instr, True, BLACK)
        screen.blit(text, (TOOLBAR_X + 5, y))
        y += 22


def handle_text_input(event):
    """Обработать ввод текста."""
    global text_input
    if event.key == pygame.K_RETURN:
        return "confirm"
    elif event.key == pygame.K_ESCAPE:
        return "cancel"
    elif event.key == pygame.K_BACKSPACE:
        text_input = text_input[:-1]
    else:
        text_input += event.unicode
    return "continue"


# ── Main Loop ────────────────────────────────────────────────────

running = True
while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.KEYDOWN:
            # Brush size (1, 2, 3)
            if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                size_key = event.key - pygame.K_0
                if size_key in BRUSH_SIZES:
                    brush_size = BRUSH_SIZES[size_key]
                    needs_redraw = True
            
            # Save (Ctrl+S)
            elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                save_canvas()
            
            # Undo (Ctrl+Z)
            elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                undo()
            
            # Clear (Delete)
            elif event.key == pygame.K_DELETE:
                clear_canvas()
            
            # Color picker (C)
            elif event.key == pygame.K_c:
                current_tool = "picker"
                needs_redraw = True
            
            # Text input
            elif text_mode:
                result = handle_text_input(event)
                if result == "confirm":
                    render_text(canvas, text_input, text_pos, font, current_color)
                    text_mode = False
                    text_input = ""
                    text_pos = None
                    needs_redraw = True
                elif result == "cancel":
                    text_mode = False
                    text_input = ""
                    text_pos = None
                    needs_redraw = True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            
            # Toolbar click
            if pos[0] >= TOOLBAR_X:
                click = get_button_click(pos)
                if click:
                    ctype, value = click
                    if ctype == "tool":
                        current_tool = value
                        text_mode = False
                        needs_redraw = True
                    elif ctype == "color":
                        current_color = value
                        needs_redraw = True
                    elif ctype == "size":
                        brush_size = value
                        needs_redraw = True
            
            # Canvas click
            else:
                canvas_x, canvas_y = pos
                
                if current_tool == "picker":
                    pick_color((canvas_x, canvas_y))
                    current_tool = "pencil"
                
                elif current_tool == "text":
                    text_mode = True
                    text_input = ""
                    text_pos = (canvas_x, canvas_y)
                    needs_redraw = True
                
                elif current_tool == "bucket":
                    save_undo_state()
                    flood_fill(canvas, (canvas_x, canvas_y), current_color)
                    needs_redraw = True
                
                else:
                    save_undo_state()
                    is_drawing = True
                    start_pos = (canvas_x, canvas_y)
                    prev_pos = (canvas_x, canvas_y)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if is_drawing and not text_mode:
                is_drawing = False
                end_pos = (event.pos[0], event.pos[1])
                
                # Draw final shape
                if start_pos and current_tool != "pencil" and current_tool != "eraser":
                    if current_tool == "rectangle":
                        draw_rectangle(canvas, current_color, start_pos, end_pos, brush_size)
                    elif current_tool == "circle":
                        draw_circle(canvas, current_color, start_pos, end_pos, brush_size)
                    elif current_tool == "line":
                        draw_line(canvas, current_color, start_pos, end_pos, brush_size)
                    elif current_tool == "square":
                        draw_square(canvas, current_color, start_pos, end_pos, brush_size)
                    elif current_tool == "r_triangle":
                        draw_right_triangle(canvas, current_color, start_pos, end_pos, brush_size)
                    elif current_tool == "e_triangle":
                        draw_equilateral_triangle(canvas, current_color, start_pos, end_pos, brush_size)
                    elif current_tool == "rhombus":
                        draw_rhombus(canvas, current_color, start_pos, end_pos, brush_size)
                    needs_redraw = True
                
                start_pos = None
                prev_pos = None
        
        elif event.type == pygame.MOUSEMOTION:
            if is_drawing and not text_mode:
                curr_pos = event.pos
                if curr_pos[0] < TOOLBAR_X:
                    if current_tool == "pencil":
                        draw_pencil_stroke(canvas, current_color, prev_pos, curr_pos, brush_size)
                        prev_pos = curr_pos
                        needs_redraw = True
                    elif current_tool == "eraser":
                        erase(canvas, curr_pos, brush_size)
                        needs_redraw = True
                    elif current_tool not in ("pencil", "eraser"):
                        # Preview для других инструментов
                        needs_redraw = True
    
    # ── Rendering (only if changed) ───────────────────────────────
    
    if needs_redraw or is_drawing:
        screen.fill(WHITE)
        screen.blit(canvas, (0, 0))
        
        # Live preview for shapes
        if is_drawing and start_pos and current_tool not in ("pencil", "eraser", "bucket"):
            curr_pos = pygame.mouse.get_pos()
            if curr_pos[0] < TOOLBAR_X:
                preview = canvas.copy()
                if current_tool == "rectangle":
                    draw_rectangle(preview, current_color, start_pos, curr_pos, brush_size)
                elif current_tool == "circle":
                    draw_circle(preview, current_color, start_pos, curr_pos, brush_size)
                elif current_tool == "line":
                    draw_line(preview, current_color, start_pos, curr_pos, brush_size)
                elif current_tool == "square":
                    draw_square(preview, current_color, start_pos, curr_pos, brush_size)
                elif current_tool == "r_triangle":
                    draw_right_triangle(preview, current_color, start_pos, curr_pos, brush_size)
                elif current_tool == "e_triangle":
                    draw_equilateral_triangle(preview, current_color, start_pos, curr_pos, brush_size)
                elif current_tool == "rhombus":
                    draw_rhombus(preview, current_color, start_pos, curr_pos, brush_size)
                screen.blit(preview, (0, 0))
        
        # Text input preview
        if text_mode and text_pos:
            text_preview = font.render(text_input + "|", True, current_color)
            screen.blit(text_preview, text_pos)
        
        draw_toolbar()
        
        # Info bar
        undo_count = len(undo_stack)
        info = f"Tool: {current_tool} | Size: {brush_size}px | Undo: {undo_count}"
        info_text = small_font.render(info, True, BLACK)
        screen.blit(info_text, (10, HEIGHT - 25))
        
        pygame.display.flip()
        needs_redraw = False

pygame.quit()
sys.exit()
