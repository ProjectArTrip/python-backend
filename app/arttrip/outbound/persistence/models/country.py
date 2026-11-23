from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Identity,
    Integer,
    String,
    Table,
    UniqueConstraint,
)

from arttrip.application.domain.exhibit.country import Country
from arttrip.outbound.persistence.registry import mapper_registry
from arttrip.outbound.persistence.timestamps import (
    created_at_column,
    updated_at_column,
)

country_table = Table(
    "country",
    mapper_registry.metadata,
    Column("id", Integer, Identity(always=False), primary_key=True),
    Column("code", String(2), nullable=False),
    Column("name", String(255), nullable=False),
    Column("display_order", Integer, nullable=False),
    created_at_column(nullable=False),
    updated_at_column(nullable=False),
    UniqueConstraint("code"),
    UniqueConstraint("name"),
    UniqueConstraint("display_order"),
    CheckConstraint("code ~ '^[A-Z]{2}$'", name="code_format"),
    CheckConstraint("display_order >= 0", name="display_order"),
)

country_alias_table = Table(
    "country_alias",
    mapper_registry.metadata,
    Column("id", Integer, Identity(always=False), primary_key=True),
    Column("country_id", Integer, ForeignKey("country.id"), nullable=False),
    Column("name", String(255), nullable=False),
    created_at_column(nullable=False),
    updated_at_column(nullable=False),
    UniqueConstraint("name"),
)


def map_country_table() -> None:
    mapper_registry.map_imperatively(
        Country,
        country_table,
        properties={"_id": country_table.c.id},
    )
