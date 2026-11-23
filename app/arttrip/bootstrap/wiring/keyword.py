from fastapi import Request

from arttrip.application.domain.keyword.keyword_services import (
    ListKeywordsService,
    ListRecommendedKeywordsService,
)
from arttrip.application.port.input.keyword.use_cases import (
    ListKeywordsUseCase,
    ListRecommendedKeywordsUseCase,
)
from arttrip.bootstrap.wiring.common import Overrides, new_unit_of_work
from arttrip.common import settings
from arttrip.inbound.http.dependencies.keyword import (
    provide_list_keywords_use_case,
    provide_list_recommended_keywords_use_case,
)


def build_list_keywords_use_case(request: Request) -> ListKeywordsUseCase:
    return ListKeywordsService(uow=new_unit_of_work(request))


def build_list_recommended_keywords_use_case(
    request: Request,
) -> ListRecommendedKeywordsUseCase:
    return ListRecommendedKeywordsService(
        uow=new_unit_of_work(request), size=settings.keyword.recommended_size
    )


def wire_keyword(overrides: Overrides) -> None:
    overrides[provide_list_keywords_use_case] = build_list_keywords_use_case
    overrides[provide_list_recommended_keywords_use_case] = (
        build_list_recommended_keywords_use_case
    )
