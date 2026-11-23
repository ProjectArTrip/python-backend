from sqlalchemy import select
from sqlalchemy.orm import Session

from arttrip.application.domain.exhibit.country import Country
from arttrip.application.domain.exhibit.region import Region
from arttrip.application.port.output.location_port import LocationPort
from arttrip.outbound.persistence.models import (
    country_alias_table,
    country_table,
    region_table,
)


class LocationAdapter(LocationPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_countries(self) -> list[Country]:
        statement = select(Country).order_by(country_table.c.display_order)
        return list(self._session.scalars(statement).all())

    def list_regions(self) -> list[Region]:
        statement = select(Region).order_by(region_table.c.display_order)
        return list(self._session.scalars(statement).all())

    def find_country_by_code(self, code: str) -> Country | None:
        statement = select(Country).where(country_table.c.code == code)
        return self._session.scalars(statement).first()

    def find_country_by_name(self, name: str) -> Country | None:
        by_name = select(Country).where(country_table.c.name == name)
        country = self._session.scalars(by_name).first()
        if country is not None:
            return country
        by_alias = (
            select(Country)
            .join(
                country_alias_table,
                country_alias_table.c.country_id == country_table.c.id,
            )
            .where(country_alias_table.c.name == name)
        )
        return self._session.scalars(by_alias).first()

    def map_countries_by_name(self) -> dict[str, Country]:
        countries = self.list_countries()
        by_id = {country.id: country for country in countries}
        aliases = self._session.execute(
            select(country_alias_table.c.name, country_alias_table.c.country_id)
        ).all()
        by_name = {name: by_id[country_id] for name, country_id in aliases}
        by_name.update({country.name: country for country in countries})
        return by_name
