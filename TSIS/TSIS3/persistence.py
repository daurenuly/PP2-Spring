"""persistence.py — Save/load leaderboard and settings to JSON files."""

import json
import os

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE    = "settings.json"

DEFAULT_SETTINGS = {
    "sound":       True,
    "car_color":   "red",       # red | blue | green | yellow
    "difficulty":  "normal",    # easy | normal | hard
}

# ── Settings ─────────────────────────────────────────────────────

def load_settings() -> dict:
    if os.path.isfile(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, encoding="utf-8") as f:
                data = json.load(f)
            # Merge with defaults so missing keys are filled in
            return {**DEFAULT_SETTINGS, **data}
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> None:
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


# ── Leaderboard ───────────────────────────────────────────────────

def load_leaderboard() -> list[dict]:
    """Return list of dicts: [{name, score, distance, coins}]"""
    if os.path.isfile(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except Exception:
            pass
    return []


def save_score(name: str, score: int, distance: int, coins: int) -> None:
    """Append a score entry and keep only the top 10."""
    board = load_leaderboard()
    board.append({"name": name, "score": score, "distance": distance, "coins": coins})
    board.sort(key=lambda x: x["score"], reverse=True)
    board = board[:10]
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(board, f, indent=2)