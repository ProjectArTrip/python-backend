from arttrip.application.domain.exhibit.exceptions import ExhibitError
from arttrip.application.port.input.location.results import CountryView, RegionView
from arttrip.application.port.input.location.use_cases import (
    ListDomesticRegionsUseCase,
    ListOverseasCountriesUseCase,
)
from arttrip.application.port.output.unit_of_work import UnitOfWork


class ListOverseasCountriesService(ListOverseasCountriesUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def list_overseas_countries(self) -> list[CountryView]:
        with self._uow as uow:
            return [
                CountryView(code=country.code, name=country.name)
                for country in uow.locations.list_countries()
                if not country.is_domestic
            ]


class ListDomesticRegionsService(ListDomesticRegionsUseCase):
    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def list_domestic_regions(self) -> list[RegionView]:
        with self._uow as uow:
            return [
                RegionView(name=region.name, image_url=region.image_url)
                for region in uow.locations.list_regions()
            ]


def ensure_known_location(
    uow: UnitOfWork, *, country_code: str | None, regions: frozenset[str]
) -> None:
    if regions - {known.name for known in uow.locations.list_regions()}:
        raise ExhibitError.unknown_region()
    if (
        country_code is not None
        and uow.locations.find_country_by_code(country_code) is None
    ):
        raise ExhibitError.unknown_country()
