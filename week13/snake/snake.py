import pygame
import random
import time


SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
BLOCK_SIZE = 20
INITIAL_SPEED = 10
SPEED_INCREMENT = 3
FOOD_PER_LEVEL = 3

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (213, 50, 80)
COLOR_GREEN = (0, 255, 0)

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Extended Snake Game')
        self.clock = pygame.time.Clock()
        
        # Game State
        self.reset_game()

    def reset_game(self):
        """Initializes or resets the game variables."""
        self.snake_pos = [100, 60]
        self.snake_body = [[100, 60], [80, 60], [60, 60]]
        self.direction = 'RIGHT'
        self.change_to = self.direction
        
        self.score = 0
        self.level = 1
        self.speed = INITIAL_SPEED
        self.food_spawn = False
        self.spawn_food()
        self.game_over = False

    def spawn_food(self):
        """Generates random food position that doesn't overlap with the snake or walls."""
        while True:
            # Generate random coords aligned to the grid
            x = random.randrange(0, (SCREEN_WIDTH // BLOCK_SIZE)) * BLOCK_SIZE
            y = random.randrange(0, (SCREEN_HEIGHT // BLOCK_SIZE)) * BLOCK_SIZE
            self.food_pos = [x, y]
            
            # Ensure food is not spawning inside the snake's body
            if self.food_pos not in self.snake_body:
                self.food_spawn = True
                break

    def show_stats(self):
        """Renders the current Score and Level on screen."""
        font = pygame.font.SysFont('arial', 20)
        stats_surface = font.render(f'Score: {self.score}  |  Level: {self.level}', True, COLOR_WHITE)
        self.display.blit(stats_surface, [10, 10])

    def check_level_up(self):
        """Increases level and speed every 3-4 food items."""
        if self.score > 0 and self.score % FOOD_PER_LEVEL == 0:
            # Calculate what the level should be based on score
            new_level = (self.score // FOOD_PER_LEVEL) + 1
            if new_level > self.level:
                self.level = new_level
                self.speed += SPEED_INCREMENT  # Increase speed for difficulty

    def run(self):
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.direction != 'DOWN':
                        self.change_to = 'UP'
                    if event.key == pygame.K_DOWN and self.direction != 'UP':
                        self.change_to = 'DOWN'
                    if event.key == pygame.K_LEFT and self.direction != 'RIGHT':
                        self.change_to = 'LEFT'
                    if event.key == pygame.K_RIGHT and self.direction != 'LEFT':
                        self.change_to = 'RIGHT'

            self.direction = self.change_to

            # Update Snake Position
            if self.direction == 'UP': self.snake_pos[1] -= BLOCK_SIZE
            if self.direction == 'DOWN': self.snake_pos[1] += BLOCK_SIZE
            if self.direction == 'LEFT': self.snake_pos[0] -= BLOCK_SIZE
            if self.direction == 'RIGHT': self.snake_pos[0] += BLOCK_SIZE

            # --- 1. Border Collision Detection ---
            if (self.snake_pos[0] < 0 or self.snake_pos[0] > SCREEN_WIDTH - BLOCK_SIZE or
                self.snake_pos[1] < 0 or self.snake_pos[1] > SCREEN_HEIGHT - BLOCK_SIZE):
                self.game_over = True

            # --- 2. Self Collision Detection ---
            for block in self.snake_body[1:]:
                if self.snake_pos == block:
                    self.game_over = True

            # Snake body growing mechanism
            self.snake_body.insert(0, list(self.snake_pos))
            if self.snake_pos == self.food_pos:
                self.score += 1
                self.check_level_up() # Check for level/speed increase
                self.food_spawn = False
            else:
                self.snake_body.pop()

            if not self.food_spawn:
                self.spawn_food()

            # Graphics
            self.display.fill(COLOR_BLACK)
            for pos in self.snake_body:
                pygame.draw.rect(self.display, COLOR_GREEN, pygame.Rect(pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE))
            
            pygame.draw.rect(self.display, COLOR_RED, pygame.Rect(self.food_pos[0], self.food_pos[1], BLOCK_SIZE, BLOCK_SIZE))

            self.show_stats()
            pygame.display.update()
            self.clock.tick(self.speed)

        pygame.quit()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()