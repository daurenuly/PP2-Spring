import pygame
import sys
import math
from datetime import datetime


class MickeyClock:
    def __init__(self):
        pygame.init()

        self.WIDTH, self.HEIGHT = 600, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Mickey Clock")

        self.clock = pygame.time.Clock()
        self.center = (self.WIDTH // 2, self.HEIGHT // 2)

        
        self.background = pygame.image.load("images/mickeyclock.jpeg")
        self.background = pygame.transform.scale(
            self.background, (self.WIDTH, self.HEIGHT)
        )

    def draw_mickey_glove(self, length, angle_deg):
        
        angle_rad = math.radians(angle_deg)

        end_x = self.center[0] + length * math.sin(angle_rad)
        end_y = self.center[1] - length * math.cos(angle_rad)

        mid_x = self.center[0] + (length - 40) * math.sin(angle_rad)
        mid_y = self.center[1] - (length - 40) * math.cos(angle_rad)

        
        pygame.draw.line(self.screen, (0, 0, 0),
                         self.center, (mid_x, mid_y), 12)

        pygame.draw.circle(self.screen, (255, 255, 255),
                           (int(end_x), int(end_y)), 18)

        
        for offset in [-20, 0, 20]:
            finger_angle = math.radians(angle_deg + offset)
            fx = end_x + 15 * math.sin(finger_angle)
            fy = end_y - 15 * math.cos(finger_angle)

            pygame.draw.circle(self.screen, (255, 255, 255),
                               (int(fx), int(fy)), 8)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            now = datetime.now()
            minutes = now.minute
            seconds = now.second

            minute_angle = minutes * 6
            second_angle = seconds * 6

            
            self.screen.blit(self.background, (0, 0))

            self.draw_mickey_glove(140, minute_angle)
            self.draw_mickey_glove(180, second_angle)  

            
            pygame.draw.circle(self.screen, (0, 0, 0), self.center, 6)

            pygame.display.flip()
            self.clock.tick(1)