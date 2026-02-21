from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ChangeDigest:
    new_count: int
    ended_count: int

    def summary(self) -> str:
        return f"NEW: {self.new_count}, ENDED: {self.ended_count}"
