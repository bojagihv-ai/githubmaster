from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable

from app.normalizers.schema import PromotionEvent

DB_PATH = Path("data/events.db")


def connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, col_type: str) -> None:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    cols = {row[1] for row in rows}
    if column not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS events_current (
            fingerprint TEXT PRIMARY KEY,
            identity_key TEXT,
            provider TEXT,
            event_title TEXT,
            event_type TEXT,
            region TEXT,
            start_at TEXT,
            end_at TEXT,
            price_before REAL,
            price_after REAL,
            currency TEXT,
            credit_amount REAL,
            credit_unit TEXT,
            eligibility TEXT,
            source_url TEXT,
            collected_at TEXT
        );

        CREATE TABLE IF NOT EXISTS events_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fingerprint TEXT,
            identity_key TEXT,
            provider TEXT,
            event_title TEXT,
            change_type TEXT,
            payload_json TEXT,
            changed_at TEXT
        );
        """
    )
    _ensure_column(conn, "events_current", "identity_key", "TEXT")
    _ensure_column(conn, "events_history", "identity_key", "TEXT")
    _ensure_column(conn, "events_history", "provider", "TEXT")
    _ensure_column(conn, "events_history", "event_title", "TEXT")
    conn.commit()


def load_current_events(conn: sqlite3.Connection) -> dict[str, sqlite3.Row]:
    rows = conn.execute("SELECT * FROM events_current").fetchall()
    return {row["identity_key"] or row["fingerprint"]: row for row in rows}


def replace_current_events(conn: sqlite3.Connection, events: Iterable[PromotionEvent]) -> None:
    conn.execute("DELETE FROM events_current")
    conn.executemany(
        """
        INSERT INTO events_current (
            fingerprint, identity_key, provider, event_title, event_type, region, start_at, end_at,
            price_before, price_after, currency, credit_amount, credit_unit,
            eligibility, source_url, collected_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                e.fingerprint,
                e.identity_key,
                e.provider,
                e.event_title,
                e.event_type,
                e.region,
                e.start_at.isoformat() if e.start_at else None,
                e.end_at.isoformat() if e.end_at else None,
                e.price_before,
                e.price_after,
                e.currency,
                e.credit_amount,
                e.credit_unit,
                e.eligibility,
                e.source_url,
                e.collected_at.isoformat(),
            )
            for e in events
        ],
    )
    conn.commit()


def insert_history(
    conn: sqlite3.Connection,
    fingerprint: str,
    identity_key: str,
    provider: str,
    event_title: str,
    change_type: str,
    payload_json: str,
) -> None:
    conn.execute(
        "INSERT INTO events_history (fingerprint, identity_key, provider, event_title, change_type, payload_json, changed_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (fingerprint, identity_key, provider, event_title, change_type, payload_json, datetime.utcnow().isoformat()),
    )
    conn.commit()
