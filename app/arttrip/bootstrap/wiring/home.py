from fastapi import Request

from arttrip.application.domain.exhibit.home_services import (
    ListGenreExhibitsService,
    ListHomeVenuesService,
    ListTodayExhibitsService,
)
from arttrip.application.port.input.home.use_cases import (
    ListGenreExhibitsUseCase,
    ListHomeVenuesUseCase,
    ListTodayExhibitsUseCase,
)
from arttrip.bootstrap.wiring.common import Overrides, new_unit_of_work
from arttrip.common import settings
from arttrip.inbound.http.dependencies.home import (
    provide_list_genre_exhibits_use_case,
    provide_list_home_venues_use_case,
    provide_list_today_exhibits_use_case,
)


def build_list_today_exhibits_use_case(request: Request) -> ListTodayExhibitsUseCase:
    return ListTodayExhibitsService(
        uow=new_unit_of_work(request),
        cache=request.app.state.today_exhibit_cache,
        status_policy=request.app.state.exhibit_status_policy,
        size=settings.home_screen.today_size,
    )


def build_list_genre_exhibits_use_case(request: Request) -> ListGenreExhibitsUseCase:
    return ListGenreExhibitsService(
        uow=new_unit_of_work(request),
        status_policy=request.app.state.exhibit_status_policy,
        size=settings.home_screen.genre_size,
    )


def build_list_home_venues_use_case(request: Request) -> ListHomeVenuesUseCase:
    return ListHomeVenuesService(
        uow=new_unit_of_work(request),
        size=settings.home_screen.venue_size,
    )


def wire_home(overrides: Overrides) -> None:
    overrides[provide_list_today_exhibits_use_case] = build_list_today_exhibits_use_case
    overrides[provide_list_genre_exhibits_use_case] = build_list_genre_exhibits_use_case
    overrides[provide_list_home_venues_use_case] = build_list_home_venues_use_case
