from __future__ import annotations

import json
from pathlib import Path

import yaml
from apscheduler.schedulers.blocking import BlockingScheduler

from app.alerts.change_digest import ChangeDigest
from app.sources.base import config_from_dict
from app.sources.gemini import GeminiSource
from app.sources.openai import OpenAISource
from app.storage.db import connect, init_db, insert_history, load_current_fingerprints, replace_current_events

SOURCE_MAP = {
    "openai": OpenAISource,
    "gemini": GeminiSource,
}


def load_config(path: Path = Path("config/sources.yaml")) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def run_once() -> ChangeDigest:
    config = load_config()
    defaults = config.get("defaults", {})
    all_events = []

    for row in config.get("sources", []):
        src_conf = config_from_dict(row, defaults)
        if not src_conf.enabled:
            continue
        source_cls = SOURCE_MAP.get(src_conf.kind)
        if not source_cls:
            continue
        source = source_cls(src_conf)
        try:
            all_events.extend(source.scrape())
        except Exception as exc:
            print(f"[WARN] source failed: {src_conf.provider}: {exc}")

    conn = connect()
    init_db(conn)

    old_fps = load_current_fingerprints(conn)
    new_fps = {e.fingerprint for e in all_events}

    new_only = new_fps - old_fps
    ended_only = old_fps - new_fps

    for e in all_events:
        if e.fingerprint in new_only:
            insert_history(conn, e.fingerprint, "NEW", e.model_dump_json())

    for fp in ended_only:
        insert_history(conn, fp, "ENDED", json.dumps({"fingerprint": fp}))

    replace_current_events(conn, all_events)
    return ChangeDigest(new_count=len(new_only), ended_count=len(ended_only))


def run_scheduler() -> None:
    scheduler = BlockingScheduler()
    scheduler.add_job(run_once, "interval", minutes=120)
    scheduler.start()
