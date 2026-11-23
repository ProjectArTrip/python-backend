from typing import Annotated, Final

from fastapi import Query
from pydantic import Field

SEARCH_TEXT_MAX_LENGTH: Final = 50
REGION_MAX_LENGTH: Final = 255
REGION_PATTERN: Final = r"^\S(?:.*\S)?$"
COUNTRY_CODE_PATTERN: Final = "^[A-Za-z]{2}$"

SearchTextParam = Annotated[str | None, Query(max_length=SEARCH_TEXT_MAX_LENGTH)]

# 쿼리 파라미터 모델의 필드 타입. 요청 이름은 ApiModel 이 필드명의 camelCase 로 정한다
SearchText = Annotated[str | None, Field(max_length=SEARCH_TEXT_MAX_LENGTH)]
Region = Annotated[
    str | None,
    Field(min_length=1, max_length=REGION_MAX_LENGTH, pattern=REGION_PATTERN),
]
CountryCode = Annotated[str | None, Field(pattern=COUNTRY_CODE_PATTERN)]
