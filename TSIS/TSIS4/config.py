"""config.py — Database connection and game constants."""

# ── PostgreSQL connection ─────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "snake_db",
    "user":     "postgres",
    "password": "1234", 
}

# ── Window & grid ─────────────────────────────────────────────────
CELL        = 24          # pixels per grid cell
COLS        = 25          # grid columns
ROWS        = 22          # grid rows
PANEL_H     = 60          # top HUD panel height
W           = CELL * COLS
H           = CELL * ROWS + PANEL_H
FPS_DEFAULT = 8           # base snake speed (frames per move)

# ── Colors ────────────────────────────────────────────────────────
BLACK   = (0,   0,   0)
WHITE   = (255, 255, 255)
GRAY    = (50,  50,  50)
LGRAY   = (160, 160, 160)
DARK    = (18,  18,  28)
PANEL   = (28,  28,  44)
ACCENT  = (0,   220, 180)
RED     = (220, 50,  50)
GREEN   = (60,  200, 80)
BLUE    = (50,  120, 220)
YELLOW  = (240, 200, 30)
ORANGE  = (255, 140, 0)
PURPLE  = (160, 60,  220)
CYAN    = (0,   200, 220)
POISON  = (120, 20,  20)   # poison food

# Food color by weight
FOOD_COLORS = {1: (220, 80, 80), 3: (240, 160, 30), 5: (80, 180, 255)}

# Power-up colors
PU_COLORS = {"speed": ORANGE, "slow": CYAN, "shield": PURPLE}