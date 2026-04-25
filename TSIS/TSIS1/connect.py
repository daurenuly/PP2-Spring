"""
connect.py – thin wrapper that returns a psycopg2 connection.
Import get_connection() wherever a DB connection is needed.
"""

import psycopg2
from config import DB_CONFIG


def get_connection():
    """Return an open psycopg2 connection using settings from config.py."""
    return psycopg2.connect(**DB_CONFIG)
