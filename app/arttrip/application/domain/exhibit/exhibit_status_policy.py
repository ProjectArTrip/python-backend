from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class ExhibitStatusPolicy:
    ending_soon_days: int

    def __post_init__(self) -> None:
        if self.ending_soon_days < 0:
            raise ValueError("ending_soon_days must not be negative")

    def ending_soon_until(self, today: date) -> date:
        return today + timedelta(days=self.ending_soon_days)
