from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta

import streamlit as st

from app.storage.db import connect, init_db


def _query(conn: sqlite3.Connection, query: str, params: tuple = ()) -> list[dict]:
    rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def run_dashboard() -> None:
    st.set_page_config(page_title="AI Savings Tracker", layout="wide")
    st.title("AI 무료/할인 이벤트 트래커")
    st.caption("신규/변경/종료 이벤트를 한눈에 확인하고 마감 임박 이벤트를 우선 확인하세요.")

    conn = connect()
    init_db(conn)

    providers = [
        row["provider"]
        for row in conn.execute("SELECT DISTINCT provider FROM events_current ORDER BY provider").fetchall()
    ]

    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        selected_provider = st.selectbox("제공사", options=["ALL", *providers])
    with col2:
        show_ending_soon = st.checkbox("3일 이내 종료만 보기", value=False)
    with col3:
        sort_key = st.selectbox("정렬", options=["마감임박", "최신수집", "이벤트명"])

    query = "SELECT * FROM events_current"
    clauses = []
    params: list = []
    if selected_provider != "ALL":
        clauses.append("provider = ?")
        params.append(selected_provider)

    if show_ending_soon:
        cutoff = (datetime.utcnow() + timedelta(days=3)).isoformat()
        clauses.append("end_at IS NOT NULL AND end_at <= ?")
        params.append(cutoff)

    if clauses:
        query += " WHERE " + " AND ".join(clauses)

    if sort_key == "마감임박":
        query += " ORDER BY end_at IS NULL, end_at ASC"
    elif sort_key == "최신수집":
        query += " ORDER BY collected_at DESC"
    else:
        query += " ORDER BY event_title ASC"

    current_rows = _query(conn, query, tuple(params))

    tab_current, tab_history = st.tabs(["현재 이벤트", "변경 이력"])

    with tab_current:
        st.metric("현재 이벤트 수", len(current_rows))
        st.dataframe(current_rows, use_container_width=True)

    with tab_history:
        history = _query(
            conn,
            "SELECT changed_at, change_type, provider, event_title, payload_json FROM events_history ORDER BY id DESC LIMIT 200",
        )
        for row in history:
            with st.expander(f"[{row['change_type']}] {row.get('event_title') or '-'} @ {row['changed_at']}"):
                st.write(f"provider: {row.get('provider')}")
                payload_raw = row.get("payload_json") or "{}"
                try:
                    st.json(json.loads(payload_raw))
                except json.JSONDecodeError:
                    st.code(payload_raw)


if __name__ == "__main__":
    run_dashboard()
