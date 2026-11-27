"""Trusted clock injection. The time source itself is a provisional default."""

from __future__ import annotations

import time
from dataclasses import dataclass, field


# PROVISIONAL_DEFAULT: 120 seconds. Section 16 leaves the agreed skew open.
DEFAULT_SKEW_SECONDS = 120


class Clock:
    """Returns integer UTC seconds."""

    def now_ts(self) -> int:
        return int(time.time())


@dataclass
class FrozenClock(Clock):
    """Deterministic clock for tests."""

    t: int
    _started: int = field(init=False)

    def __post_init__(self) -> None:
        self._started = self.t

    def now_ts(self) -> int:
        return int(self.t)

    def advance(self, seconds: int) -> None:
        self.t = int(self.t) + int(seconds)
