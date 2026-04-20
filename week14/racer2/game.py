import pygame, sys
from pygame.locals import *
import random, time

# Initializing 
pygame.init()

# Setting up FPS 
FPS = 60
FramePerSec = pygame.time.Clock()

# Creating colors
RED   = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Screen settings
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Game variables
SPEED = 5
SCORE = 0            # Score for dodging enemies
COINS_COLLECTED = 0   # Total value of coins collected
N = 10                # Increase enemy speed every N coins collected
LAST_SPEED_UP = 0     # Tracking the last milestone for speed increase

# Fonts
font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over = font.render("Game Over", True, BLACK)

# Background image
# Note: Ensure paths are correct for your local machine
background = pygame.image.load("C://Users//abyla//OneDrive//Документы//PP2\week14//files//AnimatedStreet.png")

# Screen setup
DISPLAYSURF = pygame.display.set_mode((400,600))
pygame.display.set_caption("Racer - Weighted Coins")

# ---------------- ENEMY CLASS ----------------
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("C://Users//abyla//OneDrive//Документы//PP2//week14//files//Enemy.png")
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH-40), 0)

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.rect.top = 0
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

# ---------------- PLAYER CLASS ----------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("C://Users//abyla//OneDrive//Документы//PP2//week14//files//Player.png")
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)

    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if self.rect.left > 0 and pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if self.rect.right < SCREEN_WIDTH and pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)

# ---------------- COIN CLASS (UPDATED) ----------------
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Randomly assign a weight to the coin
        # 1 = Common, 3 = Rare, 5 = Super Rare
        self.weight = random.choices([1, 3, 5], weights=[70, 20, 10], k=1)[0]
        
        original_image = pygame.image.load("C://Users//abyla//OneDrive//Документы//PP2//week14//files//coin.png")
        
        # Scale the coin based on weight (higher weight = slightly larger/different scale)
        size = 20 + (self.weight * 3) 
        self.image = pygame.transform.scale(original_image, (size, size))
        
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH-40), 0)

    def move(self):
        self.rect.move_ip(0, SPEED)
        # Reset coin if it falls off the screen
        if self.rect.top > SCREEN_HEIGHT:
            self.spawn_new()

    def spawn_new(self):
        # Re-randomize weight when respawning
        self.weight = random.choices([1, 3, 5], weights=[70, 20, 10], k=1)[0]
        size = 20 + (self.weight * 3)
        # Update image to reflect new weight
        self.image = pygame.transform.scale(pygame.image.load("C://Users//abyla//OneDrive//Документы//PP2//week14//files//coin.png"), (size, size))
        self.rect = self.image.get_rect()
        self.rect.top = 0
        self.rect.center = (random.randint(40, SCREEN_WIDTH-40), 0)

# Initialization
P1 = Player()
E1 = Enemy()
C1 = Coin()

enemies = pygame.sprite.Group()
enemies.add(E1)

coins = pygame.sprite.Group()
coins.add(C1)

all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)
all_sprites.add(C1)

# Game Loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Increase Enemy Speed when Player earns N coins
    # We check if the current total floor-divided by N has increased
    if (COINS_COLLECTED // N) > LAST_SPEED_UP:
        SPEED += 1
        LAST_SPEED_UP = COINS_COLLECTED // N
        print(f"Speed increased! Current speed: {SPEED}")

    DISPLAYSURF.blit(background, (0,0))
    
    # UI Text
    score_text = font_small.render("Dodged: " + str(SCORE), True, BLACK)
    coin_text = font_small.render("Total Value: " + str(COINS_COLLECTED), True, BLACK)
    
    DISPLAYSURF.blit(score_text, (10,10))
    DISPLAYSURF.blit(coin_text, (SCREEN_WIDTH - 180, 10))

    # Move and Draw
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # COLLISION: PLAYER & COIN
    # Using spritecollide to get the specific coin object to access its weight
    coin_hit_list = pygame.sprite.spritecollide(P1, coins, False)
    for coin in coin_hit_list:
        COINS_COLLECTED += coin.weight  # Add the specific weight of the coin
        coin.spawn_new()                # Move coin back to top instead of killing it

    # COLLISION: PLAYER & ENEMY
    if pygame.sprite.spritecollideany(P1, enemies):
        # Note: Ensure crash.wav exists or wrap in try/except
        try:
            pygame.mixer.Sound('C://Users//abyla//OneDrive//Документы//PP2//week14//files//crash.wav').play()
        except:
            pass
            
        time.sleep(0.5)
        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over, (30,250))
        pygame.display.update()
        
        for entity in all_sprites:
            entity.kill()
            
        time.sleep(2)
        pygame.quit()
        sys.exit()

    pygame.display.update()
    FramePerSec.tick(FPS)