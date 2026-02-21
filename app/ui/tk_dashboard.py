from __future__ import annotations

import json
import sqlite3
import tkinter as tk
from tkinter import ttk

from app.storage.db import connect, init_db


def _fetch_current(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT provider, event_title, event_type, end_at, source_url FROM events_current ORDER BY end_at IS NULL, end_at ASC"
    ).fetchall()


def _fetch_history(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT changed_at, change_type, provider, event_title, payload_json FROM events_history ORDER BY id DESC LIMIT 100"
    ).fetchall()


def run_tk_dashboard() -> None:
    conn = connect()
    init_db(conn)

    root = tk.Tk()
    root.title("AI 무료/할인 이벤트 트래커")
    root.geometry("980x620")

    tabs = ttk.Notebook(root)
    tabs.pack(fill="both", expand=True)

    current_tab = ttk.Frame(tabs)
    history_tab = ttk.Frame(tabs)
    tabs.add(current_tab, text="현재 이벤트")
    tabs.add(history_tab, text="변경 이력")

    current_tree = ttk.Treeview(current_tab, columns=("provider", "title", "type", "end_at", "url"), show="headings")
    for col, title, width in [
        ("provider", "제공사", 120),
        ("title", "이벤트", 330),
        ("type", "유형", 120),
        ("end_at", "종료일", 160),
        ("url", "원문 URL", 240),
    ]:
        current_tree.heading(col, text=title)
        current_tree.column(col, width=width, anchor="w")
    current_tree.pack(fill="both", expand=True)

    for row in _fetch_current(conn):
        current_tree.insert("", "end", values=(row["provider"], row["event_title"], row["event_type"], row["end_at"] or "-", row["source_url"]))

    history_text = tk.Text(history_tab, wrap="none")
    history_text.pack(fill="both", expand=True)
    for row in _fetch_history(conn):
        history_text.insert(
            "end",
            f"[{row['changed_at']}] {row['change_type']} | {row['provider']} | {row['event_title']}\n",
        )
        try:
            parsed = json.loads(row["payload_json"] or "{}")
            history_text.insert("end", f"  {json.dumps(parsed, ensure_ascii=False)}\n\n")
        except json.JSONDecodeError:
            history_text.insert("end", f"  {row['payload_json']}\n\n")

    root.mainloop()


if __name__ == "__main__":
    run_tk_dashboard()
