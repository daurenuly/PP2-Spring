import pygame
import sys


class RedBallGame:
    def __init__(self):
        pygame.init()

        self.WIDTH, self.HEIGHT = 600, 400
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Red Ball Game")

        self.clock = pygame.time.Clock()

        # 🔴 шар
        self.radius = 25
        self.x = self.WIDTH // 2
        self.y = self.HEIGHT // 2

        
        self.speed = 200  

    def handle_keys(self, dt):
        keys = pygame.key.get_pressed()

        move = self.speed * dt  

        if keys[pygame.K_LEFT]:
            if self.x - move - self.radius >= 0:
                self.x -= move

        if keys[pygame.K_RIGHT]:
            if self.x + move + self.radius <= self.WIDTH:
                self.x += move

        if keys[pygame.K_UP]:
            if self.y - move - self.radius >= 0:
                self.y -= move

        if keys[pygame.K_DOWN]:
            if self.y + move + self.radius <= self.HEIGHT:
                self.y += move

    def draw(self):
        self.screen.fill((255, 255, 255))

        pygame.draw.circle(
            self.screen,
            (255, 0, 0),
            (int(self.x), int(self.y)),
            self.radius
        )

    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000  
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.handle_keys(dt)
            self.draw()

            pygame.display.flip()