# Imports
import pygame, sys
from pygame.locals import *
import random, time

# Initializing 
pygame.init()

# Setting up FPS 
FPS = 60
FramePerSec = pygame.time.Clock()

# Creating colors
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Screen settings
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Game variables
SPEED = 5
SCORE = 0          # score for dodging enemies
COINS_COLLECTED = 0   # NEW: coins counter

# Fonts
font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over = font.render("Game Over", True, BLACK)

# Background image
background = pygame.image.load("C:\\Users\\abyla\\OneDrive\\Документы\\PP2\\week13\\pygametutorial\\AnimatedStreet.png")

# Screen setup
DISPLAYSURF = pygame.display.set_mode((400,600))
pygame.display.set_caption("Game")

# ---------------- ENEMY CLASS ----------------
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("C:\\Users\\abyla\\OneDrive\\Документы\\PP2\\week13\\pygametutorial\\Enemy.png")
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH-40), 0)

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)

        # If enemy goes off screen → reset and increase score
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.rect.top = 0
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

# ---------------- PLAYER CLASS ----------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("C:\\Users\\abyla\\OneDrive\\Документы\\PP2\\week13\\pygametutorial\\Player.png")
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)

    def move(self):
        pressed_keys = pygame.key.get_pressed()

        # Move left
        if self.rect.left > 0:
            if pressed_keys[K_LEFT]:
                self.rect.move_ip(-5, 0)

        # Move right
        if self.rect.right < SCREEN_WIDTH:
            if pressed_keys[K_RIGHT]:
                self.rect.move_ip(5, 0)

# ---------------- COIN CLASS (NEW) ----------------
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        original_image = pygame.image.load("C:\\Users\\abyla\\OneDrive\\Документы\\PP2\\week13\\pygametutorial\\coin.png")
        
        self.image = pygame.transform.scale(original_image, (30, 30))
        
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH-40), 0)
        

    def move(self):
        self.rect.move_ip(0, SPEED)

        # If coin goes off screen → respawn at top
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.top = 0
            self.rect.center = (random.randint(40, SCREEN_WIDTH-40), 0)

# Create player and enemy
P1 = Player()
E1 = Enemy()
C1 = Coin()   # NEW coin

# Sprite groups
enemies = pygame.sprite.Group()
enemies.add(E1)

coins = pygame.sprite.Group()   # NEW group
coins.add(C1)

all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)
all_sprites.add(C1)

# Speed increase event
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

# ---------------- GAME LOOP ----------------
while True:

    # Handle events
    for event in pygame.event.get():
        if event.type == INC_SPEED:
            SPEED += 0.5
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Draw background
    DISPLAYSURF.blit(background, (0,0))

    # Draw score (top-left)
    score_text = font_small.render("Score: " + str(SCORE), True, BLACK)
    DISPLAYSURF.blit(score_text, (10,10))

    # Draw coins collected (top-right)
    coin_text = font_small.render("Coins: " + str(COINS_COLLECTED), True, BLACK)
    DISPLAYSURF.blit(coin_text, (SCREEN_WIDTH - 120, 10))

    # Move and draw all sprites
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # -------- COLLISION: PLAYER & COIN --------
    collected = pygame.sprite.spritecollide(P1, coins, True)
    if collected:
        COINS_COLLECTED += 1

        # Spawn a new coin after collecting
        new_coin = Coin()
        coins.add(new_coin)
        all_sprites.add(new_coin)

    # -------- COLLISION: PLAYER & ENEMY --------
    if pygame.sprite.spritecollideany(P1, enemies):
        pygame.mixer.Sound('C://Users//abyla//OneDrive//Документы//PP2//week13//pygametutorial//crash.wav').play()
        time.sleep(0.5)

        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over, (30,250))

        pygame.display.update()

        # Remove all sprites
        for entity in all_sprites:
            entity.kill()

        time.sleep(2)
        pygame.quit()
        sys.exit()

    pygame.display.update()
    FramePerSec.tick(FPS)