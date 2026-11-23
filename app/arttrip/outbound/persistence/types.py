from enum import StrEnum
from typing import Final

from sqlalchemy.dialects.postgresql import TIMESTAMP

TIMESTAMPTZ: Final = TIMESTAMP(precision=6, timezone=True)


def list_enum_values(enum_cls: type[StrEnum]) -> list[str]:
    return [member.value for member in enum_cls]
