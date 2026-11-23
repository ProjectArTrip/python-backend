from typing import Any, Self

from pydantic import BaseModel, BeforeValidator, ConfigDict
from pydantic.alias_generators import to_camel

from arttrip.application.port.input.pagination import OffsetPage


class ApiModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_name=True)


def _uppercase(value: object) -> object:
    return value.upper() if isinstance(value, str) else value


CaseInsensitive = BeforeValidator(_uppercase)


class PageResponse[ItemT](ApiModel):
    items: list[ItemT]
    page: int
    size: int
    total_pages: int
    total_elements: int
    first: bool
    last: bool

    @classmethod
    def of(cls, result: OffsetPage[Any], items: list[ItemT]) -> Self:
        return cls(
            items=items,
            page=result.page,
            size=result.size,
            total_pages=result.total_pages,
            total_elements=result.total_elements,
            first=result.is_first,
            last=result.is_last,
        )
