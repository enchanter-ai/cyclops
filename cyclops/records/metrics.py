from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from ..enums import Taint

@dataclass
class Metrics:
    calls: int = 0
    flagged: int = 0
    blocked: int = 0
    taint: Counter[Taint] = field(default_factory=Counter)

    def observe(self, taint: Taint) -> None:
        self.calls += 1
        self.taint[taint] += 1

    def flag(self) -> None:
        self.flagged += 1

    def block(self) -> None:
        self.blocked += 1

    def summary(self) -> dict[str, Any]:
        return {
            "calls": self.calls,
            "flagged": self.flagged,
            "blocked": self.blocked,
            "taint": {t.value: n for t, n in self.taint.items()},
        }
