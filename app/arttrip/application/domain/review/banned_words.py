import re
from typing import Collection, Final

_FILTER_NOISE: Final = re.compile(r"[^a-z가-힣]")


def normalize_for_filter(text: str) -> str:
    return _FILTER_NOISE.sub("", text.lower())


def contains_banned_word(text: str, banned_words: Collection[str]) -> bool:
    normalized = normalize_for_filter(text)
    return any(
        word and word in normalized
        for word in (normalize_for_filter(banned) for banned in banned_words)
    )
