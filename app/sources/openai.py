import re

from app.normalizers.schema import PromotionEvent
from app.sources.base import BaseSource


class OpenAISource(BaseSource):
    def scrape(self) -> list[PromotionEvent]:
        if not self.can_fetch():
            return []

        html = self.get(self.config.url)
        text = re.sub(r"<[^>]+>", " ", html)
        text = " ".join(text.split())
        lower = text.lower()

        events: list[PromotionEvent] = []
        for days in re.findall(r"(\d{1,3})\s*-?\s*day[s]?\s*(?:free|trial)", lower):
            events.append(
                PromotionEvent(
                    provider=self.config.provider,
                    event_title=f"OpenAI trial {days} days",
                    event_type="trial_days",
                    region=self.config.region,
                    credit_amount=float(days),
                    credit_unit="days",
                    eligibility="Check official terms",
                    source_url=self.config.url,
                ).with_keys()
            )

        for pct in re.findall(r"(\d{1,3})\s*%\s*(?:off|discount)", lower):
            events.append(
                PromotionEvent(
                    provider=self.config.provider,
                    event_title=f"OpenAI discount {pct}%",
                    event_type="discount_percent",
                    region=self.config.region,
                    credit_amount=float(pct),
                    credit_unit="percent",
                    eligibility="Check official terms",
                    source_url=self.config.url,
                ).with_keys()
            )

        if not events and any(k in lower for k in ("free", "trial", "discount", "credit")):
            events.append(
                PromotionEvent(
                    provider=self.config.provider,
                    event_title="OpenAI promotion mention (keyword-detected)",
                    event_type="other",
                    region=self.config.region,
                    eligibility="Check official terms",
                    source_url=self.config.url,
                ).with_keys()
            )

        return events
