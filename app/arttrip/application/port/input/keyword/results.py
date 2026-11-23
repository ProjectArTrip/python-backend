from dataclasses import dataclass

from arttrip.application.domain.keyword.keyword_type import KeywordType


@dataclass(frozen=True)
class KeywordView:
    keyword_id: int
    name: str
    keyword_type: KeywordType
