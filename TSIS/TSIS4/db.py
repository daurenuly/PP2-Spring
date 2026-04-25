"""db.py — PostgreSQL integration via psycopg2."""

import psycopg2
import psycopg2.extras
from config import DB_CONFIG

SCHEMA = """
CREATE TABLE IF NOT EXISTS players (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS game_sessions (
    id            SERIAL PRIMARY KEY,
    player_id     INTEGER REFERENCES players(id),
    score         INTEGER   NOT NULL,
    level_reached INTEGER   NOT NULL,
    played_at     TIMESTAMP DEFAULT NOW()
);
"""


def get_conn():
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    """Create tables if they don't exist."""
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(SCHEMA)
    conn.commit()
    conn.close()


def get_or_create_player(username: str) -> int:
    """Return player id, creating the player row if needed."""
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO players(username) VALUES(%s) ON CONFLICT(username) DO NOTHING",
            (username,)
        )
        conn.commit()
        cur.execute("SELECT id FROM players WHERE username=%s", (username,))
        pid = cur.fetchone()[0]
    conn.close()
    return pid


def save_session(player_id: int, score: int, level: int) -> None:
    """Save a completed game session."""
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO game_sessions(player_id, score, level_reached) VALUES(%s,%s,%s)",
            (player_id, score, level)
        )
    conn.commit()
    conn.close()


def get_personal_best(player_id: int) -> int:
    """Return the player's highest score ever (0 if none)."""
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COALESCE(MAX(score), 0) FROM game_sessions WHERE player_id=%s",
            (player_id,)
        )
        best = cur.fetchone()[0]
    conn.close()
    return best


def get_leaderboard() -> list[dict]:
    """Return top 10 scores across all players."""
    conn = get_conn()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
            SELECT p.username, gs.score, gs.level_reached,
                   TO_CHAR(gs.played_at, 'YYYY-MM-DD') AS date
            FROM   game_sessions gs
            JOIN   players p ON p.id = gs.player_id
            ORDER  BY gs.score DESC
            LIMIT  10
        """)
        rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows