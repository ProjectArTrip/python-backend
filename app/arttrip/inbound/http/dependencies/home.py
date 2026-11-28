from typing import Annotated

from fastapi import Depends

from arttrip.application.port.input.home.use_cases import (
    ListGenreExhibitsUseCase,
    ListHomeVenuesUseCase,
    ListTodayExhibitsUseCase,
)


def provide_list_today_exhibits_use_case() -> ListTodayExhibitsUseCase:
    raise NotImplementedError("composition root must override this dependency")


ListTodayExhibitsUseCaseDep = Annotated[
    ListTodayExhibitsUseCase, Depends(provide_list_today_exhibits_use_case)
]


def provide_list_genre_exhibits_use_case() -> ListGenreExhibitsUseCase:
    raise NotImplementedError("composition root must override this dependency")


ListGenreExhibitsUseCaseDep = Annotated[
    ListGenreExhibitsUseCase, Depends(provide_list_genre_exhibits_use_case)
]


def provide_list_home_venues_use_case() -> ListHomeVenuesUseCase:
    raise NotImplementedError("composition root must override this dependency")


ListHomeVenuesUseCaseDep = Annotated[
    ListHomeVenuesUseCase, Depends(provide_list_home_venues_use_case)
]
