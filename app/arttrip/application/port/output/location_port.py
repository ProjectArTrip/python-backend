from abc import ABC, abstractmethod

from arttrip.application.domain.exhibit.country import Country
from arttrip.application.domain.exhibit.region import Region


class LocationPort(ABC):
    @abstractmethod
    def list_countries(self) -> list[Country]:
        pass

    @abstractmethod
    def find_country_by_name(self, name: str) -> Country | None:
        pass

    @abstractmethod
    def list_regions(self) -> list[Region]:
        pass

    @abstractmethod
    def map_countries_by_name(self) -> dict[str, Country]:
        pass

    @abstractmethod
    def find_country_by_code(self, code: str) -> Country | None:
        pass
