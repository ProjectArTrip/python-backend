from typing import Annotated, Final

from fastapi import Query
from pydantic import Field

MAX_PAGE_SIZE: Final = 20
DEFAULT_PAGE_SIZE: Final = 20

CursorParam = Annotated[int | None, Query(gt=0)]
PageSizeParam = Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)]

ADMIN_MAX_PAGE_SIZE: Final = 100
MAX_PAGE_INDEX: Final = 10_000
PageIndexParam = Annotated[int, Query(ge=0, le=MAX_PAGE_INDEX)]
AdminPageSizeParam = Annotated[int, Query(ge=1, le=ADMIN_MAX_PAGE_SIZE)]

# 쿼리 파라미터 모델의 필드 타입. 요청 이름은 ApiModel 이 필드명의 camelCase 로 정한다
CursorId = Annotated[int | None, Field(gt=0)]
PageSize = Annotated[int, Field(ge=1, le=MAX_PAGE_SIZE)]
PageIndex = Annotated[int, Field(ge=0, le=MAX_PAGE_INDEX)]
AdminPageSize = Annotated[int, Field(ge=1, le=ADMIN_MAX_PAGE_SIZE)]
