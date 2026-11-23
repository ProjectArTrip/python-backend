import secrets
from collections.abc import Sequence
from typing import Final

from arttrip.application.util.exception import DomainException

ANIMAL_NAMES: Final[tuple[str, ...]] = (
    "판다",
    "수달",
    "여우",
    "너구리",
    "다람쥐",
    "고양이",
    "강아지",
    "토끼",
    "사슴",
    "노루",
    "호랑이",
    "사자",
    "표범",
    "늑대",
    "곰",
    "펭귄",
    "고래",
    "돌고래",
    "물범",
    "해마",
    "참새",
    "제비",
    "까치",
    "부엉이",
    "올빼미",
    "두루미",
    "기러기",
    "오리",
    "백조",
    "갈매기",
    "거북이",
    "도마뱀",
    "개구리",
    "달팽이",
    "나비",
    "무지개",
    "구름",
    "별빛",
    "노을",
    "바람",
)

_DIGIT_COUNT: Final = 4


class EmptyCharacterPoolException(DomainException):
    def __init__(self) -> None:
        super().__init__(
            code="USER_CHARACTER_POOL_EMPTY",
            message="character pool must not be empty",
        )


def generate_display_name(
    *,
    pool: Sequence[str] = ANIMAL_NAMES,
    digit_count: int = _DIGIT_COUNT,
) -> str:

    if not pool:
        raise EmptyCharacterPoolException()

    word = secrets.choice(pool)
    suffix = secrets.randbelow(10**digit_count)
    return f"{word}{suffix:0{digit_count}d}"
