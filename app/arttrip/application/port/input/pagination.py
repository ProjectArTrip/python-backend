from dataclasses import dataclass


@dataclass(frozen=True)
class CursorPage[T]:
    items: tuple[T, ...]
    next_cursor: int | None

    @property
    def has_next(self) -> bool:
        return self.next_cursor is not None


@dataclass(frozen=True)
class OffsetPage[T]:
    items: tuple[T, ...]
    page: int
    size: int
    total_elements: int

    @property
    def total_pages(self) -> int:
        return -(-self.total_elements // self.size)

    @property
    def is_first(self) -> bool:
        return self.page == 0

    @property
    def is_last(self) -> bool:
        return self.page >= self.total_pages - 1
