import pygame
import math

def main():
    pygame.init()
    WIDTH, HEIGHT = 900, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Advanced Paint")

    clock = pygame.time.Clock()

    # Surface for drawing to keep previous strokes
    canvas = pygame.Surface((WIDTH, HEIGHT))
    canvas.fill((0, 0, 0))

    color = (0, 0, 255)
    radius = 5
    tool = "brush"

    drawing = False
    start_pos = None

    font = pygame.font.SysFont(None, 24)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

                # Colors (1-5)
                if event.key == pygame.K_1: color = (255, 0, 0)
                elif event.key == pygame.K_2: color = (0, 255, 0)
                elif event.key == pygame.K_3: color = (0, 0, 255)
                elif event.key == pygame.K_4: color = (255, 255, 0)
                elif event.key == pygame.K_5: color = (255, 255, 255)

                # --- Tool Selection ---
                if event.key == pygame.K_b: tool = "brush"
                elif event.key == pygame.K_e: tool = "eraser"
                elif event.key == pygame.K_r: tool = "rect"
                elif event.key == pygame.K_s: tool = "square"
                elif event.key == pygame.K_t: tool = "right_tri"
                elif event.key == pygame.K_q: tool = "equi_tri"
                elif event.key == pygame.K_h: tool = "rhombus"
                elif event.key == pygame.K_x: canvas.fill((0, 0, 0)) # Clear

            if event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
                start_pos = event.pos

            if event.type == pygame.MOUSEBUTTONUP:
                drawing = False
                end_pos = event.pos
                
                # Logic for "Shape" tools (drawn on release)
                if tool == "rect":
                    width = end_pos[0] - start_pos[0]
                    height = end_pos[1] - start_pos[1]
                    pygame.draw.rect(canvas, color, (start_pos[0], start_pos[1], width, height), 2)

                elif tool == "square":
                    # Force width and height to be the same
                    side = max(abs(end_pos[0] - start_pos[0]), abs(end_pos[1] - start_pos[1]))
                    # Determine direction (allowing drawing in any quadrant)
                    s_x = start_pos[0] if end_pos[0] > start_pos[0] else start_pos[0] - side
                    s_y = start_pos[1] if end_pos[1] > start_pos[1] else start_pos[1] - side
                    pygame.draw.rect(canvas, color, (s_x, s_y, side, side), 2)

                elif tool == "right_tri":
                    # Vertices: Start, End, and a third point to make it 90 degrees
                    points = [start_pos, end_pos, (start_pos[0], end_pos[1])]
                    pygame.draw.polygon(canvas, color, points, 2)

                elif tool == "equi_tri":
                    # Calculate distance for base length
                    side = math.sqrt((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2)
                    height_tri = (math.sqrt(3) / 2) * side
                    # Calculate vertices based on angle
                    points = [
                        start_pos, 
                        end_pos, 
                        ( (start_pos[0] + end_pos[0]) / 2 - (end_pos[1] - start_pos[1]) * math.sqrt(3) / 2,
                          (start_pos[1] + end_pos[1]) / 2 + (end_pos[0] - start_pos[0]) * math.sqrt(3) / 2 )
                    ]
                    pygame.draw.polygon(canvas, color, points, 2)

                elif tool == "rhombus":
                    # Draw using the start position as center and end position as extent
                    dx = abs(end_pos[0] - start_pos[0])
                    dy = abs(end_pos[1] - start_pos[1])
                    points = [
                        (start_pos[0], start_pos[1] - dy), # Top
                        (start_pos[0] + dx, start_pos[1]), # Right
                        (start_pos[0], start_pos[1] + dy), # Bottom
                        (start_pos[0] - dx, start_pos[1])  # Left
                    ]
                    pygame.draw.polygon(canvas, color, points, 2)

            if event.type == pygame.MOUSEMOTION and drawing:
                # Continuous tools (drawn while moving)
                if tool == "brush":
                    pygame.draw.circle(canvas, color, event.pos, radius)
                elif tool == "eraser":
                    pygame.draw.circle(canvas, (0, 0, 0), event.pos, radius * 2)

        # Rendering
        screen.fill((30, 30, 30))
        screen.blit(canvas, (0, 0))

        # UI Indicators
        pygame.draw.rect(screen, color, (10, 10, 40, 40))
        instructions = "B:Brush, E:Eraser, R:Rect, S:Square, T:Right-Tri, Q:Equi-Tri, H:Rhombus, X:Clear"
        text_tool = font.render(f"Tool: {tool.upper()}", True, (255, 255, 255))
        text_help = font.render(instructions, True, (200, 200, 200))
        
        screen.blit(text_tool, (60, 15))
        screen.blit(text_help, (10, HEIGHT - 30))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()