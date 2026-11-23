from arttrip.application.domain.keyword.keyword import Keyword
from arttrip.application.port.input.keyword.results import KeywordView
from arttrip.application.port.input.keyword.use_cases import (
    ListKeywordsUseCase,
    ListRecommendedKeywordsUseCase,
)
from arttrip.application.port.output.unit_of_work import UnitOfWork


class ListKeywordsService(ListKeywordsUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def list_keywords(self) -> list[KeywordView]:
        with self._uow as uow:
            return [to_keyword_view(keyword) for keyword in uow.keywords.list_all()]


def to_keyword_view(keyword: Keyword) -> KeywordView:
    keyword_id = keyword.id
    if keyword_id is None:
        raise RuntimeError("keyword loaded from storage must have an id")
    return KeywordView(
        keyword_id=keyword_id, name=keyword.name, keyword_type=keyword.keyword_type
    )


class ListRecommendedKeywordsService(ListRecommendedKeywordsUseCase):
    def __init__(self, *, uow: UnitOfWork, size: int) -> None:
        self._uow = uow
        self._size = size

    def list_recommended_keywords(self, user_id: int) -> list[KeywordView]:
        with self._uow as uow:
            keywords = uow.keywords.list_random_selected(
                user_id=user_id, limit=self._size
            )
            return [to_keyword_view(keyword) for keyword in keywords]
