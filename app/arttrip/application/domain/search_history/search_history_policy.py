from dataclasses import dataclass


@dataclass(frozen=True)
class SearchHistoryPolicy:
    max_count: int
    max_length: int

    def __post_init__(self) -> None:
        if self.max_count < 1 or self.max_length < 1:
            raise ValueError("search history limits must be positive")
