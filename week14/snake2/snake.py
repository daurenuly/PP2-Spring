import pygame
import random
import time

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
BLOCK_SIZE = 20
INITIAL_SPEED = 10
SPEED_INCREMENT = 2
FOOD_PER_LEVEL = 3
FOOD_TIMEOUT = 5  # Food disappears after 5 seconds

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GREEN = (0, 255, 0)
# Different colors for different food weights
FOOD_COLORS = {
    1: (200, 0, 0),    # Dark Red (Weight 1)
    2: (255, 100, 0),  # Orange (Weight 2)
    3: (255, 255, 0)   # Yellow (Weight 3)
}

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Weighted & Timed Snake Game')
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
        self.game_over = False

        # Food variables
        self.food_pos = [0, 0]
        self.food_weight = 1
        self.food_spawn_time = 0
        self.spawn_food()

    def spawn_food(self):
        """Generates random food with a weight and a timestamp."""
        while True:
            x = random.randrange(0, (SCREEN_WIDTH // BLOCK_SIZE)) * BLOCK_SIZE
            y = random.randrange(0, (SCREEN_HEIGHT // BLOCK_SIZE)) * BLOCK_SIZE
            self.food_pos = [x, y]
            
            # Ensure food doesn't spawn on snake
            if self.food_pos not in self.snake_body:
                # Random weight: 1, 2, or 3
                self.food_weight = random.choice([1, 2, 3])
                # Record the time the food was created
                self.food_spawn_time = time.time()
                break

    def show_stats(self):
        """Renders Score, Level, and the remaining time for the current food."""
        font = pygame.font.SysFont('arial', 20)
        
        # Calculate remaining time for food
        elapsed = time.time() - self.food_spawn_time
        remaining = max(0, int(FOOD_TIMEOUT - elapsed))
        
        stats_str = f'Score: {self.score}  |  Level: {self.level}  |  Food Timer: {remaining}s'
        stats_surface = font.render(stats_str, True, COLOR_WHITE)
        self.display.blit(stats_surface, [10, 10])

    def check_level_up(self):
        """Increases level based on score milestones."""
        new_level = (self.score // (FOOD_PER_LEVEL * 2)) + 1
        if new_level > self.level:
            self.level = new_level
            self.speed += SPEED_INCREMENT

    def run(self):
        while not self.game_over:
            # 1. Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
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

            # 2. Movement
            if self.direction == 'UP': self.snake_pos[1] -= BLOCK_SIZE
            if self.direction == 'DOWN': self.snake_pos[1] += BLOCK_SIZE
            if self.direction == 'LEFT': self.snake_pos[0] -= BLOCK_SIZE
            if self.direction == 'RIGHT': self.snake_pos[0] += BLOCK_SIZE

            # 3. Collision Detection (Borders)
            if (self.snake_pos[0] < 0 or self.snake_pos[0] >= SCREEN_WIDTH or
                self.snake_pos[1] < 0 or self.snake_pos[1] >= SCREEN_HEIGHT):
                self.game_over = True

            # 4. Collision Detection (Self)
            if self.snake_pos in self.snake_body:
                self.game_over = True

            # 5. Food Logic (Weight and Timer)
            # Check if food has expired
            if time.time() - self.food_spawn_time > FOOD_TIMEOUT:
                self.spawn_food()

            self.snake_body.insert(0, list(self.snake_pos))

            if self.snake_pos == self.food_pos:
                # Add score based on food weight
                self.score += self.food_weight
                
                # Growing logic: If weight > 1, we don't pop the tail for a few frames
                # but to keep it simple, we just don't pop once. 
                # For high weights, the snake will naturally get longer because
                # we only pop the tail if we DON'T eat.
                
                self.check_level_up()
                self.spawn_food()
            else:
                # If no food eaten, remove the last segment to maintain length
                self.snake_body.pop()

            # 6. Drawing
            self.display.fill(COLOR_BLACK)
            
            # Draw Snake
            for pos in self.snake_body:
                pygame.draw.rect(self.display, COLOR_GREEN, 
                                 pygame.Rect(pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE))
            
            # Draw Weighted Food with specific color
            food_color = FOOD_COLORS.get(self.food_weight, COLOR_WHITE)
            pygame.draw.rect(self.display, food_color, 
                             pygame.Rect(self.food_pos[0], self.food_pos[1], BLOCK_SIZE, BLOCK_SIZE))

            self.show_stats()
            pygame.display.update()
            
            # Control game speed
            self.clock.tick(self.speed)

        pygame.quit()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()