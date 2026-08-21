import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "bot_data.sqlite3"


class UserStore:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_schema()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    chat_id INTEGER PRIMARY KEY,
                    job_levels TEXT NOT NULL DEFAULT '[]',
                    fields TEXT NOT NULL DEFAULT '[]',
                    stage TEXT NOT NULL DEFAULT 'job_level',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

    def get_or_create(self, chat_id: int) -> sqlite3.Row:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO users (chat_id, created_at, updated_at) VALUES (?, ?, ?)",
                (chat_id, now, now),
            )
            return conn.execute("SELECT * FROM users WHERE chat_id = ?", (chat_id,)).fetchone()

    def get(self, chat_id: int) -> sqlite3.Row | None:
        with self._connect() as conn:
            return conn.execute("SELECT * FROM users WHERE chat_id = ?", (chat_id,)).fetchone()

    def toggle_job_level(self, chat_id: int, label: str) -> list[str]:
        return self._toggle(chat_id, "job_levels", label)

    def toggle_field(self, chat_id: int, label: str) -> list[str]:
        return self._toggle(chat_id, "fields", label)

    def _toggle(self, chat_id: int, column: str, label: str) -> list[str]:
        row = self.get_or_create(chat_id)
        current = json.loads(row[column])
        if label in current:
            current.remove(label)
        else:
            current.append(label)
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                f"UPDATE users SET {column} = ?, updated_at = ? WHERE chat_id = ?",
                (json.dumps(current), now, chat_id),
            )
        return current

    def set_stage(self, chat_id: int, stage: str):
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                "UPDATE users SET stage = ?, updated_at = ? WHERE chat_id = ?",
                (stage, now, chat_id),
            )