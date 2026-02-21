from __future__ import annotations

from datetime import datetime
from hashlib import sha256
from typing import Literal, Optional

from pydantic import BaseModel, Field

EventType = Literal[
    "first_signup_free",
    "trial_days",
    "discount_percent",
    "credit_bonus",
    "monthly_free_credit",
    "other",
]


class PromotionEvent(BaseModel):
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
    source_url: str
    collected_at: datetime = Field(default_factory=datetime.utcnow)
    fingerprint: str = ""

    def with_fingerprint(self) -> "PromotionEvent":
        self.fingerprint = compute_fingerprint(self)
        return self


def compute_fingerprint(event: PromotionEvent) -> str:
    raw = "|".join(
        [
            event.provider,
            event.event_title,
            str(event.start_at),
            str(event.end_at),
            str(event.price_before),
            str(event.price_after),
            str(event.credit_amount),
            str(event.credit_unit),
            str(event.eligibility),
        ]
    )
    return sha256(raw.encode("utf-8")).hexdigest()
