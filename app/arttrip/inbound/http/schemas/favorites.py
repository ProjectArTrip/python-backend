from arttrip.application.domain.favorite.favorite_sort import FavoriteSort
from arttrip.inbound.http.pagination import DEFAULT_PAGE_SIZE, CursorId, PageSize
from arttrip.inbound.http.query_params import CountryCode, Region
from arttrip.inbound.http.schemas.base import ApiModel
from arttrip.inbound.http.schemas.exhibits import ExhibitSummaryResponse


class FavoriteListResponse(ApiModel):
    favorites: list[ExhibitSummaryResponse]
    total_count: int
    next_cursor: int | None
    has_next: bool


class FavoriteListParams(ApiModel):
    sort_type: FavoriteSort = FavoriteSort.LATEST
    cursor: CursorId = None
    size: PageSize = DEFAULT_PAGE_SIZE
    domestic: bool | None = None
    country_code: CountryCode = None
    region: Region = None
