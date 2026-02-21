from __future__ import annotations

import pandas as pd
import streamlit as st

from app.storage.db import connect, init_db


def run_dashboard() -> None:
    st.set_page_config(page_title="AI Savings Tracker", layout="wide")
    st.title("AI 무료/할인 이벤트 트래커")

    conn = connect()
    init_db(conn)

    providers = [
        row[0]
        for row in conn.execute("SELECT DISTINCT provider FROM events_current ORDER BY provider").fetchall()
    ]

    selected_provider = st.selectbox("제공사", options=["ALL", *providers])

    query = "SELECT * FROM events_current"
    params = []
    if selected_provider != "ALL":
        query += " WHERE provider = ?"
        params.append(selected_provider)
    query += " ORDER BY end_at IS NULL, end_at ASC"

    current_df = pd.read_sql_query(query, conn, params=params)
    st.subheader("현재 활성 이벤트")
    st.dataframe(current_df, use_container_width=True)

    st.subheader("변경 이력")
    history_df = pd.read_sql_query(
        "SELECT changed_at, change_type, fingerprint FROM events_history ORDER BY id DESC LIMIT 200", conn
    )
    st.dataframe(history_df, use_container_width=True)
