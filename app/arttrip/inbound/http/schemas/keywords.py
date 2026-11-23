from arttrip.application.domain.keyword.keyword_type import KeywordType
from arttrip.inbound.http.schemas.base import ApiModel


class KeywordResponse(ApiModel):
    keyword_id: int
    name: str
    type: KeywordType


class KeywordListResponse(ApiModel):
    keywords: list[KeywordResponse]
