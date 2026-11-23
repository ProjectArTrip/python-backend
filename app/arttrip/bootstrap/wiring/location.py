from fastapi import Request

from arttrip.application.domain.exhibit.location_services import (
    ListDomesticRegionsService,
    ListOverseasCountriesService,
)
from arttrip.application.port.input.location.use_cases import (
    ListDomesticRegionsUseCase,
    ListOverseasCountriesUseCase,
)
from arttrip.bootstrap.wiring.common import Overrides, new_unit_of_work
from arttrip.inbound.http.dependencies.location import (
    provide_list_domestic_regions_use_case,
    provide_list_overseas_countries_use_case,
)


def build_list_overseas_countries_use_case(
    request: Request,
) -> ListOverseasCountriesUseCase:
    return ListOverseasCountriesService(uow=new_unit_of_work(request))


def build_list_domestic_regions_use_case(
    request: Request,
) -> ListDomesticRegionsUseCase:
    return ListDomesticRegionsService(uow=new_unit_of_work(request))


def wire_location(overrides: Overrides) -> None:
    overrides[provide_list_overseas_countries_use_case] = (
        build_list_overseas_countries_use_case
    )
    overrides[provide_list_domestic_regions_use_case] = (
        build_list_domestic_regions_use_case
    )
