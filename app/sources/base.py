from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Any, Dict, List
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests

from app.normalizers.schema import PromotionEvent


@dataclass
class SourceConfig:
    provider: str
    kind: str
    url: str
    region: str = "global"
    enabled: bool = True
    timeout_seconds: int = 20
    max_retries: int = 2
    user_agent: str = "AI-Savings-Tracker/0.1"
    legal_note: str = ""


class BaseSource:
    def __init__(self, config: SourceConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": config.user_agent})

    def scrape(self) -> List[PromotionEvent]:
        raise NotImplementedError

    def can_fetch(self) -> bool:
        parsed = urlparse(self.config.url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        parser = RobotFileParser()
        try:
            parser.set_url(robots_url)
            parser.read()
            return parser.can_fetch(self.config.user_agent, self.config.url)
        except Exception:
            return False

    def get(self, url: str) -> str:
        for attempt in range(self.config.max_retries + 1):
            try:
                self._delay()
                resp = self.session.get(url, timeout=self.config.timeout_seconds)
                resp.raise_for_status()
                return resp.text
            except requests.RequestException:
                if attempt >= self.config.max_retries:
                    raise
                time.sleep(2 ** attempt)
        raise RuntimeError("unreachable")

    def _delay(self) -> None:
        time.sleep(random.uniform(0.4, 1.2))


def config_from_dict(data: Dict[str, Any], defaults: Dict[str, Any]) -> SourceConfig:
    merged = {**defaults, **data}
    return SourceConfig(
        provider=merged["provider"],
        kind=merged["kind"],
        url=merged["url"],
        region=merged.get("region", "global"),
        enabled=merged.get("enabled", True),
        timeout_seconds=merged.get("timeout_seconds", 20),
        max_retries=merged.get("max_retries", 2),
        user_agent=merged.get("user_agent", "AI-Savings-Tracker/0.1"),
        legal_note=merged.get("legal_note", ""),
    )
