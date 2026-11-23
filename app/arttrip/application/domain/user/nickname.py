import re
from typing import Final

from arttrip.application.domain.user.exceptions import UserError

NICKNAME_MIN_LENGTH: Final = 2
NICKNAME_MAX_LENGTH: Final = 10
_NICKNAME_PATTERN: Final = re.compile(r"[a-zA-Z0-9가-힣]+")


def validate_nickname(raw: str) -> str:
    nickname = raw.strip()
    if not is_valid_nickname(nickname):
        raise UserError.invalid_nickname()
    return nickname


def is_valid_nickname(nickname: str) -> bool:
    return (
        NICKNAME_MIN_LENGTH <= len(nickname) <= NICKNAME_MAX_LENGTH
        and _NICKNAME_PATTERN.fullmatch(nickname) is not None
    )
