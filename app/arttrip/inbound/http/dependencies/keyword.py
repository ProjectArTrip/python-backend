from typing import Annotated

from fastapi import Depends

from arttrip.application.port.input.keyword.use_cases import (
    ListKeywordsUseCase,
    ListRecommendedKeywordsUseCase,
)


def provide_list_keywords_use_case() -> ListKeywordsUseCase:
    raise NotImplementedError("composition root must override this dependency")


ListKeywordsUseCaseDep = Annotated[
    ListKeywordsUseCase, Depends(provide_list_keywords_use_case)
]


def provide_list_recommended_keywords_use_case() -> ListRecommendedKeywordsUseCase:
    raise NotImplementedError("composition root must override this dependency")


ListRecommendedKeywordsUseCaseDep = Annotated[
    ListRecommendedKeywordsUseCase,
    Depends(provide_list_recommended_keywords_use_case),
]
