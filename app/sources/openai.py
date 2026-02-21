from bs4 import BeautifulSoup

from app.normalizers.schema import PromotionEvent
from app.sources.base import BaseSource


class OpenAISource(BaseSource):
    def scrape(self) -> list[PromotionEvent]:
        if not self.can_fetch():
            return []
        html = self.get(self.config.url)
        soup = BeautifulSoup(html, "html.parser")
        text = " ".join(soup.get_text(" ").split())

        events: list[PromotionEvent] = []
        if "free" in text.lower() or "trial" in text.lower() or "discount" in text.lower():
            events.append(
                PromotionEvent(
                    provider=self.config.provider,
                    event_title="OpenAI pricing page mention (keyword-detected)",
                    event_type="other",
                    region=self.config.region,
                    eligibility="Check official terms",
                    source_url=self.config.url,
                ).with_fingerprint()
            )
        return events
