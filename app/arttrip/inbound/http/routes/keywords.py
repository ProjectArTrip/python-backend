from fastapi import APIRouter

from arttrip.inbound.http.dependencies.auth import CurrentUserDep
from arttrip.inbound.http.dependencies.keyword import (
    ListKeywordsUseCaseDep,
    ListRecommendedKeywordsUseCaseDep,
)
from arttrip.inbound.http.openapi import AUTHENTICATION_ERRORS, error_responses
from arttrip.inbound.http.schemas.keywords import KeywordListResponse, KeywordResponse

router = APIRouter()


@router.get(
    "",
    response_model=KeywordListResponse,
)
def list_keywords(use_case: ListKeywordsUseCaseDep) -> KeywordListResponse:
    keywords = use_case.list_keywords()
    return KeywordListResponse(
        keywords=[
            KeywordResponse(
                keyword_id=keyword.keyword_id,
                name=keyword.name,
                type=keyword.keyword_type,
            )
            for keyword in keywords
        ]
    )


@router.get(
    "/recommended",
    response_model=KeywordListResponse,
    responses=error_responses(*AUTHENTICATION_ERRORS),
)
def list_recommended_keywords(
    current_user: CurrentUserDep,
    use_case: ListRecommendedKeywordsUseCaseDep,
) -> KeywordListResponse:
    keywords = use_case.list_recommended_keywords(current_user.user_id)
    return KeywordListResponse(
        keywords=[
            KeywordResponse(
                keyword_id=keyword.keyword_id,
                name=keyword.name,
                type=keyword.keyword_type,
            )
            for keyword in keywords
        ]
    )
