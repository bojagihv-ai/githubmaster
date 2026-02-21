from __future__ import annotations

import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser

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
    poll_interval_minutes: int = 720


class BaseSource:
    def __init__(self, config: SourceConfig):
        self.config = config

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
                req = Request(url, headers={"User-Agent": self.config.user_agent})
                with urlopen(req, timeout=self.config.timeout_seconds) as resp:  # nosec B310
                    return resp.read().decode("utf-8", errors="ignore")
            except URLError as exc:
                if attempt >= self.config.max_retries:
                    self._dump_failure(url, str(exc))
                    raise
                time.sleep(2**attempt)
        raise RuntimeError("unreachable")

    def _delay(self) -> None:
        time.sleep(random.uniform(0.4, 1.2))

    def _dump_failure(self, url: str, reason: str) -> None:
        out_dir = Path("data/failures")
        out_dir.mkdir(parents=True, exist_ok=True)
        safe_name = url.replace("https://", "").replace("http://", "").replace("/", "_")
        path = out_dir / f"{self.config.provider}_{safe_name}.log"
        path.write_text(f"url={url}\nreason={reason}\n", encoding="utf-8")


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
        poll_interval_minutes=merged.get("poll_interval_minutes", 720),
    )
