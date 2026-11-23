from sqlalchemy import (
    CheckConstraint,
    Column,
    Identity,
    Integer,
    String,
    Table,
    UniqueConstraint,
)

from arttrip.application.domain.exhibit.region import Region
from arttrip.outbound.persistence.registry import mapper_registry
from arttrip.outbound.persistence.timestamps import (
    created_at_column,
    updated_at_column,
)

region_table = Table(
    "region",
    mapper_registry.metadata,
    Column("id", Integer, Identity(always=False), primary_key=True),
    Column("name", String(255), nullable=False),
    Column("image_url", String(1024), nullable=True),
    Column("display_order", Integer, nullable=False),
    created_at_column(nullable=False),
    updated_at_column(nullable=False),
    UniqueConstraint("name"),
    UniqueConstraint("display_order"),
    CheckConstraint("display_order >= 0", name="display_order"),
)


def map_region_table() -> None:
    mapper_registry.map_imperatively(
        Region,
        region_table,
        properties={"_id": region_table.c.id},
    )
