from sqlalchemy import (
    CheckConstraint,
    Column,
    Identity,
    Index,
    Integer,
    Numeric,
    String,
    Table,
)

from arttrip.application.domain.exhibit.exhibit_hall import ExhibitHall
from arttrip.outbound.persistence.registry import mapper_registry
from arttrip.outbound.persistence.timestamps import (
    created_at_column,
    updated_at_column,
)

exhibit_hall_table = Table(
    "exhibit_hall",
    mapper_registry.metadata,
    Column("id", Integer, Identity(always=False), primary_key=True),
    Column("name", String(255), nullable=False),
    Column("address", String(255), nullable=True),
    Column("phone", String(255), nullable=True),
    Column("region", String(255), nullable=False),
    Column("country_code", String(2), nullable=False),
    Column("homepage_url", String(1024), nullable=True),
    Column("latitude", Numeric(9, 7), nullable=False),
    Column("longitude", Numeric(10, 7), nullable=False),
    Column("opening_hours", String(500), nullable=True),
    Column("closed_days", String(255), nullable=True),
    created_at_column(nullable=True),
    updated_at_column(nullable=True),
    CheckConstraint("latitude BETWEEN -90 AND 90", name="latitude"),
    CheckConstraint("longitude BETWEEN -180 AND 180", name="longitude"),
    CheckConstraint("country_code ~ '^[A-Z]{2}$'", name="country_code_format"),
    Index(None, "country_code", "region"),
)


def map_exhibit_hall_table() -> None:
    mapper_registry.map_imperatively(
        ExhibitHall,
        exhibit_hall_table,
        properties={"_id": exhibit_hall_table.c.id},
        exclude_properties=["created_at", "updated_at"],
    )
