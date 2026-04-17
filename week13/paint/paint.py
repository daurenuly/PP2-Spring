import pygame

def main():
    pygame.init()
    WIDTH, HEIGHT = 900, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Fast Paint")

    clock = pygame.time.Clock()

    # separate surface for drawing (BIG performance boost)
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

                # 🎨 Colors
                if event.key == pygame.K_1:
                    color = (255, 0, 0)
                elif event.key == pygame.K_2:
                    color = (0, 255, 0)
                elif event.key == pygame.K_3:
                    color = (0, 0, 255)
                elif event.key == pygame.K_4:
                    color = (255, 255, 0)
                elif event.key == pygame.K_5:
                    color = (255, 255, 255)

                # 🛠 Tools
                if event.key == pygame.K_b:
                    tool = "brush"
                elif event.key == pygame.K_r:
                    tool = "rect"
                elif event.key == pygame.K_c:
                    tool = "circle"
                elif event.key == pygame.K_e:
                    tool = "eraser"

                # clear
                if event.key == pygame.K_x:
                    canvas.fill((0, 0, 0))

            if event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
                start_pos = event.pos

            if event.type == pygame.MOUSEBUTTONUP:
                drawing = False
                end_pos = event.pos

                if tool == "rect":
                    rect = pygame.Rect(start_pos, (end_pos[0]-start_pos[0], end_pos[1]-start_pos[1]))
                    pygame.draw.rect(canvas, color, rect, 2)

                elif tool == "circle":
                    dx = end_pos[0] - start_pos[0]
                    dy = end_pos[1] - start_pos[1]
                    r = int((dx*dx + dy*dy) ** 0.5)
                    pygame.draw.circle(canvas, color, start_pos, r, 2)

            if event.type == pygame.MOUSEMOTION and drawing:
                if tool == "brush":
                    pygame.draw.circle(canvas, color, event.pos, radius)
                elif tool == "eraser":
                    pygame.draw.circle(canvas, (0, 0, 0), event.pos, radius)

        # draw everything once per frame (fast)
        screen.fill((30, 30, 30))
        screen.blit(canvas, (0, 0))

        # 🎨 COLOR INDICATOR
        pygame.draw.rect(screen, color, (10, 10, 40, 40))

        # 🛠 TOOL INDICATOR
        text = font.render(f"Tool: {tool}", True, (255, 255, 255))
        screen.blit(text, (60, 15))

        pygame.display.flip()
        clock.tick(60)


main()