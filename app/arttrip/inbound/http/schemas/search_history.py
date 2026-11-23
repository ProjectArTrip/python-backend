from datetime import datetime

from pydantic import Field

from arttrip.inbound.http.schemas.base import ApiModel


class AddSearchHistoryRequest(ApiModel):
    keyword: str = Field(min_length=1, max_length=255)


class SearchHistoryResponse(ApiModel):
    search_history_id: int
    keyword: str
    searched_at: datetime


class SearchHistoryListResponse(ApiModel):
    items: list[SearchHistoryResponse]
