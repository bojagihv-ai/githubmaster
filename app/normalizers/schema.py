from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from hashlib import sha256
from typing import Literal, Optional

EventType = Literal[
    "first_signup_free",
    "trial_days",
    "discount_percent",
    "credit_bonus",
    "monthly_free_credit",
    "other",
]


@dataclass
class PromotionEvent:
    provider: str
    event_title: str
    event_type: EventType = "other"
    region: str = "global"
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    price_before: Optional[float] = None
    price_after: Optional[float] = None
    currency: Optional[str] = None
    credit_amount: Optional[float] = None
    credit_unit: Optional[str] = None
    eligibility: Optional[str] = None
    source_url: str = ""
    collected_at: datetime = field(default_factory=datetime.utcnow)
    identity_key: str = ""
    fingerprint: str = ""

    def with_keys(self) -> "PromotionEvent":
        self.identity_key = compute_identity_key(self)
        self.fingerprint = compute_fingerprint(self)
        return self

    def model_dump(self, mode: str = "python") -> dict:
        data = asdict(self)
        if mode == "json":
            for key in ("start_at", "end_at", "collected_at"):
                val = data.get(key)
                if isinstance(val, datetime):
                    data[key] = val.isoformat()
        return data

    def model_dump_json(self) -> str:
        return json.dumps(self.model_dump(mode="json"), ensure_ascii=False)


def compute_identity_key(event: PromotionEvent) -> str:
    raw = "|".join(
        [
            event.provider,
            event.event_title.strip().lower(),
            event.event_type,
            event.region,
            event.source_url,
        ]
    )
    return sha256(raw.encode("utf-8")).hexdigest()


def compute_fingerprint(event: PromotionEvent) -> str:
    raw = "|".join(
        [
            compute_identity_key(event),
            str(event.start_at),
            str(event.end_at),
            str(event.price_before),
            str(event.price_after),
            str(event.currency),
            str(event.credit_amount),
            str(event.credit_unit),
            str(event.eligibility),
        ]
    )
    return sha256(raw.encode("utf-8")).hexdigest()
