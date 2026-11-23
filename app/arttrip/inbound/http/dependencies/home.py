from typing import Annotated

from fastapi import Depends

from arttrip.application.port.input.home.use_cases import (
    ListGenreExhibitsUseCase,
    ListPersonalizedExhibitsUseCase,
    ListScheduledExhibitsUseCase,
    ListTodayExhibitsUseCase,
)


def provide_list_today_exhibits_use_case() -> ListTodayExhibitsUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_list_scheduled_exhibits_use_case() -> ListScheduledExhibitsUseCase:
    raise NotImplementedError("composition root must override this dependency")


ListTodayExhibitsUseCaseDep = Annotated[
    ListTodayExhibitsUseCase, Depends(provide_list_today_exhibits_use_case)
]


ListScheduledExhibitsUseCaseDep = Annotated[
    ListScheduledExhibitsUseCase, Depends(provide_list_scheduled_exhibits_use_case)
]


def provide_list_personalized_exhibits_use_case() -> ListPersonalizedExhibitsUseCase:
    raise NotImplementedError("composition root must override this dependency")


def provide_list_genre_exhibits_use_case() -> ListGenreExhibitsUseCase:
    raise NotImplementedError("composition root must override this dependency")


ListPersonalizedExhibitsUseCaseDep = Annotated[
    ListPersonalizedExhibitsUseCase,
    Depends(provide_list_personalized_exhibits_use_case),
]


ListGenreExhibitsUseCaseDep = Annotated[
    ListGenreExhibitsUseCase, Depends(provide_list_genre_exhibits_use_case)
]
