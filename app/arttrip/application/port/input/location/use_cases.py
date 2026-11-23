from abc import ABC, abstractmethod

from arttrip.application.port.input.location.results import CountryView, RegionView


class ListOverseasCountriesUseCase(ABC):
    @abstractmethod
    def list_overseas_countries(self) -> list[CountryView]:
        pass


class ListDomesticRegionsUseCase(ABC):
    @abstractmethod
    def list_domestic_regions(self) -> list[RegionView]:
        pass
