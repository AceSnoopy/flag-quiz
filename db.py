"""Database access: Postgres when DATABASE_URL is set (production), SQLite otherwise (local dev).

Queries use "?" placeholders everywhere; the Postgres wrapper translates them.
"""
import os
import sqlite3
from pathlib import Path

from flask import g

DATABASE_URL = os.environ.get("DATABASE_URL")
DB_PATH = Path(__file__).parent / "flags.db"

SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    coins INTEGER NOT NULL DEFAULT 100,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX IF NOT EXISTS users_username_lower ON users (lower(username));

CREATE TABLE IF NOT EXISTS owned_flags (
    user_id INTEGER NOT NULL REFERENCES users(id),
    country_code TEXT NOT NULL,
    purchased_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, country_code)
);

-- In-progress and finished games. Questions live server-side so answers can't be read from the page.
CREATE TABLE IF NOT EXISTS quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    questions TEXT NOT NULL,          -- JSON: [{"answer": code, "options": [codes]}]
    picks TEXT NOT NULL DEFAULT '[]', -- JSON: [code picked per round]
    finished INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS quiz_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id INTEGER NOT NULL REFERENCES quizzes(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    score INTEGER NOT NULL,
    stars INTEGER NOT NULL,
    coins_earned INTEGER NOT NULL,
    played_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

_PG_NOW = "to_char(now() AT TIME ZONE 'utc', 'YYYY-MM-DD HH24:MI:SS')"
PG_SCHEMA = f"""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    coins INTEGER NOT NULL DEFAULT 100,
    created_at TEXT NOT NULL DEFAULT {_PG_NOW}
);
CREATE UNIQUE INDEX IF NOT EXISTS users_username_lower ON users (lower(username));

CREATE TABLE IF NOT EXISTS owned_flags (
    user_id INTEGER NOT NULL REFERENCES users(id),
    country_code TEXT NOT NULL,
    purchased_at TEXT NOT NULL DEFAULT {_PG_NOW},
    PRIMARY KEY (user_id, country_code)
);

CREATE TABLE IF NOT EXISTS quizzes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    questions TEXT NOT NULL,
    picks TEXT NOT NULL DEFAULT '[]',
    finished INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT {_PG_NOW}
);

CREATE TABLE IF NOT EXISTS quiz_results (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER NOT NULL REFERENCES quizzes(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    score INTEGER NOT NULL,
    stars INTEGER NOT NULL,
    coins_earned INTEGER NOT NULL,
    played_at TEXT NOT NULL DEFAULT {_PG_NOW}
);
"""


class _PgRow(dict):
    """Row usable like sqlite3.Row: by column name or by position."""

    def __init__(self, cols, values):
        super().__init__(zip(cols, values))
        self._values = values

    def __getitem__(self, key):
        return self._values[key] if isinstance(key, int) else super().__getitem__(key)


class _PgConnection:
    """Minimal sqlite3-style facade over a psycopg connection."""

    def __init__(self, url):
        import psycopg
        self._conn = psycopg.connect(url)

    def execute(self, sql, params=()):
        cur = self._conn.cursor(row_factory=lambda c: (
            lambda values: _PgRow([d.name for d in c.description], values)))
        cur.execute(sql.replace("?", "%s"), params or None)
        return cur

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


def _connect():
    if DATABASE_URL:
        return _PgConnection(DATABASE_URL)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_db():
    if "db" not in g:
        g.db = _connect()
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    if DATABASE_URL:
        conn = _PgConnection(DATABASE_URL)
        conn.execute(PG_SCHEMA)
        conn.commit()
        conn.close()
    else:
        with sqlite3.connect(DB_PATH) as conn:
            conn.executescript(SQLITE_SCHEMA)
