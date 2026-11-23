from decimal import Decimal
from typing import Final

from arttrip.application.domain.exhibit.exceptions import ExhibitError

DEFAULT_COUNTRY_CODE: Final = "KR"
MAX_LATITUDE: Final = Decimal(90)
MAX_LONGITUDE: Final = Decimal(180)


class ExhibitHall:
    def __init__(
        self,
        *,
        id_: int | None,
        name: str,
        address: str | None,
        phone: str | None,
        region: str,
        country_code: str,
        homepage_url: str | None,
        latitude: Decimal,
        longitude: Decimal,
        opening_hours: str | None,
        closed_days: str | None,
    ) -> None:
        self._id = id_
        self.name = name
        self.address = address
        self.phone = phone
        self.region = region
        self.country_code = country_code
        self.homepage_url = homepage_url
        self.latitude = latitude
        self.longitude = longitude
        self.opening_hours = opening_hours
        self.closed_days = closed_days

    @property
    def id(self) -> int | None:
        return self._id

    @property
    def is_domestic(self) -> bool:
        return self.country_code == DEFAULT_COUNTRY_CODE

    @classmethod
    def create(
        cls,
        *,
        name: str,
        country_code: str,
        region: str,
        address: str | None,
        opening_hours: str | None,
        phone: str | None,
        latitude: Decimal,
        longitude: Decimal,
    ) -> "ExhibitHall":
        hall = cls(
            id_=None,
            name=name,
            address=address,
            phone=phone,
            region=region,
            country_code=country_code,
            homepage_url=None,
            latitude=latitude,
            longitude=longitude,
            opening_hours=opening_hours,
            closed_days=None,
        )
        hall.revise(
            name=name,
            country_code=country_code,
            region=region,
            address=address,
            opening_hours=opening_hours,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
        )
        return hall

    def revise(
        self,
        *,
        name: str,
        country_code: str,
        region: str,
        address: str | None,
        opening_hours: str | None,
        phone: str | None,
        latitude: Decimal,
        longitude: Decimal,
    ) -> None:
        if not name.strip():
            raise ExhibitError.hall_name_required()
        if abs(latitude) > MAX_LATITUDE or abs(longitude) > MAX_LONGITUDE:
            raise ExhibitError.invalid_coordinates()
        self.name = name.strip()
        self.country_code = country_code
        self.region = region.strip()
        self.address = address
        self.opening_hours = opening_hours
        self.phone = phone
        self.latitude = latitude
        self.longitude = longitude
