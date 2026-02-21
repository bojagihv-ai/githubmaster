from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from app.alerts.change_digest import ChangeDigest
from app.sources.base import config_from_dict
from app.sources.gemini import GeminiSource
from app.sources.openai import OpenAISource
from app.storage.db import connect, init_db, insert_history, load_current_events, replace_current_events

SOURCE_MAP = {
    "openai": OpenAISource,
    "gemini": GeminiSource,
}


def load_config(path: Path = Path("config/sources.yaml")) -> dict[str, Any]:
    if path.exists():
        try:
            import yaml  # type: ignore

            return yaml.safe_load(path.read_text(encoding="utf-8"))
        except ModuleNotFoundError:
            pass

    json_path = Path("config/sources.json")
    if json_path.exists():
        return json.loads(json_path.read_text(encoding="utf-8"))

    raise RuntimeError("Config file not found. Use config/sources.yaml or config/sources.json")


def _row_to_payload(row: Any) -> dict[str, Any]:
    return {
        "fingerprint": row["fingerprint"],
        "identity_key": row["identity_key"],
        "provider": row["provider"],
        "event_title": row["event_title"],
        "event_type": row["event_type"],
        "region": row["region"],
        "start_at": row["start_at"],
        "end_at": row["end_at"],
        "price_before": row["price_before"],
        "price_after": row["price_after"],
        "currency": row["currency"],
        "credit_amount": row["credit_amount"],
        "credit_unit": row["credit_unit"],
        "eligibility": row["eligibility"],
        "source_url": row["source_url"],
        "collected_at": row["collected_at"],
    }


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
            print(f"[WARN] unknown source kind: {src_conf.kind}")
            continue
        source = source_cls(src_conf)
        try:
            all_events.extend(source.scrape())
        except Exception as exc:
            print(f"[WARN] source failed: {src_conf.provider}: {exc}")

    conn = connect()
    init_db(conn)

    old_map = load_current_events(conn)
    new_map = {e.identity_key: e for e in all_events}

    old_keys = set(old_map.keys())
    new_keys = set(new_map.keys())

    new_only = new_keys - old_keys
    ended_only = old_keys - new_keys
    kept = old_keys & new_keys

    updated = []
    watched_fields = [
        "fingerprint",
        "start_at",
        "end_at",
        "price_before",
        "price_after",
        "currency",
        "credit_amount",
        "credit_unit",
        "eligibility",
    ]

    for key in kept:
        old_row = old_map[key]
        new_event = new_map[key]
        changes = {}
        new_payload = new_event.model_dump(mode="json")
        for field in watched_fields:
            old_val = old_row[field]
            new_val = new_payload.get(field)
            if str(old_val) != str(new_val):
                changes[field] = {"before": old_val, "after": new_val}
        if changes:
            updated.append((key, new_event.fingerprint, changes))

    for key in new_only:
        e = new_map[key]
        insert_history(conn, e.fingerprint, e.identity_key, e.provider, e.event_title, "NEW", e.model_dump_json())

    for key in ended_only:
        old = old_map[key]
        insert_history(conn, old["fingerprint"], key, old["provider"], old["event_title"], "ENDED", json.dumps(_row_to_payload(old), ensure_ascii=False))

    for key, fp, changes in updated:
        insert_history(
            conn,
            fp,
            key,
            new_map[key].provider,
            new_map[key].event_title,
            "UPDATED",
            json.dumps(changes, ensure_ascii=False),
        )

    replace_current_events(conn, all_events)
    return ChangeDigest(new_count=len(new_only), updated_count=len(updated), ended_count=len(ended_only))


def run_scheduler() -> None:
    config = load_config()
    defaults = config.get("defaults", {})
    intervals = []
    for row in config.get("sources", []):
        src_conf = config_from_dict(row, defaults)
        if src_conf.enabled:
            intervals.append(src_conf.poll_interval_minutes)
    interval_minutes = min(intervals) if intervals else 120

    try:
        from apscheduler.schedulers.blocking import BlockingScheduler  # type: ignore

        scheduler = BlockingScheduler()
        scheduler.add_job(run_once, "interval", minutes=interval_minutes)
        scheduler.start()
    except ModuleNotFoundError:
        print(f"[WARN] APScheduler not installed, fallback loop every {interval_minutes} minutes")
        while True:
            digest = run_once()
            print(digest.summary())
            time.sleep(interval_minutes * 60)
